# palasik/core/config.py

import os
import yaml


class ConfigLoader:
    def __init__(self, config_file: str | None = None):
        self.config: dict = {}

        if config_file:
            self.load_file(config_file)

        self.normalize()   # ⬅️ INI KUNCI
        self.load_env()

    def load_file(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        if not isinstance(data, dict):
            raise ValueError("Config file must be a YAML dictionary")

        self.config.update(data)

    def normalize(self):
        """
        Pastikan semua node penting adalah dict,
        bukan None (hasil YAML kosong).
        """
        if self.config.get("palasik") is None:
            self.config["palasik"] = {}

        palasik = self.config["palasik"]

        if palasik.get("broker") is None:
            palasik["broker"] = {}

        if palasik.get("policy") is None:
            palasik["policy"] = {}

        if palasik.get("plugins") is None:
            palasik["plugins"] = {"enabled": []}

    def load_env(self):
        palasik = self.config["palasik"]
        broker = palasik["broker"]
        policy = palasik["policy"]

        broker["host"] = os.getenv("PALASIK_BROKER_HOST", broker.get("host"))
        broker["port"] = _safe_convert_int(
            os.getenv("PALASIK_BROKER_PORT", broker.get("port", 1883)),
            default=1883,
        )

        policy["threshold"] = _safe_convert_float(
            os.getenv("PALASIK_POLICY_THRESHOLD", policy.get("threshold", 0.5)),
            default=0.5,
        )

        policy["type"] = os.getenv("PALASIK_POLICY_TYPE", policy.get("type", "allow_deny"))

        if os.getenv("PALASIK_DECISION_LOG"):
            palasik["decision_log"] = os.getenv("PALASIK_DECISION_LOG")

    def get(self, *keys, default=None):
        ref = self.config
        for k in keys:
            if not isinstance(ref, dict):
                return default
            ref = ref.get(k)
        return ref if ref is not None else default


def _safe_convert_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_convert_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
