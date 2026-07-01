# 🤝 Contributing to PALASIK

Terima kasih atas minat Anda untuk berkontribusi pada **PALASIK**  
(*Pengaman Layer Edge Sistem IoT Kritis*).

PALASIK adalah **open research framework**, sehingga kontribusi tidak hanya berupa kode,
tetapi juga ide riset, dokumentasi, eksperimen, dan evaluasi ilmiah.

---

## 🎯 Tujuan Kontribusi
Kontribusi diharapkan mendukung:
- Pengembangan **Trust-Aware IoT Security**
- Reproducible research
- Kolaborasi lintas kampus dan praktisi

---

## 🧩 Jenis Kontribusi yang Diterima

### 🧠 Kontribusi Riset
- Model trust scoring
- Policy decision strategy
- Anomaly detection (rule-based / ML)
- Evaluasi performa & latency

### 💻 Kontribusi Teknis
- Python module
- Node-RED integration
- Dataset processing
- Visualization & dashboard

### 📚 Kontribusi Dokumentasi
- Penulisan artikel teknis
- Studi kasus
- Tutorial instalasi
- Paper draft (IEEE / SINTA)

---

## 🛠️ Cara Berkontribusi
1. Fork repository ini
2. Buat branch baru:
   ```bash
   git checkout -b feature/nama-kontribusi
   ```
4. Commit dengan pesan jelas:
   ```bash
   git commit -m "Add trust scoring experiment"
  ```

## ✅ Migration Gate (untuk PR ke `staging`)

Sebelum membuka PR ke branch `staging`, pastikan command ini lulus:

```bash
make migration-check
```

`make migration-check` menjalankan:

- `python3 scripts/check_legacy_imports.py` (harus tampil `0 issues`)
- `make test-strict` (`PALASIK_STRICT_DEPRECATION=1`, deprecation menjadi error)

PR ke `staging` sebaiknya tidak diteruskan bila:
- ada legacy import ke `palasik.core.trust_engine` / `palasik.core.policy_engine`
- atau strict test gagal karena warning deprecation

Untuk memastikan aturan branch protection juga aktif:

```bash
bash scripts/check_staging_gate.sh --branch=staging
```

Referensi: [docs/MIGRATION_GATE.md](docs/MIGRATION_GATE.md)

Saat membuat PR, isi template PR (termasuk checklist migration check) agar review bisa
langsung mengecek kesiapan migrasi.

---

## 🧪 Standar Penelitian
Kontribusi riset sebaiknya menyertakan:

- Tujuan eksperimen

- Metodologi

- Parameter

- Hasil & diskusi
---

## ⚖️ Etika & Legal
PALASIK bukan alat hacking.

Kontribusi tidak boleh:

- melakukan intrusive scanning

- melanggar privasi

- menyerang jaringan publik
---

## 📧 Kontak

Maintainer:
David Rinaldi
GitHub: https://github.com/notedavidrinaldi

Kami menantikan kolaborasi Anda 🚀

---

# 2️⃣ GitHub Issue Templates (Agar Ramai & Terarah)

### 📄 `.github/ISSUE_TEMPLATE/feature_request.md`

```md
---
name: Feature Request
about: Usulan fitur / ide riset baru
title: "[FEATURE] "
labels: enhancement
---

## 📌 Deskripsi Singkat
Jelaskan fitur atau ide riset yang diusulkan.

## 🎯 Tujuan
Masalah apa yang ingin diselesaikan?

## 🧠 Konteks Riset
Apakah relevan untuk:
- Trust Engine
- Policy Engine
- Dataset
- Edge Security

## 🔬 Referensi (Opsional)
Paper / standar / studi terkait.







