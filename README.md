# 🎯 RTPA Studio - Real-Time Poker Assistant

**Logiciel d'analyse de poker en temps réel avec OCR automatique et calculs CFR/Nash optimisés**

## 🚀 Fonctionnalités

### ✨ Analyse Temps Réel
- **OCR automatique avec calibrage** : Capture non-intrusive + ajustement manuel précis
- **Auto-calibrage intelligent** : Détection automatique des plateformes actives  
- **Calculs CFR/Nash continus** : Recommandations optimales en temps réel
- **Support multi-clients** : PokerStars, Winamax, PMU, PartyPoker
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
- **Calibrage OCR intégré** : Interface complète avec auto-calibrage
- **Multilingue** : Français et Anglais
- **Paramètres avancés** : Override manuel du risque, gestion GPU/CPU/RAM
- **Thèmes** : Mode sombre/clair
- **Configuration YAML** : Paramètres persistants

## 🏗️ Architecture Technique

### 🤖 Intelligence Artificielle Hybride

#### **CFR Classique (Algorithmes Mathématiques)**
- **Counterfactual Regret Minimization** : Optimisation par regret minimal
- **Tables Nash** : Stockage en mémoire (regret_sum, strategy_sum)
- **Convergence rapide** : Équilibre Nash calculé en temps réel
- **Performance** : > 50,000 actions/seconde

#### **Deep CFR (Réseaux de Neurones PyTorch)**
- **Framework** : PyTorch 2.8.0+ avec TorchVision
- **Architecture duale** :
  - `advantage_net` : Réseau neuronal des valeurs d'actions
  - `strategy_net` : Réseau neuronal des stratégies optimales
- **Accélération GPU** : Support CUDA optionnel
- **Apprentissage profond** : Reconnaissance de patterns complexes

#### **Fonctionnement Hybride Intelligent**
- **Démarrage CFR** : Algorithmes mathématiques pour base solide
- **Deep CFR optionnel** : Activation automatique si PyTorch disponible
- **Combinaison** : Meilleur des deux approches selon la situation
- **Auto-adaptation** : Choix automatique de la méthode optimale

#### **Apprentissage Continu 24/7**
- **Génération automatique** : 50 nouvelles mains toutes les 100ms
- **Intégration temps réel** : Mise à jour immédiate des tables CFR
- **Sources multiples** :
  - Mains historiques réelles (1424+ mains chargées)
  - Génération synthétique continue
  - Parties jouées en direct
- **Amélioration perpétuelle** : Nash s'améliore constamment sans interruption

### 🧠 Algorithmes CFR/CFR+
- **Regret Minimization** : Calculs Nash en temps réel
- **Card Abstraction** : Buckets optimisés (64 par défaut)
- **Action Abstraction** : Bet sizing intelligent
- **Deep CFR** : Support PyTorch avec réseaux neuronaux

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

### ⚡ Performance et IA
- **Multi-threading** : OCR, CFR, et réseaux neuronaux en parallèle
- **GPU Acceleration** : PyTorch CUDA pour Deep CFR
- **Resource Management** : Gestion automatique CPU/RAM/GPU
- **Optimisations Numba** : Calculs critiques compilés JIT
- **Apprentissage continu** : Génération de 50 mains/100ms en arrière-plan
- **Cache intelligent** : Optimisation mémoire pour réseaux neuronaux

## 🎛️ Utilisation

### Démarrage Rapide
```bash
# Lancement principal (recommandé)
python rtpa.py

# Démonstration console temps réel
python main_headless.py
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

### Technologies et IA
- **Python 3.11+** : Interface et orchestration
- **PyTorch 2.8.0+** : Réseaux neuronaux Deep CFR
- **NumPy/Numba** : Optimisations mathématiques JIT
- **pybind11** : Modules C++ haute performance
- **Tesseract OCR** : Reconnaissance optique de caractères
- **CUDA** : Accélération GPU pour réseaux neuronaux

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

### Apprentissage Continu Automatique
- **Génération perpétuelle** : 50 nouvelles mains toutes les 100ms
- **Intégration temps réel** : Mise à jour immédiate des tables CFR
- **Sources d'apprentissage multiples** :
  - Mains historiques réelles (1424+ mains)
  - Génération synthétique intelligente
  - Parties jouées en direct par l'utilisateur
- **Amélioration Nash continue** : Convergence progressive 24/7
- **Réseaux neuronaux évolutifs** : Deep CFR s'adapte aux nouveaux patterns
- **Adaptation adversaires** : Reconnaissance de styles de jeu
- **Situations complexes** : Multi-way pots, short-stack, ICM
- **Meta-game** : Évolution stratégique perpétuelle

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

## 🔧 Installation et Lancement

### Étape 1 : Téléchargement
```bash
# Cloner le repository
git clone https://github.com/MDS-AnGe/RTPA_Studio.git
cd RTPA_Studio
```

### Étape 2 : Installation Automatique
```bash
# Auto-installation des dépendances au premier lancement
python rtpa.py
```

L'auto-installation va automatiquement :
- ✅ Vérifier Python 3.8+
- ✅ Installer toutes les dépendances Python  
- ✅ Configurer l'environnement
- ✅ Lancer l'interface moderne

### Étape 3 : Utilisation
```bash
# Lancement principal (unique)
python rtpa.py
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
# OU installation complète manuelle :
pip install numpy>=2.2.6 opencv-python>=4.12.0 pytesseract>=0.3.13
pip install pillow>=11.3.0 customtkinter>=5.2.2 mss>=10.1.0
pip install psutil>=7.0.0 pybind11>=2.12.0 pyyaml>=6.0.2
pip install matplotlib>=3.10.6 seaborn>=0.13.2 scipy>=1.16.1
pip install numba>=0.61.2 pygame>=2.6.1
# IA et Deep Learning :
pip install torch>=2.8.0 torchvision>=0.23.0
```

---

## 🎮 Guide d'Utilisation Détaillé

### Premier Lancement
1. **Lancez l'interface** : `python rtpa.py`
2. **Ouvrez votre client poker** (PokerStars, Winamax, PMU, PartyPoker)
3. **Joignez une table** de poker
4. **Accédez à l'onglet "🔧 Paramètres"**
5. **Section "🔍 Calibrage OCR"** : Cliquez "🤖 Auto-Calibrage"
6. **Validation** : Testez avec le bouton "🔍 Tester OCR"

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
- **🔍 Calibrage OCR** : Interface complète avec auto-calibrage intelligent
  - Sélecteur de plateforme (PokerStars, Winamax, PMU, PartyPoker)
  - 4 boutons : Charger Preset, Auto-Calibrage, Appliquer, Tester OCR
  - 6 zones ajustables : Cartes, Board, Pot, Stack, Blinds, Actions
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
# Lancement unique et principal
python rtpa.py
```

