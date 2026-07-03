from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class CorrelationResult:
    is_correlated: bool
    correlation_id: str | None = None
    window_count: int = 0


class CorrelationEngine:
    def __init__(self, window_seconds: int = 120, repeat_threshold: int = 3, risk_threshold: int = 75):
        self.window_seconds = window_seconds
        self.repeat_threshold = max(1, int(repeat_threshold))
        self.risk_threshold = risk_threshold
        self._state: dict[str, deque] = defaultdict(deque)

    def evaluate(self, event: dict[str, Any], risk_score: int) -> CorrelationResult:
        if risk_score < self.risk_threshold:
            return CorrelationResult(False, None, 0)

        now = datetime.now(timezone.utc).timestamp()
        source = self._extract_key(event)
        self._cleanup_source(source, now)

        queue = self._state[source]
        queue.append((now, event.get("event_id")))

        count = len(queue)
        if count < self.repeat_threshold:
            return CorrelationResult(False, None, count)

        correlation_id = f"corr-{source}-{int(now)}"
        return CorrelationResult(True, correlation_id, count)

    def _extract_key(self, event: dict[str, Any]) -> str:
        source = event.get("source") if isinstance(event, dict) else {}
        device = "unknown"
        event_type = event.get("type", "generic") if isinstance(event, dict) else "generic"

        if isinstance(source, dict):
            device = source.get("device_id") or source.get("ip") or device

        return f"{device}|{event_type}"

    def _cleanup_source(self, source: str, now_ts: float):
        queue = self._state[source]
        while queue and now_ts - queue[0][0] > self.window_seconds:
            queue.popleft()

        if not queue:
            self._state.pop(source, None)
