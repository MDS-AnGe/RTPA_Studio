"""
Optimiseur système adaptatif pour RTPA Studio
Détection automatique et configuration des ressources CPU/GPU/RAM
"""

import psutil
import platform
import multiprocessing
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import os

try:
    from ..utils.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

@dataclass
class SystemCapabilities:
    """Capacités détectées du système"""
    cpu_cores: int
    cpu_threads: int
    cpu_frequency: float
    ram_total_gb: float
    ram_available_gb: float
    gpu_available: bool
    gpu_name: str
    gpu_memory_mb: int
    platform_os: str
    architecture: str
    
@dataclass
class ResourceLimits:
    """Limites d'utilisation des ressources"""
    cpu_percent: float
    ram_percent: float
    gpu_enabled: bool
    gpu_memory_percent: float
    max_threads: int
    priority_level: str

class SystemOptimizer:
    """Optimiseur système adaptatif"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.capabilities = self._detect_system_capabilities()
        self.current_profile = "equilibre"
        self.custom_limits = None
        
        # Profils prédéfinis
        self.performance_profiles = {
            "econome": ResourceLimits(
                cpu_percent=60.0,
                ram_percent=50.0,
                gpu_enabled=False,
                gpu_memory_percent=30.0,
                max_threads=max(2, self.capabilities.cpu_cores // 2),
                priority_level="below_normal"
            ),
            "equilibre": ResourceLimits(
                cpu_percent=80.0,
                ram_percent=70.0,
                gpu_enabled=self.capabilities.gpu_available,
                gpu_memory_percent=60.0,
                max_threads=max(4, self.capabilities.cpu_cores - 1),
                priority_level="normal"
            ),
            "performance_max": ResourceLimits(
                cpu_percent=95.0,
                ram_percent=85.0,
                gpu_enabled=self.capabilities.gpu_available,
                gpu_memory_percent=90.0,
                max_threads=self.capabilities.cpu_threads,
                priority_level="high"
            ),
            "custom": None  # Sera défini par l'utilisateur
        }
        
        self.logger.info(f"Optimiseur système initialisé - {self.capabilities.cpu_cores} cœurs, {self.capabilities.ram_total_gb:.1f}GB RAM, GPU: {self.capabilities.gpu_available}")
    
    def _detect_system_capabilities(self) -> SystemCapabilities:
        """Détecte automatiquement les capacités du système"""
        try:
            # CPU Info
            cpu_count = psutil.cpu_count(logical=False) or multiprocessing.cpu_count()
            cpu_threads = psutil.cpu_count(logical=True) or multiprocessing.cpu_count()
            
            try:
                cpu_freq = psutil.cpu_freq()
                max_freq = cpu_freq.max if cpu_freq and cpu_freq.max else 2400.0
            except:
                max_freq = 2400.0
            
            # RAM Info
            memory = psutil.virtual_memory()
            ram_total = memory.total / (1024**3)  # GB
            ram_available = memory.available / (1024**3)  # GB
            
            # GPU Info
            gpu_available = False
            gpu_name = "Aucun"
            gpu_memory = 0
            
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_available = True
                    gpu_name = torch.cuda.get_device_name(0)
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory // (1024**2)
            except:
                pass
            
            # OS Info
            os_name = platform.system()
            arch = platform.machine()
            
            return SystemCapabilities(
                cpu_cores=cpu_count,
                cpu_threads=cpu_threads,
                cpu_frequency=max_freq,
                ram_total_gb=ram_total,
                ram_available_gb=ram_available,
                gpu_available=gpu_available,
                gpu_name=gpu_name,
                gpu_memory_mb=gpu_memory,
                platform_os=os_name,
                architecture=arch
            )
            
        except Exception as e:
            self.logger.error(f"Erreur détection capacités système: {e}")
            # Valeurs par défaut conservatrices
            return SystemCapabilities(
                cpu_cores=4, cpu_threads=8, cpu_frequency=2400.0,
                ram_total_gb=8.0, ram_available_gb=4.0,
                gpu_available=False, gpu_name="Aucun", gpu_memory_mb=0,
                platform_os="Unknown", architecture="x64"
            )
    
    def get_recommended_profile(self) -> str:
        """Recommande un profil selon les capacités détectées"""
        caps = self.capabilities
        
        # Système très puissant
        if (caps.cpu_cores >= 8 and caps.ram_total_gb >= 16 and caps.gpu_available):
            return "performance_max"
        
        # Système correct
        elif (caps.cpu_cores >= 4 and caps.ram_total_gb >= 8):
            return "equilibre"
        
        # Système limité
        else:
            return "econome"
    
    def set_profile(self, profile_name: str) -> bool:
        """Définit le profil de performance"""
        if profile_name not in self.performance_profiles:
            self.logger.error(f"Profil inconnu: {profile_name}")
            return False
        
        if profile_name == "custom" and self.custom_limits is None:
            self.logger.error("Profil custom non défini")
            return False
        
        self.current_profile = profile_name
        self.logger.info(f"Profil de performance changé: {profile_name}")
        return True
    
    def get_current_limits(self) -> ResourceLimits:
        """Retourne les limites actuelles"""
        if self.current_profile == "custom" and self.custom_limits:
            return self.custom_limits
        return self.performance_profiles[self.current_profile]
    
    def set_custom_limits(self, cpu_percent: float, ram_percent: float, 
                         gpu_enabled: bool, gpu_memory_percent: float) -> bool:
        """Définit des limites personnalisées"""
        try:
            # Validation des valeurs
            cpu_percent = max(10.0, min(100.0, cpu_percent))
            ram_percent = max(10.0, min(95.0, ram_percent))
            gpu_memory_percent = max(10.0, min(95.0, gpu_memory_percent))
            
            # Calcul du nombre de threads optimal
            max_threads = max(1, int(self.capabilities.cpu_threads * (cpu_percent / 100.0)))
            
            self.custom_limits = ResourceLimits(
                cpu_percent=cpu_percent,
                ram_percent=ram_percent,
                gpu_enabled=gpu_enabled and self.capabilities.gpu_available,
                gpu_memory_percent=gpu_memory_percent,
                max_threads=max_threads,
                priority_level="normal"
            )
            
            self.logger.info(f"Limites personnalisées définies: CPU={cpu_percent}%, RAM={ram_percent}%, GPU={gpu_enabled}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur définition limites custom: {e}")
            return False
    
    def get_optimal_cfr_settings(self) -> Dict[str, Any]:
        """Retourne les paramètres CFR optimaux pour le système"""
        limits = self.get_current_limits()
        caps = self.capabilities
        
        # Calculs adaptatifs
        batch_size = min(10000, max(1000, int(caps.ram_available_gb * 1000)))
        iterations_target = min(100000, max(10000, int(caps.cpu_cores * 12500)))
        
        if limits.gpu_enabled:
            # Paramètres optimisés GPU
            settings = {
                'device': 'cuda',
                'batch_size': min(batch_size * 2, 50000),
                'max_iterations': iterations_target * 2,
                'memory_limit': limits.gpu_memory_percent / 100.0,
                'cpu_threads': limits.max_threads // 2,  # Réserver pour GPU
                'enable_mixed_precision': True
            }
        else:
            # Paramètres optimisés CPU
            settings = {
                'device': 'cpu',
                'batch_size': batch_size,
                'max_iterations': iterations_target,
                'cpu_threads': limits.max_threads,
                'enable_parallel_processing': True,
                'memory_limit': limits.ram_percent / 100.0
            }
        
        return settings
    
    def monitor_resource_usage(self) -> Dict[str, float]:
        """Surveille l'utilisation actuelle des ressources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            ram_percent = memory.percent
            
            gpu_usage = 0.0
            gpu_memory_percent = 0.0
            
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory_used = torch.cuda.memory_allocated(0)
                    gpu_memory_total = torch.cuda.get_device_properties(0).total_memory
                    gpu_memory_percent = (gpu_memory_used / gpu_memory_total) * 100
                    # GPU usage approximation via NVIDIA-ML si disponible
                    try:
                        import pynvml
                        pynvml.nvmlInit()
                        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                        gpu_usage = util.gpu
                    except:
                        gpu_usage = gpu_memory_percent  # Fallback
            except:
                pass
            
            return {
                'cpu_percent': cpu_percent,
                'ram_percent': ram_percent,
                'gpu_usage': gpu_usage,
                'gpu_memory_percent': gpu_memory_percent
            }
            
        except Exception as e:
            self.logger.error(f"Erreur monitoring ressources: {e}")
            return {'cpu_percent': 0, 'ram_percent': 0, 'gpu_usage': 0, 'gpu_memory_percent': 0}
    
    def auto_adjust_if_needed(self) -> bool:
        """Ajuste automatiquement si les ressources sont surchargées"""
        usage = self.monitor_resource_usage()
        limits = self.get_current_limits()
        adjusted = False
        
        # Réduction automatique si surcharge
        if usage['cpu_percent'] > 95 and limits.cpu_percent > 70:
            new_cpu = max(60, limits.cpu_percent - 10)
            self.set_custom_limits(new_cpu, limits.ram_percent, limits.gpu_enabled, limits.gpu_memory_percent)
            self.logger.info(f"Auto-ajustement CPU: {limits.cpu_percent}% → {new_cpu}%")
            adjusted = True
        
        if usage['ram_percent'] > 90 and limits.ram_percent > 60:
            new_ram = max(50, limits.ram_percent - 10)
            self.set_custom_limits(limits.cpu_percent, new_ram, limits.gpu_enabled, limits.gpu_memory_percent)
            self.logger.info(f"Auto-ajustement RAM: {limits.ram_percent}% → {new_ram}%")
            adjusted = True
        
        return adjusted
    
    def get_system_info_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des informations système"""
        caps = self.capabilities
        limits = self.get_current_limits()
        usage = self.monitor_resource_usage()
        
        return {
            'system': {
                'os': caps.platform_os,
                'cpu_cores': caps.cpu_cores,
                'cpu_threads': caps.cpu_threads,
                'ram_total_gb': caps.ram_total_gb,
                'gpu_available': caps.gpu_available,
                'gpu_name': caps.gpu_name
            },
            'current_profile': self.current_profile,
            'limits': {
                'cpu_percent': limits.cpu_percent,
                'ram_percent': limits.ram_percent,
                'gpu_enabled': limits.gpu_enabled,
                'max_threads': limits.max_threads
            },
            'usage': usage,
            'recommended_profile': self.get_recommended_profile()
        }
    
    def save_configuration(self, file_path: str = "config/system_optimization.json"):
        """Sauvegarde la configuration actuelle"""
        try:
            config = {
                'current_profile': self.current_profile,
                'custom_limits': self.custom_limits.__dict__ if self.custom_limits else None
            }
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Configuration sauvegardée: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde configuration: {e}")
            return False
    
    def load_configuration(self, file_path: str = "config/system_optimization.json"):
        """Charge une configuration sauvegardée"""
        try:
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            if 'current_profile' in config:
                self.current_profile = config['current_profile']
            
            if config.get('custom_limits'):
                limits_data = config['custom_limits']
                self.custom_limits = ResourceLimits(**limits_data)
            
            self.logger.info(f"Configuration chargée: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur chargement configuration: {e}")
            return False