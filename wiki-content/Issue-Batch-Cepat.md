# Fast Track 10 Issue Good-First

## Opsi A: Manual (tanpa CLI)
1. Buka halaman: https://github.com/notedavidrinaldi/palasik-iot-framework/issues/new/choose
2. Untuk setiap issue, copy dari [GOOD_FIRST_ISSUES_BATCH.md](https://github.com/notedavidrinaldi/palasik-iot-framework/blob/main/docs/GOOD_FIRST_ISSUES_BATCH.md)
3. Tambahkan label:
   - `good first issue`
   - `area:docs`
4. Klik `Submit new issue`

## Opsi B: Otomatis (CLI)
Jika Anda sudah `gh auth login`:

```bash
cd /Users/davidrinaldi/Documents/PROJECT-DAVID/palasik-iot-framework
./scripts/setup-community-labels.sh
./scripts/bootstrap-good-first-issues.sh
```

## Opsi C: Setiap issue langsung diprioritaskan
- Label `good first issue` untuk pemula
- Label `help wanted` untuk yang butuh bantuan
- Beri milestone: `Community Onboarding` (jika Anda punya milestone ini, lalu tambah secara bertahap)
