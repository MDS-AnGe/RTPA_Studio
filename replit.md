# RTPA Studio - Real-Time Poker Assistant

## Overview
RTPA Studio is an advanced poker analysis system designed for education and training. It combines traditional CFR algorithms with Deep CFR neural networks to provide optimal strategic recommendations in real-time. The system leverages Nash equilibrium to offer mathematically sound game advice, aiming to improve user poker skills through continuous learning and sophisticated analysis.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
The application features a modular, event-driven architecture. An `App Manager` orchestrates system components, which are organized into distinct packages (core, algorithms, ocr, database, gui, utils). It employs a multi-threaded model for screen capture, CFR calculations, and GUI updates, and uses a YAML-based configuration system for runtime parameter adjustment.

### Data Flow & Processing
A real-time pipeline handles OCR capture, game state extraction, CFR engine processing, recommendations generation, and GUI display. It utilizes an in-memory database for high performance, with SQLite as a fallback for persistence. Smart caching optimizes OCR results and CFR calculations, while centralized state management tracks game history.

### Algorithm Implementation
The core algorithm is an advanced Counterfactual Regret Minimization (CFR) engine with CFR+ optimizations. It includes sophisticated card abstraction for computational efficiency, dynamic bet sizing, and contextual action spaces. High-speed Monte Carlo simulations are used for win rate estimations.

### UI Architecture
The UI is built with `CustomTkinter` for a modern, themed look with dark/light mode support. It features real-time updates via a dedicated thread for responsiveness, complete French/English localization, and an adaptive layout for various screen resolutions. The visual display includes realistic poker cards with accurate symbols.

### Performance Optimization
The system includes robust resource management, monitoring CPU, RAM, and GPU usage with automatic throttling. It leverages concurrent processing for OCR, CFR, and UI updates, and optimizes memory with efficient data structures. A headless mode is available for non-GUI environments. The system dynamically switches between CPU and GPU based on workload, utilizing CUDA for GPU acceleration.

### Feature Specifications
- **Hybrid AI**: Combines CFR and Deep CFR Neural Networks (PyTorch) for strategic analysis.
- **Automatic Detection**: Monitors and automatically launches/pauses with poker platforms (PokerStars, Winamax, PMU).
- **Advanced OCR**: Captures screenshots and recognizes game states automatically.
- **Continuous Learning**: Perpetually improves strategies 24/7 by generating and integrating 450 hands/minute.
- **Nash Recommendations**: Provides optimal actions based on game theory.
- **GPU Acceleration**: Utilizes CUDA for massive parallel computations.
- **In-Memory Database**: High-performance storage with SQLite fallback.
- **Intelligent Caching**: Optimizes equity calculations and card abstractions.
- **Real-time Probabilities**: Monte Carlo calculations for win estimations.
- **Performance Tracking**: Compares user performance against professional play.
- **ICM Support**: Adjusts for tournament play with the Independent Chip Model.
- **Configurable CFR**: Detailed parameters for fine-tuning algorithms (Iterations, Discount Factor, Exploration Rate, Depth, Epsilon).
- **PyTorch/GPU Management**: Automatic detection, installation, and dynamic CPU/GPU switching with configurable memory limits.
- **CFR Base Export/Import**: Allows saving and restoring complete CFR data, learning, and statistics in JSON format.
- **Customizable Interface**: Adjustable accent colors, opacity, fonts, themes (dark/light), and adaptive layouts.

## External Dependencies

### Core Libraries
- **NumPy/SciPy**: Mathematical computations for CFR algorithms.
- **OpenCV**: Image processing for OCR preprocessing.
- **PyTesseract**: OCR engine for text recognition.
- **PyTorch**: Deep learning framework for advanced CFR implementations.
- **Numba**: Just-in-time compilation for performance-critical operations.

### GUI Framework
- **CustomTkinter**: GUI framework for native-looking interfaces.
- **PIL/Pillow**: Image processing for GUI components.
- **Matplotlib/Seaborn**: Data visualization and statistical plotting.

### System Integration
- **MSS**: High-performance screen capture.
- **PSUtil**: System resource monitoring.
- **PyYAML**: Configuration file parsing.
- **Threading/Multiprocessing**: Concurrency for parallel processing.

### Data Storage
- **SQLite3**: Lightweight database for data persistence and hand history.

---

## 🚀 Guide de Démarrage Rapide

### Installation Ultra-Simple
```bash
# 1. Cloner le projet
git clone <repository-url>
cd rtpa-studio

# 2. Lancement direct (installation automatique)
python main_gui.py
```

### 🎯 **Installation Automatique Intégrée**
✅ **Aucune installation manuelle requise !**
- **Premier lancement** : Les dépendances s'installent automatiquement
- **Détection intelligente** : Vérification et installation des packages manquants
- **Zéro configuration** : Prêt à l'emploi en une commande

### ⚡ Utilisation Immédiate
1. **Lancez simplement** : `python main_gui.py` ou `python test_rtpa.py`
2. **Installation auto** : Les dépendances se téléchargent automatiquement au premier lancement
3. **Ouvrez votre plateforme poker** (PokerStars, Winamax, PMU)
4. **Détection automatique** : RTPA se lance automatiquement
5. **Recommandations instantanées** : Les conseils Nash apparaissent en temps réel
6. **Amélioration continue** : Le système s'améliore pendant que vous jouez

---

## ❓ Questions Fréquentes

### Fonctionnement CFR/Nash
**Q: Quelle est la différence entre CFR et Nash ?**
📊 **CFR est l'algorithme qui calcule Nash.** CFR (Counterfactual Regret Minimization) utilise les regrets pour converger vers l'équilibre de Nash optimal. Ce n'est pas deux calculs séparés.

**Q: Puis-je utiliser RTPA pendant l'apprentissage ?**
✅ **Oui !** L'apprentissage est continu en arrière-plan (450 mains/minute). Vous pouvez jouer immédiatement et profiter des améliorations progressives. Pas besoin d'attendre !

### Configuration Technique
**Q: GPU vs CPU ?**
⚡ Le système bascule automatiquement : CPU pour petits calculs, GPU pour gros batches (50+ mains). Fallback sécurisé si GPU indisponible.

**Q: Installation PyTorch/GPU ?**
🔥 Détection automatique avec bouton d'installation directe dans l'interface. Support CUDA avec gestion mémoire intelligente.

### Troubleshooting
**🔴 Erreur 'No module named'** : Relancez le programme, l'auto-installation se déclenchera
**🔴 Installation échoue** : Vérifiez connexion internet et permissions Python
**🔴 Performance lente** : Activez GPU dans Configuration, augmentez limite mémoire
**🔴 Erreurs mémoire GPU** : Réduisez `gpu_memory_limit` à 0.6 et `batch_size` à 1000
**🔴 Détection échoue** : Vérifiez plateforme ouverte, redémarrez RTPA

### 🛠️ Commandes de Test et Lancement
```bash
# Test automatique avec installation des dépendances
python test_rtpa.py

# Interface graphique complète
python main_gui.py

# Version console/headless
python main_headless.py
```