#!/usr/bin/env python3
"""
Installateur automatique pour RTPA Studio
Installation automatique de toutes les dépendances
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

class RTAPInstaller:
    """Installateur automatique RTPA Studio"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.errors = []
        
    def print_header(self):
        """Affiche l'en-tête d'installation"""
        print("🎯 RTPA STUDIO - INSTALLATEUR AUTOMATIQUE")
        print("=" * 55)
        print(f"Système: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        print(f"Architecture: {platform.machine()}")
        print()
        print("⚠️  AVERTISSEMENT IMPORTANT ⚠️")
        print("Ce logiciel est conçu exclusivement à des fins d'étude")
        print("et de recherche académique sur les algorithmes de poker.")
        print("Usage strictement éducatif et non-commercial.")
        print()
        
    def check_python_version(self):
        """Vérifie la version Python"""
        print("🐍 Vérification version Python...")
        
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ requis")
            print(f"   Version actuelle: {self.python_version}")
            return False
        
        print(f"✅ Python {self.python_version} OK")
        return True
    
    def install_tesseract(self):
        """Installe Tesseract OCR selon le système"""
        print("👁️ Installation Tesseract OCR...")
        
        try:
            # Test si Tesseract est déjà installé
            subprocess.run(['tesseract', '--version'], 
                         capture_output=True, check=True)
            print("✅ Tesseract déjà installé")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⏳ Installation de Tesseract...")
            
            if self.system == "windows":
                return self._install_tesseract_windows()
            elif self.system == "darwin":  # macOS
                return self._install_tesseract_macos()
            elif self.system == "linux":
                return self._install_tesseract_linux()
            else:
                print(f"❌ Système non supporté: {self.system}")
                return False
    
    def _install_tesseract_windows(self):
        """Installation Tesseract sur Windows"""
        try:
            print("📥 Téléchargement Tesseract Windows...")
            
            # URL de Tesseract pour Windows
            url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
            installer_path = "tesseract_installer.exe"
            
            urllib.request.urlretrieve(url, installer_path)
            
            print("🔧 Lancement installation Tesseract...")
            print("⚠️  Suivez les instructions à l'écran")
            print("⚠️  Assurez-vous d'ajouter Tesseract au PATH")
            
            subprocess.run([installer_path, '/S'], check=True)
            os.remove(installer_path)
            
            # Ajouter au PATH si nécessaire
            tesseract_path = r"C:\\Program Files\\Tesseract-OCR"
            if tesseract_path not in os.environ.get('PATH', ''):
                print("📝 Ajout de Tesseract au PATH...")
                current_path = os.environ.get('PATH', '')
                os.environ['PATH'] = f"{current_path};{tesseract_path}"
            
            print("✅ Tesseract installé avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur installation Tesseract: {e}")
            print("🔧 Installation manuelle requise:")
            print("   1. Téléchargez Tesseract: https://github.com/UB-Mannheim/tesseract/releases")
            print("   2. Installez en suivant les instructions")
            print("   3. Ajoutez Tesseract au PATH système")
            return False
    
    def _install_tesseract_macos(self):
        """Installation Tesseract sur macOS"""
        try:
            # Tenter avec Homebrew
            print("🍺 Installation via Homebrew...")
            subprocess.run(['brew', 'install', 'tesseract'], check=True)
            print("✅ Tesseract installé via Homebrew")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Homebrew non trouvé")
            print("🔧 Installation manuelle requise:")
            print("   1. Installez Homebrew: https://brew.sh")
            print("   2. Exécutez: brew install tesseract")
            print("   Ou téléchargez depuis: https://github.com/tesseract-ocr/tesseract")
            return False
    
    def _install_tesseract_linux(self):
        """Installation Tesseract sur Linux"""
        try:
            # Détecter la distribution
            if os.path.exists('/etc/debian_version'):
                # Debian/Ubuntu
                print("🐧 Installation via apt...")
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'tesseract-ocr'], check=True)
                
            elif os.path.exists('/etc/redhat-release'):
                # RedHat/CentOS/Fedora
                print("🎩 Installation via yum/dnf...")
                try:
                    subprocess.run(['sudo', 'dnf', 'install', '-y', 'tesseract'], check=True)
                except:
                    subprocess.run(['sudo', 'yum', 'install', '-y', 'tesseract'], check=True)
                    
            elif os.path.exists('/etc/arch-release'):
                # Arch Linux
                print("🏹 Installation via pacman...")
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'tesseract'], check=True)
                
            else:
                print("❌ Distribution Linux non reconnue")
                print("🔧 Installez manuellement: sudo apt install tesseract-ocr")
                return False
            
            print("✅ Tesseract installé sur Linux")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur installation Tesseract: {e}")
            print("🔧 Essayez manuellement: sudo apt install tesseract-ocr")
            return False
    
    def install_python_dependencies(self):
        """Installe les dépendances Python"""
        print("📦 Installation des dépendances Python...")
        
        # Liste des packages requis
        packages = [
            "numpy>=1.21.0",
            "opencv-python>=4.5.0",
            "pytesseract>=0.3.8",
            "pillow>=8.0.0",
            "customtkinter>=5.0.0",
            "mss>=6.1.0",
            "psutil>=5.8.0",
            "pyyaml>=6.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "scipy>=1.7.0",
            "numba>=0.56.0"
        ]
        
        try:
            # Mise à jour pip
            print("⬆️ Mise à jour pip...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            
            # Installation des packages
            for package in packages:
                print(f"📥 Installation {package}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True)
            
            print("✅ Toutes les dépendances Python installées")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur installation dépendances: {e}")
            return False
    
    def setup_directories(self):
        """Crée les répertoires nécessaires"""
        print("📁 Création des répertoires...")
        
        directories = [
            "logs",
            "config",
            "attached_assets/generated_images",
            "exports"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory}/")
        
        return True
    
    def configure_tesseract_path(self):
        """Configure le chemin Tesseract pour pytesseract"""
        print("⚙️ Configuration Tesseract...")
        
        try:
            import pytesseract
            
            # Tentative de détection automatique
            if self.system == "windows":
                possible_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getlogin())
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        print(f"✅ Tesseract configuré: {path}")
                        return True
            
            # Test avec le PATH par défaut
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Tesseract accessible via PATH")
                return True
            
            print("⚠️ Tesseract peut nécessiter une configuration manuelle")
            return True
            
        except ImportError:
            print("⚠️ pytesseract non encore installé")
            return True
        except Exception as e:
            print(f"⚠️ Configuration Tesseract: {e}")
            return True
    
    def test_installation(self):
        """Test l'installation complète"""
        print("🧪 Test de l'installation...")
        
        try:
            # Test imports Python
            import numpy
            import cv2
            import pytesseract
            from PIL import Image
            import customtkinter
            import mss
            import psutil
            import yaml
            
            print("✅ Tous les modules Python importés")
            
            # Test Tesseract
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract {version} fonctionnel")
            
            # Test création image simple
            test_img = Image.new('RGB', (100, 50), 'white')
            text = pytesseract.image_to_string(test_img)
            print("✅ OCR Tesseract opérationnel")
            
            # Test capture écran
            with mss.mss() as sct:
                screenshot = sct.grab({"top": 0, "left": 0, "width": 100, "height": 100})
                print("✅ Capture d'écran fonctionnelle")
            
            print("🎉 Installation validée avec succès!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur test installation: {e}")
            return False
    
    def create_shortcuts(self):
        """Crée les raccourcis de lancement"""
        print("🔗 Création des raccourcis...")
        
        # Script de lancement principal
        launcher_content = f'''#!/usr/bin/env python3
"""Lanceur RTPA Studio"""
import sys
import os

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Lancement interface graphique
if __name__ == "__main__":
    try:
        from main_gui import main
        main()
    except Exception as e:
        print(f"Erreur lancement RTPA Studio: {{e}}")
        input("Appuyez sur Entrée pour fermer...")
'''
        
        with open("rtpa_studio.py", "w", encoding="utf-8") as f:
            f.write(launcher_content)
        
        # Rendre exécutable sur Unix
        if self.system in ["linux", "darwin"]:
            os.chmod("rtpa_studio.py", 0o755)
        
        print("✅ Lanceur rtpa_studio.py créé")
        return True
    
    def show_final_instructions(self):
        """Affiche les instructions finales"""
        print()
        print("🎉 INSTALLATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 45)
        print()
        print("🚀 LANCEMENT DU LOGICIEL:")
        print("   python rtpa_studio.py          # Interface graphique complète")
        print("   python main_gui.py             # Interface graphique")
        print("   python main_headless.py        # Mode démo console")
        print("   python test_final.py           # Tests complets")
        print()
        print("📋 CALIBRAGE INITIAL:")
        print("   1. Lancez votre client poker (PokerStars, Winamax, PMU)")
        print("   2. Ouvrez une table de poker")
        print("   3. Lancez RTPA Studio")
        print("   4. Utilisez l'outil de calibrage pour ajuster les zones OCR")
        print()
        print("⚙️ CONFIGURATION:")
        print("   • config/settings.yaml - Paramètres généraux")
        print("   • Onglet 'Configuration' - Zones OCR et clients poker")
        print("   • Onglet 'Performance' - Optimisations système")
        print()
        print("⚠️  IMPORTANT:")
        print("   • Usage strictement éducatif et de recherche")
        print("   • Respectez les conditions d'utilisation des plateformes")
        print("   • Aucune injection de code dans les clients poker")
        print("   • Lecture passive uniquement via OCR")
        print()
        print("📚 DOCUMENTATION:")
        print("   • README.md - Guide complet d'utilisation")
        print("   • logs/ - Fichiers de logs pour debug")
        print("   • exports/ - Données exportées")
        print()
    
    def run_installation(self):
        """Lance l'installation complète"""
        self.print_header()
        
        success = True
        
        # Vérifications préalables
        if not self.check_python_version():
            return False
        
        # Installation Tesseract
        if not self.install_tesseract():
            success = False
            self.errors.append("Installation Tesseract échouée")
        
        # Installation dépendances Python
        if not self.install_python_dependencies():
            success = False
            self.errors.append("Installation dépendances Python échouée")
        
        # Configuration
        self.setup_directories()
        self.configure_tesseract_path()
        
        # Test final
        if success and not self.test_installation():
            success = False
            self.errors.append("Tests de validation échoués")
        
        # Finalisation
        if success:
            self.create_shortcuts()
            self.show_final_instructions()
        else:
            print("❌ INSTALLATION INCOMPLÈTE")
            print("Erreurs rencontrées:")
            for error in self.errors:
                print(f"   • {error}")
        
        return success

if __name__ == "__main__":
    installer = RTAPInstaller()
    installer.run_installation()