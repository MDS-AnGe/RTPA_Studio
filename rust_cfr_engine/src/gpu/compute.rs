/// GPU Compute engine pour CFR
use crate::types::*;
use crate::cfr::AbstractionManager;
use dashmap::DashMap;
use std::sync::Arc;
use wgpu::{Device, Queue, Buffer, ComputePipeline};

pub struct GpuCompute {
    device: Device,
    queue: Queue,
    compute_pipeline: ComputePipeline,
    config: GpuConfig,
    // Buffers pour GPU
    input_buffer: Buffer,
    output_buffer: Buffer,
    staging_buffer: Buffer,
}

impl GpuCompute {
    /// Initialisation GPU compute
    pub async fn new(config: GpuConfig) -> Result<Self, String> {
        // Créer instance WGPU
        let instance = wgpu::Instance::new(wgpu::InstanceDescriptor {
            backends: wgpu::Backends::all(),
            ..Default::default()
        });

        // Adapter GPU
        let adapter = instance
            .request_adapter(&wgpu::RequestAdapterOptions {
                power_preference: wgpu::PowerPreference::HighPerformance,
                compatible_surface: None,
                force_fallback_adapter: false,
            })
            .await
            .ok_or_else(|| "Aucun adapteur GPU trouvé".to_string())?;

        println!("🔥 GPU détecté: {:?}", adapter.get_info());

        // Device et queue
        let (device, queue) = adapter
            .request_device(
                &wgpu::DeviceDescriptor {
                    required_features: wgpu::Features::empty(),
                    required_limits: wgpu::Limits::default(),
                    label: Some("CFR GPU Device"),
                },
                None,
            )
            .await.map_err(|e| e.to_string())?;

        // Charger shader compute
        let shader_source = include_str!("shaders/cfr_compute.wgsl");
        let compute_shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("CFR Compute Shader"),
            source: wgpu::ShaderSource::Wgsl(shader_source.into()),
        });

        // Pipeline compute
        let compute_pipeline = device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
            label: Some("CFR Pipeline"),
            layout: None,
            module: &compute_shader,
            entry_point: "main",
        });

        // Créer buffers
        let buffer_size = (config.batch_size * std::mem::size_of::<f32>() * 256) as u64; // 256 floats par state

        let input_buffer = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("CFR Input Buffer"),
            size: buffer_size,
            usage: wgpu::BufferUsages::STORAGE | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });

        let output_buffer = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("CFR Output Buffer"),
            size: buffer_size,
            usage: wgpu::BufferUsages::STORAGE | wgpu::BufferUsages::COPY_SRC,
            mapped_at_creation: false,
        });

        let staging_buffer = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("CFR Staging Buffer"),
            size: buffer_size,
            usage: wgpu::BufferUsages::MAP_READ | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });

        println!("✅ GPU CFR engine initialisé - Buffer: {:.1}MB", buffer_size as f64 / 1024.0 / 1024.0);

        Ok(Self {
            device,
            queue,
            compute_pipeline,
            config,
            input_buffer,
            output_buffer,
            staging_buffer,
        })
    }

    /// Calcul CFR sur GPU pour un batch de states
    pub async fn compute_cfr_batch(
        &self,
        states: &[PokerState], 
        _strategies: &Arc<DashMap<InformationSet, Strategy>>,
        _abstraction: &AbstractionManager
    ) -> Result<f64, String> {
        
        // Convertir states en données GPU
        let gpu_data = self.prepare_gpu_data(states)?;
        
        // Écrire données dans buffer GPU
        self.queue.write_buffer(&self.input_buffer, 0, &gpu_data);
        
        // Créer bind group
        let bind_group_layout = self.compute_pipeline.get_bind_group_layout(0);
        let bind_group = self.device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("CFR Bind Group"),
            layout: &bind_group_layout,
            entries: &[
                wgpu::BindGroupEntry {
                    binding: 0,
                    resource: self.input_buffer.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 1,
                    resource: self.output_buffer.as_entire_binding(),
                },
            ],
        });

        // Encoder commandes GPU
        let mut encoder = self.device.create_command_encoder(&wgpu::CommandEncoderDescriptor {
            label: Some("CFR Compute Encoder"),
        });

        {
            let mut compute_pass = encoder.begin_compute_pass(&wgpu::ComputePassDescriptor {
                label: Some("CFR Compute Pass"),
                timestamp_writes: None,
            });
            
            compute_pass.set_pipeline(&self.compute_pipeline);
            compute_pass.set_bind_group(0, &bind_group, &[]);
            
            // Dispatch: 1 workgroup par state, 64 threads par workgroup
            let workgroups = (states.len() as u32 + 63) / 64;
            compute_pass.dispatch_workgroups(workgroups, 1, 1);
        }

        // Copier résultats vers staging buffer
        encoder.copy_buffer_to_buffer(
            &self.output_buffer, 0,
            &self.staging_buffer, 0,
            gpu_data.len() as u64
        );

        // Soumettre commandes
        self.queue.submit(std::iter::once(encoder.finish()));
        
        // Lire résultats
        let buffer_slice = self.staging_buffer.slice(..);
        let (sender, receiver) = futures_intrusive::channel::shared::oneshot_channel();
        buffer_slice.map_async(wgpu::MapMode::Read, move |result| {
            sender.send(result).unwrap();
        });
        
        self.device.poll(wgpu::Maintain::Wait);
        receiver.receive().await.unwrap()?;
        
        let results = buffer_slice.get_mapped_range();
        let convergence = self.parse_gpu_results(&results, states.len())?;
        
        // Nettoyer
        drop(results);
        self.staging_buffer.unmap();
        
        Ok(convergence)
    }

    /// Préparer données pour GPU
    fn prepare_gpu_data(&self, states: &[PokerState]) -> Result<Vec<u8>, String> {
        let mut gpu_data = Vec::new();
        
        for state in states.iter().take(self.config.batch_size) {
            // Encoder state pour GPU (format simple)
            let mut state_data = vec![0.0f32; 256]; // 256 floats par state
            
            // Index 0-1: hole cards
            if state.hole_cards.len() >= 2 {
                state_data[0] = state.hole_cards[0].rank as f32;
                state_data[1] = state.hole_cards[1].suit as f32;
            }
            
            // Index 2-6: community cards
            for (i, card) in state.community_cards.iter().enumerate().take(5) {
                state_data[2 + i * 2] = card.rank as f32;
                state_data[3 + i * 2] = card.suit as f32;
            }
            
            // Index 12-15: pot, stack, position, players
            state_data[12] = state.pot_size as f32;
            state_data[13] = state.stack_size as f32;
            state_data[14] = state.position as f32;
            state_data[15] = state.num_players as f32;
            
            // Index 16: betting round
            state_data[16] = match state.betting_round {
                BettingRound::Preflop => 0.0,
                BettingRound::Flop => 1.0,
                BettingRound::Turn => 2.0,
                BettingRound::River => 3.0,
            };
            
            // Index 17-20: actions disponibles (encodées comme bits)
            let mut actions_mask = 0.0f32;
            for action in &state.available_actions {
                actions_mask += match action {
                    Action::Fold => 1.0,
                    Action::Call => 2.0,
                    Action::Check => 4.0,
                    Action::Bet(_) => 8.0,
                    Action::Raise(_) => 16.0,
                    Action::AllIn => 32.0,
                };
            }
            state_data[17] = actions_mask;
            
            // Convertir vers bytes
            for &f in &state_data {
                gpu_data.extend_from_slice(&f.to_le_bytes());
            }
        }
        
        Ok(gpu_data)
    }

    /// Parser résultats GPU
    fn parse_gpu_results(&self, data: &[u8], num_states: usize) -> Result<f64, String> {
        if data.len() < num_states * 4 {
            return Err("Données GPU insuffisantes".to_string());
        }
        
        let mut total_convergence = 0.0;
        let mut count = 0;
        
        for i in 0..num_states {
            let offset = i * 256 * 4; // 256 floats * 4 bytes par float
            if offset + 4 <= data.len() {
                let convergence_bytes = [data[offset], data[offset + 1], data[offset + 2], data[offset + 3]];
                let convergence = f32::from_le_bytes(convergence_bytes);
                
                if convergence.is_finite() && convergence >= 0.0 {
                    total_convergence += convergence as f64;
                    count += 1;
                }
            }
        }
        
        if count > 0 {
            Ok(total_convergence / count as f64)
        } else {
            Ok(1.0) // Convergence par défaut
        }
    }

    /// Vérifier mémoire GPU disponible
    pub fn get_memory_info(&self) -> (u64, u64) {
        // Note: WGPU ne fournit pas directement ces infos
        // On estime basé sur la configuration
        let total_memory = (8 * 1024 * 1024 * 1024) as u64; // Assume 8GB GPU
        let used_memory = (self.config.memory_limit * total_memory as f32) as u64;
        (total_memory, used_memory)
    }
}