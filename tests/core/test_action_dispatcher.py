from __future__ import annotations

import json

from palasik.core.action_dispatcher import ActionDispatcher, WebhookActionAdapter
from palasik.core.audit import AuditService
from palasik.core.logger import Logger
from palasik.core.metrics import RuntimeMetrics


class DummyResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code

    def raise_for_status(self):
        return None


def test_action_dispatcher_retries_and_audits(monkeypatch, tmp_path):
    calls = {"count": 0}

    def fake_post(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("timeout")
        return DummyResponse(202)

    monkeypatch.setattr("palasik.core.action_dispatcher.requests.post", fake_post)

    metrics = RuntimeMetrics()
    audit_path = tmp_path / "audit.jsonl"
    dispatcher = ActionDispatcher(
        logger=Logger(),
        metrics=metrics,
        audit_service=AuditService(str(audit_path)),
        adapters={"webhook": WebhookActionAdapter("http://example.test/hook")},
        action_map={"create_ticket": "webhook"},
        max_retries=2,
    )

    results = dispatcher.dispatch_actions(
        ["create_ticket"],
        {"event_id": "evt-1", "type": "alert", "source": {"device_id": "edge-1"}},
        trace_id="trace-1",
    )

    assert calls["count"] == 2
    assert len(results) == 1
    assert results[0].status == "success"
    assert results[0].attempt == 2
    assert metrics.actions_total == 1
    assert metrics.actions_succeeded == 1

    records = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert [item["status"] for item in records if item["record_type"] == "action"] == [
        "pending",
        "retrying",
        "success",
    ]


def test_action_dispatcher_idempotency_skips_duplicate(tmp_path):
    metrics = RuntimeMetrics()
    dispatcher = ActionDispatcher(
        logger=Logger(),
        metrics=metrics,
        audit_service=AuditService(str(tmp_path / "audit.jsonl")),
        max_retries=1,
    )

    event = {"event_id": "evt-dup", "type": "alert", "source": {"device_id": "edge-2"}}
    first = dispatcher.dispatch_actions(["notify_telegram"], event, trace_id="trace-dup")
    second = dispatcher.dispatch_actions(["notify_telegram"], event, trace_id="trace-dup")

    assert first[0].duplicate is False
    assert second[0].duplicate is True
    assert metrics.actions_total == 2
    assert metrics.duplicate_actions == 1
