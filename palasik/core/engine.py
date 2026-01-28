# palasik/core/engine.py

from palasik.core.registry import PluginRegistry
from palasik.core.decision import Decision


class PalasikEngine:
    """
    Engine utama PALASIK.
    Enforcement point Zero Trust.
    """

    def __init__(self, context):
        self.context = context
        self.registry = PluginRegistry()
        self.running = False

    def register_plugin(self, plugin):
        self.registry.register(plugin)

    def start(self):
        self.running = True
        for plugin in self.registry.all():
            plugin.on_start(self.context)

    def emit(self, event: dict):
        """
        Enforcement point utama.
        Hanya event ALLOW yang diteruskan.
        """

        trust_score = self.context.trust.evaluate(event, self.context)
        decision = self.context.policy.decide(trust_score, event, self.context)

        # 🔐 ENFORCEMENT
        if decision != Decision.ALLOW.value:
            self.context.logger.info(
                f"Event blocked by policy | trust={trust_score} | event={event}"
            )
            return

        # ✅ EVENT ALLOW → plugin
        for plugin in self.registry.all():
            plugin.on_event(event, self.context)

        # ✅ EVENT ALLOW → HTTP (opsional)
        http_adapter = getattr(self.context, "http_adapter", None)
        if http_adapter:
            http_adapter.forward(event)

    def stop(self):
        for plugin in self.registry.all():
            plugin.on_stop(self.context)
        self.running = False
