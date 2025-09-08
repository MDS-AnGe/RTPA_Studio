
# RTPA Studio — Rapport d’installation & Diagnostic (Windows)

**Date**: auto-généré  
**Portée**: Analyse du script `install_rtpa_dependencies.py`, erreurs rencontrées, causes probables et correctifs, plus un plan de relance vérifiable.

---

## 0) Journal fourni (source)

```
python install_rtpa_dependencies.py
======================================================================
🚀 RTPA Studio - Installation Automatique Complète
🎯 Objectif: CFR 100% Rust pour performance maximale
======================================================================

📋 Étape 1/4: Dépendances Python
📦 Vérification dépendances Python...
✅ numpy
✅ psutil
✅ customtkinter
✅ pyautogui
✅ mss
✅ pynput
✅ requests
✅ matplotlib
✅ pandas
✅ psutil
✅ dxcam
🔄 Installation de 3 dépendances manquantes...
📥 Installation pyyaml...
✅ pyyaml installé
📥 Installation opencv-python...
✅ opencv-python installé
📥 Installation pillow...
✅ pillow installé
✅ Toutes les dépendances Python sont installées

📋 Étape 2/4: Installation Rust
✅ Rust: rustc 1.89.0 (29483883e 2025-08-04)

📋 Étape 3/4: Compilation CFR Engine Rust
🔥 Compilation CFR Engine Rust ultra-performance...
🔄 Tentative: cargo build --release
❌ Erreur avec cargo:    Compiling target-lexicon v0.12.16
   Compiling cfg-if v1.0.3
   Compiling proc-macro2 v1.0.101
   Compiling once_cell v1.21.3
   Compiling unicode-ident v1.0.18
   Compiling autocfg v1.5.0
   Compi...
🔄 Tentative: C:\Users\33769/.cargo/bin/cargo build --release
✅ CFR Engine Rust compilé avec succès
⚠️  Module compilé mais fichier bibliothèque introuvable
❌ Compilation CFR Rust échouée

📋 Étape 4/4: Test intégration CFR Rust
🧪 Test CFR Engine Rust...
❌ Erreur test CFR: module 'rust_cfr_engine' has no attribute 'RustCfrEngine'
❌ Test intégration échoué

======================================================================
⚠️  Installation partiellement réussie (2/4)
❌ Certaines fonctionnalités peuvent être limitées
💡 Relancez ce script pour compléter l'installation

```

---

## 1) Résumé exécutif

- **Python** OK (toutes dépendances installées).  
- **Rust** OK (`rustc 1.89.0`).  
- **Build Rust** KO — *Accès refusé* lors de la création du dossier `target` sous `Desktop` ⇒ protection Windows (Controlled Folder Access/OneDrive, ACL).  
- **Test Python** KO — le module `rust_cfr_engine` **n’expose pas** `RustCfrEngine` (absence d’interface PyO3 ou build non “extension module”).

**Conclusion** : Blocage principal = répertoire protégé + build non configuré pour une extension Python.

---

## 2) Causes racines (Root causes)

1. **Erreur Windows `os error 5 (Accès refusé)`**  
   - Dossier de build sous **Bureau** (`Desktop`) souvent protégé par **Controlled Folder Access** ou **OneDrive**.  
   - ACL héritées et attributs “bloqués” sur fichiers téléchargés.

2. **Chaîne de build Python↔Rust incomplète**  
   - Appel `cargo build --release` ne produit pas de `.pyd` Python importable **sans** configuration **PyO3** (`extension-module`) + **crate-type `cdylib`**.  
   - Le test d’intégration attend une classe **`RustCfrEngine`** non exposée côté Rust.

---

## 3) Correctifs recommandés (rapides)

### 3.1 Déplacer et autoriser le build
- **Déplace** le projet hors Bureau : `C:\Dev\RTPA_Studio\`  
- **Forcer** un répertoire de build Cargo sûr :

```powershell
mkdir C:\Dev\cargo_target
setx CARGO_TARGET_DIR C:\Dev\cargo_target
```

- **Débloquer** fichiers & réparer ACL (optionnel mais utile) :

```powershell
cd C:\Dev\RTPA_Studio
Get-ChildItem -Recurse | Unblock-File
icacls . /inheritance:e /grant "%USERNAME%":(F)
```

- **Éviter** si possible : désactiver temporairement Controlled Folder Access
```powershell
# Vérifier l’état
Get-MpPreference | Select ControlledFolderAccessEnabled
# (Option) désactiver temporairement
Set-MpPreference -EnableControlledFolderAccess Disabled
```

### 3.2 Chaîne PyO3 + Maturin (build module Python)

1) Installer **maturin** dans ton venv :
```powershell
pip install maturin
```

2) Dans le crate `rust_cfr_engine`, configure **Cargo.toml** :
```toml
[package]
name = "rust_cfr_engine"
version = "0.1.0"
edition = "2021"

