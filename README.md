# 🎯 RTPA Studio - Real-Time Poker Analysis

**Logiciel d'analyse de poker en temps réel avec OCR et calculs CFR/Nash**

## 🚀 Fonctionnalités

### ✨ Analyse Temps Réel
- **OCR automatique** : Capture non-intrusive des données de jeu
- **Calculs CFR/Nash continus** : Recommandations optimales en temps réel
- **Support multi-clients** : Compatible PokerStars, Winamax, et autres
- **Latence ultra-faible** : < 50ms pour l'OCR, calculs en continu

### 🎮 Types de Jeu Supportés
- **Cash Games** : Texas Hold'em No Limit 9-max
- **Tournois** : Avec ajustements ICM automatiques
- **Antes et Blinds** : Gestion complète des structures

### 🎯 Recommandations Intelligentes
- **Actions optimales** : Fold, Check, Call, Bet (Small/Medium/Large/All-in)
- **Probabilités de victoire** : Calculs Monte Carlo précis
- **Niveau de risque** : Évaluation en temps réel (0-100%)
- **Reasoning** : Explications détaillées des recommandations

### 📊 Statistiques et Performance
- **Suivi des performances** : Mains jouées/gagnées, taux de victoire
- **Comparaison pro** : Benchmark avec joueurs professionnels (65% attendu)
- **Historique complet** : Base de données en mémoire haute performance
- **Exports** : CSV, PDF pour analyse approfondie

### ⚙️ Interface et Paramètres
- **Interface moderne** : CustomTkinter élégant et responsive
- **Multilingue** : Français et Anglais
- **Paramètres avancés** : Override manuel du risque, gestion GPU/CPU/RAM
- **Thèmes** : Mode sombre/clair
- **Configuration YAML** : Paramètres persistants

## 🏗️ Architecture Technique

### 🧠 Algorithmes CFR/CFR+
- **Regret Minimization** : Calculs Nash en temps réel
- **Card Abstraction** : Buckets optimisés (64 par défaut)
- **Action Abstraction** : Bet sizing intelligent
- **Deep CFR** : Support PyTorch optionnel

### 🖥️ Capture OCR
- **Tesseract OCR** : Reconnaissance haute précision
- **Preprocessing avancé** : CLAHE, débruitage, seuillage adaptatif
- **Zones ROI** : Détection automatique des clients poker
- **Cache intelligent** : Optimisation mémoire

### 💾 Base de Données
- **In-Memory SQLite** : Performance maximale
- **Structure optimisée** : Index pour recherches rapides
- **Persistance optionnelle** : Sauvegarde sélective
- **Threading-safe** : Accès concurrent sécurisé

### ⚡ Performance
- **Multi-threading** : OCR et calculs parallèles
- **GPU Acceleration** : PyTorch CUDA optionnel
- **Resource Management** : Gestion automatique CPU/RAM/GPU
- **Optimisations Numba** : Calculs critiques compilés

## 🎛️ Utilisation

### Démarrage Rapide
```bash
# Test des composants
python test_rtpa.py

# Lancement complet
python main.py
```

### Interface Principale
1. **État du Jeu** : Cartes héros, board, pot, stack
2. **Recommandations** : Action optimale avec probabilités
3. **Statistiques** : Performance et comparaisons
4. **Paramètres** : Configuration avancée

### Paramètres Avancés
- **Type de table** : Cash Game / Tournoi
- **Pourcentage de risque** : Manuel ou automatique
- **Resources** : Allocation CPU/GPU/RAM
- **OCR** : Zones et seuils de confiance

## 🔧 Configuration

### Fichiers de Configuration
- `config/settings.yaml` : Paramètres principaux
- `logs/rtpa_studio.log` : Journaux d'activité

### Langages et Performance
- **Python** : Interface et orchestration
- **C++/Rust** : Calculs critiques (optionnel)
- **NumPy/Numba** : Optimisations mathématiques
- **PyTorch** : Deep CFR et GPU

## 📋 Spécifications Techniques

### Exigences Système
- **OS** : Windows 10+, Linux x64
- **RAM** : 4GB minimum, 8GB recommandé
- **GPU** : CUDA optionnel pour Deep CFR
- **CPU** : Multi-core recommandé

### Performance Cibles
- **OCR** : < 50ms par capture
- **CFR** : ≥ 50k actions/s
- **Monte Carlo** : ≥ 200k iterations/s
- **Interface** : 60 FPS, < 100ms latence

