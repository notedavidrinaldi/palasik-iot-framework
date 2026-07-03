# GitHub Repo Presentation Pack

Paket ini disiapkan agar halaman GitHub PALASIK lebih mudah ditemukan, lebih cepat dipahami, dan lebih mendorong orang untuk fork lalu berkontribusi.

## 1. Repo description

Pilih salah satu yang paling cocok untuk kolom description repo.

### Opsi A

`Zero Trust IoT security framework for edge gateways with trust scoring, policy enforcement, health contracts, and contributor-friendly docs.`

### Opsi B

`Python framework for Zero Trust IoT event enforcement on edge gateways, with DEMIT runtime, deploy gates, rollback, and community-friendly docs.`

### Opsi C

`Research-ready Zero Trust IoT framework for Raspberry Pi, MQTT, and edge event pipelines with practical operations and open contribution paths.`

## 2. Website

Isi kolom website repo dengan:

`https://notedavidrinaldi.github.io/palasik/`

## 3. Topics

Gunakan 10-15 topic yang paling relevan. Rekomendasi utama:

- `iot`
- `iot-security`
- `zero-trust`
- `edge-computing`
- `raspberry-pi`
- `mqtt`
- `industrial-iot`
- `python`
- `event-driven`
- `gateway`
- `iot-gateway`
- `policy-engine`
- `trust-engine`
- `cybersecurity`
- `research`

Jika ingin lebih ringkas, pakai 10 topic pertama saja.

## 4. Pinned issue

Buat issue baru lalu pin di bagian atas repo.

### Judul

`[START HERE] New contributors: where to begin with PALASIK`

### Isi

```md
## Welcome

Terima kasih sudah mampir ke PALASIK.

PALASIK adalah framework Zero Trust untuk event IoT di edge/gateway. Jika Anda ingin fork repo ini dan mulai kontribusi, thread ini adalah titik masuk terbaik.

## Contribution paths

Anda tidak harus mulai dari core engine. Kontribusi yang sangat membantu:

- docs dan tutorial
- test dan validasi command
- sample config dan example event
- plugin sederhana
- issue triage dan reproduksi bug

## Start in 15 minutes

1. Baca [README](../README.md)
2. Baca [CONTRIBUTING.md](../CONTRIBUTING.md)
3. Lihat [docs/GOOD_FIRST_ISSUES.md](../docs/GOOD_FIRST_ISSUES.md)
4. Ambil issue berlabel `good first issue` atau `help wanted`

## Quick setup

```bash
pip install palasik
palasik init
palasik check --config config.yaml
palasik status --config config.yaml
```

## Good first contribution ideas

- perbaiki docs yang kurang jelas
- tambah contoh event JSON
- tambah test kecil untuk command atau policy
- perbaiki wording atau troubleshooting guide

## If you are unsure

Balas issue ini atau buka Discussion baru dengan format:

- latar belakang Anda
- area yang ingin dibantu
- apakah ingin kontribusi docs, test, plugin, atau riset

Kami akan bantu arahkan ke tugas pertama yang aman.
```

## 5. Pinned discussion

Jika Discussions aktif, buat 1 pinned discussion untuk membuat repo terasa hidup.

### Judul

`Welcome to PALASIK: introduce yourself, your use case, and how you want to contribute`

### Kategori

`General` atau `Ideas`

### Isi

```md
# Welcome to PALASIK

Jika Anda baru datang ke repo ini, silakan perkenalkan diri di thread ini.

Kami ingin tahu:

1. Anda datang dari latar belakang apa?
2. Tertarik ke area mana: docs, testing, plugin, use case, atau core engine?
3. Use case apa yang paling ingin Anda bangun dengan PALASIK?

## What PALASIK is

PALASIK adalah framework Zero Trust IoT untuk edge/gateway yang memproses event melalui trust scoring, policy decision, dan action enforcement.

## Best places to start

- README
- CONTRIBUTING.md
- docs/GETTING_STARTED.md
- docs/GOOD_FIRST_ISSUES.md

## If you want a safe first task

Tulis komentar dengan format:

- `I want to help with docs`
- `I want to help with tests`
- `I want to help with examples`
- `I want to help with plugins`

Nanti maintainer bisa arahkan Anda ke issue pertama yang paling cocok.
```

## 6. Suggested repository tagline for social posts

Gunakan versi pendek ini saat posting ke LinkedIn, X, forum, atau grup komunitas:

`PALASIK is a Zero Trust IoT framework for edge gateways: trust scoring, policy enforcement, rollback-aware operations, and open contribution paths for docs, tests, plugins, and research.`

## 7. Suggested first pinned labels

Pastikan label ini terlihat aktif di issue list:

- `good first issue`
- `help wanted`
- `documentation`
- `bug`
- `enhancement`
- `question`
- `area:docs`
- `area:policy`
- `area:plugin`
- `discussion-needed`

## 8. Suggested maintainer response template

Gunakan balasan singkat ini saat orang baru membuka issue atau discussion:

```md
Terima kasih sudah tertarik ke PALASIK.

Kalau Anda ingin mulai dari kontribusi yang aman, saya sarankan lihat:

- `CONTRIBUTING.md`
- `docs/GOOD_FIRST_ISSUES.md`
- label `good first issue`

Kalau mau, balas dengan minat Anda:
- docs
- tests
- examples
- plugin
- core engine

Nanti saya bantu arahkan ke tugas pertama yang paling cocok.
```
