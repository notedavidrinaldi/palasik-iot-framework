from pathlib import Path

from palasik.core.plugin_loader import PluginLoader


def _create_plugin(path: Path, class_name: str, plugin_name: str):
    path.mkdir(parents=True, exist_ok=True)
    plugin_file = path / "plugin.py"
    plugin_file.write_text(
        f"""
from palasik.core.plugin import PalasikPlugin


class {class_name}(PalasikPlugin):
    def name(self):
        return \"{plugin_name}\"

    def version(self):
        return \"0.1.0\"

    def on_start(self, context):
        pass

    def on_event(self, event, context):
        pass

    def on_stop(self, context):
        pass
"""
    )


def test_plugin_loader_supports_subclass_name(tmp_path, monkeypatch):
    (tmp_path / "plugins").mkdir()
    _create_plugin(tmp_path / "plugins/logger", "LoggerPlugin", "logger")
    monkeypatch.syspath_prepend(str(tmp_path))

    loader = PluginLoader(plugins_path=str(tmp_path / "plugins"))
    plugins = loader.load()

    assert len(plugins) == 1
    assert plugins[0].name() == "logger"


def test_plugin_loader_loads_only_enabled(tmp_path, monkeypatch):
    (tmp_path / "plugins").mkdir()
    _create_plugin(tmp_path / "plugins/logger", "LoggerPlugin", "logger")
    _create_plugin(tmp_path / "plugins/firewall", "FirewallPlugin", "firewall")
    monkeypatch.syspath_prepend(str(tmp_path))

    loader = PluginLoader(plugins_path=str(tmp_path / "plugins"))
    plugins = loader.load(only_names=["logger"])

    assert len(plugins) == 1
    assert plugins[0].name() == "logger"
