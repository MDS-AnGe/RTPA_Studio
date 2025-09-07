"""
Version headless du système de capture pour environnement sans X11
Simule les données OCR pour démonstration
"""

import time
import random
from typing import Dict, Any, Optional
from ..utils.logger import get_logger

class ScreenCaptureHeadless:
    """Version simulation du système de capture d'écran"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Simulation de données de poker
        self.simulation_hands = [
            {
                'hero_cards': ('As', 'Kh'),
                'board_cards': ['Ah', 'Kd', '7c'],
                'pot_size': 150.0,
                'hero_stack': 2500.0,
                'small_blind': 5.0,
                'big_blind': 10.0,
                'action_to_hero': True
            },
            {
                'hero_cards': ('Qd', 'Qs'),
                'board_cards': ['9h', '3c', '2s', 'Jd'],
                'pot_size': 340.0,
                'hero_stack': 1850.0,
                'small_blind': 5.0,
                'big_blind': 10.0,
                'action_to_hero': True
            },
            {
                'hero_cards': ('Ac', '7d'),
                'board_cards': ['Ah', '7h', '2c', '9s', 'Kh'],
                'pot_size': 890.0,
                'hero_stack': 1200.0,
                'small_blind': 5.0,
                'big_blind': 10.0,
                'action_to_hero': False
            }
        ]
        
        self.current_hand_index = 0
        self.hand_progress = 0  # 0-100, progression dans la main
        
        self.logger.info("ScreenCaptureHeadless initialisé (mode simulation)")
    
    def capture_and_analyze(self) -> Optional[Dict[str, Any]]:
        """Simule une capture et analyse"""
        try:
            # Progression automatique des mains
            self.hand_progress += 1
            if self.hand_progress > 100:
                self.hand_progress = 0
                self.current_hand_index = (self.current_hand_index + 1) % len(self.simulation_hands)
            
            # Récupération de la main actuelle
            current_hand = self.simulation_hands[self.current_hand_index].copy()
            
            # Simulation de variations
            current_hand['pot_size'] += random.uniform(-50, 50)
            current_hand['hero_stack'] += random.uniform(-100, 100)
            
            # Ajout de métadonnées
            current_hand.update({
                'timestamp': time.time(),
                'confidence': random.uniform(85, 98),
                'poker_client': 'simulation',
                'current_bet': random.uniform(0, 50),
                'players_count': 9,
                'hero_position': random.randint(0, 8),
                'ante': 0.0,
                'tournament_level': 1,
                'rebuys_available': 0,
                'table_type': 'cashgame'
            })
            
            return current_hand
            
        except Exception as e:
            self.logger.error(f"Erreur simulation OCR: {e}")
            return None
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Retourne des métriques simulées"""
        return {
            'avg_capture_time_ms': 12.0,
            'avg_ocr_time_ms': 28.0,
            'avg_confidence': 92.5,
            'success_rate': 96.8
        }