"""
PALASIK Policy Engine
Otak pengambilan keputusan berbasis trust score
"""

class PolicyEngine:
    def decide(self, trust_score):
        if trust_score >= 0.8:
            return "ALLOW"
        elif trust_score >= 0.5:
            return "MONITOR"
        elif trust_score >= 0.3:
            return "RESTRICT"
        else:
            return "QUARANTINE"

