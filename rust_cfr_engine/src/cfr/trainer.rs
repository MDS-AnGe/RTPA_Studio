/// CFR Trainer haute performance
use crate::types::*;
use crate::cfr::CfrEngine;
use rayon::prelude::*;
use std::sync::{Arc, atomic::{AtomicUsize, AtomicBool, Ordering}};
use std::time::{Duration, Instant};
use tokio::time::sleep;

pub struct CfrTrainer {
    engine: Arc<CfrEngine>,
    config: CfrConfig,
    is_training: AtomicBool,
    iterations_completed: AtomicUsize,
    training_start_time: Arc<std::sync::Mutex<Option<Instant>>>,
}

impl CfrTrainer {
    pub fn new(engine: Arc<CfrEngine>, config: CfrConfig) -> Self {
        Self {
            engine,
            config,
            is_training: AtomicBool::new(false),
            iterations_completed: AtomicUsize::new(0),
            training_start_time: Arc::new(std::sync::Mutex::new(None)),
        }
    }

    /// Démarrer entraînement asynchrone  
    pub async fn start_training(&self, states: Vec<PokerState>) -> Result<(), String> {
        if self.is_training.load(Ordering::Relaxed) {
            return Err("Training déjà en cours".into());
        }

        self.is_training.store(true, Ordering::Relaxed);
        self.iterations_completed.store(0, Ordering::Relaxed);
        
        // Enregistrer heure de début
        if let Ok(mut start_time) = self.training_start_time.lock() {
            *start_time = Some(Instant::now());
        }

        println!("🚀 Démarrage CFR training Rust:");
        println!("   • States: {}", states.len());
        println!("   • Max iterations: {}", self.config.max_iterations);
        println!("   • GPU: {}", self.engine.gpu_compute.is_some());
        println!("   • CPU threads: {}", self.config.cpu_threads);

        // Boucle d'entraînement principale
        let mut iteration = 0;
        let mut best_convergence = f64::INFINITY;
        let convergence_history = Arc::new(std::sync::Mutex::new(Vec::new()));

        while self.is_training.load(Ordering::Relaxed) && iteration < self.config.max_iterations {
            let iter_start = Instant::now();
            
            // Échantillonner batch pour cette itération
            let batch = self.sample_training_batch(&states, 100).map_err(|e| e.to_string())?;
            
            // Entraînement CFR sur batch
            let convergence = self.engine.train_batch(&batch).await.map_err(|e| e.to_string())?;
            
            // Mise à jour métriques
            self.iterations_completed.fetch_add(1, Ordering::Relaxed);
            iteration += 1;
            
            // Suivi convergence
            if let Ok(mut history) = convergence_history.lock() {
                history.push(convergence);
                if history.len() > 1000 {
                    history.remove(0); // Garder historique limité
                }
            }
            
            if convergence < best_convergence {
                best_convergence = convergence;
            }
            
            // Log progression
            if iteration % 1000 == 0 {
                let iter_time = iter_start.elapsed();
                let avg_convergence = self.get_average_convergence(&convergence_history, 100);
                
                println!("🔄 Iteration {}: convergence={:.4f}, avg={:.4f}, temps={:.2}ms", 
                    iteration, convergence, avg_convergence, iter_time.as_secs_f64() * 1000.0);
                
                // Vérifier convergence
                if avg_convergence < self.config.convergence_threshold {
                    println!("✅ Convergence atteinte à l'itération {}", iteration);
                    break;
                }
            }
            
            // Pause courte pour éviter overload
            if iteration % 10 == 0 {
                sleep(Duration::from_millis(1)).await;
            }
        }

        self.is_training.store(false, Ordering::Relaxed);
        
        let total_time = if let Ok(start_time) = self.training_start_time.lock() {
            start_time.as_ref().map(|t| t.elapsed()).unwrap_or(Duration::ZERO)
        } else {
            Duration::ZERO
        };

        println!("🎯 Training terminé:");
        println!("   • Itérations: {}", iteration);
        println!("   • Temps total: {:.2}s", total_time.as_secs_f64());
        println!("   • Convergence finale: {:.4f}", best_convergence);
        println!("   • Débit: {:.1} iter/s", iteration as f64 / total_time.as_secs_f64());

        Ok(())
    }

    /// Arrêter entraînement
    pub fn stop_training(&self) {
        self.is_training.store(false, Ordering::Relaxed);
        println!("⏹️ Arrêt training demandé");
    }

    /// Échantillonner batch de training
    fn sample_training_batch(&self, states: &[PokerState], batch_size: usize) -> Result<Vec<PokerState>, String> {
        use rand::seq::SliceRandom;
        use rand::thread_rng;
        
        let mut rng = thread_rng();
        let sample_size = batch_size.min(states.len());
        
        let sampled: Vec<PokerState> = states
            .choose_multiple(&mut rng, sample_size)
            .cloned()
            .collect();
            
        Ok(sampled)
    }

    /// Calculer convergence moyenne
    fn get_average_convergence(&self, history: &Arc<std::sync::Mutex<Vec<f64>>>, window: usize) -> f64 {
        if let Ok(history) = history.lock() {
            let start_idx = history.len().saturating_sub(window);
            let recent_values: Vec<f64> = history[start_idx..].to_vec();
            
            if recent_values.is_empty() {
                1.0
            } else {
                recent_values.iter().sum::<f64>() / recent_values.len() as f64
            }
        } else {
            1.0
        }
    }

