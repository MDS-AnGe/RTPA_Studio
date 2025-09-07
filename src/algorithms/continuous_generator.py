"""
Générateur continu de mains poker pour amélioration CFR temps réel
Tourne en arrière-plan sans ralentir le logiciel principal
"""

import time
import threading
import queue
from typing import Optional, Callable, List
from dataclasses import dataclass
import random

from .hand_generator import HandGenerator, GenerationSettings
from .hand_parser import ParsedHand
from ..utils.logger import get_logger

@dataclass
class ContinuousSettings:
    """Configuration du générateur continu"""
    batch_size: int = 50  # Petits batches pour éviter latence
    generation_interval: float = 0.1  # 100ms entre générations
    max_queue_size: int = 1000  # File d'attente limitée
    cpu_usage_limit: float = 0.15  # Max 15% CPU
    priority_scenarios: Optional[List[str]] = None  # Scénarios prioritaires
    
    def __post_init__(self):
        if self.priority_scenarios is None:
            self.priority_scenarios = [
                'heads_up',
                'tournament_bubble', 
                'deep_stacks',
                'short_stacks',
                'multiway_pots'
            ]

class ContinuousHandGenerator:
    """Générateur de mains en continu optimisé pour performance"""
    
    def __init__(self, settings: Optional[ContinuousSettings] = None):
        self.logger = get_logger(__name__)
        self.settings = settings or ContinuousSettings()
        
        # Composants
        self.hand_generator = HandGenerator()
        self.generation_queue = queue.Queue(maxsize=self.settings.max_queue_size)
        
        # État du générateur
        self.running = False
        self.generation_thread = None
        self.processing_thread = None
        self.paused = False
        self.user_stopped = False  # Arrêt manuel par utilisateur
        
        # Statistiques
        self.hands_generated = 0
        self.hands_integrated = 0
        self.generation_rate = 0.0  # mains/seconde
        self.cpu_usage = 0.0
        
        # Callbacks
        self.integration_callback: Optional[Callable] = None
        self.stats_callback: Optional[Callable] = None
        
        # Optimisations performance
        self.last_cpu_check = time.time()
        self.adaptive_interval = self.settings.generation_interval
        
        self.logger.info("Générateur continu initialisé")
    
    def set_integration_callback(self, callback: Callable):
        """Définit le callback pour intégrer les mains dans CFR"""
        self.integration_callback = callback
    
    def set_stats_callback(self, callback: Callable):
        """Définit le callback pour les statistiques temps réel"""
        self.stats_callback = callback
    
    def start(self):
        """Démarre la génération continue"""
        if self.running:
            return
        
        self.running = True
        self.paused = False
        
        # Thread de génération (priorité basse)
        self.generation_thread = threading.Thread(
            target=self._generation_loop,
            daemon=True,
            name="ContinuousGenerator"
        )
        
        # Thread de traitement/intégration
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True,
            name="HandProcessor"
        )
        
        self.generation_thread.start()
        self.processing_thread.start()
        
        self.logger.info("Génération continue démarrée")
    
    def stop(self, user_initiated: bool = False):
        """Arrête la génération continue"""
        self.running = False
        self.user_stopped = user_initiated
        
        if self.generation_thread:
            self.generation_thread.join(timeout=1.0)
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
        
        stop_reason = "par l'utilisateur" if user_initiated else "automatiquement"
        self.logger.info(f"Génération continue arrêtée {stop_reason}")
    
    def is_user_stopped(self) -> bool:
        """Vérifie si l'arrêt a été initié par l'utilisateur"""
        return self.user_stopped
    
    def set_resource_limits(self, cpu_limit: Optional[float] = None, memory_limit_mb: Optional[float] = None, 
                           generation_rate: Optional[float] = None):
        """Configure les limites de ressources avec feedback utilisateur"""
        if cpu_limit is not None:
            old_limit = self.settings.cpu_usage_limit
            self.settings.cpu_usage_limit = min(1.0, max(0.01, cpu_limit))
            self.logger.info(f"Limite CPU mise à jour: {cpu_limit*100:.1f}%")
            print(f"🎛️ CPU limite: {old_limit*100:.1f}% → {self.settings.cpu_usage_limit*100:.1f}% (active dans la génération continue)")
        
        if memory_limit_mb is not None:
            # Ajustement de la taille de queue selon mémoire disponible
            old_queue = self.settings.max_queue_size
            max_hands_in_queue = int(memory_limit_mb * 2)  # ~2 mains par MB
            self.settings.max_queue_size = min(2000, max(100, max_hands_in_queue))
            self.logger.info(f"Limite mémoire mise à jour: {memory_limit_mb:.0f}MB")
            print(f"🎛️ RAM limite: {old_queue} → {self.settings.max_queue_size} mains en queue ({memory_limit_mb:.0f}MB)")
        
        if generation_rate is not None:
            old_interval = self.settings.generation_interval
            self.settings.generation_interval = max(0.05, 1.0 / generation_rate)
            self.logger.info(f"Taux génération mis à jour: {generation_rate:.1f} mains/s")
            old_rate = 1.0 / old_interval if old_interval > 0 else 0
            new_rate = 1.0 / self.settings.generation_interval
            print(f"🎛️ Vitesse génération: {old_rate:.1f} → {new_rate:.1f} mains/seconde")
        
        # Afficher le résumé des paramètres actuels
        self._print_current_settings()
    
    def pause(self):
        """Met en pause la génération"""
        self.paused = True
        self.logger.info("Génération continue en pause")
    
    def resume(self):
        """Reprend la génération"""
        self.paused = False
        self.logger.info("Génération continue reprise")
    
    def _generation_loop(self):
        """Boucle principale de génération"""
        start_time = time.time()
        batch_count = 0
        
        while self.running:
            try:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # Vérification charge CPU
                if self._should_throttle():
                    time.sleep(self.adaptive_interval * 2)
                    continue
                
                # Génération d'un petit batch
                batch = self._generate_optimized_batch()
                
                if batch:
                    # Ajout à la queue (non-bloquant)
                    try:
                        self.generation_queue.put(batch, block=False)
                        self.hands_generated += len(batch)
                        batch_count += 1
                        
                        # Calcul du taux de génération
                        if batch_count % 10 == 0:
                            elapsed = time.time() - start_time
                            self.generation_rate = self.hands_generated / elapsed
                    
                    except queue.Full:
                        # Queue pleine, on attend
                        time.sleep(self.adaptive_interval * 3)
                
                # Attente adaptative
                time.sleep(self.adaptive_interval)
                
            except Exception as e:
                self.logger.error(f"Erreur génération continue: {e}")
                time.sleep(1.0)
    
    def _processing_loop(self):
        """Boucle de traitement et intégration"""
        while self.running:
            try:
                # Récupération d'un batch
                batch = self.generation_queue.get(timeout=1.0)
                
                if batch and self.integration_callback:
                    # Intégration immédiate dans CFR
                    self.integration_callback(batch)
                    self.hands_integrated += len(batch)
                    
                    # Mise à jour statistiques
                    if self.stats_callback:
                        stats = self.get_statistics()
                        self.stats_callback(stats)
                
                self.generation_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Erreur traitement: {e}")
                time.sleep(0.5)
    
    def _generate_optimized_batch(self) -> List[ParsedHand]:
        """Génère un batch optimisé selon les priorités"""
        try:
            # Sélection scenario prioritaire
            if self.settings.priority_scenarios:
                scenario = random.choice(self.settings.priority_scenarios)
            else:
                # Scénario par défaut si pas de priorités
                default_scenarios = [
                    'heads_up', 'deep_stacks', 'short_stacks', 
                    'tournament_bubble', 'multiway_pots'
                ]
                scenario = random.choice(default_scenarios)
            
            # Configuration adaptée au scenario
            settings = self._get_scenario_settings(scenario)
            
            # Génération rapide
            temp_generator = HandGenerator(settings)
            batch = temp_generator.generate_batch(self.settings.batch_size)
            
            return batch
            
        except Exception as e:
            self.logger.error(f"Erreur génération batch: {e}")
            return []
    
    def _get_scenario_settings(self, scenario: str) -> GenerationSettings:
        """Retourne les paramètres optimisés pour un scénario"""
        base_settings = GenerationSettings()
        
        if scenario == 'heads_up':
            base_settings.stack_sizes = [1000.0, 1000.0]
            
        elif scenario == 'tournament_bubble':
            base_settings.stack_sizes = [200.0, 300.0, 150.0, 400.0, 100.0, 250.0]
            
        elif scenario == 'deep_stacks':
            base_settings.stack_sizes = [5000.0] * 6
            base_settings.blind_levels = [(25.0, 50.0)]
            
        elif scenario == 'short_stacks':
            base_settings.stack_sizes = [400.0] * 6
            base_settings.blind_levels = [(50.0, 100.0)]
            
        elif scenario == 'multiway_pots':
            # Configuration pour pots multiway
            base_settings.stack_sizes = [2500.0] * 9
        
        return base_settings
    
    def _should_throttle(self) -> bool:
        """Détermine si on doit ralentir pour économiser CPU"""
        current_time = time.time()
        
        # Vérification CPU périodique
        if current_time - self.last_cpu_check > 5.0:  # Chaque 5 secondes
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=0.1)
                self.cpu_usage = cpu_percent / 100.0
                
                # Adaptation de l'intervalle selon CPU
                if self.cpu_usage > self.settings.cpu_usage_limit:
                    self.adaptive_interval = min(1.0, self.adaptive_interval * 1.5)
                    return True
                else:
                    self.adaptive_interval = max(
                        self.settings.generation_interval,
                        self.adaptive_interval * 0.9
                    )
                
                self.last_cpu_check = current_time
                
            except ImportError:
                # Fallback si psutil non disponible
                pass
        
        return False
    
    def _print_current_settings(self):
        """Affiche un résumé des paramètres actuels"""
        print(f"📊 Paramètres génération CFR:")
        print(f"   • CPU limite: {self.settings.cpu_usage_limit*100:.1f}%")
        print(f"   • Queue mémoire: {self.settings.max_queue_size} mains max")
        print(f"   • Vitesse cible: {1.0/self.settings.generation_interval:.1f} mains/seconde")
        print(f"   • Intervalle adaptatif actuel: {self.adaptive_interval:.3f}s")
        print(f"   • Usage CPU actuel: {self.cpu_usage*100:.1f}%")
    
    def get_statistics(self) -> dict:
        """Retourne les statistiques de génération"""
        queue_size = self.generation_queue.qsize()
        
        return {
            'running': self.running,
            'paused': self.paused,
            'hands_generated': self.hands_generated,
            'hands_integrated': self.hands_integrated,
            'generation_rate': self.generation_rate,
            'queue_size': queue_size,
            'cpu_usage': self.cpu_usage,
            'adaptive_interval': self.adaptive_interval,
            'integration_pending': queue_size > 0
        }
    
    def boost_generation(self, scenario: Optional[str] = None, multiplier: float = 2.0):
        """Booste temporairement la génération pour un scénario"""
        if scenario and self.settings.priority_scenarios:
            # Focus sur un scénario spécifique
            original_scenarios = self.settings.priority_scenarios.copy()
            self.settings.priority_scenarios = [scenario] * 5
            
            # Restore après 10 secondes
            def restore():
                time.sleep(10.0)
                if self.settings.priority_scenarios:
                    self.settings.priority_scenarios = original_scenarios
            
            threading.Thread(target=restore, daemon=True).start()
        
        # Réduction temporaire de l'intervalle
        original_interval = self.adaptive_interval
        self.adaptive_interval = original_interval / multiplier
        
        def restore_interval():
            time.sleep(30.0)  # Boost pendant 30 secondes
            self.adaptive_interval = original_interval
        
        threading.Thread(target=restore_interval, daemon=True).start()
        
        self.logger.info(f"Boost génération activé: {scenario or 'général'} x{multiplier}")