[lib]
name = "rust_cfr_engine"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.21", features = ["extension-module"] }
```

3) Exposer l’API attendue côté Rust (`RustCfrEngine`) :
```rust
use pyo3::prelude::*;

#[pyclass]
struct RustCfrEngine {
    // champs si besoin
}

#[pymethods]
impl RustCfrEngine {
    #[new]
    fn new(_config: Option<PyObject>) -> Self { Self{} }

    fn get_status(&self, py: Python<'_>) -> PyResult<PyObject> {
        Ok(pyo3::types::PyDict::new(py).into())
    }
}

#[pymodule]
fn rust_cfr_engine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustCfrEngine>()?;
    Ok(())
}
```

4) Construire/installer l’extension dans l’environnement Python :
```powershell
# depuis la racine du projet (où se trouve rust_cfr_engine\Cargo.toml)
maturin develop -m rust_cfr_engine\Cargo.toml --release
# ou générer un wheel
maturin build   -m rust_cfr_engine\Cargo.toml --release
```

> **Attendu** : Import Python fonctionnel `import rust_cfr_engine; rust_cfr_engine.RustCfrEngine(...)`.

---

## 4) Patchs conseillés pour `install_rtpa_dependencies.py`

**Objectif** : rendre l’installation idempotente et compatible PyO3/maturin, éviter les échecs cargo sur dossiers protégés.

### 4.1 Ajouter `maturin` aux dépendances Python

```python
PYTHON_DEPENDENCIES = [
    # ...
    "maturin",
]
```

### 4.2 Forcer un CARGO_TARGET_DIR sûr

```python
import os
from pathlib import Path

os.environ.setdefault("CARGO_TARGET_DIR", str(Path.home() / "cargo_target"))
```

### 4.3 Tenter `maturin develop` avant `cargo build`

```python
cargo_commands = [
    ["maturin", "develop", "-m", "rust_cfr_engine/Cargo.toml", "--release"],
    ["cargo", "build", "--release"],
    [str(Path.home() / ".cargo" / "bin" / "cargo"), "build", "--release"],
]

# Filtrer les None et exécuter séquentiellement avec logs
```

### 4.4 Vérification d’import après build

```python
try:
    import rust_cfr_engine
    assert hasattr(rust_cfr_engine, "RustCfrEngine")
    print("✅ Module RustCfrEngine détecté")
except Exception as e:
    print("❌ Test d’intégration échoué:", e)
```

---

## 5) Procédure de relance (checklist express)

1. **Déplacer** projet → `C:\Dev\RTPA_Studio\`  
2. **Créer** `C:\Dev\cargo_target` et `setx CARGO_TARGET_DIR C:\Dev\cargo_target`  
3. `pip install maturin`  
4. Configurer **Cargo.toml** + code PyO3 (section 3.2)  
5. `maturin develop -m rust_cfr_engine\Cargo.toml --release`  
6. `python -c "import rust_cfr_engine; print(hasattr(rust_cfr_engine, 'RustCfrEngine'))"` doit retourner `True`  
7. Relancer `install_rtpa_dependencies.py` (le test d’intégration devrait passer).

---

## 6) Notes complémentaires

- Si tu restes sur `cargo build`, tu obtiendras un `.dll`/`.so` non packagé pour Python (pas de métadonnées wheel, pas d’installation site-packages). **Maturin** standardise tout ça.  
- Si le nom du module Python doit **différer** du crate, aligne le `#[pymodule] fn <name>` et le chargement.  
- En CI, exporte `CARGO_TARGET_DIR` vers un volume non surveillé/antivirus pour des builds plus rapides et stables.

---

## 7) Annexe — Commandes PowerShell prêtes à coller

```powershell
# 1) Préparer chemins sûrs
mkdir C:\Dev\RTPA_Studio -Force
mkdir C:\Dev\cargo_target -Force
setx CARGO_TARGET_DIR C:\Dev\cargo_target

# 2) Débloquer fichiers & ACL (si zip/téléchargements)
cd C:\Dev\RTPA_Studio
Get-ChildItem -Recurse | Unblock-File
icacls . /inheritance:e /grant "%USERNAME%":(F)

# 3) Installer maturin (dans venv si utilisé)
pip install maturin

# 4) Build/Install extension Python
maturin develop -m rust_cfr_engine\Cargo.toml --release

# 5) Smoke test
python - << 'PY'
import rust_cfr_engine
print("RustCfrEngine?", hasattr(rust_cfr_engine, "RustCfrEngine"))
PY
```

---

**Fin du rapport.**
