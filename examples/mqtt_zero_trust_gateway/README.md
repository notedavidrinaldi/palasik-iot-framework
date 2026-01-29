# MQTT Zero Trust Gateway (PALASIK Example)

Contoh ini menunjukkan bagaimana **PALASIK digunakan sebagai IoT Gateway berbasis MQTT**
dengan **Zero Trust enforcement di level event**.

Setiap data sensor:
- dievaluasi trust-nya
- diputuskan policy-nya
- lalu **DITERUSKAN atau DIBLOK**

---

## 🔧 Prasyarat

- Python >= 3.10
- Mosquitto MQTT Broker

Install broker (Ubuntu):

```bash
sudo apt install mosquitto mosquitto-clients
sudo systemctl start mosquitto
```
---
## 📦 Install PALASIK

```bash
pip install palasik
```
---
## ⚙️ Konfigurasi

File config.yaml sudah disediakan dan berisi:

- MQTT broker

- policy threshold

- plugin logger
---
## ▶️ Menjalankan Gateway

```bash
./run.sh
```

Jika berhasil, kamu akan melihat:

```bash
[PALASIK] Starting agent...
```
---
## 📡 Kirim Event (ALLOW)

```bash
mosquitto_pub -t palasik/sensor/temp -m '{"value": 42}'
```

Expected:

- trust tinggi

- policy ALLOW

- event diproses plugin
---
## 🚫 Kirim Event (DENY)

```bash
mosquitto_pub -t palasik/sensor/temp -m '{"value": 150}'
```

## 🧠 Konsep yang Ditunjukkan
Expected:

- trust rendah

- policy DENY

- event DIBLOK

- Zero Trust (no implicit trust)

Trust-based decision

Policy enforcement di edge

Event-level security

Contoh ini adalah baseline resmi untuk semua pengembangan PALASIK berikutnya.
```code

---

## 3️⃣ ISI `examples/mqtt_zero_trust_gateway/config.yaml`

```yaml
palasik:
  broker:
    host: localhost
    port: 1883
    topic: palasik/sensor/#

  policy:
    type: allow_deny
    threshold: 0.7

  plugins:
    enabled:
      - logger
```

👉 SENGAJA sederhana.
Jangan pamer konfigurasi dulu.


