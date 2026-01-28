# palasik/core/config.py

import os
import yaml


class ConfigLoader:
    def __init__(self, config_file: str | None = None):
        self.config = {}

        if config_file:
            self.load_yaml(config_file)

        self.load_env()

    def load_yaml(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
            self.config.update(data)

    def load_env(self):
        broker = self.config.setdefault("palasik", {}).setdefault("broker", {})
        policy = self.config.setdefault("palasik", {}).setdefault("policy", {})

        broker["host"] = os.getenv("PALASIK_BROKER_HOST", broker.get("host"))
        broker["port"] = int(os.getenv("PALASIK_BROKER_PORT", broker.get("port", 1883)))

        policy["threshold"] = float(
            os.getenv("PALASIK_POLICY_THRESHOLD", policy.get("threshold", 0.5))
        )

    def get(self, *keys, default=None):
        data = self.config
        for key in keys:
            data = data.get(key, {})
        return data or default
