"""
Moteur CFR/CFR+ pour calculs Nash en temps réel
Implémentation optimisée pour le poker Texas Hold'em No Limit
"""

import numpy as np
import math
import time
import threading
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import itertools
import multiprocessing as mp

# GPU/CPU Acceleration support
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

from numba import jit, prange
from ..utils.logger import get_logger

@dataclass
class PokerState:
    """État de poker pour CFR"""
    street: int  # 0=preflop, 1=flop, 2=turn, 3=river
    hero_cards: Tuple[str, str]
    board_cards: List[str]
    pot_size: float
    hero_stack: float
    position: int
    num_players: int
    current_bet: float
    action_history: List[str]
    table_type: str  # "cashgame" ou "tournament"

@dataclass
class ActionSpace:
    """Espace d'actions possibles"""
    fold: bool = True
    check_call: bool = True
    bet_sizes: Optional[List[float]] = None  # En pourcentage du pot
    
    def __post_init__(self):
        if self.bet_sizes is None:
            self.bet_sizes = [0.25, 0.33, 0.5, 0.66, 0.75, 1.0, 1.5, 2.0]  # Pourcentages du pot

class CFREngine:
    """Moteur CFR+ optimisé pour poker temps réel avec accélération GPU/CPU"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Configuration d'accélération GPU/CPU
        self.device = self._setup_compute_device()
        self.use_acceleration = TORCH_AVAILABLE
        self.gpu_enabled = False  # Sera configuré via l'interface
        self.gpu_memory_limit = 0.8  # 80% max mémoire GPU
        self.cpu_threads = mp.cpu_count()
        
        # Tables de regrets et stratégies
        self.regret_sum = defaultdict(lambda: defaultdict(float))
        self.strategy_sum = defaultdict(lambda: defaultdict(float))
        self.current_strategy = defaultdict(lambda: defaultdict(float))
        
        # Cache tenseurs pour optimisation
        self._tensor_cache = {}
        self._computation_cache = {}
        
        # Configuration CFR
        self.iterations = 0
        self.iterations_count = 0  # Pour compatibilité avec export/import
        self.total_training_time = 0.0  # Temps total d'entraînement
        self.discount_factor = 0.95
        self.exploration_rate = 0.1
        
        # Nouveaux composants pour entraînement massif
        self.cfr_trainer = None
        self.auto_training_enabled = True
        self.training_target_reached = False
        
        # Abstractions
        self.card_abstraction = CardAbstraction()
        self.action_abstraction = ActionAbstraction()
        
        # Cache des calculs
        self.equity_cache = {}
        self.abstraction_cache = {}
        
        # Multithreading optimisé
        self.calculation_lock = threading.RLock()
        self.background_thread = None
        self.is_running = False
        
        # Configuration du threading optimal
        if TORCH_AVAILABLE:
            torch.set_num_threads(self.cpu_threads)
            torch.set_num_interop_threads(self.cpu_threads // 2)
        
        # Modèle Deep CFR (optionnel)
        self.deep_cfr_enabled = False
        self.advantage_net = None
        self.strategy_net = None
        
        # Initialisation de l'entraîneur CFR (sera fait plus tard pour éviter import circulaire)
        self.cfr_trainer = None
        
        # Initialiser l'accélérateur GPU
        self._init_gpu_accelerator()
        
        self.logger.info("CFREngine initialisé avec entraînement automatique")
        if self.use_acceleration:
            self.logger.info(f"Accélération disponible: {self.device}")
        else:
            self.logger.warning("PyTorch non disponible - utilisation CPU uniquement")
    
    def _setup_compute_device(self):
        """Configure le device optimal pour les calculs"""
        if not TORCH_AVAILABLE:
            return "cpu"
        
        # Vérifier disponibilité GPU
        if torch.cuda.is_available():
            device = torch.device("cuda:0")
            gpu_props = torch.cuda.get_device_properties(0)
            self.logger.info(f"GPU détecté: {gpu_props.name} ({gpu_props.total_memory // 1024**2} MB)")
            return device
        else:
            device = torch.device("cpu")
            self.logger.info(f"Utilisation CPU optimisé: {self.cpu_threads} threads")
            return device
    
    def set_gpu_enabled(self, enabled: bool, memory_limit: float = 0.8):
        """Active/désactive l'utilisation du GPU"""
        self.gpu_enabled = enabled and torch.cuda.is_available() if TORCH_AVAILABLE else False
        self.gpu_memory_limit = memory_limit
        
        if self.gpu_enabled:
            self.device = torch.device("cuda:0")
            # Limiter l'utilisation mémoire GPU
            torch.cuda.set_per_process_memory_fraction(memory_limit)
            self.logger.info(f"GPU activé avec limite mémoire: {memory_limit*100:.0f}%")
        else:
            self.device = torch.device("cpu")
            self.logger.info("Utilisation CPU forcée")
        
        # Vider les caches
        self._clear_tensor_cache()
    
    def _clear_tensor_cache(self):
        """Vide les caches de tenseurs"""
        self._tensor_cache.clear()
        self._computation_cache.clear()
        if self.gpu_enabled and torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def get_gpu_memory_usage(self):
        """Retourne l'utilisation mémoire GPU"""
        if not self.gpu_enabled or not torch.cuda.is_available():
            return {"available": False, "used": 0, "total": 0}
        
        used = torch.cuda.memory_allocated() / 1024**2
        total = torch.cuda.get_device_properties(0).total_memory / 1024**2
        return {
            "available": True,
            "used": used,
            "total": total,
            "percent": (used / total) * 100
        }
    
    @jit(nopython=True)
    def _compute_regrets_numba(self, utilities, strategy_probs):
        """Calcul optimisé des regrets avec Numba"""
        regrets = np.zeros_like(utilities)
        ev = np.sum(utilities * strategy_probs)
        
        for i in prange(len(utilities)):
            regrets[i] = utilities[i] - ev
        
        return regrets
    
    def _compute_regrets_torch(self, utilities_tensor, strategy_tensor):
        """Calcul optimisé des regrets avec PyTorch"""
        if not self.use_acceleration:
            return None
        
        # Calculer la valeur espérée
        ev = torch.sum(utilities_tensor * strategy_tensor)
        
        # Calculer les regrets
        regrets = utilities_tensor - ev
        
        return regrets.cpu().numpy()
    
    def _init_gpu_accelerator(self):
        """Initialise l'accélérateur GPU/CPU"""
        try:
            from .gpu_accelerator import GPUAccelerator, AccelerationConfig
            
            config = AccelerationConfig(
                gpu_enabled=self.gpu_enabled,
                gpu_memory_limit=self.gpu_memory_limit,
                cpu_threads=self.cpu_threads
            )
            
            self.gpu_accelerator = GPUAccelerator(config)
            self.logger.info("Accélérateur GPU/CPU initialisé")
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation accélérateur: {e}")
            self.gpu_accelerator = None
    
    def update_gpu_settings(self, gpu_enabled: bool, memory_limit: float):
        """Met à jour les paramètres GPU depuis l'interface"""
        self.set_gpu_enabled(gpu_enabled, memory_limit)
        
        if self.gpu_accelerator:
            self.gpu_accelerator.update_config(gpu_enabled, memory_limit)
            self.logger.info(f"Paramètres GPU mis à jour: enabled={gpu_enabled}, memory={memory_limit*100:.0f}%")
    
    def get_acceleration_stats(self):
        """Retourne les statistiques d'accélération"""
        if self.gpu_accelerator:
            return self.gpu_accelerator.get_performance_stats()
        return {}
    
    def init_trainer(self):
        """Initialise l'entraîneur CFR (séparé pour éviter import circulaire)"""
        try:
            from .cfr_trainer import CFRTrainer
            self.cfr_trainer = CFRTrainer(self)
            
            # Chargement automatique des mains historiques
            self._load_historical_hands()
            
            # Démarrage de l'entraînement automatique
            if self.auto_training_enabled and not self.training_target_reached:
                self._start_auto_training()
                
            # Démarrage de la génération continue
            self._start_continuous_generation()
                
        except Exception as e:
            self.logger.error(f"Erreur initialisation trainer: {e}")
    
    def _load_historical_hands(self):
        """Charge automatiquement les mains historiques disponibles"""
        try:
            import os
            hand_files = []
            
            # Recherche des fichiers de mains dans attached_assets
            assets_dir = "attached_assets"
            if os.path.exists(assets_dir):
                for file in os.listdir(assets_dir):
                    if file.startswith("All_Hands_part") and file.endswith(".txt"):
                        hand_files.append(os.path.join(assets_dir, file))
            
            if hand_files and self.cfr_trainer:
                self.logger.info(f"Chargement de {len(hand_files)} fichiers de mains...")
                total_loaded = self.cfr_trainer.load_historical_hands(hand_files)
                self.logger.info(f"Chargé {total_loaded} mains historiques")
            
        except Exception as e:
            self.logger.error(f"Erreur chargement mains historiques: {e}")
    
    def _start_auto_training(self):
        """Démarre l'entraînement automatique en arrière-plan"""
        try:
            if self.cfr_trainer:
                # Génération de dataset supplémentaire si nécessaire
                if len(self.cfr_trainer.training_hands) < 50000:
                    self.logger.info("Génération de mains supplémentaires pour entraînement...")
                    self.cfr_trainer.generate_training_dataset(200000)
                
                # Démarrage entraînement intensif
                self.logger.info("Démarrage entraînement CFR automatique...")
                success = self.cfr_trainer.start_intensive_training(
                    target_iterations=100000,
                    target_convergence=0.01
                )
                
                if success:
                    self.logger.info("Entraînement CFR démarré avec succès")
                else:
                    self.logger.warning("Impossible de démarrer l'entraînement CFR")
            
        except Exception as e:
            self.logger.error(f"Erreur démarrage auto-training: {e}")
    
    def _start_continuous_generation(self):
        """Démarre la génération continue de mains en arrière-plan"""
        try:
            if self.cfr_trainer and self.cfr_trainer.continuous_generator:
                self.cfr_trainer.start_continuous_generation()
                self.logger.info("Génération continue de mains activée")
        except Exception as e:
            self.logger.error(f"Erreur génération continue: {e}")
    
    def get_training_progress(self) -> Dict[str, Any]:
        """Retourne les informations de progression de l'entraînement"""
        if self.cfr_trainer:
            stats = self.cfr_trainer.get_training_statistics()
            return {
                'training_active': stats['is_training'],
                'iterations': stats['iterations'],
                'target_iterations': stats['target_iterations'],
                'progress_percent': stats['progress_percentage'],
                'quality': stats['current_quality'],
                'confidence': min(100, stats['current_quality'] * 100),
                'convergence': stats['last_convergence'],
                'training_hands': stats['training_hands'],
                'info_sets': stats['info_sets_learned']
            }
        else:
            return {
                'training_active': False,
                'iterations': self.iterations,
                'target_iterations': 0,
                'progress_percent': 0,
                'quality': 0.0,
                'confidence': 0,
                'convergence': 1.0,
                'training_hands': 0,
                'info_sets': 0
            }
    
    def get_recommendation(self, game_state) -> Dict[str, Any]:
        """Retourne une recommandation basée sur CFR/Nash"""
        try:
            with self.calculation_lock:
                # Conversion en état poker
                poker_state = self._convert_to_poker_state(game_state)
                
                # Calcul de l'information set
                info_set = self._get_information_set(poker_state)
                
                # Obtention de la stratégie
                strategy = self._get_strategy(info_set, poker_state)
                
                # Calcul des probabilités de victoire
                win_probability = self._calculate_win_probability(poker_state)
                
                # Calcul de la valeur espérée pour chaque action
                action_values = self._calculate_action_values(poker_state, strategy)
                
                # Sélection de l'action optimale
                best_action = max(action_values.items(), key=lambda x: x[1])
                
                # Calcul du niveau de risque
                risk_level = self._calculate_risk_level(poker_state, best_action[0])
                
                # Calcul de confiance basé sur les métriques CFR réelles
                confidence = self._calculate_cfr_confidence(info_set, strategy)
                
                # Construction de la recommandation
                recommendation = {
                    'action_type': best_action[0],
                    'bet_size': self._get_bet_size(best_action[0], poker_state),
                    'win_probability': win_probability,
                    'expected_value': best_action[1],
                    'risk_level': risk_level,
                    'confidence': confidence,
                    'reasoning': self._generate_reasoning(poker_state, best_action[0], strategy),
                    'alternative_actions': self._get_alternative_actions(action_values),
                    'timestamp': time.time()
                }
                
                return recommendation
                
        except KeyError as e:
            self.logger.error(f"Erreur données manquantes pour recommandation: {e}")
            return self._get_default_recommendation()
        except ValueError as e:
            self.logger.error(f"Erreur valeur invalide dans calcul CFR: {e}")
            return self._get_default_recommendation()
        except ZeroDivisionError as e:
            self.logger.error(f"Erreur division par zéro dans calculs: {e}")
            return self._get_default_recommendation()
        except Exception as e:
            self.logger.error(f"Erreur inattendue calcul recommandation: {e}")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return self._get_default_recommendation()
    
    def _convert_to_poker_state(self, game_state) -> PokerState:
        """Convertit l'état de jeu en état poker avec validation"""
        try:
            # Validation des données critiques
            if not hasattr(game_state, 'hero_cards') or not game_state.hero_cards:
                raise ValueError("Cartes héros manquantes")
            
            if not hasattr(game_state, 'pot_size') or game_state.pot_size < 0:
                raise ValueError("Taille pot invalide")
            
            if not hasattr(game_state, 'hero_stack') or game_state.hero_stack < 0:
                raise ValueError("Stack héros invalide")
            
            # Détermination de la street
            board_count = len(game_state.board_cards) if game_state.board_cards else 0
            if board_count == 0:
                street = 0  # preflop
            elif board_count == 3:
                street = 1  # flop
            elif board_count == 4:
                street = 2  # turn
            else:
                street = 3  # river
            
            return PokerState(
                street=street,
                hero_cards=game_state.hero_cards,
                board_cards=game_state.board_cards or [],
                pot_size=float(game_state.pot_size),
                hero_stack=float(game_state.hero_stack),
                position=getattr(game_state, 'hero_position', 0),
                num_players=getattr(game_state, 'players_count', 9),
                current_bet=float(getattr(game_state, 'current_bet', 0)),
                action_history=[],  # À implémenter
                table_type=getattr(game_state, 'table_type', 'cashgame')
            )
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error(f"Erreur conversion état poker: {e}")
            # Retourner un état par défaut plutôt que d'échouer
            return self._get_default_poker_state()
            
        except Exception as e:
            self.logger.error(f"Erreur conversion état: {e}")
            return PokerState(0, ("", ""), [], 0, 0, 0, 9, 0, [], "cashgame")
    
    def _get_information_set(self, poker_state: PokerState) -> str:
        """Calcule l'information set pour CFR"""
        try:
            # Abstraction des cartes
            card_bucket = self.card_abstraction.get_bucket(
                poker_state.hero_cards, 
                poker_state.board_cards,
                poker_state.street
            )
            
            # État abstrait du jeu
            bet_history = "_".join(poker_state.action_history[-10:])  # Dernières 10 actions
            
            # SPR (Stack to Pot Ratio)
            spr = poker_state.hero_stack / max(poker_state.pot_size, 1.0)
            spr_bucket = min(int(spr), 20)  # Cap à 20
            
            # Information set
            info_set = f"{poker_state.street}_{card_bucket}_{poker_state.position}_{spr_bucket}_{bet_history}"
            
            return info_set
            
        except Exception as e:
            self.logger.error(f"Erreur information set: {e}")
            return "default_0_0_0_0_"
    
    def _get_strategy(self, info_set: str, poker_state: PokerState) -> Dict[str, float]:
        """Calcule la stratégie pour un information set"""
        try:
            actions = self._get_available_actions(poker_state)
            
            if info_set not in self.regret_sum:
                # Stratégie uniforme pour nouveau info_set
                uniform_prob = 1.0 / len(actions)
                return {action: uniform_prob for action in actions}
            
            # Calcul de la stratégie basée sur les regrets
            strategy = {}
            regret_sum = 0.0
            
            for action in actions:
                regret = max(0.0, self.regret_sum[info_set][action])
                strategy[action] = regret
                regret_sum += regret
            
            # Normalisation
            if regret_sum > 0:
                for action in actions:
                    strategy[action] /= regret_sum
            else:
                # Stratégie uniforme si pas de regret positif
                uniform_prob = 1.0 / len(actions)
                strategy = {action: uniform_prob for action in actions}
            
            # Ajout d'exploration
            for action in actions:
                strategy[action] = (1.0 - self.exploration_rate) * strategy[action] + \
                                 self.exploration_rate / len(actions)
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Erreur calcul stratégie: {e}")
            return {"fold": 0.3, "call": 0.4, "raise": 0.3}
    
    def _get_available_actions(self, poker_state: PokerState) -> List[str]:
        """Retourne les actions disponibles"""
        try:
            actions = []
            
            # Fold toujours disponible (sauf si check possible)
            if poker_state.current_bet > 0:
                actions.append("fold")
            
            # Check/Call
            if poker_state.current_bet == 0:
                actions.append("check")
            else:
                actions.append("call")
            
            # Bet/Raise si stack suffisant
            min_bet = max(poker_state.current_bet * 2, poker_state.pot_size * 0.25)
            if poker_state.hero_stack > min_bet:
                actions.extend(["bet_small", "bet_medium", "bet_large", "bet_allin"])
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Erreur actions disponibles: {e}")
            return ["fold", "call", "raise"]
    
    def _calculate_win_probability(self, poker_state: PokerState) -> float:
        """Calcule la probabilité de victoire"""
        try:
            # Cache check
            cache_key = f"{poker_state.hero_cards}_{poker_state.board_cards}_{poker_state.num_players}"
            if cache_key in self.equity_cache:
                return self.equity_cache[cache_key]
            
            # Simulation Monte Carlo rapide
            wins = 0
            simulations = 1000  # Réduit pour temps réel
            
            for _ in range(simulations):
                # Simulation d'une main complète
                if self._simulate_hand(poker_state):
                    wins += 1
            
            win_prob = wins / simulations
            self.equity_cache[cache_key] = win_prob
            
            return win_prob
            
        except Exception as e:
            self.logger.error(f"Erreur calcul probabilité: {e}")
            return 0.5  # Valeur par défaut
    
    def _simulate_hand(self, poker_state: PokerState) -> bool:
        """Simule une main complète"""
        try:
            # Simulation simplifiée basée sur la force des cartes
            hero_strength = self._calculate_hand_strength(
                poker_state.hero_cards, 
                poker_state.board_cards
            )
            
            # Estimation de la force moyenne des adversaires
            avg_opponent_strength = 0.4 + (0.1 * (9 - poker_state.num_players))
            
            return hero_strength > avg_opponent_strength
            
        except Exception as e:
            self.logger.error(f"Erreur simulation main: {e}")
            return False
    
    def _calculate_hand_strength(self, hero_cards: Tuple[str, str], board_cards: List[str]) -> float:
        """Calcule la force de la main (0-1)"""
        try:
            if not hero_cards or hero_cards == ("", ""):
                return 0.0
            
            # Évaluation simplifiée basée sur les cartes hautes
            card_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10}
            
            strength = 0.0
            
            # Force des cartes individuelles
            for card in hero_cards:
                if card and len(card) >= 2:
                    rank = card[0]
                    value = card_values.get(rank, int(rank) if rank.isdigit() else 5)
                    strength += value / 14.0
            
            strength /= 2.0  # Moyenne des deux cartes
            
            # Bonus pour paires, couleurs, etc. (à améliorer)
            if hero_cards[0][0] == hero_cards[1][0]:  # Paire
                strength += 0.2
            
            if hero_cards[0][1] == hero_cards[1][1]:  # Suited
                strength += 0.05
            
            return min(strength, 1.0)
            
        except Exception as e:
            self.logger.error(f"Erreur force main: {e}")
            return 0.0
    
    def _calculate_action_values(self, poker_state: PokerState, strategy: Dict[str, float]) -> Dict[str, float]:
        """Calcule les valeurs espérées pour chaque action"""
        try:
            action_values = {}
            
            for action, probability in strategy.items():
                # Calcul EV simplifié pour chaque action
                if action == "fold":
                    action_values[action] = 0.0
                elif action in ["check", "call"]:
                    win_prob = self._calculate_win_probability(poker_state)
                    call_amount = poker_state.current_bet
                    pot_odds = call_amount / (poker_state.pot_size + call_amount)
                    action_values[action] = (win_prob - pot_odds) * poker_state.pot_size
                else:  # bet/raise
                    action_values[action] = self._calculate_bet_ev(poker_state, action)
            
            return action_values
            
        except Exception as e:
            self.logger.error(f"Erreur valeurs actions: {e}")
            return {"fold": 0.0, "call": 0.0, "raise": 0.0}
    
    def _calculate_bet_ev(self, poker_state: PokerState, action: str) -> float:
        """Calcule l'EV d'un bet/raise"""
        try:
            win_prob = self._calculate_win_probability(poker_state)
            
            # Taille du bet selon l'action
            bet_size_multipliers = {
                "bet_small": 0.33,
                "bet_medium": 0.66,
                "bet_large": 1.0,
                "bet_allin": min(poker_state.hero_stack / poker_state.pot_size, 3.0)
            }
            
            multiplier = bet_size_multipliers.get(action, 0.66)
            bet_amount = poker_state.pot_size * multiplier
            
            # Probabilité de fold des adversaires (estimation)
            fold_prob = min(0.6 * multiplier, 0.8)
            
            # EV = (fold_prob * pot_actuel) + ((1-fold_prob) * win_prob * pot_final) - bet_amount
            immediate_win = fold_prob * poker_state.pot_size
            showdown_ev = (1 - fold_prob) * win_prob * (poker_state.pot_size + bet_amount * 2)
            
            total_ev = immediate_win + showdown_ev - bet_amount
            
            return total_ev
            
        except Exception as e:
            self.logger.error(f"Erreur EV bet: {e}")
            return 0.0
    
    def _get_bet_size(self, action: str, poker_state: PokerState) -> float:
        """Retourne la taille du bet pour une action"""
        try:
            if action in ["fold", "check"]:
                return 0.0
            elif action == "call":
                return poker_state.current_bet
            elif action == "bet_small":
                return poker_state.pot_size * 0.33
            elif action == "bet_medium":
                return poker_state.pot_size * 0.66
            elif action == "bet_large":
                return poker_state.pot_size * 1.0
            elif action == "bet_allin":
                return poker_state.hero_stack
            else:
                return poker_state.pot_size * 0.5
                
        except Exception as e:
            self.logger.error(f"Erreur taille bet: {e}")
            return 0.0
    
    def _calculate_risk_level(self, poker_state: PokerState, action: str) -> float:
        """Calcule le niveau de risque (0-100)"""
        try:
            base_risk = 0.0
            
            if action == "fold":
                base_risk = 0.0
            elif action in ["check", "call"]:
                base_risk = 30.0
            elif action.startswith("bet"):
                bet_size = self._get_bet_size(action, poker_state)
                risk_ratio = bet_size / poker_state.hero_stack
                base_risk = 50.0 + (risk_ratio * 50.0)
            
            # Ajustements selon le contexte
            if poker_state.table_type == "tournament":
                base_risk *= 1.2  # Plus risqué en tournoi
            
            # Ajustement selon la position pour 9-max
            if poker_state.position <= 2:  # UTG, UTG+1, MP1 (early position)
                base_risk *= 1.15
            elif poker_state.position == 6:  # Button
                base_risk *= 0.9  # Moins risqué au button
            elif poker_state.position == 7:  # Small Blind  
                base_risk *= 1.1  # Plus risqué SB
            elif poker_state.position == 8:  # Big Blind
                base_risk *= 1.05  # Légèrement plus risqué BB
            
            return min(base_risk, 100.0)
            
        except Exception as e:
            self.logger.error(f"Erreur niveau risque: {e}")
            return 50.0
    
    def _calculate_cfr_confidence(self, info_set: str, strategy: Dict[str, float]) -> float:
        """Calcule la confiance basée sur les métriques CFR réelles"""
        try:
            # Progression de l'entraînement depuis les métriques CFR trainer
            training_progress = self.get_training_progress()
            
            # Facteurs de confiance
            iteration_factor = min(1.0, training_progress['iterations'] / 10000)  # Converge vers 1 à 10k itérations
            quality_factor = training_progress['quality']  # Qualité des stratégies
            convergence_factor = max(0.0, 1.0 - training_progress['convergence'])  # Inverse de convergence
            
            # Facteur spécifique à cet information set
            info_set_factor = 1.0
            if info_set in self.strategy_sum and self.strategy_sum[info_set]:
                # Plus l'info set a été vu, plus on a confiance
                total_visits = sum(self.strategy_sum[info_set].values())
                info_set_factor = min(1.0, total_visits / 100)  # Converge à 100 visites
            
            # Facteur de cohérence de la stratégie
            strategy_coherence = self._calculate_strategy_coherence(strategy)
            
            # Calcul de confiance combiné (0-100%)
            base_confidence = (
                iteration_factor * 0.3 +      # 30% basé sur nombre d'itérations
                quality_factor * 0.25 +       # 25% basé sur qualité générale
                convergence_factor * 0.25 +   # 25% basé sur convergence
                info_set_factor * 0.15 +      # 15% basé sur expérience de cette situation
                strategy_coherence * 0.05     # 5% basé sur cohérence de stratégie
            )
            
            confidence_percent = min(100, max(0, base_confidence * 100))
            
            # Bonus pour entraînement intensif actif
            if training_progress['training_active']:
                confidence_percent = min(100, confidence_percent + 5)
            
            return confidence_percent
            
        except Exception as e:
            self.logger.error(f"Erreur calcul confiance CFR: {e}")
            # Fallback sur ancien calcul de confiance
            return self._calculate_confidence_fallback(strategy)
    
    def _calculate_strategy_coherence(self, strategy: Dict[str, float]) -> float:
        """Calcule la cohérence d'une stratégie (moins aléatoire = plus cohérent)"""
        if not strategy or len(strategy) <= 1:
            return 1.0
        
        # Calcul de l'entropie normalisée
        entropy = 0.0
        for prob in strategy.values():
            if prob > 0:
                entropy -= prob * np.log2(prob)
        
        max_entropy = np.log2(len(strategy))
        if max_entropy == 0:
            return 1.0
        
        # Cohérence = inverse de l'entropie normalisée
        coherence = 1.0 - (entropy / max_entropy)
        return max(0.0, min(1.0, coherence))
    
    def _calculate_confidence_fallback(self, strategy: Dict[str, float]) -> float:
        """Calcule la confiance dans la stratégie"""
        try:
            # Entropie comme mesure de confiance (inversée)
            entropy = 0.0
            for prob in strategy.values():
                if prob > 0:
                    entropy -= prob * math.log2(prob)
            
            # Normalisation (max entropy pour 3 actions = log2(3) ≈ 1.58)
            max_entropy = math.log2(len(strategy))
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
            
            # Confiance = 1 - entropy normalisée
            confidence = (1.0 - normalized_entropy) * 100.0
            
            return confidence
            
        except Exception as e:
            self.logger.error(f"Erreur confiance: {e}")
            return 50.0
    
    def _generate_reasoning(self, poker_state: PokerState, action: str, strategy: Dict[str, float]) -> str:
        """Génère une explication de la recommandation"""
        try:
            reasoning_parts = []
            
            # Analyse de la main
            hand_strength = self._calculate_hand_strength(poker_state.hero_cards, poker_state.board_cards)
            if hand_strength > 0.7:
                reasoning_parts.append("Main forte")
            elif hand_strength > 0.4:
                reasoning_parts.append("Main moyenne")
            else:
                reasoning_parts.append("Main faible")
            
            # Analyse de position pour 9-max (0-8)
            # 0=UTG, 1=UTG+1, 2=MP1, 3=MP2, 4=MP3, 5=CO, 6=BTN, 7=SB, 8=BB
            if poker_state.position <= 2:  # UTG, UTG+1, MP1
                reasoning_parts.append("position précoce")
            elif poker_state.position <= 5:  # MP2, MP3, CO
                reasoning_parts.append("position milieu") 
            elif poker_state.position == 6:  # BTN
                reasoning_parts.append("button")
            elif poker_state.position == 7:  # SB
                reasoning_parts.append("small blind")
            else:  # BB
                reasoning_parts.append("big blind")
            
            # Analyse du pot
            spr = poker_state.hero_stack / max(poker_state.pot_size, 1.0)
            if spr < 5:
                reasoning_parts.append("SPR faible")
            elif spr > 15:
                reasoning_parts.append("SPR élevé")
            
            # Construction du message
            base_msg = f"Recommandation {action} basée sur: {', '.join(reasoning_parts)}"
            
            return base_msg
            
        except Exception as e:
            self.logger.error(f"Erreur génération raisonnement: {e}")
            return f"Recommandation {action} basée sur l'analyse CFR"
    
    def _get_alternative_actions(self, action_values: Dict[str, float]) -> List[Dict[str, Any]]:
        """Retourne les actions alternatives"""
        try:
            sorted_actions = sorted(action_values.items(), key=lambda x: x[1], reverse=True)
            
            alternatives = []
            for i, (action, value) in enumerate(sorted_actions[1:3]):  # Top 2 alternatives
                alternatives.append({
                    'action': action,
                    'expected_value': value,
                    'rank': i + 2
                })
            
            return alternatives
            
        except Exception as e:
            self.logger.error(f"Erreur actions alternatives: {e}")
            return []
    
    def _get_default_recommendation(self) -> Dict[str, Any]:
        """Retourne une recommandation par défaut en cas d'erreur"""
        return {
            'action_type': 'check',
            'bet_size': 0.0,
            'win_probability': 50.0,
            'expected_value': 0.0,
            'risk_level': 30.0,
            'confidence': 25.0,
            'reasoning': 'Recommandation de sécurité (erreur de calcul)',
            'alternative_actions': [],
            'timestamp': time.time()
        }
    
    def _get_default_poker_state(self) -> 'PokerState':
        """Retourne un état poker par défaut en cas d'erreur"""
        from ..utils.data_structures import PokerState
        return PokerState(
            street=0,  # preflop
            hero_cards=("Ah", "Kh"),  # Cartes par défaut
            board_cards=[],
            pot_size=100.0,
            hero_stack=1000.0,
            position=0,
            num_players=9,
            current_bet=0.0,
            action_history=[],
            table_type='cashgame'
        )
    
    def update_settings(self, settings: Dict[str, Any]):
        """Met à jour les paramètres CFR"""
        try:
            if 'cfr_iterations' in settings:
                self.iterations = settings['cfr_iterations']
            
            if 'exploration_rate' in settings:
                self.exploration_rate = settings['exploration_rate']
            
            if 'deep_cfr_enabled' in settings:
                self.deep_cfr_enabled = settings['deep_cfr_enabled']
            
            self.logger.info("Paramètres CFR mis à jour")
            
        except Exception as e:
            self.logger.error(f"Erreur mise à jour paramètres: {e}")
    
    def start_background_training(self):
        """Démarre l'entraînement CFR en arrière-plan"""
        if not self.is_running:
            self.is_running = True
            self.background_thread = threading.Thread(target=self._training_loop, daemon=True)
            self.background_thread.start()
            self.logger.info("Entraînement CFR démarré en arrière-plan")
    
    def stop_background_training(self):
        """Arrête l'entraînement en arrière-plan"""
        self.is_running = False
        if self.background_thread:
            self.background_thread.join(timeout=1.0)
        self.logger.info("Entraînement CFR arrêté")
    
    def _training_loop(self):
        """Boucle d'entraînement CFR continu"""
        while self.is_running:
            try:
                # Mise à jour CFR+ (version simplifiée)
                self._update_regrets()
                time.sleep(0.1)  # 100ms entre les mises à jour
                
            except Exception as e:
                self.logger.error(f"Erreur boucle entraînement: {e}")
                time.sleep(1.0)
    
    def _update_regrets(self):
        """Met à jour les regrets CFR+ (implémentation simplifiée)"""
        try:
            # Ici on devrait faire une traversée CFR complète
            # Pour l'instant, on fait une mise à jour légère
            self.iterations += 1
            self.iterations_count = self.iterations  # Synchronisation
            
            # Décroissance des regrets anciens
            if self.iterations % 100 == 0:
                for info_set in self.regret_sum:
                    for action in self.regret_sum[info_set]:
                        self.regret_sum[info_set][action] *= self.discount_factor
                        
        except Exception as e:
            self.logger.error(f"Erreur mise à jour regrets: {e}")

