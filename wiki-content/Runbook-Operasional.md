# Runbook Operasional

## Start of Shift (5 menit)

1. `palasik check --config config.yaml`
2. `palasik status --config config.yaml`
3. Jika ada alarm deny spike, catat status baseline lalu investigasi log.

## Deploy Policy Baru

1. `python3 -m palasik.cli.main policy-snapshot --config config.yaml`
2. `python3 -m palasik.cli.main policy-deploy-check --config config.yaml --require-allow`
3. Deploy hanya jika hasil check aman.
4. Verifikasi lewat `palasik status` dan `palasik check` setelah deploy.

## Insiden

### Jika ada perilaku tidak normal

1. Ambil status sementara ke file:

```bash
palasik status --config config.yaml > /tmp/palasik-status-before-incident.json
```

2. Rollback ke snapshot terakhir yang valid:

```bash
python3 -m palasik.cli.main policy-rollback --config config.yaml --snapshot runs/policy_snapshots/<file>
```

3. Jalankan ulang `palasik check` dan `status`.

## Kunci operasional

- Metrik deny spike dan trust drop harus dipantau rutin.
- Snapshot + rollback adalah mekanisme utama kontrol risiko.
