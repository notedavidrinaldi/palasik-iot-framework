# Migration Gate Checklist

Dokumen ini menjelaskan aturan minimum agar perubahan pada `main` bisa bergerak ke `staging` dan `ci-staging` tetap valid.

## Tujuan
Menjaga fase migrasi arsitektur tetap aman dengan memastikan
- import legacy tidak tersisa di jalur aktif
- strict deprecation tidak ditemukan di test suite

## Artifak yang dicek
1. **Legacy import scan**
   - Jalankan:
     ```bash
     python3 scripts/check_legacy_imports.py
     ```
   - Harus hasilkan:
     ```
     [migration-check] legacy-import-scan: 0 issues
     ```

2. **Strict migration test**
   - Jalankan:
     ```bash
     make test-strict
     ```
   - Harus lulus dengan `PALASIK_STRICT_DEPRECATION=1` dan `-W error::DeprecationWarning`.

3. **One-command migration check**
   - Jalankan:
     ```bash
     make migration-check
     ```
   - Wajib diperlakukan sebagai command rekomendasi sebelum PR ke `staging`.

## Status check di GitHub
Workflow `ci-staging.yml` mengekspos job berikut:
- `migration-gate` (required check)

Jika `migration-gate` fail, PR ke `staging` tidak boleh di-merge.

## Kriteria penghapusan `ci-staging.yml`
Workflow `ci-staging.yml` dapat dihapus bila 30 hari berturut-turut:
- `Legacy import scan = 0 issues`
- `make migration-check` pass
- tidak ada fitur baru yang mengembalikan dependency ke `palasik.core.trust_engine` atau `palasik.core.policy_engine`

## Branch protection

Jika sudah siap, jalankan:

```bash
bash scripts/apply_staging_branch_protection.sh --dry-run
bash scripts/apply_staging_branch_protection.sh --branch=staging
```

`--dry-run` bisa dijalankan tanpa `gh auth login` (menggunakan remote origin lokal untuk
menampilkan repository), jadi kamu tetap bisa verifikasi payload yang akan di-apply.

Pastikan `migration-gate` menjadi required status check pada branch protection `staging`.

Untuk verifikasi cepat:

```bash
bash scripts/check_staging_gate.sh --branch=staging
```

Exit code:
- `0` => `migration-gate` sudah required
- `2`/`3` => belum required (perlu diaktifkan)
- `4` => perlu autentikasi `gh` / token GitHub (`gh auth login` atau set `GH_TOKEN`)

Jika helper menolak karena token belum siap, jalankan autentikasi GitHub:

```bash
gh auth login
```

Atau gunakan token environment variable:

```bash
export GH_TOKEN=<token_with_repo_scope>
bash scripts/check_staging_gate.sh
```

Script ini membaca setting branch protection yang aktif saat ini.

## PR workflow

Gunakan PR template yang sudah disiapkan agar setiap perubahan yang mengarah ke `staging`
memuat checklist migration check.

- Lokasi template: `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md`
