# palasik/core/registry.py

class PluginRegistry:
    """
    Registry untuk menyimpan dan mengelola plugin.
    """

    def __init__(self):
        self._plugins = {}

    def register(self, plugin):
        name = plugin.name()
        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' already registered")
        self._plugins[name] = plugin

    def get(self, name):
        return self._plugins.get(name)

    def all(self):
        return list(self._plugins.values())
