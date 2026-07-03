# Palasik untuk Tim Non-Teknis (1 Halaman)

## PALASIK itu apa?
PALASIK adalah “petugas gerbang keamanan” untuk data sensor/IoT.

Setiap data yang masuk ke gateway tidak langsung dianggap aman.
Ia diproses dulu melalui aturan yang kita tentukan, lalu diputuskan apakah:
- **dilewati** (ALLOW),
- **ditolak** (DENY),
- **dipantau/diwaspadai** (MONITOR/RESTRICT/CHALLENGE).

Tujuannya: mencegah event berbahaya mempengaruhi sistem lebih dulu.

## Kenapa ini penting untuk operasi
- Keputusan berjalan konsisten (berbasis aturan).
- Ada bukti keputusan (reason code) dan log.
- Tim bisa rollback cepat jika policy berubah dan bermasalah.
- Ada indikator cepat seperti jumlah deny, deny spike, dan indikator penurunan trust.

## “Peta mental” cara kerja PALASIK
1) Event masuk dari sensor/gateway.
2) Sistem menilai tingkat kepercayaan.
3) Rule policy dipakai untuk menentukan keputusan.
4) Keputusan dieksekusi + dicatat.

## Cara kerja harian (simple)
- **Mulai shift**: jalankan check dan status untuk pastikan sehat.
- **Sebelum deploy policy baru**: ambil snapshot, lalu jalankan smoke-check.
- **Saat ada anomali**: rollback cepat ke snapshot terakhir yang valid.
- **Setelah normal**: kembalikan monitoring rutin.

## Command kunci (untuk staf operasi)
- `palasik check --config config.yaml`
- `palasik status --config config.yaml`
- `python3 -m palasik.cli.main policy-snapshot --config config.yaml`
- `python3 -m palasik.cli.main policy-deploy-check --config config.yaml --require-allow`
- `python3 -m palasik.cli.main policy-rollback --config config.yaml --snapshot runs/policy_snapshots/<file>`

## Kapan rollback dilakukan
Rollback dilakukan jika deployment menyebabkan:
- penolakan event tidak normal (deny spike),
- latency meningkat mendadak,
- keputusan jadi tidak sesuai ekspektasi bisnis.

Prosesnya cepat: rollback dipicu dari snapshot, lalu `check` ulang.

## Catatan akhir
- Default baseline sudah diarahkan untuk **tidak percaya event secara otomatis**.
- Prinsip yang dijaga: aman dulu, lalu tetap jalan (fail-safe).
