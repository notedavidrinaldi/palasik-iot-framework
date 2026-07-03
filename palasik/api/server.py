from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse
import json

from palasik.core.audit import AuditService
from palasik.core.service_helpers import (
    build_status_payload,
    normalize_event_payload,
    resolve_health_http_status,
)


def _decision_payload(agent) -> dict[str, Any]:
    latest = agent.context.latest_decision
    if latest is None:
        return {}
    return latest.to_dict()


def create_handler(agent):
    class PalasikAPIHandler(BaseHTTPRequestHandler):
        server_version = "PalasikHTTP/0.1"

        def do_GET(self):
            parsed = urlparse(self.path)

            if parsed.path == "/health":
                payload = build_status_payload(agent, command="health")
                degraded_http_mode = agent.config.get(
                    "palasik",
                    "health",
                    "degraded_http_mode",
                    default="ok",
                )
                self._send_json(
                    resolve_health_http_status(payload, degraded_http_mode=degraded_http_mode),
                    payload,
                )
                return

            if parsed.path == "/audit":
                query = parse_qs(parsed.query)
                try:
                    limit = int(query.get("limit", ["20"])[0])
                except ValueError:
                    limit = 20
                limit = max(1, min(limit, 200))

                items = agent.context.audit_service.read_recent(limit=limit)
                if not items and agent.context.decision_log:
                    items = AuditService(agent.context.decision_log).read_recent(limit=limit)
                payload = {
                    "status": "OK",
                    "count": 0,
                    "items": items,
                }
                payload["count"] = len(payload["items"])
                self._send_json(HTTPStatus.OK, payload)
                return

            if parsed.path == "/metrics":
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "status": "OK",
                        "metrics": agent.context.metrics.as_dict(),
                    },
                )
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"status": "NOT_FOUND"})

        def do_POST(self):
            parsed = urlparse(self.path)

            if parsed.path not in {"/events/ingest", "/evaluate", "/dispatch"}:
                self._send_json(HTTPStatus.NOT_FOUND, {"status": "NOT_FOUND"})
                return

            try:
                raw_payload = self._read_json_body()
                if parsed.path == "/dispatch":
                    event = normalize_event_payload(raw_payload.get("event"))
                    raw_actions = raw_payload.get("actions", [])
                    if not isinstance(raw_actions, list):
                        raise ValueError("Field 'actions' harus array")

                    results = agent.context.action_dispatcher.dispatch_actions(
                        raw_actions,
                        event,
                        trace_id=raw_payload.get("trace_id"),
                        metadata=raw_payload.get("metadata"),
                    )
                    self._send_json(
                        HTTPStatus.OK,
                        {
                            "status": "OK",
                            "endpoint": parsed.path,
                            "event_id": event.get("event_id"),
                            "results": [item.to_dict() for item in results],
                        },
                    )
                    return

                event = normalize_event_payload(raw_payload)
                agent.emit(event)
                decision = _decision_payload(agent)
                payload = {
                    "status": "OK",
                    "endpoint": parsed.path,
                    "event_id": event.get("event_id"),
                    "decision": decision,
                }
                self._send_json(HTTPStatus.OK, payload)
            except ValueError as exc:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"status": "BAD_REQUEST", "error": str(exc)},
                )
            except Exception as exc:
                self._send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"status": "ERROR", "error": str(exc)},
                )

        def log_message(self, format, *args):
            logger = getattr(agent.context, "logger", None)
            if logger is not None:
                logger.info(f"http_api {self.address_string()} - {format % args}")

        def _read_json_body(self) -> dict[str, Any]:
            content_length = self.headers.get("Content-Length")
            if content_length is None:
                return {}

            try:
                length = int(content_length)
            except ValueError as exc:
                raise ValueError("Content-Length tidak valid") from exc

            if length <= 0:
                return {}

            raw = self.rfile.read(length)
            if not raw:
                return {}

            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("Body harus JSON valid") from exc

            if not isinstance(payload, dict):
                raise ValueError("Body harus JSON object")

            return payload

        def _send_json(self, status: HTTPStatus, payload: dict[str, Any]):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return PalasikAPIHandler


def create_server(agent, host: str = "127.0.0.1", port: int = 8080) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), create_handler(agent))
