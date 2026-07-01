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
