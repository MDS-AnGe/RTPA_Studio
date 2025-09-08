/// Utilitaires pour CFR Engine
use std::time::{Duration, SystemTime, UNIX_EPOCH};

/// Performance timer
pub struct Timer {
    start: SystemTime,
}

impl Timer {
    pub fn new() -> Self {
        Self {
            start: SystemTime::now(),
        }
    }
    
    pub fn elapsed(&self) -> Duration {
        self.start.elapsed().unwrap_or(Duration::ZERO)
    }
    
    pub fn elapsed_ms(&self) -> f64 {
        self.elapsed().as_secs_f64() * 1000.0
    }
}

/// Logger simple pour Rust
pub struct Logger;

impl Logger {
    pub fn info(msg: &str) {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or(Duration::ZERO)
            .as_secs();
        println!("[{}] INFO: {}", timestamp, msg);
    }
    
    pub fn error(msg: &str) {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or(Duration::ZERO)
            .as_secs();
        eprintln!("[{}] ERROR: {}", timestamp, msg);
    }
    
    pub fn debug(msg: &str) {
        #[cfg(debug_assertions)]
        {
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or(Duration::ZERO)
                .as_secs();
            println!("[{}] DEBUG: {}", timestamp, msg);
        }
        #[cfg(not(debug_assertions))]
        {
            let _ = msg;
        }
    }
}

/// Métriques de performance
#[derive(Debug, Clone)]
pub struct PerformanceMetrics {
    pub iterations_per_second: f64,
    pub memory_usage_mb: f64,
    pub gpu_utilization: f64,
    pub convergence_rate: f64,
}

impl PerformanceMetrics {
    pub fn new() -> Self {
        Self {
            iterations_per_second: 0.0,
            memory_usage_mb: 0.0,
            gpu_utilization: 0.0,
            convergence_rate: 0.0,
        }
    }
    
    pub fn update(&mut self, iterations: usize, elapsed: Duration, convergence: f64) {
        if elapsed.as_secs_f64() > 0.0 {
            self.iterations_per_second = iterations as f64 / elapsed.as_secs_f64();
        }
        self.convergence_rate = convergence;
        
        // Estimer usage mémoire (très approximatif)
        self.memory_usage_mb = (iterations as f64 * 0.001).min(1024.0);
        
        // GPU utilization mockée pour l'instant
        self.gpu_utilization = if convergence > 0.1 { 75.0 } else { 25.0 };
    }
}

/// Gestionnaire de ressources
pub struct ResourceManager {
    max_memory_mb: f64,
    max_cpu_threads: usize,
    gpu_memory_limit: f32,
}

impl ResourceManager {
    pub fn new(max_memory_mb: f64, max_cpu_threads: usize, gpu_memory_limit: f32) -> Self {
        Self {
            max_memory_mb,
            max_cpu_threads,
            gpu_memory_limit,
        }
    }
    
    pub fn can_allocate(&self, required_memory_mb: f64) -> bool {
        required_memory_mb <= self.max_memory_mb
    }
    
    pub fn optimal_batch_size(&self, state_size_bytes: usize) -> usize {
        let max_batch_memory = self.max_memory_mb * 1024.0 * 1024.0 * 0.5; // 50% de la mémoire max
        let batch_size = (max_batch_memory / state_size_bytes as f64) as usize;
        batch_size.max(10).min(10000) // Entre 10 et 10k
    }
    
    pub fn get_cpu_threads(&self) -> usize {
        self.max_cpu_threads.min(num_cpus::get())
    }
}