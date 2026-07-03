import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import yaml
import pytest

from palasik.cli.main import (
    _collect_startup_issues,
    _normalize_event_payload,
    _build_status_payload,
    _resolve_decision_payload,
    _validate_policy,
    cmd_check_startup,
    cmd_install_systemd,
    cmd_policy_deploy_check,
    cmd_policy_rollback,
    cmd_policy_snapshot,
)
from palasik.core.agent import PalasikAgent


def _write_config(path: Path):
    config_data = {
        "palasik": {
            "broker": {
                "host": "localhost",
                "port": 1883,
                "topic": "palasik/sensor/#",
            },
            "policy": {
                "version": "1",
                "default_deny": True,
                "default_action": "DENY",
                "type": "rule",
                "rules": [
                    {
                        "id": "deny_unknown_device",
                        "action": "DENY",
                        "reason_code": "UNKNOWN_DEVICE",
                        "condition": {
                            "op": "eq",
                            "key": "source.device_id",
                            "value": "unknown",
                        },
                    },
                    {
                        "id": "allow_trusted_device",
                        "action": "ALLOW",
                        "reason_code": "TRUSTED_DEVICE",
                        "condition": {
                            "op": "gte",
                            "key": "trust_score",
                            "value": 0.75,
                        },
                    },
                ],
            },
        }
    }
    path.write_text(yaml.safe_dump(config_data))


def _request_json(url: str, method: str = "GET", payload: dict | None = None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = Request(url, data=data, headers=headers, method=method)
    with urlopen(req, timeout=3) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _start_json_stub_server(responses: dict[str, tuple[int, dict]]):
    class StubHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            status, payload = responses.get(self.path, (404, {"status": "NOT_FOUND"}))
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), StubHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, thread, f"http://{host}:{port}"


def test_normalize_event_payload_sets_defaults():
    event = _normalize_event_payload({"source": {"device_id": "edge-01", "ip": "1.2.3.4"}})

    assert event["version"] == "1"
    assert event["type"] == "simulate"
    assert event["event_id"].startswith("evt_")
    assert event["timestamp"]
    assert event["source"]["device_id"] == "edge-01"


def test_simulate_decision_payload_uses_reason_code_and_matches_rule():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        _write_config(config_path)

        agent = PalasikAgent(config_file=str(config_path))

        trust_high = _resolve_decision_payload(
            agent,
            _normalize_event_payload(
                {
                    "source": {
                        "device_id": "edge-01",
                        "ip": "1.2.3.4",
                    },
                    "value": 42,
                }
            ),
        )
        assert trust_high["decision"] == "ALLOW"
        assert trust_high["reason_code"] == "TRUSTED_DEVICE"
        assert trust_high["policy_name"] == "rule_policy"

        trust_low = _resolve_decision_payload(
            agent,
            _normalize_event_payload(
                {
                    "source": {
                        "device_id": "unknown",
                        "ip": "1.2.3.4",
                    },
                    "value": 42,
                }
            ),
        )
        assert trust_low["decision"] == "DENY"
        assert trust_low["reason_code"] == "UNKNOWN_DEVICE"


def test_decision_payload_is_json_serializable(tmp_path):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)

    event = {
        "version": "1",
        "type": "sensor.sample",
        "source": {"device_id": "edge-01", "ip": "127.0.0.1"},
        "value": 10,
    }

    resolved = _resolve_decision_payload(
        PalasikAgent(config_file=str(config_path)),
        _normalize_event_payload(event),
    )

    dumped = json.dumps(resolved)
    loaded = json.loads(dumped)
    assert loaded["decision"] == "ALLOW"
    assert loaded["event_version"] == "1"


def test_validate_policy_accepts_valid_rule_policy():
    issues = _validate_policy(
        {
            "version": "1",
            "default_deny": True,
            "default_action": "DENY",
            "rules": [
                {
                    "id": "deny_unknown",
                    "action": "DENY",
                    "reason_code": "UNKNOWN",
                    "condition": {"op": "eq", "key": "source.device_id", "value": "unknown"},
                },
                {
                    "id": "allow_trusted",
                    "action": "ALLOW",
                    "reason_code": "TRUSTED",
                    "condition": {"op": "gte", "key": "trust_score", "value": 0.8},
                },
            ],
        }
    )
    assert issues == []


