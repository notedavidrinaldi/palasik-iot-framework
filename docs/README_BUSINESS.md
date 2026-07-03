# PALASIK untuk Stakeholder (Versi Ringkas)

PALASIK adalah lapisan keamanan yang menentukan apakah setiap data/event IoT boleh diproses atau tidak, bukan langsung mengizinkan semuanya.

Setiap event akan melalui aturan kepercayaan dan policy terlebih dulu, lalu diputuskan sebagai “izinkan”, “batalkan”, atau “monitor khusus”. Karena ini otomatis, keputusan menjadi konsisten dan lebih terukur dibandingkan pemeriksaan manual.

Untuk operasi, PALASIK menyediakan kontrol yang penting: pengecekan sehat (`check`), status metrik real-time (`status`), snapshot policy sebelum deploy, dan rollback cepat jika ada masalah.

Sebelum merilis policy baru, tim mengeksekusi `policy-snapshot` lalu `policy-deploy-check` sebagai guard. Jika hasil guard tidak aman, deploy dibatalkan dulu agar sistem tidak terkena outage.

Target operasional PALASIK bukan sekadar “aman secara teori”, tetapi “aman dan tetap jalan”: risiko bisa dibatasi, keputusan bisa ditelusuri, dan pemulihan bisa dilakukan cepat.
