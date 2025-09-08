#!/usr/bin/env python3
"""
RTPA Studio - Real-Time Poker Assistant
Point d'entrée unique avec interface graphique et mode console
"""

import sys
import time
import argparse
from pathlib import Path

# Configuration du projet
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# Configuration Windows pour nom d'application
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW("RTPA Studio")
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("RTAPStudio.PokerAnalysis.1.0")
        except:
            pass
    except ImportError:
        pass

def main_headless():
    """Mode démonstration console (sans interface graphique)"""
    try:
        from src.core.app_manager import RTAPStudioManager
        from src.utils.logger import setup_logger
        
        logger = setup_logger()
        logger.info("Démarrage de RTPA Studio (mode headless)")
        
        # Initialisation du gestionnaire
        app_manager = RTAPStudioManager()
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
                
                print("🧠 Recommandation Nash:")
                print(f"   Action: {recommendation.action}")
                print(f"   Probabilité victoire: {recommendation.win_probability:.1f}%")
                print(f"   Niveau risque: {recommendation.risk_level:.1f}%")
                print()
                
                print("📈 Statistiques:")
                print(f"   Mains jouées: {stats.hands_played}")
                print(f"   Taux victoire: {stats.win_rate:.1f}%")
                print(f"   Performance vs Pro: {stats.performance_vs_pro:.1f}%")
                print()
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du mode démonstration")
            app_manager.stop()
            
    except Exception as e:
        print(f"❌ Erreur mode headless: {e}")
        return False
    
    return True

def main():
    """Lance RTPA Studio avec interface graphique moderne"""
    
    # Gestion des arguments
    parser = argparse.ArgumentParser(description='RTPA Studio - Real-Time Poker Assistant')
    parser.add_argument('--headless', action='store_true', 
                       help='Mode console sans interface graphique (pour démonstration)')
    parser.add_argument('--version', action='store_true',
                       help='Affiche la version')
    
    args = parser.parse_args()
    
    if args.version:
        print("RTPA Studio v1.1.0")
        return
    
    if args.headless:
        return main_headless()
    
    # Auto-installation des dépendances
    print("🚀 RTPA Studio")
    print("=" * 30)
    
    try:
        from src.utils.auto_install import auto_install_dependencies
        if auto_install_dependencies():
            print("✅ Dépendances prêtes!\n")
        else:
            print("⚠️  Problème installation automatique\n")
    except Exception as e:
        print(f"⚠️  Auto-installation échouée: {e}")
        print("📝 Poursuite...\n")
    
    try:
        from src.core.app_manager import RTAPStudioManager
        from src.gui.rtpa_gui import RTAPGUIWindow
        from src.utils.logger import setup_logger
        
        logger = setup_logger()
        logger.info("Démarrage RTPA Studio GUI")
        
        # Initialisation et lancement
        app_manager = RTAPStudioManager()
        gui = RTAPGUIWindow(app_manager)
        app_manager.set_gui_window(gui)
        
        gui.run()
        
    except Exception as e:
        print(f"Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()