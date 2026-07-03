# Paket Manual: Post 10 Issue Good First Issues

Gunakan ini kalau belum bisa pakai `gh` login.

## Cara Posting Cepat

1. Buka: https://github.com/notedavidrinaldi/palasik-iot-framework/issues/new/choose
2. Pilih `Docs Update` (atau `Bug report` jika sesuai)
3. Copy blok di bawah ini per issue
4. Tambahkan label: `good first issue`, `area:docs`

---

## ISSUE #1
**Title:** docs: perbaiki typo kecil dan konsistensi istilah PALASIK

**Body:**
```md
## Latar Belakang
Perbaiki typo kecil dan konsistensi istilah di README/docs.

## Scope
- [x] Dokumentasi
- [ ] Kode

## Yang dikerjakan
- Konsistenkan istilah: `policy`, `decision`, `trust`, `monitoring`.
- Perbaiki typo minor yang jelas.

## Acceptance Criteria
- Isi teknis tidak berubah.
- Dokumen tetap terbaca rapi.
```

---

## ISSUE #2
**Title:** docs: tambah contoh event simulate untuk sensor temperatur

**Body:**
```md
## Latar Belakang
Perlu contoh `event.json` untuk pemula saat simulasi.

## Scope
- [x] Dokumentasi
- [ ] Kode

## Yang dikerjakan
- Tambahkan file `samples/event_temperature.json`.
- Isi sample: `temp_c`, `device_id`, `topic`, `ts`.
- Tambahkan contoh command `palasik simulate <event.json>`.

## Acceptance Criteria
- JSON valid.
- Contoh simulasi dapat dijalankan.
```

---

## ISSUE #3
**Title:** docs: contoh hasil output status dalam format JSON

**Body:**
```md
## Latar Belakang
Pemula butuh contoh output `status`/`status --json` yang mudah dibaca.

## Scope
- [x] Dokumentasi
- [ ] Kode

## Yang dikerjakan
- Tambahkan contoh output `palasik status` (atau format yang tersedia).
- Jelaskan 3 indikator penting.

## Acceptance Criteria
- Pemula bisa menilai sehat/tidak sehat dari indikator.
```

---

## ISSUE #4
**Title:** docs: buat cheatsheet perintah operasi harian

**Body:**
```md
## Latar Belakang
Butuh satu halaman perintah harian untuk operator.

## Scope
- [x] Dokumentasi
- [ ] Kode

## Yang dikerjakan
- Tambahkan section Cheat Sheet (5+ command).
- Sertakan urutan minimal: `check`, `status`, `simulate`, `policy-snapshot`, `policy-deploy-check`.

## Acceptance Criteria
- Boleh langsung dicoba oleh pemula.
```

---

## ISSUE #5
**Title:** docs: tambah troubleshooting issue paling umum

**Body:**
```md
## Latar Belakang
Buat daftar isu umum agar pemula cepat pulih.

## Scope
- [x] Dokumentasi
- [ ] Kode

## Yang dikerjakan
- Tambahkan minimal 3 kasus: `check`/`run`/`simulate` gagal.
- Setiap kasus: gejala, kemungkinan penyebab, solusi cepat.

## Acceptance Criteria
- Resolusi issue dipercepat pada pertanyaan awal.
```

---

## ISSUE #6
**Title:** docs: tambah catatan praktis konfigurasi MQTT adapter

**Body:**
```md
## Latar Belakang
Butuh panduan ringkas setup adapter MQTT.

## Scope
- [x] Dokumentasi
- [ ] Kode

## Yang dikerjakan
- Tambahkan pengaturan host, port, topic wildcard.
- Tambahkan contoh `mosquitto_pub`.

## Acceptance Criteria
- Pemula bisa mencoba simulasi MQTT.
```

---

## ISSUE #7
**Title:** docs: tambahkan badge komunitas dan kontribusi

**Body:**
```md
## Latar Belakang
Perlu indikator keterlibatan komunitas lebih jelas.

## Scope
- [x] Dokumentasi
- [ ] Kode

## Yang dikerjakan
- Tambah badge repo/community yang valid di README utama.
- Jaga agar badge existing tetap ada.

## Acceptance Criteria
- Badge tampil dan link tidak rusak.
```

---

## ISSUE #8
**Title:** docs: rapikan checklist pertumbuhan komunitas

**Body:**
```md
## Latar Belakang
Checklist pertumbuhan perlu dieksekusi lebih mudah.

## Scope
- [x] Dokumentasi
- [ ] Kode

## Yang dikerjakan
- Rapikan urutan 30 hari dan target mingguan.
- Pastikan indikator ukur jelas (issue, PR, respons time).

## Acceptance Criteria
- Tim maintainer bisa checklist per minggu.
```

---

## ISSUE #9
**Title:** docs: tambah template ringkas untuk kontribusi dokumentasi

**Body:**
```md
## Latar Belakang
Pemula butuh format PR/docs yang seragam.

## Scope
- [x] Dokumentasi
- [ ] Kode

## Yang dikerjakan
- Tambahkan template issue/pull request mini untuk kontribusi docs.
- Sertakan contoh before/after singkat.

## Acceptance Criteria
- Kontributor baru lebih cepat submit PR.
```

---

## ISSUE #10
**Title:** docs: audit link rusak di dokumentasi

**Body:**
```md
## Latar Belakang
Link rusak mengganggu onboarding.

## Scope
- [x] Dokumentasi
- [ ] Kode

## Yang dikerjakan
- Cek README/docs utama.
- Perbaiki link internal/eksternal yang 404.

## Acceptance Criteria
- Minimal 5 link dicek dan valid.
```
