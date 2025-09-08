#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC OCR WINDOWS POUR RTPA
Script de diagnostic pour vérifier pourquoi l'OCR ne fonctionne pas sur Windows
"""

import os
import sys
import platform
import psutil
from pathlib import Path

def diagnostic_windows_ocr():
    """Diagnostic complet OCR Windows"""
    
    print("🔍 DIAGNOSTIC OCR WINDOWS - RTPA")
    print("=" * 50)
    
    # 1. Vérification environnement
    print("\n1️⃣ ENVIRONNEMENT:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Python: {sys.version}")
    print(f"   Architecture: {platform.architecture()[0]}")
    
    # 2. Vérification Winamax
    print("\n2️⃣ DÉTECTION WINAMAX:")
    winamax_processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if 'winamax' in proc.info['name'].lower():
                    winamax_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'exe': proc.info['exe']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        if winamax_processes:
            print("   ✅ Winamax détecté:")
            for proc in winamax_processes:
                print(f"      • PID {proc['pid']}: {proc['name']}")
        else:
            print("   ❌ Aucun processus Winamax trouvé")
            print("   🔧 SOLUTION: Ouvrez Winamax et lancez une table")
            
    except Exception as e:
        print(f"   ❌ Erreur détection: {e}")
    
    # 3. Vérification dépendances OCR
    print("\n3️⃣ DÉPENDANCES OCR:")
    
    required_modules = [
        'mss', 'cv2', 'pytesseract', 'numpy', 'PIL'
    ]
    
    for module in required_modules:
        try:
            if module == 'cv2':
                import cv2
                print(f"   ✅ OpenCV: {cv2.__version__}")
            elif module == 'mss':
                import mss
                # Test rapide de capture
                try:
                    with mss.mss() as sct:
                        screenshot = sct.grab({'top': 0, 'left': 0, 'width': 100, 'height': 100})
                    print(f"   ✅ MSS: Capture d'écran OK")
                except Exception as e:
                    print(f"   ❌ MSS: Erreur capture - {e}")
            elif module == 'pytesseract':
                import pytesseract
                # Vérifier Tesseract
                try:
                    version = pytesseract.get_tesseract_version()
                    print(f"   ✅ Tesseract: {version}")
                except Exception as e:
                    print(f"   ❌ Tesseract non trouvé: {e}")
                    print("   🔧 SOLUTION: Installez Tesseract-OCR")
            else:
                __import__(module)
                print(f"   ✅ {module}: OK")
                
        except ImportError:
            print(f"   ❌ {module}: MANQUANT")
            print(f"   🔧 SOLUTION: pip install {module}")
    
    # 4. Test capture d'écran basique
    print("\n4️⃣ TEST CAPTURE D'ÉCRAN:")
    try:
        import mss
        import numpy as np
        
        with mss.mss() as sct:
            # Capture petite zone pour test
            region = {'top': 100, 'left': 100, 'width': 200, 'height': 100}
            screenshot = sct.grab(region)
            img = np.array(screenshot)
            
            print(f"   ✅ Capture réussie: {img.shape}")
            print(f"   📊 Résolution écran: {sct.monitors[1]['width']}x{sct.monitors[1]['height']}")
            
    except Exception as e:
        print(f"   ❌ Erreur capture: {e}")
    
    # 5. Configuration RTPA
    print("\n5️⃣ CONFIGURATION RTPA:")
    
    # Vérifier variables d'environnement
    rtpa_vars = [
        'RTPA_FORCE_REAL_CAPTURE',
        'DISPLAY'
    ]
    
    for var in rtpa_vars:
        value = os.getenv(var)
        if value:
            print(f"   • {var}={value}")
        else:
            print(f"   • {var}: Non défini")
    
    # 6. Recommandations
    print("\n6️⃣ RECOMMANDATIONS:")
    print("   🔧 Pour activer l'OCR sur Windows:")
    print("   1. Ouvrez Winamax")
    print("   2. Lancez une table de poker")
    print("   3. Définissez: set RTPA_FORCE_REAL_CAPTURE=true")
    print("   4. Relancez: python rtpa.py")
    print("   5. Vérifiez les messages de debug dans la console")
    
    print("\n✅ Diagnostic terminé!")
    print("📧 Si le problème persiste, partagez ces informations")

if __name__ == "__main__":
    diagnostic_windows_ocr()