class CardAbstraction:
    """Abstraction des cartes pour CFR"""
    
    def __init__(self):
        self.buckets = 64  # Nombre de buckets
        
    def get_bucket(self, hero_cards: Tuple[str, str], board_cards: List[str], street: int) -> int:
        """Retourne le bucket d'abstraction pour les cartes"""
        try:
            # Implémentation simplifiée
            # En pratique, on utiliserait k-means sur les équités
            
            if not hero_cards or hero_cards == ("", ""):
                return 0
            
            # Hash simple basé sur les cartes
            card_hash = hash(str(hero_cards) + str(board_cards))
            return abs(card_hash) % self.buckets
            
        except Exception as e:
            return 0

class ActionAbstraction:
    """Abstraction des actions pour CFR"""
    
    def __init__(self):
        self.bet_sizes = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]  # Multiples du pot
        
    def get_abstract_action(self, action: str, bet_size: float, pot_size: float) -> str:
        """Convertit une action réelle en action abstraite"""
        try:
            if action in ["fold", "check", "call"]:
                return action
            
            # Abstraction des bet sizes
            if pot_size > 0:
                ratio = bet_size / pot_size
                closest_size = min(self.bet_sizes, key=lambda x: abs(x - ratio))
                return f"bet_{closest_size}"
            
            return "bet_0.5"
            
        except Exception as e:
            return action