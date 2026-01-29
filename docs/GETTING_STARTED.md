# Getting Started with PALASIK

Dokumen ini memandu penggunaan PALASIK dari nol
hingga gateway Zero Trust pertama berjalan.

---

## 1. Instalasi

```bash
pip install palasik
```
Isi (copas mentah):

```bash
python - <<'EOF'
import palasik
print(palasik.__version__)
EOF
```

## 2. Inisialisasi Project
```bash
mkdir palasik-demo
cd palasik-demo
palasik init
```

File yang dihasilkan:

```code
config.yaml
```

## 3. Contoh Konfigurasi

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
## 4. Menjalankan Gateway

```bash
palasik run --config config.yaml
```

Jika berhasil:

```code
[PALASIK] Starting agent...
```

## 5. Kirim Event Uji
```bash
mosquitto_pub -t palasik/sensor/temp -m '{"value": 42}'
```

## 6. Apa yang Terjadi?

1. Event diterima adapter

2. Trust Engine menghitung skor

3. Policy Engine memutuskan

4. Plugin mengeksekusi aksi
PALASIK tidak pernah mempercayai event secara default.

---

### 2️⃣ README contoh (example-first)
User **lebih percaya contoh daripada klaim**.

**Edit file:**
```bash
nano examples/mqtt_zero_trust_gateway/README.md
```

isi:

# MQTT Zero Trust Gateway Example

Contoh gateway IoT berbasis MQTT
dengan kebijakan Zero Trust menggunakan PALASIK.

---

## Cara Menjalankan

```bash
cd examples/mqtt_zero_trust_gateway
./run.sh
```

Struktur

```code
.
├── config.yaml
├── run.sh
└── README.md
```

Eksperimen
Event Trusted

```bash
mosquitto_pub -t palasik/sensor/temp -m '{"value": 30}'
```
Event Suspicious

```bash
mosquitto_pub -t palasik/sensor/temp -m '{"value": 999}'
```

Perhatikan perbedaan keputusan policy.


---

### 3️⃣ Tambah badge CI di README utama
Ini **sinyal kepercayaan**.

Tambahkan di `README.md` bagian atas:
```md
[![CI](https://github.com/notedavidrinaldi/palasik-iot-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/notedavidrinaldi/palasik-iot-framework/actions)
```
### 4️⃣ CONTRIBUTING.md (pendek tapi tegas)

Biar orang nggak asal PR.

```bash
nano CONTRIBUTING.md
```

# Contributing to PALASIK

Terima kasih tertarik berkontribusi.

## Aturan Dasar
- Semua PR **harus lulus pytest**
- Tambahkan test untuk fitur baru
- Jangan refactor tanpa alasan jelas

## Setup Dev
```bash
pip install -e .
pip install pytest
pytest
```
PR tanpa test kemungkinan besar ditolak.


---

## 5️⃣ Commit docs (jangan dicampur)
```bash
git add docs examples README.md CONTRIBUTING.md
git commit -m "docs: add getting started, examples, and contribution guide"
git push
```

