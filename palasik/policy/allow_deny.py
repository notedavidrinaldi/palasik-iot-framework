# palasik/policy/allow_deny.py

from palasik.policy.base import PolicyEngine

class AllowDenyPolicy(PolicyEngine):

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def name(self):
        return "allow_deny_policy"

    def decide(self, trust_score: float, event: dict, context) -> str:
        if trust_score >= self.threshold:
            return "ALLOW"
        return "DENY"