### Sécurité et Éthique
- **Usage d'étude uniquement** : Formation et simulation
- **Pas d'intégration live** : Aucune communication avec clients poker
- **Données locales** : Aucune transmission externe
- **Open source** : Code transparent et vérifiable

## 🏆 Objectifs Stratégiques

### Optimisation Bankroll
- **Minimisation des pertes** : Stratégies conservatrices
- **Maximisation du stack** : Opportunités EV positives
- **Gestion du risque** : Adaptation au type de jeu
- **ICM Tournament** : Ajustements bubble/ITM

### Apprentissage Continu
- **Amélioration CFR** : Mise à jour des regrets
- **Adaptation adversaires** : Patterns comportementaux
- **Situations complexes** : Multi-way pots, short-stack
- **Meta-game** : Évolution des stratégies

## 📊 Métriques de Succès

### KPIs Principaux
- **Taux de victoire** : Target 65%+ (niveau pro)
- **BB/100** : Profit par 100 mains
- **Variance** : Stabilité des résultats
- **ROI Tournois** : Return on Investment

### Indicateurs Techniques
- **Latence OCR** : < 50ms
- **Précision reconnaissance** : > 95%
- **Uptime** : 99.9%+ stabilité
- **Resource usage** : < 80% CPU/RAM

---

---

## 🔧 Installation Automatique

### Étape 1 : Téléchargement
```bash
# Cloner le repository ou télécharger l'archive
cd rtpa-studio
```

### Étape 2 : Installation Automatique
```bash
# Lancer l'installateur automatique
python setup_installer.py
```

L'installateur va automatiquement :
- ✅ Vérifier Python 3.8+
- ✅ Installer Tesseract OCR
- ✅ Installer toutes les dépendances Python  
- ✅ Configurer les répertoires
- ✅ Tester l'installation
- ✅ Créer les raccourcis

### Étape 3 : Lancement
```bash
# Interface graphique complète
python rtpa_studio.py
# OU directement
python main_gui.py
```

---

## 🛠️ Installation Manuelle (si nécessaire)

### Prérequis Système
- **Python 3.8+** (3.9+ recommandé)
- **Tesseract OCR 4.0+**
- **4 GB RAM minimum** (8 GB recommandé)
- **Résolution écran** 1920x1080+ pour OCR optimal

### Installation Tesseract OCR

#### Windows
```bash
# Télécharger depuis GitHub
https://github.com/UB-Mannheim/tesseract/releases
# Ajouter au PATH système : C:\Program Files\Tesseract-OCR
```

