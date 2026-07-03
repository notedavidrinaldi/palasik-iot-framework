from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from palasik.core.decision import Decision


@dataclass
class RiskPolicyConfig:
    warn_threshold: int = 55
    quarantine_threshold: int = 75
    critical_threshold: int = 92
    critical_action: str = "BLOCK_ALARM"


@dataclass
class RiskContext:
    base: int
    adjustments: int
    total: int
    details: list[str]


class RiskEngine:
    def __init__(self, config: RiskPolicyConfig | None = None):
        self.config = config or RiskPolicyConfig()

    def _normalize_decision(self, decision: Decision | str) -> Decision:
        return Decision.from_value(decision)

    def score(self, trust_score: float, event: dict[str, Any], policy_decision: Decision | str) -> tuple[int, list[str]]:
        trust = float(trust_score) if trust_score is not None else 0.5
        base = int(max(0, min(100, round((1.0 - trust) * 100, 2))))
        details = [f"base_from_trust={base}"]

        adjustments = 0

        value = event.get("value") if isinstance(event, dict) else None
        try:
            numeric = float(value)
            if numeric > 150:
                penalties = min(20, int((numeric - 150) / 5))
                adjustments += penalties
                details.append(f"value={numeric} => +{penalties}")
        except (TypeError, ValueError):
            pass

        trust_ctx = event.get("trust_ctx") if isinstance(event, dict) else None
        if isinstance(trust_ctx, dict):
            if trust_ctx.get("authenticated") is False:
                adjustments += 20
                details.append("not_authenticated => +20")
            if trust_ctx.get("token_ttl_ok") is False:
                adjustments += 10
                details.append("token_ttl_ok=false => +10")

        decision_value = self._normalize_decision(policy_decision)
        if decision_value == Decision.DENY:
            adjustments += 25
            details.append("policy=Deny => +25")
        elif decision_value == Decision.QUARANTINE:
            adjustments += 15
            details.append("policy=Quarantine => +15")
        elif decision_value == Decision.MONITOR:
            adjustments += 5
            details.append("policy=Monitor => +5")

        total = max(0, min(100, base + adjustments))
        return total, details

    def label(self, score: int) -> str:
        if score >= 81:
            return "CRITICAL"
        if score >= 61:
            return "HIGH"
        if score >= 26:
            return "MEDIUM"
        return "LOW"

    def escalate(self, policy_decision: Decision | str, risk_score: int) -> str:
        decision = self._normalize_decision(policy_decision)

        if decision == Decision.CHALLENGE:
            return Decision.CHALLENGE.value
        if decision == Decision.BLOCK_ALARM:
            return Decision.BLOCK_ALARM.value

        if decision == Decision.DENY:
            return Decision.DENY.value

        if decision == Decision.QUARANTINE and risk_score >= self.config.critical_threshold:
            return Decision.BLOCK_ALARM.value

        if decision == Decision.ALLOW:
            if risk_score >= self.config.critical_threshold:
                return Decision.BLOCK_ALARM.value
            if risk_score >= self.config.quarantine_threshold:
                return Decision.QUARANTINE.value
            if risk_score >= self.config.warn_threshold:
                return Decision.WARN.value
            return Decision.ALLOW.value

        if decision in (Decision.RESTRICT, Decision.MONITOR):
            return Decision.WARN.value

        return decision.value
