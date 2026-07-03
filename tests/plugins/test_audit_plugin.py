import json
from pathlib import Path

from palasik.plugins.audit.plugin import AuditPlugin
from palasik.core.decision import DecisionRecord


def test_audit_plugin_writes_decision_to_file(tmp_path):
    ctx = type("DummyContext", (), {})()
    ctx.audit_log = str(tmp_path / "audit" / "trail.jsonl")
    ctx.latest_decision = DecisionRecord(
        event_id="evt-1",
        trust_score=0.5,
        decision=type("D", (), {"value": "ALLOW"})(),
        policy_name="rule",
        rationale=["ok"],
        reason_code="TRUSTED",
    )
    ctx.config = {}

    plugin = AuditPlugin()
    plugin.on_event({}, ctx)

    lines = (tmp_path / "audit" / "trail.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["event_id"] == "evt-1"
    assert data["decision"] == "ALLOW"
