# DEMIT + PALASIK
**DEMIT Super App for Digital Monitoring, with PALASIK as the Zero Trust IoT security application**

[![PyPI](https://img.shields.io/pypi/v/palasik.svg)](https://pypi.org/project/palasik/)
[![Python](https://img.shields.io/pypi/pyversions/palasik.svg)](https://pypi.org/project/palasik/)
[![CI-Staging](https://github.com/notedavidrinaldi/palasik-iot-framework/actions/workflows/ci-staging.yml/badge.svg)](https://github.com/notedavidrinaldi/palasik-iot-framework/actions/workflows/ci-staging.yml)
[![License](https://img.shields.io/github/license/notedavidrinaldi/palasik-iot-framework)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-green)]()

PALASIK adalah framework Python untuk **Zero Trust IoT event enforcement** di **edge/gateway**.
Repo ini cocok untuk orang yang ingin:

- mencoba pipeline keputusan `trust -> policy -> action` dalam hitungan menit
- membangun gateway IoT yang lebih aman di Raspberry Pi, MQTT, atau HTTP event flow
- berkontribusi pada framework riset yang terbuka untuk docs, test, plugin, dan eksperimen

## Start Here

- Quickstart: [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
- Arsitektur: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Runbook operasional: [docs/OPERATIONAL_RUNBOOK.md](docs/OPERATIONAL_RUNBOOK.md)
- Deploy edge: [docs/EDGE_DEPLOYMENT.md](docs/EDGE_DEPLOYMENT.md)
- Cara kontribusi: [CONTRIBUTING.md](CONTRIBUTING.md)
- Good first issues: [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md)
- Diskusi komunitas: https://github.com/notedavidrinaldi/palasik-iot-framework/discussions

## Kenapa layak di-fork?

- **Research-ready**: cocok untuk eksperimen trust scoring, policy engine, dan IoT security workflow.
- **Practical ops**: sudah punya health contract, deploy gate, rollback, dan post-restart check.
- **Contribution-friendly**: kontribusi docs, sample config, plugin, test, dan use case sama berharganya dengan perubahan core.

## Quick Demo (60 detik)

```bash
pip install palasik
palasik init
palasik check --config config.yaml
palasik simulate docs/samples/policy-smoke-events.json --config config.yaml
palasik status --config config.yaml
```

Jika Anda ingin kontribusi pertama yang aman, mulai dari:

1. [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md)
2. [CONTRIBUTING.md](CONTRIBUTING.md)
3. issue berlabel `good first issue` atau `help wanted`

**Catatan migrasi:** badge `CI-Staging` menunjukkan jalur migrasi ketat. Pipeline akan fail jika terdapat legacy deprecation warning untuk `palasik.core.trust_engine` atau `palasik.core.policy_engine`.

**Cek cepat untuk menghapus `ci-staging.yml`:** hilangkan workflow ini bila semua kondisi berikut terpenuhi:

1. Legacy import scan = `0 issues`.
2. `make migration-check` berjalan clean (termasuk strict deprecation test).

Cek cepat otomatis tersedia via:

```bash
python3 scripts/check_legacy_imports.py
make migration-check
```

Untuk menjadikan ini gate yang benar-benar mandatory pada branch `staging`, aktifkan check `migration-gate` sebagai required status check di branch protection.
Untuk verifikasi cepat apakah sudah wajib, gunakan script audit:

```bash
bash scripts/check_staging_gate.sh --branch=staging
```

Untuk meng-enable dan melihat payload update branch protection (dan bisa dicoba dulu tanpa auth via `--dry-run`):

```bash
bash scripts/apply_staging_branch_protection.sh --dry-run
bash scripts/apply_staging_branch_protection.sh --branch=staging
```

Dokumen lengkap: [docs/MIGRATION_GATE.md](docs/MIGRATION_GATE.md)
Konfigurasi operasional: [docs/CONFIG.md](docs/CONFIG.md)
Runbook operasional: [docs/OPERATIONAL_RUNBOOK.md](docs/OPERATIONAL_RUNBOOK.md)
Draft deploy edge: [docs/EDGE_DEPLOYMENT.md](docs/EDGE_DEPLOYMENT.md)

Shortcut operasional yang paling sering dipakai:

```bash
make edge-health
make edge-health-wait
make edge-health-strict
make edge-post-restart-check
make edge-post-restart-check-strict
```

Ringkasannya:

- `edge-health`: cek health cepat
- `edge-health-wait`: cek health dengan retry lebih panjang
- `edge-health-strict`: hanya lolos jika status `UP`
- `edge-post-restart-check`: `check-startup` lalu tunggu health
- `edge-post-restart-check-strict`: versi gate ketat pasca-restart

---

## 🔷 Apa Itu DEMIT?

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

## 🔐 Apa Itu PALASIK?

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

## 📦 Instalasi

```bash
pip install palasik
```
Python >= 3.10 direkomendasikan.

Untuk runtime DEMIT, package yang sama juga menyediakan command:

```bash
demit --config demit.yaml
```

---

## 🚀 Mulai Cepat

### 1️⃣ Inisialisasi Proyek

```bash
palasik init
```

Perintah ini akan membuat:

1. config.yaml

2. struktur dasar runtime PALASIK

### 1b) Cek Health

```bash
palasik check
```

Menguji startup pipeline trust/policy dan plugin.

### 1c) Simulasi event

```bash
palasik simulate <event.json>
```

Preview keputusan (ALLOW/DENY + alasan) tanpa menyalakan runtime penuh.

### 1d) Gate deploy (opsional)

```bash
palasik policy-snapshot --config config.yaml
palasik policy-deploy-check --config config.yaml --require-allow
```

Rollback cepat jika perlu:

```bash
palasik policy-rollback --config config.yaml --snapshot runs/policy_snapshots/<snapshot>
```

### 1e) Shortcut health operasional

```bash
make edge-health
make edge-post-restart-check
```

### 2️⃣ Jalankan Agent PALASIK

```bash
palasik run
```

PALASIK akan:

1. load konfigurasi

2. start agent

3. menunggu event dari adapter
---
### 3️⃣ Contoh Event MQTT

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

## ✅ Jalur Aktif (Migration Note)

Untuk konsistensi implementasi saat ini, gunakan jalur aktif berikut:

- Trust: `palasik.trust` (`SimpleTrustEvaluator` atau custom evaluator)
- Policy: `palasik.policy` (`AllowDenyPolicy`, `RuleBasedPolicy`, atau custom policy)

Import dari `palasik.core.trust_engine` dan `palasik.core.policy_engine` tetap didukung
untuk kompatibilitas, dan akan diperlakukan sebagai deprecation path pada fase migrasi
berikutnya.

Untuk enforce perilaku fase berikutnya secara lokal, bisa diaktifkan lewat:
`PALASIK_STRICT_DEPRECATION=1`.
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
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m pytest -q
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

Mulai cepat:
- Buat PR pertama dengan scope kecil (dokumen, contoh, atau test).
- Ikuti alur di 👉 CONTRIBUTING.md
- Lihat label `good first issue` untuk kontribusi paling ramah pemula.

Panduan:
👉 CONTRIBUTING.md

🧩 Untuk strategi pertumbuhan komunitas:
👉 docs/GROWTH.md

🚀 Mulai hari ini:
- Star repo
- Buka 1 issue kecil yang jelas
- Kirim 1 PR percobaan (dokumen atau test)

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

✅ Core stable (v0.2.0)

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
