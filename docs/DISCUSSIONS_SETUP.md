# Aktifkan Diskusi Komunitas (GitHub Discussions)

Tujuan: membuat jalur pertanyaan, ide fitur, dan showcase use-case agar kontribusi makin banyak.

## Opsi 1: Aktifkan lewat GitHub UI (paling cepat)

1. Buka repositori: https://github.com/notedavidrinaldi/palasik-iot-framework/settings
2. Pilih tab **General** atau **Features** (tergantung layout GitHub).
3. Cari bagian **Features**.
4. Centang **Discussions**.
5. Simpan perubahan.

## Opsi 2: Aktifkan via GitHub API/CLI (otomatis)

Gunakan token dengan scope `repo`.

```bash
export GH_TOKEN=<YOUR_TOKEN>
gh auth status

gh api \
  -X PATCH \
  -H "Accept: application/vnd.github+json" \
  /repos/notedavidrinaldi/palasik-iot-framework \
  -f has_discussions=true
```

## Buat 3 kategori awal

Buat dulu 3 kategori ini agar diskusi tidak terlalu kacau:

- `General`
- `Q&A`
- `Ideas`

Cara cepat (UI):

1. Buka https://github.com/notedavidrinaldi/palasik-iot-framework/discussions/categories
2. Klik **New category**
3. Isi nama + deskripsi + format (Announcements/General/Ideas/Q&A)

## Template topik pertama (siapkan dulu, lalu paste)

- **[Q&A]** "Cara cepat menjalankan PALASIK demo?"
- **[Show and tell]** "Use case: IoT suhu + policy deny by default"
- **[Ideas]** "Usulan plugin audit event"

## Link cepat yang dipakai kontribusi

- Diskusi: https://github.com/notedavidrinaldi/palasik-iot-framework/discussions
- Buat issue: https://github.com/notedavidrinaldi/palasik-iot-framework/issues/new/choose

## Checklist setelah aktif

- [ ] Discussions sudah visible di tab repo
- [ ] 3 kategori aktif
- [ ] Pin satu topik pengenalan
- [ ] Pin satu topik kontribusi pertama