def test_validate_policy_requires_default_deny():
    issues = _validate_policy(
        {
            "version": "1",
            "default_deny": False,
            "default_action": "DENY",
            "rules": [
                {
                    "id": "allow_device",
                    "action": "ALLOW",
                    "condition": {"op": "eq", "key": "source.device_id", "value": "edge-01"},
                }
            ],
        }
    )
    assert any("policy.default_deny harus bernilai true" in item for item in issues)


def test_validate_policy_rejects_deny_without_reason_code():
    issues = _validate_policy(
        {
            "version": "1",
            "default_deny": True,
            "default_action": "DENY",
            "type": "rule",
            "rules": [
                {
                    "id": "deny_device",
                    "action": "DENY",
                    "condition": {"op": "eq", "key": "source.device_id", "value": "unknown"},
                }
            ],
        }
    )
    assert any("wajib memiliki reason_code" in item for item in issues)


def test_status_payload_includes_metrics_and_alerts(tmp_path):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)
    config_data = yaml.safe_load(config_path.read_text())
    # tighten alert sensitivity so test can assert alert output deterministically
    config_data["palasik"]["observability"] = {
        "metrics_file": str(tmp_path / "metrics.json"),
        "alert": {
            "deny_spike_threshold": 0.2,
            "trust_score_drop_threshold": 0.0,
        },
    }
    config_path.write_text(yaml.safe_dump(config_data))

    agent = PalasikAgent(config_file=str(config_path))
    agent.context.metrics_file = str(tmp_path / "metrics.json")
    agent.load_plugins()
    agent.start()
    agent.emit(
        _normalize_event_payload(
            {
                "type": "sensor.sample",
                "source": {"device_id": "edge-01", "ip": "127.0.0.1"},
                "value": 10,
            }
        )
    )
    payload = _build_status_payload(agent)

    assert payload["command"] == "status"
    assert payload["status"] == "UP"
    assert payload["health"]["status"] == "UP"
    assert payload["metrics"]["events_total"] == 1
    assert "health_status" in payload["metrics"]
    assert "alerts" in payload["metrics"]

    agent.stop()


def _read_config_policy(path: Path):
    payload = yaml.safe_load(path.read_text())
    return payload["palasik"]["policy"]


def _sample_smoke_events_path() -> Path:
    return Path(__file__).resolve().parents[2] / "docs/samples/policy-smoke-events.json"


def test_policy_snapshot_and_rollback(tmp_path, capsys):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)

    snapshot_args = SimpleNamespace(
        config=str(config_path),
        snapshot_dir=str(tmp_path / "policy_snapshots"),
    )
    cmd_policy_snapshot(snapshot_args)
    _ = capsys.readouterr()

    snapshots = list((tmp_path / "policy_snapshots").glob("*.snapshot.yaml"))
    assert len(snapshots) == 1

    modified = _read_config_policy(config_path)
    modified["default_deny"] = False
    config_data = yaml.safe_load(config_path.read_text())
    config_data["palasik"]["policy"] = modified
    config_path.write_text(yaml.safe_dump(config_data))

    rollback_args = SimpleNamespace(
        config=str(config_path),
        snapshot=str(snapshots[0]),
        backup_dir=str(tmp_path / "policy_backups"),
    )
    cmd_policy_rollback(rollback_args)
    restored = _read_config_policy(config_path)

    assert restored["default_deny"] is True
    backups = list((tmp_path / "policy_backups").glob("config.yaml.rollback-backup-*"))
    assert len(backups) == 1


def test_policy_deploy_check_pass_and_fail(tmp_path, capsys):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)

    pass_args = SimpleNamespace(
        config=str(config_path),
        smoke_events=str(_sample_smoke_events_path()),
        max_deny_ratio=0.95,
        limit=10,
        require_allow=True,
    )
    cmd_policy_deploy_check(pass_args)
    out = capsys.readouterr().out
    assert "policy deploy-check: PASS" in out

    data = yaml.safe_load(config_path.read_text())
    data["palasik"]["policy"]["rules"] = [
        {
            "id": "deny_all",
            "action": "DENY",
            "reason_code": "HARD_DENY",
            "condition": {
                "op": "eq",
                "key": "type",
                "value": "sensor.sample",
            },
        }
    ]
    config_path.write_text(yaml.safe_dump(data))

    fail_args = SimpleNamespace(
        config=str(config_path),
        smoke_events=str(_sample_smoke_events_path()),
        max_deny_ratio=0.95,
        limit=10,
        require_allow=True,
    )
    with pytest.raises(SystemExit):
        cmd_policy_deploy_check(fail_args)


