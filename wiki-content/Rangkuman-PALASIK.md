# Rangkuman PALASIK (Ringkas)

PALASIK adalah lapisan keamanan keputusan untuk event IoT.

## Tujuan

- Menjaga data/event IoT lolos ke backend hanya ketika aman.
- Mengotomatisasi evaluasi keamanan dengan _trust score_ + aturan kebijakan.
- Mengurangi risiko outage karena kesalahan policy berkat _guard_ deployment.

## Cara kerja ringkas

- `adapter` menerima event dari sensor/gateway (MQTT/HTTP).
- `agent` menjalankan pipeline evaluasi.
- `trust engine` menentukan skor kepercayaan.
- `policy engine` memutuskan aksi.
- `plugin system` menjalankan tindakan log/forward/block/alert.

## Keunggulan operasional

- Decision log + reason code untuk audit.
- Snapshot policy sebelum perubahan.
- Smoke-check (`policy-deploy-check`) sebelum roll-out.
- Rollback cepat jika ada penurunan performa/police.

## Untuk siapa ini?

- Tim R&D dan akademik yang meneliti Zero Trust
- Tim operasi yang butuh kontrol deploy/rollback
- Produsen/peneliti sistem edge IoT skala industri
