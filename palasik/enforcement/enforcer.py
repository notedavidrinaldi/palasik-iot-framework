# palasik/enforcement/enforcer.py

def enforce(ip, action):
    if action == "ALLOW":
        return f"{ip} allowed"

    elif action == "MONITOR":
        return f"👀{ip} under monitoring"

    elif action == "RESTRICT":
        return f"⚠️ {ip} rate-limited (simulated)"

    elif action == "QUARANTINE":
        return f"🚫{ip} isolated (simulated)"

    return "UNKNOWN ACTION"
