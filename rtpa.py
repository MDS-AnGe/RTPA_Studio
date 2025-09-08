#!/usr/bin/env python3
"""
RTPA Studio - Real-Time Poker Assistant
Point d'entrée principal pour l'interface graphique moderne
"""

import sys
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

def main():
    """Lance RTPA Studio avec interface graphique moderne"""
    
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