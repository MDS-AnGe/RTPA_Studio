# Audit technique & UX — **RTPAStudio**
**Version du rapport :** 1.0  
**Date :** 08/09/2025  
**Auteur :** ChatGPT (audit sur archive fournie : `RTPAStudio.zip`)  

---

## 1) Résumé exécutif (TL;DR)
- **Installation fragile** : `requirements.txt` contient des versions irréalistes (ex. `numpy==2.2.6`, `matplotlib==3.10.6`, `psutil==7.0.0`, `pillow==11.3.0`) et des dépendances lourdes/optionnelles (`torch`, `numba`, `seaborn`, `pygame`) ⇒ échecs d’installation fréquents, set‑up lent et instable.
- **OCR non garanti** : `pytesseract` utilisé sans configuration fiable du binaire Tesseract (`tesseract.exe`) ⇒ OCR peut ne jamais démarrer.
- **Détection fenêtre Windows fragile** : usage direct de `ctypes`/`EnumWindows` sans callback typé ni gestion robuste des `HWND` ⇒ faux positifs/erreurs silencieuses.
- **Promesse C++/GPU non tenue** : code d’intégration C++/pybind11 prévu mais **aucun build** packagé (`setup.py/pyproject` manquants) ⇒ repli Python systématique.
- **Interface lente** : la liste des joueurs est **détruite/recréée** à chaque rafraîchissement ⇒ micro‑freezes Tkinter.
- **OCR trop fréquent et trop large** : capture d’écran + Tesseract toutes les ~500 ms, sans détection de changement ⇒ CPU élevé, latence.
- **Packaging gonflé** : archive contenant `.git`, caches et assets inutiles ⇒ lancement/scan lents.

**Impact prioritaire :**  
1) Réduire la latence et les freezes GUI (réutiliser les widgets, rafraîchir parcimonieusement).  
2) Stabiliser l’OCR (path Tesseract + ROI précises + déclenchement conditionnel).  
3) Normaliser les dépendances (requirements minimal), rendre GPU/C++ **optionnels**.  
4) Remplacer l’énumération de fenêtres via `ctypes` par `pywin32` ou APIs Tkinter.

---

## 2) Contexte & portée
- Audit rapide du code et de l’UX de l’application fournie (`RTPAStudio.zip`).
- Objectif : relever incohérences, erreurs probables, problèmes de performances/latence GUI, et proposer des correctifs concrets & vérifiables.

---

## 3) Constats détaillés

### 3.1 Dépendances & installation
- **Versions invraisemblables ou non publiées** :  
  - `numpy==2.2.6`, `matplotlib==3.10.6`, `psutil==7.0.0`, `pillow==11.3.0`.  
  - `torch`/`torchvision` **non versionnés** ⇒ téléchargements lourds, incompatibilités fréquentes (surtout Windows).
- **Librairies inutilisées** (ex. `seaborn`, `pygame`) présentes ⇒ complexifient l’install sans bénéfice.
- **Auto-installation récursive** : `auto_install.py` tente d’auto‑corriger en cascade en cas d’échec ⇒ risque de boucles et messages confus.

**Correctif recommandé — requirements minimal :**
```txt
# requirements-minimal.txt
opencv-python>=4.8,<5
pytesseract>=0.3.10,<0.4
numpy>=1.24,<2.1
mss>=7,<11
psutil>=5.9,<6
pillow>=9,<11
customtkinter>=5.2,<6
pyyaml>=6,<7
# Optionnels (installer SEULEMENT si features activées)
# pywin32>=306,<307
# torch>=2.1,<2.4 ; torchvision>=0.16,<0.19
# numba>=0.58,<0.60
```

### 3.2 OCR & robustesse
- **Tesseract non configuré** : pas d’initialisation fiable de `pytesseract.pytesseract.tesseract_cmd`.  
- **ROI** : zones par défaut dépendantes du client/position d’écran, non compensées par le **DPI scaling** Windows ⇒ OCR vide/erratique.  
- **Parsing numérique** : `parse_monetary_value` fragile (virgule/point/espaces/thin spaces/k) ⇒ retours à 0.

**Correctifs :**
- Détection **automatique** du chemin Tesseract + sélection manuelle si introuvable.
- **ROI précises** basées sur la fenêtre poker (et non l’écran complet).
- **Hash d’image** rapide (per ROI) ⇒ ne lancer l’OCR que si changement.
- Profils `psm`/`oem` adaptés (digits/mono‑ligne) pour les zones numériques.

