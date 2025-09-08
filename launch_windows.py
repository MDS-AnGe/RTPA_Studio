#!/usr/bin/env python3
"""
🚀 LANCEUR RTPA STUDIO POUR WINDOWS
Lanceur spécialisé pour environnement Windows avec capture OCR temps réel
"""

import os
import sys
import platform
import subprocess

def check_windows_requirements():
    """Vérifie les prérequis Windows"""
    print("🔍 Vérification environnement Windows...")
    
    if platform.system() != 'Windows':
        print("❌ Ce lanceur est spécialement conçu pour Windows")
        return False
    
    print("✅ Système Windows détecté")
    
    # Vérifier Python
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        print(f"❌ Python 3.8+ requis (trouvé: {python_version.major}.{python_version.minor})")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor} OK")
    
    # Vérifier dépendances critiques
    required_modules = ['mss', 'cv2', 'numpy', 'PIL', 'psutil']
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'cv2':
                import cv2
            elif module == 'PIL':
                import PIL
            else:
                __import__(module)
            print(f"✅ {module}: OK")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module}: MANQUANT")
    
    if missing_modules:
        print(f"\n🔧 Installez les dépendances manquantes:")
        print(f"pip install {' '.join(missing_modules)}")
        if 'cv2' in missing_modules:
            print("pip install opencv-python")
        return False
    
    return True

def check_tesseract():
    """Vérifie Tesseract OCR"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract OCR non trouvé: {e}")
        print("🔧 Téléchargez: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def launch_rtpa():
    """Lance RTPA Studio avec configuration Windows"""
    print("\n🚀 Lancement RTPA Studio pour Windows...")
    
    # Forcer la capture d'écran réelle
    os.environ['RTPA_FORCE_REAL_CAPTURE'] = 'true'
    os.environ['RTPA_WINDOWS_MODE'] = 'true'
    
    # Lancer RTPA
    try:
        import rtpa
        print("✅ RTPA Studio démarré avec capture OCR temps réel")
    except Exception as e:
        print(f"❌ Erreur démarrage RTPA: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("🎯 RTPA STUDIO - LANCEUR WINDOWS")
    print("=" * 50)
    
    # Vérifications prérequis
    if not check_windows_requirements():
        input("\nAppuyez sur Entrée pour quitter...")
        return
    
    if not check_tesseract():
        input("\nAppuyez sur Entrée pour quitter...")
        return
    
    print("\n✅ Tous les prérequis sont satisfaits")
    print("\n📋 INSTRUCTIONS UTILISATION:")
    print("1. Ouvrez Winamax")
    print("2. Lancez une table de poker")
    print("3. RTPA détectera automatiquement la table")
    print("4. Les données OCR apparaîtront en temps réel")
    
    input("\nAppuyez sur Entrée pour démarrer RTPA...")
    
    # Lancement
    if launch_rtpa():
        print("🎉 RTPA Studio lancé avec succès !")
    else:
        print("❌ Échec du lancement")
        input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()