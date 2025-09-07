#!/usr/bin/env python3
"""
🎯 RTPA Studio - Lanceur Principal
Logiciel d'analyse poker temps réel à des fins d'étude
"""

import sys
import os
import subprocess
from pathlib import Path

def print_banner():
    """Affiche la bannière de lancement"""
    print("🎯 RTPA STUDIO - REAL-TIME POKER ANALYSIS")
    print("=" * 60)
    print("Logiciel d'analyse poker temps réel à des fins d'étude")
    print("Usage exclusivement éducatif et non-commercial")
    print("=" * 60)
    print()

def check_requirements():
    """Vérifie les prérequis d'installation"""
    errors = []
    
    # Vérification Python
    if sys.version_info < (3, 8):
        errors.append(f"Python 3.8+ requis (version actuelle: {sys.version_info.major}.{sys.version_info.minor})")
    
    # Vérification Tesseract
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            errors.append("Tesseract OCR non fonctionnel")
    except (subprocess.CalledProcessError, FileNotFoundError):
        errors.append("Tesseract OCR non installé ou non dans le PATH")
    
    # Vérification modules Python critiques
    critical_modules = [
        'numpy', 'cv2', 'pytesseract', 'PIL', 'customtkinter',
        'mss', 'psutil', 'yaml'
    ]
    
    missing_modules = []
    for module in critical_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        errors.append(f"Modules Python manquants: {', '.join(missing_modules)}")
    
    return errors

def show_launcher_menu():
    """Affiche le menu de lancement"""
    print("🚀 MODES DE LANCEMENT DISPONIBLES:")
    print()
    print("1. 🎮 Interface Graphique Complète")
    print("   → Analyse temps réel avec GUI moderne")
    print("   → Tous les onglets et fonctionnalités")
    print()
    print("2. 🖥️  Mode Console/Démo")
    print("   → Démonstration en ligne de commande")
    print("   → Affichage temps réel des calculs")
    print()
    print("3. 🧪 Tests et Validation")
    print("   → Tests complets du système")
    print("   → Validation algorithmes CFR/Nash")
    print()
    print("4. ⚙️  Installation/Configuration")
    print("   → Réinstaller les dépendances")
    print("   → Calibrage OCR client poker")
    print()
    print("0. ❌ Quitter")
    print()

def launch_gui():
    """Lance l'interface graphique"""
    print("🎮 Lancement interface graphique...")
    print("⏳ Chargement des composants...")
    
    try:
        # Ajouter le répertoire du projet au path
        project_dir = Path(__file__).parent
        sys.path.insert(0, str(project_dir))
        
        # Lancement de l'interface
        from main_gui import main
        main()
        
    except Exception as e:
        print(f"❌ Erreur lancement interface: {e}")
        print("\n🔧 Solutions possibles:")
        print("   1. Vérifiez l'installation: python setup_installer.py")
        print("   2. Mode console: python main_headless.py")
        print("   3. Tests: python test_final.py")
        input("\nAppuyez sur Entrée pour continuer...")

def launch_console():
    """Lance le mode console"""
    print("🖥️  Lancement mode console...")
    
    try:
        subprocess.run([sys.executable, "main_headless.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur mode console: {e}")
    except FileNotFoundError:
        print("❌ Fichier main_headless.py non trouvé")

def launch_tests():
    """Lance les tests"""
    print("🧪 TESTS DISPONIBLES:")
    print("1. Tests complets (recommandé)")
    print("2. Tests algorithmes CFR/Nash")
    print("3. Benchmarks performance")
    print("4. Retour menu principal")
    
    choice = input("\nChoisissez (1-4): ").strip()
    
    test_files = {
        '1': 'test_final.py',
        '2': 'test_algorithms_validation.py',
        '3': 'test_performance_benchmarks.py'
    }
    
    if choice in test_files:
        test_file = test_files[choice]
        print(f"🔄 Exécution {test_file}...")
        
        try:
            subprocess.run([sys.executable, test_file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur test: {e}")
        except FileNotFoundError:
            print(f"❌ Fichier {test_file} non trouvé")
    elif choice == '4':
        return
    else:
        print("❌ Choix invalide")

def launch_setup():
    """Lance l'installation/configuration"""
    print("⚙️  INSTALLATION ET CONFIGURATION:")
    print("1. Réinstaller toutes les dépendances")
    print("2. Test installation actuelle")
    print("3. Configuration OCR clients poker")
    print("4. Retour menu principal")
    
    choice = input("\nChoisissez (1-4): ").strip()
    
    if choice == '1':
        print("🔄 Lancement installateur automatique...")
        try:
            subprocess.run([sys.executable, "setup_installer.py"], check=True)
        except FileNotFoundError:
            print("❌ Fichier setup_installer.py non trouvé")
            print("💡 Téléchargez le package complet de RTPA Studio")
    
    elif choice == '2':
        print("🧪 Test installation...")
        errors = check_requirements()
        if not errors:
            print("✅ Installation complète et fonctionnelle!")
        else:
            print("❌ Problèmes détectés:")
            for error in errors:
                print(f"   • {error}")
    
    elif choice == '3':
        print("⚙️  Configuration OCR...")
        print("💡 Utilisez l'onglet 'Configuration' dans l'interface graphique")
        print("   pour calibrer les zones OCR selon votre client poker.")
        launch_gui()
    
    elif choice == '4':
        return
    else:
        print("❌ Choix invalide")

def main():
    """Fonction principale du lanceur"""
    print_banner()
    
    # Vérification des prérequis
    print("🔍 Vérification de l'installation...")
    errors = check_requirements()
    
    if errors:
        print("⚠️  PROBLÈMES DÉTECTÉS:")
        for error in errors:
            print(f"   • {error}")
        print()
        print("🔧 Exécutez l'installateur automatique:")
        print("   python setup_installer.py")
        print()
        
        choice = input("Continuer malgré les erreurs? (o/N): ").lower()
        if choice not in ['o', 'oui', 'y', 'yes']:
            print("Installation requise. Arrêt du programme.")
            return
    else:
        print("✅ Installation vérifiée et fonctionnelle!")
    
    print()
    
    # Menu principal
    while True:
        show_launcher_menu()
        
        choice = input("Choisissez votre option (0-4): ").strip()
        print()
        
        if choice == '1':
            launch_gui()
        elif choice == '2':
            launch_console()
        elif choice == '3':
            launch_tests()
        elif choice == '4':
            launch_setup()
        elif choice == '0':
            print("🎓 Merci d'avoir utilisé RTPA Studio!")
            print("📚 N'oubliez pas: usage strictement éducatif!")
            break
        else:
            print("❌ Choix invalide. Utilisez 0-4.")
        
        print("\n" + "─" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("🔧 Essayez: python setup_installer.py")
    finally:
        print("\n👋 Au revoir!")