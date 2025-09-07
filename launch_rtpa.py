#!/usr/bin/env python3
"""
Lanceur principal pour RTPA Studio
Configuré pour apparaître comme une application indépendante
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Lance RTPA Studio avec configuration Windows appropriée"""
    
    # Configuration du titre pour Windows
    if sys.platform == "win32":
        try:
            import ctypes
            # Définir le titre de la console
            ctypes.windll.kernel32.SetConsoleTitleW("RTPA Studio")
            
            # Configuration de l'ID d'application Windows
            try:
                app_id = "RTPA.Studio.PokerAnalysis.1.0"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            except Exception:
                pass
        except ImportError:
            pass
    
    # Changer le titre du processus si possible
    try:
        if hasattr(sys, 'ps1'):  # Mode interactif
            sys.ps1 = "RTPA Studio >>> "
    except:
        pass
    
    # Lancer le programme principal
    script_path = Path(__file__).parent / "main_gui.py"
    
    try:
        # Exécuter avec le bon titre
        if sys.platform == "win32":
            os.system(f'title RTPA Studio & python "{script_path}"')
        else:
            subprocess.run([sys.executable, str(script_path)])
    except Exception as e:
        print(f"Erreur lors du lancement: {e}")
        # Fallback - lancement direct
        import main_gui
        main_gui.main()

if __name__ == "__main__":
    main()