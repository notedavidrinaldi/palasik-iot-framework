def decide_policy(trust_score):
    if trust_score >= 0.8:
        return "ALLOW"
    elif trust_score >= 0.5:
        return "RESTRICT"
    else:
        return "QUARANTINE"
