"""SIMULASI BERJALAN

Quick demo command-line untuk menyalurkan trafik ke pipeline trust → policy → decision.
"""

from palasik.core.device_registry import DeviceRegistry
from palasik.trust.simple import SimpleTrustEvaluator
from palasik.policy.allow_deny import AllowDenyPolicy
from palasik.core.events import log_event
from palasik.enforcement.enforcer import enforce
from palasik.enforcement.firewall import FirewallEnforcer

registry = DeviceRegistry()
trust_engine = SimpleTrustEvaluator()
policy_engine = AllowDenyPolicy(threshold=0.7)
enforcer = FirewallEnforcer(dry_run=True)

# Simulasi traffic
traffic = [
    ("192.168.1.10", "B8:27:EB:AA", "MQTT", 40),
    ("192.168.1.10", "B8:27:EB:AA", "MQTT", 130),
    ("192.168.1.20", "DC:A6:32:BB", "HTTP", 50),
    ("192.168.1.10", "B8:27:EB:ZZ", "UNKNOWN", 200),
    ("192.168.1.10", "B8:27:EB:ZZ", "UNKNOWN", 180),
]

for ip, mac, proto, value in traffic:
    device = registry.register_or_update(ip, mac, proto)
    event = {
        "ip": ip,
        "source": ip,
        "value": value,
        "protocol": proto,
        "type": "mqtt_sample",
    }
    trust_score = trust_engine.evaluate(event, None)
    action = policy_engine.decide(trust_score, event, None)

    if action == "QUARANTINE":
        enforcer.block_ip(ip)

    result = enforce(ip, action)
    log_event(ip, trust_score, action)
    print("ENFORCE:", result)
