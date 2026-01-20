import importlib
import subprocess
import sys

REQUIRED_PACKAGES = {
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "numpy": "numpy",
    "sklearn": "scikit-learn"
}

def ensure_dependencies():
    for module, package in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module)
        except ImportError:
            print(f"📦 Installing missing dependency: {package}")
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                package
            ])
