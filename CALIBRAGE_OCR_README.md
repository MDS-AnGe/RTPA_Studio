# 🔍 Guide de Calibrage OCR - RTPA Studio

Le système de calibrage OCR permet d'ajuster précisément la détection des éléments de jeu selon votre résolution d'écran et votre plateforme poker.

## 📍 Accès au Calibrage

1. **Lancez RTPA Studio** avec `python rtpa.py`
2. **Cliquez sur l'onglet "🔧 Paramètres"**
3. **Localisez la section "🔍 Calibrage OCR"**

![Interface de Calibrage OCR](attached_assets/image_1757290049909.png)

## ⚙️ Interface de Calibrage

### 🎯 Sélection de Plateforme
- **Menu déroulant** : Choisissez votre plateforme poker
  - PokerStars
  - Winamax  
  - PMU
  - PartyPoker

### 📐 Zones Configurables

Chaque zone a 4 paramètres ajustables :

| Zone | Description | Paramètres |
|------|-------------|------------|
| **Cartes Héros** | Position de vos 2 cartes | Y, X, L, H |
| **Board** | Cartes communes (flop/turn/river) | Y, X, L, H |
| **Pot** | Montant du pot | Y, X, L, H |
| **Stack Héros** | Votre pile de jetons | Y, X, L, H |
| **Blinds** | Petite et grosse blinde | Y, X, L, H |
| **Boutons Action** | Zone Fold/Call/Raise | Y, X, L, H |

**Paramètres des coordonnées :**
- **Y** : Position verticale (pixels depuis le haut)
- **X** : Position horizontale (pixels depuis la gauche)
- **L** : Largeur de la zone de détection
- **H** : Hauteur de la zone de détection

## 🛠️ Boutons de Contrôle

### 📋 Charger Preset
- **Fonction** : Charge les coordonnées par défaut pour votre plateforme
- **Usage** : Cliquez pour remplir automatiquement tous les champs
- **Conseil** : Utilisez ceci comme point de départ avant ajustements

### 🤖 Auto-Calibrage (NOUVEAU)
- **Fonction** : Détection automatique et application des réglages OCR
- **Intelligence IA** : Détecte votre plateforme poker active en temps réel
- **Surveillance continue** : Détection automatique des nouvelles plateformes (toutes les 2 secondes)
- **Activation instantanée** : Calibrage en un clic sans intervention manuelle
- **Support total** : PokerStars, Winamax, PMU, PartyPoker
- **Technologie** : Analyse des processus système + titres de fenêtres
- **Persistance** : Les réglages sont automatiquement sauvegardés et rechargés

### ✅ Appliquer
- **Fonction** : Sauvegarde vos réglages personnalisés
- **Sauvegarde** : Crée le fichier `config/ocr_calibration.json`
- **Persistance** : Vos réglages sont rechargés au prochain démarrage

### 🔍 Tester OCR
- **Fonction** : Vérifie que la détection fonctionne
- **Feedback** : Affiche les résultats dans la console et l'interface
- **Validation** : Confirme que vos zones sont bien configurées
- **Détection temps réel** : Capture et analyse l'état actuel du jeu

## 🎯 Guide d'Utilisation Étape par Étape

### 🚀 Méthode Ultra-Rapide (Recommandée)
1. **Ouvrez votre plateforme poker** (PokerStars, Winamax, PMU, PartyPoker)
2. **Lancez RTPA Studio** 
3. ✅ **Le calibrage se fait automatiquement !**
4. **Optionnel** : Cliquez "🔍 Tester OCR" pour vérifier

⚡ **Détection automatique** : RTPA détecte la plateforme et applique le bon calibrage sans intervention.

### 🎯 Méthode Manuelle (Si besoin)
1. **Sélectionnez votre plateforme** dans le menu déroulant
2. **Cliquez "🤖 Auto-Calibrage"**
3. **Cliquez "🔍 Tester OCR"** pour vérifier
4. ✅ **Terminé !**

### Méthode Manuelle (Ajustements Précis)
1. **Sélectionnez votre plateforme**
2. **Cliquez "📋 Charger Preset"**
3. **Ajustez les coordonnées** selon vos besoins :
   - Modifiez Y/X pour déplacer la zone
   - Ajustez L/H pour redimensionner
4. **Cliquez "✅ Appliquer"** pour sauvegarder
5. **Cliquez "🔍 Tester OCR"** pour valider

## 🔧 Résolution de Problèmes

### Détection Imprécise
- **Vérifiez** que votre plateforme est correctement sélectionnée
- **Ajustez** les coordonnées Y/X si les zones sont décalées
- **Redimensionnez** L/H si la zone est trop petite/grande

