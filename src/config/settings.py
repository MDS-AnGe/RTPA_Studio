"""
Gestion des paramètres de RTPA Studio
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field

from ..utils.logger import get_logger

@dataclass
class Settings:
    """Paramètres de configuration de RTPA Studio"""
    
    # Paramètres généraux
    language: str = "fr"  # fr ou en
    risk_percentage: float = 50.0  # Pourcentage de risque par défaut
    manual_risk_override: bool = False
    
    # Paramètres OCR
    ocr_enabled: bool = True
    ocr_interval_ms: int = 100
    ocr_confidence_threshold: float = 0.8
    screen_region: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "width": 1920, "height": 1080})
    
    # Paramètres CFR/Nash
    cfr_iterations: int = 1000
    cfr_sampling_enabled: bool = True
    nash_calculation_interval_ms: int = 50
    abstraction_buckets: int = 64
    
    # Paramètres de performance
    cpu_usage_limit: float = 80.0  # Pourcentage max CPU
    ram_usage_limit: float = 70.0  # Pourcentage max RAM
    gpu_enabled: bool = True
    gpu_memory_limit: float = 80.0  # Pourcentage max GPU
    auto_resource_management: bool = True
    
    # Paramètres de jeu
    default_table_type: str = "cashgame"  # cashgame ou tournament
    max_players: int = 9
    target_hands_per_100: int = 65  # Objectif de mains gagnées
    auto_hand_target: bool = True
    
    # Paramètres d'affichage
    show_probabilities: bool = True
    show_recommendations: bool = True
    show_statistics: bool = True
    theme: str = "dark"  # dark ou light
    
    # Fichier de configuration
    config_file: Path = field(default_factory=lambda: Path("config/settings.yaml"))
    
    def __post_init__(self):
        self.logger = get_logger(__name__)
        self.load_from_file()
    
    def load_from_file(self):
        """Charge les paramètres depuis le fichier YAML"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                if config_data:
                    for key, value in config_data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
                
                self.logger.info(f"Paramètres chargés depuis {self.config_file}")
            else:
                self.logger.info("Fichier de configuration non trouvé, utilisation des valeurs par défaut")
                self.save_to_file()  # Créer le fichier avec les valeurs par défaut
                
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des paramètres: {e}")
    
    def save_to_file(self):
        """Sauvegarde les paramètres dans le fichier YAML"""
        try:
            # Créer le dossier config s'il n'existe pas
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convertir en dictionnaire
            config_data = {}
            for key, value in self.__dict__.items():
                if not key.startswith('_') and key not in ['logger', 'config_file']:
                    config_data[key] = value
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"Paramètres sauvegardés dans {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des paramètres: {e}")
    
    def update(self, new_settings: Dict[str, Any]):
        """Met à jour les paramètres"""
        updated = False
        for key, value in new_settings.items():
            if hasattr(self, key):
                setattr(self, key, value)
                updated = True
                self.logger.info(f"Paramètre mis à jour: {key} = {value}")
        
        if updated:
            self.save_to_file()
    
    def reset_to_defaults(self):
        """Remet les paramètres aux valeurs par défaut"""
        default_settings = Settings()
        for key, value in default_settings.__dict__.items():
            if not key.startswith('_') and key not in ['logger', 'config_file']:
                setattr(self, key, value)
        
        self.save_to_file()
        self.logger.info("Paramètres remis aux valeurs par défaut")
    
    def get_display_settings(self) -> Dict[str, Any]:
        """Retourne les paramètres d'affichage"""
        return {
            'language': self.language,
            'theme': self.theme,
            'show_probabilities': self.show_probabilities,
            'show_recommendations': self.show_recommendations,
            'show_statistics': self.show_statistics
        }
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """Retourne les paramètres de performance"""
        return {
            'cpu_usage_limit': self.cpu_usage_limit,
            'ram_usage_limit': self.ram_usage_limit,
            'gpu_enabled': self.gpu_enabled,
            'gpu_memory_limit': self.gpu_memory_limit,
            'auto_resource_management': self.auto_resource_management
        }