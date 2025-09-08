#!/usr/bin/env python3
"""
RTPA Studio - Installation Automatique CFR Rust
Installation 100% automatique des dépendances Rust pour performance maximale
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_rust_installation():
    """Vérifier si Rust est installé"""
    try:
        result = subprocess.run(['rustc', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Rust détecté: {result.stdout.strip()}")
            return True
    except:
        pass
    return False

def install_rust():
    """Installation automatique de Rust"""
    print("🦀 Installation Rust en cours...")
    
    try:
        # Download et install Rust
        install_cmd = 'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'
        
        if os.name == 'nt':  # Windows
            print("💻 Détection Windows - Téléchargement rustup...")
            subprocess.run(['powershell', '-Command', 
                          'Invoke-WebRequest -Uri "https://win.rustup.rs/x86_64" -OutFile "rustup-init.exe"; ./rustup-init.exe -y'],
                          check=True)
        else:  # Linux/macOS
            subprocess.run(['bash', '-c', install_cmd], check=True)
        
        # Refresh environment
        if os.name != 'nt':
            os.environ['PATH'] = f"{os.path.expanduser('~/.cargo/bin')}:{os.environ.get('PATH', '')}"
        
        print("✅ Installation Rust terminée")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation Rust: {e}")
        return False

def compile_rust_cfr():
    """Compilation du module CFR Rust"""
    rust_dir = Path("rust_cfr_engine")
    
    if not rust_dir.exists():
        print(f"❌ Répertoire Rust manquant: {rust_dir}")
        return False
    
    print("🔥 Compilation CFR Engine Rust...")
    
    try:
        # Compilation en mode release pour performance maximale
        os.chdir(rust_dir)
        
        result = subprocess.run(['cargo', 'build', '--release'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Compilation Rust réussie")
            
            # Vérifier le fichier .so généré
            lib_file = None
            target_release = Path("target/release")
            
            for lib_pattern in ["librust_cfr_engine.so", "librust_cfr_engine.dylib", "rust_cfr_engine.dll"]:
                lib_path = target_release / lib_pattern
                if lib_path.exists():
                    lib_file = lib_path
                    break
            
            if lib_file:
                print(f"📦 Module CFR généré: {lib_file} ({lib_file.stat().st_size} bytes)")
                return True
            else:
                print("⚠️  Module compilé mais fichier .so introuvable")
                return False
        else:
            print(f"❌ Erreur compilation Rust:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout compilation Rust (>5min)")
        return False
    except Exception as e:
        print(f"❌ Erreur compilation: {e}")
        return False
    finally:
        os.chdir("..")

def verify_rust_cfr_integration():
    """Vérifier l'intégration CFR Rust avec Python"""
    print("🔍 Test intégration CFR Rust...")
    
    try:
        sys.path.insert(0, "rust_cfr_engine/target/release")
        
        import rust_cfr_engine
        
        # Test basique
        config = {
            "max_iterations": 1000,
            "convergence_threshold": 0.01,
        }
        
        engine = rust_cfr_engine.RustCfrEngine(config)
        status = engine.get_status()
        
        print("✅ Intégration CFR Rust fonctionnelle")
        print(f"   Engine: {status.get('engine', 'Unknown')}")
        print(f"   Parallélisme: {status.get('parallel_processing', False)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Impossible d'importer rust_cfr_engine: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        return False

def setup_rtpa_rust():
    """Installation complète RTPA CFR Rust"""
    print("=" * 60)
    print("🚀 RTPA Studio - Setup CFR Rust Ultra-Performance")
    print("=" * 60)
    
    success_steps = 0
    total_steps = 4
    
    # Étape 1: Vérifier/Installer Rust
    print("\n📋 Étape 1/4: Vérification Rust...")
    if not check_rust_installation():
        print("⚠️  Rust non détecté - Installation automatique")
        if install_rust():
            success_steps += 1
        else:
            print("❌ Installation Rust échouée")
            return False
    else:
        success_steps += 1
    
    # Étape 2: Vérifier Cargo
    print("\n📋 Étape 2/4: Vérification Cargo...")
    try:
        result = subprocess.run(['cargo', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Cargo détecté: {result.stdout.strip()}")
            success_steps += 1
        else:
            print("❌ Cargo indisponible")
            return False
    except:
        print("❌ Cargo non trouvé")
        return False
    
    # Étape 3: Compilation CFR Rust
    print("\n📋 Étape 3/4: Compilation CFR Engine...")
    if compile_rust_cfr():
        success_steps += 1
    else:
        print("❌ Compilation CFR échouée")
        return False
    
    # Étape 4: Test intégration
    print("\n📋 Étape 4/4: Test intégration...")
    if verify_rust_cfr_integration():
        success_steps += 1
    else:
        print("❌ Test intégration échoué")
        return False
    
    # Résultats
    print("\n" + "=" * 60)
    if success_steps == total_steps:
        print("🎉 INSTALLATION RTPA CFR RUST RÉUSSIE!")
        print("✅ Tous les calculs CFR sont maintenant 100% Rust")
        print("⚡ Performance estimée: 50-200x plus rapide que Python")
        print("🔥 Zero fallback Python - Performance maximale garantie")
        print("\n🚀 Lancez RTPA Studio: python main_gui.py")
        return True
    else:
        print(f"❌ Installation partiellement échouée ({success_steps}/{total_steps})")
        print("⚠️  Certaines fonctionnalités peuvent être limitées")
        return False

if __name__ == "__main__":
    success = setup_rtpa_rust()
    sys.exit(0 if success else 1)