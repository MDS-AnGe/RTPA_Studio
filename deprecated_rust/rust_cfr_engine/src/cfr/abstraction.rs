/// Gestionnaire d'abstraction pour CFR
use crate::types::*;
use std::collections::HashMap;
use ahash::AHasher;
use std::hash::{Hash, Hasher};

pub struct AbstractionManager {
    pub num_buckets: usize,
    hand_strength_cache: HashMap<Vec<Card>, f64>,
}

impl AbstractionManager {
    pub fn new(num_buckets: usize) -> Self {
        Self {
            num_buckets,
            hand_strength_cache: HashMap::new(),
        }
    }

    /// Convertir PokerState vers InformationSet abstrait
    pub fn state_to_infoset(&self, state: &PokerState) -> InformationSet {
        // Hash des cartes abstraites
        let abstracted_cards = self.abstract_cards(&state.hole_cards, &state.community_cards);
        
        // Séquence de mise simplifiée
        let betting_sequence = self.abstract_betting_sequence(state);
        
        InformationSet {
            abstracted_cards,
            betting_sequence,
            position: state.position as u8,
            round: state.betting_round.clone(),
        }
    }

    /// Abstraction des cartes en buckets
    fn abstract_cards(&self, hole_cards: &[Card], community_cards: &[Card]) -> u64 {
        let mut hasher = AHasher::default();
        
        // Évaluer force de main
        let hand_strength = self.evaluate_hand_strength(hole_cards, community_cards);
        
        // Bucketing basé sur force de main
        let bucket = ((hand_strength * self.num_buckets as f64) as usize).min(self.num_buckets - 1);
        
        // Hash du bucket + cartes importantes
        bucket.hash(&mut hasher);
        
        // Ajouter informations sur les suits (pour flush draws)
        let suit_info = self.get_suit_information(hole_cards, community_cards);
        suit_info.hash(&mut hasher);
        
        // Ajouter informations sur les straights
        let straight_info = self.get_straight_information(hole_cards, community_cards);
        straight_info.hash(&mut hasher);
        
        hasher.finish()
    }

    /// Évaluation simplifiée de force de main
    fn evaluate_hand_strength(&self, hole_cards: &[Card], community_cards: &[Card]) -> f64 {
        if hole_cards.is_empty() {
            return 0.0;
        }

        let mut all_cards = hole_cards.to_vec();
        all_cards.extend_from_slice(community_cards);
        
        // Cache lookup
        if let Some(&cached_strength) = self.hand_strength_cache.get(&all_cards) {
            return cached_strength;
        }

        let strength = match community_cards.len() {
            0 => self.evaluate_preflop(hole_cards),
            3..=5 => self.evaluate_postflop(&all_cards),
            _ => 0.0,
        };

        strength.clamp(0.0, 1.0)
    }

    /// Évaluation preflop basée sur ranges
    fn evaluate_preflop(&self, hole_cards: &[Card]) -> f64 {
        if hole_cards.len() < 2 {
            return 0.0;
        }

        let card1 = hole_cards[0];
        let card2 = hole_cards[1];
        
        let high_card = card1.rank.max(card2.rank);
        let low_card = card1.rank.min(card2.rank);
        let is_suited = card1.suit == card2.suit;
        let is_pair = card1.rank == card2.rank;

        // Système de scoring preflop
        let mut strength = 0.0;

        // Bonus pour paires
        if is_pair {
            strength += match high_card {
                14 => 0.95, // AA
                13 => 0.90, // KK
                12 => 0.85, // QQ
                11 => 0.75, // JJ
                10 => 0.65, // TT
                9 => 0.55,  // 99
                8 => 0.45,  // 88
                7 => 0.35,  // 77
                6 => 0.25,  // 66
                _ => 0.15,  // Petites paires
            };
        } else {
            // Cartes non appariées
            strength += (high_card as f64 - 2.0) / 12.0 * 0.6;
            strength += (low_card as f64 - 2.0) / 12.0 * 0.3;
            
            // Bonus suited
            if is_suited {
                strength += 0.1;
            }
            
            // Bonus connecteurs
            if high_card.abs_diff(low_card) <= 2 {
                strength += 0.05;
            }
            
            // Bonus broadway cards
            if high_card >= 10 && low_card >= 10 {
                strength += 0.1;
            }
        }

        strength.clamp(0.0, 1.0)
    }

