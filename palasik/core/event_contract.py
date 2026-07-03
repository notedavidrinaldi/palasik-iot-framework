from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import uuid4


_ALLOWED_VERSIONS = {"1", "1.0", "1.1", 1}


def _to_version(value) -> str:
    if value is None:
        return "1.1"

    if isinstance(value, (int, float)):
        if int(value) == 1:
            return "1"
        if int(value) == 11:
            return "1.1"
        return str(value)

    return str(value)


def _parse_event_timestamp(value: Any) -> tuple[datetime | None, str | None]:
    if not isinstance(value, str) or not value.strip():
        return None, "timestamp wajib string ISO-8601"

    timestamp = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(timestamp)
    except ValueError:
        return None, "timestamp tidak valid (ISO-8601 dibutuhkan)"

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed, None


def normalize_event(payload: dict | None, *, default_version: str = "1.1", max_age_seconds: int | None = 600) -> tuple[dict, list[str]]:
    """Normalize and validate event payload.

    Mengembalikan tuple `(event, issues)`:
    - `event` tetap berupa dict hasil normalisasi.
    - `issues` berisi validasi non-fatal. Event tetap diproses jika ada issue.
    """

    if payload is None:
        payload = {}

    if not isinstance(payload, dict):
        return {}, ["event harus berformat JSON object"]

    event: dict[str, Any] = dict(payload)
    issues: list[str] = []

    if not event.get("event_id"):
        event["event_id"] = f"evt-{uuid4()}"

    if event.get("version") is None:
        event["version"] = default_version

    event_version = _to_version(event.get("version"))
    if event_version not in _ALLOWED_VERSIONS:
        issues.append(f"version event tidak didukung: {event.get('version')!r}")
    else:
        event["version"] = "1" if event_version == "1" else event_version

    if not event.get("type"):
        event["type"] = "generic"

    if not event.get("timestamp"):
        event["timestamp"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    parsed_ts, parse_err = _parse_event_timestamp(event.get("timestamp"))
    if parse_err:
        issues.append(parse_err)
    elif max_age_seconds is not None and parsed_ts is not None:
        now = datetime.now(timezone.utc)
        if parsed_ts > now + timedelta(seconds=60):
            issues.append("timestamp di masa depan")
        elif (now - parsed_ts).total_seconds() > max_age_seconds:
            issues.append("timestamp sudah kedaluwarsa")

    source = event.get("source")
    if not isinstance(source, dict):
        source = {}
        if isinstance(event.get("ip"), str):
            source["ip"] = event.get("ip")
        if isinstance(event.get("device_id"), str):
            source["device_id"] = event.get("device_id")
        event["source"] = source

    if not isinstance(event.get("source"), dict):
        issues.append("source harus object")
    else:
        if not event["source"].get("device_id"):
            event["source"].setdefault("device_id", "unknown")

        if not event["source"].get("ip"):
            event["source"].setdefault("ip", "127.0.0.1")

    event.setdefault("trust_ctx", {})
    event.setdefault("metadata", {})
    event.setdefault("context", {})

    return event, issues
