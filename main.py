from core.trust_engine import calculate_trust
from core.policy_engine import decide_policy
from core.device_registry import is_registered, update_trust
import os

# contoh data simulasi
incoming_data = {
    "device_id": "D04",
    "device_ip": "192.168.1.50",
    "failed_auth_count": 5,
    "anomaly": True,
    "packet_rate": 400
}

trust = calculate_trust(incoming_data)
policy = decide_policy(trust)

print("Trust Score:", trust)
print("Policy:", policy)

if policy == "QUARANTINE":
    os.system(f"bash enforcement/quarantine.sh {incoming_data['device_ip']}")

elif policy == "ALLOW":
    os.system(f"bash enforcement/firewall.sh {incoming_data['device_ip']}")