    /// Évaluation postflop (simplifiée)
    fn evaluate_postflop(&self, all_cards: &[Card]) -> f64 {
        let mut strength = 0.0;

        // Vérifier paires, brelans, etc.
        let ranks = self.count_ranks(all_cards);
        let suits = self.count_suits(all_cards);

        // Paires et mieux
        let mut pairs = 0;
        let mut trips = 0;
        let mut quads = 0;
        
        for &count in ranks.values() {
            match count {
                2 => pairs += 1,
                3 => trips += 1,
                4 => quads += 1,
                _ => {}
            }
        }

        // Scoring par type de main
        if quads > 0 {
            strength = 0.95; // Four of a kind
        } else if trips > 0 && pairs > 0 {
            strength = 0.90; // Full house
        } else if self.has_flush(&suits) {
            strength = 0.85; // Flush
        } else if self.has_straight(all_cards) {
            strength = 0.80; // Straight
        } else if trips > 0 {
            strength = 0.75; // Three of a kind
        } else if pairs >= 2 {
            strength = 0.65; // Two pair
        } else if pairs == 1 {
            strength = 0.45; // One pair
        } else {
            // High card
            let highest = all_cards.iter().map(|c| c.rank).max().unwrap_or(2);
            strength = (highest as f64 - 2.0) / 12.0 * 0.3;
        }

        strength
    }

    /// Compter occurrences de chaque rang
    fn count_ranks(&self, cards: &[Card]) -> HashMap<u8, usize> {
        let mut ranks = HashMap::new();
        for card in cards {
            *ranks.entry(card.rank).or_insert(0) += 1;
        }
        ranks
    }

    /// Compter occurrences de chaque couleur
    fn count_suits(&self, cards: &[Card]) -> HashMap<u8, usize> {
        let mut suits = HashMap::new();
        for card in cards {
            *suits.entry(card.suit).or_insert(0) += 1;
        }
        suits
    }

    /// Vérifier présence de flush
    fn has_flush(&self, suits: &HashMap<u8, usize>) -> bool {
        suits.values().any(|&count| count >= 5)
    }

    /// Vérifier présence de straight
    fn has_straight(&self, cards: &[Card]) -> bool {
        let mut ranks: Vec<u8> = cards.iter().map(|c| c.rank).collect();
        ranks.sort_unstable();
        ranks.dedup();

        // Vérifier séquences de 5
        for i in 0..=ranks.len().saturating_sub(5) {
            let mut consecutive = true;
            for j in 1..5 {
                if ranks[i + j] != ranks[i + j - 1] + 1 {
                    consecutive = false;
                    break;
                }
            }
            if consecutive {
                return true;
            }
        }

        // Cas spécial: A-2-3-4-5 (wheel)
        if ranks.contains(&14) && ranks.contains(&2) && ranks.contains(&3) && ranks.contains(&4) && ranks.contains(&5) {
            return true;
        }

        false
    }

    /// Information sur les couleurs (flush draws)
    fn get_suit_information(&self, hole_cards: &[Card], community_cards: &[Card]) -> u32 {
        let all_cards = [hole_cards, community_cards].concat();
        let suits = self.count_suits(&all_cards);
        
        // Encoder informations flush/flush draw
        let max_suit_count = suits.values().max().unwrap_or(&0);
        match max_suit_count {
            5.. => 4, // Flush made
            4 => 3,   // Flush draw
            3 => 2,   // Backdoor flush draw  
            2 => 1,   // Suited hole cards
            _ => 0,   // No flush potential
        }
    }

    /// Information sur les straights
    fn get_straight_information(&self, hole_cards: &[Card], community_cards: &[Card]) -> u32 {
        let all_cards = [hole_cards, community_cards].concat();
        
        if self.has_straight(&all_cards) {
            return 4; // Straight made
        }
        
        // Vérifier straight draws (simplifié)
        let mut ranks: Vec<u8> = all_cards.iter().map(|c| c.rank).collect();
        ranks.sort_unstable();
        ranks.dedup();
        
        // Open-ended straight draw detection (simplifié)
        for window in ranks.windows(4) {
            let mut consecutive = true;
            for i in 1..4 {
                if window[i] != window[i-1] + 1 {
                    consecutive = false;
                    break;
                }
            }
            if consecutive {
                return 3; // Open-ended straight draw
            }
        }
        
        // Gutshot (très simplifié)
        if ranks.len() >= 3 {
            return 1; // Possible gutshot
        }
        
        0 // No straight potential
    }

    /// Simplifier séquence de mise
    fn abstract_betting_sequence(&self, state: &PokerState) -> Vec<u8> {
        // Pour l'instant, séquence très simple basée sur pot size ratio
        let pot_ratio = if state.stack_size > 0.0 {
            (state.pot_size / state.stack_size * 10.0) as u8
        } else {
            255 // All-in
        };
        
        vec![
            state.betting_round as u8,
            pot_ratio.min(10), // Clamp à 10 pour limiter explosion
            state.position as u8 % 10, // Position relative
        ]
    }
}