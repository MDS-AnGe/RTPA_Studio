"""
Détecteur automatique de plateformes poker
Surveille les processus et fenêtres pour démarrage automatique
"""

import psutil
import time
import threading
from typing import List, Dict, Optional, Callable, Any
try:
    from ..utils.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

class PlatformDetector:
    """Détecteur automatique des plateformes poker"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Plateformes supportées avec leurs processus
        self.supported_platforms = {
            'pokerstars': {
                'processes': ['PokerStars.exe', 'pokerstars'],
                'window_titles': ['PokerStars', 'Poker Stars'],
                'name': 'PokerStars'
            },
            'winamax': {
                'processes': ['Winamax.exe', 'winamax', 'WinamaxPoker.exe'],
                'window_titles': ['Winamax Poker', 'Winamax - ', 'Winamax', 'Table', 'NL', 'PL', 'FL', 'SNG', 'MTT'],
                'name': 'Winamax'
            },
            'pmu': {
                'processes': ['PMUPoker.exe', 'pmu-poker'],
                'window_titles': ['PMU Poker', 'PMU.fr'],
                'name': 'PMU Poker'
            },
            'partypoker': {
                'processes': ['PartyPoker.exe', 'partypoker'],
                'window_titles': ['PartyPoker', 'Party Poker'],
                'name': 'PartyPoker'
            }
        }
        
        self.detected_platforms = set()
        self.is_monitoring = False
        self.monitor_thread = None
        self.status_callback = None
        self.detection_interval = 2.0  # Vérification toutes les 2 secondes
        
        self.logger.info("PlatformDetector initialisé")
    
    def set_status_callback(self, callback: Callable[[str, str], None]):
        """Définit le callback pour les changements d'état"""
        self.status_callback = callback
    
    def start_monitoring(self):
        """Démarre la surveillance automatique"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Surveillance automatique des plateformes démarrée")
    
    def stop_monitoring(self):
        """Arrête la surveillance"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        self.logger.info("Surveillance automatique arrêtée")
    
    def _monitor_loop(self):
        """Boucle de surveillance continue"""
        while self.is_monitoring:
            try:
                current_platforms = self._detect_active_platforms()
                
                # Détecter les nouvelles plateformes
                new_platforms = current_platforms - self.detected_platforms
                for platform in new_platforms:
                    self.logger.info(f"Plateforme détectée: {self.supported_platforms[platform]['name']}")
                    if self.status_callback:
                        self.status_callback('platform_detected', platform)
                
                # Détecter les plateformes fermées
                closed_platforms = self.detected_platforms - current_platforms
                for platform in closed_platforms:
                    self.logger.info(f"Plateforme fermée: {self.supported_platforms[platform]['name']}")
                    if self.status_callback:
                        self.status_callback('platform_closed', platform)
                
                self.detected_platforms = current_platforms
                
                # Notifier l'état global
                if current_platforms:
                    if self.status_callback:
                        self.status_callback('status', 'active')
                else:
                    if self.status_callback:
                        self.status_callback('status', 'waiting')
                
            except Exception as e:
                self.logger.error(f"Erreur surveillance plateformes: {e}")
            
            time.sleep(self.detection_interval)
    
    def get_detection_info(self) -> dict:
        """Récupère des informations détaillées pour debug"""
        platforms = self._detect_active_platforms()
        result = {
            'detected_platforms': list(platforms),
            'all_processes': [],
            'matching_processes': [],
            'all_windows': [],
            'matching_windows': []
        }
        
        try:
            # Analyse des processus
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name:
                        result['all_processes'].append(proc_name)
                        
                        # Vérifier si correspond à une plateforme
                        for platform_id, platform_info in self.supported_platforms.items():
                            for process_pattern in platform_info['processes']:
                                pattern_base = process_pattern.lower().replace('.exe', '')
                                if (proc_name.lower() == process_pattern.lower() or
                                    proc_name.lower() == pattern_base or
                                    proc_name.lower().startswith(pattern_base) or
                                    'winamax' in proc_name.lower() or
                                    pattern_base in proc_name.lower()):
                                    result['matching_processes'].append((proc_name, platform_id, pattern_base))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Analyse des fenêtres (si disponible)
            try:
                import importlib.util
                spec = importlib.util.find_spec('pygetwindow')
                if spec is not None:
                    gw = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(gw)
                    windows = gw.getAllTitles()
                    
                    for window_title in windows:
                        if window_title.strip():  # Ignorer les titres vides
                            result['all_windows'].append(window_title)
                            
                            # Vérifier correspondance Winamax
                            if ('winamax' in window_title.lower() or
                                any(keyword in window_title.lower() for keyword in ['table', 'nl', 'pl', 'fl', 'sng', 'mtt'])):
                                result['matching_windows'].append((window_title, 'winamax'))
                                
            except (ImportError, ModuleNotFoundError, AttributeError):
                result['all_windows'] = ['pygetwindow non disponible']
            except Exception as e:
                result['all_windows'] = [f'Erreur fenêtres: {e}']
                
        except Exception as e:
            self.logger.error(f"Erreur get_detection_info: {e}")
        
        return result
    
    def _detect_active_platforms(self) -> set:
        """Détecte les plateformes actuellement actives"""
        active_platforms = set()
        
        try:
            # Vérification par processus
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name:
                        for platform_id, platform_info in self.supported_platforms.items():
                            # Vérification améliorée des noms de processus
                            for process_pattern in platform_info['processes']:
                                pattern_base = process_pattern.lower().replace('.exe', '')
                                if (proc_name.lower() == process_pattern.lower() or
                                    proc_name.lower() == pattern_base or
                                    proc_name.lower().startswith(pattern_base) or
                                    pattern_base in proc_name.lower()):
                                    active_platforms.add(platform_id)
                                    break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Vérification supplémentaire par fenêtres (si disponible)
            try:
                import importlib.util
                spec = importlib.util.find_spec('pygetwindow')
                if spec is not None:
                    # Tentative d'import dynamique
                    gw = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(gw)
                    windows = gw.getAllTitles()
                    
                    for window_title in windows:
                        for platform_id, platform_info in self.supported_platforms.items():
                            # Logique spéciale pour Winamax (détection plus inclusive)
                            if platform_id == 'winamax':
                                # Détecter Winamax dans le titre de fenêtre (lobby ou table)
                                if ('winamax' in window_title.lower() or
                                    (any(keyword in window_title.lower() 
                                         for keyword in ['table', 'nl', 'pl', 'fl', 'sng', 'mtt']) and 
                                     len([w for w in windows if 'winamax' in w.lower()]) > 0)):
                                    active_platforms.add(platform_id)
                                    break
                            else:
                                # Logique normale pour les autres plateformes
                                if any(title.lower() in window_title.lower() 
                                      for title in platform_info['window_titles']):
                                    active_platforms.add(platform_id)
                                    break
                            
            except (ImportError, ModuleNotFoundError, AttributeError):
                # pygetwindow non disponible, utiliser seulement les processus
                pass
            except Exception as e:
                pass
        
        except Exception as e:
            self.logger.error(f"Erreur détection plateformes: {e}")
        
        return active_platforms
    
    def get_detected_platforms(self) -> List[Dict[str, str]]:
        """Retourne la liste des plateformes détectées"""
        return [
            {
                'id': platform_id,
                'name': self.supported_platforms[platform_id]['name']
            }
            for platform_id in self.detected_platforms
        ]
    
    def is_any_platform_active(self) -> bool:
        """Vérifie si au moins une plateforme est active"""
        return len(self.detected_platforms) > 0
    
    def get_primary_platform(self) -> Optional[str]:
        """Retourne la plateforme principale détectée"""
        if not self.detected_platforms:
            return None
        
        # Ordre de priorité
        priority_order = ['pokerstars', 'winamax', 'pmu', 'partypoker']
        for platform in priority_order:
            if platform in self.detected_platforms:
                return platform
        
        # Retourner le premier disponible
        return next(iter(self.detected_platforms))
    
    def force_detection(self) -> Dict[str, Any]:
        """Force une détection immédiate (pour tests)"""
        platforms = self._detect_active_platforms()
        return {
            'active_platforms': list(platforms),
            'platform_names': [self.supported_platforms[p]['name'] for p in platforms],
            'count': len(platforms)
        }
    
    def simulate_winamax_detection(self):
        """Simule la détection de Winamax pour tests"""
        self.detected_platforms.add('winamax')
        if self.status_callback:
            self.status_callback('platform_detected', 'winamax')
        self.logger.info("Simulation détection Winamax activée")