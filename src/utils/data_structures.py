"""
Structures de données pour RTPA Studio
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional

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