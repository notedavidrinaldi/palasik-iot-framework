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

    Format fase 1+:
      - id: rule_name
        condition:
          op: gte
          key: trust_score
          value: 0.75
        action: ALLOW
        reason_code: TRUSTED_DEVICE
    """

    def __init__(self, policy_cfg: dict | None = None):
        cfg = policy_cfg or {}
        self.rules = cfg.get("rules", []) or []
        self.default_action = str(cfg.get("default_action", "DENY")).upper()
        self._last_reason_code = None
        self._last_match = None
        self._last_matched_actions = []

    def name(self):
        return "rule_policy"

    def _get_event_value(self, event):
        if not isinstance(event, dict):
            return None
        return event.get("value")

    def _extract_field(self, event: dict | None, key: str):
        if event is None or not isinstance(event, dict):
            return None

        value = event
        for part in str(key).split("."):
            if not isinstance(value, dict):
                return None
            value = value.get(part)
        return value

    def _match_condition(self, trust_score, event, condition):
        if not isinstance(condition, dict):
            return False

        op = str(condition.get("op", "")).lower()
        key = condition.get("key")
        value = condition.get("value")

        if not key:
            return False

        if key == "trust_score":
            current = trust_score
        else:
            current = self._extract_field(event, key)

        if op == "exists":
            return current is not None

        if op in ("eq", "equal", "equals"):
            return current == value

        if op == "ne":
            return current != value

        if op in ("gt", "greater_than"):
            try:
                return float(current) > float(value)
            except (TypeError, ValueError):
                return False

        if op in ("gte", "greater_than_or_equal"):
            try:
                return float(current) >= float(value)
            except (TypeError, ValueError):
                return False

        if op in ("lt", "less_than"):
            try:
                return float(current) < float(value)
            except (TypeError, ValueError):
                return False

        if op in ("lte", "less_than_or_equal"):
            try:
                return float(current) <= float(value)
            except (TypeError, ValueError):
                return False

        if op == "in":
            if isinstance(value, (list, tuple, set)):
                return current in value
            return False

        if op in ("nin", "not_in"):
            if isinstance(value, (list, tuple, set)):
                return current not in value
            return True

        if op == "contains":
            if current is None:
                return False
            try:
                return value in current
            except TypeError:
                return False

        return False

    def _match_when(self, trust_score, event, when_cfg):
        if not when_cfg:
            return False

        if not isinstance(when_cfg, dict):
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

    def _match(self, trust_score, event, rule):
        if not isinstance(rule, dict):
            return None

        condition = rule.get("condition")
        if condition is not None:
            if self._match_condition(trust_score, event, condition):
                return "condition"
            return None

        when_cfg = rule.get("when", {})
        if self._match_when(trust_score, event, when_cfg):
            return "when"

        return None

    def _build_rationale(self, rule, action, trust_score):
        reason_code = (rule.get("reason_code") if isinstance(rule, dict) else None) or ""
        if reason_code:
            return [
                f"rule='{rule.get('name', rule.get('id', 'unnamed'))}' matched",
                f"action={action}",
                f"trust_score={trust_score}",
                f"reason_code={reason_code}",
            ]

        return [
            f"rule='{rule.get('name', rule.get('id', 'unnamed'))}' matched",
            f"action={action}",
            f"trust_score={trust_score}",
        ]

    def _iter_rules(self):
        def _priority(rule):
            try:
                return int(rule.get("priority", 0))
            except (TypeError, ValueError):
                return 0

        return sorted(self.rules, key=_priority, reverse=True)

    def decide(self, trust_score: float, event: dict, context) -> str:
        self._last_reason_code = None
        self._last_match = None
        self._last_matched_actions = []

        for rule in self._iter_rules():
            if self._match(trust_score, event, rule) is None:
                continue

            action = str(rule.get("action", self.default_action)).upper()
            reason_code = rule.get("reason_code") if isinstance(rule, dict) else None
            self._last_reason_code = reason_code
            self._last_match = rule
            actions = rule.get("actions")
            if isinstance(actions, list):
                self._last_matched_actions = [str(a) for a in actions if str(a).strip()]
            return action

        return str(self.default_action).upper()

    def explain(self, trust_score: float, event: dict, context) -> list[str]:
        self._last_reason_code = None
        self._last_match = None
        self._last_matched_actions = []

        for rule in self._iter_rules():
            if self._match(trust_score, event, rule) is None:
                continue

            action = str(rule.get("action", self.default_action)).upper()
            reason_code = rule.get("reason_code") if isinstance(rule, dict) else None
            self._last_reason_code = reason_code
            self._last_match = rule
            actions = rule.get("actions")
            if isinstance(actions, list):
                self._last_matched_actions = [str(a) for a in actions if str(a).strip()]
            return self._build_rationale(rule, action, trust_score)

        return [
            "no rule matched",
            f"default_action={self.default_action}",
            f"trust_score={trust_score}",
        ]

    def reason_code(self, trust_score: float, event: dict, context) -> str | None:
        self.explain(trust_score, event, context)

        if self._last_reason_code:
            return str(self._last_reason_code)

        return None

    def last_match(self):
        return self._last_match

    def last_matched_actions(self):
        return list(self._last_matched_actions)
