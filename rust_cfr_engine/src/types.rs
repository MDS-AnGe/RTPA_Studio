/// Types de base pour le CFR engine
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Représentation d'une carte
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Card {
    pub rank: u8,  // 2-14 (2, 3, ..., 9, 10, J, Q, K, A)
    pub suit: u8,  // 0-3 (Spades, Hearts, Diamonds, Clubs)
}

/// État d'une main de poker
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PokerState {
    pub hole_cards: Vec<Card>,
    pub community_cards: Vec<Card>,
    pub pot_size: f64,
    pub stack_size: f64,
    pub position: usize,
    pub num_players: usize,
    pub betting_round: BettingRound,
    pub available_actions: Vec<Action>,
}

/// Rounds de mise
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum BettingRound {
    Preflop = 0,
    Flop = 1,
    Turn = 2,
    River = 3,
}

/// Actions possibles
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Action {
    Fold,
    Call,
    Raise(f64),
    Check,
    Bet(f64),
    AllIn,
}

/// Information set pour CFR
#[derive(Debug, Clone, Hash, PartialEq, Eq)]
pub struct InformationSet {
    pub abstracted_cards: u64,  // Hash des cartes abstraites
    pub betting_sequence: Vec<u8>,  // Séquence des actions
    pub position: u8,
    pub round: BettingRound,
}

/// Stratégie CFR pour un information set
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Strategy {
    pub regret_sum: HashMap<Action, f64>,
    pub strategy_sum: HashMap<Action, f64>,
    pub current_strategy: HashMap<Action, f64>,
}

impl Strategy {
    pub fn new() -> Self {
        Self {
            regret_sum: HashMap::new(),
            strategy_sum: HashMap::new(),
            current_strategy: HashMap::new(),
        }
    }
    
    /// Calculate current strategy using regret matching
    pub fn get_current_strategy(&mut self, actions: &[Action]) -> HashMap<Action, f64> {
        let mut normalizing_sum = 0.0;
        let mut strategy = HashMap::new();
        
        // Calculate positive regrets
        for action in actions {
            let regret = self.regret_sum.get(action).unwrap_or(&0.0).max(0.0);
            strategy.insert(action.clone(), regret);
            normalizing_sum += regret;
        }
        
        // Normalize strategy
        if normalizing_sum > 0.0 {
            for (_, prob) in strategy.iter_mut() {
                *prob /= normalizing_sum;
            }
        } else {
            // Uniform strategy if no positive regrets
            let uniform_prob = 1.0 / actions.len() as f64;
            for action in actions {
                strategy.insert(action.clone(), uniform_prob);
            }
        }
        
        self.current_strategy = strategy.clone();
        strategy
    }
    
    /// Update regrets after iteration
    pub fn update_regret(&mut self, action: &Action, regret: f64) {
        *self.regret_sum.entry(action.clone()).or_insert(0.0) += regret;
    }
    
    /// Update strategy sum for average strategy calculation
    pub fn update_strategy(&mut self, action: &Action, probability: f64) {
        *self.strategy_sum.entry(action.clone()).or_insert(0.0) += probability;
    }
    
    /// Get average strategy over all iterations
    pub fn get_average_strategy(&self) -> HashMap<Action, f64> {
        let mut avg_strategy = HashMap::new();
        let total: f64 = self.strategy_sum.values().sum();
        
        if total > 0.0 {
            for (action, sum) in &self.strategy_sum {
                avg_strategy.insert(action.clone(), sum / total);
            }
        }
        
        avg_strategy
    }
}

/// Configuration du GPU
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuConfig {
    pub enabled: bool,
    pub memory_limit: f32,  // Fraction de mémoire GPU à utiliser (0.0-1.0)
    pub batch_size: usize,  // Taille des batches pour GPU
    pub prefer_gpu: bool,   // Préférer GPU même pour petits calculs
}

impl Default for GpuConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            memory_limit: 0.8,
            batch_size: 1000,
            prefer_gpu: true,
        }
    }
}

/// Configuration CFR
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CfrConfig {
    pub max_iterations: usize,
    pub convergence_threshold: f64,
    pub cpu_threads: usize,
    pub gpu_config: GpuConfig,
    pub abstraction_buckets: usize,
    pub sampling_enabled: bool,
}

impl Default for CfrConfig {
    fn default() -> Self {
        Self {
            max_iterations: 10000,
            convergence_threshold: 0.01,
            cpu_threads: num_cpus::get(),
            gpu_config: GpuConfig::default(),
            abstraction_buckets: 64,
            sampling_enabled: true,
        }
    }
}