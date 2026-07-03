# Memulai PALASIK

## Instalasi

```bash
pip install palasik
```

## Inisialisasi proyek contoh

```bash
palasik init
```

Perintah ini membuat `config.yaml` dan struktur dasar demo.

## Alur kerja dasar

```bash
palasik check
palasik simulate sample-event.json
palasik run
```

## Command yang sering dipakai

- `palasik check` → validasi runtime start-up
- `palasik status --config config.yaml` → indikator kesehatan dan metrik runtime
- `palasik simulate <event.json>` → uji keputusan tanpa running penuh
- `palasik policy-snapshot --config config.yaml` → ambil snapshot policy
- `palasik policy-deploy-check --config config.yaml --require-allow` → smoke test kebijakan
- `palasik policy-rollback --config config.yaml --snapshot runs/policy_snapshots/<file>` → rollback cepat

## Contoh event MQTT

```bash
mosquitto_pub -t palasik/sensor/temp -m '{"value": 42}'
```