def test_check_startup_accepts_absolute_storage_paths(tmp_path):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)

    payload = yaml.safe_load(config_path.read_text())
    payload["palasik"]["observability"] = {
        "metrics_file": str(tmp_path / "metrics.json"),
    }
    payload["palasik"]["decision_log"] = str(tmp_path / "decisions.jsonl")
    payload["palasik"]["audit_log"] = str(tmp_path / "audit.jsonl")
    config_path.write_text(yaml.safe_dump(payload))

    agent = PalasikAgent(config_file=str(config_path))
    issues = _collect_startup_issues(
        agent=agent,
        config_path=str(config_path),
        host="0.0.0.0",
        port=8080,
    )

    assert issues == []


def test_check_startup_rejects_missing_route_adapter(tmp_path):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)

    payload = yaml.safe_load(config_path.read_text())
    payload["palasik"]["observability"] = {
        "metrics_file": str(tmp_path / "metrics.json"),
    }
    payload["palasik"]["decision_log"] = str(tmp_path / "decisions.jsonl")
    payload["palasik"]["audit_log"] = str(tmp_path / "audit.jsonl")
    payload["palasik"]["actions"] = {
        "routes": {
            "create_ticket": "webhook",
        }
    }
    config_path.write_text(yaml.safe_dump(payload))

    agent = PalasikAgent(config_file=str(config_path))
    issues = _collect_startup_issues(
        agent=agent,
        config_path=str(config_path),
        host="0.0.0.0",
        port=8080,
    )

    assert any("adapter 'webhook' tapi adapter tidak aktif" in item for item in issues)


def test_check_startup_rejects_invalid_webhook_endpoint(tmp_path):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)

    payload = yaml.safe_load(config_path.read_text())
    payload["palasik"]["observability"] = {
        "metrics_file": str(tmp_path / "metrics.json"),
    }
    payload["palasik"]["decision_log"] = str(tmp_path / "decisions.jsonl")
    payload["palasik"]["audit_log"] = str(tmp_path / "audit.jsonl")
    payload["palasik"]["actions"] = {
        "routes": {
            "create_ticket": "webhook",
        },
        "webhook": {
            "endpoint": "not-a-valid-url",
        },
    }
    config_path.write_text(yaml.safe_dump(payload))

    agent = PalasikAgent(config_file=str(config_path))
    issues = _collect_startup_issues(
        agent=agent,
        config_path=str(config_path),
        host="127.0.0.1",
        port=8080,
    )

    assert any("palasik.actions.webhook.endpoint tidak valid" in item for item in issues)


def test_check_startup_rejects_unbindable_port_and_exits_non_zero(tmp_path):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)

    payload = yaml.safe_load(config_path.read_text())
    payload["palasik"]["observability"] = {
        "metrics_file": str(tmp_path / "metrics.json"),
    }
    payload["palasik"]["decision_log"] = str(tmp_path / "decisions.jsonl")
    payload["palasik"]["audit_log"] = str(tmp_path / "audit.jsonl")
    config_path.write_text(yaml.safe_dump(payload))

    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    blocker.listen(1)
    occupied_port = blocker.getsockname()[1]

    try:
        args = SimpleNamespace(
            config=str(config_path),
            host="127.0.0.1",
            port=occupied_port,
            allow_relative_paths=False,
        )
        with pytest.raises(SystemExit) as exc:
            cmd_check_startup(args)
        assert exc.value.code == 1
    finally:
        blocker.close()


