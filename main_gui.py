#!/usr/bin/env python3
"""
Lancement de RTPA Studio avec interface graphique moderne
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

def main():
    """Lance RTPA Studio avec interface graphique"""
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
        gui.run()
        
    except Exception as e:
        print(f"Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()