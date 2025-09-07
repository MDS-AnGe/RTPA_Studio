#!/usr/bin/env python3
"""
Version headless de RTPA Studio pour démonstration
Fonctionne sans interface graphique X11
"""

import sys
import time
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from src.core.app_manager import RTAPStudioManager
from src.utils.logger import setup_logger

def main():
    """Point d'entrée pour la démonstration headless"""
    try:
        logger = setup_logger()
        logger.info("Démarrage de RTPA Studio (mode headless)")
        
        # Initialisation du gestionnaire
        app_manager = RTAPStudioManager()
        
        # Démarrage de l'analyse
        app_manager.start()
        logger.info("Analyse démarrée - Mode démonstration")
        
        print("🎯 RTPA Studio - Démonstration")
        print("=" * 50)
        print("Mode: Simulation (sans capture d'écran réelle)")
        print("Appuyez sur Ctrl+C pour arrêter")
        print()
        
        try:
            while True:
                # Affichage des données actuelles
                game_state = app_manager.get_current_state()
                recommendation = app_manager.get_recommendation()
                stats = app_manager.get_statistics()
                
                # Clear screen
                print("\033[2J\033[H", end="")
                
                print("🎯 RTPA Studio - Démonstration Temps Réel")
                print("=" * 60)
                print(f"📊 Situation Actuelle:")
                print(f"   Cartes Héros: {game_state.hero_cards[0]} {game_state.hero_cards[1]}")
                print(f"   Board: {' '.join(game_state.board_cards)}")
                print(f"   Pot: {game_state.pot_size:.2f}€")
                print(f"   Stack: {game_state.hero_stack:.2f}€")
                print(f"   Type: {game_state.table_type}")
                print()
                
                if recommendation:
                    print("🎯 Recommandation:")
                    print(f"   Action: {recommendation['action_type'].upper()}")
                    if recommendation['bet_size'] > 0:
                        print(f"   Taille: {recommendation['bet_size']:.2f}€")
                    print(f"   Probabilité Victoire: {recommendation['win_probability']:.1f}%")
                    print(f"   Niveau Risque: {recommendation['risk_level']:.0f}%")
                    print(f"   Confiance: {recommendation['confidence']:.0f}%")
                    print(f"   Raisonnement: {recommendation['reasoning']}")
                    print()
                
                print("📈 Statistiques:")
                print(f"   Mains Jouées: {stats['hands_played']}")
                print(f"   Mains Gagnées: {stats['hands_won']}")
                print(f"   Taux Victoire: {stats['win_rate']:.1f}%")
                print(f"   Taux Attendu: {stats['expected_win_rate']:.1f}%")
                print(f"   Performance: {stats['performance_ratio']:.1f}%")
                print()
                
                print("⚡ Système:")
                print("   Status: ✅ Actif")
                print("   OCR: 🔄 Simulation")
                print("   CFR: 🧠 Calculs continus")
                print("   Base: 💾 En mémoire")
                
                time.sleep(2)  # Mise à jour toutes les 2 secondes
                
        except KeyboardInterrupt:
            print("\n\n🛑 Arrêt demandé...")
            app_manager.stop()
            print("✅ RTPA Studio arrêté proprement")
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()