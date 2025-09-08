// Types simplifiés pour CFR Engine RTPA - Version fonctionnelle
use std::collections::HashMap;

/// Configuration CFR simplifiée
#[derive(Debug, Clone)]
pub struct CfrConfig {
    pub max_iterations: usize,
    pub convergence_threshold: f64,
    pub exploration_rate: f64,
    pub discount_factor: f64,
}

impl Default for CfrConfig {
    fn default() -> Self {
        Self {
            max_iterations: 10000,
            convergence_threshold: 0.01,
            exploration_rate: 0.1,
            discount_factor: 0.95,
        }
    }
}

/// État de jeu simplifié
#[derive(Debug, Clone)]
pub struct GameState {
    pub pot_size: f64,
    pub stack_size: f64,
    pub position: usize,
    pub num_players: usize,
    pub betting_round: String,
}

impl GameState {
    pub fn new() -> Self {
        Self {
            pot_size: 10.0,
            stack_size: 100.0,
            position: 0,
            num_players: 2,
            betting_round: "preflop".to_string(),
        }
    }
}

/// Information système
#[derive(Debug, Clone)]
pub struct SystemInfo {
    pub cpu_threads: usize,
    pub total_memory: u64,
    pub available_memory: u64,
}

impl SystemInfo {
    pub fn new() -> Self {
        Self {
            cpu_threads: get_cpu_count(),
            total_memory: 1024 * 1024 * 1024, // 1GB par défaut
            available_memory: 512 * 1024 * 1024, // 512MB par défaut
        }
    }
}

// Utilités
pub fn get_cpu_count() -> usize {
    // Estimation simple sans dépendance externe
    match std::thread::available_parallelism() {
        Ok(count) => count.get(),
        Err(_) => 1,
    }
}