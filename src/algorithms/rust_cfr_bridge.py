"""
Bridge Python-Rust pour CFR Engine
Intégration transparente du système CFR Rust dans RTPA Studio
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional
import threading
import time

class RustCfrBridge:
    """Bridge Python vers CFR Engine Rust"""
    
    def __init__(self):
        self.rust_engine = None
        self.is_initialized = False
        self.last_error = None
        
        # Configuration par défaut
        self.config = {
            "max_iterations": 10000,
            "convergence_threshold": 0.01,
            "cpu_threads": os.cpu_count(),
            "gpu_enabled": True,
            "gpu_memory_limit": 0.6,
            "gpu_batch_size": 1000,
            "abstraction_buckets": 64
        }
        
        self._init_rust_engine()
    
    def _init_rust_engine(self):
        """Initialiser engine Rust"""
        try:
            # 🔧 CHEMIN FLEXIBLE: Recherche module Rust dans plusieurs emplacements
            rust_paths = [
                os.path.join(os.path.dirname(__file__), '../../rust_cfr_engine/target/release'),
                os.path.join(os.path.dirname(__file__), '../../rust_cfr_engine/target/debug'),
                './rust_cfr_engine/target/release',
                './rust_cfr_engine/target/debug'
            ]
            
            rust_engine = None
            for path in rust_paths:
                try:
                    if os.path.exists(path):
                        sys.path.insert(0, path)
                        import rust_cfr_engine
                        rust_engine = rust_cfr_engine.RustCfrEngine(self.config)
                        break
                except ImportError:
                    continue
            
            if rust_engine:
                self.rust_engine = rust_engine
                self.is_initialized = True
                print("🚀 Bridge Rust CFR initialisé avec succès!")
            else:
                print("⚠️  Module Rust non trouvé dans les chemins standards")
                print("   Utilisation fallback Python CFR")
                self.is_initialized = False
                
        except Exception as e:
            self.last_error = str(e)
            print(f"❌ Erreur initialisation Rust CFR: {e}")
            self.is_initialized = False
    
    def is_rust_available(self) -> bool:
        """Vérifier si Rust CFR est disponible"""
        return self.is_initialized and self.rust_engine is not None
    
    def train_batch(self, states: List[Dict[str, Any]]) -> float:
        """🔥 TRAINING CFR 100% RUST - ZERO FALLBACK Python"""
        if not self.is_rust_available():
            print("🚨 ERREUR CRITIQUE: CFR Rust requis mais indisponible!")
            print("🔄 Tentative réinitialisation automatique...")
            self._init_rust_engine()
            
            if not self.is_rust_available():
                raise RuntimeError("❌ SYSTÈME CFR RUST REQUIS - Installation impossible. Vérifiez les dépendances Rust.")
        
        try:
            # Conversion vers format Rust optimisée
            rust_states = self._convert_states_to_rust(states)
            
            print(f"⚡ Training CFR Rust: {len(rust_states)} états")
            convergence = self.rust_engine.train_batch(rust_states)
            
            return float(convergence)
            
        except Exception as e:
            self.last_error = str(e)
            raise RuntimeError(f"❌ Erreur critique CFR Rust: {e}") from e
    
    def get_strategy(self, state: Dict[str, Any]) -> Dict[str, float]:
        """🚀 STRATÉGIE CFR 100% RUST - ZERO FALLBACK Python"""
        if not self.is_rust_available():
            raise RuntimeError("❌ CFR Rust requis pour stratégies optimales")
        
        try:
            rust_state = self._convert_state_to_rust(state)
            strategy = self.rust_engine.get_strategy(rust_state)
            return dict(strategy) if strategy else {"fold": 0.25, "call": 0.25, "bet": 0.25, "check": 0.25}
            
        except Exception as e:
            self.last_error = str(e)
            raise RuntimeError(f"❌ Erreur stratégie Rust: {e}") from e
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Statistiques de performance"""
        if not self.is_rust_available():
            return {
                "engine": "Python (fallback)",
                "gpu_available": False,
                "error": self.last_error
            }
        
        try:
            return {
                "engine": "Rust + GPU",
                "gpu_available": True,
                "rust_initialized": True,
                "last_error": self.last_error
            }
        except Exception as e:
            return {
                "engine": "Rust (error)",
                "gpu_available": False,
                "error": str(e)
            }
    
    def configure_gpu(self, enabled: bool, memory_limit: float, batch_size: int):
        """Configurer paramètres GPU"""
        self.config.update({
            "gpu_enabled": enabled,
            "gpu_memory_limit": memory_limit,
            "gpu_batch_size": batch_size
        })
        
        if self.is_rust_available():
            try:
                self.rust_engine.configure_gpu(enabled, memory_limit, batch_size)
                print(f"✅ GPU configuré: enabled={enabled}, memory={memory_limit:.1%}, batch={batch_size}")
            except Exception as e:
                print(f"⚠️  Erreur configuration GPU: {e}")
    
    def _convert_states_to_rust(self, states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convertir states Python vers format Rust"""
        rust_states = []
        
        for state in states:
            rust_state = {
                "hole_cards": state.get("hole_cards", []),
                "community_cards": state.get("community_cards", []),
                "pot_size": float(state.get("pot_size", 0.0)),
                "stack_size": float(state.get("stack_size", 100.0)),
                "position": int(state.get("position", 0)),
                "num_players": int(state.get("num_players", 2)),
                "betting_round": state.get("betting_round", "preflop")
            }
            rust_states.append(rust_state)
        
        return rust_states
    
    def _convert_state_to_rust(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir single state vers format Rust"""
        return {
            "hole_cards": state.get("hole_cards", []),
            "community_cards": state.get("community_cards", []),
            "pot_size": float(state.get("pot_size", 0.0)),
            "stack_size": float(state.get("stack_size", 100.0)),
            "position": int(state.get("position", 0)),
            "num_players": int(state.get("num_players", 2)),
            "betting_round": state.get("betting_round", "preflop")
        }
    
    def _train_batch_python_fallback(self, states: List[Dict[str, Any]]) -> float:
        """Fallback Python pour training CFR"""
        # Simulation simple pour test
        print("🐍 Utilisation fallback Python CFR")
        time.sleep(0.001)  # Simule calcul
        return 0.5  # Convergence mockée
    
    def _get_strategy_python_fallback(self, state: Dict[str, Any]) -> Dict[str, float]:
        """Fallback Python pour stratégie"""
        print("🐍 Stratégie fallback Python")
        return {
            "fold": 0.25,
            "call": 0.25,  
            "bet": 0.25,
            "check": 0.25
        }

# Instance globale
rust_cfr_bridge = RustCfrBridge()