def test_serve_api_strict_health_mode_returns_503_when_runtime_degraded(tmp_path):
    class SlowWebhookHandler(BaseHTTPRequestHandler):
        calls = 0

        def do_POST(self):
            type(self).calls += 1
            time.sleep(0.2)
            self.send_response(202)
            self.end_headers()

        def log_message(self, format, *args):
            return None

    webhook_server = ThreadingHTTPServer(("127.0.0.1", 0), SlowWebhookHandler)
    webhook_thread = threading.Thread(target=webhook_server.serve_forever, daemon=True)
    webhook_thread.start()
    webhook_host, webhook_port = webhook_server.server_address
    webhook_url = f"http://{webhook_host}:{webhook_port}/hook"

    config_path = tmp_path / "config.yaml"
    config_data = {
        "palasik": {
            "policy": {
                "version": "1",
                "default_deny": True,
                "default_action": "DENY",
                "type": "rule",
                "rules": [
                    {
                        "id": "allow_everything_for_dispatch_test",
                        "action": "ALLOW",
                        "reason_code": "TEST_OK",
                        "condition": {
                            "op": "exists",
                            "key": "source.device_id",
                        },
                    }
                ],
            },
            "observability": {
                "metrics_file": str(tmp_path / "metrics.json"),
            },
            "decision_log": str(tmp_path / "decisions.jsonl"),
            "audit_log": str(tmp_path / "audit.jsonl"),
            "health": {
                "degraded_http_mode": "fail",
            },
            "actions": {
                "timeout": 0.1,
                "max_retries": 2,
                "retry_backoff_seconds": 0.0,
                "routes": {"create_ticket": "webhook"},
                "webhook": {"endpoint": webhook_url},
            },
        }
    }
    config_path.write_text(yaml.safe_dump(config_data), encoding="utf-8")

    port_probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_probe.bind(("127.0.0.1", 0))
    port = port_probe.getsockname()[1]
    port_probe.close()

    server_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "palasik.cli.main",
            "serve-api",
            "--config",
            str(config_path),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(Path(__file__).resolve().parents[2]),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"

    try:
        for _ in range(30):
            try:
                _request_json(f"{base_url}/health")
                break
            except Exception:
                time.sleep(0.2)
        else:
            assert False, "serve-api did not become ready"

        status, payload = _request_json(
            f"{base_url}/dispatch",
            method="POST",
            payload={
                "trace_id": "trace-cli-strict",
                "actions": ["create_ticket"],
                "event": {
                    "event_id": "evt-cli-strict",
                    "type": "manual.dispatch",
                    "source": {"device_id": "ops-console", "ip": "127.0.0.1"},
                },
            },
        )
        assert status == 200
        assert payload["results"][0]["status"] == "failed"

        try:
            _request_json(f"{base_url}/health")
            assert False, "expected HTTPError"
        except HTTPError as exc:
            assert exc.code == 503
            health = json.loads(exc.read().decode("utf-8"))
            assert health["status"] == "DEGRADED"
    finally:
        server_process.terminate()
        server_process.wait(timeout=5)
        webhook_server.shutdown()
        webhook_server.server_close()
        webhook_thread.join(timeout=3)


