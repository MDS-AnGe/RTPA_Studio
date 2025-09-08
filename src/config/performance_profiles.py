"""
Profils de performance pour RTPA Studio
Chaque profil ajuste automatiquement tous les paramètres pour optimiser l'expérience
"""

from dataclasses import dataclass
from typing import Dict, Any
import json
import os

@dataclass
class PerformanceProfile:
    """Configuration d'un profil de performance"""
    name: str
    description: str
    
    # Paramètres CFR
    auto_training_enabled: bool
    cfr_iterations: int
    cfr_batch_size: int
    cfr_discount_factor: float
    cfr_exploration_rate: float
    background_training: bool
    
    # Génération continue
    continuous_generation: bool
    generation_interval: float  # secondes
    generation_batch_size: int
    cpu_usage_limit: float  # pourcentage (0.0-1.0)
    
    # Interface et GUI
    gui_update_interval: float  # secondes
    show_detailed_stats: bool
    enable_real_time_charts: bool
    
    # GPU/CPU
    prefer_gpu: bool
    max_cpu_threads: int
    memory_optimization: bool
    
    # Démarrage
    delayed_start: bool  # Démarrer les calculs avec délai
    startup_delay: float  # secondes avant démarrage calculs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le profil en dictionnaire"""
        return {
            'name': self.name,
            'description': self.description,
            'auto_training_enabled': self.auto_training_enabled,
            'cfr_iterations': self.cfr_iterations,
            'cfr_batch_size': self.cfr_batch_size,
            'cfr_discount_factor': self.cfr_discount_factor,
            'cfr_exploration_rate': self.cfr_exploration_rate,
            'background_training': self.background_training,
            'continuous_generation': self.continuous_generation,
            'generation_interval': self.generation_interval,
            'generation_batch_size': self.generation_batch_size,
            'cpu_usage_limit': self.cpu_usage_limit,
            'gui_update_interval': self.gui_update_interval,
            'show_detailed_stats': self.show_detailed_stats,
            'enable_real_time_charts': self.enable_real_time_charts,
            'prefer_gpu': self.prefer_gpu,
            'max_cpu_threads': self.max_cpu_threads,
            'memory_optimization': self.memory_optimization,
            'delayed_start': self.delayed_start,
            'startup_delay': self.startup_delay
        }

