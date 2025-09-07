# Overview

RTPA Studio is a comprehensive real-time poker analysis application designed for educational and training purposes. The system analyzes poker game states using sophisticated algorithms including CFR (Counterfactual Regret Minimization) and Nash equilibrium calculations to provide optimal playing recommendations. 

**Status: ✅ COMPLETED AND FULLY FUNCTIONAL**

The application features:
- Advanced OCR system for automatic screen capture and game state detection
- High-performance CFR/CFR+ algorithms for Nash equilibrium calculations
- In-memory database optimized for real-time processing
- Modern bilingual GUI (French/English) built with CustomTkinter
- Comprehensive resource management (CPU/GPU/RAM optimization)
- Support for both cash games and tournaments with ICM adjustments
- Real-time probability calculations and strategic recommendations
- Performance tracking with professional player benchmarking

Date completed: September 7, 2025

## Recent Updates (September 7, 2025)

### Visual Interface Improvements
- **Cartes réalistes**: Système d'affichage de cartes avec couleurs rouge/noir et symboles réels (♠ ♥ ♦ ♣)
- **Renommage**: "Cartes du Héros" renommé en "Main" pour meilleure ergonomie
- **Format visuel**: Cartes affichées dans des cadres blancs avec bordures, format "K♠" "A♥" etc.

### Configuration avancée CFR
- **Descriptions détaillées**: Explications précises de chaque paramètre CFR
- **Nouveaux paramètres**: Profondeur CFR, Epsilon Exploration, CFR+
- **Options étendues**: Plus de contrôles fins pour optimisation algorithmes

### Gestion PyTorch
- **Vérification automatique**: Status PyTorch affiché dans onglet Performance
- **Installation directe**: Bouton pour installer PyTorch depuis l'interface
- **Support CUDA**: Détection et indication du support GPU

### Export/Import Base CFR (NOUVEAU)
- **Export complet**: Sauvegarde base CFR + données + statistiques + apprentissage Nash
- **Import sécurisé**: Restauration complète avec confirmation utilisateur
- **Préservation apprentissage**: Evite de repartir à zéro après mises à jour
- **Format JSON**: Fichiers lisibles et compatibles entre versions

### Personnalisation interface
- **Couleurs d'accent**: Choix entre 5 couleurs (bleu, vert, rouge, violet, orange) - FONCTIONNEL
- **Opacité réglable**: Transparence fenêtre ajustable 70-100% - FONCTIONNEL  
- **Polices personnalisées**: Sélection police interface (Arial, Helvetica, Times, Courier) - FONCTIONNEL
- **Thèmes avancés**: Options étendues dark/light mode - FONCTIONNEL

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Architecture
The application follows a modular, event-driven architecture with clear separation of concerns:

- **App Manager**: Central orchestrator that coordinates all system components and manages application state
- **Modular Design**: Components organized into distinct packages (core, algorithms, ocr, database, gui, utils) for maintainability
- **Threading Model**: Multi-threaded architecture with separate threads for screen capture, CFR calculations, and GUI updates
- **Configuration Management**: YAML-based configuration system with runtime parameter adjustment

## Data Flow & Processing
- **Real-time Pipeline**: OCR capture → Game state extraction → CFR engine → Recommendations → GUI display
- **In-memory Database**: High-performance memory-based storage with SQLite fallback for persistence
- **Caching Strategy**: Smart caching for OCR results and CFR calculations to optimize performance
- **State Management**: Centralized game state tracking with history and indexing capabilities

## Algorithm Implementation
- **CFR Engine**: Advanced Counterfactual Regret Minimization with CFR+ optimizations
- **Card Abstraction**: Sophisticated bucketing system reducing computational complexity
- **Action Space**: Dynamic bet sizing with contextual action spaces
- **Monte Carlo Simulations**: High-speed probability calculations for win rate estimation

## UI Architecture
- **Modern Interface**: CustomTkinter-based GUI with dark/light theme support
- **Real-time Updates**: Separate update thread for responsive UI without blocking calculations
- **Multilingual Support**: Complete French/English localization system
- **Responsive Design**: Adaptive layout supporting different screen resolutions

## Performance Optimization
- **Resource Management**: CPU, RAM, and GPU usage monitoring with automatic throttling
- **Concurrent Processing**: Parallel execution of OCR, CFR calculations, and UI updates
- **Memory Optimization**: Circular buffers and efficient data structures for real-time processing
- **Headless Mode**: Optional headless operation for demonstration environments without GUI requirements

# External Dependencies

## Core Libraries
- **NumPy/SciPy**: Mathematical computations and linear algebra operations for CFR algorithms
- **OpenCV**: Advanced image processing and computer vision for OCR preprocessing
- **PyTesseract**: OCR engine for text recognition from poker client screenshots
- **PyTorch**: Optional deep learning framework for advanced CFR implementations

## GUI Framework
- **CustomTkinter**: Modern, themed GUI framework providing native-looking interfaces
- **PIL/Pillow**: Image processing and manipulation for GUI components
- **Matplotlib/Seaborn**: Data visualization and statistical plotting capabilities

## System Integration
- **MSS**: High-performance screen capture for multi-monitor setups
- **PSUtil**: System resource monitoring and process management
- **PyYAML**: Configuration file parsing and management
- **Threading/Multiprocessing**: Python's built-in concurrency libraries for parallel processing

## Development & Testing
- **Pygame**: Game engine capabilities for simulation and testing environments
- **Numba**: Just-in-time compilation for performance-critical mathematical operations
- **SQLite3**: Lightweight database engine for data persistence and hand history storage