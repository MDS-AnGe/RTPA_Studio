"""
Gestionnaire principal de l'application RTPA Studio
"""

import threading
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
import yaml

from ..database.memory_db import MemoryDatabase
import os
# 🔍 DÉTECTION INTELLIGENTE D'ENVIRONNEMENT
import platform
import sys

IS_REPLIT = bool(os.getenv('REPL_SLUG') or os.getenv('REPLIT_ENVIRONMENT'))
IS_WINDOWS = platform.system() == 'Windows'

if IS_REPLIT:
    # Mode Replit - Fallback simulation temporaire pour développement
    print("🎯 Mode développement Replit - Simulation temporaire")
    from ..ocr.screen_capture_headless import ScreenCaptureHeadless as ScreenCapture
    REAL_CAPTURE_ACTIVE = False
elif IS_WINDOWS:
    # Mode Windows - Capture réelle forcée
    print("🔍 WINDOWS DÉTECTÉ - Activation capture d'écran réelle")
    print("📹 Mode OCR temps réel pour Winamax")
    try:
        from ..ocr.screen_capture import ScreenCapture
        print("✅ Capture d'écran réelle activée sur Windows")
        print("🎯 Prêt pour détection temps réel Winamax")
        REAL_CAPTURE_ACTIVE = True
    except Exception as e:
        print(f"❌ ERREUR Windows: {e}")
        print("🔧 Vérifiez les dépendances: pip install mss opencv-python pytesseract")
        raise RuntimeError(f"Capture d'écran Windows requise: {e}")
else:
    # Autres OS - Tentative capture réelle
    try:
        from ..ocr.screen_capture import ScreenCapture
        print("✅ Capture d'écran réelle activée")
        REAL_CAPTURE_ACTIVE = True
    except Exception as e:
        print(f"⚠️ Capture non disponible: {e}")
        from ..ocr.screen_capture_headless import ScreenCaptureHeadless as ScreenCapture
        REAL_CAPTURE_ACTIVE = False
