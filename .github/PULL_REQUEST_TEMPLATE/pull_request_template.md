---
name: PR Template
about: Standard PR checklist for PALASIK contributions
labels: []
assignees: []
---

## Ringkasan
<!-- Jelaskan perubahan yang dilakukan secara singkat -->

## Checklist Testing
- [ ] `make migration-check` telah dijalankan (wajib)
- [ ] Jika relevan dengan fitur inti trust/policy, juga menjalankan test terkait secara manual
- [ ] `bash scripts/check_staging_gate.sh --branch=staging` (status required check `migration-gate`) jika PR target ke `staging`

## Untuk PR ke `staging`
Centang jika PR ini ditargetkan ke `staging`:
- [ ] `python3 scripts/check_legacy_imports.py` menghasilkan `0 issues`
- [ ] `make test-strict` lulus (deprecation menjadi error)
- [ ] `make migration-check` tercapai clean

## Catatan Migrasi
- [ ] Tidak ada penggunaan import legacy baru ke `palasik.core.trust_engine` atau `palasik.core.policy_engine`
- [ ] Jika ada pengecualian, dijelaskan di komentar PR dan dirujuk ke `docs/MIGRATION_GATE.md`

## Referensi
- docs: [MIGRATION_GATE](docs/MIGRATION_GATE.md)
- quick-check command: `make migration-check`
