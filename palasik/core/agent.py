# palasik/core/agent.py

from palasik.core.context import PalasikContext
from palasik.core.engine import PalasikEngine
from palasik.core.config import ConfigLoader
from palasik.core.plugin_loader import PluginLoader


class PalasikAgent:
    """
    Entry point utama PALASIK.
    Dipakai oleh CLI dan runtime.
    """

    def __init__(self, plugins_path="plugins", config_file=None):
        # Load configuration
        self.config = ConfigLoader(config_file)

        # Build context
        self.context = PalasikContext(self.config)

        # Core engine
        self.engine = PalasikEngine(self.context)

        # Plugin loader
        self.loader = PluginLoader(plugins_path)

        # Setup optional adapters
        self._setup_optional_adapters()

    def _setup_optional_adapters(self):
        # HTTP adapter (optional)
        http_cfg = self.config.get("palasik", "http", default={})
        if http_cfg.get("enabled"):
            from palasik.adapters.http.adapter import HTTPAdapter
            self.context.http_adapter = HTTPAdapter(
                endpoint=http_cfg.get("endpoint"),
                timeout=http_cfg.get("timeout", 5),
            )

    def load_plugins(self):
        plugins = self.loader.load()
        for plugin in plugins:
            self.engine.register_plugin(plugin)

    def start(self):
        self.engine.start()

    def emit(self, event: dict):
        self.engine.emit(event)

    def stop(self):
        self.engine.stop()
