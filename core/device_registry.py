# Device Registry PALASIK

DEVICE_REGISTRY = {
    "D01": {
        "type": "sensor",
        "owner": "lab",
        "trust": 1.0
    },
    "D02": {
        "type": "rfid",
        "owner": "lab",
        "trust": 1.0
    }
}

def is_registered(device_id):
    return device_id in DEVICE_REGISTRY

def get_device(device_id):
    return DEVICE_REGISTRY.get(device_id)

def update_trust(device_id, score):
    if device_id in DEVICE_REGISTRY:
        DEVICE_REGISTRY[device_id]["trust"] = score

