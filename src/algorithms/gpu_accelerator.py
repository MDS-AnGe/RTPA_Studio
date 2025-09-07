"""
Accélérateur GPU/CPU pour optimisations CFR et Nash
Module dédié pour l'accélération des calculs poker
"""

import logging
import numpy as np
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import multiprocessing as mp

# GPU/CPU Acceleration imports
try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

from numba import jit, prange

@dataclass
class AccelerationConfig:
    """Configuration pour l'accélération GPU/CPU"""
    gpu_enabled: bool = False
    gpu_memory_limit: float = 0.8
    cpu_threads: int = mp.cpu_count()
    use_mixed_precision: bool = True
    batch_size: int = 1000

class GPUAccelerator:
    """Gestionnaire d'accélération GPU/CPU pour calculs CFR"""
    
    def __init__(self, config: AccelerationConfig = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or AccelerationConfig()
        
        # Configuration du device
        self.device = self._setup_device()
        self.memory_pool = {}
        self.tensor_cache = {}
        
        # Statistiques de performance
        self.performance_stats = {
            "total_calculations": 0,
            "gpu_calculations": 0,
            "cpu_calculations": 0,
            "cache_hits": 0,
            "total_time": 0.0
        }
        
        self.logger.info(f"GPUAccelerator initialisé: {self.device}")
    
    def _setup_device(self):
        """Configure le device optimal"""
        if not TORCH_AVAILABLE:
            return "cpu"
        
        if self.config.gpu_enabled and torch.cuda.is_available():
            device = torch.device("cuda:0")
            # Configuration mémoire GPU
            torch.cuda.set_per_process_memory_fraction(self.config.gpu_memory_limit)
            # Configuration threads CPU
            torch.set_num_threads(self.config.cpu_threads)
            torch.set_num_interop_threads(max(1, self.config.cpu_threads // 2))
            
            self.logger.info(f"GPU activé: {torch.cuda.get_device_name(0)}")
            return device
        else:
            device = torch.device("cpu")
            if TORCH_AVAILABLE:
                torch.set_num_threads(self.config.cpu_threads)
            self.logger.info(f"CPU threads: {self.config.cpu_threads}")
            return device
    
    def update_config(self, gpu_enabled: bool, memory_limit: float):
        """Met à jour la configuration GPU"""
        self.config.gpu_enabled = gpu_enabled
        self.config.gpu_memory_limit = memory_limit
        
        # Reconfigurer le device
        old_device = self.device
        self.device = self._setup_device()
        
        if old_device != self.device:
            self.clear_cache()
            self.logger.info(f"Device changé: {old_device} → {self.device}")
    
    def clear_cache(self):
        """Vide tous les caches"""
        self.tensor_cache.clear()
        self.memory_pool.clear()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def get_memory_info(self):
        """Retourne les informations mémoire"""
        if self.device.type == "cuda" and torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**2
            cached = torch.cuda.memory_reserved() / 1024**2
            total = torch.cuda.get_device_properties(0).total_memory / 1024**2
            
            return {
                "type": "gpu",
                "allocated": allocated,
                "cached": cached,
                "total": total,
                "percent": (allocated / total) * 100,
                "available": total - allocated
            }
        else:
            import psutil
            memory = psutil.virtual_memory()
            return {
                "type": "cpu",
                "allocated": (memory.total - memory.available) / 1024**2,
                "total": memory.total / 1024**2,
                "percent": memory.percent,
                "available": memory.available / 1024**2
            }
    
    def compute_equity_fast(self, hand_strengths, opponent_ranges):
        """Calcul rapide d'equity avec Numba"""
        return _compute_equity_numba(hand_strengths, opponent_ranges)

@jit(nopython=True)
def _compute_equity_numba(hand_strengths, opponent_ranges):
    """Fonction Numba compilée pour calcul d'equity"""
    equity = 0.0
    total_combos = 0.0
    
    for i in prange(len(opponent_ranges)):
        if opponent_ranges[i] > 0:
            wins = np.sum(hand_strengths > hand_strengths[i])
            ties = np.sum(hand_strengths == hand_strengths[i])
            equity += opponent_ranges[i] * (wins + 0.5 * ties)
            total_combos += opponent_ranges[i]
    
    return equity / total_combos if total_combos > 0 else 0.0
    
    def compute_regrets_batch(self, utilities_batch, strategies_batch):
        """Calcul optimisé des regrets par lots"""
        start_time = time.time()
        
        if not TORCH_AVAILABLE or utilities_batch.shape[0] < 100:
            # Utiliser NumPy pour petits calculs
            result = self._compute_regrets_numpy(utilities_batch, strategies_batch)
            self.performance_stats["cpu_calculations"] += 1
        else:
            # Utiliser PyTorch pour gros calculs
            result = self._compute_regrets_torch(utilities_batch, strategies_batch)
            self.performance_stats["gpu_calculations"] += 1
        
        calc_time = time.time() - start_time
        self.performance_stats["total_time"] += calc_time
        self.performance_stats["total_calculations"] += 1
        
        return result
    
    def _compute_regrets_numpy(self, utilities, strategies):
        """Calcul regrets avec NumPy"""
        batch_size, num_actions = utilities.shape
        regrets = np.zeros_like(utilities)
        
        for i in range(batch_size):
            ev = np.sum(utilities[i] * strategies[i])
            regrets[i] = utilities[i] - ev
        
        return regrets
    
    def _compute_regrets_torch(self, utilities, strategies):
        """Calcul regrets avec PyTorch"""
        # Convertir en tenseurs
        utilities_tensor = torch.tensor(utilities, device=self.device, dtype=torch.float32)
        strategies_tensor = torch.tensor(strategies, device=self.device, dtype=torch.float32)
        
        # Calcul vectorisé
        ev = torch.sum(utilities_tensor * strategies_tensor, dim=1, keepdim=True)
        regrets = utilities_tensor - ev
        
        return regrets.cpu().numpy()
    
    def compute_nash_equilibrium(self, payoff_matrix, max_iterations=1000):
        """Calcul équilibre de Nash optimisé"""
        if not TORCH_AVAILABLE:
            return self._compute_nash_numpy(payoff_matrix, max_iterations)
        
        return self._compute_nash_torch(payoff_matrix, max_iterations)
    
    def _compute_nash_torch(self, payoff_matrix, max_iterations):
        """Calcul Nash avec PyTorch"""
        n_actions = payoff_matrix.shape[0]
        
        # Initialiser stratégie uniforme
        strategy = torch.ones(n_actions, device=self.device) / n_actions
        
        for iteration in range(max_iterations):
            # Calcul des utilités esperées
            expected_utilities = torch.matmul(payoff_matrix, strategy)
            
            # Mise à jour de la stratégie (fictitious play)
            best_response = torch.zeros_like(strategy)
            best_action = torch.argmax(expected_utilities)
            best_response[best_action] = 1.0
            
            # Moyenne pondérée
            alpha = 1.0 / (iteration + 1)
            strategy = (1 - alpha) * strategy + alpha * best_response
            
            # Test de convergence
            if iteration % 100 == 0:
                exploitability = torch.max(expected_utilities) - torch.sum(strategy * expected_utilities)
                if exploitability < 1e-6:
                    break
        
        return strategy.cpu().numpy()
    
    def _compute_nash_numpy(self, payoff_matrix, max_iterations):
        """Calcul Nash avec NumPy"""
        n_actions = payoff_matrix.shape[0]
        strategy = np.ones(n_actions) / n_actions
        
        for iteration in range(max_iterations):
            expected_utilities = np.dot(payoff_matrix, strategy)
            
            best_response = np.zeros(n_actions)
            best_action = np.argmax(expected_utilities)
            best_response[best_action] = 1.0
            
            alpha = 1.0 / (iteration + 1)
            strategy = (1 - alpha) * strategy + alpha * best_response
            
            if iteration % 100 == 0:
                exploitability = np.max(expected_utilities) - np.sum(strategy * expected_utilities)
                if exploitability < 1e-6:
                    break
        
        return strategy
    
    def optimize_hand_generation(self, num_hands, hand_types):
        """Génération optimisée de mains"""
        if TORCH_AVAILABLE and num_hands > 1000:
            return self._generate_hands_torch(num_hands, hand_types)
        else:
            return self._generate_hands_numpy(num_hands, hand_types)
    
    def _generate_hands_torch(self, num_hands, hand_types):
        """Génération de mains avec PyTorch"""
        # Génération vectorisée rapide
        cards = torch.randint(0, 52, (num_hands, 2), device=self.device)
        
        # Éviter les doublons (même carte 2 fois)
        mask = cards[:, 0] != cards[:, 1]
        valid_hands = cards[mask]
        
        # Regénérer si nécessaire
        while len(valid_hands) < num_hands:
            additional = torch.randint(0, 52, (num_hands - len(valid_hands), 2), device=self.device)
            mask = additional[:, 0] != additional[:, 1]
            valid_hands = torch.cat([valid_hands, additional[mask]])
        
        return valid_hands[:num_hands].cpu().numpy()
    
    def _generate_hands_numpy(self, num_hands, hand_types):
        """Génération de mains avec NumPy"""
        hands = []
        for _ in range(num_hands):
            hand = np.random.choice(52, 2, replace=False)
            hands.append(hand)
        return np.array(hands)
    
    def get_performance_stats(self):
        """Retourne les statistiques de performance"""
        total_calcs = self.performance_stats["total_calculations"]
        if total_calcs == 0:
            return self.performance_stats
        
        stats = self.performance_stats.copy()
        stats["gpu_percent"] = (stats["gpu_calculations"] / total_calcs) * 100
        stats["cpu_percent"] = (stats["cpu_calculations"] / total_calcs) * 100
        stats["avg_time"] = stats["total_time"] / total_calcs
        stats["cache_hit_rate"] = (stats["cache_hits"] / total_calcs) * 100
        
        return stats
    
    def benchmark(self):
        """Benchmark des performances GPU vs CPU"""
        results = {}
        
        # Test matrices de différentes tailles
        sizes = [100, 1000, 5000, 10000]
        
        for size in sizes:
            utilities = np.random.randn(size, 8).astype(np.float32)
            strategies = np.random.rand(size, 8).astype(np.float32)
            strategies = strategies / strategies.sum(axis=1, keepdims=True)
            
            # Test CPU
            start = time.time()
            self._compute_regrets_numpy(utilities, strategies)
            cpu_time = time.time() - start
            
            # Test GPU si disponible
            gpu_time = None
            if TORCH_AVAILABLE and self.device.type == "cuda":
                start = time.time()
                self._compute_regrets_torch(utilities, strategies)
                torch.cuda.synchronize()  # Attendre la fin des calculs GPU
                gpu_time = time.time() - start
            
            results[size] = {
                "cpu_time": cpu_time,
                "gpu_time": gpu_time,
                "speedup": cpu_time / gpu_time if gpu_time else None
            }
        
        return results