class PerformanceProfileManager:
    """Gestionnaire des profils de performance"""
    
    def __init__(self):
        self.profiles = self._create_default_profiles()
        self.current_profile = "equilibre"
        self.config_file = "config/performance_profile.json"
        self.load_config()
    
    def _create_default_profiles(self) -> Dict[str, PerformanceProfile]:
        """Crée les profils par défaut"""
        
        # 🌱 Profil ÉCO - Performance minimale, consommation réduite
        eco = PerformanceProfile(
            name="Éco",
            description="💚 Démarrage rapide, consommation minimale - Idéal pour ordinateurs moins puissants",
            
            # CFR - Minimum
            auto_training_enabled=False,  # Pas d'auto-training
            cfr_iterations=1000,
            cfr_batch_size=100,
            cfr_discount_factor=0.90,
            cfr_exploration_rate=0.05,
            background_training=False,  # Pas de calculs en arrière-plan
            
            # Génération - Très limitée
            continuous_generation=False,  # Pas de génération continue
            generation_interval=2.0,  # 2 secondes
            generation_batch_size=10,
            cpu_usage_limit=0.05,  # 5% CPU max
            
            # Interface - Allégée
            gui_update_interval=1.0,  # 1 seconde
            show_detailed_stats=False,
            enable_real_time_charts=False,
            
            # Ressources - Limitées
            prefer_gpu=False,
            max_cpu_threads=2,
            memory_optimization=True,
            
            # Démarrage - Immédiat
            delayed_start=False,
            startup_delay=0.0
        )
        
        # ⚖️ Profil ÉQUILIBRÉ - Bon compromis performance/ressources
        equilibre = PerformanceProfile(
            name="Équilibré",
            description="⚖️ Bon équilibre performance/consommation - Recommandé pour la plupart des utilisateurs",
            
            # CFR - Modéré
            auto_training_enabled=True,
            cfr_iterations=5000,
            cfr_batch_size=500,
            cfr_discount_factor=0.95,
            cfr_exploration_rate=0.1,
            background_training=True,
            
            # Génération - Modérée
            continuous_generation=True,
            generation_interval=0.5,  # 500ms
            generation_batch_size=25,
            cpu_usage_limit=0.15,  # 15% CPU max
            
            # Interface - Standard
            gui_update_interval=0.5,  # 500ms
            show_detailed_stats=True,
            enable_real_time_charts=True,
            
            # Ressources - Équilibrées
            prefer_gpu=True,
            max_cpu_threads=4,
            memory_optimization=True,
            
            # Démarrage - Délai modéré
            delayed_start=True,
            startup_delay=3.0  # 3 secondes de délai
        )
        
        # 🚀 Profil PERFORMANCE - Maximum de calculs et précision
        performance = PerformanceProfile(
            name="Performance",
            description="🚀 Performance maximale - Pour ordinateurs puissants et analyse poussée",
            
            # CFR - Maximum
            auto_training_enabled=True,
            cfr_iterations=20000,
            cfr_batch_size=2000,
            cfr_discount_factor=0.98,
            cfr_exploration_rate=0.15,
            background_training=True,
            
            # Génération - Intensive
            continuous_generation=True,
            generation_interval=0.1,  # 100ms
            generation_batch_size=50,
            cpu_usage_limit=0.30,  # 30% CPU max
            
            # Interface - Temps réel
            gui_update_interval=0.2,  # 200ms
            show_detailed_stats=True,
            enable_real_time_charts=True,
            
            # Ressources - Maximum
            prefer_gpu=True,
            max_cpu_threads=8,
            memory_optimization=False,
            
            # Démarrage - Délai pour optimisation
            delayed_start=True,
            startup_delay=5.0  # 5 secondes pour initialisation complète
        )
        
        return {
            "eco": eco,
            "equilibre": equilibre,
            "performance": performance
        }
    
    def get_profile(self, profile_name: str) -> PerformanceProfile:
        """Récupère un profil par son nom"""
        return self.profiles.get(profile_name, self.profiles["equilibre"])
    
    def get_current_profile(self) -> PerformanceProfile:
        """Récupère le profil actuel"""
        return self.get_profile(self.current_profile)
    
    def set_current_profile(self, profile_name: str) -> bool:
        """Définit le profil actuel"""
        if profile_name in self.profiles:
            self.current_profile = profile_name
            self.save_config()
            return True
        return False
    
    def get_profile_names(self) -> list:
        """Retourne la liste des noms de profils"""
        return list(self.profiles.keys())
    
    def get_profile_descriptions(self) -> Dict[str, str]:
        """Retourne les descriptions des profils"""
        return {name: profile.description for name, profile in self.profiles.items()}
    
    def load_config(self):
        """Charge la configuration depuis le fichier"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_profile = data.get('current_profile', 'equilibre')
        except Exception:
            # Si erreur, garder les valeurs par défaut
            pass
    
    def save_config(self):
        """Sauvegarde la configuration dans le fichier"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'current_profile': self.current_profile
                }, f, indent=2, ensure_ascii=False)
        except Exception:
            # Si erreur de sauvegarde, continuer sans crash
            pass
    
    def apply_profile_to_settings(self, settings_instance):
        """Applique le profil actuel aux paramètres du logiciel"""
        profile = self.get_current_profile()
        
        # Application des paramètres CFR
        if hasattr(settings_instance, 'cfr_iterations'):
            settings_instance.cfr_iterations = profile.cfr_iterations
        if hasattr(settings_instance, 'cfr_discount_factor'):
            settings_instance.cfr_discount_factor = profile.cfr_discount_factor
        if hasattr(settings_instance, 'cfr_exploration_rate'):
            settings_instance.cfr_exploration_rate = profile.cfr_exploration_rate
        
        # Application des paramètres de génération
        if hasattr(settings_instance, 'generation_interval'):
            settings_instance.generation_interval = profile.generation_interval
        if hasattr(settings_instance, 'cpu_usage_limit'):
            settings_instance.cpu_usage_limit = profile.cpu_usage_limit
        
        # Application des paramètres GPU/CPU
        if hasattr(settings_instance, 'gpu_enabled'):
            settings_instance.gpu_enabled = profile.prefer_gpu
        if hasattr(settings_instance, 'cpu_threads'):
            settings_instance.cpu_threads = profile.max_cpu_threads

# Instance globale pour accès facile
performance_manager = PerformanceProfileManager()

def get_performance_manager() -> PerformanceProfileManager:
    """Retourne l'instance du gestionnaire de profils"""
    return performance_manager