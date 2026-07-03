# palasik/core/registry.py

class PluginRegistry:
    """
    Registry untuk menyimpan dan mengelola plugin.
    """

    def __init__(self):
        self._plugins = {}

    def register(self, plugin):
        name = self._plugin_name(plugin)
        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' already registered")
        self._plugins[name] = plugin

    @staticmethod
    def _plugin_name(plugin):
        getter = getattr(plugin, "name", None)
        if callable(getter):
            return getter()

        return plugin.__class__.__name__

    def get(self, name):
        return self._plugins.get(name)

    def all(self):
        return list(self._plugins.values())
