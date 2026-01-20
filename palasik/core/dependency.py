import subprocess
import sys
import importlib

REQUIRED_PACKAGES = [
    "pandas",
    "matplotlib",
    "numpy"
]

def ensure_dependencies():
    """
    Pastikan semua dependency tersedia.
    Jika tidak ada → install via pip (dalam venv).
    """
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            print(f"[DEPENDENCY] Installing missing package: {pkg}")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", pkg
            ])
