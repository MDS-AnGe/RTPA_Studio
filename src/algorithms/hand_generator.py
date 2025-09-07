"""
Générateur de mains synthétiques pour entraînement CFR massif
Création de millions de situations poker réalistes
"""

import random
import itertools
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .hand_parser import ParsedHand
from ..utils.logger import get_logger

@dataclass
class GenerationSettings:
    """Configuration pour la génération de mains"""
    hands_per_batch: int = 10000
    max_hands: int = 1000000
    preflop_ratio: float = 0.4
    flop_ratio: float = 0.3
    turn_ratio: float = 0.2
    river_ratio: float = 0.1
    aggressive_ratio: float = 0.3  # Proportion d'actions agressives
    stack_sizes: Optional[List[float]] = None
    blind_levels: Optional[List[Tuple[float, float]]] = None
    
    def __post_init__(self):
        if self.stack_sizes is None:
            self.stack_sizes = [1000, 2000, 5000, 10000, 20000]
        if self.blind_levels is None:
            self.blind_levels = [(25, 50), (50, 100), (100, 200), (200, 400), (400, 800)]

class HandGenerator:
    """Générateur de mains poker synthétiques"""
    
    def __init__(self, settings: Optional[GenerationSettings] = None):
        self.logger = get_logger(__name__)
        self.settings = settings or GenerationSettings()
        
        # Deck de cartes
        self.suits = ['h', 'd', 'c', 's']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.deck = [rank + suit for rank in self.ranks for suit in self.suits]
        
        # Statistiques de génération
        self.hands_generated = 0
        self.generation_time = 0.0
        
        # Poids pour réalisme des mains
        self._init_hand_weights()
    
    def _init_hand_weights(self):
        """Initialise les poids de probabilité pour des mains réalistes"""
        
        # Poids des mains de départ (basé sur statistiques réelles)
        self.preflop_weights = {}
        
        # Pairs
        pairs = [f"{rank}{rank}" for rank in self.ranks]
        for pair in pairs:
            if pair in ['AA', 'KK', 'QQ']:
                self.preflop_weights[pair] = 3.0  # Mains premium
            elif pair in ['JJ', 'TT', '99']:
                self.preflop_weights[pair] = 2.5
            else:
                self.preflop_weights[pair] = 2.0
        
        # Suited connectors et suited aces
        for i, rank1 in enumerate(self.ranks):
            for j, rank2 in enumerate(self.ranks):
                if i != j:
                    hand = f"{rank1}{rank2}"
                    if abs(i - j) == 1:  # Connectors
                        self.preflop_weights[hand + "s"] = 1.5
                    elif rank1 == 'A' or rank2 == 'A':  # Ace-x suited
                        self.preflop_weights[hand + "s"] = 1.8
                    else:
                        self.preflop_weights[hand + "s"] = 1.0
        
        # Offsuit hands
        broadway = ['T', 'J', 'Q', 'K', 'A']
        for rank1 in broadway:
            for rank2 in broadway:
                if rank1 != rank2:
                    hand = f"{rank1}{rank2}"
                    if hand + "o" not in self.preflop_weights:
                        self.preflop_weights[hand + "o"] = 1.2
    
    def generate_batch(self, batch_size: Optional[int] = None) -> List[ParsedHand]:
        """Génère un batch de mains synthétiques"""
        if batch_size is None:
            batch_size = self.settings.hands_per_batch
        
        start_time = time.time()
        hands = []
        
        for i in range(batch_size):
            # Détermine la street selon les ratios
            street = self._select_street()
            hand = self._generate_hand_for_street(street, str(self.hands_generated + i))
            if hand:
                hands.append(hand)
        
        self.hands_generated += len(hands)
        self.generation_time += time.time() - start_time
        
        self.logger.info(f"Généré {len(hands)} mains en {time.time() - start_time:.2f}s")
        return hands
    
    def generate_massive_dataset(self, target_hands: Optional[int] = None) -> List[ParsedHand]:
        """Génère un dataset massif de mains avec multiprocessing"""
        if target_hands is None:
            target_hands = self.settings.max_hands
        
        self.logger.info(f"Génération de {target_hands} mains synthétiques...")
        
        hands = []
        batch_size = self.settings.hands_per_batch
        total_batches = (target_hands + batch_size - 1) // batch_size
        
        # Génération parallèle pour optimiser les performances
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_batch = {}
            
            for batch_idx in range(total_batches):
                remaining = target_hands - len(hands)
                current_batch_size = min(batch_size, remaining)
                
                if current_batch_size <= 0:
                    break
                
                future = executor.submit(self._generate_batch_worker, current_batch_size, batch_idx)
                future_to_batch[future] = batch_idx
            
            # Collecte des résultats
            for future in as_completed(future_to_batch):
                batch_hands = future.result()
                hands.extend(batch_hands)
                
                if len(hands) % 50000 == 0:
                    self.logger.info(f"Progression: {len(hands)}/{target_hands} mains générées")
        
        self.logger.info(f"Génération terminée: {len(hands)} mains créées")
        return hands[:target_hands]
    
    def _generate_batch_worker(self, batch_size: int, batch_idx: int) -> List[ParsedHand]:
        """Worker pour génération parallèle"""
        hands = []
        
        for i in range(batch_size):
            street = self._select_street()
            hand_id = f"{batch_idx * 10000 + i}"
            hand = self._generate_hand_for_street(street, hand_id)
            if hand:
                hands.append(hand)
        
        return hands
    
    def _select_street(self) -> int:
        """Sélectionne une street selon les ratios configurés"""
        rand = random.random()
        
        if rand < self.settings.preflop_ratio:
            return 0  # preflop
        elif rand < self.settings.preflop_ratio + self.settings.flop_ratio:
            return 1  # flop
        elif rand < self.settings.preflop_ratio + self.settings.flop_ratio + self.settings.turn_ratio:
            return 2  # turn
        else:
            return 3  # river
    
    def _generate_hand_for_street(self, street: int, hand_id: str) -> Optional[ParsedHand]:
        """Génère une main pour une street donnée"""
        try:
            # Sélection deck et cartes
            deck = self.deck.copy()
            random.shuffle(deck)
            
            # Cartes héros
            hero_cards = (deck.pop(), deck.pop())
            
            # Board selon street
            board_cards = []
            if street >= 1:  # flop
                board_cards.extend([deck.pop(), deck.pop(), deck.pop()])
            if street >= 2:  # turn
                board_cards.append(deck.pop())
            if street >= 3:  # river
                board_cards.append(deck.pop())
            
            # Configuration de jeu
            blinds = random.choice(self.settings.blind_levels)
            stack_size = random.choice(self.settings.stack_sizes)
            
            # Génération d'actions réalistes
            actions = self._generate_realistic_actions(street, hero_cards, board_cards, blinds)
            
            # Calcul du pot et résultat
            pot_size = self._calculate_pot_from_actions(actions, blinds)
            result = self._calculate_realistic_result(hero_cards, board_cards, actions, pot_size)
            
            return ParsedHand(
                hand_id=hand_id,
                hero_cards=hero_cards,
                board_cards=board_cards,
                actions=actions,
                pot_size=pot_size,
                hero_stack=stack_size,
                villain_stack=stack_size,
                position=random.randint(0, 1),
                blinds=blinds,
                result=result,
                street=street
            )
            
        except Exception as e:
            self.logger.error(f"Erreur génération main: {e}")
            return None
    
    def _generate_realistic_actions(self, street: int, hero_cards: Tuple[str, str], 
                                   board_cards: List[str], blinds: Tuple[float, float]) -> List[str]:
        """Génère une séquence d'actions réaliste"""
        actions = []
        
        # Force de la main héros
        hand_strength = self._evaluate_hand_strength(hero_cards, board_cards)
        
        # Nombre d'actions par street (réaliste)
        max_actions_per_street = {0: 4, 1: 3, 2: 3, 3: 2}  # preflop peut être plus long
        
        for current_street in range(street + 1):
            street_actions = self._generate_street_actions(
                current_street, hand_strength, blinds, len(board_cards) >= (current_street * 3)
            )
            actions.extend(street_actions)
        
        return actions
    
    def _generate_street_actions(self, street: int, hand_strength: float, 
                                blinds: Tuple[float, float], has_board: bool) -> List[str]:
        """Génère les actions pour une street"""
        actions = []
        num_actions = random.randint(1, 4 if street == 0 else 3)
        
        # Probabilités d'actions selon force de main
        if hand_strength > 0.8:  # Main très forte
            action_probs = {'bet': 0.5, 'raise': 0.3, 'call': 0.15, 'check': 0.05, 'fold': 0.0}
        elif hand_strength > 0.6:  # Main forte
            action_probs = {'bet': 0.3, 'raise': 0.2, 'call': 0.3, 'check': 0.15, 'fold': 0.05}
        elif hand_strength > 0.4:  # Main moyenne
            action_probs = {'bet': 0.15, 'raise': 0.1, 'call': 0.4, 'check': 0.25, 'fold': 0.1}
        else:  # Main faible
            action_probs = {'bet': 0.05, 'raise': 0.05, 'call': 0.2, 'check': 0.4, 'fold': 0.3}
        
        for i in range(num_actions):
            # Sélection action pondérée
            action = np.random.choice(
                list(action_probs.keys()),
                p=list(action_probs.values())
            )
            
            # Ajout de sizing pour bet/raise
            if action in ['bet', 'raise']:
                sizing = self._generate_bet_sizing(blinds[1])
                actions.append(f"{action}_{sizing}")
            else:
                actions.append(action)
            
            # Arrêt si fold
            if action == 'fold':
                break
        
        return actions
    
    def _generate_bet_sizing(self, big_blind: float) -> int:
        """Génère un sizing de bet réaliste"""
        # Sizings standards en % du pot ou en BB
        pot_sizings = [0.25, 0.33, 0.5, 0.66, 0.75, 1.0, 1.5]
        bb_sizings = [2, 2.5, 3, 4, 5]
        
        if random.random() < 0.7:  # 70% pot-sized bets
            sizing = int(random.choice(pot_sizings) * 100)  # Convert to percentage
        else:  # 30% BB-sized bets
            sizing = int(random.choice(bb_sizings) * big_blind)
        
        return max(sizing, int(big_blind))  # Minimum 1 BB
    
    def _evaluate_hand_strength(self, hero_cards: Tuple[str, str], board_cards: List[str]) -> float:
        """Évalue la force de la main (0.0 à 1.0)"""
        # Simplification : évaluation basée sur les cartes et board
        
        # Parse cartes
        ranks = [card[0] for card in hero_cards]
        suits = [card[1] for card in hero_cards]
        
        strength = 0.0
        
        # Pocket pairs
        if ranks[0] == ranks[1]:
            pair_strength = {'A': 0.9, 'K': 0.85, 'Q': 0.8, 'J': 0.75, 'T': 0.7}
            strength = pair_strength.get(ranks[0], 0.6)
        
        # High cards
        elif 'A' in ranks:
            strength = 0.7 if 'K' in ranks or 'Q' in ranks else 0.6
        elif 'K' in ranks and 'Q' in ranks:
            strength = 0.65
        
        # Suited bonus
        if suits[0] == suits[1]:
            strength += 0.1
        
        # Connecteur bonus
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        if abs(rank_values.get(ranks[0], 0) - rank_values.get(ranks[1], 0)) == 1:
            strength += 0.05
        
        # Ajustement selon board (simplifié)
        if board_cards:
            # Check for pairs, flushes, straights etc. (implementation simplifiée)
            hero_ranks = set(ranks)
            board_ranks = set([card[0] for card in board_cards])
            
            # Paire avec le board
            if hero_ranks & board_ranks:
                strength += 0.2
            
            # Two pair potentiel
            if len(hero_ranks & board_ranks) == 2:
                strength += 0.3
        
        return min(1.0, max(0.0, strength))
    
    def _calculate_pot_from_actions(self, actions: List[str], blinds: Tuple[float, float]) -> float:
        """Calcule la taille du pot selon les actions"""
        pot = blinds[0] + blinds[1]  # Start with blinds
        
        for action in actions:
            if action.startswith('bet_'):
                bet_size = int(action.split('_')[1])
                pot += bet_size
            elif action.startswith('raise_'):
                raise_size = int(action.split('_')[1])
                pot += raise_size
            elif action == 'call':
                pot += blinds[1]  # Assume BB call
        
        return pot
    
    def _calculate_realistic_result(self, hero_cards: Tuple[str, str], board_cards: List[str], 
                                   actions: List[str], pot_size: float) -> float:
        """Calcule un résultat réaliste selon la force de main"""
        
        # Si fold, perte des blinds/investissement
        if 'fold' in actions:
            return -pot_size * 0.1  # Perte partielle
        
        # Force de main
        hand_strength = self._evaluate_hand_strength(hero_cards, board_cards)
        
        # Win probability selon force
        win_prob = hand_strength
        
        # Résultat selon probabilité
        if random.random() < win_prob:
            return pot_size * 0.5  # Gain
        else:
            return -pot_size * 0.3  # Perte
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de génération"""
        return {
            'hands_generated': self.hands_generated,
            'generation_time': self.generation_time,
            'hands_per_second': self.hands_generated / max(self.generation_time, 0.001),
            'settings': {
                'max_hands': self.settings.max_hands,
                'batch_size': self.settings.hands_per_batch
            }
        }