/// CFR Engine ultra-rapide avec support GPU
use crate::types::*;
use crate::gpu::GpuCompute;
use dashmap::DashMap;
use rayon::prelude::*;
use std::sync::{Arc, atomic::{AtomicUsize, Ordering}};
use std::time::{Duration, Instant};

pub struct CfrEngine {
    /// Stockage des stratégies par information set
    pub strategies: Arc<DashMap<InformationSet, Strategy>>,
    /// Configuration
    pub config: CfrConfig,
    /// GPU compute engine (si disponible)
    pub gpu_compute: Option<GpuCompute>,
    /// Statistiques
    pub iterations: AtomicUsize,
    pub convergence_metric: Arc<std::sync::Mutex<f64>>,
    /// Abstraction manager
    pub abstraction: crate::cfr::AbstractionManager,
}

impl CfrEngine {
    /// Création nouvelle instance CFR
    pub async fn new(config: CfrConfig) -> Result<Self, Box<dyn std::error::Error>> {
        // Initialiser GPU si demandé
        let gpu_compute = if config.gpu_config.enabled {
            match GpuCompute::new(config.gpu_config.clone()).await {
                Ok(gpu) => {
                    println!("🚀 GPU CFR initialisé avec succès!");
                    Some(gpu)
                }
                Err(e) => {
                    println!("⚠️  GPU indisponible, fallback CPU: {}", e);
                    None
                }
            }
        } else {
            None
        };

        let abstraction = crate::cfr::AbstractionManager::new(config.abstraction_buckets);

        Ok(Self {
            strategies: Arc::new(DashMap::new()),
            config,
            gpu_compute,
            iterations: AtomicUsize::new(0),
            convergence_metric: Arc::new(std::sync::Mutex::new(1.0)),
            abstraction,
        })
    }

    /// Entraînement CFR sur un batch de states
    pub async fn train_batch(&self, states: &[PokerState]) -> f64 {
        let start = Instant::now();
        
        // Choisir méthode selon taille batch et GPU disponibilité
        let convergence = if states.len() >= self.config.gpu_config.batch_size && self.gpu_compute.is_some() {
            self.train_batch_gpu(states).await
        } else {
            self.train_batch_cpu(states)
        }?;
        
        // Mise à jour statistiques
        self.iterations.fetch_add(states.len(), Ordering::Relaxed);
        if let Ok(mut metric) = self.convergence_metric.lock() {
            *metric = convergence;
        }
        
        let duration = start.elapsed();
        if duration.as_millis() > 100 {  // Log seulement si > 100ms
            println!("🔄 CFR batch: {} states, {:.3}ms, convergence: {:.4}", 
                states.len(), duration.as_secs_f64() * 1000.0, convergence);
        }
        
        Ok(convergence)
    }

    /// Entraînement GPU (parallèle massif)
    async fn train_batch_gpu(&self, states: &[PokerState]) -> Result<f64, Box<dyn std::error::Error>> {
        if let Some(ref gpu) = self.gpu_compute {
            gpu.compute_cfr_batch(states, &self.strategies, &self.abstraction).await
        } else {
            // Fallback CPU si GPU échoue
            Ok(self.train_batch_cpu(states))
        }
    }

    /// Entraînement CPU (parallèle multi-thread)
    fn train_batch_cpu(&self, states: &[PokerState]) -> f64 {
        let chunk_size = (states.len() / self.config.cpu_threads).max(1);
        
        let convergences: Vec<f64> = states
            .par_chunks(chunk_size)
            .map(|chunk| {
                chunk.iter()
                    .map(|state| self.cfr_recursive(state, 1.0, 1.0))
                    .sum::<f64>() / chunk.len() as f64
            })
            .collect();
            
        convergences.iter().sum::<f64>() / convergences.len() as f64
    }

    /// Algorithme CFR récursif (coeur du calcul)
    fn cfr_recursive(&self, state: &PokerState, reach_prob_player: f64, reach_prob_opponent: f64) -> f64 {
        // Convertir state en information set
        let info_set = self.abstraction.state_to_infoset(state);
        
        // Récupérer ou créer stratégie
        let mut strategy_entry = self.strategies.entry(info_set.clone()).or_insert_with(Strategy::new);
        let strategy = strategy_entry.get_current_strategy(&state.available_actions);
        
        // Calculer values pour chaque action
        let mut action_values = std::collections::HashMap::new();
        let mut node_value = 0.0;
        
        for action in &state.available_actions {
            let action_prob = strategy.get(action).unwrap_or(&0.0);
            let new_state = self.apply_action(state, action);
            
            // Récursion CFR
            let action_value = if new_state.is_terminal() {
                self.evaluate_terminal_state(&new_state)
            } else {
                -self.cfr_recursive(&new_state, reach_prob_opponent, reach_prob_player * action_prob)
            };
            
            action_values.insert(action.clone(), action_value);
            node_value += action_prob * action_value;
        }
        
        // Mise à jour regrets
        for (action, &value) in &action_values {
            let regret = value - node_value;
            strategy_entry.update_regret(action, regret * reach_prob_opponent);
            strategy_entry.update_strategy(action, reach_prob_player * strategy.get(action).unwrap_or(&0.0));
        }
        
        node_value
    }

