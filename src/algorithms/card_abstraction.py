"""
Abstraction des cartes pour CFR
"""

from typing import List, Tuple
import hashlib

class CardAbstraction:
    """Système d'abstraction pour réduire l'espace des cartes"""
    
    def __init__(self, num_buckets: int = 64):
        self.num_buckets = num_buckets
        self.cache = {}
    
    def get_bucket(self, hero_cards: Tuple[str, str], board_cards: List[str], street: int) -> int:
        """Retourne le bucket d'abstraction pour une situation donnée"""
        # Cache key
        cache_key = f"{hero_cards}_{board_cards}_{street}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Calcul simple basé sur hash pour la démo
        combined = f"{hero_cards[0]}{hero_cards[1]}{''.join(board_cards)}{street}"
        hash_value = int(hashlib.md5(combined.encode()).hexdigest()[:8], 16)
        bucket = hash_value % self.num_buckets
        
        self.cache[cache_key] = bucket
        return bucket
    
    def get_bucket_preflop(self, hero_cards: Tuple[str, str]) -> int:
        """Retourne le bucket d'abstraction pour preflop"""
        return self.get_bucket(hero_cards, [], 0)