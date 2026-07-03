# Policy Engine

Policy Engine mengubah input trust + metadata event menjadi keputusan:

- `ALLOW`
- `DENY`
- `MONITOR / RESTRICT / CHALLENGE` (sesuai konfigurasi)

## Aturan dan tipe umum

- `allow_deny` (mode aman default)
- `rule_based` (aturan deklaratif)
- plugin policy custom (jika diperlukan)

## Mekanisme keamanan saat deploy

Sebelum policy aktif, jalankan:

1. `policy-snapshot` untuk merekam kebijakan saat ini.
2. `policy-deploy-check` untuk melakukan smoke check.

Jika hasil pemeriksaan tidak aman, rollback ke snapshot terakhir.
