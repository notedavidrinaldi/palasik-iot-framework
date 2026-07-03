from datetime import datetime, timedelta, timezone

from palasik.core.context import PalasikContext
from palasik.core.engine import PalasikEngine
from palasik.core.risk import RiskEngine


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


def test_risk_engine_keeps_allow_when_risk_is_low():
    engine = RiskEngine()

    score, details = engine.score(0.9, {"trust_ctx": {}}, "ALLOW")

    assert score == 10
    assert "base_from_trust=10" in details
    assert engine.escalate("ALLOW", score) == "ALLOW"


def test_risk_engine_escalates_allow_to_warn_and_block_alarm():
    engine = RiskEngine()

    assert engine.escalate("ALLOW", 60) == "WARN"
    assert engine.escalate("ALLOW", 80) == "QUARANTINE"
    assert engine.escalate("ALLOW", 95) == "BLOCK_ALARM"


def test_invalid_event_is_denied_with_reason_code():
    context = PalasikContext()
    context.trust = DummyTrust()
    context.policy = DummyPolicy("ALLOW")

    engine = PalasikEngine(context)
    engine.emit({"trust": 0.9, "timestamp": "not-iso"})

    assert context.latest_decision.decision.value == "DENY"
    assert context.latest_decision.reason_code == "INVALID_SCHEMA"
    assert "event_contract=timestamp tidak valid (ISO-8601 dibutuhkan)" in context.latest_decision.rationale


def test_correlation_escalates_repeated_high_risk_events():
    context = PalasikContext()
    context.trust = DummyTrust()
    context.policy = DummyPolicy("ALLOW")

    engine = PalasikEngine(context)
    base_time = datetime.now(timezone.utc).replace(microsecond=0)

    for offset in range(2):
        engine.emit(
            {
                "trust": 0.05,
                "timestamp": (base_time + timedelta(seconds=offset)).isoformat().replace("+00:00", "Z"),
                "source": {"device_id": "sensor-burst", "ip": "10.0.0.9"},
                "type": "vibration",
            }
        )
        assert context.latest_decision.correlation_id is None

    engine.emit(
        {
            "trust": 0.05,
            "timestamp": (base_time + timedelta(seconds=3)).isoformat().replace("+00:00", "Z"),
            "source": {"device_id": "sensor-burst", "ip": "10.0.0.9"},
            "type": "vibration",
        }
    )

    assert context.latest_decision.decision.value == "BLOCK_ALARM"
    assert context.latest_decision.correlation_id is not None
    assert "correlation_hit=count=3" in context.latest_decision.rationale
    assert "create_ticket" in (context.latest_decision.actions or [])
