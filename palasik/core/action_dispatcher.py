from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from time import sleep
from typing import Any
import threading

import requests


@dataclass
class ActionDispatchResult:
    action: str
    adapter: str
    status: str
    attempt: int
    idempotency_key: str
    duplicate: bool = False
    error: str | None = None
    response_code: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "adapter": self.adapter,
            "status": self.status,
            "attempt": self.attempt,
            "idempotency_key": self.idempotency_key,
            "duplicate": self.duplicate,
            "error": self.error,
            "response_code": self.response_code,
        }


class ActionAdapter:
    name = "base"

    def dispatch(
        self,
        action: str,
        event: dict[str, Any],
        metadata: dict[str, Any],
        timeout: float,
        idempotency_key: str,
    ) -> ActionDispatchResult:
        raise NotImplementedError


class LoggingActionAdapter(ActionAdapter):
    name = "logger"

    def __init__(self, logger):
        self.logger = logger

    def dispatch(self, action, event, metadata, timeout, idempotency_key):
        event_id = event.get("event_id")
        self.logger.info(
            f"ACTION {action} logged | event_id={event_id} | adapter={self.name}"
        )
        return ActionDispatchResult(
            action=action,
            adapter=self.name,
            status="success",
            attempt=1,
            idempotency_key=idempotency_key,
        )


