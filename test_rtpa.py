#!/usr/bin/env python3
"""
Test simple pour vérifier que RTPA Studio démarre correctement
"""

import sys
import os
from pathlib import Path

# Ajout du chemin du projet
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

try:
    # Test des imports principaux
    print("🔄 Test des imports...")
    
    from src.core.app_manager import RTAPStudioManager
    from src.utils.logger import get_logger
    from src.database.memory_db import MemoryDatabase
    from src.config.settings import Settings
    
    print("✅ Imports OK")
    
    # Test initialisation des composants
    print("🔄 Test initialisation des composants...")
    
    logger = get_logger("test")
    logger.info("Logger initialisé")
    
    settings = Settings()
    print(f"✅ Settings chargés (langue: {settings.language})")
    
    db = MemoryDatabase()
    print("✅ Base de données mémoire initialisée")
    
    app_manager = RTAPStudioManager()
    print("✅ AppManager initialisé")
    
    # Test état de base
    game_state = app_manager.get_current_state()
    print(f"✅ État de jeu récupéré: {game_state.table_type}")
    
    # Test statistiques
    stats = app_manager.get_statistics()
    print(f"✅ Statistiques: {stats['hands_played']} mains jouées")
    
    print("\n🎉 Tous les tests sont passés avec succès!")
    print("RTPA Studio est prêt à fonctionner.")
    
    # Test interface graphique (sans l'afficher)
    print("\n🔄 Test interface graphique...")
    from src.gui.main_window import RTAPMainWindow
    print("✅ Interface graphique importée avec succès")
    
    print("\n🚀 Pour lancer RTPA Studio complet, exécutez: python main.py")
    
except Exception as e:
    print(f"❌ Erreur lors du test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)