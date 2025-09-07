"""
Abstraction des actions pour CFR
"""

from typing import List, Dict
from ..utils.data_structures import PokerState

class ActionAbstraction:
    """Système d'abstraction pour l'espace d'actions"""
    
    def __init__(self):
        self.action_buckets = {
            'fold': 0,
            'check': 1, 
            'call': 2,
            'bet_small': 3,
            'bet_medium': 4,
            'bet_large': 5,
            'bet_allin': 6
        }
    
    def get_legal_actions(self, poker_state: PokerState) -> List[str]:
        """Retourne les actions légales pour un état donné"""
        actions = []
        
        # Fold toujours possible (sauf si check gratuit)
        if poker_state.current_bet > 0:
            actions.append('fold')
        
        # Check/Call
        if poker_state.current_bet == 0:
            actions.append('check')
        else:
            actions.append('call')
        
        # Bet/Raise si stack suffisant
        min_bet = max(poker_state.current_bet * 2, poker_state.pot_size * 0.25)
        if poker_state.hero_stack > min_bet:
            actions.extend(['bet_small', 'bet_medium', 'bet_large'])
            
        # All-in toujours possible
        if poker_state.hero_stack > 0:
            actions.append('bet_allin')
            
        return actions
    
    def get_action_bucket(self, action: str) -> int:
        """Retourne le bucket pour une action"""
        return self.action_buckets.get(action, 0)