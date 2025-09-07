#!/usr/bin/env python3
# RTPA Studio — Installateur automatique (Windows/macOS/Linux)

from __future__ import annotations
import os, sys, subprocess, platform, shutil
from pathlib import Path

def run(cmd, check=True, capture=True, shell=False):
    return subprocess.run(cmd if not shell else " ".join(cmd),
                          check=check, capture_output=capture, text=True, shell=shell)
def which(exe:str)->str|None: return shutil.which(exe)
def info(msg): print(msg)
def ok(msg):   print(f"✅ {msg}")
def warn(msg): print(f"⚠️  {msg}")
def err(msg):  print(f"❌ {msg}")

class RTPAInstaller:
    def __init__(self):
        self.system = platform.system().lower()  # windows / darwin / linux
        self.arch = platform.machine()
        self.pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.errors:list[str] = []
        Path("config").mkdir(exist_ok=True)

    # ---------------- Main ----------------
    def run(self)->bool:
        self.header()
        ok_all = True
        ok_all &= self.check_python()
        ok_all &= self.install_tesseract()
        ok_all &= self.install_python_deps()
        ok_all &= self.setup_dirs()
        ok_all &= self.configure_pytesseract()
        ok_all &= self.test_imports()
        self.footer(ok_all)
        return bool(ok_all)

    # ---------------- UI ----------------
    def header(self):
        print("🎯 RTPA STUDIO - INSTALLATEUR AUTOMATIQUE")
        print("=======================================================")
        print(f"Système : {platform.system()} {platform.release()}  ({self.arch})")
        print(f"Python  : {platform.python_version()}\n")
        print("⚠️  Usage strictement éducatif / recherche académique.\n")

    def footer(self, success:bool):
        print()
        if success and not self.errors:
            ok("INSTALLATION COMPLÈTE")
        else:
            err("INSTALLATION INCOMPLÈTE")
            for e in self.errors:
                print("   •", e)
        print("\n📚 CONSEILS")
        if self.system == "windows":
            print(" - Pour Tesseract : 'winget install -e --id UB-Mannheim.TesseractOCR'")
        elif self.system == "darwin":
            print(" - 'brew install tesseract'")
        else:
            print(" - 'sudo apt install tesseract-ocr' (ou dnf/pacman)")

    # ---------------- Steps ----------------
    def check_python(self)->bool:
        info("🐍 Vérification version Python…")
        if sys.version_info < (3,8):
            err("Python 3.8+ requis.")
            self.errors.append("Version Python trop ancienne")
            return False
        ok(f"Python {self.pyver} OK")
        return True

    # ---- Tesseract ----
    def tesseract_paths_windows(self):
        return [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]

    def tesseract_installed(self)->bool:
        if which("tesseract"):
            return True
        if self.system == "windows":
            for p in self.tesseract_paths_windows():
                if Path(p).exists():
                    return True
        return False

    def set_tesseract_env(self, exe_path:Path)->None:
        # Ajoute le dossier au PATH courant et configure pytesseract
        parent = str(Path(exe_path).parent)
        os.environ["PATH"] = parent + os.pathsep + os.environ.get("PATH","")
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = str(exe_path)
        except Exception as e:
            warn(f"pytesseract non disponible au moment de la config: {e}")
        # Persiste le chemin pour l’app
        Path("config/tesseract_path.txt").write_text(str(exe_path), encoding="utf-8")

    def install_tesseract(self)->bool:
        info("👁️ Installation / vérification Tesseract OCR…")
        if self.tesseract_installed():
            ok("Tesseract déjà présent")
            return True

        try:
            if self.system == "windows":
                return self._install_tesseract_windows()
            elif self.system == "darwin":
                return self._install_tesseract_macos()
            elif self.system == "linux":
                return self._install_tesseract_linux()
            else:
                err(f"Système non supporté: {self.system}")
                self.errors.append("Tesseract: système non supporté")
                return False
        except subprocess.CalledProcessError as e:
            err(f"Installation Tesseract: {e}")
            self.errors.append("Tesseract: échec installation")
            return False

    def _install_tesseract_windows(self)->bool:
        if which("winget"):
            try:
                info("📦 winget → UB-Mannheim.TesseractOCR")
                run([
                    "winget","install","-e","--id","UB-Mannheim.TesseractOCR",
                    "--silent","--accept-package-agreements","--accept-source-agreements"
                ])
                # Cherche le binaire et configure PATH + pytesseract
                for p in self.tesseract_paths_windows():
                    if Path(p).exists():
                        self.set_tesseract_env(Path(p))
                        ok(f"Tesseract installé via winget ({p})")
                        return True
                warn("Tesseract installé mais binaire non trouvé aux chemins standards.")
            except subprocess.CalledProcessError as e:
                warn(f"winget échec: {e}")

        err("Installation Tesseract requise manuellement.")
        print("   ➜ https://github.com/UB-Mannheim/tesseract/releases")
        self.errors.append("Tesseract: installation manuelle requise")
        return False

    def _install_tesseract_macos(self)->bool:
        if not which("brew"):
            err("Homebrew requis: https://brew.sh/")
            self.errors.append("brew manquant (macOS)")
            return False
        run(["brew","install","tesseract"])
        ok("Tesseract installé (macOS)")
        return True

    def _install_tesseract_linux(self)->bool:
        pm_cmds = [
            (which("apt"),   ["sudo","apt","update"], ["sudo","apt","install","-y","tesseract-ocr"]),
            (which("dnf"),   None,                    ["sudo","dnf","install","-y","tesseract"]),
            (which("yum"),   None,                    ["sudo","yum","install","-y","tesseract"]),
            (which("pacman"),None,                    ["sudo","pacman","-S","--noconfirm","tesseract"]),
        ]
        for pm, pre, inst in pm_cmds:
            if pm:
                if pre: run(pre)
                run(inst)
                ok("Tesseract installé (Linux)")
                return True
        err("Gestionnaire de paquets non détecté. Installez Tesseract manuellement.")
        self.errors.append("Tesseract: installation manuelle (Linux)")
        return False

    # ---- Dépendances Python ----
    def install_python_deps(self)->bool:
        info("📦 Installation des dépendances Python…")
        base = [
            "pip>=24.0","setuptools>=68.0","wheel>=0.41.0",
            "numpy>=1.24.0","pillow>=9.0.0","opencv-python>=4.8.0",
            "pytesseract>=0.3.10","mss>=6.1.0","psutil>=5.9.0",
            "pyyaml>=6.0","matplotlib>=3.7.0","seaborn>=0.12.0",
            "scipy>=1.10.0","customtkinter>=5.0.0","pybind11>=2.12.0",
        ]
        opt = ["numba>=0.56.0"]
        try:
            info("⬆️ Mise à jour pip/setuptools/wheel…")
            run([sys.executable,"-m","pip","install","--upgrade"] + base)
            for pkg in opt:
                try:
                    info(f"📥 (optionnel) {pkg}…")
                    run([sys.executable,"-m","pip","install",pkg])
                except subprocess.CalledProcessError as e:
                    warn(f"{pkg} non installé (optionnel): {e}")
            ok("Dépendances installées")
            return True
        except subprocess.CalledProcessError as e:
            err(f"Échec installation dépendances: {e}")
            self.errors.append("pip install a échoué")
            return False

    # ---- Dossiers ----
    def setup_dirs(self)->bool:
        info("📁 Création des répertoires…")
        for d in ["logs","config","attached_assets/generated_images","exports"]:
            Path(d).mkdir(parents=True, exist_ok=True)
            ok(f"{d}/")
        return True

    # ---- Config pytesseract ----
    def configure_pytesseract(self)->bool:
        info("⚙️ Configuration Tesseract pour pytesseract…")

        # 0) Si un chemin est stocké, l'utiliser
        cfg_path = Path("config/tesseract_path.txt")
        if cfg_path.exists():
            exe = Path(cfg_path.read_text(encoding="utf-8").strip())
            if exe.exists():
                self.set_tesseract_env(exe)
                ok(f"Tesseract configuré (config): {exe}")
                return True

        # 1) Si binaire trouvé via which()
        w = which("tesseract")
        if w:
            self.set_tesseract_env(Path(w))
            ok(f"Tesseract configuré (PATH): {w}")
            return True

        # 2) Windows: chemins standards
        if self.system == "windows":
            for p in self.tesseract_paths_windows():
                if Path(p).exists():
                    self.set_tesseract_env(Path(p))
                    ok(f"Tesseract configuré: {p}")
                    return True

        warn("Tesseract non trouvé — configurez manuellement si besoin.")
        return True  # on ne bloque pas ici

    # ---- Tests ----
    def test_imports(self)->bool:
        info("🧪 Test d’imports…")
        tests = [
            ("numpy","numpy.__version__"),
            ("cv2","cv2.__version__"),
            ("pytesseract","pytesseract.get_tesseract_version() if hasattr(pytesseract,'get_tesseract_version') else 'OK'"),
            ("PIL","'OK'"),
            ("yaml","'OK'"),
            ("matplotlib","'OK'"),
            ("scipy","'OK'"),
        ]
        ok_all = True
        for mod, expr in tests:
            try:
                m = __import__(mod)
                val = eval(expr, {mod:m}, {})
                ok(f"{mod} import OK ({val})")
            except Exception as e:
                warn(f"{mod} indisponible: {e}")
                ok_all = False
        if not ok_all:
            self.errors.append("Certains modules Python manquent (voir messages)")
        return True

# ---------------- Entrée ----------------
if __name__ == "__main__":
    RTPAInstaller().run()
