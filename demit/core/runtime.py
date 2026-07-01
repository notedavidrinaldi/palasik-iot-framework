"""DEMIT runtime: orchestrator multi-aplikasi."""

from __future__ import annotations

from typing import Dict
from pathlib import Path
import importlib
import threading

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency for config files
    yaml = None

from demit.core.app import BaseDemitApp


DEFAULT_APP_FACTORIES = {
    "palasik": lambda app_id, cfg: _build_palasik_app(app_id, cfg),
}


def _build_palasik_app(app_id: str, cfg: dict):
    from demit.apps.palasik import PalasikDemitApp
    return PalasikDemitApp(app_id, cfg)


class DemitRuntime:
    """Menjalankan beberapa aplikasi di bawah satu runtime DEMIT."""

    def __init__(self, config_path: str | None = None, app_factories=None):
        self.config_path = config_path or "demit.yaml"
        self.config = self._load_config(self.config_path)
        self.apps: Dict[str, BaseDemitApp] = {}
        self._running = False
        self._stop_event = threading.Event()

        self._factories = DEFAULT_APP_FACTORIES.copy()
        if app_factories:
            self._factories.update(app_factories)

        self._load_active_apps()

    def _load_config(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {
                "demit": {"apps": []},
                "apps": {},
            }

        if yaml is None:
            raise RuntimeError("PyYAML diperlukan untuk membaca demit.yaml. Install: pip install pyyaml")

        with p.open("r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        if not isinstance(cfg, dict):
            raise ValueError("DEMIT config must be a YAML object")

        return cfg

    def _load_active_apps(self):
        de_mit_cfg = self.config.get("demit", {}) or {}
        active_apps = de_mit_cfg.get("apps", []) or []

        app_cfg_root = self.config.get("apps", {}) or {}
        if not isinstance(app_cfg_root, dict):
            app_cfg_root = {}

        for app_id in active_apps:
            if not isinstance(app_id, str):
                continue

            cfg = app_cfg_root.get(app_id, {})
            if not isinstance(cfg, dict):
                cfg = {}

            kind = cfg.get("type", app_id)
            factory = self._factories.get(kind)
            if not factory:
                # fallback dinamis (opsional)
                module_name = cfg.get("module")
                class_name = cfg.get("class")
                if module_name and class_name:
                    factory = self._make_dynamic_factory(module_name, class_name)
                else:
                    continue

            app = factory(app_id, cfg)
            if isinstance(app, BaseDemitApp):
                self.apps[app_id] = app

    def _make_dynamic_factory(self, module_name: str, class_name: str):
        def _factory(app_id, cfg):
            module = importlib.import_module(module_name)
            app_cls = getattr(module, class_name)
            return app_cls(app_id, cfg)
        return _factory

    def start(self):
        self._running = True
        for app_id in list(self.apps):
            self.apps[app_id].start()

    def stop(self):
        for app_id in list(self.apps):
            try:
                self.apps[app_id].stop()
            finally:
                pass
        self._running = False
        self._stop_event.set()

    def emit(self, event: dict) -> list[dict]:
        event = dict(event or {})
        if not isinstance(event, dict):
            return []

        target = event.get("app")
        route = event.get("route", target)
        if not target and not self.apps:
            return []

        if not target:
            if len(self.apps) == 1:
                target = next(iter(self.apps))
            else:
                return self._emit_to_matching_apps(event, route)

        app = self.apps.get(target)
        if app:
            return [app.handle_event(event)]

        return self._emit_to_matching_apps(event, route)

    def _emit_to_matching_apps(self, event: dict, route: str | None) -> list[dict]:
        results: list[dict] = []
        for app in self.apps.values():
            allowed = app.supported_routes()
            if allowed is None or route is None:
                results.append(app.handle_event(event))
                continue

            if route in allowed:
                results.append(app.handle_event(event))
        return results
