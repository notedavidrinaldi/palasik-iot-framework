#INTI PALASIK - Menilai device berdasarkan perilaku, bukan identitas.
# palasik/core/trust_engine.py

class TrustEngine:
    def __init__(self):
        self.trust_map = {}

    def evaluate(self, device):
        ip = device["ip"]

        # Trust awal
        trust = self.trust_map.get(ip, 0.5)

        # Parameter evaluasi
        protocol = device.get("protocol", "UNKNOWN")
        freq = device.get("count", 1)

        # Penilaian berbasis protokol
        if protocol in ["MQTT", "HTTP"]:
            trust += 0.02
        else:
            trust -= 0.05

        # Penilaian berbasis frekuensi
        if freq > 10:
            trust -= 0.1

        # Clamp nilai trust
        trust = max(0.0, min(1.0, trust))

        # Simpan state
        self.trust_map[ip] = trust

        return {
            "ip": ip,
            "trust_score": round(trust, 2),
            "protocol": protocol
        }

#📌 PENTING SECARA AKADEMIK

#Tidak pakai ML dulu (Phase 3)