#### macOS
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-fra
```

### Installation Dépendances Python
```bash
pip install -r requirements.txt
# OU manuellement :
pip install numpy>=1.21.0 opencv-python>=4.5.0 pytesseract>=0.3.8
pip install pillow>=8.0.0 customtkinter>=5.0.0 mss>=6.1.0
pip install psutil>=5.8.0 pyyaml>=6.0 matplotlib>=3.5.0
```

---

## 🎮 Guide d'Utilisation Détaillé

### Premier Lancement
1. **Lancez l'interface** : `python main_gui.py`
2. **Ouvrez votre client poker** (PokerStars, Winamax, PMU)
3. **Joignez une table** de poker
4. **Accédez à l'onglet "Configuration"**
5. **Sélectionnez votre client** et lancez le calibrage

### Onglets Interface

#### 🎯 Game State - État Actuel du Jeu
- **Cartes héros** : Visualisation réaliste avec couleurs
- **Cartes board** : Flop, Turn, River
- **Informations** : Pot, stack, blinds, position
- **Action** : Tour du joueur (action_to_hero)

#### 🧠 Recommendations - Conseils Stratégiques  
- **Action optimale** : Fold, Check, Call, Bet_Small/Medium/Large
- **Probabilité victoire** : Calculs Monte Carlo en temps réel
- **Niveau de risque** : Évaluation 0-100%
- **Raisonnement** : Explications détaillées de la stratégie
- **Actions alternatives** : Autres choix possibles

#### 📊 Statistics - Performance et Historique
- **Taux de victoire** : Pourcentage mains gagnées
- **Performance vs Pro** : Comparaison avec joueurs professionnels (65% cible)
- **Graphiques temps réel** : Évolution de la performance
- **Historique complet** : Toutes les mains analysées

#### ⚙️ Configuration - Paramètres Système
- **Calibrage OCR** : Zones de capture pour chaque client poker
- **Sélection client** : PokerStars, Winamax, PMU
- **Paramètres CFR** : Itérations, exploration, discount factor
- **Thèmes** : Dark/Light mode, couleurs d'accent, polices
- **Langues** : Français/Anglais

#### 🔧 Performance - Monitoring Système
- **Usage ressources** : CPU, RAM, GPU en temps réel
- **Status PyTorch** : Installation et support CUDA
- **Vitesse calculs** : Recommandations/seconde
- **Gestion automatique** : Optimisation des ressources

#### 💾 Database - Gestion Données
- **Export/Import CFR** : Sauvegarde apprentissages Nash
- **Historique complet** : Base de données mains
- **Statistiques détaillées** : Performance par session
- **Nettoyage** : Purge des anciennes données

### Modes de Lancement

#### Mode Interface Graphique
```bash
python main_gui.py        # Interface complète
python rtpa_studio.py     # Raccourci créé par l'installateur
```

#### Mode Console/Démo
```bash
python main_headless.py   # Démonstration temps réel en console
```

#### Tests et Validation
```bash
python test_final.py                    # Tests complets du système
python test_algorithms_validation.py    # Validation algorithmes CFR/Nash
python test_performance_benchmarks.py   # Benchmarks de performance
```

---

## 🎯 Calibrage OCR pour Clients Poker

### Calibrage Automatique
1. **Client ouvert** avec une table active
2. **Configuration > Calibrage OCR**
3. **"Détection Automatique"**
4. **Validation** des zones détectées

### Zones OCR Prédéfinies

#### PokerStars
```yaml
hero_cards: {top: 580, left: 440, width: 140, height: 50}
board_cards: {top: 280, left: 350, width: 320, height: 60}
pot_size: {top: 220, left: 450, width: 120, height: 30}
hero_stack: {top: 650, left: 420, width: 100, height: 25}
```

#### Winamax
```yaml
hero_cards: {top: 590, left: 460, width: 130, height: 45}
board_cards: {top: 290, left: 370, width: 300, height: 55}
pot_size: {top: 230, left: 470, width: 110, height: 28}
hero_stack: {top: 660, left: 440, width: 90, height: 23}
```

### Optimisation OCR
- **Résolution** : 1920x1080+ recommandé
- **Zoom client** : 100% (pas de zoom)
- **Thème** : Couleurs contrastées
- **Position** : Fenêtre stable
- **Éclairage** : Écran uniforme

---

## 🔧 Dépannage et Support

### Problèmes Fréquents

#### Tesseract Non Trouvé
```bash
# Vérification
tesseract --version

# Windows : Ajout PATH
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
```

#### OCR Imprécis
- Recalibrez les zones dans Configuration
- Vérifiez résolution écran et zoom client 100%
- Améliorez éclairage et contraste

#### Performance Lente
- Réduisez itérations CFR dans Configuration > Avancé
- Activez GPU si disponible
- Fermez applications gourmandes

#### Plantage Interface
```bash
# Mode debug
python main_gui.py --debug

# Logs détaillés
tail -f logs/rtpa_studio.log
```

### Tests Composants
```bash
# Test CFR
python -c "import src.algorithms.cfr_engine; print('CFR OK')"

# Test Tesseract
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"

# Test capture écran
python -c "import mss; print('Capture OK')"
```

---

## 📂 Structure Fichiers

```
rtpa-studio/
├── src/
│   ├── algorithms/          # Moteur CFR et Nash
│   ├── core/               # Gestionnaire principal  
│   ├── database/           # Base de données mémoire
│   ├── gui/                # Interface graphique
│   ├── ocr/                # Système OCR
│   ├── config/             # Configuration
│   └── utils/              # Utilitaires
├── config/                 # Fichiers configuration
├── logs/                   # Logs d'activité
├── exports/                # Données exportées
├── main_gui.py            # Interface graphique
├── main_headless.py       # Mode console
├── setup_installer.py     # Installateur automatique
└── rtpa_studio.py         # Raccourci de lancement
```

---

**⚠️ Usage Responsable**: Ce logiciel est conçu exclusivement à des fins d'étude, formation et simulation post-session. L'utilisation en live ou pour contourner les règles des sites de poker est strictement interdite.

**🎓 Objectif Pédagogique**: RTPA Studio vise à améliorer la compréhension de la théorie des jeux et des stratégies optimales au poker Texas Hold'em No Limit.

**📧 Contact**: Pour contributions académiques ou recherche en théorie des jeux.

---

*Dernière mise à jour : Septembre 2025 - Version 1.0.0 - Statut : Stable et Opérationnel*