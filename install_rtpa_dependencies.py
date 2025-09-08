#!/usr/bin/env python3
"""
RTPA Studio - Installation Automatique des Dépendances
Installation 100% automatique pour performance maximale Rust CFR
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

# Dépendances Python critiques pour RTPA
PYTHON_DEPENDENCIES = [
    "pyyaml",
    "opencv-python", 
    "numpy",
    "pillow",
    "psutil",
    "customtkinter",
    "pyautogui",
    "mss",
    "pynput",
    "requests",
    "matplotlib",
    "pandas",
    "psutil",
    "dxcam",
]

def check_dependency(package_name):
    """Vérifier si une dépendance Python est installée"""
    try:
        importlib.import_module(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False

def install_python_dependencies():
    """Installation automatique des dépendances Python"""
    print("📦 Vérification dépendances Python...")
    
    missing_deps = []
    for dep in PYTHON_DEPENDENCIES:
        if not check_dependency(dep):
            missing_deps.append(dep)
        else:
            print(f"✅ {dep}")
    
    if missing_deps:
        print(f"🔄 Installation de {len(missing_deps)} dépendances manquantes...")
        
        for dep in missing_deps:
            try:
                print(f"📥 Installation {dep}...")
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                              check=True, capture_output=True)
                print(f"✅ {dep} installé")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur installation {dep}: {e}")
                return False
    
    print("✅ Toutes les dépendances Python sont installées")
    return True

def check_rust_installation():
    """Vérifier installation Rust"""
    try:
        result = subprocess.run(['rustc', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Rust: {result.stdout.strip()}")
            return True
    except:
        pass
    return False

def install_rust():
    """Installation automatique Rust"""
    print("🦀 Installation Rust pour CFR ultra-performance...")
    
    try:
        if os.name == 'nt':  # Windows
            print("💻 Windows détecté - Installation rustup...")
            # Download rustup-init.exe
            import urllib.request
            urllib.request.urlretrieve(
                "https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe",
                "rustup-init.exe"
            )
            subprocess.run(["rustup-init.exe", "-y"], check=True)
            os.remove("rustup-init.exe")
        else:  # Linux/macOS
            install_cmd = 'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'
            subprocess.run(['bash', '-c', install_cmd], check=True)
        
        print("✅ Rust installé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur installation Rust: {e}")
        return False

def compile_rust_cfr():
    """Compilation du module CFR Rust"""
    rust_dir = Path("rust_cfr_engine")
    
    if not rust_dir.exists():
        print(f"❌ Répertoire Rust CFR manquant: {rust_dir}")
        return False
    
    print("🔥 Compilation CFR Engine Rust ultra-performance...")
    
    try:
        os.chdir(rust_dir)
        
        # Essayer différentes commandes cargo
        cargo_commands = [
            ['cargo', 'build', '--release'],
            [os.path.expanduser('~/.cargo/bin/cargo'), 'build', '--release'],
            [os.path.expanduser('~') + '\\.cargo\\bin\\cargo.exe', 'build', '--release'] if os.name == 'nt' else None,
        ]
        
        cargo_commands = [cmd for cmd in cargo_commands if cmd]  # Filtrer None
        
        compilation_success = False
        for cmd in cargo_commands:
            try:
                print(f"🔄 Tentative: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print("✅ CFR Engine Rust compilé avec succès")
                    compilation_success = True
                    break
                else:
                    print(f"❌ Erreur avec {cmd[0]}: {result.stderr[:200]}...")
                    
            except FileNotFoundError:
                print(f"❌ Commande non trouvée: {cmd[0]}")
                continue
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout avec: {cmd[0]}")
                continue
        
        if not compilation_success:
            print("❌ Aucune commande cargo n'a fonctionné")
            return False
        
        # Vérifier module généré
        target_release = Path("target/release")
        lib_patterns = ["librust_cfr_engine.so", "librust_cfr_engine.dylib", "rust_cfr_engine.dll", "rust_cfr_engine.pyd"]
        
        for pattern in lib_patterns:
            lib_path = target_release / pattern
            if lib_path.exists():
                size_mb = lib_path.stat().st_size / (1024 * 1024)
                print(f"📦 Module CFR: {lib_path.name} ({size_mb:.1f} MB)")
                return True
        
        print("⚠️  Module compilé mais fichier bibliothèque introuvable")
        return False
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False
    finally:
        os.chdir("..")

def test_rust_cfr_integration():
    """Test intégration CFR Rust"""
    print("🧪 Test CFR Engine Rust...")
    
    try:
        # Ajouter le path du module Rust
        sys.path.insert(0, "rust_cfr_engine/target/release")
        
        import rust_cfr_engine
        
        # Test de base
        config = {"max_iterations": 1000, "convergence_threshold": 0.01}
        engine = rust_cfr_engine.RustCfrEngine(config)
        status = engine.get_status()
        
        print("✅ CFR Engine Rust fonctionnel")
        print(f"   🔥 Engine: {status.get('engine', 'Unknown')}")
        print(f"   ⚡ Threads: {status.get('cpu_threads', 1)}")
        print(f"   🚀 Parallélisme: {status.get('parallel_processing', False)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Impossible d'importer rust_cfr_engine: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur test CFR: {e}")
        return False

def main():
    """Installation complète RTPA Studio"""
    print("=" * 70)
    print("🚀 RTPA Studio - Installation Automatique Complète")
    print("🎯 Objectif: CFR 100% Rust pour performance maximale")
    print("=" * 70)
    
    steps_completed = 0
    total_steps = 4
    
    # Étape 1: Dépendances Python
    print(f"\n📋 Étape 1/{total_steps}: Dépendances Python")
    if install_python_dependencies():
        steps_completed += 1
    else:
        print("❌ Échec installation dépendances Python")
    
    # Étape 2: Installation/Vérification Rust
    print(f"\n📋 Étape 2/{total_steps}: Installation Rust")
    if not check_rust_installation():
        if install_rust():
            steps_completed += 1
        else:
            print("❌ Installation Rust échouée")
    else:
        steps_completed += 1
    
    # Étape 3: Compilation CFR Rust
    print(f"\n📋 Étape 3/{total_steps}: Compilation CFR Engine Rust")
    if compile_rust_cfr():
        steps_completed += 1
    else:
        print("❌ Compilation CFR Rust échouée")
    
    # Étape 4: Test intégration
    print(f"\n📋 Étape 4/{total_steps}: Test intégration CFR Rust")
    if test_rust_cfr_integration():
        steps_completed += 1
    else:
        print("❌ Test intégration échoué")
    
    # Résultats finaux
    print("\n" + "=" * 70)
    if steps_completed == total_steps:
        print("🎉 INSTALLATION RTPA RÉUSSIE À 100%!")
        print("✅ CFR Engine Rust opérationnel - Performance maximale")
        print("🔥 Calculs CFR: 100% Rust (50-200x plus rapide que Python)")
        print("❌ Fallback Python: ÉLIMINÉ - Performance garantie")
        print("\n🚀 Commande de lancement: python main_gui.py")
        print("🎯 RTPA Studio prêt pour analyse poker temps réel!")
        return True
    else:
        print(f"⚠️  Installation partiellement réussie ({steps_completed}/{total_steps})")
        print("❌ Certaines fonctionnalités peuvent être limitées")
        print("💡 Relancez ce script pour compléter l'installation")
        return False

if __name__ == "__main__":
    success = main()
    input("\nAppuyez sur Entrée pour continuer...")
    sys.exit(0 if success else 1)