**Exemple (détection Tesseract + fallback)** :
```python
import os, shutil, pytesseract
CANDIDATES = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    shutil.which("tesseract"),
]
p = next((c for c in CANDIDATES if c and os.path.isfile(c)), None)
if p:
    pytesseract.pytesseract.tesseract_cmd = p
else:
    # Afficher un dialogue GUI 'Parcourir...' et bloquer l'OCR tant que non configuré
    raise RuntimeError("Tesseract introuvable. Configurez le chemin vers tesseract.exe.")
```

### 3.3 Détection de fenêtre & multi‑client
- `ctypes.windll.user32.EnumWindows` appelé sans **callback CFUNCTYPE** typé, et gestion des handles limitée ⇒ instabilité probable.
- Heuristiques par **titre de fenêtre**/process name fragiles (variantes locales, majuscules, clients multiples).

**Correctifs :**
- Utiliser **pywin32** (`win32gui.EnumWindows`, `GetWindowText`, `GetClassName`, `GetWindowRect`) pour récupérer le **HWND** et la **bounding box** exacte.  
- Filtrage par **classe/famille** de fenêtre + vérification du **processus** (via `psutil`) plutôt que par simple substring.

**Exemple (pywin32)** :
```python
import win32gui, win32process, psutil

def iter_windows():
    hwnds = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
    win32gui.EnumWindows(cb, None)
    return hwnds

def find_poker_window():
    for hwnd in iter_windows():
        title = win32gui.GetWindowText(hwnd).lower()
        if any(k in title for k in ("winamax", "pokerstars", "ggpoker")):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            pname = psutil.Process(pid).name().lower()
            return hwnd, pname
    return None, None
```

### 3.4 Intégration C++/GPU
- Fichiers d’intégration mentionnent pybind11 mais **aucun** artefact de build (`pyproject.toml`, `setup.cfg`, wheel) n’est fourni.  
- Documentation promet **CFR+ GPU** et latence `<50 ms` — irréaliste sans build/optimisations et sans réduire le travail OCR.

**Correctifs :**
- Soit **fournir** la chaîne de build (pybind11) + wheel pré‑compilée Windows x64,  
- Soit **retirer** la promesse et rendre l’option GPU/C++ désactivée par défaut.

### 3.5 Interface graphique (Tkinter/customtkinter)
- **Antipattern** : recréation complète des widgets joueurs à chaque tick (`destroy()` → `create()`).
- **Threads daemon** sans `join()` à la fermeture ⇒ fuites possibles.
- **Logs verbeux** (prints/emoji) ⇒ coût inutile.

**Correctifs UI (pattern “créer une fois, mettre à jour souvent”)** :
```python
class PlayersPanel:
    def __init__(self, parent, seats=9):
        self.rows = []
        for i in range(seats):
            frame = ctk.CTkFrame(parent)
            name_lbl = ctk.CTkLabel(frame, text=f"Seat {{i+1}}: —")
            stack_lbl = ctk.CTkLabel(frame, text="Stack: —")
            state_lbl = ctk.CTkLabel(frame, text="State: —")
            frame.grid(row=i, column=0, sticky="ew", padx=6, pady=3)
            name_lbl.grid(row=0, column=0, padx=4)
            stack_lbl.grid(row=0, column=1, padx=4)
            state_lbl.grid(row=0, column=2, padx=4)
            self.rows.append((name_lbl, stack_lbl, state_lbl))

    def update(self, players_data):
        # players_data: list of dicts [{{'name':..., 'stack':..., 'state':...}}, ...]
        for i, data in enumerate(players_data):
            n = data.get("name","—"); s = data.get("stack","—"); t = data.get("state","—")
            name_lbl, stack_lbl, state_lbl = self.rows[i]
            name_lbl.configure(text=f"Seat {{i+1}}: {{n}}")
            stack_lbl.configure(text=f"Stack: {{s}}")
            state_lbl.configure(text=f"State: {{t}}")
```

---

## 4) Performance & latence

### 4.1 Goulots identifiés
- **Tesseract** : coût dominant si appelé fréquemment et sur de larges surfaces.
- **Rafraîchissement UI** : recréer les widgets est bien plus cher que `configure(text=...)`.
- **Capture écran** : capture full screen + conversion PIL fréquente.
- **Logs** : sorties console répétées.

### 4.2 Stratégie de réduction
1. **Régime évènementiel/conditionnel** :
   - Calculer un **hash** rapide (ex. `xxhash`, `hashlib.blake2b` sur image downscale) de chaque ROI.
   - **Skipper l’OCR** si hash identique à N‑1.
2. **ROI strictes** :
   - Découper uniquement les zones nécessaires (cartes, pot, stacks, boutons d’action).
