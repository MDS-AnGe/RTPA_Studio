#!/usr/bin/env python3
"""
Script d'installation PyTorch avec support GPU/CUDA
Optimise automatiquement la configuration pour les meilleures performances
"""

import subprocess
import sys
import platform

def check_gpu_support():
    """Vérifie la disponibilité GPU/CUDA"""
    try:
        # Vérifier NVIDIA-SMI
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ GPU NVIDIA détecté")
            return True
        else:
            print("❌ Aucun GPU NVIDIA détecté")
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi non trouvé - Pas de GPU NVIDIA")
        return False

def install_pytorch_gpu():
    """Installe PyTorch avec support CUDA"""
    print("🔥 Installation PyTorch avec support GPU...")
    
    # Commande d'installation PyTorch avec CUDA
    install_cmd = [
        sys.executable, "-m", "pip", "install", "--upgrade",
        "torch", "torchvision", "torchaudio",
        "--index-url", "https://download.pytorch.org/whl/cu121"  # CUDA 12.1
    ]
    
    try:
        result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print("✅ PyTorch GPU installé avec succès!")
            return True
        else:
            print(f"❌ Erreur installation: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout installation - Connexion trop lente")
        return False

def install_pytorch_cpu():
    """Installe PyTorch optimisé CPU"""
    print("⚡ Installation PyTorch optimisé CPU...")
    
    install_cmd = [
        sys.executable, "-m", "pip", "install", "--upgrade",
        "torch", "torchvision", "torchaudio",
        "--index-url", "https://download.pytorch.org/whl/cpu"
    ]
    
    try:
        result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print("✅ PyTorch CPU optimisé installé!")
            return True
        else:
            print(f"❌ Erreur installation: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout installation")
        return False

def test_pytorch():
    """Test PyTorch et GPU"""
    try:
        import torch
        print(f"📦 PyTorch version: {torch.__version__}")
        print(f"🔥 CUDA disponible: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"🎯 GPU détecté: {torch.cuda.get_device_name(0)}")
            print(f"💾 Mémoire GPU: {torch.cuda.get_device_properties(0).total_memory // 1024**2} MB")
        else:
            print("⚡ Mode CPU optimisé activé")
        
        # Test de calcul
        x = torch.randn(1000, 1000)
        if torch.cuda.is_available():
            x = x.cuda()
            print("✅ Test GPU réussi")
        else:
            print("✅ Test CPU réussi")
        
        return True
    except Exception as e:
        print(f"❌ Erreur test PyTorch: {e}")
        return False

def main():
    """Installation principale"""
    print("🚀 RTPA Studio - Optimisation GPU/CPU")
    print("=" * 50)
    
    # Vérifier support GPU
    has_gpu = check_gpu_support()
    
    if has_gpu:
        success = install_pytorch_gpu()
        if not success:
            print("🔄 Fallback vers version CPU...")
            success = install_pytorch_cpu()
    else:
        success = install_pytorch_cpu()
    
    if success:
        print("\n🧪 Test de l'installation...")
        test_pytorch()
        print("\n✅ Installation terminée!")
        print("💡 Redémarrez RTPA Studio pour utiliser la nouvelle configuration")
    else:
        print("\n❌ Installation échouée")
        sys.exit(1)

if __name__ == "__main__":
    main()