def test_check_health_alerts_script_returns_zero_for_up(tmp_path):
    responses = {
        "/health": (
            200,
            {
                "status": "UP",
                "health": {
                    "status_since_utc": "2026-07-03T03:00:00Z",
                    "last_transition_utc": "2026-07-03T03:00:00Z",
                    "last_reason": None,
                    "transition_count": 0,
                },
                "actions": {
                    "latest_retry_issue": None,
                },
            },
        ),
        "/metrics": (
            200,
            {
                "metrics": {
                    "failed_action_rate": 0.0,
                    "actions_total": 0,
                    "actions_failed": 0,
                    "alerts": [],
                },
            },
        ),
    }
    server, thread, base_url = _start_json_stub_server(responses)

    try:
        result = subprocess.run(
            ["bash", "scripts/check_health_alerts.sh"],
            cwd=str(Path(__file__).resolve().parents[2]),
            env={**dict(os.environ), "PALASIK_BASE_URL": base_url},
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert '"status": "UP"' in result.stdout
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_check_health_alerts_script_returns_one_for_degraded_in_strict_mode(tmp_path):
    responses = {
        "/health": (
            200,
            {
                "status": "DEGRADED",
                "health": {
                    "status_since_utc": "2026-07-03T03:01:00Z",
                    "last_transition_utc": "2026-07-03T03:01:00Z",
                    "last_reason": "latest action failure: action=create_ticket event_id=evt-1",
                    "transition_count": 1,
                },
                "actions": {
                    "latest_retry_issue": {
                        "status": "failed",
                        "action": "create_ticket",
                        "event_id": "evt-1",
                    },
                },
            },
        ),
        "/metrics": (
            200,
            {
                "metrics": {
                    "failed_action_rate": 0.5,
                    "actions_total": 2,
                    "actions_failed": 1,
                    "alerts": [],
                },
            },
        ),
    }
    server, thread, base_url = _start_json_stub_server(responses)

    try:
        result = subprocess.run(
            ["bash", "scripts/check_health_alerts.sh"],
            cwd=str(Path(__file__).resolve().parents[2]),
            env={
                **dict(os.environ),
                "PALASIK_BASE_URL": base_url,
                "PALASIK_HEALTH_STRICT_UP_ONLY": "1",
            },
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 1
        assert '"status": "DEGRADED"' in result.stdout
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_check_health_alerts_script_returns_two_for_down_alert(tmp_path):
    responses = {
        "/health": (
            503,
            {
                "status": "DOWN",
                "health": {
                    "status_since_utc": "2026-07-03T03:02:00Z",
                    "last_transition_utc": "2026-07-03T03:02:00Z",
                    "last_reason": "audit_service is not initialized",
                    "transition_count": 2,
                },
                "actions": {
                    "latest_retry_issue": None,
                },
            },
        ),
        "/metrics": (
            200,
            {
                "metrics": {
                    "failed_action_rate": 0.0,
                    "actions_total": 0,
                    "actions_failed": 0,
                    "alerts": [
                        {
                            "type": "health_down",
                            "severity": "critical",
                            "message": "Service is down",
                        }
                    ],
                },
            },
        ),
    }
    server, thread, base_url = _start_json_stub_server(responses)

    try:
        result = subprocess.run(
            ["bash", "scripts/check_health_alerts.sh"],
            cwd=str(Path(__file__).resolve().parents[2]),
            env={**dict(os.environ), "PALASIK_BASE_URL": base_url},
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 2
        assert '"status": "DOWN"' in result.stdout
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_check_health_alerts_script_returns_four_for_unreachable_endpoint(tmp_path):
    unreachable_port_probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    unreachable_port_probe.bind(("127.0.0.1", 0))
    port = unreachable_port_probe.getsockname()[1]
    unreachable_port_probe.close()
    base_url = f"http://127.0.0.1:{port}"

    result = subprocess.run(
        ["bash", "scripts/check_health_alerts.sh"],
        cwd=str(Path(__file__).resolve().parents[2]),
        env={
            **dict(os.environ),
            "PALASIK_BASE_URL": base_url,
            "PALASIK_HEALTH_RETRIES": "2",
            "PALASIK_HEALTH_RETRY_SLEEP": "0.1",
        },
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 4
    assert '"status": "UNREACHABLE"' in result.stdout
    assert "Health endpoint is not reachable" in result.stdout


def test_install_systemd_renders_bundle(tmp_path, capsys):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)
    env_template = tmp_path / "palasik.env.example"
    env_template.write_text("PALASIK_METRICS_FILE=/var/lib/palasik/runs/metrics.json\n")

    args = SimpleNamespace(
        config_source=str(config_path),
        env_template=str(env_template),
        output_dir=str(tmp_path / "rendered"),
        service_name="palasik",
        install_root="/opt/palasik",
        etc_dir="/etc/palasik",
        state_dir="/var/lib/palasik/runs",
        log_dir="/var/log/palasik",
        user="palasik",
        group="palasik",
        host="0.0.0.0",
        port=8080,
    )

    cmd_install_systemd(args)
    output = capsys.readouterr().out

    service_file = tmp_path / "rendered" / "palasik.service"
    install_script = tmp_path / "rendered" / "install_palasik_systemd.sh"
    copied_env = tmp_path / "rendered" / "palasik.env"

    assert "install-systemd: PASS" in output
    assert service_file.exists()
    assert copied_env.exists()
    assert install_script.exists()
    assert "ExecStartPre=/opt/palasik/.venv/bin/python -m palasik.cli.main check-startup" in service_file.read_text()
    assert "systemctl enable \"$SERVICE_NAME.service\"" in install_script.read_text()
