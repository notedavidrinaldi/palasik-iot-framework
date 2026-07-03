# PALASIK Executive Summary (1 Menit)

PALASIK adalah komponen Zero Trust untuk lalu lintas event IoT yang memutuskan otomatis apakah tiap event boleh diproses, ditunda untuk verifikasi, atau ditolak. Tujuannya meningkatkan keamanan tanpa mengorbankan kontrol operasional.

Keputusan dibuat berdasarkan trust score dan policy yang tervalidasi, lalu dikaitkan dengan catatan keputusan (`reason code`) sehingga perilaku sistem bisa diaudit dan ditelusuri.

Dari sisi operasi, PALASIK dirancang agar perubahan kebijakan aman: ada command snapshot policy sebelum deploy, smoke-check deployment (`policy-deploy-check`), dan rollback cepat ke policy sebelumnya bila terjadi degradasi.

Indikator kesehatan utama yang dipakai tim operasi adalah: status startup (`check`), metrik runtime (`status`), event deny rate, dan alert otomatis.

Secara praktis, PALASIK menurunkan risiko outage akibat policy salah dengan menambah guard sebelum deployment dan jalur pemulihan yang cepat.
