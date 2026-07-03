# Getting Started with PALASIK

Panduan singkat untuk menjalankan PALASIK dari nol.

## 1. Instalasi

```bash
pip install palasik
```

## 2. Inisialisasi

```bash
mkdir palasik-demo
cd palasik-demo
palasik init
```

Perintah ini membuat `config.yaml` dengan policy baseline.

## 3. Health Check

```bash
palasik check
```

Cek ini memastikan agent bisa load config, menjalankan trust/policy pipeline,
and semua command startup berjalan.

## 4. Simulasi Keputusan

Buat event test:

```bash
cat > sample-event.json <<'EOF_JSON'
{
  "version": "1",
  "event_id": "evt-startup-01",
  "timestamp": "2026-07-01T09:00:00Z",
  "type": "sensor.sample",
  "source": {
    "device_id": "edge-sensor-01",
    "ip": "192.168.1.10"
  },
  "value": 42
}
EOF_JSON

palasik simulate sample-event.json
```

## 5. Memantau Status

```bash
palasik status --config config.yaml
```

Output berisi status, counters, dan alerts:

```text
{
  "command": "status",
  "status": "UP",
  "metrics": {
    "events_total": 12,
    "events_allowed": 11,
    "events_denied": 1,
    "avg_latency_ms": 2.5,
    "reason_code_breakdown": {
      "TRUSTED_DEVICE": 10,
      "UNKNOWN_DEVICE": 1
    },
    "alerts": [...]
  }
}
```

## 5b. Rollout policy aman

Sebelum deploy policy baru, ambil snapshot dan jalankan smoke check:

```bash
python3 -m palasik.cli.main policy-snapshot --config config.yaml
python3 -m palasik.cli.main policy-deploy-check --config config.yaml --require-allow
```

Jika perlu rollback cepat:

```bash
python3 -m palasik.cli.main policy-rollback \
  --config config.yaml \
  --snapshot runs/policy_snapshots/<file>
```

Untuk melihat metrik mentah (sehingga bisa dipasang ke dashboard):

```bash
cat runs/metrics.json
```

## 6. Menjalankan Gateway

```bash
palasik run --config config.yaml
```

Jika berhasil, agent akan aktif menunggu event.
