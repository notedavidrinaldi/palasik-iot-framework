from palasik.policy.allow_deny import AllowDenyPolicy


def test_allow_when_trust_high():
    policy = AllowDenyPolicy(threshold=0.7)
    assert policy.decide(0.9, {}, None) == "ALLOW"


def test_deny_when_trust_low():
    policy = AllowDenyPolicy(threshold=0.7)
    assert policy.decide(0.3, {}, None) == "DENY"
