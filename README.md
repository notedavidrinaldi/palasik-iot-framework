# DEMIT + PALASIK
**DEMIT Super App for Digital Monitoring, with PALASIK as the Zero Trust IoT security application**

[![PyPI](https://img.shields.io/pypi/v/palasik.svg)](https://pypi.org/project/palasik/)
[![Python](https://img.shields.io/pypi/pyversions/palasik.svg)](https://pypi.org/project/palasik/)
[![License](https://img.shields.io/github/license/notedavidrinaldi/palasik-iot-framework)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-green)]()

---

## 🔷 What is DEMIT?

**DEMIT** adalah kerangka **super app** yang dirancang untuk menampung beberapa aplikasi digital
dalam satu runtime terpadu.

Di dalam roadmap DEMIT:

- **PALASIK** menjadi **App 1**
- fokus PALASIK adalah **keamanan IoT berbasis Zero Trust**
- aplikasi lain nantinya bisa ditambahkan tanpa merusak core PALASIK

Struktur pikirnya:

1. DEMIT = ekosistem / super-app runtime
2. PALASIK = aplikasi keamanan IoT di dalam DEMIT
3. aplikasi lain = modul lanjutan yang berbagi orchestration yang sama

Detail runtime DEMIT:
[`docs/DEMIT.md`](docs/DEMIT.md)

---

## 🔐 What is PALASIK?

**PALASIK** (Policy-Aware Lightweight Adaptive Security for IoT) adalah **framework Python berbasis Zero Trust**
yang berfungsi sebagai **security enforcement layer** di **edge / gateway IoT**.

PALASIK **tidak pernah menganggap event atau device itu tepercaya secara default**.
Setiap event **HARUS**:
1. Dievaluasi tingkat kepercayaannya (**Trust Engine**)
2. Diputuskan secara eksplisit (**Policy Engine**)
3. Baru diteruskan atau diblok (**Enforcement Point**)

Ide utamanya adalah:

- perangkat IoT tidak boleh langsung dipercaya
- event tidak boleh langsung lewat
- sistem harus belajar pola, mengevaluasi trust, dan memastikan tidak ada upaya
  pengambilan data paksa atau penyalahgunaan jalur komunikasi IoT

Framework ini dirancang **ringan, modular, extensible, dan research-ready**.

---

## 🎯 Use Case Utama

PALASIK cocok digunakan untuk:

- IoT Gateway & Edge Computing
- Security-aware event pipeline
- Zero Trust IoT experimentation
- Research & academic prototype
- Lightweight industrial IoT security layer

---

## ✨ Core Capabilities

- 🔍 **Trust Evaluation Engine**  
  Menilai event secara dinamis (behavior & context aware)

- 🔐 **Policy Enforcement (ALLOW / DENY)**  
  Enforcement point eksplisit (bukan implicit filtering)

- 🧩 **Plugin-based Architecture**  
  Logging, forwarding, alerting, extensible

- 🌐 **Adapters**  
  MQTT, HTTP, Webhook (extensible)

- ⚙️ **YAML / ENV Configuration**

- 📦 **Installable via PyPI**

---

## 📦 Installation

```bash
pip install palasik
```
Python >= 3.10 direkomendasikan.

Untuk runtime DEMIT, package yang sama juga menyediakan command:

```bash
demit --config demit.yaml
```

---

## 🚀 Quick Start

### 1️⃣ Initialize Project

```bash
palasik init
```

Perintah ini akan membuat:

1. config.yaml

2. struktur dasar runtime PALASIK
---
### 2️⃣ Run PALASIK Agent

```bash
palasik run
```

PALASIK akan:

1. load konfigurasi

2. start agent

3. menunggu event dari adapter
---
### 3️⃣ Example: MQTT Event

```bash
mosquitto_pub -t palasik/sensor/temp -m '{"value": 42}'
```
Alur yang terjadi:

1. Event masuk via adapter

2. Trust dievaluasi

3. Policy diputuskan

4. ALLOW → diteruskan

5. DENY → diblok

---

## 🚀 Run As DEMIT Super App

Contoh `demit.yaml` bawaan:

```yaml
demit:
  apps:
    - palasik

apps:
  palasik:
    type: palasik
    config_file: "config.yaml"
    plugins_path: "plugins"
    routes:
      - palasik
```

Jalankan:

```bash
demit --config demit.yaml
```

Dengan ini, PALASIK berjalan sebagai aplikasi pertama di dalam runtime DEMIT.
---
## 🧠 How It Works (High Level)
```planttext
Event → Trust Engine → Policy Engine → Enforcement
                         │
                         ├─ ALLOW → Plugin / Adapter
                         └─ DENY  → Blocked
```

PALASIK adalah decision layer, bukan sekadar message router.
---
## 🗂 Project Structure
```plaintext
demit/
├── core/        # Super-app runtime, app contract, router
├── apps/        # App modules inside DEMIT
└── cli/         # demit CLI

palasik/
├── core/        # Agent, engine, context
├── trust/       # Trust evaluators
├── policy/      # Policy engines
├── adapters/    # MQTT, HTTP, Webhook
├── plugins/     # Extensible actions
├── cli/         # palasik CLI
└── config/      # Config loader
```
---
## ⚙️ Configuration

PALASIK menggunakan konfigurasi YAML + Environment Variable.

Contoh config.yaml

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
Prioritas konfigurasi:

1. Environment Variable

2. YAML

3. Default code

Detail lengkap:
👉 docs/CONFIG.md

---
## 🧪 Testing

```bash
pytest
```

Semua komponen inti memiliki unit test.
---
## 📚 Documentation

| Topik         | File                        |
| ------------- | --------------------------- |
| Architecture  | `docs/ARCHITECTURE.md`      |
| DEMIT         | `docs/DEMIT.md`             |
| Configuration | `docs/CONFIG.md`            |
| Trust Engine  | `docs/raw/trust-engine.md`  |
| Policy Engine | `docs/raw/policy-engine.md` |
| Research Docs | `docs/raw/`                 |

---
## 🎓 Research Context (Academic Track)
PALASIK berasal dari riset keamanan IoT berbasis Edge & Zero Trust
dan tetap mempertahankan jalur akademik.

Jika kamu tertarik pada:

1. skripsi / tesis

2. paper / jurnal

3. eksperimen trust & policy

👉 lihat folder docs/raw/
---

## 🤝 Contributing
Kontribusi sangat diterima, terutama:

trust model baru

policy logic

adapter tambahan

benchmark & dataset

dokumentasi & studi kasus

Panduan:
👉 CONTRIBUTING.md

---

## 📄 Citation

Jika menggunakan PALASIK dalam publikasi ilmiah, silakan sertakan sitasi:

👉 citation.md

---

## 📜 License

MIT License
Bebas digunakan untuk riset dan pengembangan lanjutan.
---

## 👤 Maintainer

David Rinaldi
🔗 https://github.com/notedavidrinaldi

---

## 🚦 Project Status

✅ Core stable (v0.1.0)

📦 Published on PyPI

🧪 Tested

📘 Research-ready

🔄 Actively improved

---

## 🧠 Final Note
PALASIK bukan sekadar project contoh.
Ini adalah framework keputusan keamanan yang bisa berkembang ke:

- Industrial IoT

- Smart Infrastructure

- Security research platform

Jika kamu ingin:

- memakai → install & run

- mengembangkan → plugin & adapter

- meneliti → trust & policy

PALASIK sudah siap.

⭐ Star repo ini jika relevan.
🤝 Fork jika ingin eksperimen.
---
