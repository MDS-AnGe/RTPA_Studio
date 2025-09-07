"""
Gestionnaire principal de l'application RTPA Studio
"""

import threading
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
import yaml

from ..database.memory_db import MemoryDatabase
try:
    from ..ocr.screen_capture import ScreenCapture
except Exception:
    from ..ocr.screen_capture_headless import ScreenCaptureHeadless as ScreenCapture
from ..algorithms.cfr_engine import CFREngine
from ..utils.logger import get_logger
from ..config.settings import Settings

@dataclass
class GameState:
    """État actuel du jeu"""
    table_type: str = "cashgame"  # cashgame ou tournament
    players_count: int = 9
    hero_position: int = 0
    hero_cards: tuple = ()
    board_cards: tuple = ()
    pot_size: float = 0.0
    hero_stack: float = 0.0
    small_blind: float = 0.0
    big_blind: float = 0.0
    current_bet: float = 0.0
    action_to_hero: bool = False
    ante: float = 0.0
    tournament_level: int = 1
    rebuys_available: int = 0

class RTAPStudioManager:
    """Gestionnaire principal de RTPA Studio"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.settings = Settings()
        self.database = MemoryDatabase()
        self.screen_capture = ScreenCapture()
        self.cfr_engine = CFREngine()
        
        self.game_state = GameState()
        self.running = False
        self.analysis_thread = None
        self.ocr_thread = None
        
        # Statistiques
        self.hands_played = 0
        self.hands_won = 0
        self.win_rate = 0.0
        self.expected_win_rate = 0.65  # Taux normal d'un joueur pro
        
        self.logger.info("RTAPStudioManager initialisé")
    
    def start(self):
        """Démarre le système d'analyse en temps réel"""
        if self.running:
            return
            
        self.running = True
        self.logger.info("Démarrage du système d'analyse temps réel")
        
        # Démarrage des threads d'analyse
        self.ocr_thread = threading.Thread(target=self._ocr_loop, daemon=True)
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        
        self.ocr_thread.start()
        self.analysis_thread.start()
    
    def stop(self):
        """Arrête le système d'analyse"""
        self.running = False
        self.logger.info("Arrêt du système d'analyse")
    
    def _ocr_loop(self):
        """Boucle de capture et d'analyse OCR"""
        while self.running:
            try:
                # Capture et analyse de l'écran
                game_data = self.screen_capture.capture_and_analyze()
                if game_data:
                    self._update_game_state(game_data)
                
                time.sleep(0.1)  # 100ms entre les captures
                
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle OCR: {e}")
                time.sleep(1)
    
    def _analysis_loop(self):
        """Boucle de calcul CFR/Nash en continu"""
        while self.running:
            try:
                if self.game_state.action_to_hero:
                    # Calcul des recommandations
                    recommendation = self.cfr_engine.get_recommendation(self.game_state)
                    self._update_recommendation(recommendation)
                
                time.sleep(0.05)  # 50ms entre les calculs
                
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle d'analyse: {e}")
                time.sleep(1)
    
    def _update_game_state(self, game_data: Dict[str, Any]):
        """Met à jour l'état du jeu avec les données OCR"""
        # Extraction et mise à jour des données
        for key, value in game_data.items():
            if hasattr(self.game_state, key):
                setattr(self.game_state, key, value)
        
        # Sauvegarde en base mémoire
        self.database.store_game_state(self.game_state)
    
    def _update_recommendation(self, recommendation: Dict[str, Any]):
        """Met à jour les recommandations de jeu"""
        self.database.store_recommendation(recommendation)
    
    def get_current_state(self) -> GameState:
        """Retourne l'état actuel du jeu"""
        return self.game_state
    
    def get_recommendation(self) -> Optional[Dict[str, Any]]:
        """Retourne la dernière recommandation"""
        return self.database.get_latest_recommendation()
    
    def get_statistics(self) -> Dict[str, float]:
        """Retourne les statistiques de performance"""
        return {
            'hands_played': self.hands_played,
            'hands_won': self.hands_won,
            'win_rate': self.win_rate,
            'expected_win_rate': self.expected_win_rate,
            'performance_ratio': self.win_rate / self.expected_win_rate if self.expected_win_rate > 0 else 0
        }
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Met à jour les paramètres"""
        self.settings.update(new_settings)
        self.cfr_engine.update_settings(new_settings)
    
    def manual_override(self, risk_percentage: float):
        """Override manuel du pourcentage de risque"""
        self.settings.risk_percentage = risk_percentage
        self.settings.manual_risk_override = True
        self.logger.info(f"Override manuel du risque: {risk_percentage}%")