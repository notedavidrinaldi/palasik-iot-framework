# Cara Menggunakan PALASIK

## 60 Detik Setup

Jika Anda baru pertama kali, lakukan:

```bash
pip install palasik
palasik init
palasik check
palasik run
```

Jika `check` lolos, itu tandanya instalasi sudah siap.

## 5 menit pemakaian pertama

1. Jalankan demo lokal dari konfigurasi default.
2. Coba `simulate` dengan event contoh.
3. Buat policy awal sesuai kebutuhan (`ALLOW`/`DENY`).
4. Jalankan `status` sebelum dan sesudah update policy.

## Saran untuk pemakaian nyata

- Mulai dari `deny-by-default` di edge yang sensitif.
- Tetapkan alert pada deny spike dan trust drop.
- Aktifkan plugin audit/log untuk observability sejak awal.
- Selalu lakukan `policy-snapshot` sebelum `policy-deploy-check`.

## Arsitektur pemakaian

- **PoC kecil**: 1 sensor + 1 adapter + 1 policy.
- **Uji lab**: tambah simulasi event abnormal.
- **Produksi awal**: gunakan DEMIT, plugin audit, dan runbook operasional.

## Referensi cepat

- [Memulai PALASIK](/Memulai-PALASIK)
- [Trust Engine](/Trust-Engine)
- [Runbook Operasional](/Runbook-Operasional)
