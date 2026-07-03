from __future__ import annotations

from pathlib import Path
from typing import Any
import json


class AuditService:
    def __init__(self, path: str | None):
        self.path = path

    def read_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self.path:
            return []

        target = Path(self.path)
        if not target.exists():
            return []

        records: list[dict[str, Any]] = []
        for line in target.read_text(encoding="utf-8").splitlines()[-max(0, limit):]:
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                records.append(payload)
        return records

    def write_decision(self, decision_record):
        if decision_record is None:
            return
        self._append(
            {
                "record_type": "decision",
                "status": "decision",
                "decision": decision_record.to_dict(),
                "event_id": decision_record.event_id,
                "trace_id": decision_record.trace_id,
                "created_at_utc": decision_record.created_at_utc,
            }
        )

    def latest_action_issue(self) -> dict[str, Any] | None:
        for item in reversed(self.read_recent(limit=200)):
            if item.get("record_type") != "action":
                continue
            if item.get("status") not in {"retrying", "failed"}:
                continue
            return item
        return None

    def write_action(
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
        decision = decision_record.to_dict() if decision_record is not None else None
        self._append(
            {
                "record_type": "action",
                "status": status,
                "action": action,
                "adapter": adapter,
                "attempt": attempt,
                "idempotency_key": idempotency_key,
                "duplicate": duplicate,
                "error": error,
                "response_code": response_code,
                "event_id": event.get("event_id"),
                "trace_id": trace_id,
                "event_snapshot": {
                    "type": event.get("type"),
                    "source": event.get("source"),
                    "value": event.get("value"),
                },
                "decision": decision,
            }
        )

    def _append(self, payload: dict[str, Any]):
        if not self.path:
            return

        target = Path(self.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
