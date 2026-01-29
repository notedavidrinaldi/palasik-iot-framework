from palasik.policy.allow_deny import AllowDenyPolicy


def test_allow_when_trust_above_threshold():
    policy = AllowDenyPolicy(threshold=0.7)
    decision = policy.decide(0.9, {}, None)
    assert decision == "ALLOW"


def test_deny_when_trust_below_threshold():
    policy = AllowDenyPolicy(threshold=0.7)
    decision = policy.decide(0.2, {}, None)
    assert decision == "DENY"


def test_edge_case_equal_threshold():
    policy = AllowDenyPolicy(threshold=0.7)
    decision = policy.decide(0.7, {}, None)
    assert decision == "ALLOW"
