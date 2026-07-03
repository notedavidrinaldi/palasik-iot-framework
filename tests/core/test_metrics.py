from pathlib import Path
from datetime import datetime, timedelta, timezone

from palasik.core.metrics import RuntimeMetrics


def test_metrics_record_and_snapshot():
    m = RuntimeMetrics()
    m.record("ALLOW", "TRUSTED", 10.0, 0.8)
    m.record("DENY", "UNKNOWN", 20.0, 0.2, correlated=True)
    m.record("DENY", None, 30.0, 0.3)
    m.record_action("success")
    m.record_action("failed")
    m.record_action("success", duplicate=True)

    snapshot = m.as_dict()

    assert snapshot["events_total"] == 3
    assert snapshot["events_allowed"] == 1
    assert snapshot["events_denied"] == 2
    assert snapshot["reason_code_breakdown"] == {"TRUSTED": 1, "UNKNOWN": 1}
    assert snapshot["pipeline_avg_latency_ms"] == round((10.0 + 20.0 + 30.0) / 3, 3)
    assert snapshot["deny_ratio"] == round(2 / 3, 3)
    assert snapshot["actions_total"] == 3
    assert snapshot["actions_failed"] == 1
    assert snapshot["actions_succeeded"] == 2
    assert snapshot["duplicate_actions"] == 1
    assert snapshot["failed_action_rate"] == round(1 / 3, 3)
    assert snapshot["correlation_hit_count"] == 1
    assert snapshot["health_status"] == "UP"
    assert snapshot["health_transition_count"] == 0


def test_metrics_dump_and_reload(tmp_path: Path):
    metrics_path = tmp_path / "metrics.json"
    source = RuntimeMetrics()
    source.record("ALLOW", "A", 10.0, 0.5)
    source.record_action("success")
    source.dump_to_file(str(metrics_path))

    restored, loaded_path = RuntimeMetrics.from_file(str(metrics_path))
    assert loaded_path == str(metrics_path)
    assert restored.events_total == 1
    assert restored.actions_total == 1
    assert restored.reason_code_breakdown == {"A": 1}


def test_metrics_track_health_transitions_and_alerts():
    m = RuntimeMetrics()
    m.observe_health("DEGRADED", ["latest action failure: action=create_ticket event_id=evt-1"])
    m.observe_health("DOWN", ["audit_service is not initialized"])
    m.observe_health("DEGRADED", ["latest action failure: action=create_ticket event_id=evt-2"])

    degraded_since = (datetime.now(timezone.utc) - timedelta(seconds=120)).replace(microsecond=0)
    m.health_status_since_utc = degraded_since.isoformat().replace("+00:00", "Z")
    m.health_last_transition_utc = m.health_status_since_utc

    snapshot = m.as_dict()
    alerts = m.evaluate_alerts(
        {
            "health_degraded_for_seconds": 30,
            "health_down_for_seconds": 0,
            "failed_action_rate_threshold": 1.0,
        }
    )

    assert snapshot["health_transition_count"] == 3
    assert snapshot["health_status_breakdown"]["DEGRADED"] == 2
    assert snapshot["health_status_breakdown"]["DOWN"] == 1
    assert snapshot["health_last_reason"] == "latest action failure: action=create_ticket event_id=evt-2"
    assert any(item["type"] == "health_degraded" for item in alerts)
