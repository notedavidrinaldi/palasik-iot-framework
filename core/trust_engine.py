def calculate_trust(data):
    """
    data = {
        failed_auth_count: int,
        anomaly: bool,
        packet_rate: int
    }
    """

    trust = 1.0

    trust -= 0.1 * data["failed_auth_count"]

    if data["anomaly"]:
        trust -= 0.4

    if data["packet_rate"] > 300:
        trust -= 0.2

    return max(trust, 0.0)
