from palasik.policy.base import PolicyEngine


class RuleBasedPolicy(PolicyEngine):
    """
    Policy engine sederhana berbasis urutan aturan.

    Format rules:
    policy:
      type: rule
      rules:
        - name: suspicious_value
          when:
            trust_below: 0.4
            event_value_gt: 100
          action: RESTRICT
        - name: low_trust
          when:
            trust_below: 0.2
          action: QUARANTINE
      default_action: DENY
    """

    def __init__(self, policy_cfg: dict | None = None):
        cfg = policy_cfg or {}
        self.rules = cfg.get("rules", []) or []
        self.default_action = str(cfg.get("default_action", "DENY")).upper()

    def name(self):
        return "rule_policy"

    def _get_event_value(self, event):
        if not isinstance(event, dict):
            return None
        return event.get("value")

    def _match(self, trust_score, event, when_cfg):
        if not when_cfg:
            return False

        trust_above = when_cfg.get("trust_above")
        if trust_above is not None:
            try:
                if not (trust_score > float(trust_above)):
                    return False
            except (TypeError, ValueError):
                return False

        trust_below = when_cfg.get("trust_below")
        if trust_below is not None:
            try:
                if not (trust_score < float(trust_below)):
                    return False
            except (TypeError, ValueError):
                return False

        trust_below_eq = when_cfg.get("trust_below_eq")
        if trust_below_eq is not None:
            try:
                if not (trust_score <= float(trust_below_eq)):
                    return False
            except (TypeError, ValueError):
                return False

        trust_above_eq = when_cfg.get("trust_above_eq")
        if trust_above_eq is not None:
            try:
                if not (trust_score >= float(trust_above_eq)):
                    return False
            except (TypeError, ValueError):
                return False

        event_value = self._get_event_value(event)
        if "event_value_gt" in when_cfg:
            try:
                if not (event_value is not None and float(event_value) > float(when_cfg["event_value_gt"])):
                    return False
            except (TypeError, ValueError):
                return False

        if "event_value_lt" in when_cfg:
            try:
                if not (event_value is not None and float(event_value) < float(when_cfg["event_value_lt"])):
                    return False
            except (TypeError, ValueError):
                return False

        if "event_type" in when_cfg:
            if not (isinstance(event, dict) and event.get("type") == when_cfg["event_type"]):
                return False

        return True

    def decide(self, trust_score: float, event: dict, context) -> str:
        for rule in self.rules:
            name = rule.get("name") if isinstance(rule, dict) else None
            if not isinstance(rule, dict):
                continue

            when_cfg = rule.get("when", {}) or {}
            if self._match(trust_score, event, when_cfg):
                action = rule.get("action", self.default_action)
                return str(action).upper()

        return str(self.default_action).upper()

    def explain(self, trust_score: float, event: dict, context) -> list[str]:
        for rule in self.rules:
            if not isinstance(rule, dict):
                continue

            when_cfg = rule.get("when", {}) or {}
            if self._match(trust_score, event, when_cfg):
                rule_name = rule.get("name") or "unnamed"
                action = str(rule.get("action", self.default_action)).upper()
                return [
                    f"rule='{rule_name}' matched",
                    f"action={action}",
                    f"trust_score={trust_score}",
                ]

        return [
            "no rule matched",
            f"default_action={self.default_action}",
            f"trust_score={trust_score}",
        ]
