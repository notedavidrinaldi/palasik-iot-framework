# Checklist Bootstrap Komunitas PALASIK

Gunakan ini setiap awal sprint komunitas:

- [ ] Aktifkan Discussions
- [ ] Jalankan seeding label (`./scripts/setup-community-labels.sh`)
- [ ] Buat 3 thread awal (Announcements, Q&A, Ideas)
- [ ] Pin pinned bulletin
- [ ] Tandai 1 issue sebagai `good first issue`
- [ ] Tandai 1 issue sebagai `help wanted`
- [ ] Tambah 1 label `area:plugin` dan 1 `area:policy` pada issue yang sesuai
- [ ] Review kontribusi masuk dan responkan maksimal 24 jam pertama

## Template hasil update di README (wajib)

1. Tambahkan link ke label di CONTRIBUTING
2. Update docs/GROWTH dengan jumlah PR/issue minggu ini
3. Dokumentasikan hasil thread diskusi mingguan

---

## Checklist Siap Publish Good First Issues

Sebelum paket komunitas dinyatakan siap dipublikasikan ke repo, jalankan urutan ini:

- [ ] Pastikan halaman ini sudah link-nya benar:
  - [GOOD_FIRST_ISSUES.md](GOOD_FIRST_ISSUES.md)
  - [GOOD_FIRST_ISSUES_BATCH.md](GOOD_FIRST_ISSUES_BATCH.md)
  - [CREATE_10_ISSUES_FAST.md](CREATE_10_ISSUES_FAST.md)
  - [Good-First-Issues.md](../wiki-content/Good-First-Issues.md)
  - [Good-First-Issues-Batch.md](../wiki-content/Good-First-Issues-Batch.md)
  - [Issue-Batch-Cepat.md](../wiki-content/Issue-Batch-Cepat.md)
- [ ] Jalankan script label:
  - `bash ./scripts/setup-community-labels.sh`
- [ ] Jalankan bootstrap issue bila ingin langsung publikasi issue:
  - `./scripts/bootstrap-good-first-issues.sh`
- [ ] Verifikasi 10 issue target muncul di GitHub (atau siap copy-paste untuk posting manual).
- [ ] Cek sidebar wiki: `wiki-content/_Sidebar.md` memuat:
  - `Good First Issues`
  - `Issue Batch Cepat`
- [ ] Review template issue batch agar siap tempel:
  - `docs/GOOD_FIRST_ISSUES_BATCH.md`
  - `wiki-content/Good-First-Issues-Batch.md`
- [ ] Pastikan `CONTRIBUTING.md` menyebut jalur cepat kontribusi pemula.
- [ ] Simpan bukti publish (screenshot halaman wiki / commit summary).
- [ ] Isi post-mortem 30 menit: [Community Publish Postmortem](COMMUNITY_PUBLISH_POSTMORTEM.md).
- [ ] Siapkan dan posting announcement paket: [COMMUNITY_PUBLISH_ANNOUNCEMENT.md](../docs/COMMUNITY_PUBLISH_ANNOUNCEMENT.md).

## Template “siap publish” singkat (opsional)

```md
## Hasil Sprint Community Bootstrap
- Hari peluncuran: YYYY-MM-DD
- Label dibuat: ya / tidak
- 10 issue siap: ya / tidak
- Diskusi aktif: ya / tidak
- README/docs terupdate: ya / tidak
- Penerima issue pertama: ya / tidak

Keputusan: Publish komunitas dinyatakan ... (SELESAI / TUNGGU)
```
