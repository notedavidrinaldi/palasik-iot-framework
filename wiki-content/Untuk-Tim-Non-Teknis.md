# Untuk Tim Non-Teknis

PALASIK adalah “petugas gerbang keamanan” untuk data sensor.

Setiap data tidak langsung aman dan harus melewati aturan.

Keputusan yang dihasilkan:

- **ALLOW**: data diteruskan
- **DENY**: data diblok
- **MONITOR/RESTRICT/CHALLENGE**: data masuk jalur khusus pengawasan

Kenapa ini penting:

- Aturan lebih konsisten daripada pemeriksaan manual.
- Setiap keputusan punya alasan.
- Jika ada masalah, rollback bisa dilakukan cepat.

Langkah kerja sederhana:

1. `palasik check`
2. `palasik status`
3. Sebelum perubahan policy: snapshot + deploy-check
4. Jika anomali: rollback ke snapshot valid
