from palasik.policy.allow_deny import AllowDenyPolicy
from palasik.core.engine import PalasikEngine
from palasik.core.context import PalasikContext

class DummyTrust:
    def evaluate(self, event, context):
        return event["trust"]

class DummyPlugin:
    def __init__(self):
        self.called = False

    def on_event(self, event, context):
        self.called = True

def test_event_denied_not_reach_plugin():
    context = PalasikContext()
    context.trust = DummyTrust()
    context.policy = AllowDenyPolicy(threshold=0.7)

    engine = PalasikEngine(context)
    plugin = DummyPlugin()
    engine.register_plugin(plugin)

    engine.emit({"trust": 0.3})

    assert plugin.called is False
