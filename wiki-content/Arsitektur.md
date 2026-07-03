# Arsitektur PALASIK

## Lokasi dan posisi

PALASIK berjalan di **edge / gateway** sebagai pengaman lalu lintas IoT sebelum masuk ke backend.

## Alur data (high level)

```text
IoT Device/Sensor -> Adapter -> Agent -> Trust Engine -> Policy Engine -> Plugin/Enforcement -> Backend/Service
```

## Komponen utama

- **Adapter**: terima event dari sumber eksternal (MQTT, HTTP)
- **Agent**: orkestrasi runtime PALASIK
- **Trust Engine**: hitung trust score (0.0 – 1.0)
- **Policy Engine**: ubah skor + aturan menjadi keputusan
- **Plugin System**: aksesi side-effect (log, forward, alert, audit)

## Prinsip desain

- Zero Trust by Default
- Keputusan eksplisit (explicit decision)
- Alur satu arah (event masuk, diputuskan, dieksekusi)
- Pemisahan tanggung jawab modul
