import yaml

from demit.core.app import BaseDemitApp
from demit.core.runtime import DemitRuntime


class DummyApp(BaseDemitApp):
    def __init__(self, app_id, config=None):
        super().__init__(app_id, config)
        self.started = False
        self.stopped = False
        self.events = []

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def handle_event(self, event):
        self.events.append(event)
        return event

    def supported_routes(self):
        routes = self.config.get("routes")
        if isinstance(routes, list):
            return routes
        return None


def _write_config(path, apps_list, app_cfg):
    cfg = {
        "demit": {"apps": apps_list},
        "apps": app_cfg,
    }
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")


def _factory_registry():
    created = {}

    def factory(app_id, cfg):
        created[app_id] = True
        return DummyApp(app_id, cfg)

    return factory, created


def test_routing_single_app_without_app_field(tmp_path):
    config_path = tmp_path / "demit.yaml"
    _write_config(
        config_path,
        ["iot_guard"],
        {"iot_guard": {"type": "dummy"}},
    )

    factory, created = _factory_registry()
    runtime = DemitRuntime(str(config_path), app_factories={"dummy": factory})

    runtime.start()
    assert created == {"iot_guard": True}
    app = runtime.apps["iot_guard"]
    assert app.started

    out = runtime.emit({"value": 42})
    assert out == [{"value": 42}]
    assert app.events == [{"value": 42}]

    runtime.stop()
    assert app.stopped


def test_routing_by_app_field(tmp_path):
    config_path = tmp_path / "demit.yaml"
    _write_config(
        config_path,
        ["iot_guard", "another"],
        {
            "iot_guard": {"type": "dummy"},
            "another": {"type": "dummy"},
        },
    )

    runtime = DemitRuntime(
        str(config_path),
        app_factories={
            "dummy": lambda app_id, cfg: DummyApp(app_id, cfg),
        },
    )
    runtime.start()
    assert runtime.emit({"app": "iot_guard", "value": 7})[0]["app"] == "iot_guard"
    assert runtime.emit({"app": "missing", "value": 1}) == [
        {"app": "missing", "value": 1},
        {"app": "missing", "value": 1},
    ]


def test_route_field_targets_matching_apps(tmp_path):
    config_path = tmp_path / "demit.yaml"
    _write_config(
        config_path,
        ["iot_guard", "audit"],
        {
            "iot_guard": {"type": "dummy", "routes": ["palasik"]},
            "audit": {"type": "dummy", "routes": ["audit"]},
        },
    )

    runtime = DemitRuntime(
        str(config_path),
        app_factories={
            "dummy": lambda app_id, cfg: DummyApp(app_id, cfg),
        },
    )
    runtime.start()

    out = runtime.emit({"route": "palasik", "value": 99})

    assert out == [{"route": "palasik", "value": 99}]
    assert runtime.apps["iot_guard"].events == [{"route": "palasik", "value": 99}]
    assert runtime.apps["audit"].events == []
