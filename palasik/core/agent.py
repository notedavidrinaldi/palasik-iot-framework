# palasik/core/agent.py

from palasik.core.context import PalasikContext
from palasik.core.engine import PalasikEngine
from palasik.core.loader import PluginLoader
from palasik.core.config import ConfigLoader

class PalasikAgent:
    """
    Agent runtime PALASIK.
    """

    def __init__(self, plugins_path="plugins", config_file=None):
    self.config = ConfigLoader(config_file)
    self.context = PalasikContext(self.config)
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

http_cfg = self.config.get("palasik", "http", default={})
if http_cfg.get("enabled"):
    from palasik.adapters.http.adapter import HTTPAdapter
    self.context.http_adapter = HTTPAdapter(
        endpoint=http_cfg.get("endpoint"),
        timeout=http_cfg.get("timeout", 5),
    )
