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

**⚠️ Usage Responsable**: Ce logiciel est conçu exclusivement à des fins d'étude, formation et simulation post-session. L'utilisation en live ou pour contourner les règles des sites de poker est strictement interdite.

**🎓 Objectif Pédagogique**: RTPA Studio vise à améliorer la compréhension de la théorie des jeux et des stratégies optimales au poker Texas Hold'em No Limit.