    /// Obtenir statistiques training
    pub fn get_training_stats(&self) -> TrainingStats {
        let iterations = self.iterations_completed.load(Ordering::Relaxed);
        let is_training = self.is_training.load(Ordering::Relaxed);
        
        let (elapsed, eta) = if let Ok(start_time) = self.training_start_time.lock() {
            if let Some(start) = *start_time {
                let elapsed = start.elapsed();
                let rate = if elapsed.as_secs() > 0 {
                    iterations as f64 / elapsed.as_secs_f64()
                } else {
                    0.0
                };
                
                let remaining_iter = self.config.max_iterations.saturating_sub(iterations);
                let eta = if rate > 0.0 {
                    Duration::from_secs_f64(remaining_iter as f64 / rate)
                } else {
                    Duration::ZERO
                };
                
                (elapsed, eta)
            } else {
                (Duration::ZERO, Duration::ZERO)
            }
        } else {
            (Duration::ZERO, Duration::ZERO)
        };

        let (engine_iterations, convergence) = self.engine.get_convergence_stats();
        
        TrainingStats {
            iterations,
            max_iterations: self.config.max_iterations,
            is_training,
            elapsed_time: elapsed,
            estimated_time_remaining: eta,
            convergence_metric: convergence,
            engine_iterations,
        }
    }

    /// Générer nouvelles hands pour training
    pub fn generate_training_hands(&self, count: usize) -> Result<Vec<PokerState>, String> {
        use rand::{thread_rng, Rng};
        use rand::seq::SliceRandom;
        
        let mut rng = thread_rng();
        let mut hands = Vec::with_capacity(count);
        
        // Distribution des rounds de mise
        let preflop_ratio = 0.4;
        let flop_ratio = 0.3;
        let turn_ratio = 0.2;
        let river_ratio = 0.1;
        
        let preflop_count = (count as f64 * preflop_ratio) as usize;
        let flop_count = (count as f64 * flop_ratio) as usize;
        let turn_count = (count as f64 * turn_ratio) as usize;
        let river_count = count - preflop_count - flop_count - turn_count;
        
        // Génération parallèle
        let hands_preflop: Vec<PokerState> = (0..preflop_count)
            .into_par_iter()
            .map(|_| self.generate_random_state(BettingRound::Preflop))
            .collect();
            
        let hands_flop: Vec<PokerState> = (0..flop_count)
            .into_par_iter()
            .map(|_| self.generate_random_state(BettingRound::Flop))
            .collect();
            
        let hands_turn: Vec<PokerState> = (0..turn_count)
            .into_par_iter()
            .map(|_| self.generate_random_state(BettingRound::Turn))
            .collect();
            
        let hands_river: Vec<PokerState> = (0..river_count)
            .into_par_iter()
            .map(|_| self.generate_random_state(BettingRound::River))
            .collect();
        
        hands.extend(hands_preflop);
        hands.extend(hands_flop);
        hands.extend(hands_turn);
        hands.extend(hands_river);
        
        // Mélanger
        hands.shuffle(&mut rng);
        
        Ok(hands)
    }

    /// Générer state aléatoire pour round donné
    fn generate_random_state(&self, round: BettingRound) -> PokerState {
        use rand::{thread_rng, Rng};
        let mut rng = thread_rng();
        
        // Générer cartes hole aléatoires
        let hole_cards = vec![
            Card { rank: rng.gen_range(2..=14), suit: rng.gen_range(0..4) },
            Card { rank: rng.gen_range(2..=14), suit: rng.gen_range(0..4) },
        ];
        
        // Générer cartes communautaires selon round
        let community_cards = match round {
            BettingRound::Preflop => vec![],
            BettingRound::Flop => (0..3).map(|_| Card {
                rank: rng.gen_range(2..=14),
                suit: rng.gen_range(0..4)
            }).collect(),
            BettingRound::Turn => (0..4).map(|_| Card {
                rank: rng.gen_range(2..=14),
                suit: rng.gen_range(0..4)
            }).collect(),
            BettingRound::River => (0..5).map(|_| Card {
                rank: rng.gen_range(2..=14),
                suit: rng.gen_range(0..4)
            }).collect(),
        };
        
        // Paramètres aléatoires réalistes
        let stack_size = rng.gen_range(50.0..=200.0);
        let pot_size = rng.gen_range(5.0..=50.0);
        let position = rng.gen_range(0..9);
        let num_players = rng.gen_range(2..=9);
        
        // Actions disponibles selon contexte
        let available_actions = if stack_size > pot_size {
            vec![
                Action::Fold,
                Action::Call,
                Action::Raise(pot_size * 0.5),
                Action::Raise(pot_size),
            ]
        } else {
            vec![Action::Fold, Action::Call, Action::AllIn]
        };
        
        PokerState {
            hole_cards,
            community_cards,
            pot_size,
            stack_size,
            position,
            num_players,
            betting_round: round,
            available_actions,
        }
    }
}

/// Statistiques d'entraînement
#[derive(Debug, Clone)]
pub struct TrainingStats {
    pub iterations: usize,
    pub max_iterations: usize,
    pub is_training: bool,
    pub elapsed_time: Duration,
    pub estimated_time_remaining: Duration,
    pub convergence_metric: f64,
    pub engine_iterations: usize,
}