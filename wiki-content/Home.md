# PALASIK Wiki

## PALASIK adalah apa?

**PALASIK** (Policy-Aware Lightweight Adaptive Security for IoT) adalah **framework Python berbasis Zero Trust** untuk edge/gateway IoT.

Framework ini tidak menganggap event atau device aman secara default. Setiap event diproses lewat alur:

1. **Trust Evaluation** → hitung trust score
2. **Policy Decision** → ambil keputusan eksplisit `ALLOW / DENY / MONITOR`
3. **Enforcement & Plugin** → eksekusi aksi (log/forwarding/alert)

---

## Sumber cepat

- Repositori: https://github.com/notedavidrinaldi/palasik-iot-framework
- Dokumentasi web: https://notedavidrinaldi.github.io/palasik/
- Versi pypi: https://pypi.org/project/palasik/

---

## Konsep inti PALASIK

- **Trust Engine**: menilai perilaku dan konteks event (device, topic, anomali, nilai metrik)
- **Policy Engine**: menerjemahkan skor trust + aturan menjadi keputusan
- **Enforcement**: mengeksekusi keputusan secara konsisten, bukan implicit routing
- **Plugin**: menambah aksi seperti audit, logging, alerting, forward

## Kenapa penting

- Mencegah keputusan keamanan ad-hoc
- Meningkatkan konsistensi keputusan
- Menyediakan `snapshot` + `rollback` agar deployment policy lebih aman
- Lebih mudah ditelusuri karena alasan keputusan disertakan dalam event log

---

## Status proyek saat ini

- Core sudah stabil (v0.2.0)
- Tersedia `check`, `status`, `simulate`, `policy-snapshot`, `policy-deploy-check`, `policy-rollback`
- Sudah dipakai untuk eksperimen riset dan siap dikembangkan sebagai platform keamanan IoT

Lihat halaman lain di sidebar untuk detail.

## Dukung Proyek Ini

- ⭐ **Star** repository untuk meningkatkan visibilitas
- 🛠️ **Contribute** lewat PR untuk kode, dokumentasi, atau contoh eksperimen
- 🗣️ Bagikan penggunaan PALASIK di forum/komunitas
- ✅ Buat 1 issue kecil kalau menemukan bug atau ide
- 🤝 Ajak 1 kolaborator untuk mencoba setup 10 menit

