#!/usr/bin/env python3
"""
RTPA Studio v2.0.0 - Script d'Installation et Lancement Unique
Vérification, installation et lancement automatique complet
Compatible Windows/Linux/macOS avec détection matérielle
"""

import sys
import os
import subprocess
import platform
import shutil
import logging
from pathlib import Path

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class RTPAInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.python_version = sys.version_info
        self.build_dir = Path("build")
        self.src_dir = Path("src")
        self.executable_name = "rtpa_studio"
        
        if self.system == "windows":
            self.executable_name += ".exe"
            
        print("🚀 RTPA Studio v2.0.0 - Installation et Lancement Unique")
        print(f"   🖥️  Système: {platform.system()} {platform.release()}")
        print(f"   🐍 Python: {sys.version.split()[0]}")
        print()

    def check_python_requirements(self):
        """Vérification version Python minimum"""
        if self.python_version < (3, 8):
            logger.error("❌ Python 3.8+ requis (détecté: {}.{})".format(
                self.python_version.major, self.python_version.minor))
            return False
        
        logger.info("✅ Version Python compatible")
        return True

    def detect_system_dependencies(self):
        """Détection et installation dépendances système"""
        logger.info("🔍 Détection dépendances système...")
        
        required_libs = []
        
        if self.system == "linux":
            # Dépendances Ubuntu/Debian
            required_libs = [
                "build-essential", "cmake", "qt6-base-dev", 
                "libopencv-dev", "libtesseract-dev", "pkg-config"
            ]
            install_cmd = ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y"] + required_libs
            
        elif self.system == "windows":
            # Windows - vérifier vcpkg ou installer via scoop/chocolatey
            logger.info("🏠 Windows détecté - vérification outils de développement...")
            if not self.check_windows_build_tools():
                return False
                
        elif self.system == "darwin":  # macOS
            # macOS - Homebrew
            required_libs = ["cmake", "qt6", "opencv", "tesseract", "pkg-config"]
            if not shutil.which("brew"):
                logger.error("❌ Homebrew requis sur macOS")
                return False
            install_cmd = ["brew", "install"] + required_libs
        
        if required_libs and self.system != "windows":
            logger.info(f"📦 Installation dépendances: {', '.join(required_libs)}")
            try:
                if self.system == "linux":
                    subprocess.run(["sudo", "apt", "update"], check=True)
                    subprocess.run(["sudo", "apt", "install", "-y"] + required_libs, check=True)
                elif self.system == "darwin":
                    subprocess.run(["brew", "install"] + required_libs, check=True)
                    
                logger.info("✅ Dépendances système installées")
                return True
                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Erreur installation dépendances: {e}")
                return False
        
        return True

    def check_windows_build_tools(self):
        """Vérification outils build Windows"""
        tools_needed = []
        
        # Visual Studio Build Tools
        if not self.find_msvc():
            tools_needed.append("Visual Studio Build Tools")
            
        # CMake
        if not shutil.which("cmake"):
            tools_needed.append("CMake")
            
        if tools_needed:
            logger.warning(f"⚠️  Outils manquants: {', '.join(tools_needed)}")
            logger.info("📋 Installation recommandée:")
            logger.info("   1. Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/")
            logger.info("   2. CMake: https://cmake.org/download/")
            logger.info("   3. vcpkg pour Qt6/OpenCV: https://vcpkg.io/")
            
            response = input("Continuer sans ces outils? (y/N): ").lower()
            return response == 'y'
            
        return True

    def find_msvc(self):
        """Recherche Visual Studio Build Tools"""
        vs_paths = [
            "C:\\Program Files\\Microsoft Visual Studio\\2022\\BuildTools",
            "C:\\Program Files\\Microsoft Visual Studio\\2019\\BuildTools",
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools"
        ]
        
        for path in vs_paths:
            if os.path.exists(path):
                return True
        return False

    def verify_source_code(self):
        """Vérification intégrité code source"""
        logger.info("📁 Vérification code source...")
        
        required_files = [
            "CMakeLists.txt",
            "src/main.cpp", 
            "src/core/AppManager.h",
            "src/core/ConfigManager.h",
            "src/algorithms/CfrEngine.h",
            "src/gui/MainWindow.h",
            "src/utils/HardwareDetector.h"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            logger.error(f"❌ Fichiers source manquants: {missing_files}")
            return False
            
        logger.info("✅ Code source complet")
        return True

    def build_application(self):
        """Build CMake de l'application"""
        logger.info("🔨 Compilation RTPA Studio...")
        
        # Création dossier build
        self.build_dir.mkdir(exist_ok=True)
        
        try:
            # Configuration CMake
            cmake_args = [
                "cmake", "..", 
                "-DCMAKE_BUILD_TYPE=Release",
                "-DENABLE_OPTIMIZATIONS=ON"
            ]
            
            if self.system == "windows":
                cmake_args.extend(["-A", "x64"])
                
            subprocess.run(cmake_args, cwd=self.build_dir, check=True)
            
            # Build
            build_args = ["cmake", "--build", ".", "--config", "Release"]
            if self.system != "windows":
                build_args.extend(["-j", str(os.cpu_count() or 4)])
                
            subprocess.run(build_args, cwd=self.build_dir, check=True)
            
            # Vérification exécutable
            executable_path = self.build_dir / self.executable_name
            if not executable_path.exists():
                # Recherche dans Release/ pour Windows
                executable_path = self.build_dir / "Release" / self.executable_name
                
            if executable_path.exists():
                logger.info("✅ Compilation réussie")
                return True
            else:
                logger.error("❌ Exécutable non trouvé après build")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erreur compilation: {e}")
            return False

    def run_hardware_detection_test(self):
        """Test rapide détection matérielle"""
        logger.info("🔧 Test détection matérielle...")
        
        try:
            # Test basique de détection
            cpu_count = os.cpu_count()
            logger.info(f"  CPU: {cpu_count} cœurs détectés")
            
            # Vérification mémoire (approximative)
            if self.system == "linux":
                try:
                    with open('/proc/meminfo', 'r') as f:
                        for line in f:
                            if 'MemTotal:' in line:
                                mem_kb = int(line.split()[1])
                                mem_gb = mem_kb / (1024 * 1024)
                                logger.info(f"  RAM: {mem_gb:.1f} GB détectée")
                                break
                except:
                    pass
                    
            logger.info("✅ Détection matérielle basique fonctionnelle")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Test matériel partiel: {e}")
            return True  # Non-bloquant

    def launch_application(self):
        """Lancement de l'application"""
        logger.info("🚀 Lancement RTPA Studio...")
        
        executable_path = self.build_dir / self.executable_name
        if not executable_path.exists():
            executable_path = self.build_dir / "Release" / self.executable_name
            
        if not executable_path.exists():
            logger.error("❌ Exécutable RTPA Studio non trouvé")
            return False
            
        try:
            print()
            print("=" * 50)
            print("🎯 RTPA Studio v2.0.0 - Lancement")
            print("   ⚡ Performance: Calculs natifs C++20 ultra-rapides")
            print("   🎨 Interface: Qt6 moderne avec adaptation matérielle")
            print("   👁️  OCR: OpenCV+Tesseract temps réel uniquement")
            print("   🔧 Configuration: Automatique selon votre matériel")
            print("=" * 50)
            print()
            
            # Lancement en mode non-bloquant
            if self.system == "windows":
                os.startfile(str(executable_path))
            else:
                subprocess.Popen([str(executable_path)])
                
            logger.info("✅ RTPA Studio lancé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lancement: {e}")
            return False

    def cleanup_old_builds(self):
        """Nettoyage anciens builds"""
        if self.build_dir.exists():
            logger.info("🧹 Nettoyage ancien build...")
            try:
                shutil.rmtree(self.build_dir)
                logger.info("✅ Build directory nettoyé")
            except Exception as e:
                logger.warning(f"⚠️  Nettoyage partiel: {e}")

    def install_and_run(self):
        """Processus complet d'installation et lancement"""
        print("🏁 Démarrage processus d'installation RTPA Studio v2.0.0")
        print()
        
        steps = [
            ("Vérification Python", self.check_python_requirements),
            ("Vérification code source", self.verify_source_code),  
            ("Installation dépendances système", self.detect_system_dependencies),
            ("Nettoyage builds précédents", self.cleanup_old_builds),
            ("Compilation application", self.build_application),
            ("Test détection matérielle", self.run_hardware_detection_test),
            ("Lancement application", self.launch_application)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            if not step_func():
                logger.error(f"❌ Échec: {step_name}")
                return False
            print()
            
        print("🎉 INSTALLATION ET LANCEMENT TERMINÉS AVEC SUCCÈS !")
        print()
        print("📖 RTPA Studio v2.0.0 est maintenant actif:")
        print("   • Détection automatique de votre matériel")
        print("   • Configuration optimisée pour vos performances")
        print("   • Mode temps réel uniquement (pas de simulation)")
        print("   • Interface Qt6 moderne et responsive")
        print()
        print("🎯 L'application s'adapte automatiquement à votre configuration !")
        
        return True

def main():
    """Point d'entrée principal"""
    installer = RTPAInstaller()
    
    try:
        success = installer.install_and_run()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Installation interrompue par l'utilisateur")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"💥 Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()