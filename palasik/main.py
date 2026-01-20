#SIMULASI BERJALAN
# main.py
from palasik.core.dependency import ensure_dependencies
ensure_dependencies()

from palasik.core.device_registry import DeviceRegistry
from palasik.core.trust_engine import TrustEngine
from palasik.core.policy_engine import PolicyEngine
from palasik.core.events import log_event
from palasik.enforcement.enforcer import enforce
from palasik.enforcement.firewall import FirewallEnforcer
import time

registry = DeviceRegistry()
trust_engine = TrustEngine()
policy_engine = PolicyEngine()
enforcer = FirewallEnforcer(dry_run=True)

# Simulasi traffic
traffic = [
    ("192.168.1.10", "B8:27:EB:AA", "MQTT"),
    ("192.168.1.10", "B8:27:EB:AA", "MQTT"),
    ("192.168.1.20", "DC:A6:32:BB", "HTTP"),
    ("192.168.1.10", "B8:27:EB:ZZ", "UNKNOWN"),  # spoof
    ("192.168.1.10", "B8:27:EB:ZZ", "UNKNOWN"),
]

for ip, mac, proto in traffic:
    device = registry.register_or_update(ip, mac, proto)
    trust = trust_engine.evaluate(device)
    action = policy_engine.decide(trust["trust_score"])

    if action == "QUARANTINE":
        enforcer.block_ip(ip)

    result = enforce(ip, action)
    log_event(ip, trust["trust_score"], action)
    print("ENFORCE:", result)
    time.sleep(1)

