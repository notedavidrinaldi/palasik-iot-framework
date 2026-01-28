# palasik/core/engine.py

from palasik.core.registry import PluginRegistry

class PalasikEngine:
    """
    Engine utama PALASIK.
    Mengelola lifecycle dan event dispatch.
    """

    def __init__(self, context):
        self.context = context
        self.registry = PluginRegistry()
        self.running = False

    def register_plugin(self, plugin):
        self.registry.register(plugin)

    def start(self):
        self.running = True
        for plugin in self.registry.all():
            plugin.on_start(self.context)

    def emit(self, event: dict):
        if not self.running:
            return

        for plugin in self.registry.all():
            plugin.on_event(event, self.context)

    def stop(self):
        for plugin in self.registry.all():
            plugin.on_stop(self.context)
        self.running = False
