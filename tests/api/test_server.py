from __future__ import annotations

from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import json
import time
import threading

import yaml

from palasik.api.server import create_server
from palasik.core.agent import PalasikAgent


def _write_config(path: Path):
    config_data = {
        "palasik": {
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
            "observability": {
                "metrics_file": str(path.parent / "metrics.json"),
            },
            "decision_log": str(path.parent / "decisions.jsonl"),
            "audit_log": str(path.parent / "audit.jsonl"),
            "actions": {
                "max_retries": 2,
            },
        }
    }
    path.write_text(yaml.safe_dump(config_data), encoding="utf-8")


def _write_dispatch_config(
    path: Path,
    *,
    webhook_endpoint: str | None = None,
    routes: dict | None = None,
    degraded_http_mode: str = "ok",
):
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
                "metrics_file": str(path.parent / "metrics.json"),
            },
            "decision_log": str(path.parent / "decisions.jsonl"),
            "audit_log": str(path.parent / "audit.jsonl"),
            "actions": {
                "timeout": 0.1,
                "max_retries": 2,
                "retry_backoff_seconds": 0.0,
                "routes": routes or {"create_ticket": "webhook"},
                "webhook": {},
            },
            "health": {
                "degraded_http_mode": degraded_http_mode,
            },
        }
    }
    if webhook_endpoint:
        config_data["palasik"]["actions"]["webhook"]["endpoint"] = webhook_endpoint
    path.write_text(yaml.safe_dump(config_data), encoding="utf-8")


def _request_json(url: str, method: str = "GET", payload: dict | None = None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = Request(url, data=data, headers=headers, method=method)
    with urlopen(req, timeout=3) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _start_server(server):
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def _start_webhook_stub(handler_cls):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    thread = _start_server(server)
    host, port = server.server_address
    return server, thread, f"http://{host}:{port}"


def test_http_api_health_ingest_evaluate_metrics_dispatch_and_audit(tmp_path):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)

    agent = PalasikAgent(config_file=str(config_path))
    agent.start()

    server = create_server(agent, host="127.0.0.1", port=0)
    thread = _start_server(server)

    host, port = server.server_address
    base_url = f"http://{host}:{port}"

    try:
        status, health = _request_json(f"{base_url}/health")
        assert status == 200
        assert health["status"] == "UP"
        assert health["health"]["status"] == "UP"

        status, ingest = _request_json(
            f"{base_url}/events/ingest",
            method="POST",
            payload={
                "type": "sensor.sample",
                "source": {"device_id": "edge-01", "ip": "127.0.0.1"},
                "value": 10,
            },
        )
        assert status == 200
        assert ingest["decision"]["decision"] == "ALLOW"

        status, evaluated = _request_json(
            f"{base_url}/evaluate",
            method="POST",
            payload={
                "type": "sensor.sample",
                "source": {"device_id": "unknown", "ip": "127.0.0.1"},
                "value": 10,
            },
        )
        assert status == 200
        assert evaluated["decision"]["decision"] == "DENY"
        assert evaluated["decision"]["reason_code"] == "UNKNOWN_DEVICE"

        status, audit = _request_json(f"{base_url}/audit?limit=10")
        assert status == 200
        assert audit["count"] >= 2
        decisions = [
            item["decision"]["decision"]
            for item in audit["items"]
            if item.get("record_type") == "decision"
        ]
        assert "ALLOW" in decisions
        assert "DENY" in decisions

        status, metrics = _request_json(f"{base_url}/metrics")
        assert status == 200
        assert metrics["metrics"]["events_total"] >= 2
        assert metrics["metrics"]["health_status"] == "UP"
        assert "deny_ratio" in metrics["metrics"]

        status, dispatched = _request_json(
            f"{base_url}/dispatch",
            method="POST",
            payload={
                "actions": ["notify_telegram"],
                "event": {
                    "type": "manual.dispatch",
                    "source": {"device_id": "ops-console", "ip": "127.0.0.1"},
                    "value": 1,
                },
            },
        )
        assert status == 200
        assert dispatched["results"][0]["status"] == "success"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        agent.stop()


