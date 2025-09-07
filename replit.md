# RTPA Studio - Real-Time Poker Assistant

**Assistant Poker Temps Réel avec Intelligence Artificielle Hybride**

RTPA Studio est un système d'analyse poker avancé combinant algorithmes CFR traditionnels et réseaux de neurones Deep CFR pour des recommandations stratégiques optimales en temps réel. Conçu pour l'éducation et l'entraînement, le système utilise l'équilibre de Nash pour fournir des conseils de jeu mathématiquement parfaits.

**Status: ✅ COMPLETED AND FULLY FUNCTIONAL**

## 🎯 Fonctionnalités Principales

### 🧠 Intelligence Hybride CFR + Deep Learning
- **CFR/CFR+ Engine**: Algorithmes Counterfactual Regret Minimization pour calcul d'équilibre Nash
- **Deep CFR Neural Networks**: Réseaux de neurones PyTorch pour reconnaissance de patterns complexes
- **Basculement Dynamique CPU/GPU**: Optimisation automatique selon les ressources disponibles
- **Apprentissage Continu 24/7**: Amélioration perpétuelle sans interruption

### 🎮 Interface et Intégration
- **Détection Automatique**: Surveillance temps réel des plateformes poker (PokerStars, Winamax, PMU)
- **OCR Avancé**: Capture d'écran et reconnaissance automatique des états de jeu
- **Interface Bilingue**: Support complet Français/Anglais avec thèmes personnalisables
- **Cartes Réalistes**: Affichage visuel avec symboles authentiques (♠ ♥ ♦ ♣)

### ⚡ Performance et Optimisation
- **GPU Acceleration**: Support CUDA pour calculs massifs en parallèle
- **Base de Données Mémoire**: Stockage haute performance avec fallback SQLite
- **Gestion Ressources**: Monitoring CPU/RAM/GPU avec throttling automatique
- **Cache Intelligent**: Optimisation des calculs d'équité et abstractions de cartes

### 📊 Analyses et Statistiques
- **Probabilités Temps Réel**: Calculs Monte Carlo pour estimations de victoire
- **Recommandations Nash**: Actions optimales basées sur théorie des jeux
- **Tracking Performance**: Comparaison avec joueurs professionnels
- **Support ICM**: Ajustements tournois avec Independent Chip Model

Date completed: September 7, 2025

---

## 🔬 Comment Fonctionne le Système CFR/Nash

### CFR = Algorithme pour Calculer Nash

**CFR (Counterfactual Regret Minimization)** est l'algorithme mathématique qui permet de calculer l'**équilibre de Nash** au poker. Ce ne sont pas deux calculs séparés :