class WebhookActionAdapter(ActionAdapter):
    name = "webhook"

    def __init__(self, endpoint: str, headers: dict[str, str] | None = None):
        self.endpoint = endpoint
        self.headers = headers or {"Content-Type": "application/json"}

    def dispatch(self, action, event, metadata, timeout, idempotency_key):
        headers = dict(self.headers)
        headers.setdefault("Idempotency-Key", idempotency_key)
        payload = {
            "action": action,
            "event": event,
            "metadata": metadata,
        }
        response = requests.post(
            self.endpoint,
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return ActionDispatchResult(
            action=action,
            adapter=self.name,
            status="success",
            attempt=1,
            idempotency_key=idempotency_key,
            response_code=response.status_code,
        )


class TelegramActionAdapter(ActionAdapter):
    name = "telegram"

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def dispatch(self, action, event, metadata, timeout, idempotency_key):
        endpoint = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        message = metadata.get("message") or (
            f"PALASIK {action} event_id={event.get('event_id')} "
            f"decision={metadata.get('decision', 'UNKNOWN')}"
        )
        response = requests.post(
            endpoint,
            json={
                "chat_id": self.chat_id,
                "text": message,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        return ActionDispatchResult(
            action=action,
            adapter=self.name,
            status="success",
            attempt=1,
            idempotency_key=idempotency_key,
            response_code=response.status_code,
        )


class WhatsAppActionAdapter(ActionAdapter):
    name = "whatsapp"

    def __init__(self, endpoint: str, headers: dict[str, str] | None = None):
        self.endpoint = endpoint
        self.headers = headers or {"Content-Type": "application/json"}

    def dispatch(self, action, event, metadata, timeout, idempotency_key):
        headers = dict(self.headers)
        headers.setdefault("Idempotency-Key", idempotency_key)
        response = requests.post(
            self.endpoint,
            json={
                "action": action,
                "message": metadata.get("message"),
                "event": event,
                "metadata": metadata,
            },
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return ActionDispatchResult(
            action=action,
            adapter=self.name,
            status="success",
            attempt=1,
            idempotency_key=idempotency_key,
            response_code=response.status_code,
        )


class RelayActionAdapter(ActionAdapter):
    name = "relay"

    def __init__(self, endpoint: str, headers: dict[str, str] | None = None):
        self.endpoint = endpoint
        self.headers = headers or {"Content-Type": "application/json"}

    def dispatch(self, action, event, metadata, timeout, idempotency_key):
        headers = dict(self.headers)
        headers.setdefault("Idempotency-Key", idempotency_key)
        response = requests.post(
            self.endpoint,
            json={
                "command": action,
                "event_id": event.get("event_id"),
                "source": event.get("source"),
                "metadata": metadata,
            },
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return ActionDispatchResult(
            action=action,
            adapter=self.name,
            status="success",
            attempt=1,
            idempotency_key=idempotency_key,
            response_code=response.status_code,
        )


class HTTPForwardActionAdapter(ActionAdapter):
    name = "http_forward"

    def __init__(self, http_adapter):
        self.http_adapter = http_adapter

    def dispatch(self, action, event, metadata, timeout, idempotency_key):
        delivered = self.http_adapter.forward(event, idempotency_key=idempotency_key)
        if not delivered:
            raise RuntimeError("HTTP forward returned false")
        return ActionDispatchResult(
            action=action,
            adapter=self.name,
            status="success",
            attempt=1,
            idempotency_key=idempotency_key,
        )


class ActionDispatcher:
    def __init__(
        self,
        *,
        logger,
        metrics,
        audit_service=None,
        adapters: dict[str, ActionAdapter] | None = None,
        action_map: dict[str, str] | None = None,
        default_timeout: float = 5.0,
        max_retries: int = 1,
        retry_backoff_seconds: float = 0.0,
        idempotency_ttl: int = 1024,
    ):
        self.logger = logger
        self.metrics = metrics
        self.audit_service = audit_service
        self.adapters = dict(adapters or {})
        self.action_map = dict(action_map or {})
        self.default_timeout = float(default_timeout)
        self.max_retries = max(1, int(max_retries))
        self.retry_backoff_seconds = max(0.0, float(retry_backoff_seconds))
        self._seen_keys: deque[str] = deque(maxlen=max(32, int(idempotency_ttl)))
        self._seen_lookup: set[str] = set()
        self._lock = threading.Lock()
        self.logging_adapter = self.adapters.get("logger") or LoggingActionAdapter(logger)
        self.adapters.setdefault("logger", self.logging_adapter)

    def dispatch_actions(
        self,
        actions: list[str],
        event: dict[str, Any],
        *,
        decision_record=None,
        trace_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[ActionDispatchResult]:
        results: list[ActionDispatchResult] = []
        for raw_action in actions or []:
            action = str(raw_action).strip().lower()
            if not action or action == "none":
                continue

            adapter = self._resolve_adapter(action)
            idempotency_key = self._build_idempotency_key(
                action=action,
                event=event,
                trace_id=trace_id,
            )

            if self._is_duplicate(idempotency_key):
                self.metrics.record_action("success", True)
                result = ActionDispatchResult(
                    action=action,
                    adapter=adapter.name,
                    status="success",
                    attempt=0,
                    idempotency_key=idempotency_key,
                    duplicate=True,
                )
                self._write_action_audit(
                    status="success",
                    action=action,
                    adapter=adapter.name,
                    event=event,
                    decision_record=decision_record,
                    trace_id=trace_id,
                    attempt=0,
                    idempotency_key=idempotency_key,
                    duplicate=True,
                )
                results.append(result)
                continue

            base_metadata = {
                "decision": getattr(getattr(decision_record, "decision", None), "value", None),
                "trace_id": trace_id,
            }
            if metadata:
                base_metadata.update(metadata)

            self._write_action_audit(
                status="pending",
                action=action,
                adapter=adapter.name,
                event=event,
                decision_record=decision_record,
                trace_id=trace_id,
                attempt=0,
                idempotency_key=idempotency_key,
            )

            last_error = None
            for attempt in range(1, self.max_retries + 1):
                if attempt > 1:
                    self._write_action_audit(
                        status="retrying",
                        action=action,
                        adapter=adapter.name,
                        event=event,
                        decision_record=decision_record,
                        trace_id=trace_id,
                        attempt=attempt,
                        idempotency_key=idempotency_key,
                        error=last_error,
                    )
                    if self.retry_backoff_seconds > 0:
                        sleep(self.retry_backoff_seconds)

                try:
                    result = adapter.dispatch(
                        action,
                        event,
                        dict(base_metadata),
                        self.default_timeout,
                        idempotency_key,
                    )
                    result.attempt = attempt
                    self._mark_seen(idempotency_key)
                    self.metrics.record_action(result.status, result.duplicate)
                    self._write_action_audit(
                        status="success",
                        action=action,
                        adapter=result.adapter,
                        event=event,
                        decision_record=decision_record,
                        trace_id=trace_id,
                        attempt=attempt,
                        idempotency_key=idempotency_key,
                        duplicate=result.duplicate,
                        response_code=result.response_code,
                    )
                    results.append(result)
                    break
                except Exception as exc:
                    last_error = str(exc)
                    if attempt >= self.max_retries:
                        self.metrics.record_action("failed", False)
                        failed = ActionDispatchResult(
                            action=action,
                            adapter=adapter.name,
                            status="failed",
                            attempt=attempt,
                            idempotency_key=idempotency_key,
                            error=last_error,
                        )
                        self._write_action_audit(
                            status="failed",
                            action=action,
                            adapter=adapter.name,
                            event=event,
                            decision_record=decision_record,
                            trace_id=trace_id,
                            attempt=attempt,
                            idempotency_key=idempotency_key,
                            error=last_error,
                        )
                        self.logger.error(
                            f"ACTION {action} failed | event_id={event.get('event_id')} | error={last_error}"
                        )
                        results.append(failed)
                    else:
                        self.logger.warning(
                            f"ACTION {action} retrying | event_id={event.get('event_id')} | attempt={attempt} | error={last_error}"
                        )

        return results

    def _resolve_adapter(self, action: str) -> ActionAdapter:
        adapter_name = self.action_map.get(action)
        if adapter_name is None:
            adapter_name = "logger"
            if action.startswith("notify_telegram"):
                adapter_name = "telegram"
            elif action.startswith("notify_whatsapp"):
                adapter_name = "whatsapp"
            elif action in {"relay_off", "plc_stop"}:
                adapter_name = "relay"
            elif action in {"http_forward", "forward"}:
                adapter_name = "http_forward"
            elif action in {"create_ticket", "quarantine_device"}:
                adapter_name = "webhook"

        return self.adapters.get(adapter_name) or self.logging_adapter

    def _build_idempotency_key(self, *, action: str, event: dict[str, Any], trace_id: str | None) -> str:
        event_id = event.get("event_id") or "unknown-event"
        trace = trace_id or event.get("trace_id") or "no-trace"
        return f"{action}:{event_id}:{trace}"

    def _is_duplicate(self, key: str) -> bool:
        with self._lock:
            return key in self._seen_lookup

    def _mark_seen(self, key: str):
        with self._lock:
            if key in self._seen_lookup:
                return
            if len(self._seen_keys) == self._seen_keys.maxlen:
                expired = self._seen_keys.popleft()
                self._seen_lookup.discard(expired)
            self._seen_keys.append(key)
            self._seen_lookup.add(key)

    def _write_action_audit(
        self,
        *,
        status: str,
        action: str,
        adapter: str,
        event: dict[str, Any],
        decision_record,
        trace_id: str | None,
        attempt: int,
        idempotency_key: str,
        duplicate: bool = False,
        error: str | None = None,
        response_code: int | None = None,
    ):
        if self.audit_service is None:
            return
        self.audit_service.write_action(
            status=status,
            action=action,
            adapter=adapter,
            event=event,
            decision_record=decision_record,
            trace_id=trace_id,
            attempt=attempt,
            idempotency_key=idempotency_key,
            duplicate=duplicate,
            error=error,
            response_code=response_code,
        )
