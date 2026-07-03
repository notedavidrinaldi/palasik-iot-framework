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

        if palasik.get("observability") is None:
            palasik["observability"] = {}

        if palasik.get("audit_log") is None:
            palasik["audit_log"] = None

        if palasik.get("actions") is None:
            palasik["actions"] = {
                "timeout": 5,
                "max_retries": 2,
                "retry_backoff_seconds": 0.0,
                "idempotency_cache_size": 1024,
                "routes": {},
                "webhook": {},
                "telegram": {},
                "whatsapp": {},
                "relay": {},
            }

        if palasik.get("event") is None:
            palasik["event"] = {"max_age_seconds": 600}

        if palasik.get("risk") is None:
            palasik["risk"] = {
                "warn_threshold": 55,
                "quarantine_threshold": 75,
                "critical_threshold": 92,
                "critical_action": "BLOCK_ALARM",
            }

        if palasik.get("correlation") is None:
            palasik["correlation"] = {
                "window_seconds": 120,
                "repeat_threshold": 3,
                "risk_threshold": 75,
            }

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

        observability = palasik["observability"]
        if os.getenv("PALASIK_METRICS_FILE"):
            observability["metrics_file"] = os.getenv("PALASIK_METRICS_FILE")

        if os.getenv("PALASIK_DENY_SPIKE_THRESHOLD"):
            observability.setdefault("alert", {})
            observability["alert"]["deny_spike_threshold"] = os.getenv("PALASIK_DENY_SPIKE_THRESHOLD")

        if os.getenv("PALASIK_TRUST_DROP_THRESHOLD"):
            observability.setdefault("alert", {})
            observability["alert"]["trust_score_drop_threshold"] = os.getenv("PALASIK_TRUST_DROP_THRESHOLD")

        if os.getenv("PALASIK_AUDIT_LOG"):
            palasik["audit_log"] = os.getenv("PALASIK_AUDIT_LOG")

        actions = palasik["actions"]
        if os.getenv("PALASIK_ACTION_TIMEOUT"):
            actions["timeout"] = _safe_convert_float(
                os.getenv("PALASIK_ACTION_TIMEOUT"),
                default=actions.get("timeout", 5),
            )
        if os.getenv("PALASIK_ACTION_MAX_RETRIES"):
            actions["max_retries"] = _safe_convert_int(
                os.getenv("PALASIK_ACTION_MAX_RETRIES"),
                default=actions.get("max_retries", 2),
            )
        if os.getenv("PALASIK_ACTION_RETRY_BACKOFF_SECONDS"):
            actions["retry_backoff_seconds"] = _safe_convert_float(
                os.getenv("PALASIK_ACTION_RETRY_BACKOFF_SECONDS"),
                default=actions.get("retry_backoff_seconds", 0.0),
            )

        event = palasik["event"]
        if os.getenv("PALASIK_EVENT_MAX_AGE_SECONDS"):
            event["max_age_seconds"] = _safe_convert_int(
                os.getenv("PALASIK_EVENT_MAX_AGE_SECONDS"),
                default=600,
            )

        risk = palasik["risk"]
        if os.getenv("PALASIK_RISK_WARN_THRESHOLD"):
            risk["warn_threshold"] = _safe_convert_int(
                os.getenv("PALASIK_RISK_WARN_THRESHOLD"),
                default=risk.get("warn_threshold", 55),
            )

        if os.getenv("PALASIK_RISK_QUARANTINE_THRESHOLD"):
            risk["quarantine_threshold"] = _safe_convert_int(
                os.getenv("PALASIK_RISK_QUARANTINE_THRESHOLD"),
                default=risk.get("quarantine_threshold", 75),
            )

        if os.getenv("PALASIK_RISK_CRITICAL_THRESHOLD"):
            risk["critical_threshold"] = _safe_convert_int(
                os.getenv("PALASIK_RISK_CRITICAL_THRESHOLD"),
                default=risk.get("critical_threshold", 92),
            )

        if os.getenv("PALASIK_RISK_CRITICAL_ACTION"):
            risk["critical_action"] = os.getenv("PALASIK_RISK_CRITICAL_ACTION")

        correlation = palasik["correlation"]
        if os.getenv("PALASIK_CORRELATION_WINDOW_SECONDS"):
            correlation["window_seconds"] = _safe_convert_int(
                os.getenv("PALASIK_CORRELATION_WINDOW_SECONDS"),
                default=correlation.get("window_seconds", 120),
            )

        if os.getenv("PALASIK_CORRELATION_REPEAT_THRESHOLD"):
            correlation["repeat_threshold"] = _safe_convert_int(
                os.getenv("PALASIK_CORRELATION_REPEAT_THRESHOLD"),
                default=correlation.get("repeat_threshold", 3),
            )

        if os.getenv("PALASIK_CORRELATION_RISK_THRESHOLD"):
            correlation["risk_threshold"] = _safe_convert_int(
                os.getenv("PALASIK_CORRELATION_RISK_THRESHOLD"),
                default=correlation.get("risk_threshold", 75),
            )

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
