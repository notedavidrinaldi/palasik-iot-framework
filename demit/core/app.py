"""Base contracts untuk aplikasi di dalam ekosistem DEMIT."""

from abc import ABC, abstractmethod


class BaseDemitApp(ABC):
    """Kontrak dasar aplikasi super-app.

    Setiap aplikasi implement `start`, `handle_event`, `stop`.
    """

    app_id = "base"

    def __init__(self, app_id, config: dict | None = None):
        self.app_id = app_id
        self.config = config or {}

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def handle_event(self, event: dict) -> dict:
        pass

    def supported_routes(self) -> list[str] | None:
        return None
