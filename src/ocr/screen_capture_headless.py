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
        
        # Noms de joueurs réalistes pour simulation
        self.player_names = [
            "PokerPro", "AliceBluff", "BobNuts", "CharlieTilt", "DianaAce", 
            "EdRaise", "FionaCall", "GaryFold", "HelenShark", "IvanFish",
            "JackPot", "KarenNit", "LeoLAG", "MonaTag", "NickRock"
        ]
        
        # Position mapping 9-max
        self.position_names = {
            0: "UTG", 1: "UTG+1", 2: "MP1", 3: "MP2", 4: "MP3", 
            5: "CO", 6: "BTN", 7: "SB", 8: "BB"
        }
        
        # Simulation de données de poker avec joueurs complets 9-max
        self.simulation_hands = [
            {
                'hero_cards': ('As', 'Kh'),
                'board_cards': ['Ah', 'Kd', '7c'],
                'pot_size': 150.0,
                'hero_stack': 2500.0,
                'small_blind': 5.0,
                'big_blind': 10.0,
                'action_to_hero': True,
                'players_at_table': self._generate_players_data(0)
            },
            {
                'hero_cards': ('Qd', 'Qs'),
                'board_cards': ['9h', '3c', '2s', 'Jd'],
                'pot_size': 340.0,
                'hero_stack': 1850.0,
                'small_blind': 5.0,
                'big_blind': 10.0,
                'action_to_hero': True,
                'players_at_table': self._generate_players_data(1)
            },
            {
                'hero_cards': ('Ac', '7d'),
                'board_cards': ['Ah', '7h', '2c', '9s', 'Kh'],
                'pot_size': 890.0,
                'hero_stack': 1200.0,
                'small_blind': 5.0,
                'big_blind': 10.0,
                'action_to_hero': False,
                'players_at_table': self._generate_players_data(2)
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

    def _generate_players_data(self, scenario: int) -> list:
        """Génère des données de joueurs réalistes pour une table 9-max"""
        players = []
        
        # Nombre de joueurs actifs selon le scénario (6-9 joueurs)
        num_players = [8, 9, 7][scenario % 3]
        
        # Position hero aléatoire
        hero_position = random.randint(0, 8)
        
        # Positions occupées (excluant le héros)
        occupied_positions = []
        available_positions = [i for i in range(9) if i != hero_position]
        random.shuffle(available_positions)
        occupied_positions = available_positions[:num_players-1]
        
        # Créer les joueurs
        for i, position in enumerate(occupied_positions):
            player_name = random.choice(self.player_names)
            
            # Stack réaliste
            stack = random.uniform(500, 5000)
            
            # Stats poker réalistes selon type de joueur
            player_type = random.choice(['tight', 'loose', 'aggressive', 'passive'])
            if player_type == 'tight':
                vpip = random.randint(8, 18)
                pfr = random.randint(6, 15)
            elif player_type == 'loose':
                vpip = random.randint(25, 45)
                pfr = random.randint(8, 20)
            elif player_type == 'aggressive':
                vpip = random.randint(18, 35)
                pfr = random.randint(15, 30)
            else:  # passive
                vpip = random.randint(20, 40)
                pfr = random.randint(5, 12)
            
            # Status du joueur
            status = random.choice(['actif', 'fold', 'sitting_out']) if random.random() < 0.85 else 'fold'
            
            # Positions spéciales
            is_button = position == 6
            is_sb = position == 7  
            is_bb = position == 8
            
            players.append({
                'name': player_name,
                'position': position,
                'position_name': self.position_names[position],
                'stack': stack,
                'vpip': vpip,
                'pfr': pfr,
                'status': status,
                'is_button': is_button,
                'is_sb': is_sb,
                'is_bb': is_bb,
                'cards_visible': status == 'actif',
                'action_pending': status == 'actif' and random.random() < 0.3
            })
        
        return players