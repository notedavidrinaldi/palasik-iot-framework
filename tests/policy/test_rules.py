from palasik.policy.rules import RuleBasedPolicy


def test_rule_policy_matches_restrict():
    cfg = {
        "rules": [
            {
                "name": "high value",
                "when": {
                    "event_value_gt": 100,
                },
                "action": "RESTRICT",
            },
            {
                "name": "low trust",
                "when": {
                    "trust_below": 0.2,
                },
                "action": "QUARANTINE",
            },
        ],
        "default_action": "ALLOW",
    }

    policy = RuleBasedPolicy(cfg)

    decision = policy.decide(0.9, {"value": 120}, None)
    rationale = policy.explain(0.9, {"value": 120}, None)

    assert decision == "RESTRICT"
    assert any("high value" in r for r in rationale)


def test_rule_policy_default_applies_fallback():
    cfg = {
        "rules": [
            {
                "name": "block",
                "when": {"trust_below": 0.2},
                "action": "DENY",
            }
        ],
        "default_action": "ALLOW",
    }

    policy = RuleBasedPolicy(cfg)

    decision = policy.decide(0.5, {}, None)
    rationale = policy.explain(0.5, {}, None)

    assert decision == "ALLOW"
    assert rationale[0] == "no rule matched"


def test_rule_policy_supports_condition_v1_syntax():
    cfg = {
        "default_action": "DENY",
        "rules": [
            {
                "id": "deny_unknown",
                "condition": {
                    "op": "eq",
                    "key": "source.device_id",
                    "value": "unknown",
                },
                "action": "DENY",
                "reason_code": "UNKNOWN_DEVICE",
            },
            {
                "id": "allow_trusted",
                "condition": {
                    "op": "gte",
                    "key": "trust_score",
                    "value": 0.75,
                },
                "action": "ALLOW",
                "reason_code": "TRUSTED",
            },
        ],
    }

    policy = RuleBasedPolicy(cfg)

    deny = policy.decide(0.2, {"source": {"device_id": "unknown"}}, None)
    assert deny == "DENY"
    assert policy.reason_code(0.2, {"source": {"device_id": "unknown"}}, None) == "UNKNOWN_DEVICE"

    allow = policy.decide(0.9, {"source": {"device_id": "edge-01"}}, None)
    assert allow == "ALLOW"
    assert policy.reason_code(0.9, {"source": {"device_id": "edge-01"}}, None) == "TRUSTED"
