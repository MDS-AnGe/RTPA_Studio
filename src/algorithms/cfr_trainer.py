"""
Entraîneur CFR intensif pour convergence Nash rapide
Implémentation optimisée avec métriques de qualité
"""

import time
import threading
import numpy as np
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import pickle
import json

from .hand_parser import ParsedHand
from .hand_generator import HandGenerator, GenerationSettings
from .cfr_engine import CFREngine, PokerState
from ..utils.logger import get_logger

class CFRTrainer:
    """Entraîneur CFR avec génération massive de mains"""
    
    def __init__(self, cfr_engine: CFREngine):
        self.logger = get_logger(__name__)
        self.cfr_engine = cfr_engine
        
        # Configuration d'entraînement
        self.target_iterations = 200000
        self.convergence_threshold = 0.005
        self.quality_threshold = 0.85
        
        # Générateur de mains
        generation_settings = GenerationSettings(
            hands_per_batch=5000,
            max_hands=500000,
            preflop_ratio=0.3,
            flop_ratio=0.3,
            turn_ratio=0.25,
            river_ratio=0.15
        )
        self.hand_generator = HandGenerator(generation_settings)
        
        # Métriques de training
        self.training_hands = []
        self.convergence_history = deque(maxlen=1000)
        self.quality_history = deque(maxlen=1000)
        self.iteration_times = deque(maxlen=100)
        
        # État de l'entraînement
        self.is_training = False
        self.training_thread = None
        self.start_time = 0.0
        self.total_training_time = 0.0
        
        # Métriques de progression pour l'interface
        self.current_iteration = 0
        self.training_start_time = None
        
        # Cache et optimisations
        self.strategy_cache = {}
        self.regret_updates = 0
        self.strategy_updates = 0
        
        # Générateur continu et gestionnaire de données
        self.continuous_generator = None
        self.data_manager = None
        self._init_continuous_generator()
        self._init_data_manager()
        
        self.logger.info("CFRTrainer initialisé avec génération continue")
    
    def _init_continuous_generator(self):
        """Initialise le générateur continu de mains"""
        try:
            from .continuous_generator import ContinuousHandGenerator, ContinuousSettings
            
            # Configuration optimisée pour performance maximale
            settings = ContinuousSettings(
                batch_size=50,  # Batches plus gros pour efficacité
                generation_interval=0.1,  # 100ms entre générations
                max_queue_size=1000,  # Queue plus importante
                cpu_usage_limit=0.2  # Max 20% CPU pour plus de puissance
            )
            
            self.continuous_generator = ContinuousHandGenerator(settings)
            
            # Configuration des callbacks
            self.continuous_generator.set_integration_callback(self._integrate_continuous_hands)
            self.continuous_generator.set_stats_callback(self._update_generation_stats)
            
        except Exception as e:
            self.logger.error(f"Erreur init générateur continu: {e}")
    
    def _integrate_continuous_hands(self, hands):
        """Intègre les mains générées en continu dans l'entraînement CFR"""
        try:
            if not hands:
                return
            
            # Ajout immédiat aux mains d'entraînement
            self.training_hands.extend(hands)
            
            # Si entraînement en cours, intégration directe dans CFR
            if self.is_training:
                for hand in hands:
                    try:
                        # Conversion en état CFR
                        cfr_state = self._hand_to_cfr_state(hand)
                        if cfr_state:
                            # Mise à jour immédiate des tables CFR
                            self._update_cfr_tables_immediate(cfr_state)
                    except Exception as e:
                        continue
            
            # Mise à jour statistiques
            if len(hands) > 0:
                self.logger.debug(f"Intégré {len(hands)} mains continues -> Total: {len(self.training_hands)}")
                
        except Exception as e:
            self.logger.error(f"Erreur intégration mains continues: {e}")
    
    def _hand_to_cfr_state(self, hand):
        """Convertit une main parsée en état CFR"""
        try:
            from .cfr_engine import PokerState
            
            # Extraction des informations de la main
            hero_cards = (hand.hero_cards[0], hand.hero_cards[1]) if hand.hero_cards and len(hand.hero_cards) >= 2 else ('As', 'Ks')
            board_cards = hand.board_cards if hand.board_cards else []
            pot_size = hand.pot_size if hand.pot_size else 100.0
            hero_stack = hand.hero_stack if hand.hero_stack else 1000.0
            
            # Détermination de la street
            street = 0
            if len(board_cards) >= 3:
                street = 1  # flop
            if len(board_cards) >= 4:
                street = 2  # turn
            if len(board_cards) >= 5:
                street = 3  # river
            
            cfr_state = PokerState(
                street=street,
                hero_cards=hero_cards,
                board_cards=board_cards,
                pot_size=pot_size,
                hero_stack=hero_stack,
                position=0,  # Default position
                num_players=2,  # Default heads-up
                current_bet=0.0,
                action_history=[],
                table_type="cashgame"
            )
            
            return cfr_state
            
        except Exception as e:
            self.logger.error(f"Erreur conversion main->CFR: {e}")
            return None
    
    def _get_information_set(self, cfr_state):
        """Génère l'ensemble d'informations pour un état CFR"""
        try:
            # Génération simplifiée d'information set
            bucket = self.cfr_engine.card_abstraction.get_bucket(
                cfr_state.hero_cards, 
                cfr_state.board_cards, 
                cfr_state.street
            )
            
            # Combine bucket, position, action history
            action_history_str = "_".join(cfr_state.action_history[-5:])  # Dernières 5 actions
            info_set = f"{bucket}_{cfr_state.position}_{cfr_state.street}_{action_history_str}"
            
            return info_set
            
        except Exception as e:
            return f"default_{cfr_state.street}_{hash(str(cfr_state.hero_cards)) % 100}"
    
    def _get_legal_actions(self, cfr_state):
        """Retourne les actions légales pour un état CFR"""
        try:
            actions = ['fold', 'check_call']
            
            # Actions de mise disponibles selon l'état
            if cfr_state.hero_stack > cfr_state.current_bet:
                # Tailles de mises basées sur le pot
                bet_sizes = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
                for size in bet_sizes:
                    bet_amount = cfr_state.pot_size * size
                    if bet_amount <= cfr_state.hero_stack:
                        actions.append(f'bet_{size}')
            
            return actions
            
        except Exception:
            return ['fold', 'check_call', 'bet_0.5']
    
    def _get_strategy_from_regrets(self, info_set):
        """Calcule la stratégie à partir des regrets"""
        try:
            regrets = self.cfr_engine.regret_sum[info_set]
            if not regrets:
                # Stratégie uniforme par défaut
                return {'fold': 0.2, 'check_call': 0.4, 'bet_0.5': 0.4}
            
            # Conversion regrets -> probabilités
            positive_regrets = {action: max(0, regret) for action, regret in regrets.items()}
            total_regret = sum(positive_regrets.values())
            
            if total_regret <= 0:
                # Stratégie uniforme si pas de regrets positifs
                num_actions = len(regrets)
                uniform_prob = 1.0 / num_actions
                return {action: uniform_prob for action in regrets.keys()}
            
            # Normalisation
            strategy = {action: regret / total_regret for action, regret in positive_regrets.items()}
            return strategy
            
        except Exception:
            return {'fold': 0.2, 'check_call': 0.4, 'bet_0.5': 0.4}
    
    def _update_cfr_tables_immediate(self, cfr_state):
        """Met à jour les tables CFR immédiatement avec un nouvel état"""
        try:
            # Calcul rapide CFR pour cet état
            info_set = self._get_information_set(cfr_state)
            actions = self._get_legal_actions(cfr_state)
            
            if info_set and actions:
                # Calcul des regrets pour cet état
                regrets = self._calculate_immediate_regrets(cfr_state, actions)
                
                # Mise à jour des tables de regret
                for action, regret in regrets.items():
                    self.cfr_engine.regret_sum[info_set][action] += regret
                
                # Mise à jour de la stratégie courante
                strategy = self._get_strategy_from_regrets(info_set)
                for action, prob in strategy.items():
                    self.cfr_engine.strategy_sum[info_set][action] += prob
                
        except Exception as e:
            pass  # Ignore les erreurs pour ne pas ralentir
    
    def _calculate_immediate_regrets(self, cfr_state, actions):
        """Calcul rapide des regrets pour un état donné"""
        regrets = {}
        
        try:
            # Simulation Monte Carlo rapide
            for action in actions:
                # Valeur de l'action
                action_value = self._quick_action_evaluation(cfr_state, action)
                
                # Valeur moyenne des autres actions
                other_values = []
                for other_action in actions:
                    if other_action != action:
                        other_values.append(self._quick_action_evaluation(cfr_state, other_action))
                
                avg_other_value = np.mean(other_values) if other_values else 0.0
                
                # Regret = différence
                regrets[action] = max(0.0, float(avg_other_value - action_value))
                
        except Exception:
            # Fallback: regrets uniformes
            for action in actions:
                regrets[action] = 0.1
                
        return regrets
    
    def _evaluate_hand_strength(self, hero_cards, board_cards):
        """Évalue la force de la main actuelle"""
        try:
            # Évaluation simplifiée de la force de main
            if not hero_cards or len(hero_cards) != 2:
                return 0.5
                
            # Basé sur les cartes hautes et potentiels
            card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                          '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
            
            hero_value = sum(card_values.get(card[0], 7) for card in hero_cards) / 28.0  # Normalisé
            
            # Bonus pour paire
            if hero_cards[0][0] == hero_cards[1][0]:
                hero_value *= 1.5
                
            # Bonus pour couleur
            if hero_cards[0][1] == hero_cards[1][1]:
                hero_value *= 1.2
                
            return min(hero_value, 1.0)
            
        except Exception:
            return 0.5
    
    def _quick_action_evaluation(self, cfr_state, action):
        """Évaluation rapide d'une action"""
        try:
            # Évaluation simplifiée basée sur les heuristiques
            hand_strength = self._evaluate_hand_strength(cfr_state.hero_cards, cfr_state.board_cards)
            
            if action == 'fold':
                return 0.0
            elif action == 'check_call':
                return hand_strength * cfr_state.pot_size * 0.5
            elif action.startswith('bet') or action.startswith('raise'):
                # Valeur agressive basée sur force de main
                aggression_value = hand_strength * cfr_state.pot_size * 1.2
                return aggression_value - (cfr_state.current_bet * 0.8)
            else:
                return hand_strength * cfr_state.pot_size * 0.3
                
        except Exception:
            return 0.5  # Valeur neutre
    
    def _update_generation_stats(self, stats):
        """Met à jour les statistiques de génération continue"""
        try:
            # Log périodique des statistiques
            if stats['hands_generated'] % 1000 == 0:
                self.logger.info(f"Génération continue: {stats['hands_generated']} mains, "
                               f"rate: {stats['generation_rate']:.1f}/s, "
                               f"CPU: {stats['cpu_usage']*100:.1f}%")
                
        except Exception as e:
            pass
    
    def start_continuous_generation(self):
        """Démarre la génération continue de mains"""
        try:
            if self.continuous_generator and not self.continuous_generator.running:
                self.continuous_generator.start()
                self.logger.info("Génération continue de mains démarrée")
                
        except Exception as e:
            self.logger.error(f"Erreur démarrage génération continue: {e}")
    
    def stop_continuous_generation(self):
        """Arrête la génération continue"""
        try:
            if self.continuous_generator and self.continuous_generator.running:
                self.continuous_generator.stop()
                self.logger.info("Génération continue arrêtée")
                
        except Exception as e:
            self.logger.error(f"Erreur arrêt génération continue: {e}")
    
    def boost_generation_for_scenario(self, scenario: str):
        """Booste la génération pour un scénario spécifique"""
        try:
            if self.continuous_generator:
                self.continuous_generator.boost_generation(scenario, multiplier=3.0)
                self.logger.info(f"Boost génération activé pour: {scenario}")
                
        except Exception as e:
            self.logger.error(f"Erreur boost génération: {e}")
    
    def _init_data_manager(self):
        """Initialise le gestionnaire de données optimisé"""
        try:
            from .data_manager import DataManager, StorageSettings
            
            # Configuration du stockage
            storage_settings = StorageSettings(
                max_memory_hands=30000,  # 30k mains en mémoire
                max_disk_size_mb=200,    # 200MB max sur disque
                compression_level=6,     # Compression équilibrée
                cleanup_interval=180.0   # Nettoyage toutes les 3 minutes
            )
            
            self.data_manager = DataManager(storage_settings)
            self.data_manager.start_cleanup_service()
            
            self.logger.info("Gestionnaire de données initialisé")
            
        except Exception as e:
            self.logger.error(f"Erreur init data manager: {e}")
    
    def stop_continuous_generation_user(self):
        """Arrête la génération continue à la demande de l'utilisateur"""
        try:
            if self.continuous_generator and self.continuous_generator.running:
                self.continuous_generator.stop(user_initiated=True)
                self.logger.info("Génération continue arrêtée par l'utilisateur")
                
        except Exception as e:
            self.logger.error(f"Erreur arrêt utilisateur: {e}")
    
    def is_generation_user_stopped(self) -> bool:
        """Vérifie si la génération a été arrêtée par l'utilisateur"""
        if self.continuous_generator:
            return self.continuous_generator.is_user_stopped()
        return False
    
    def configure_generation_resources(self, cpu_percent: Optional[float] = None, 
                                     memory_mb: Optional[float] = None, rate_per_second: Optional[float] = None):
        """Configure les ressources allouées à la génération"""
        try:
            if self.continuous_generator:
                cpu_limit = cpu_percent / 100.0 if cpu_percent else None
                self.continuous_generator.set_resource_limits(
                    cpu_limit=cpu_limit,
                    memory_limit_mb=memory_mb,
                    generation_rate=rate_per_second
                )
                self.logger.info("Ressources de génération mises à jour")
                
        except Exception as e:
            self.logger.error(f"Erreur configuration ressources: {e}")
    
    def configure_storage_settings(self, max_disk_mb: Optional[int] = None, 
                                 max_memory_hands: Optional[int] = None, compression_level: Optional[int] = None):
        """Configure les paramètres de stockage"""
        try:
            if self.data_manager:
                settings_update = {}
                if max_disk_mb is not None:
                    settings_update['max_disk_size_mb'] = max_disk_mb
                if max_memory_hands is not None:
                    settings_update['max_memory_hands'] = max_memory_hands
                if compression_level is not None:
                    settings_update['compression_level'] = compression_level
                
                if settings_update:
                    self.data_manager.configure_storage(settings_update)
                    self.logger.info("Paramètres de stockage mis à jour")
                    
        except Exception as e:
            self.logger.error(f"Erreur configuration stockage: {e}")
    
    def get_storage_status(self) -> Dict[str, Any]:
        """Retourne le statut du stockage et des ressources"""
        status = {
            'generation_active': False,
            'generation_user_stopped': False,
            'storage_stats': {},
            'generation_stats': {}
        }
        
        try:
            # Statut génération
            if self.continuous_generator:
                status['generation_active'] = self.continuous_generator.running
                status['generation_user_stopped'] = self.continuous_generator.is_user_stopped()
                status['generation_stats'] = self.continuous_generator.get_statistics()
            
            # Statut stockage
            if self.data_manager:
                status['storage_stats'] = self.data_manager.get_storage_statistics()
            
        except Exception as e:
            self.logger.error(f"Erreur statut stockage: {e}")
        
        return status
    
    def export_optimized_database(self, export_path: str) -> bool:
        """Exporte la base de données de façon optimisée"""
        try:
            if self.data_manager:
                return self.data_manager.export_database(export_path)
            else:
                # Fallback export basique
                self.logger.warning("Export basique - data manager non disponible")
                return self.export_cfr_data_fallback(export_path)
                
        except Exception as e:
            self.logger.error(f"Erreur export optimisé: {e}")
            return False
    
    def export_cfr_data_fallback(self, export_path: str) -> bool:
        """Export basique des données CFR"""
        try:
            import json
            
            data = {
                'training_hands': len(self.training_hands),
                'regret_sum': dict(self.cfr_engine.regret_sum) if hasattr(self.cfr_engine, 'regret_sum') else {},
                'strategy_sum': dict(self.cfr_engine.strategy_sum) if hasattr(self.cfr_engine, 'strategy_sum') else {},
                'iterations': getattr(self, 'iterations_completed', 0),
                'timestamp': time.time()
            }
            
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Export CFR basique sauvé: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur export CFR basique: {e}")
            return False
    
    def load_historical_hands(self, file_paths: List[str]) -> int:
        """Charge les mains historiques depuis les fichiers fournis"""
        self.logger.info("Chargement des mains historiques...")
        
        from .hand_parser import HandParser
        parser = HandParser()
        
        total_hands = 0
        for file_path in file_paths:
            try:
                hands = parser.parse_file(file_path)
                self.training_hands.extend(hands)
                total_hands += len(hands)
                self.logger.info(f"Chargé {len(hands)} mains depuis {file_path}")
            except Exception as e:
                self.logger.error(f"Erreur chargement {file_path}: {e}")
        
        self.logger.info(f"Total mains historiques chargées: {total_hands}")
        return total_hands
    
    def generate_training_dataset(self, target_size: int = 500000) -> int:
        """Génère un dataset d'entraînement massif"""
        self.logger.info(f"Génération de {target_size} mains synthétiques...")
        
        start_time = time.time()
        
        # Génération par batches pour optimiser la mémoire
        batch_size = 10000
        generated_hands = 0
        
        while generated_hands < target_size:
            remaining = target_size - generated_hands
            current_batch_size = min(batch_size, remaining)
            
            batch_hands = self.hand_generator.generate_batch(current_batch_size)
            self.training_hands.extend(batch_hands)
            generated_hands += len(batch_hands)
            
            if generated_hands % 50000 == 0:
                self.logger.info(f"Généré {generated_hands}/{target_size} mains...")
        
        generation_time = time.time() - start_time
        self.logger.info(f"Génération terminée: {generated_hands} mains en {generation_time:.2f}s")
        
        return generated_hands
    
    def start_intensive_training(self, target_iterations: Optional[int] = None, 
                                target_convergence: Optional[float] = None) -> bool:
        """Démarre l'entraînement CFR intensif"""
        if self.is_training:
            self.logger.warning("Entraînement déjà en cours")
            return False
        
        if target_iterations:
            self.target_iterations = target_iterations
        if target_convergence:
            self.convergence_threshold = target_convergence
        
        self.logger.info(f"Démarrage entraînement CFR intensif:")
        self.logger.info(f"  - Objectif: {self.target_iterations} itérations")
        self.logger.info(f"  - Convergence: {self.convergence_threshold}")
        self.logger.info(f"  - Mains disponibles: {len(self.training_hands)}")
        
        # Vérification dataset
        if len(self.training_hands) < 10000:
            self.logger.warning("Dataset insuffisant, génération de mains supplémentaires...")
            self.generate_training_dataset(100000)
        
        # Démarrage training en arrière-plan
        self.is_training = True
        self.start_time = time.time()
        self.training_thread = threading.Thread(target=self._training_loop, daemon=True)
        self.training_thread.start()
        
        return True
    
    def stop_training(self):
        """Arrête l'entraînement"""
        if self.is_training:
            self.is_training = False
            self.total_training_time += time.time() - self.start_time
            self.logger.info("Arrêt de l'entraînement CFR demandé")
    
    def _training_loop(self):
        """Boucle principale d'entraînement CFR"""
        self.logger.info("Démarrage de la boucle d'entraînement CFR")
        
        iteration = 0
        last_convergence_check = 0
        convergence = 1.0  # Initialize convergence
        
        # Initialiser le temps de démarrage pour l'estimation
        self.training_start_time = time.time()
        
        while self.is_training and iteration < self.target_iterations:
            try:
                iter_start = time.time()
                
                # Sélection batch de mains pour cette itération
                batch_hands = self._select_training_batch()
                
                # Entraînement CFR sur le batch
                convergence = self._train_cfr_batch(batch_hands, iteration)
                
                # Mise à jour métriques
                iter_time = time.time() - iter_start
                self.iteration_times.append(iter_time)
                self.convergence_history.append(convergence)
                
                iteration += 1
                self.current_iteration = iteration  # Mettre à jour pour l'interface
                
                # Check convergence périodique
                if iteration - last_convergence_check >= 100:
                    quality = self._evaluate_strategy_quality()
                    self.quality_history.append(quality)
                    
                    # Log progression
                    if iteration % 1000 == 0:
                        avg_time = np.mean(list(self.iteration_times))
                        self.logger.info(f"Itération {iteration}: convergence={convergence:.4f}, "
                                       f"qualité={quality:.4f}, temps={avg_time:.3f}s")
                    
                    # Check arrêt anticipé si convergence atteinte
                    if convergence < self.convergence_threshold and quality > self.quality_threshold:
                        self.logger.info(f"Convergence atteinte à l'itération {iteration}")
                        break
                    
                    last_convergence_check = iteration
                
                # Pause courte pour éviter surcharge CPU
                time.sleep(0.001)
                
            except Exception as e:
                self.logger.error(f"Erreur itération {iteration}: {e}")
                time.sleep(0.1)
        
        self.is_training = False
        self.total_training_time += time.time() - self.start_time
        
        final_quality = self._evaluate_strategy_quality()
        self.logger.info(f"Entraînement terminé:")
        self.logger.info(f"  - Itérations: {iteration}")
        self.logger.info(f"  - Convergence finale: {convergence:.4f}")
        self.logger.info(f"  - Qualité finale: {final_quality:.4f}")
        self.logger.info(f"  - Temps total: {self.total_training_time:.2f}s")
    
    def _select_training_batch(self, batch_size: int = 100) -> List[ParsedHand]:
        """Sélectionne un batch de mains pour l'entraînement"""
        if len(self.training_hands) < batch_size:
            return self.training_hands.copy()
        
        # Sélection stratifiée pour couvrir différentes situations
        preflop_hands = [h for h in self.training_hands if h.street == 0]
        postflop_hands = [h for h in self.training_hands if h.street > 0]
        
        batch = []
        
        # 40% preflop, 60% postflop
        if preflop_hands:
            batch.extend(np.random.choice(preflop_hands, size=min(40, len(preflop_hands)), replace=False))
        if postflop_hands:
            batch.extend(np.random.choice(postflop_hands, size=min(60, len(postflop_hands)), replace=False))
        
        return batch[:batch_size]
    
    def _train_cfr_batch(self, hands: List[ParsedHand], iteration: int) -> float:
        """Entraîne CFR sur un batch de mains"""
        total_regret_change = 0.0
        processed_hands = 0
        
        for hand in hands:
            try:
                # Conversion en PokerState
                poker_state = self._convert_hand_to_poker_state(hand)
                
                # CFR traversal
                regret_change = self._cfr_traversal(poker_state, iteration)
                total_regret_change += abs(regret_change)
                processed_hands += 1
                
            except Exception as e:
                self.logger.error(f"Erreur processing main {hand.hand_id}: {e}")
        
        # Calcul de convergence (changement moyen des regrets)
        convergence = total_regret_change / max(processed_hands, 1)
        return convergence
    
    def _cfr_traversal(self, poker_state: PokerState, iteration: int) -> float:
        """Effectue une traversée CFR sur un état de poker"""
        
        # Calcul information set
        info_set = self.cfr_engine._get_information_set(poker_state)
        
        # Actions disponibles
        actions = self.cfr_engine._get_available_actions(poker_state)
        if not actions:
            return 0.0
        
        # Stratégie actuelle
        strategy = self.cfr_engine._get_strategy(info_set, poker_state)
        
        # Calcul des valeurs d'action (simplifié)
        action_values = {}
        for action in actions:
            # Simulation de la valeur de l'action
            value = self._simulate_action_value(poker_state, action)
            action_values[action] = value
        
        # Calcul des regrets
        node_value = sum(strategy.get(action, 0) * action_values.get(action, 0) for action in actions)
        total_regret_change = 0.0
        
        for action in actions:
            # Regret = valeur action - valeur noeud
            regret = action_values.get(action, 0) - node_value
            
            # Mise à jour regret avec discount
            old_regret = self.cfr_engine.regret_sum[info_set][action]
            self.cfr_engine.regret_sum[info_set][action] = max(0, old_regret + regret)
            
            total_regret_change += abs(regret)
            self.regret_updates += 1
        
        # Mise à jour stratégie cumulée
        for action in actions:
            self.cfr_engine.strategy_sum[info_set][action] += strategy.get(action, 0)
            self.strategy_updates += 1
        
        return total_regret_change
    
    def _simulate_action_value(self, poker_state: PokerState, action: str) -> float:
        """Simule la valeur d'une action (implémentation simplifiée)"""
        
        # Évaluation basique selon l'action et l'état
        base_value = 0.0
        
        # Force de main approximative
        hand_strength = self._estimate_hand_strength(poker_state)
        
        if action == 'fold':
            base_value = -poker_state.current_bet
        elif action == 'check' or action == 'call':
            base_value = hand_strength * poker_state.pot_size - poker_state.current_bet
        elif action.startswith('bet') or action.startswith('raise'):
            # Extract bet size
            try:
                bet_size = float(action.split('_')[1]) if '_' in action else poker_state.pot_size * 0.5
            except (ValueError, IndexError, AttributeError):
                bet_size = poker_state.pot_size * 0.5
            
            # Agressivité récompensée selon force de main
            aggression_bonus = hand_strength * bet_size * 0.5
            base_value = hand_strength * (poker_state.pot_size + bet_size) - bet_size + aggression_bonus
        
        # Ajustement selon position et SPR
        spr = poker_state.hero_stack / max(poker_state.pot_size, 1)
        position_factor = 1.1 if poker_state.position == 1 else 0.9  # Button advantage
        spr_factor = min(1.2, max(0.8, spr / 10))  # SPR adjustment
        
        return base_value * position_factor * spr_factor
    
    def _estimate_hand_strength(self, poker_state: PokerState) -> float:
        """Estime la force de la main (implémentation simplifiée)"""
        
        hero_cards = poker_state.hero_cards
        board_cards = poker_state.board_cards
        
        if not hero_cards or hero_cards == ("", ""):
            return 0.5
        
        # Analyse basique des cartes
        ranks = [card[0] for card in hero_cards if card]
        suits = [card[1] for card in hero_cards if len(card) == 2]
        
        strength = 0.5  # Base
        
        # Pocket pairs
        if len(ranks) == 2 and ranks[0] == ranks[1]:
            pair_values = {'A': 0.95, 'K': 0.9, 'Q': 0.85, 'J': 0.8, 'T': 0.75}
            strength = pair_values.get(ranks[0], 0.7)
        
        # High cards
        elif 'A' in ranks:
            strength = 0.75 if 'K' in ranks or 'Q' in ranks else 0.65
        elif 'K' in ranks and 'Q' in ranks:
            strength = 0.7
        
        # Suited
        if len(suits) == 2 and suits[0] == suits[1]:
            strength += 0.05
        
        # Ajustement selon board (très simplifié)
        if board_cards:
            hero_ranks_set = set(ranks)
            board_ranks_set = set([card[0] for card in board_cards if card])
            
            # Paire avec board
            if hero_ranks_set & board_ranks_set:
                strength += 0.15
        
        return min(1.0, max(0.0, strength))
    
    def _convert_hand_to_poker_state(self, hand: ParsedHand) -> PokerState:
        """Convertit une ParsedHand en PokerState"""
        return PokerState(
            street=hand.street,
            hero_cards=hand.hero_cards,
            board_cards=hand.board_cards,
            pot_size=hand.pot_size,
            hero_stack=hand.hero_stack,
            position=hand.position,
            num_players=2,  # Heads-up par défaut
            current_bet=hand.blinds[1],  # Big blind comme bet de base
            action_history=hand.actions,
            table_type="cashgame"
        )
    
    def _evaluate_strategy_quality(self) -> float:
        """Évalue la qualité de la stratégie actuelle"""
        
        # Métriques de qualité:
        # 1. Cohérence des stratégies
        # 2. Exploitation des situations évidentes
        # 3. Convergence des regrets
        
        if not self.cfr_engine.strategy_sum:
            return 0.0
        
        quality_score = 0.0
        num_evaluations = 0
        
        # Sample information sets pour évaluation
        info_sets = list(self.cfr_engine.strategy_sum.keys())
        sample_size = min(100, len(info_sets))
        
        if sample_size == 0:
            return 0.0
        
        sample_info_sets = np.random.choice(info_sets, size=sample_size, replace=False)
        
        for info_set in sample_info_sets:
            strategy_sum = self.cfr_engine.strategy_sum[info_set]
            
            if not strategy_sum:
                continue
            
            # Normalisation de la stratégie
            total = sum(strategy_sum.values())
            if total <= 0:
                continue
            
            normalized_strategy = {action: count/total for action, count in strategy_sum.items()}
            
            # Évaluation de cohérence (entropy inverse)
            entropy = 0.0
            for prob in normalized_strategy.values():
                if prob > 0:
                    entropy -= prob * np.log2(prob)
            
            # Score de qualité (préfère stratégies moins aléatoires)
            max_entropy = np.log2(len(normalized_strategy))
            coherence_score = 1.0 - (entropy / max_entropy) if max_entropy > 0 else 1.0
            
            quality_score += coherence_score
            num_evaluations += 1
        
        average_quality = quality_score / max(num_evaluations, 1)
        
        # Ajustement selon nombre d'itérations (stratégies prennent temps à converger)
        iteration_factor = min(1.0, self.cfr_engine.iterations / 10000)
        
        return average_quality * iteration_factor
    
    def save_training_progress(self, file_path: str):
        """Sauvegarde le progrès d'entraînement"""
        try:
            progress_data = {
                'iterations': self.cfr_engine.iterations,
                'total_training_time': self.total_training_time,
                'convergence_history': list(self.convergence_history),
                'quality_history': list(self.quality_history),
                'regret_updates': self.regret_updates,
                'strategy_updates': self.strategy_updates,
                'hands_trained': len(self.training_hands),
                'final_quality': self._evaluate_strategy_quality()
            }
            
            with open(file_path, 'w') as f:
                json.dump(progress_data, f, indent=2)
            
            self.logger.info(f"Progrès sauvegardé: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde progrès: {e}")
    
    def get_training_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques d'entraînement stabilisées"""
        
        # Calcul qualité lissée pour éviter fluctuations
        try:
            if not hasattr(self, '_quality_history'):
                self._quality_history = []
            
            raw_quality = self._evaluate_strategy_quality()
            self._quality_history.append(raw_quality)
            
            # Garder seulement les 5 dernières valeurs pour lissage
            if len(self._quality_history) > 5:
                self._quality_history.pop(0)
            
            # Moyenne mobile pour stabilité
            current_quality = sum(self._quality_history) / len(self._quality_history)
        except Exception:
            current_quality = getattr(self, '_last_quality', 0.0)
        
        self._last_quality = current_quality
        
        # Convergence stabilisée
        last_convergence = self.convergence_history[-1] if self.convergence_history else 1.0
        
        # Progression monotone croissante
        if not hasattr(self, '_last_progress'):
            self._last_progress = 0.0
        
        current_progress = min(100, (self.cfr_engine.iterations / max(self.target_iterations, 1)) * 100)
        # S'assurer que la progression ne recule jamais
        self._last_progress = max(self._last_progress, current_progress)
        
        # Temps d'estimation stabilisé
        if self.iteration_times and len(self.iteration_times) > 5:
            avg_time = np.mean(list(self.iteration_times)[-5:])  # Moyenne des 5 dernières
        else:
            avg_time = np.mean(list(self.iteration_times)) if self.iteration_times else 0.1
        
        remaining_iterations = max(0, self.target_iterations - self.cfr_engine.iterations)
        estimated_time_remaining = remaining_iterations * avg_time
        
        return {
            'is_training': self.is_training,
            'iterations': self.cfr_engine.iterations,
            'target_iterations': self.target_iterations,
            'training_hands': len(self.training_hands),
            'regret_updates': self.regret_updates,
            'strategy_updates': self.strategy_updates,
            'total_training_time': self.total_training_time,
            'current_quality': min(1.0, max(0.0, current_quality)),
            'last_convergence': max(0.001, last_convergence),
            'convergence_threshold': self.convergence_threshold,
            'quality_threshold': self.quality_threshold,
            'avg_iteration_time': max(0.01, float(avg_time)),
            'info_sets_learned': len(self.cfr_engine.strategy_sum),
            'progress_percentage': self._last_progress,
            'estimated_time_remaining': max(0.0, float(estimated_time_remaining))
        }