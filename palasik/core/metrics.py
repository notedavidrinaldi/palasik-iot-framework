from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
import json
import threading


@dataclass
class RuntimeMetrics:
    events_total: int = 0
    events_allowed: int = 0
    events_denied: int = 0
    total_latency_ms: float = 0.0
    latency_samples: int = 0
    actions_total: int = 0
    actions_failed: int = 0
    actions_succeeded: int = 0
    duplicate_actions: int = 0
    correlation_hit_count: int = 0
    reason_code_breakdown: dict[str, int] = field(default_factory=dict)
    trust_scores: deque = field(default_factory=lambda: deque(maxlen=200))
    health_status: str = "UP"
    health_status_since_utc: str | None = None
    health_last_transition_utc: str | None = None
    health_transition_count: int = 0
    health_status_breakdown: dict[str, int] = field(default_factory=dict)
    health_last_reason: str | None = None
    health_last_reasons: list[str] = field(default_factory=list)
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def __post_init__(self):
        self.reason_code_breakdown = dict(self.reason_code_breakdown or {})
        self.health_status_breakdown = dict(self.health_status_breakdown or {})
        if self.health_status_since_utc is None:
            now = _utc_now_iso()
            self.health_status_since_utc = now
            self.health_last_transition_utc = now

    @classmethod
    def from_file(cls, path: str | None):
        if not path:
            return cls(), None

        snapshot_path = Path(path)
        payload = {}
        if snapshot_path.exists():
            try:
                with snapshot_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    payload = data
            except (OSError, json.JSONDecodeError):
                payload = {}

        reason_code_breakdown = payload.get("reason_code_breakdown", {})
        if not isinstance(reason_code_breakdown, dict):
            reason_code_breakdown = {}

        metrics = cls(
            events_total=int(payload.get("events_total", 0) or 0),
            events_allowed=int(payload.get("events_allowed", 0) or 0),
            events_denied=int(payload.get("events_denied", 0) or 0),
            total_latency_ms=float(payload.get("total_latency_ms", 0.0) or 0.0),
            latency_samples=int(payload.get("latency_samples", 0) or 0),
            actions_total=int(payload.get("actions_total", 0) or 0),
            actions_failed=int(payload.get("actions_failed", 0) or 0),
            actions_succeeded=int(payload.get("actions_succeeded", 0) or 0),
            duplicate_actions=int(payload.get("duplicate_actions", 0) or 0),
            correlation_hit_count=int(payload.get("correlation_hit_count", 0) or 0),
            reason_code_breakdown=reason_code_breakdown,
            health_status=str(payload.get("health_status", "UP") or "UP").upper(),
            health_status_since_utc=payload.get("health_status_since_utc"),
            health_last_transition_utc=payload.get("health_last_transition_utc"),
            health_transition_count=int(payload.get("health_transition_count", 0) or 0),
            health_status_breakdown=payload.get("health_status_breakdown", {}),
            health_last_reason=payload.get("health_last_reason"),
            health_last_reasons=list(payload.get("health_last_reasons", []) or []),
        )

        trust_scores = payload.get("trust_scores", [])
        if isinstance(trust_scores, list):
            for item in trust_scores[-200:]:
                try:
                    metrics.trust_scores.append(float(item))
                except (TypeError, ValueError):
                    continue

        return metrics, path

    def as_dict(self):
        with self._lock:
            avg_latency_ms = 0.0
            if self.latency_samples > 0:
                avg_latency_ms = round(self.total_latency_ms / self.latency_samples, 3)

            deny_ratio = 0.0
            if self.events_total > 0:
                deny_ratio = round(self.events_denied / self.events_total, 3)

            failed_action_rate = 0.0
            if self.actions_total > 0:
                failed_action_rate = round(self.actions_failed / self.actions_total, 3)

            return {
                "events_total": self.events_total,
                "events_allowed": self.events_allowed,
                "events_denied": self.events_denied,
                "pipeline_avg_latency_ms": avg_latency_ms,
                "deny_ratio": deny_ratio,
                "actions_total": self.actions_total,
                "actions_succeeded": self.actions_succeeded,
                "actions_failed": self.actions_failed,
                "duplicate_actions": self.duplicate_actions,
                "failed_action_rate": failed_action_rate,
                "correlation_hit_count": self.correlation_hit_count,
                "reason_code_breakdown": dict(self.reason_code_breakdown),
                "health_status": self.health_status,
                "health_status_since_utc": self.health_status_since_utc,
                "health_last_transition_utc": self.health_last_transition_utc,
                "health_transition_count": self.health_transition_count,
                "health_status_breakdown": dict(self.health_status_breakdown),
                "health_last_reason": self.health_last_reason,
                "health_last_reasons": list(self.health_last_reasons),
            }

    def record(
        self,
        decision: str,
        reason_code: str | None,
        latency_ms: float,
        trust_score: float | None,
        correlated: bool = False,
    ):
        with self._lock:
            self.events_total += 1
            self.total_latency_ms += float(latency_ms)
            self.latency_samples += 1

            normalized = str(decision).upper()
            if normalized == "ALLOW":
                self.events_allowed += 1
            elif normalized == "DENY":
                self.events_denied += 1

            if reason_code:
                self.reason_code_breakdown[reason_code] = self.reason_code_breakdown.get(reason_code, 0) + 1

            if trust_score is not None:
                try:
                    self.trust_scores.append(float(trust_score))
                except (TypeError, ValueError):
                    pass

            if correlated:
                self.correlation_hit_count += 1

    def record_action(self, status: str, duplicate: bool = False):
        with self._lock:
            self.actions_total += 1
            normalized = str(status).lower()
            if normalized == "success":
                self.actions_succeeded += 1
            elif normalized == "failed":
                self.actions_failed += 1
            if duplicate:
                self.duplicate_actions += 1

    def evaluate_alerts(self, alert_cfg: dict | None = None):
        cfg = alert_cfg or {}
        deny_spike_threshold = float(cfg.get("deny_spike_threshold", 0.5))
        trust_drop_threshold = float(cfg.get("trust_score_drop_threshold", 0.25))
        trust_window = int(cfg.get("trust_window", 20))
        failed_action_rate_threshold = float(cfg.get("failed_action_rate_threshold", 0.5))
        degraded_for_seconds_threshold = float(cfg.get("health_degraded_for_seconds", 0.0))
        down_for_seconds_threshold = float(cfg.get("health_down_for_seconds", 0.0))

        alerts = []
        snapshot = self.as_dict()

        if self.events_total > 0:
            deny_ratio = self.events_denied / max(self.events_total, 1)
            if deny_ratio >= deny_spike_threshold:
                alerts.append(
                    {
                        "type": "deny_spike",
                        "threshold": deny_spike_threshold,
                        "value": round(deny_ratio, 3),
                        "severity": "high",
                        "message": "Deny ratio above configured threshold",
                    }
                )

        if trust_window > 1 and len(self.trust_scores) >= trust_window * 2:
            scores = list(self.trust_scores)
            prior = scores[:-trust_window]
            recent = scores[-trust_window:]

            prior_avg = mean(prior) if prior else None
            recent_avg = mean(recent) if recent else None
            if prior_avg is not None and recent_avg is not None and (prior_avg - recent_avg) >= trust_drop_threshold:
                alerts.append(
                    {
                        "type": "trust_drop",
                        "threshold": trust_drop_threshold,
                        "value": round(prior_avg - recent_avg, 3),
                        "severity": "medium",
                        "message": "Trust score dropped sharply",
                    }
                )

        failed_action_rate = snapshot.get("failed_action_rate", 0.0)
        if snapshot.get("actions_total", 0) > 0 and failed_action_rate >= failed_action_rate_threshold:
            alerts.append(
                {
                    "type": "failed_action_rate",
                    "threshold": failed_action_rate_threshold,
                    "value": failed_action_rate,
                    "severity": "high",
                    "message": "Failed action rate above configured threshold",
                }
            )

        current_health = snapshot.get("health_status", "UP")
        health_duration_seconds = _seconds_since_iso(snapshot.get("health_status_since_utc"))
        if current_health == "DEGRADED" and health_duration_seconds >= degraded_for_seconds_threshold:
            alerts.append(
                {
                    "type": "health_degraded",
                    "threshold": degraded_for_seconds_threshold,
                    "value": round(health_duration_seconds, 3),
                    "severity": "high",
                    "message": "Service remains degraded",
                }
            )
        if current_health == "DOWN" and health_duration_seconds >= down_for_seconds_threshold:
            alerts.append(
                {
                    "type": "health_down",
                    "threshold": down_for_seconds_threshold,
                    "value": round(health_duration_seconds, 3),
                    "severity": "critical",
                    "message": "Service is down",
                }
            )

        return alerts

    def observe_health(self, status: str, reasons: list[str] | None = None, observed_at_utc: str | None = None):
        normalized_status = str(status or "DOWN").upper()
        if normalized_status not in {"UP", "DEGRADED", "DOWN"}:
            normalized_status = "DOWN"

        reason_list = [str(item) for item in (reasons or []) if str(item).strip()]
        observed_at = observed_at_utc or _utc_now_iso()

        with self._lock:
            current = self.health_status
            if current != normalized_status:
                self.health_transition_count += 1
                self.health_last_transition_utc = observed_at
                self.health_status_since_utc = observed_at
                self.health_status_breakdown[normalized_status] = self.health_status_breakdown.get(normalized_status, 0) + 1

            self.health_status = normalized_status
            self.health_last_reason = reason_list[0] if reason_list else None
            self.health_last_reasons = reason_list

    def dump_to_file(self, path: str | None):
        if not path:
            return

        with self._lock:
            payload = self.as_dict()
            payload.update(
                {
                    "total_latency_ms": self.total_latency_ms,
                    "latency_samples": self.latency_samples,
                    "trust_scores": list(self.trust_scores),
                    "health_status": self.health_status,
                    "health_status_since_utc": self.health_status_since_utc,
                    "health_last_transition_utc": self.health_last_transition_utc,
                    "health_transition_count": self.health_transition_count,
                    "health_status_breakdown": dict(self.health_status_breakdown),
                    "health_last_reason": self.health_last_reason,
                    "health_last_reasons": list(self.health_last_reasons),
                }
            )

            snapshot_path = Path(path)
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            with snapshot_path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, sort_keys=True)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _seconds_since_iso(value: str | None) -> float:
    if not value:
        return 0.0

    try:
        normalized = value.replace("Z", "+00:00")
        return max(0.0, (datetime.now(timezone.utc) - datetime.fromisoformat(normalized)).total_seconds())
    except ValueError:
        return 0.0
