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
3. Lakukan perubahan.
4. Commit dengan pesan jelas:
   ```bash
   git commit -m "Add trust scoring experiment"
   ```
5. Push branch dan buat PR.

## 🚀 Mulai Kontribusi dalam 10 Menit
1. Buka issue berlabel `good first issue`.
2. Pilih tugas dengan perubahan kecil (docs, test, helper function).
3. Fork repo.
4. Jalankan test cepat:
   ```bash
   python -m pytest -q
   ```
5. Kirim PR dan cantumkan hasil test di deskripsi.

## ✅ Migration Gate (untuk PR ke `staging`)

Sebelum membuka PR ke branch `staging`, pastikan command ini lulus:

```bash
make migration-check
```

`make migration-check` menjalankan:

- `python3 scripts/check_legacy_imports.py` (harus tampil `0 issues`)
- `make test-strict` (`PALASIK_STRICT_DEPRECATION=1`, deprecation menjadi error)
- `make migration-check` (termasuk `validate-policy` lint untuk config dan policy sampel)
- `make policy-deploy-check` (smoke deploy check untuk meminimalkan outage)

Jalankan juga `policy-deploy-check` sebelum rollout operasional:

```bash
python3 -m palasik.cli.main policy-snapshot --config config.yaml
python3 -m palasik.cli.main policy-deploy-check --config config.yaml --require-allow
```

PR ke `staging` sebaiknya tidak diteruskan bila:
- ada legacy import ke `palasik.core.trust_engine` / `palasik.core.policy_engine`
- atau strict test gagal karena warning deprecation

Untuk memastikan aturan branch protection juga aktif:

```bash
bash scripts/check_staging_gate.sh --branch=staging
```

Referensi: [docs/MIGRATION_GATE.md](docs/MIGRATION_GATE.md)

Saat membuat PR, isi checklist PR agar review bisa langsung mengecek kesiapan migrasi.

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

## 💬 Dapatkan bantuan
- Buka issue dengan label `question` untuk pertanyaan operasional.
- Bahas desain besar melalui Discussion.

## 📚 Rujukan komunitas
- Strategi pertumbuhan: [docs/GROWTH.md](docs/GROWTH.md)
- Label kontribusi: [docs/LABELS_COMMUNITY.md](docs/LABELS_COMMUNITY.md)
- Checklist aktivasi komunitas: [docs/CHECKLIST_COMMUNITY_BOOTSTRAP.md](docs/CHECKLIST_COMMUNITY_BOOTSTRAP.md)
- Paket presentasi GitHub: [docs/GITHUB_REPO_PRESENTATION.md](docs/GITHUB_REPO_PRESENTATION.md)

## 🏷️ Label Wajib

- `good first issue` untuk tugas yang ringan (pemula).
- `help wanted` untuk issue yang butuh bantuan komunitas.
- `question` untuk pertanyaan setup/operasional.
- `area:docs`, `area:plugin`, `area:policy`, `discussion-needed` untuk klasifikasi area.

Untuk pengaturan label otomatis jalankan:

```bash
./scripts/setup-community-labels.sh
```

## 📧 Kontak

Maintainer:
David Rinaldi
GitHub: https://github.com/notedavidrinaldi

Kami menantikan kolaborasi Anda 🚀

## 💬 Diskusi Komunitas
Untuk pertanyaan awal dan ide pengembangan, gunakan
GitHub Discussions: https://github.com/notedavidrinaldi/palasik-iot-framework/discussions

Panduan aktifasi untuk maintainer: [docs/DISCUSSIONS_SETUP.md](docs/DISCUSSIONS_SETUP.md)

## 🧭 Paket tugas pemula
Untuk mulai langsung, lihat
- [Good First Issues](docs/GOOD_FIRST_ISSUES.md)
- [Wiki Good First Issues](wiki-content/Good-First-Issues.md)
- Tandai issue dengan `good first issue`.

## 🔧 Bootstrap tugas pemula (otomatis)
Jika sudah login gh, Anda bisa membuat 10 issue dari file template secara otomatis:

```bash
./scripts/bootstrap-good-first-issues.sh
```

Untuk validasi publikasi paket komunitas, lihat checklist:
[docs/CHECKLIST_COMMUNITY_BOOTSTRAP.md](docs/CHECKLIST_COMMUNITY_BOOTSTRAP.md) bagian
“Checklist Siap Publish Good First Issues”.

## ⚡ Cara mulai kontribusi cepat
- 10 issue pemula: [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md)
- Paket copy-paste issue: [docs/GOOD_FIRST_ISSUES_BATCH.md](docs/GOOD_FIRST_ISSUES_BATCH.md)
- Tutorial posting cepat: [docs/CREATE_10_ISSUES_FAST.md](docs/CREATE_10_ISSUES_FAST.md)
- Checklist siap publish paket komunitas: [docs/PUBLISH_PACKAGE_READINESS.md](docs/PUBLISH_PACKAGE_READINESS.md)
- Template announcement publikasi komunitas: [docs/COMMUNITY_PUBLISH_ANNOUNCEMENT.md](docs/COMMUNITY_PUBLISH_ANNOUNCEMENT.md)
