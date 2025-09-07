#!/usr/bin/env python3
"""
Lancement de RTPA Studio avec interface graphique moderne
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# Configuration pour Windows - Nom du processus dans le gestionnaire des tâches
if sys.platform == "win32":
    try:
        import ctypes
        # Définir le nom de l'application pour Windows
        ctypes.windll.kernel32.SetConsoleTitleW("RTPA Studio")
        
        # Essayer de changer l'identifiant du processus (si possible)
        try:
            # Note: cela nécessite des privilèges élevés et peut ne pas fonctionner
            app_id = "RTAPStudio.PokerAnalysis.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass  # Ne pas échouer si cela ne fonctionne pas
            
    except ImportError:
        pass  # ctypes n'est pas disponible

def main():
    """Lance RTPA Studio avec interface graphique"""
    
    # Auto-installation des dépendances
    print("🚀 RTPA Studio - Interface Graphique")
    print("=" * 45)
    
    try:
        from src.utils.auto_install import auto_install_dependencies
        if auto_install_dependencies():
            print("✅ Dépendances vérifiées/installées avec succès!\n")
        else:
            print("⚠️  Problème avec l'installation automatique\n")
    except Exception as e:
        print(f"⚠️  Auto-installation échouée: {e}")
        print("📝 Tentative de poursuite...\n")
    
    try:
        from src.core.app_manager import RTAPStudioManager
        from src.gui.rtpa_gui import RTAPGUIWindow
        from src.utils.logger import setup_logger
        
        logger = setup_logger()
        logger.info("Démarrage de RTPA Studio avec interface graphique")
        
        # Initialisation du gestionnaire
        app_manager = RTAPStudioManager()
        
        # Lancement de l'interface
        gui = RTAPGUIWindow(app_manager)
        
        # Connecter la GUI au gestionnaire pour les callbacks de statut
        app_manager.set_gui_window(gui)
        
        gui.run()
        
    except Exception as e:
        print(f"Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()