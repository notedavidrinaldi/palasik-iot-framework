# Paket: Siap Publish Komunitas

Gunakan halaman ini untuk menyiapkan snapshot final sebelum mempublikasikan paket komunitas PALASIK.

## 1) Persiapan cepat

- [ ] Checkout branch final (mis. `staging` atau `release/community`).
- [ ] `git status` bersih (hanya perubahan yang sudah direncanakan).
- [ ] `CONTRIBUTING.md` sudah memuat jalur paket pemula.
- [ ] `docs/README.md` sudah menautkan semua halaman komunitas yang relevan.

## 2) Validasi aset paket

- [ ] `docs/GOOD_FIRST_ISSUES.md` ada.
- [ ] `docs/GOOD_FIRST_ISSUES_BATCH.md` ada.
- [ ] `docs/CREATE_10_ISSUES_FAST.md` ada.
- [ ] `wiki-content/Good-First-Issues.md` ada.
- [ ] `wiki-content/Good-First-Issues-Batch.md` ada.
- [ ] `wiki-content/Issue-Batch-Cepat.md` ada.
- [ ] `scripts/setup-community-labels.sh` ada dan dapat dieksekusi (`bash -n`).
- [ ] `scripts/bootstrap-good-first-issues.sh` ada dan dapat dieksekusi (`bash -n`).

### Jalankan verifikasi

```bash
cd /Users/davidrinaldi/Documents/PROJECT-DAVID/palasik-iot-framework
bash -n scripts/setup-community-labels.sh
bash -n scripts/bootstrap-good-first-issues.sh
```

## 3) Validasi komunitas

- [ ] Tabel checklist komunitas diisi: [docs/CHECKLIST_COMMUNITY_BOOTSTRAP.md](CHECKLIST_COMMUNITY_BOOTSTRAP.md)
- [ ] Sidebar wiki memuat menu:
  - `Good First Issues`
  - `Issue Batch Cepat`
- [ ] Draft link diskusi/pengumuman sudah dipersiapkan.

## 4) Opsi publikasi issue

- [ ] Opsi manual siap: `docs/GOOD_FIRST_ISSUES_BATCH.md` (copy-paste per issue).
- [ ] Opsi otomatis siap: `scripts/bootstrap-good-first-issues.sh`.
- [ ] Jika pakai otomatis, setidaknya 10 issue target sudah terbuat dengan label `good first issue`.

## 5) Catatan release PR (wajib)

Sisipkan ke deskripsi PR sebelum merge:

- Ringkas keputusan paket (1 paragraf).
- Daftar file yang berubah.
- Bukti eksekusi verifikasi (jalankan command).
- Link dokumen publikasi: 
  - `docs/PUBLISH_PACKAGE_READINESS.md`
  - `docs/CHECKLIST_COMMUNITY_BOOTSTRAP.md`
  - `docs/COMMUNITY_PUBLISH_ANNOUNCEMENT.md`

## Template ringkas PR

```md
## Ringkasan release komunitas
- Paket: Good First Issues
- Tanggal publish: YYYY-MM-DD
- Label seed: `good first issue`, `area:docs`
- Jalur: manual/otomatis (tambahkan)

### Hasil verifikasi
- [ ] Script valid
- [ ] Checklist wiki/link valid
- [ ] Bootstrap checklist 10 issue terpenuhi
- [ ] Dokumentasi dan sidebar terhubung

### Bukti
- Screenshot: 
- Commit: 
```

Setelah 30 menit publikasi, lanjutkan isi ringkas di:
[docs/COMMUNITY_PUBLISH_POSTMORTEM.md](COMMUNITY_PUBLISH_POSTMORTEM.md)
