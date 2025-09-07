"""
Intégration du module C++ pour optimisations
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CPPIntegration:
    """Wrapper pour le module C++ optimisé"""
    
    def __init__(self):
        self.cpp_module = None
        self.cpp_available = False
        self._initialize_cpp()
    
    def _initialize_cpp(self):
        """Initialise le module C++ si disponible"""
        try:
            import rtpa_core
            self.cpp_module = rtpa_core
            self.cpp_module.init_cfr_engine()
            self.cpp_available = True
            logger.info("Module C++ chargé avec succès")
        except ImportError:
            logger.warning("Module C++ non disponible, utilisation des versions Python")
            self.cpp_available = False
        except Exception as e:
            logger.error(f"Erreur chargement module C++: {e}")
            self.cpp_available = False
    
    def calculate_equity_optimized(self, hero_cards: List[int], board_cards: List[int], 
                                 num_opponents: int = 1, simulations: int = 10000) -> float:
        """Calcul d'équité optimisé C++ ou fallback Python"""
        if self.cpp_available and self.cpp_module:
            try:
                return self.cpp_module.calculate_equity_fast(
                    hero_cards, board_cards, num_opponents, simulations
                )
            except Exception as e:
                logger.error(f"Erreur calcul C++: {e}")
        
        # Fallback Python
        return self._calculate_equity_python(hero_cards, board_cards, num_opponents, simulations)
    
    def get_recommendation_optimized(self, game_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recommandation optimisée C++ ou fallback Python"""
        if self.cpp_available and self.cpp_module:
            try:
                # Conversion de l'état de jeu
                street = 0  # 0=preflop, 1=flop, 2=turn, 3=river
                hero_card1 = self._card_to_int(game_state.get('hero_cards', ['', ''])[0])
                hero_card2 = self._card_to_int(game_state.get('hero_cards', ['', ''])[1])
                position = game_state.get('hero_position', 0)
                num_players = game_state.get('players_count', 9)
                pot_size = game_state.get('pot_size', 0.0)
                hero_stack = game_state.get('hero_stack', 0.0)
                current_bet = game_state.get('current_bet', 0.0)
                
                # Conversion des cartes board
                board_cards = []
                for card_str in game_state.get('board_cards', []):
                    if card_str:
                        board_cards.append(self._card_to_int(card_str))
                
                table_type = game_state.get('table_type', 'cashgame')
                action_to_hero = 1 if game_state.get('action_to_hero', True) else 0
                
                return self.cpp_module.get_recommendation_fast(
                    street, hero_card1, hero_card2, position, num_players,
                    pot_size, hero_stack, current_bet, board_cards,
                    table_type, action_to_hero
                )
            except Exception as e:
                logger.error(f"Erreur recommandation C++: {e}")
        
        # Fallback Python
        return self._get_recommendation_python(game_state)
    
    def _card_to_int(self, card_str: str) -> int:
        """Convertit une carte string en entier"""
        if not card_str or len(card_str) != 2:
            return -1
        
        rank_char = card_str[0].upper()
        suit_char = card_str[1].lower()
        
        # Mapping des rangs
        rank_map = {
            '2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7,
            'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12
        }
        
        # Mapping des couleurs
        suit_map = {'s': 0, 'h': 1, 'd': 2, 'c': 3}
        
        if rank_char in rank_map and suit_char in suit_map:
            return rank_map[rank_char] + suit_map[suit_char] * 13
        
        return -1
    
    def _calculate_equity_python(self, hero_cards: List[int], board_cards: List[int], 
                               num_opponents: int, simulations: int) -> float:
        """Version Python du calcul d'équité"""
        import random
        
        # Simulation simplifiée
        wins = 0
        deck = list(range(52))
        
        # Retire les cartes connues
        used_cards = set(hero_cards + board_cards)
        available_deck = [card for card in deck if card not in used_cards]
        
        for _ in range(min(simulations, 1000)):  # Limite pour performance
            random.shuffle(available_deck)
            
            # Simule une main gagnante avec probabilité basée sur les cartes
            base_prob = 0.5
            if len(hero_cards) == 2:
                # Ajustement basique selon les cartes héros
                if hero_cards[0] % 13 == hero_cards[1] % 13:  # Paire
                    base_prob = 0.7
                elif abs(hero_cards[0] % 13 - hero_cards[1] % 13) <= 1:  # Connectées
                    base_prob = 0.6
            
            if random.random() < base_prob:
                wins += 1
        
        return wins / min(simulations, 1000)
    
    def _get_recommendation_python(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Version Python de la recommandation"""
        # Logique simplifiée
        pot_size = game_state.get('pot_size', 0.0)
        hero_stack = game_state.get('hero_stack', 0.0)
        current_bet = game_state.get('current_bet', 0.0)
        hero_cards = game_state.get('hero_cards', ['', ''])
        
        # Analyse basique
        win_prob = 50.0  # Valeur par défaut
        
        # Ajustements selon les cartes
        if len(hero_cards) == 2 and hero_cards[0] and hero_cards[1]:
            if hero_cards[0][0] == hero_cards[1][0]:  # Paire
                win_prob = 70.0
            elif hero_cards[0][0] in 'AKQJ' or hero_cards[1][0] in 'AKQJ':  # Cartes hautes
                win_prob = 60.0
        
        # Décision d'action
        if win_prob > 65:
            action = "bet_large"
            bet_size = pot_size * 0.75
            risk_level = 40.0
        elif win_prob > 50:
            action = "bet_medium"
            bet_size = pot_size * 0.5
            risk_level = 50.0
        elif current_bet == 0:
            action = "check"
            bet_size = 0.0
            risk_level = 30.0
        elif current_bet < pot_size * 0.3:
            action = "call"
            bet_size = current_bet
            risk_level = 60.0
        else:
            action = "fold"
            bet_size = 0.0
            risk_level = 0.0
        
        return {
            'action_type': action,
            'bet_size': bet_size,
            'win_probability': win_prob,
            'expected_value': win_prob / 100.0 * pot_size - (1 - win_prob / 100.0) * bet_size,
            'risk_level': risk_level,
            'confidence': min(95.0, 50.0 + win_prob / 2),
            'reasoning': f"Analyse Python - Probabilité {win_prob:.1f}%"
        }
    
    def cleanup(self):
        """Nettoyage des ressources C++"""
        if self.cpp_available and self.cpp_module:
            try:
                self.cpp_module.cleanup_cfr()
            except Exception as e:
                logger.error(f"Erreur nettoyage C++: {e}")

# Instance globale
cpp_integration = CPPIntegration()