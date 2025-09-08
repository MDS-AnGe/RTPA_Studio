# RTPA Studio - Real-Time Poker Assistant

## Recent Changes

### 2025-09-08 - Améliorations CFR inspirées de l'analyse iciamyplant/Poker_CFR
- **Analyse comparative complète** : Étude du repo éducatif iciamyplant/Poker_CFR (134⭐) vs RTPA Studio
- **Confirmation supériorité technique** : RTPA dépasse largement le repo éducatif (CFR+ vs Vanilla CFR, GPU vs CPU, Texas Hold'em vs Kuhn Poker)
- **Métriques CFR améliorées** : Ajout de calculs de convergence et qualité inspirés du style iciamyplant
- **Fonction d'inspection CFR** : `inspect_cfr_strategies()` pour debug avancé des information sets
- **Bouton Debug CFR** : Interface GUI `🔍 Debug CFR` pour visualiser métriques en temps réel
- **Optimisation affichage** : Logs CFR détaillés toutes les 1000 itérations avec convergence/qualité
- **Style educatif intégré** : Affichage des stratégies normalisées comme dans iciamyplant pour debug

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

### Automatic Dependency Management
RTPA Studio features an intelligent auto-installation system that automatically detects and installs missing dependencies at first launch. The system checks 14 critical packages (yaml, opencv, numpy, etc.), installs only what's missing, and handles installation errors with fallback mechanisms. This ensures a seamless first-time user experience with zero manual configuration required.

### Feature Specifications
- **Hybrid AI**: Combines CFR and Deep CFR Neural Networks (PyTorch) for strategic analysis.
- **Automatic Detection**: Monitors and automatically launches/pauses with poker platforms (PokerStars, Winamax, PMU).
- **Advanced OCR with Auto-Calibration**: Captures screenshots and recognizes game states with automatic platform detection and calibration.
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

### OCR Automatic Calibration System
RTPA Studio features an intelligent OCR calibration system that eliminates manual configuration:

- **Automatic Platform Detection**: Real-time monitoring of poker platforms (PokerStars, Winamax, PMU, PartyPoker)
- **Intelligent Recognition**: Analysis of active processes and window titles every 2 seconds  
- **Zero-Configuration Setup**: Automatic application of optimal OCR presets when platforms are detected
- **Smart Presets**: Pre-configured zones for hero cards, board, pot, stack, blinds, and action buttons
- **Platform Switching**: Seamless transition between different poker clients without recalibration
- **Manual Override**: Optional fine-tuning through GUI interface for custom screen configurations
- **Persistent Settings**: Automatic saving and restoration of calibration preferences
- **Multi-Resolution Support**: Optimized presets for common screen resolutions (1920x1080, 1366x768, 2560x1440)

The system monitors:
```
PokerStars: PokerStars.exe, "PokerStars" windows
Winamax:    Winamax.exe, "Winamax Poker" windows + web browsers
PMU:        PMUPoker.exe, "PMU Poker" windows  
PartyPoker: PartyPoker.exe, "PartyPoker" windows
```

Technical Implementation:
- **Detection Engine**: `src/utils/platform_detector.py` - Continuous platform monitoring
- **Preset Management**: `src/ocr/screen_capture.py` - Pre-configured OCR zones
- **Auto-Application**: `src/core/app_manager.py` - Automatic preset application on detection
- **Configuration**: `CALIBRAGE_OCR_README.md` - Complete setup and troubleshooting guide

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
**🔴 OCR imprécis** : Le calibrage automatique s'applique dès la détection de plateforme. Consultez `CALIBRAGE_OCR_README.md` pour ajustements manuels

### 🛠️ Commandes de Test et Lancement
```bash
# Test automatique avec installation des dépendances
python test_rtpa.py

# Interface graphique complète
python main_gui.py

# Version console/headless
python main_headless.py
```