def test_http_api_rejects_invalid_json(tmp_path):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path)

    agent = PalasikAgent(config_file=str(config_path))
    agent.start()

    server = create_server(agent, host="127.0.0.1", port=0)
    thread = _start_server(server)

    host, port = server.server_address
    url = f"http://{host}:{port}/events/ingest"

    try:
        req = Request(
            url,
            data=b"{bad-json",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urlopen(req, timeout=3)
            assert False, "expected HTTPError"
        except HTTPError as exc:
            assert exc.code == 400
            payload = json.loads(exc.read().decode("utf-8"))
            assert payload["status"] == "BAD_REQUEST"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        agent.stop()


def test_dispatch_retries_webhook_timeout_and_surfaces_latest_issue(tmp_path):
    class SlowWebhookHandler(BaseHTTPRequestHandler):
        calls = 0

        def do_POST(self):
            type(self).calls += 1
            time.sleep(0.2)
            self.send_response(202)
            self.end_headers()

        def log_message(self, format, *args):
            return None

    webhook_server, webhook_thread, webhook_url = _start_webhook_stub(SlowWebhookHandler)
    config_path = tmp_path / "config.yaml"
    _write_dispatch_config(config_path, webhook_endpoint=f"{webhook_url}/hook")

    agent = PalasikAgent(config_file=str(config_path))
    agent.start()
    server = create_server(agent, host="127.0.0.1", port=0)
    thread = _start_server(server)
    host, port = server.server_address
    base_url = f"http://{host}:{port}"

    try:
        status, payload = _request_json(
            f"{base_url}/dispatch",
            method="POST",
            payload={
                "trace_id": "trace-timeout",
                "actions": ["create_ticket"],
                "event": {
                    "event_id": "evt-timeout",
                    "type": "manual.dispatch",
                    "source": {"device_id": "ops-console", "ip": "127.0.0.1"},
                },
            },
        )
        assert status == 200
        assert payload["results"][0]["status"] == "failed"
        assert payload["results"][0]["attempt"] == 2
        assert SlowWebhookHandler.calls == 2

        status, health = _request_json(f"{base_url}/health")
        assert status == 200
        assert health["status"] == "DEGRADED"
        assert health["health"]["transition_count"] >= 1
        assert health["actions"]["latest_retry_issue"]["status"] == "failed"
        assert health["actions"]["latest_retry_issue"]["event_id"] == "evt-timeout"
        assert any("latest action failure:" in item for item in health["degraded_reasons"])
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        agent.stop()
        webhook_server.shutdown()
        webhook_server.server_close()
        webhook_thread.join(timeout=3)


def test_dispatch_retries_webhook_5xx(tmp_path):
    class FlakyWebhookHandler(BaseHTTPRequestHandler):
        calls = 0

        def do_POST(self):
            type(self).calls += 1
            body = b"ok"
            if type(self).calls == 1:
                self.send_response(503)
            else:
                self.send_response(202)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return None

    webhook_server, webhook_thread, webhook_url = _start_webhook_stub(FlakyWebhookHandler)
    config_path = tmp_path / "config.yaml"
    _write_dispatch_config(config_path, webhook_endpoint=f"{webhook_url}/hook")

    agent = PalasikAgent(config_file=str(config_path))
    agent.start()
    server = create_server(agent, host="127.0.0.1", port=0)
    thread = _start_server(server)
    host, port = server.server_address
    base_url = f"http://{host}:{port}"

    try:
        status, payload = _request_json(
            f"{base_url}/dispatch",
            method="POST",
            payload={
                "trace_id": "trace-5xx",
                "actions": ["create_ticket"],
                "event": {
                    "event_id": "evt-5xx",
                    "type": "manual.dispatch",
                    "source": {"device_id": "ops-console", "ip": "127.0.0.1"},
                },
            },
        )
        assert status == 200
        assert payload["results"][0]["status"] == "success"
        assert payload["results"][0]["attempt"] == 2
        assert FlakyWebhookHandler.calls == 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        agent.stop()
        webhook_server.shutdown()
        webhook_server.server_close()
        webhook_thread.join(timeout=3)


def test_health_uses_503_for_degraded_when_strict_mode_enabled(tmp_path):
    class SlowWebhookHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            time.sleep(0.2)
            self.send_response(202)
            self.end_headers()

        def log_message(self, format, *args):
            return None

    webhook_server, webhook_thread, webhook_url = _start_webhook_stub(SlowWebhookHandler)
    config_path = tmp_path / "config.yaml"
    _write_dispatch_config(
        config_path,
        webhook_endpoint=f"{webhook_url}/hook",
        degraded_http_mode="fail",
    )

    agent = PalasikAgent(config_file=str(config_path))
    agent.start()
    server = create_server(agent, host="127.0.0.1", port=0)
    thread = _start_server(server)
    host, port = server.server_address
    base_url = f"http://{host}:{port}"

    try:
        status, payload = _request_json(
            f"{base_url}/dispatch",
            method="POST",
            payload={
                "trace_id": "trace-strict",
                "actions": ["create_ticket"],
                "event": {
                    "event_id": "evt-strict",
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
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        agent.stop()
        webhook_server.shutdown()
        webhook_server.server_close()
        webhook_thread.join(timeout=3)


def test_dispatch_marks_duplicate_requests_as_safe_duplicate(tmp_path):
    class OkWebhookHandler(BaseHTTPRequestHandler):
        calls = 0

        def do_POST(self):
            type(self).calls += 1
            body = b"ok"
            self.send_response(202)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return None

    webhook_server, webhook_thread, webhook_url = _start_webhook_stub(OkWebhookHandler)
    config_path = tmp_path / "config.yaml"
    _write_dispatch_config(config_path, webhook_endpoint=f"{webhook_url}/hook")

    agent = PalasikAgent(config_file=str(config_path))
    agent.start()
    server = create_server(agent, host="127.0.0.1", port=0)
    thread = _start_server(server)
    host, port = server.server_address
    base_url = f"http://{host}:{port}"
    payload = {
        "trace_id": "trace-dup",
        "actions": ["create_ticket"],
        "event": {
            "event_id": "evt-dup",
            "type": "manual.dispatch",
            "source": {"device_id": "ops-console", "ip": "127.0.0.1"},
        },
    }

    try:
        _, first = _request_json(f"{base_url}/dispatch", method="POST", payload=payload)
        _, second = _request_json(f"{base_url}/dispatch", method="POST", payload=payload)
        assert first["results"][0]["duplicate"] is False
        assert second["results"][0]["duplicate"] is True
        assert second["results"][0]["attempt"] == 0
        assert OkWebhookHandler.calls == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        agent.stop()
        webhook_server.shutdown()
        webhook_server.server_close()
        webhook_thread.join(timeout=3)


def test_dispatch_falls_back_to_logger_when_adapter_not_available(tmp_path):
    config_path = tmp_path / "config.yaml"
    _write_dispatch_config(
        config_path,
        routes={"create_ticket": "webhook"},
    )

    agent = PalasikAgent(config_file=str(config_path))
    agent.start()
    server = create_server(agent, host="127.0.0.1", port=0)
    thread = _start_server(server)
    host, port = server.server_address
    base_url = f"http://{host}:{port}"

    try:
        status, payload = _request_json(
            f"{base_url}/dispatch",
            method="POST",
            payload={
                "trace_id": "trace-fallback",
                "actions": ["create_ticket"],
                "event": {
                    "event_id": "evt-fallback",
                    "type": "manual.dispatch",
                    "source": {"device_id": "ops-console", "ip": "127.0.0.1"},
                },
            },
        )
        assert status == 200
        assert payload["results"][0]["status"] == "success"
        assert payload["results"][0]["adapter"] == "logger"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        agent.stop()


def test_dispatch_telegram_payload_contract(monkeypatch):
    calls = {}

    class DummyResponse:
        status_code = 200

        def raise_for_status(self):
            return None

    def fake_post(url, json=None, headers=None, timeout=None):
        calls["url"] = url
        calls["json"] = json
        calls["headers"] = headers
        calls["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr("palasik.core.action_dispatcher.requests.post", fake_post)

    from palasik.core.action_dispatcher import TelegramActionAdapter

    adapter = TelegramActionAdapter(bot_token="token-123", chat_id="-100999")
    result = adapter.dispatch(
        "notify_telegram_ops",
        {"event_id": "evt-telegram"},
        {"message": "hello ops", "decision": "DENY"},
        timeout=2.5,
        idempotency_key="idem-1",
    )

    assert result.status == "success"
    assert calls["url"] == "https://api.telegram.org/bottoken-123/sendMessage"
    assert calls["json"] == {"chat_id": "-100999", "text": "hello ops"}
    assert calls["timeout"] == 2.5


def test_dispatch_whatsapp_payload_contract(monkeypatch):
    calls = {}

    class DummyResponse:
        status_code = 202

        def raise_for_status(self):
            return None

    def fake_post(url, json=None, headers=None, timeout=None):
        calls["url"] = url
        calls["json"] = json
        calls["headers"] = headers
        calls["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr("palasik.core.action_dispatcher.requests.post", fake_post)

    from palasik.core.action_dispatcher import WhatsAppActionAdapter

    adapter = WhatsAppActionAdapter(
        endpoint="https://wa.example/messages",
        headers={"Authorization": "Bearer test"},
    )
    event = {"event_id": "evt-wa", "type": "manual.dispatch"}
    metadata = {"message": "WA alert", "decision": "BLOCK_ALARM"}
    result = adapter.dispatch(
        "notify_whatsapp_ops",
        event,
        metadata,
        timeout=1.25,
        idempotency_key="idem-wa",
    )

    assert result.status == "success"
    assert calls["url"] == "https://wa.example/messages"
    assert calls["headers"]["Authorization"] == "Bearer test"
    assert calls["headers"]["Idempotency-Key"] == "idem-wa"
    assert calls["json"] == {
        "action": "notify_whatsapp_ops",
        "message": "WA alert",
        "event": event,
        "metadata": metadata,
    }
    assert calls["timeout"] == 1.25


def test_dispatch_relay_payload_contract(monkeypatch):
    calls = {}

    class DummyResponse:
        status_code = 200

        def raise_for_status(self):
            return None

    def fake_post(url, json=None, headers=None, timeout=None):
        calls["url"] = url
        calls["json"] = json
        calls["headers"] = headers
        calls["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr("palasik.core.action_dispatcher.requests.post", fake_post)

    from palasik.core.action_dispatcher import RelayActionAdapter

    adapter = RelayActionAdapter(
        endpoint="http://relay.local/api",
        headers={"X-Relay-Key": "abc"},
    )
    event = {
        "event_id": "evt-relay",
        "source": {"device_id": "edge-1", "ip": "127.0.0.1"},
    }
    metadata = {"message": "stop line", "decision": "BLOCK_ALARM"}
    result = adapter.dispatch(
        "relay_off",
        event,
        metadata,
        timeout=0.75,
        idempotency_key="idem-relay",
    )

    assert result.status == "success"
    assert calls["url"] == "http://relay.local/api"
    assert calls["headers"]["X-Relay-Key"] == "abc"
    assert calls["headers"]["Idempotency-Key"] == "idem-relay"
    assert calls["json"] == {
        "command": "relay_off",
        "event_id": "evt-relay",
        "source": {"device_id": "edge-1", "ip": "127.0.0.1"},
        "metadata": metadata,
    }
    assert calls["timeout"] == 0.75
