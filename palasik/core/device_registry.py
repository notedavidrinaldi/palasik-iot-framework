# device_registry.py
# palasik/core/device_registry.py
import time

class DeviceRegistry:
    def __init__(self):
        self.devices = {}

    def register_or_update(self, ip, mac, protocol):
        now = time.time()

        if ip not in self.devices:
            self.devices[ip] = {
                "ip": ip,
                "mac": mac,
                "protocol": protocol,
                "first_seen": now,
                "last_seen": now,
                "count": 1
            }
        else:
            device = self.devices[ip]
            device["last_seen"] = now
            device["count"] += 1

            # update protocol jika berubah
            if protocol:
                device["protocol"] = protocol

        return self.devices[ip]

#phase1
#Tugas:1.Menyimpan & mengelola profil device BUKAN menilai trust
#📌 Catatan desain: Registry tidak pintar , Registry tidak membuat keputusan,Registry hanya menyimpan fakta
