from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List


class Decision(str, Enum):
    ALLOW = "ALLOW"
    MONITOR = "MONITOR"
    RESTRICT = "RESTRICT"
    CHALLENGE = "CHALLENGE"
    QUARANTINE = "QUARANTINE"
    DENY = "DENY"

    @classmethod
    def from_value(cls, value):
        """Normalisasi nilai keputusan dari policy menjadi Decision.

        Menerima:
        - enum Decision
        - string (case-insensitive)
        - nilai lain akan dianggap DENY bila tidak valid
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            normalized = value.strip().upper()
            try:
                return cls(normalized)
            except ValueError:
                pass
        return cls.DENY


@dataclass
class DecisionRecord:
    event_id: str
    trust_score: float
    decision: Decision
    policy_name: str
    rationale: List[str]
    event_snapshot: dict | None = None
    context: Any | None = None
    challenge: str | None = None
    created_at_utc: str | None = None

    def __post_init__(self):
        if self.created_at_utc is None:
            self.created_at_utc = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "trust_score": self.trust_score,
            "decision": self.decision.value,
            "policy_name": self.policy_name,
            "rationale": list(self.rationale),
            "event_snapshot": self.event_snapshot,
            "challenge": self.challenge,
            "created_at_utc": self.created_at_utc,
        }
