# 🧿 PALASIK  
**Policy-Aware Zero Trust Event Enforcement Framework for IoT & Edge**

[![PyPI](https://img.shields.io/pypi/v/palasik.svg)](https://pypi.org/project/palasik/)
[![Python](https://img.shields.io/pypi/pyversions/palasik.svg)](https://pypi.org/project/palasik/)
[![License](https://img.shields.io/github/license/notedavidrinaldi/palasik-iot-framework)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-green)]()

---

## 🔐 What is PALASIK?

**PALASIK** (Policy-Aware Lightweight Adaptive Security for IoT) adalah **framework Python berbasis Zero Trust**
yang berfungsi sebagai **security enforcement layer** di **edge / gateway IoT**.

PALASIK **tidak pernah menganggap event atau device itu tepercaya secara default**.  
Setiap event **HARUS**:
1. Dievaluasi tingkat kepercayaannya (**Trust Engine**)
2. Diputuskan secara eksplisit (**Policy Engine**)
3. Baru diteruskan atau diblok (**Enforcement Point**)

Framework ini dirancang **ringan, modular, dan extensible**.

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
IoT Security & Edge Computing
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
