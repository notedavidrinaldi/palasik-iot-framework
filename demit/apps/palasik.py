"""Integrasi aplikasi PALASIK di super-app DEMIT."""

from demit.core.app import BaseDemitApp
from palasik.core.agent import PalasikAgent


class PalasikDemitApp(BaseDemitApp):
    """Satu aplikasi DEMIT: PALASIK."""

    def __init__(self, app_id: str, config: dict | None = None):
        super().__init__(app_id, config)
        self.agent = None
        routes = config.get("routes") if config else None
        self._routes = routes if isinstance(routes, list) else None

    def start(self):
        cfg_path = self.config.get("config_file", "config.yaml")
        plugin_path = self.config.get("plugins_path", "plugins")

        self.agent = PalasikAgent(
            plugins_path=plugin_path,
            config_file=cfg_path,
        )
        self.agent.load_plugins()
        self.agent.start()

    def stop(self):
        if self.agent is not None:
            self.agent.stop()

    def handle_event(self, event: dict) -> dict:
        if self.agent is None:
            self.start()

        normalized = dict(event)
        # Tetap kirim event_id agar dapat jejak keputusan per-event
        self.agent.emit(normalized)
        return normalized

    def supported_routes(self) -> list[str] | None:
        if self._routes is None:
            return None
        return [str(route) for route in self._routes]
