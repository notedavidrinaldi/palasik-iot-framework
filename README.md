# 🧿 PALASIK  
**Pengaman Layer Edge Sistem IoT Kritis**  
*A Trust-Aware Zero Trust IoT Gateway Framework*

![Research](https://img.shields.io/badge/type-research-blue)
![IoT](https://img.shields.io/badge/domain-IoT-orange)
![Zero Trust](https://img.shields.io/badge/security-zero--trust-red)
![Edge](https://img.shields.io/badge/edge-computing-green)
![Python](https://img.shields.io/badge/lang-python-blue)

---


```md
# PALASIK IoT Framework

**PALASIK** (Policy-Aware Lightweight Adaptive Security for IoT) adalah
framework Python untuk membangun **IoT Gateway berbasis Zero Trust** yang
modular, extensible, dan siap dikembangkan secara kolaboratif.

PALASIK dirancang untuk:
- menerima event dari berbagai sumber IoT (MQTT, HTTP, dll)
- mengevaluasi **trust**
- menerapkan **policy (allow / deny)**
- memproses event melalui **plugin system**

Framework ini cocok untuk:
- IoT Gateway
- Edge Computing
- Security-aware data pipeline
- Riset & implementasi Zero Trust pada IoT

---

## ✨ Fitur Utama

- Modular **Core Agent**
- **Plugin System** (drop-in, auto discovery)
- **Trust Engine**
- **Policy Engine**
- Adapter dunia nyata (MQTT)
- Siap dikembangkan untuk riset maupun produksi

---

## 📦 Struktur Proyek

```

palasik-iot-framework/
├── palasik/        # Core framework
├── plugins/        # Plugin ekstensi
├── examples/       # Contoh runnable
├── docs/           # Dokumentasi
├── tests/          # Unit & integration test
└── README.md

````

---

## 🚀 Quick Start (MQTT Gateway)

### 1. Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

### 2. Jalankan Broker MQTT

```bash
sudo apt install mosquitto mosquitto-clients
sudo systemctl start mosquitto
```

### 3. Jalankan PALASIK

```bash
python examples/mqtt_gateway.py
```

### 4. Kirim Event

```bash
mosquitto_pub -t palasik/sensor/temp -m '{"value": 42}'
```

---

## 🧠 Konsep Inti

* **Trust Engine** → menghitung skor kepercayaan event
* **Policy Engine** → memutuskan ALLOW / DENY
* **Plugin** → merespons keputusan
* **Adapter** → menjembatani dunia luar

---

## 📚 Dokumentasi Lanjutan

* `docs/ARCHITECTURE.md` — arsitektur & alur sistem
* `docs/CONFIG.md` — konfigurasi YAML / ENV
* `docs/raw/` — dokumentasi riset & bahan jurnal

---

## 🤝 Kontribusi

PALASIK bersifat open-source dan terbuka untuk kontribusi.
Silakan lihat `CONTRIBUTING.md`.

---

## 📄 Lisensi

MIT License

````

---

# 2️⃣ docs/ARCHITECTURE.md — ARSITEKTUR & ALUR

👉 **Buat file `docs/ARCHITECTURE.md`**

```md
# PALASIK Architecture

Dokumen ini menjelaskan arsitektur internal PALASIK sebagai framework
IoT Gateway berbasis Zero Trust.

---

## 🧩 Komponen Utama

1. **Agent**
   - Runtime utama
   - Mengelola lifecycle

2. **Adapter**
   - Input dari dunia luar (MQTT, HTTP, dll)
   - Mengubah data menjadi event PALASIK

3. **Trust Engine**
   - Menghitung skor trust (0.0 – 1.0)

4. **Policy Engine**
   - Menentukan keputusan (ALLOW / DENY)

5. **Plugin**
   - Menangani event & keputusan

---

## 🔁 Alur Event

```mermaid
sequenceDiagram
    participant Device as IoT Device
    participant Broker as MQTT Broker
    participant Adapter as MQTT Adapter
    participant Agent as PALASIK Agent
    participant Trust as Trust Engine
    participant Policy as Policy Engine
    participant Plugin as Plugin

    Device ->> Broker: publish data
    Broker ->> Adapter: message
    Adapter ->> Agent: emit_event()
    Agent ->> Trust: evaluate(event)
    Trust ->> Agent: trust_score
    Agent ->> Policy: decide(trust_score)
    Policy ->> Agent: ALLOW / DENY
    Agent ->> Plugin: on_event(event, decision)
````

---

## 🧠 Prinsip Desain

* **Single Direction Flow**
* **Separation of Concern**
* **Policy is Explicit**
* **Zero Trust by Default**

---

## 📌 Catatan Penting

* Adapter tidak tahu policy
* Policy tidak tahu sumber event
* Plugin tidak mengubah keputusan

Ini memastikan PALASIK tetap aman, modular, dan scalable.

````

---

# 3️⃣ docs/CONFIG.md — KONFIGURASI (YAML / ENV)

👉 **Buat file `docs/CONFIG.md`**

```md
# PALASIK Configuration

PALASIK mendukung konfigurasi melalui **YAML** dan **Environment Variable**.

---

## 📄 Contoh config.yaml

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
````

---

## 🌱 Environment Variables

```env
PALASIK_BROKER_HOST=localhost
PALASIK_BROKER_PORT=1883
PALASIK_POLICY_THRESHOLD=0.7
```

---

## 🔐 Prioritas Konfigurasi

1. ENV
2. YAML
3. Default code

---

## 🧠 Rencana Implementasi

* Loader config di Agent
* Validasi schema
* Hot reload (opsional)

Konfigurasi akan menjadi fokus di versi berikutnya.

```

---

# 4️⃣ TESTING & CI — LANGKAH SELANJUTNYA (SETELAH INI)

Belum kita kerjakan sekarang, tapi **inilah roadmap teknisnya**:

### 🧪 Testing
- `tests/core/test_agent.py`
- `tests/policy/test_allow_deny.py`
- `tests/plugins/test_loader.py`
- Mock adapter

### 🔄 CI (GitHub Actions)
- Python 3.10–3.12
- Lint (ruff / flake8)
- Unit test
- Coverage



----
## 📌 Abstrak
**PALASIK** adalah framework riset keamanan **Internet of Things (IoT)**  
berbasis **Raspberry Pi** yang menerapkan konsep  
**Zero Trust Security Architecture di level edge gateway**.

Berbeda dengan pendekatan tradisional yang hanya mengamankan cloud atau network perimeter,  
PALASIK menempatkan **mekanisme penilaian kepercayaan (trust evaluation)**  
langsung di gateway IoT untuk:

- mendeteksi perangkat mencurigakan,
- menilai perilaku komunikasi,
- dan merespons ancaman secara adaptif.

Framework ini dirancang **ringan, modular, dan reproducible**  
untuk kebutuhan **penelitian akademik, eksperimen laboratorium, dan prototipe industri kecil**.

---

## 🎯 Latar Belakang Masalah
Sebagian besar sistem IoT saat ini masih:

- ❌ Mempercayai semua sensor di jaringan
- ❌ Mengandalkan autentikasi statis (password / TLS saja)
- ❌ Fokus mengirim data ke cloud tanpa validasi di edge

Padahal di lapangan sering terjadi:
- Rogue device
- Spoofing identitas sensor
- Manipulasi data di gateway
- Keterlambatan respon keamanan dari cloud

👉 **PALASIK hadir untuk menutup celah ini di level edge.**

---

## 🧠 Kontribusi Ilmiah Utama
PALASIK memberikan kontribusi riset sebagai berikut:

### 1️⃣ Trust Engine Berbasis Edge
- Evaluasi kepercayaan perangkat secara dinamis
- Trust score berbasis:
  - identitas (IP, MAC),
  - perilaku komunikasi,
  - konteks operasional

### 2️⃣ Policy Engine Modular
- Pengambilan keputusan berbasis kebijakan
- Aksi proporsional:
  - `ALLOW`
  - `MONITOR`
  - `RESTRICT`
  - `QUARANTINE`

### 3️⃣ Framework Eksperimental Terbuka
- Mudah direplikasi di lingkungan kampus
- Mendukung eksperimen terkontrol
- Cocok untuk skripsi, tesis, dan publikasi

### 4️⃣ Dokumentasi Akademik Terstruktur
- Arsitektur sistem
- Konsep trust & policy
- Roadmap penelitian
- Dataset & eksperimen

---

## 🏗️ Arsitektur Sistem (Ringkas)
  
[ IoT Device ]
│
▼
[ Trust Engine ] ──► [ Policy Engine ] ──► [ IoT Service / Backend ]
▲
│
[ Behavior & Context Observation ]

---


PALASIK berfungsi sebagai **security decision layer**  
di antara perangkat IoT dan layanan aplikasi.

---

## 🧪 Platform & Teknologi

### Hardware
- Raspberry Pi 3B / 3B+
- IoT Device / RFID Reader (contoh: Invengo XC-RF850)

### Software
- Python
- Node-RED (opsional sebagai control plane)
- MQTT / REST API

### Konsep Keamanan
- Zero Trust Architecture (ZTA)
- Edge Computing
- Policy-based Access Control
- Trust-aware System

---

## 📚 Dokumentasi Lengkap
Dokumentasi pengembangan tersedia di:

👉 **https://notedavidrinaldi.github.io/palasik/**

Struktur dokumentasi:
- Overview
- Architecture
- Trust Engine
- Policy Engine
- Installation
- Roadmap
- Contributors
- Citation

---

## 🧑‍🔬 Konteks Penelitian & Use Case
PALASIK ditujukan untuk riset di bidang:

- IoT Security
- Edge Computing
- Embedded Systems
- Industrial IoT (IIoT)

Potensi implementasi:
- Smart Campus
- Smart Port & Logistics
- Smart Healthcare
- Smart Agriculture
- Industrial Monitoring

---

## 🤝 Kontribusi & Kolaborasi (SANGAT DIHARAPKAN)
PALASIK adalah **open research framework**.

Kami mengundang kontribusi dari:
- 🎓 Mahasiswa (skripsi / tesis)
- 🧪 Peneliti
- 🧠 Praktisi IoT & Security

Contoh kontribusi yang dibutuhkan:
- Trust scoring model
- Policy rule design
- Dataset eksperimen
- Dokumentasi & studi kasus
- Evaluasi performa

📄 Panduan kontribusi:
👉 `CONTRIBUTING.md`

---

## ⚖️ Etika & Ruang Lingkup
PALASIK dirancang untuk:
- jaringan milik sendiri,
- laboratorium riset,
- lingkungan industri tertutup.

❌ **Tidak ditujukan untuk offensive security atau scanning ilegal.**

---

## 📄 Sitasi
Jika menggunakan PALASIK dalam publikasi ilmiah, silakan rujuk:

📑 `citation.md`

---

## 📜 Lisensi
Dirilis di bawah **MIT License**  
Bebas digunakan untuk riset dan pengembangan lanjutan.

---

## 👤 Maintainer & Peneliti Utama
**David Rinaldi**  
IoT Security & Edge Computing Researcher  
🔗 GitHub: https://github.com/notedavidrinaldi/palasik-iot-framework

---

## 🚀 Selanjutnya?
- 🔍 Lihat **Issues** untuk ide kontribusi
- ⭐ Star repo ini jika tertarik
- 🤝 Fork & eksperimen

---

### 🧠 Catatan
README ini disusun agar:
- layak dijadikan referensi akademik,
- mudah dipahami kontributor baru,
- dan siap mendukung publikasi ilmiah.

PALASIK bukan sekadar project,  
tetapi **platform riset terbuka** untuk keamanan IoT berbasis edge.

