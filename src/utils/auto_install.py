#!/usr/bin/env python3
"""
Auto-installation des dépendances pour RTPA Studio
Installation automatique lors du premier lancement
"""

import subprocess
import sys
import os
import importlib.util
from pathlib import Path

def check_and_install_dependencies():
    """
    Vérifie et installe automatiquement toutes les dépendances manquantes
    """
    print("🔍 Vérification des dépendances...")
    
    # Liste des dépendances critiques avec leur nom d'import et nom pip
    dependencies = {
        'yaml': 'pyyaml',
        'cv2': 'opencv-python',
        'pytesseract': 'pytesseract',
        'numpy': 'numpy',
        'scipy': 'scipy',
        'numba': 'numba',
        'pygame': 'pygame',
        'customtkinter': 'customtkinter',
        'PIL': 'pillow',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'mss': 'mss',
        'psutil': 'psutil',
        'requests': 'requests'
    }
    
    missing_packages = []
    
    # Vérification de chaque dépendance
    for import_name, pip_name in dependencies.items():
        if not is_package_installed(import_name):
            missing_packages.append(pip_name)
            print(f"❌ {import_name} manquant")
        else:
            print(f"✅ {import_name} disponible")
    
    # Installation des paquets manquants
    if missing_packages:
        print(f"\n📦 Installation de {len(missing_packages)} dépendances manquantes...")
        install_packages(missing_packages)
        print("✅ Toutes les dépendances ont été installées avec succès!")
    else:
        print("✅ Toutes les dépendances sont déjà installées!")
    
    return True

def is_package_installed(package_name):
    """
    Vérifie si un package est installé et importable
    """
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except (ImportError, AttributeError, ValueError, ModuleNotFoundError):
        return False

def install_packages(packages):
    """
    Installe une liste de packages via pip
    """
    for package in packages:
        try:
            print(f"📦 Installation de {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package, "--quiet"
            ], capture_output=True, text=True, check=True)
            print(f"✅ {package} installé avec succès")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation de {package}: {e}")
            print(f"📝 Sortie d'erreur: {e.stderr}")
            
            # Tentative d'installation avec --user si échec
            try:
                print(f"🔄 Tentative d'installation avec --user pour {package}...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package, "--user", "--quiet"
                ], capture_output=True, text=True, check=True)
                print(f"✅ {package} installé avec succès (mode utilisateur)")
            except subprocess.CalledProcessError as e2:
                print(f"❌ Échec complet de l'installation de {package}")
                return False
    
    return True

def install_from_requirements():
    """
    Installe directement depuis requirements.txt si disponible
    """
    requirements_path = Path(__file__).parent.parent.parent / "requirements.txt"
    
    if requirements_path.exists():
        print("📋 Installation depuis requirements.txt...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_path), "--quiet"
            ], check=True)
            print("✅ Installation depuis requirements.txt réussie!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation depuis requirements.txt: {e}")
            return False
    
    return False

def ensure_pip_available():
    """
    S'assure que pip est disponible
    """
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ pip n'est pas disponible. Tentative d'installation...")
        try:
            subprocess.run([sys.executable, "-m", "ensurepip", "--default-pip"], 
                          capture_output=True, check=True)
            print("✅ pip installé avec succès!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Impossible d'installer pip automatiquement")
            return False

def auto_install_dependencies():
    """
    Point d'entrée principal pour l'auto-installation
    """
    print("🚀 RTPA Studio - Installation automatique des dépendances")
    print("=" * 60)
    
    # Vérification de pip
    if not ensure_pip_available():
        print("❌ pip n'est pas disponible. Installation manuelle requise.")
        return False
    
    # Tentative d'installation depuis requirements.txt d'abord
    if install_from_requirements():
        return True
    
    # Sinon, installation package par package
    return check_and_install_dependencies()

if __name__ == "__main__":
    auto_install_dependencies()