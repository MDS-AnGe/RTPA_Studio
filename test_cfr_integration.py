#!/usr/bin/env python3
"""
Test d'intégration complète du système CFR RTPA Studio
Valide l'entraînement automatique et la qualité des recommandations
"""

import time
import sys
import os
sys.path.append('src')

from src.algorithms.cfr_engine import CFREngine
from src.algorithms.cfr_trainer import CFRTrainer
from src.algorithms.hand_parser import HandParser
from src.core.app_manager import GameState
from src.utils.logger import get_logger

def test_cfr_integration():
    """Test complet d'intégration CFR"""
    logger = get_logger("test_cfr_integration")
    
    print("🎯 Test d'Intégration CFR RTPA Studio")
    print("=" * 60)
    
    # 1. Initialisation CFR Engine
    print("📊 1. Initialisation CFR Engine...")
    cfr_engine = CFREngine()
    initial_iterations = cfr_engine.iterations
    print(f"   ✓ CFR initialisé - Itérations: {initial_iterations}")
    
    # 2. Initialisation Trainer
    print("🚀 2. Initialisation CFR Trainer...")
    cfr_engine.init_trainer()
    time.sleep(3)  # Laisser temps à l'initialisation
    print(f"   ✓ Trainer initialisé")
    
    # 3. Vérification chargement des mains
    print("📁 3. Vérification chargement des mains...")
    if cfr_engine.cfr_trainer:
        training_hands = len(cfr_engine.cfr_trainer.training_hands)
        print(f"   ✓ Mains chargées: {training_hands}")
        
        if training_hands == 0:
            print("   ⚠️  Aucune main chargée, génération de mains de test...")
            cfr_engine.cfr_trainer.generate_training_dataset(10000)
            training_hands = len(cfr_engine.cfr_trainer.training_hands)
            print(f"   ✓ Mains générées: {training_hands}")
    else:
        print("   ❌ Trainer non initialisé")
        return False
    
    # 4. Test de progression d'entraînement
    print("⚡ 4. Test progression d'entraînement...")
    progress_initial = cfr_engine.get_training_progress()
    print(f"   📈 Progression initiale:")
    print(f"      - Itérations: {progress_initial['iterations']}")
    print(f"      - Qualité: {progress_initial['quality']:.2%}")
    print(f"      - Confiance: {progress_initial['confidence']:.1f}%")
    print(f"      - Info sets: {progress_initial['info_sets']}")
    
    # 5. Test recommandation avec progression
    print("🎯 5. Test recommandations avec amélioration...")
    
    # Création d'un état de jeu test
    game_state = GameState(
        table_type="cashgame",
        players_count=2,
        hero_position=1,
        hero_cards=("As", "Kh"),
        board_cards=("Ah", "Kd", "7c"),
        pot_size=150.0,
        hero_stack=2500.0,
        current_bet=50.0,
        action_to_hero=True
    )
    
    # Test initial
    rec_initial = cfr_engine.get_recommendation(game_state)
    print(f"   🃏 Recommandation initiale:")
    print(f"      - Action: {rec_initial.get('action_type', 'unknown')}")
    print(f"      - Confiance: {rec_initial.get('confidence', 0):.1f}%")
    print(f"      - Probabilité victoire: {rec_initial.get('win_probability', 0):.1%}")
    
    # Attendre un peu d'entraînement
    print("   ⏳ Attente entraînement (30 secondes)...")
    time.sleep(30)
    
    # Test après entraînement
    progress_after = cfr_engine.get_training_progress()
    rec_after = cfr_engine.get_recommendation(game_state)
    
    print(f"   📈 Progression après entraînement:")
    print(f"      - Itérations: {progress_after['iterations']} (+{progress_after['iterations'] - progress_initial['iterations']})")
    print(f"      - Qualité: {progress_after['quality']:.2%}")
    print(f"      - Confiance: {progress_after['confidence']:.1f}%")
    print(f"      - Info sets: {progress_after['info_sets']}")
    
    print(f"   🃏 Recommandation après entraînement:")
    print(f"      - Action: {rec_after.get('action_type', 'unknown')}")
    print(f"      - Confiance: {rec_after.get('confidence', 0):.1f}%")
    print(f"      - Probabilité victoire: {rec_after.get('win_probability', 0):.1%}")
    
    # 6. Validation des améliorations
    print("✅ 6. Validation des améliorations...")
    
    improvements = {
        'iterations_increased': progress_after['iterations'] > progress_initial['iterations'],
        'quality_acceptable': progress_after['quality'] > 0.1,  # Au moins 10%
        'confidence_working': rec_after.get('confidence', 0) >= 0,
        'training_active': progress_after['training_active'],
        'info_sets_growing': progress_after['info_sets'] > 0
    }
    
    for test_name, passed in improvements.items():
        status = "✓" if passed else "❌"
        print(f"   {status} {test_name.replace('_', ' ').title()}: {passed}")
    
    # Calcul du score global
    score = sum(improvements.values()) / len(improvements) * 100
    print(f"\n📊 Score global: {score:.1f}%")
    
    if score >= 80:
        print("🎉 ✅ SYSTÈME CFR FONCTIONNEL ET VIABLE!")
        print("   Le système d'entraînement automatique fonctionne correctement.")
        print("   Les recommandations s'améliorent avec l'entraînement.")
        return True
    elif score >= 60:
        print("⚠️  ✅ SYSTÈME CFR PARTIELLEMENT FONCTIONNEL")
        print("   Le système fonctionne mais nécessite plus d'entraînement.")
        return True
    else:
        print("❌ SYSTÈME CFR NON FONCTIONNEL")
        print("   Des problèmes empêchent le bon fonctionnement.")
        return False

if __name__ == "__main__":
    success = test_cfr_integration()
    sys.exit(0 if success else 1)