from ..algorithms.cfr_engine import CFREngine
from ..utils.logger import get_logger
from ..config.settings import Settings
from ..utils.platform_detector import PlatformDetector

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
        self.platform_detector = PlatformDetector()
        self.current_platform = None  # Plateforme actuellement détectée
        
        # Initialisation de l'entraînement CFR automatique
        self._init_cfr_training()
        
        self.game_state = GameState()
        self.running = False
        self.analysis_thread = None
        self.auto_mode = True  # Mode automatique activé
        self.current_status = "waiting"  # waiting, active, paused
        self.status_callbacks = []
        
        # Configuration du détecteur de plateformes
        self.platform_detector.set_status_callback(self._on_platform_status_change)
        self.ocr_thread = None
        
        # Référence à la GUI pour les callbacks de statut
        self.gui_window = None
        
        # Statistiques
        self.hands_played = 0
        self.hands_won = 0
        self.win_rate = 0.0
        self.expected_win_rate = 0.65  # Taux normal d'un joueur pro
        
        self.logger.info("RTPA Studio Manager initialisé avec entraînement CFR automatique")
    
    def set_gui_window(self, gui_window):
        """Définit la référence à la fenêtre GUI pour les callbacks de statut"""
        self.gui_window = gui_window
    
    def _init_cfr_training(self):
        """Initialise l'entraînement CFR selon le profil de performance"""
        try:
            from ..config.performance_profiles import get_performance_manager
            
            # Récupération du profil actuel
            profile_manager = get_performance_manager()
            profile = profile_manager.get_current_profile()
            
            if profile.delayed_start:
                # Initialisation différée selon le profil
                import threading
                init_thread = threading.Thread(target=self._delayed_cfr_init, daemon=True)
                init_thread.start()
            else:
                # Initialisation immédiate pour profil Éco
                if profile.auto_training_enabled:
                    self.cfr_engine.init_trainer()
                    self.logger.info("Entraînement CFR initialisé (mode immédiat)")
                else:
                    self.logger.info("Entraînement CFR désactivé (profil Éco)")
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation CFR training: {e}")
    
    def _delayed_cfr_init(self):
        """Initialisation différée du CFR selon le profil"""
        try:
            from ..config.performance_profiles import get_performance_manager
            
            profile_manager = get_performance_manager()
            profile = profile_manager.get_current_profile()
            
            # Délai selon le profil
            time.sleep(profile.startup_delay)
            
            if profile.auto_training_enabled:
                self.cfr_engine.init_trainer()
                self.logger.info(f"Entraînement CFR initialisé (profil {profile.name}, délai {profile.startup_delay}s)")
            else:
                self.logger.info(f"Entraînement CFR désactivé (profil {profile.name})")
                
        except Exception as e:
            self.logger.error(f"Erreur initialisation différée CFR: {e}")
        
        # Démarrer la surveillance automatique des plateformes
        self.platform_detector.start_monitoring()
    
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
        ocr_iterations = 0
        while self.running:
            try:
                # Capture et analyse de l'écran
                game_data = self.screen_capture.capture_and_analyze()
                ocr_iterations += 1
                
                # Debug pour Windows
                if REAL_CAPTURE_ACTIVE and ocr_iterations % 20 == 0:
                    print(f"🔍 OCR itération {ocr_iterations} - Données: {bool(game_data)}")
                
                if game_data:
                    if REAL_CAPTURE_ACTIVE:
                        print(f"✅ Données OCR reçues: {list(game_data.keys())}")
                    self._update_game_state(game_data)
                elif REAL_CAPTURE_ACTIVE and ocr_iterations % 50 == 0:
                    print("⚠️ Aucune donnée OCR détectée - Vérifiez que Winamax est ouvert")
                
                time.sleep(0.05)  # 50ms entre les captures pour réactivité maximale
                
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle OCR: {e}")
                if REAL_CAPTURE_ACTIVE:
                    print(f"❌ Erreur capture OCR: {e}")
                time.sleep(1)
    
    def _analysis_loop(self):
        """Boucle de calcul CFR/Nash en continu"""
        while self.running:
            try:
                if self.game_state.action_to_hero:
                    # Calcul des recommandations
                    recommendation = self.cfr_engine.get_recommendation(self.game_state)
                    self._update_recommendation(recommendation)
                
                time.sleep(0.025)  # 25ms entre les calculs pour temps réel
                
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
    
    def has_active_platform(self) -> bool:
        """Vérifie si une plateforme poker est active"""
        if hasattr(self, 'platform_detector') and self.platform_detector:
            return self.platform_detector.is_any_platform_active()
        return False
    
    def get_current_state(self) -> GameState:
        """Retourne l'état actuel du jeu"""
        # Retourner état vide si aucune plateforme active
        if not self.has_active_platform():
            return GameState()  # État vide par défaut
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
        
        # Mise à jour des paramètres GPU si modifiés
        if 'gpu_enabled' in new_settings or 'gpu_memory_limit' in new_settings:
            gpu_enabled = new_settings.get('gpu_enabled', getattr(self.settings, 'gpu_enabled', False))
            gpu_memory = new_settings.get('gpu_memory_limit', getattr(self.settings, 'gpu_memory_limit', 0.8))
            
            if hasattr(self.cfr_engine, 'update_gpu_settings'):
                self.cfr_engine.update_gpu_settings(gpu_enabled, gpu_memory / 100.0)
                self.logger.info(f"Paramètres GPU mis à jour: enabled={gpu_enabled}, memory={gpu_memory}%")
    
    def manual_override(self, risk_percentage: float):
        """Override manuel du pourcentage de risque"""
        self.settings.risk_percentage = risk_percentage
        self.settings.manual_risk_override = True
        self.logger.info(f"Override manuel du risque: {risk_percentage}%")
    
    def add_status_callback(self, callback):
        """Ajoute un callback pour les changements d'état"""
        self.status_callbacks.append(callback)
    
    def _notify_status_change(self, status, details=None):
        """Notifie les callbacks des changements d'état avec gestion robuste"""
        self.current_status = status
        failed_callbacks = []
        
        for i, callback in enumerate(self.status_callbacks):
            try:
                if callable(callback):
                    callback(status, details)
                else:
                    self.logger.warning(f"Callback {i} n'est pas callable")
                    failed_callbacks.append(i)
            except TypeError as e:
                self.logger.error(f"Erreur type callback {i}: {e}")
                failed_callbacks.append(i)
            except Exception as e:
                self.logger.error(f"Erreur callback {i}: {e}")
                import traceback
                failed_callbacks.append(i)
        
        # Nettoyer les callbacks défaillants
        if failed_callbacks:
            self.logger.info(f"Suppression de {len(failed_callbacks)} callbacks défaillants")
            for i in reversed(failed_callbacks):
                self.status_callbacks.pop(i)
    
    def _on_platform_status_change(self, event_type, data):
        """Gère les changements de statut des plateformes avec validation"""
        try:
            if not isinstance(event_type, str):
                self.logger.warning(f"Type d'événement invalide: {type(event_type)}")
                return
            
            if event_type == 'platform_detected':
                self.logger.info(f"Plateforme détectée: {data}")
                
                # 🎯 AUTO-CALIBRAGE OCR AUTOMATIQUE
                if data != self.current_platform:
                    self.current_platform = data
                    self._auto_apply_ocr_profile(data)
                
                # Notifier la GUI
                if self.gui_window:
                    self.gui_window.on_platform_detected(data)
                if not self.running and hasattr(self, '_auto_start'):
                    self._auto_start()
            
            elif event_type == 'platform_closed':
                self.logger.info(f"Plateforme fermée: {data}")
                # Notifier la GUI si aucune plateforme n'est active
                if (hasattr(self, 'platform_detector') and 
                    hasattr(self.platform_detector, 'is_any_platform_active') and
                    not self.platform_detector.is_any_platform_active()):
                    if self.gui_window:
                        self.gui_window.on_platform_closed()
                    self._auto_stop()
            
            elif event_type == 'status':
                if data == 'active' and not self.running:
                    if self.gui_window:
                        self.gui_window.update_connection_status("active")
                    self._auto_start()
                elif data == 'waiting' and self.running:
                    if self.gui_window:
                        self.gui_window.update_connection_status("waiting")
                    self._auto_stop()
                    
        except Exception as e:
            self.logger.error(f"Erreur gestion changement statut plateforme: {e}")
            import traceback
    
    def _auto_apply_ocr_profile(self, platform_name):
        """Applique automatiquement le profil OCR pour la plateforme détectée"""
        try:
            print(f"🎯 AUTO-CALIBRAGE: Application profil OCR pour {platform_name}")
            
            # Charger les zones OCR prédéfinies pour cette plateforme
            if hasattr(self.screen_capture, 'roi_presets'):
                if platform_name in self.screen_capture.roi_presets:
                    
                    # Appliquer le preset
                    preset = self.screen_capture.roi_presets[platform_name]
                    self.screen_capture.roi_zones = preset.copy()
                    self.screen_capture.current_client = platform_name
                    
                    print(f"✅ Profil OCR {platform_name} appliqué automatiquement")
                    print(f"📋 Zones configurées: {list(preset.keys())}")
                    
                    # Notifier la GUI pour mise à jour interface
                    if self.gui_window:
                        self.gui_window.load_ocr_preset_for_platform(platform_name)
                        # Auto-appliquer le calibrage
                        if hasattr(self.gui_window, 'apply_ocr_calibration'):
                            self.gui_window.apply_ocr_calibration()
                            print(f"🔧 Calibrage {platform_name} appliqué à l'interface")
                    
                    self.logger.info(f"Profil OCR {platform_name} appliqué automatiquement")
                    
                else:
                    print(f"⚠️ Aucun preset OCR trouvé pour {platform_name}")
            else:
                print("⚠️ Presets OCR non disponibles")
                
        except Exception as e:
            self.logger.error(f"Erreur application profil OCR automatique: {e}")
            print(f"❌ Échec auto-calibrage: {e}")
    
    def _auto_start(self):
        """Démarrage automatique de l'analyse"""
        if self.running or not self.auto_mode:
            return
        
        self.running = True
        self.logger.info("Démarrage automatique du système d'analyse")
        
        # Démarrage des threads d'analyse
        self.ocr_thread = threading.Thread(target=self._ocr_loop, daemon=True)
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        
        self.ocr_thread.start()
        self.analysis_thread.start()
        
        platform = self.platform_detector.get_primary_platform()
        self._notify_status_change('active', {'platform': platform})
    
    def _auto_stop(self):
        """Arrêt automatique de l'analyse"""
        if not self.running:
            return
        
        self.running = False
        self.logger.info("Arrêt automatique - Aucune plateforme détectée")
        self._notify_status_change('waiting')
    
    def get_system_status(self):
        """Retourne l'état actuel du système"""
        platforms = self.platform_detector.get_detected_platforms()
        return {
            'status': self.current_status,
            'running': self.running,
            'auto_mode': self.auto_mode,
            'platforms': platforms,
            'primary_platform': self.platform_detector.get_primary_platform()
        }

    def get_display_data(self) -> Dict[str, Any]:
        """Retourne les données pour l'affichage GUI avec joueurs complets"""
        try:
            # Récupération de l'état actuel du jeu
            current_state = self.get_current_state()
            recommendation = self.get_recommendation()
            statistics = self.get_statistics()
            
            # Récupération des données joueurs depuis l'OCR  
            ocr_data = self.screen_capture.capture_and_analyze() if hasattr(self.screen_capture, 'capture_and_analyze') else {}
            players_at_table = ocr_data.get('players_at_table', []) if ocr_data else []
            
            return {
                'hero_cards': list(current_state.hero_cards) if current_state.hero_cards else [],
                'board_cards': current_state.board_cards,
                'pot': current_state.pot_size,
                'hero_stack': current_state.hero_stack,
                'small_blind': current_state.small_blind,
                'big_blind': current_state.big_blind,
                'antes': getattr(current_state, 'ante', 0.0),
                'table_type': current_state.table_type,
                'hero_position': current_state.hero_position,
                'recommendation': recommendation,
                'statistics': statistics,
                'active_players': getattr(current_state, 'active_players', 8),
                'total_players': getattr(current_state, 'total_players', 9),
                'players_info': players_at_table  # Liste complète des joueurs avec positions
            }
            
        except Exception as e:
            self.logger.error(f"Erreur récupération données affichage: {e}")
            return {}