# Good First Issues (10)

Daftar tugas awal untuk kontributor baru. Semua item ini ringan, jelas, dan aman untuk PR pertama.

## Cara pakai
- Buat issue baru dengan judul, deskripsi, dan checklist sesuai item.
- Label: `good first issue`
- Jika item ini menyentuh dokumentasi: juga tambahkan `area:docs`

---

### 1) Perbaiki typo dan konsistensi istilah di README

**Judul:** `docs: perbaiki typo kecil dan konsistensi istilah PALASIK`

**Deskripsi:**
- Cari typo kecil di README/docs.
- Konsolidasikan istilah `policy`, `decision`, `trust`, `monitoring` agar konsisten.
- Pastikan tidak mengubah makna teknis.

**Acceptance Criteria:**
- Tidak ada typo mencolok.
- Isi teknis tetap sama.
- Lint dokumentasi (kalau ada) tetap lulus.

---

### 2) Tambahkan contoh `event.json` untuk simulasi temperatur

**Judul:** `docs: tambah contoh event simulate untuk sensor temperatur`

**Deskripsi:**
- Tambahkan file di `samples/event_temperature.json`.
- Isi nilai `temp_c`, `device_id`, `topic`, `ts`.
- Tambahkan contoh pemakaian di README atau docs/README.

**Acceptance Criteria:**
- File JSON valid.
- Command simulasi langsung jalan dengan contoh tersebut.

---

### 3) Tulis contoh penggunaan `status --json`

**Judul:** `docs: contoh hasil output status dalam format JSON`

**Deskripsi:**
- Tambahkan contoh output ringkas `palasik status --json` (atau command ekuivalen).
- Jelaskan 3 indikator penting yang perlu diperhatikan.

**Acceptance Criteria:**
- Contoh mudah dipahami pemula.
- Ada penjelasan cepat interpretasi metrik.

---

### 4) Buat cheat sheet perintah start PALASIK

**Judul:** `docs: buat cheatsheet perintah operasi harian`

**Deskripsi:**
- Tambahkan section `Cheat Sheet` di docs/README.md (atau file terkait).
- Isi command `check`, `status`, `simulate`, `policy-snapshot`, `policy-deploy-check`.

**Acceptance Criteria:**
- Ada urutan minimal 5 perintah.
- Cocok untuk operator non-teknis.

---

### 5) Tambahkan daftar error umum + solusi

**Judul:** `docs: tambah troubleshooting issue paling umum`

**Deskripsi:**
- Buat 5 issue umum saat `check`/`run`/`simulate` gagal.
- Sertakan gejala, penyebab, dan perbaikan cepat.

**Acceptance Criteria:**
- Minimal 3 entri troubleshooting + solusi.
- Format konsisten.

---

### 6) Tambah section dokumentasi adapter MQTT

**Judul:** `docs: tambah catatan praktis konfigurasi MQTT adapter`

**Deskripsi:**
- Tulis pengaturan dasar host, port, topic wildcard, dan contoh payload.
- Sertakan contoh `mqtt_pub` untuk publikasi event.

**Acceptance Criteria:**
- Contoh command bisa dicoba langsung.
- Aman untuk pemula.

---

### 7) Tambahkan badge status komunitas di README

**Judul:** `docs: tambahkan badge komunitas dan kontribusi`

**Deskripsi:**
- Tambahkan badge untuk repo stats/last commit/discussions jika tersedia.
- Jangan menghapus badge existing.

**Acceptance Criteria:**
- README menampilkan badge tambahan yang valid.

---

### 8) Koreksi metadata `docs/GROWTH.md`

**Judul:** `docs: rapikan checklist pertumbuhan komunitas`

**Deskripsi:**
- Update checklist 30 hari agar urutan jelas.
- Tambah target mingguan yang terukur (mis. PR, issue, discussion response time).

**Acceptance Criteria:**
- Checklist mudah dieksekusi oleh maintainer.
- Tidak ada kalimat ambigu.

---

### 9) Tambahkan contoh file kontribusi untuk docs

**Judul:** `docs: tambah template ringkas untuk kontribusi dokumentasi`

**Deskripsi:**
- Buat template markdown kecil agar kontributor baru tahu format update docs.
- Sisipkan di docs/README jika perlu.

**Acceptance Criteria:**
- Template siap copy-paste.
- Ada contoh `before/after` minimal.

---

### 10) Audit tautan eksternal yang rusak di docs/

**Judul:** `docs: audit link rusak di dokumentasi`

**Deskripsi:**
- Cek link di README/docs utama.
- Temukan dan perbaiki link 404 jika ada.

**Acceptance Criteria:**
- Minimal 5 link dicek.
- Daftar link rusak tertutup.

---

## Template posting issue (siap pakai)

```md
## Ringkas
<deskripsi singkat>

## Scope
- [ ] Dokumentasi
- [ ] Contoh
- [ ] Kecil

## Langkah cepat
1. Apa yang diubah
2. Mengapa
3. Cara verifikasi

## Target akhir
- [ ] PR kecil
- [ ] Tidak bergantung fitur besar
- [ ] Mudah direview
```

