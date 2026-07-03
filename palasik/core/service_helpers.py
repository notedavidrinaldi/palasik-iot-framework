from __future__ import annotations

from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path
from uuid import uuid4
import os


def normalize_event_payload(payload: dict | None):
    if payload is None:
        payload = {}

    if not isinstance(payload, dict):
        raise ValueError("Event payload harus berformat JSON object")

    event = dict(payload)
    if "version" not in event:
        event["version"] = "1"
    if "event_id" not in event:
        event["event_id"] = f"evt_{uuid4()}"
    if "timestamp" not in event:
        event["timestamp"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if "type" not in event:
        event["type"] = "simulate"

    if "source" not in event:
        event["source"] = {"device_id": "unknown", "ip": "127.0.0.1"}

    return event


def build_status_payload(agent, command: str = "status"):
    status, degraded_reasons = evaluate_runtime_health(agent)
    agent.context.metrics.observe_health(status, degraded_reasons)
    metrics = agent.context.metrics.as_dict()
    metrics["alerts"] = agent.context.metrics.evaluate_alerts(
        agent.context.metrics_alerts or {}
    )

    dispatcher = getattr(agent.context, "action_dispatcher", None)
    adapter_names = ("logger", "webhook", "telegram", "whatsapp", "relay", "http_forward")
    active_adapters = {}
    if dispatcher is not None:
        for name in adapter_names:
            active_adapters[name] = name in dispatcher.adapters

    audit_log = getattr(agent.context, "audit_log", None)
    metrics_file = getattr(agent.context, "metrics_file", None)
    latest_action_issue = agent.context.audit_service.latest_action_issue()
    routes = dict(getattr(dispatcher, "action_map", {}) or {})

    payload = {
        "command": command,
        "status": status,
        "metrics": metrics,
        "health": {
            "status": metrics.get("health_status"),
            "status_since_utc": metrics.get("health_status_since_utc"),
            "last_transition_utc": metrics.get("health_last_transition_utc"),
            "transition_count": metrics.get("health_transition_count"),
            "status_breakdown": metrics.get("health_status_breakdown"),
            "last_reason": metrics.get("health_last_reason"),
            "last_reasons": metrics.get("health_last_reasons"),
        },
        "latest_event_id": agent.context.latest_event_id,
        "policy_name": getattr(agent.context.policy, "name", lambda: "policy")(),
        "actions": {
            "active_adapters": active_adapters,
            "routes": routes,
            "latest_retry_issue": latest_action_issue,
        },
        "storage": {
            "audit_log": _path_status(audit_log),
            "metrics_file": _path_status(metrics_file),
        },
        "degraded_reasons": degraded_reasons,
    }

    latest = agent.context.latest_decision
    if latest is not None:
        payload["latest_decision"] = latest.to_dict()

    return payload


def evaluate_runtime_health(agent):
    dispatcher = getattr(agent.context, "action_dispatcher", None)
    if dispatcher is None:
        return "DOWN", ["action_dispatcher is not initialized"]

    audit_service = getattr(agent.context, "audit_service", None)
    if audit_service is None:
        return "DOWN", ["audit_service is not initialized"]

    degraded_reasons = _evaluate_degraded_reasons(
        latest_action_issue=audit_service.latest_action_issue(),
        audit_log=getattr(agent.context, "audit_log", None),
        metrics_file=getattr(agent.context, "metrics_file", None),
    )
    if degraded_reasons:
        return "DEGRADED", degraded_reasons

    return "UP", []


def resolve_health_http_status(payload: dict, *, degraded_http_mode: str = "ok") -> HTTPStatus:
    status = str(payload.get("status", "DOWN")).upper()
    if status == "UP":
        return HTTPStatus.OK
    if status == "DEGRADED":
        if str(degraded_http_mode).lower() == "fail":
            return HTTPStatus.SERVICE_UNAVAILABLE
        return HTTPStatus.OK
    return HTTPStatus.SERVICE_UNAVAILABLE


def _path_status(path_value: str | None):
    if not path_value:
        return {
            "configured": False,
            "path": None,
            "writable": False,
        }

    target = Path(path_value)
    writable = _is_path_writable(target)
    return {
        "configured": True,
        "path": str(target),
        "exists": target.exists(),
        "writable": writable,
    }


def _is_path_writable(target: Path) -> bool:
    probe = target if target.exists() else target.parent
    probe = probe.resolve(strict=False)

    while not probe.exists() and probe != probe.parent:
        probe = probe.parent

    return os.access(probe, os.W_OK)


def _evaluate_degraded_reasons(
    *,
    latest_action_issue: dict | None,
    audit_log: str | None,
    metrics_file: str | None,
):
    reasons = []

    if latest_action_issue and latest_action_issue.get("status") == "failed":
        reasons.append(
            f"latest action failure: action={latest_action_issue.get('action')} event_id={latest_action_issue.get('event_id')}"
        )
    elif latest_action_issue and latest_action_issue.get("status") == "retrying":
        reasons.append(
            f"latest action retrying: action={latest_action_issue.get('action')} event_id={latest_action_issue.get('event_id')}"
        )

    audit_status = _path_status(audit_log)
    if audit_status.get("configured") and not audit_status.get("writable"):
        reasons.append("audit_log is configured but not writable")

    metrics_status = _path_status(metrics_file)
    if metrics_status.get("configured") and not metrics_status.get("writable"):
        reasons.append("metrics_file is configured but not writable")

    return reasons