3. **Cadence adaptative** :
   - Si 3 OCR d’affilée renvoient “rien/changé=non” ⇒ allonger l’intervalle (p.ex. 1200 ms).
   - Repasser à 400–600 ms dès que changement détecté.
4. **UI “diff only”** :
   - Mettre à jour uniquement les labels dont le texte change.
5. **Logs** :
   - Logger en fichier (niveau INFO) + console WARN/ERROR seulement.

**Pseudo-scheduler OCR adaptatif** :
```python
interval = 600  # ms
miss = 0
def tick():
    global interval, miss
    changed = any(roi_hash_new[i] != roi_hash_old[i] for i in rois)
    if changed:
        run_ocr()
        miss = 0
        interval = 600
    else:
        miss += 1
        if miss >= 3:
            interval = min(1600, interval + 200)
    root.after(interval, tick)
```

---

## 5) Cohérence Doc ↔ Réalité
- **Promesses** : multi‑clients, latence <50 ms, CFR+ GPU, auto‑calibrage.  
- **Réalité actuelle** : pas d’auto‑calibrage DPI robuste, build C++ absent, OCR “polling” lourd, UI recréée fréquemment.  
- **Action** : reformuler la documentation et/ou livrer les composants manquants (builds, scripts de calibration).

---

## 6) Plan de remédiation priorisé

### P0 (Aujourd’hui – J+1)
- Remplacer la recréation UI par **mise à jour in‑place** (pattern ci‑dessus).
- Introduire **détection Tesseract** + blocage si non configuré.
- Restreindre l’OCR aux **ROI** et activer le **hash‑based skip**.
- Réduire logs console → fichier rotatif.

### P1 (Semaine 1)
- Migrer la détection de fenêtre vers **pywin32** (ou au minimum corriger `ctypes` avec `CFUNCTYPE`).
- Implémenter **cadence adaptative** OCR.
- Nettoyer l’archive (exclure `.git`, caches, assets lourds).
- Publier `requirements-minimal.txt`.

### P2 (Semaines 2–3)
- Optionnaliser GPU/C++ : fournir **pyproject.toml** (pybind11) + wheel Windows x64.
- Ajouter un **assistant de calibration** (wizard DPI/positions).
- Benchmarks automatisés (temps capture → OCR → parse → UI).

---

## 7) Validation & tests

### 7.1 Checklist fonctionnelle
- [ ] Démarrage sans Tesseract : message clair + sélection chemin.  
- [ ] Détection fenêtre : bon `HWND` + `GetWindowRect` correct.  
- [ ] OCR ROI : valeurs non vides sur table réelle.  
- [ ] UI : pas de freeze perceptible à 1 Hz (600–1000 ms).  
- [ ] Fermeture : threads `join()` en <2 s, pas d’exception.

### 7.2 Benchmarks (cibles)
- Capture ROI : **< 5 ms**  
- OCR (numérique mono‑ligne ROI) : **35–60 ms** par zone (Tesseract CPU)  
- Update UI (labels uniquement) : **< 2 ms**  
- Latence bout‑en‑bout (changement visuel → UI) : **< 150–250 ms** sans GPU

---

## 8) Risques & conformité
- **Anti‑détection/ToS** : lecture de fenêtres/écrans et assistance in‑game peuvent violer les CGU des plateformes de poker.  
  - **Recommandation** : mode “training/offline” par défaut, et avertissements explicites à l’utilisateur.

---

## 9) Annexes

### 9.1 Extrait `requirements-minimal.txt`
*(voir section 3.1)*

### 9.2 Arrêt propre des threads
```python
class Worker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._stop = threading.Event()
    def stop(self):
        self._stop.set()
    def run(self):
        while not self._stop.is_set():
            work()
        cleanup()

# À la fermeture:
for w in workers: w.stop()
for w in workers: w.join(timeout=2.0)
```

### 9.3 Notes DPI / Windows
- Activer **“Override high DPI scaling”** si l’UI n’aligne pas correctement les ROI.
- Utiliser `ctypes.windll.shcore.SetProcessDpiAwareness(2)` en début de process (Windows 10+).

---

## 10) Conclusion
La stabilité et la réactivité s’améliorent nettement en :
1) **Réutilisant les widgets** (fin des recréations),  
2) **OCR conditionnel par hash** + **ROI strictes**,  
3) **requirements** assainis, **GPU/C++ optionnels**,  
4) **pywin32** pour la gestion des fenêtres,  
5) **Fermeture propre** des threads.

Ces changements sont ciblés, peu risqués et apportent un **gain immédiat** sur la latence et la fiabilité.