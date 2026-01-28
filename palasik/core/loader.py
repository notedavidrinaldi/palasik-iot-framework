# palasik/core/loader.py

import importlib.util
import os
import inspect

from palasik.core.plugin import PalasikPlugin

class PluginLoader:
    """
    Auto discovery dan loader plugin PALASIK.
    """

    def __init__(self, plugins_path="plugins"):
        self.plugins_path = plugins_path

    def discover(self):
        plugins = []

        if not os.path.isdir(self.plugins_path):
            return plugins

        for name in os.listdir(self.plugins_path):
            plugin_dir = os.path.join(self.plugins_path, name)
            plugin_file = os.path.join(plugin_dir, "plugin.py")

            if not os.path.isfile(plugin_file):
                continue

            spec = importlib.util.spec_from_file_location(
                f"plugins.{name}",
                plugin_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, PalasikPlugin) and obj is not PalasikPlugin:
                    plugins.append(obj())

        return plugins
