# palasik/core/agent.py

from palasik.core.context import PalasikContext
from palasik.core.engine import PalasikEngine
from palasik.core.action_dispatcher import (
    ActionDispatcher,
    HTTPForwardActionAdapter,
    LoggingActionAdapter,
    RelayActionAdapter,
    TelegramActionAdapter,
    WebhookActionAdapter,
    WhatsAppActionAdapter,
)
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

        actions_cfg = self.config.get("palasik", "actions", default={}) or {}
        adapters = {
            "logger": LoggingActionAdapter(self.context.logger),
        }

        webhook_cfg = actions_cfg.get("webhook", {}) or {}
        if webhook_cfg.get("endpoint"):
            adapters["webhook"] = WebhookActionAdapter(
                endpoint=webhook_cfg.get("endpoint"),
                headers=webhook_cfg.get("headers"),
            )

        telegram_cfg = actions_cfg.get("telegram", {}) or {}
        if telegram_cfg.get("bot_token") and telegram_cfg.get("chat_id"):
            adapters["telegram"] = TelegramActionAdapter(
                bot_token=telegram_cfg.get("bot_token"),
                chat_id=telegram_cfg.get("chat_id"),
            )

        whatsapp_cfg = actions_cfg.get("whatsapp", {}) or {}
        if whatsapp_cfg.get("endpoint"):
            adapters["whatsapp"] = WhatsAppActionAdapter(
                endpoint=whatsapp_cfg.get("endpoint"),
                headers=whatsapp_cfg.get("headers"),
            )

        relay_cfg = actions_cfg.get("relay", {}) or {}
        if relay_cfg.get("endpoint"):
            adapters["relay"] = RelayActionAdapter(
                endpoint=relay_cfg.get("endpoint"),
                headers=relay_cfg.get("headers"),
            )

        if self.context.http_adapter is not None:
            adapters["http_forward"] = HTTPForwardActionAdapter(self.context.http_adapter)

        self.context.audit_service.path = self.context.audit_log
        self.context.action_dispatcher = ActionDispatcher(
            logger=self.context.logger,
            metrics=self.context.metrics,
            audit_service=self.context.audit_service,
            adapters=adapters,
            action_map=actions_cfg.get("routes", {}) or {},
            default_timeout=actions_cfg.get("timeout", 5),
            max_retries=actions_cfg.get("max_retries", 2),
            retry_backoff_seconds=actions_cfg.get("retry_backoff_seconds", 0.0),
            idempotency_ttl=actions_cfg.get("idempotency_cache_size", 1024),
        )

    def load_plugins(self):
        plugins_cfg = self.config.get("palasik", "plugins", default={}) or {}
        enabled = plugins_cfg.get("enabled")
        if enabled is None:
            enabled = []
        elif isinstance(enabled, str):
            enabled = [enabled]
        elif not isinstance(enabled, (list, tuple, set)):
            enabled = []
        else:
            enabled = [name for name in enabled if name]

        plugins = self.loader.load(only_names=enabled)
        for plugin in plugins:
            self.engine.register_plugin(plugin)

    def start(self):
        self.engine.start()

    def emit_event(self, event: dict):
        self.emit(event)

    def emit(self, event: dict):
        self.engine.emit(event)

    def stop(self):
        self.engine.stop()