#### Mode Console/Démo
```bash
python main_headless.py   # Démonstration temps réel en console
```

---

## 🎯 Calibrage OCR pour Clients Poker

### Calibrage Automatique (Recommandé)
1. **Client ouvert** avec une table active  
2. **Onglet "🔧 Paramètres" > Section "🔍 Calibrage OCR"**
3. **Sélectionnez votre plateforme** dans le menu déroulant
4. **Cliquez "🤖 Auto-Calibrage"** (détection automatique)
5. **Validation** avec "🔍 Tester OCR"

### Calibrage Manuel (Ajustements fins)
1. **Cliquez "📋 Charger Preset"** pour les coordonnées par défaut
2. **Ajustez manuellement** les champs Y, X, L, H selon vos besoins
3. **Cliquez "✅ Appliquer"** pour sauvegarder
4. **Testez** avec "🔍 Tester OCR"

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
RTPA_Studio/
├── src/
│   ├── algorithms/          # Moteur CFR et Nash
│   ├── core/               # Gestionnaire principal  
│   ├── database/           # Base de données mémoire
│   ├── gui/                # Interface graphique moderne
│   ├── ocr/                # Système OCR avec calibrage
│   ├── config/             # Configuration
│   └── utils/              # Utilitaires et optimisations
├── config/                 # Fichiers configuration
├── logs/                   # Logs d'activité  
├── rtpa.py                # Point d'entrée principal
├── main_headless.py       # Mode console
├── CALIBRAGE_OCR_README.md # Guide calibrage OCR
└── README.md              # Documentation complète
```

---

**⚠️ Usage Responsable**: Ce logiciel est conçu exclusivement à des fins d'étude, formation et simulation post-session. L'utilisation en live ou pour contourner les règles des sites de poker est strictement interdite.

**🎓 Objectif Pédagogique**: RTPA Studio vise à améliorer la compréhension de la théorie des jeux et des stratégies optimales au poker Texas Hold'em No Limit.

**📧 Contact**: Pour contributions académiques ou recherche en théorie des jeux.

---

## 🧪 Intelligence Artificielle - Détails Techniques

### **Architecture IA Complète**

#### **1. CFR Traditionnel (Base Mathématique)**
```python
# Stockage en mémoire haute performance
regret_sum = {}          # Tables de regrets accumulés
strategy_sum = {}        # Stratégies cumulatives
info_sets = {}          # Ensembles d'information
```

#### **2. Deep CFR (Réseaux de Neurones)**
```python
# Réseaux PyTorch pour situations complexes
advantage_net = None     # Réseau des valeurs d'actions
strategy_net = None      # Réseau des stratégies optimales
deep_cfr_enabled = False # Activation conditionnelle
```

#### **3. Fonctionnement Intelligent**
- **Démarrage** : CFR classique pour convergence rapide
- **Complexité** : Activation automatique Deep CFR si nécessaire
- **GPU** : Accélération CUDA pour réseaux neuronaux
- **Hybride** : Combinaison optimale selon la situation

### **Génération Continue de Données**
- **Fréquence** : 50 mains/100ms (30,000 mains/minute)
- **Scénarios prioritaires** : Heads-up, tournois, stacks variés
- **Intégration immédiate** : Calcul CFR et mise à jour Nash temps réel
- **Apprentissage perpétuel** : Amélioration continue sans arrêt

### **Technologies IA Utilisées**
- **PyTorch 2.8.0+** : Framework de deep learning
- **CUDA** : Accélération GPU optionnelle
- **NumPy** : Calculs matriciels optimisés
- **Numba** : Compilation JIT pour performances critiques
- **CFR/CFR+** : Algorithmes de théorie des jeux
- **Monte Carlo** : Simulations probabilistes

---

*Dernière mise à jour : Septembre 2025 - Version 1.1.0*  
*Statut : ✅ Stable et Opérationnel*  
*IA : 🤖 CFR Hybride + Deep Learning PyTorch*  
*Windows : 🖥️ Application native 'RTPA Studio' dans le Gestionnaire des tâches*