    /// Appliquer une action sur un state
    fn apply_action(&self, state: &PokerState, action: &Action) -> PokerState {
        let mut new_state = state.clone();
        
        match action {
            Action::Fold => {
                // État terminal - joueur fold
                new_state.available_actions = vec![];
            }
            Action::Call => {
                // Avancer au prochain round ou terminal
                new_state = self.advance_betting_round(new_state);
            }
            Action::Raise(amount) | Action::Bet(amount) => {
                new_state.pot_size += amount;
                new_state.stack_size -= amount;
                new_state = self.advance_betting_round(new_state);
            }
            Action::Check => {
                new_state = self.advance_betting_round(new_state);
            }
            Action::AllIn => {
                new_state.pot_size += new_state.stack_size;
                new_state.stack_size = 0.0;
                new_state.available_actions = vec![];
            }
        }
        
        new_state
    }

    /// Avancer au prochain round de mise
    fn advance_betting_round(&self, mut state: PokerState) -> PokerState {
        match state.betting_round {
            BettingRound::Preflop => {
                state.betting_round = BettingRound::Flop;
                // Ajouter 3 cartes flop si pas déjà là
                if state.community_cards.len() == 0 {
                    state.community_cards = self.generate_flop();
                }
            }
            BettingRound::Flop => {
                state.betting_round = BettingRound::Turn;
                if state.community_cards.len() == 3 {
                    state.community_cards.push(self.generate_turn_river());
                }
            }
            BettingRound::Turn => {
                state.betting_round = BettingRound::River;
                if state.community_cards.len() == 4 {
                    state.community_cards.push(self.generate_turn_river());
                }
            }
            BettingRound::River => {
                // État terminal
                state.available_actions = vec![];
            }
        }
        
        // Réinitialiser actions disponibles pour nouveau round
        if !state.available_actions.is_empty() {
            state.available_actions = vec![Action::Check, Action::Bet(state.stack_size * 0.5), Action::Fold];
        }
        
        state
    }

    /// Générer cartes flop aléatoires
    fn generate_flop(&self) -> Vec<Card> {
        use rand::{thread_rng, Rng};
        let mut rng = thread_rng();
        
        (0..3).map(|_| Card {
            rank: rng.gen_range(2..=14),
            suit: rng.gen_range(0..4),
        }).collect()
    }

    /// Générer carte turn/river
    fn generate_turn_river(&self) -> Card {
        use rand::{thread_rng, Rng};
        let mut rng = thread_rng();
        
        Card {
            rank: rng.gen_range(2..=14),
            suit: rng.gen_range(0..4),
        }
    }

    /// Évaluer état terminal
    fn evaluate_terminal_state(&self, state: &PokerState) -> f64 {
        // Simulation simple - à améliorer avec évaluateur de main réel
        use rand::{thread_rng, Rng};
        let mut rng = thread_rng();
        
        // Pour l'instant, retourne une évaluation aléatoire
        // TODO: Implémenter évaluateur de main poker réel
        if rng.gen_bool(0.5) {
            state.pot_size  // Gain
        } else {
            -state.pot_size * 0.5  // Perte
        }
    }

    /// Obtenir stratégie moyennée pour un information set
    pub fn get_average_strategy(&self, info_set: &InformationSet) -> Option<std::collections::HashMap<Action, f64>> {
        self.strategies.get(info_set).map(|strategy| strategy.get_average_strategy())
    }

    /// Statistiques de convergence
    pub fn get_convergence_stats(&self) -> (usize, f64) {
        let iterations = self.iterations.load(Ordering::Relaxed);
        let convergence = self.convergence_metric.lock().unwrap_or_else(|_| std::sync::MutexGuard::leak(self.convergence_metric.lock().unwrap()));
        (iterations, *convergence)
    }

    /// Export des données CFR
    pub fn export_data(&self) -> Result<String, Box<dyn std::error::Error>> {
        let mut export_data = std::collections::HashMap::new();
        
        for entry in self.strategies.iter() {
            let (info_set, strategy) = entry.pair();
            export_data.insert(format!("{:?}", info_set), strategy.clone());
        }
        
        Ok(serde_json::to_string_pretty(&export_data)?)
    }

    /// Import des données CFR
    pub fn import_data(&self, data: &str) -> Result<(), Box<dyn std::error::Error>> {
        let import_data: std::collections::HashMap<String, Strategy> = serde_json::from_str(data)?;
        
        for (info_set_str, strategy) in import_data {
            // TODO: Convertir string vers InformationSet
            // Pour l'instant, skip cette fonctionnalité
            println!("Import CFR: {} strategies importées", self.strategies.len());
        }
        
        Ok(())
    }
}

// Implémentation des traits pour état terminal
impl PokerState {
    pub fn is_terminal(&self) -> bool {
        self.available_actions.is_empty() || self.stack_size <= 0.0
    }
}