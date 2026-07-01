from palasik.core.decision import Decision
from palasik.core.engine import PalasikEngine
from palasik.core.context import PalasikContext


class DummyTrust:
    def evaluate(self, event, context):
        return event["trust"]


class DummyPolicy:
    def __init__(self, decision):
        self._decision = decision

    def name(self):
        return "dummy"

    def decide(self, trust_score, event, context):
        return self._decision

    def explain(self, trust_score, event, context):
        return [f"forced={self._decision}"]


class DummyPlugin:
    def __init__(self):
        self.called = 0

    def on_start(self, context):
        pass

    def on_event(self, event, context):
        self.called += 1

    def on_stop(self, context):
        pass


def test_monitor_and_restrict_trigger_plugin():
    for decision in ["MONITOR", "RESTRICT", Decision.ALLOW]:
        context = PalasikContext()
        context.trust = DummyTrust()
        context.policy = DummyPolicy(decision)

        engine = PalasikEngine(context)
        plugin = DummyPlugin()
        engine.register_plugin(plugin)

        engine.emit({"trust": 0.5})

        assert plugin.called == 1


def test_deny_blocks_plugin():
    context = PalasikContext()
    context.trust = DummyTrust()
    context.policy = DummyPolicy("DENY")

    engine = PalasikEngine(context)
    plugin = DummyPlugin()
    engine.register_plugin(plugin)

    engine.emit({"trust": 0.5})

    assert plugin.called == 0


def test_decision_log_written_if_configured(tmp_path):
    context = PalasikContext()
    context.trust = DummyTrust()
    context.policy = DummyPolicy("ALLOW")
    context.decision_log = str(tmp_path / "decisions" / "events.jsonl")

    engine = PalasikEngine(context)

    engine.emit({"trust": 0.9})

    lines = (tmp_path / "decisions" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert "\"decision\": \"ALLOW\"" in lines[0]
    assert context.latest_decision.decision == Decision.ALLOW


def test_challenge_can_be_passed_through_event():
    context = PalasikContext()
    context.trust = DummyTrust()
    context.policy = DummyPolicy("CHALLENGE")

    engine = PalasikEngine(context)
    plugin = DummyPlugin()
    engine.register_plugin(plugin)

    engine.emit({"trust": 0.5, "challenge_passed": True})

    assert plugin.called == 1
    assert context.latest_decision.decision == Decision.ALLOW


def test_challenge_handler_allows_or_denies():
    context = PalasikContext()
    context.trust = DummyTrust()
    context.policy = DummyPolicy("CHALLENGE")
    context.challenge_handler = lambda event, _context, _record: event.get("code") == "ok"

    engine = PalasikEngine(context)
    plugin = DummyPlugin()
    engine.register_plugin(plugin)

    engine.emit({"trust": 0.5, "code": "bad"})
    assert plugin.called == 0
    assert context.latest_decision.decision == Decision.DENY

    engine.emit({"trust": 0.5, "code": "ok"})
    assert plugin.called == 1
    assert context.latest_decision.decision == Decision.ALLOW