### Aucune Détection
- **Assurez-vous** que votre plateforme poker est ouverte
- **Vérifiez** que la table de jeu est visible à l'écran
- **Testez** avec "🔍 Tester OCR" pour diagnostiquer

### Coordonnées Incorrectes
- **Utilisez** "📋 Charger Preset" pour revenir aux valeurs par défaut
- **Essayez** "🤖 Auto-Calibrage" pour une détection automatique
- **Ajustez** manuellement selon votre résolution d'écran

## 💾 Sauvegarde et Restauration

### Sauvegarde Automatique
- **Fichier** : `config/ocr_calibration.json`
- **Contenu** : Toutes vos coordonnées personnalisées
- **Chargement** : Automatique au démarrage de RTPA Studio

### Réinitialisation
- **Supprimez** le fichier `config/ocr_calibration.json`
- **Redémarrez** RTPA Studio
- **Rechargez** les presets par défaut

## 🎮 Plateformes Supportées

### PokerStars
- **Résolution testée** : 1920x1080, 1366x768, 2560x1440
- **Zones optimisées** : Table standard PokerStars
- **Détection automatique** : Processus PokerStars.exe
- **Particularités** : Interface classique avec thèmes sombre/clair

### Winamax
- **Résolution testée** : 1920x1080, 1366x768, 2560x1440
- **Zones optimisées** : Interface web/logiciel
- **Détection automatique** : Processus Winamax.exe, navigateurs (Firefox, Chrome)
- **Particularités** : Interface moderne avec animations

### PMU Poker
- **Résolution testée** : 1920x1080, 1366x768
- **Zones optimisées** : Interface PMU spécifique
- **Détection automatique** : Processus PMUPoker.exe
- **Particularités** : Layout et couleurs distinctifs

### PartyPoker
- **Résolution testée** : 1920x1080
- **Zones optimisées** : Interface PartyPoker
- **Détection automatique** : Processus PartyPoker.exe
- **Particularités** : Boutons d'action et design spécifiques

## ⚡ Conseils d'Optimisation

### Pour de Meilleures Performances
- **Utilisez** une résolution d'écran stable
- **Placez** votre table poker au même endroit
- **Évitez** de redimensionner la fenêtre poker
- **Calibrez** une seule fois par plateforme

### Ajustements Fins
- **Commencez** toujours par "📋 Charger Preset"
- **Ajustez** par petits incréments (+/- 5-10 pixels)
- **Testez** après chaque modification
- **Sauvegardez** dès que c'est optimal

## 🔧 Fonctionnement Technique du Système Automatique

### 🎯 Détection des Plateformes
Le système surveille automatiquement :
- **Processus actifs** : PokerStars.exe, Winamax.exe, PMUPoker.exe, PartyPoker.exe
- **Titres de fenêtres** : "PokerStars", "Winamax Poker", "PMU Poker", etc.
- **Navigation web** : Détection dans Chrome/Firefox pour Winamax web

### ⚙️ Application Automatique
Quand une plateforme est détectée :
1. **Chargement du preset** correspondant depuis `src/ocr/screen_capture.py`
2. **Application des zones OCR** : hero_cards, board_cards, pot_size, etc.
3. **Notification GUI** : Mise à jour de l'interface utilisateur
4. **Sauvegarde automatique** : Configuration persistante

### 📋 Presets Intégrés
Zones préconfigurees pour chaque plateforme :
```yaml
PokerStars: hero_cards: {top: 580, left: 440, width: 140, height: 50}
Winamax:   hero_cards: {top: 590, left: 460, width: 130, height: 45}
PMU:       hero_cards: {top: 575, left: 450, width: 135, height: 48}
```

### 🔄 Surveillance Continue
- **Fréquence** : Vérification toutes les 2 secondes
- **Thread dédié** : Surveillance en arrière-plan sans impact performance
- **Multi-plateforme** : Support simultané de plusieurs clients
- **Callbacks** : Notifications instantanées des changements d'état

### 🛠️ Fichiers de Configuration
- **Presets** : `src/ocr/screen_capture.py` (zones par défaut)
- **Détection** : `src/utils/platform_detector.py` (logique de surveillance)
- **Auto-application** : `src/core/app_manager.py` (orchestration)
- **Sauvegarde** : `config/ocr_calibration.json` (paramètres utilisateur)

### 🎮 Ajustement Manuel (Si Nécessaire)
Si les presets ne conviennent pas à votre configuration :
1. **Utilisez l'interface de calibrage** pour ajuster les zones
2. **Les réglages remplacent** automatiquement les presets
3. **Sauvegarde permanente** : Vos ajustements sont conservés
4. **Reset possible** : Supprimez `config/ocr_calibration.json` pour revenir aux presets

---

**🚀 Le calibrage OCR automatique assure une détection précise et fiable pour des recommandations optimales sans configuration manuelle !**