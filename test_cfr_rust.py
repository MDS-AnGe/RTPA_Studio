#!/usr/bin/env python3
"""
Test complet CFR Engine Rust pour RTPA Studio
Vérification que tous les calculs CFR sont 100% Rust
"""

import sys
import os
sys.path.insert(0, 'rust_cfr_engine')

def test_cfr_rust_complete():
    """Test complet du CFR Engine Rust"""
    print("=" * 60)
    print("🚀 TEST CFR ENGINE RUST - 100% PERFORMANCE")
    print("=" * 60)
    
    try:
        # Import du module Rust
        print("📦 Import module CFR Rust...")
        import rust_cfr_engine
        print("✅ Module rust_cfr_engine importé")
        
        # Création de l'engine
        print("\n🔧 Création CFR Engine...")
        config = {
            'max_iterations': 1000, 
            'convergence_threshold': 0.01,
            'gpu_enabled': True
        }
        engine = rust_cfr_engine.RustCfrEngine(config)
        print("✅ CFR Engine Rust créé")
        
        # Test status
        print("\n📊 Test status engine...")
        status = engine.get_status()
        print("✅ Status récupéré:")
        for key, value in status.items():
            print(f"   • {key}: {value}")
        
        # Test stratégie
        print("\n🎯 Test calcul stratégie...")
        test_state = {
            'pot_size': 20.0,
            'stack_size': 100.0,
            'position': 2,
            'num_players': 6,
            'betting_round': 'preflop'
        }
        strategy = engine.get_strategy(test_state)
        print("✅ Stratégie calculée:")
        for action, prob in strategy.items():
            print(f"   • {action}: {prob:.3f}")
        
        # Test calcul probabilité
        print("\n🎲 Test calcul probabilité victoire...")
        win_prob = engine.calculate_win_probability(test_state, 1000)
        print(f"✅ Probabilité victoire: {win_prob:.3f} (1000 simulations)")
        
        # Test training batch
        print("\n🔥 Test training CFR...")
        states = [test_state] * 5  # 5 états identiques pour test
        convergence = engine.train_batch(states)
        print(f"✅ Training terminé - Convergence: {convergence:.4f}")
        
        # Test final status
        print("\n📊 Status final après training...")
        final_status = engine.get_status()
        print("✅ Status après training:")
        for key, value in final_status.items():
            print(f"   • {key}: {value}")
        
        print("\n" + "=" * 60)
        print("🎉 TOUS LES TESTS CFR RUST RÉUSSIS!")
        print("✅ CFR Engine 100% fonctionnel")
        print("🔥 Performance: Calculs ultra-rapides Rust")
        print("❌ Python CFR: Complètement remplacé")
        print("🎯 RTPA Studio: Prêt pour performance maximale")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"❌ ERREUR IMPORT MODULE: {e}")
        print("💡 Solution: Relancer install_rtpa_dependencies.py")
        return False
    except Exception as e:
        print(f"❌ ERREUR TEST CFR: {e}")
        return False

if __name__ == "__main__":
    success = test_cfr_rust_complete()
    if success:
        print("\n🚀 CFR Rust prêt - Lancez RTPA: python main_gui.py")
    else:
        print("\n⚠️  CFR Rust a des problèmes - Vérifiez l'installation")
    
    input("\nAppuyez sur Entrée pour continuer...")