# palasik/core/agent.py

from palasik.core.context import PalasikContext
from palasik.core.engine import PalasikEngine
from palasik.core.loader import PluginLoader

class PalasikAgent:
    """
    Agent runtime PALASIK.
    """

    def __init__(self, plugins_path="plugins"):
        self.context = PalasikContext()
        self.engine = PalasikEngine(self.context)
        self.loader = PluginLoader(plugins_path)

    def load_plugins(self):
        plugins = self.loader.discover()
        for plugin in plugins:
            self.engine.register_plugin(plugin)

    def start(self):
        self.engine.start()

    def emit_event(self, event: dict):
        self.engine.emit(event)

    def stop(self):
        self.engine.stop()
