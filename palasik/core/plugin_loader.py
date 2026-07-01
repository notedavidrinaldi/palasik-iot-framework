# palasik/core/plugin_loader.py

import importlib
import inspect
import pkgutil
from pathlib import Path

from palasik.core.plugin import PalasikPlugin


class PluginLoader:
    """
    Loader plugin PALASIK.
    Mencari dan memuat plugin dari folder plugins/.
    """

    def __init__(self, plugins_path="plugins"):
        self.plugins_path = plugins_path

    def load(self, only_names=None):
        plugins = []
        only_names = {name for name in (only_names or []) if name}
        enabled = None if not only_names else set(only_names)

        if not Path(self.plugins_path).exists():
            return plugins

        for _, name, _ in pkgutil.iter_modules([self.plugins_path]):
            if enabled is not None and name not in enabled:
                continue

            module_path = f"{self.plugins_path}.{name}.plugin"
            try:
                module = importlib.import_module(module_path)

                plugin_class = self._resolve_plugin_class(module)
                if plugin_class is None:
                    continue

                plugins.append(plugin_class())
            except Exception as e:
                print(f"[PALASIK] Failed load plugin '{name}': {e}")
                continue

        return plugins

    @staticmethod
    def _resolve_plugin_class(module):
        explicit = getattr(module, "Plugin", None)
        if (
            explicit
            and inspect.isclass(explicit)
            and issubclass(explicit, PalasikPlugin)
            and not inspect.isabstract(explicit)
        ):
            return explicit

        candidates = []
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                obj is PalasikPlugin
                or inspect.isabstract(obj)
                or not issubclass(obj, PalasikPlugin)
            ):
                continue
            if obj.__module__ != module.__name__:
                continue
            candidates.append(obj)

        return candidates[0] if candidates else None
