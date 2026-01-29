import tempfile
import yaml
from palasik.core.config import ConfigLoader


def test_config_load_basic_yaml():
    config_data = {
        "palasik": {
            "broker": {"host": "localhost", "port": 1883},
            "policy": {"threshold": 0.8},
        }
    }

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml") as f:
        yaml.dump(config_data, f)
        f.flush()

        cfg = ConfigLoader(f.name)

        assert cfg.get("palasik", "broker", "host") == "localhost"
        assert cfg.get("palasik", "policy", "threshold") == 0.8


def test_config_handle_null_nodes():
    config_data = {"palasik": None}

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml") as f:
        yaml.dump(config_data, f)
        f.flush()

        cfg = ConfigLoader(f.name)

        assert isinstance(cfg.get("palasik"), dict)
