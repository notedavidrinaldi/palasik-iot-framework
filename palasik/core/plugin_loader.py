# palasik/core/plugin_loader.py

import importlib
import pkgutil
from pathlib import Path


class PluginLoader:
    """
    Loader plugin PALASIK.
    Mencari dan memuat plugin dari folder plugins/.
    """

    def __init__(self, plugins_path="plugins"):
        self.plugins_path = plugins_path

    def load(self):
        plugins = []

        if not Path(self.plugins_path).exists():
            return plugins

        for _, name, _ in pkgutil.iter_modules([self.plugins_path]):
            module_path = f"{self.plugins_path}.{name}.plugin"
            try:
                module = importlib.import_module(module_path)
                plugin_class = getattr(module, "Plugin", None)
                if plugin_class:
                    plugins.append(plugin_class())
            except Exception as e:
                # Plugin error tidak mematikan engine
                continue

        return plugins
