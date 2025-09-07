#!/usr/bin/env python3
"""
RTPA Studio - Real-Time Poker Analysis Studio
Logiciel d'analyse de poker en temps réel avec OCR et calculs CFR/Nash
"""

import sys
import os
import threading
import time
from pathlib import Path

# Configuration du projet
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# Auto-installation des dépendances au premier lancement
print("🚀 RTPA Studio - Démarrage")
print("=" * 40)

try:
    from src.utils.auto_install import auto_install_dependencies
    if auto_install_dependencies():
        print("✅ Dépendances vérifiées/installées avec succès!\n")
    else:
        print("⚠️  Problème avec l'installation automatique\n")
except Exception as e:
    print(f"⚠️  Auto-installation échouée: {e}")
    print("📝 Tentative de poursuite...\n")

# Import des modules principaux
from src.core.app_manager import RTAPStudioManager
from src.gui.main_window import RTAPMainWindow
from src.utils.logger import setup_logger

def main():
    """Point d'entrée principal de RTPA Studio"""
    try:
        # Configuration des logs
        logger = setup_logger()
        logger.info("Démarrage de RTPA Studio...")
        
        # Initialisation du gestionnaire principal
        app_manager = RTAPStudioManager()
        
        # Lancement de l'interface graphique
        main_window = RTAPMainWindow(app_manager)
        main_window.run()
        
    except Exception as e:
        print(f"Erreur critique au démarrage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()