1. **Calcul des Regrets** : CFR analyse chaque décision et calcule les "regrets" (différence entre l'action prise et la meilleure action possible)
2. **Mise à Jour Stratégies** : Les regrets sont utilisés pour ajuster les probabilités d'actions futures
3. **Convergence Nash** : Après de nombreuses itérations, la stratégie converge vers l'équilibre de Nash optimal

### Apprentissage Continu en Temps Réel

#### ✅ Utilisation Immédiate Possible
- **Démarrage Instantané** : Le logiciel peut être utilisé dès le lancement
- **Recommandations Immédiates** : Basées sur les calculs CFR déjà effectués
- **Amélioration Progressive** : Chaque nouvelle main améliore la précision
- **Pas d'Attente** : Aucun besoin d'attendre la fin de l'apprentissage

#### 🔄 Fonctionnement de l'Apprentissage
```
Génération Continue : 25 mains toutes les 200ms (450 mains/minute)
↓
Intégration CFR : Mise à jour immédiate tables regrets/stratégies
↓
Amélioration Nash : Convergence progressive vers stratégie optimale
↓
Recommandations : Conseils de plus en plus précis en temps réel
```

#### 📈 Sources d'Apprentissage Multiples
- **Mains Historiques** : Chargement de bases de données existantes
- **Génération Synthétique** : Création continue de nouveaux scénarios
- **Parties en Direct** : Intégration des mains jouées par l'utilisateur
- **Simulation Monte Carlo** : Exploration massive d'espaces de jeu

### GPU vs CPU : Basculement Intelligent
- **Petits Calculs** : CPU pour efficacité et réactivité
- **Gros Batches** : GPU pour puissance de calcul parallèle
- **Seuil Automatique** : Basculement à 50+ mains simultanées
- **Fallback Sécurisé** : Retour CPU si GPU indisponible

---

## 🆕 Mises à Jour Récentes (September 7, 2025)

### 🤖 Interface Automatique Intelligente (NOUVEAU)
- **Détection automatique**: Surveillance continue des plateformes poker (PokerStars, Winamax, PMU)
- **Démarrage automatique**: Lancement automatique dès qu'une plateforme est détectée
- **Arrêt automatique**: Pause automatique quand aucune plateforme n'est active
- **Indicateur d'état**: Affichage temps réel en haut à droite (attente/actif/pause)
- **Suppression boutons**: Plus de boutons manuels démarrer/arrêter - tout est géré automatiquement

### 🎨 Logo et Branding
- **Logo officiel**: Intégration du logo RTPA Studio dans l'interface
- **Icône application**: Icône personnalisée pour la fenêtre principale
- **Identité visuelle**: Design cohérent et professionnel

### 🔍 Détection Plateformes Avancée
- **Surveillance processus**: Détection par nom de processus (PokerStars.exe, Winamax.exe, etc.)
- **Détection fenêtres**: Reconnaissance par titre de fenêtre
- **Support multi-plateformes**: PokerStars, Winamax, PMU, PartyPoker
- **Callback temps réel**: Notifications instantanées des changements d'état

### 🎴 Améliorations Interface Visuelle
- **Cartes réalistes**: Système d'affichage de cartes avec couleurs rouge/noir et symboles réels (♠ ♥ ♦ ♣)
- **Renommage**: "Cartes du Héros" renommé en "Main" pour meilleure ergonomie
- **Format visuel**: Cartes affichées dans des cadres blancs avec bordures, format "K♠" "A♥" etc.

### ⚙️ Configuration Avancée CFR
- **Descriptions détaillées**: Explications précises de chaque paramètre CFR
- **Nouveaux paramètres**: Profondeur CFR, Epsilon Exploration, CFR+
- **Options étendues**: Plus de contrôles fins pour optimisation algorithmes

### 🔥 Gestion PyTorch & GPU
- **Vérification automatique**: Status PyTorch affiché dans onglet Performance
- **Installation directe**: Bouton pour installer PyTorch depuis l'interface
- **Support CUDA**: Détection et indication du support GPU
- **Basculement Dynamique**: Choix automatique CPU/GPU selon charge de travail
- **Optimisation Mémoire**: Gestion intelligente de la mémoire GPU (limite configurable)

### 💾 Export/Import Base CFR (NOUVEAU)
- **Export complet**: Sauvegarde base CFR + données + statistiques + apprentissage Nash
- **Import sécurisé**: Restauration complète avec confirmation utilisateur
- **Préservation apprentissage**: Evite de repartir à zéro après mises à jour
- **Format JSON**: Fichiers lisibles et compatibles entre versions
- **Compression Intelligente**: Optimisation taille fichiers pour stockage/transfert

### 🎨 Personnalisation Interface
- **Couleurs d'accent**: Choix entre 5 couleurs (bleu, vert, rouge, violet, orange) - ✅ FONCTIONNEL
- **Opacité réglable**: Transparence fenêtre ajustable 70-100% - ✅ FONCTIONNEL  
- **Polices personnalisées**: Sélection police interface (Arial, Helvetica, Times, Courier) - ✅ FONCTIONNEL
- **Thèmes avancés**: Options étendues dark/light mode - ✅ FONCTIONNEL
- **Layouts adaptatifs**: Interface responsive pour différentes résolutions d'écran

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