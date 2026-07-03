# Runbook Operasional PALASIK

Dokumen ini untuk tim operasi agar rollout dan rollback policy bisa dilakukan cepat dan aman.

## Tahap 3: Dispatch, Audit, Metrics, Health

Tahap 3 berfokus pada kesiapan operasional fitur action dispatch sebelum deployment edge.

### Alur `POST /dispatch`

1. API menerima payload JSON:
   ```json
   {
     "trace_id": "trace-ops-001",
     "event": {
       "event_id": "evt-001",
       "type": "manual.dispatch",
       "source": {"device_id": "ops-console", "ip": "127.0.0.1"}
     },
     "actions": ["create_ticket", "notify_telegram_ops"],
     "metadata": {"message": "PALASIK alarm"}
   }
   ```
2. Event dinormalisasi jika `event_id`, `timestamp`, atau `source` belum ada.
3. Setiap action dipetakan ke adapter lewat `palasik.actions.routes`.
4. Dispatcher menulis audit `pending`.
5. Adapter dipanggil dengan `timeout` dan `idempotency_key`.
6. Jika gagal dan retry masih tersedia, dispatcher menulis `retrying`.
7. Jika akhirnya sukses, dispatcher menulis `success`.
8. Jika semua attempt habis, dispatcher menulis `failed`.
9. Response API mengembalikan hasil per action di field `results`.

### Arti status audit action

- `pending`: action sudah diterima dispatcher dan sedang menunggu attempt pertama.
- `retrying`: attempt sebelumnya gagal dan dispatcher sedang mencoba lagi.
- `success`: action berhasil dikirim atau ditandai duplicate yang aman untuk di-skip.
- `failed`: semua retry habis dan action tidak berhasil dijalankan.

### Isi `GET /metrics`

Endpoint ini mengembalikan snapshot operasional runtime:

- `events_total`, `events_allowed`, `events_denied`
- `pipeline_avg_latency_ms`
- `deny_ratio`
- `actions_total`, `actions_succeeded`, `actions_failed`
- `duplicate_actions`
- `failed_action_rate`
- `correlation_hit_count`
- `reason_code_breakdown`
- `health_status`
- `health_status_since_utc`
- `health_last_transition_utc`
- `health_transition_count`
- `health_status_breakdown`
- `health_last_reason`
- `health_last_reasons`

### Isi `GET /health`

Health operasional sekarang memakai severity eksplisit:

- `UP` -> HTTP `200`
- `DEGRADED` -> HTTP `200` jika `palasik.health.degraded_http_mode=ok`
- `DEGRADED` -> HTTP `503` jika `palasik.health.degraded_http_mode=fail`
- `DOWN` -> HTTP `503`

Payload tetap menjadi ringkasan cepat untuk on-call:

- `status`: status umum runtime
- `health.status_since_utc`: kapan status aktif sekarang mulai terjadi
- `health.last_transition_utc`: kapan transisi terakhir terjadi
- `health.transition_count`: berapa kali runtime sudah berpindah status
- `health.last_reason`: alasan utama yang paling baru
- `health.last_reasons`: daftar alasan health saat ini
- `actions.active_adapters`: adapter yang benar-benar aktif (`logger`, `webhook`, `telegram`, `whatsapp`, `relay`, `http_forward`)
- `actions.routes`: route action yang sedang dimuat dari config
- `actions.latest_retry_issue`: ringkasan retry/failed terakhir dari audit log
- `storage.audit_log`: path, status configured, exist, dan writable
- `storage.metrics_file`: path, status configured, exist, dan writable
- `metrics`: snapshot metrik + alert aktif

Pemisahan tanggung jawab:

- `check-startup` dipakai untuk fail-fast: config invalid, bind host/port tidak valid, route penting ke adapter tidak aktif, endpoint adapter aktif rusak, path wajib tidak writable.
- `GET /health` dipakai untuk degradasi runtime: action retry/failure terakhir, storage yang bermasalah setelah service hidup, atau komponen runtime yang turun.

### Alert contract dasar

Alert minimal yang perlu dipantau dari `metrics.alerts`:

- `health_down`: service berada di status `DOWN`.
- `health_degraded`: service terlalu lama di status `DEGRADED`.
- `failed_action_rate`: rasio action gagal terlalu tinggi.
- `deny_spike`: rasio deny melonjak di atas baseline.
- `trust_drop`: trust score turun tajam dibanding window sebelumnya.

Ambang alert dikendalikan dari `palasik.observability.alert` di config.

Interpretasi cepat:

- `health_down` adalah prioritas tertinggi karena service dianggap unavailable.
- `health_degraded` berarti service masih hidup, tapi ada gejala operasional yang harus dipulihkan.
- `failed_action_rate` biasanya menunjuk gangguan downstream action adapter atau endpoint target.

### Contoh dashboard dan query cepat

Panel minimum yang disarankan:

- `Current Health Status`
  Tampilkan `health.status`, `health.status_since_utc`, dan `health.last_reason`.
- `Health Transitions`
  Tampilkan `metrics.health_transition_count` dan `metrics.health_status_breakdown`.
- `Action Failure Rate`
  Tampilkan `metrics.failed_action_rate`, `metrics.actions_total`, dan `metrics.actions_failed`.
- `Latest Retry Issue`
  Tampilkan `actions.latest_retry_issue.action`, `actions.latest_retry_issue.status`, dan `actions.latest_retry_issue.event_id`.

Contoh query cepat dari host edge:

```bash
curl -s http://127.0.0.1:8080/health | jq '{status, health, latest_retry_issue: .actions.latest_retry_issue}'
```

```bash
curl -s http://127.0.0.1:8080/metrics | jq '.metrics | {
  health_status,
  health_transition_count,
  health_status_breakdown,
  failed_action_rate,
  actions_total,
  actions_failed,
  alerts
}'
```

Filter alert health saja:

```bash
curl -s http://127.0.0.1:8080/metrics | jq '.metrics.alerts | map(select(.type == "health_down" or .type == "health_degraded" or .type == "failed_action_rate"))'
```

Shortcut untuk operator:

```bash
bash scripts/check_health_alerts.sh
make edge-health
make edge-health-wait
make edge-health-strict
make edge-post-restart-check
make edge-post-restart-check-strict
```

Exit code:

- `0`: health `UP`, tidak ada alert health penting
- `1`: health `DEGRADED` atau ada alert warning/high
- `2`: health `DOWN` atau ada alert `critical`
- `4`: endpoint `/health` atau `/metrics` tidak reachable sama sekali

Mode strict:

- `make edge-health-strict` cocok untuk post-restart gate atau automation yang hanya menerima `status=UP`
- `make edge-health-wait` cocok untuk post-restart check yang memberi waktu tunggu lebih panjang sebelum menyatakan endpoint tidak reachable
- `make edge-post-restart-check` menjalankan `check-startup` lalu `edge-health-wait` berurutan untuk verifikasi pasca-restart
- `make edge-post-restart-check-strict` menjalankan `check-startup` lalu `edge-health-strict` untuk gate pasca-restart yang hanya menerima kondisi hijau penuh

### Langkah saat action gagal berulang

1. Cek `GET /health` dan lihat `actions.latest_retry_issue`.
2. Cek `GET /audit?limit=50` untuk urutan `pending -> retrying -> failed`.
3. Pastikan route action benar di `palasik.actions.routes`.
4. Verifikasi adapter aktif:
   - `webhook` perlu `endpoint`
   - `telegram` perlu `bot_token` dan `chat_id`
   - `whatsapp` perlu `endpoint`
   - `relay` perlu `endpoint`
5. Uji endpoint target dari host PALASIK:
   ```bash
   curl -i https://target.example/health
   ```
6. Jika error didominasi timeout/5xx:
   - naikkan `actions.timeout` seperlunya
   - pertimbangkan `actions.max_retries` dan `actions.retry_backoff_seconds`
   - jika target sedang bermasalah, ubah route sementara ke fallback `logger`
7. Jika duplicate dispatch muncul, cek apakah `event_id` dan `trace_id` memang dikirim ulang oleh caller.
8. Jika adapter memang belum tersedia, perbaiki config lalu restart service. Pada mode service, kondisi ini seharusnya ditangkap `check-startup`, bukan dibiarkan menjadi degradasi runtime.

### Langkah saat health masuk `DEGRADED` atau `DOWN`

1. Cek `GET /health` dan baca `health.last_reason` serta `health.status_since_utc`.
2. Jika `actions.latest_retry_issue` ada, telusuri action dan endpoint target yang sedang gagal.
3. Cek `GET /metrics` untuk `health_transition_count` dan `health_status_breakdown`:
   - transisi sering `UP <-> DEGRADED` biasanya menandakan flapping
   - bertahan lama di `DEGRADED` berarti perlu tindakan operasional, bukan sekadar observasi
4. Jika `status=DOWN`, perlakukan sebagai outage:
   - cek proses service
   - cek log runtime
   - verifikasi dependency internal yang wajib
5. Setelah recovery, pastikan `status` kembali `UP` dan catat durasi insiden dari `health.status_since_utc` sebelumnya.

## PALASIK dalam 5 Menit (Tim Operasi)

Tujuan: bisa cek kondisi, deploy aman, dan rollback cepat tanpa lihat source.

### 1) Kenali konsepnya
- Event melewati evaluasi trust + policy sebelum diteruskan.
- Output keputusan utama: `ALLOW`, `DENY`, `RESTRICT`, `CHALLENGE`, `MONITOR`.
- Metrik operasional berada di `status` output.

### 2) Cek kesehatan cepat (wajib di awal shift)

```bash
palasik check --config config.yaml
palasik status --config config.yaml
```

Interpretasi cepat:
- `check: PASS` → pipeline trust + policy aktif.
- `status.metrics.events_denied` / `events_allowed` stabil sesuai beban normal.
- `status.metrics.alerts` sebaiknya kosong.
- `status.health.status_since_utc` membantu melihat sejak kapan kondisi sekarang berlangsung.

### 3) Rollout policy aman (pre-deploy)

```bash
python3 -m palasik.cli.main policy-snapshot --config config.yaml
python3 -m palasik.cli.main policy-deploy-check \
  --config config.yaml \
  --smoke-events docs/samples/policy-smoke-events.json \
  --max-deny-ratio 0.95 \
  --require-allow
```

Jika PASS: lanjut deploy.
Jika FAIL: stop rollout dulu, review aturan policy.

### 4) Tanggap degradasi

```bash
palasik status --config config.yaml > /tmp/palasik-status-before-incident.json

python3 -m palasik.cli.main policy-rollback \
  --config config.yaml \
  --snapshot runs/policy_snapshots/<snapshot_terakhir>.snapshot.yaml

palasik check --config config.yaml
palasik status --config config.yaml
```

Jika rollback dipakai, catat:
- timestamp insiden
- snapshot yang dipakai
- `/tmp/palasik-status-before-incident.json` sebagai bukti status awal

## 1) Rollout rutin

1. Ambil snapshot policy aktif (sebelum deploy)
   ```bash
   python3 -m palasik.cli.main policy-snapshot --config config.yaml
   ```
2. Jalankan validasi akhir policy (pre-deploy)
   ```bash
   python3 -m palasik.cli.main policy-deploy-check \
     --config config.yaml \
     --smoke-events docs/samples/policy-smoke-events.json \
     --max-deny-ratio 0.95 \
     --require-allow
   ```
3. Terapkan policy baru di sistem distribusi config (ansible/helm/pulled config).
4. Verifikasi jalur hidup:
   - `palasik check`
   - `palasik status --config config.yaml`
5. Pantau `events_denied`, `avg_latency_ms`, dan `alerts` dari output status selama 5 menit pertama.

## 2) Jika terjadi degradasi (deny spike / trust drop)

- Jika `alerts` menampilkan `deny_spike` atau `trust_drop`, turunkan tingkat risiko dengan menjalankan:
  ```bash
  python3 -m palasik.cli.main status --config config.yaml
  ```
- Cek apakah ada event baru yang memicu deny massal (event source, policy id, reason code).
- Jika dampak layanan tinggi, rollback:
  ```bash
  python3 -m palasik.cli.main policy-rollback \
    --config config.yaml \
    --snapshot runs/policy_snapshots/<snapshot_file>.snapshot.yaml
  ```
  lalu `palasik check` ulang.

## 3) Backup / rollback artifacts

- Snapshot policy: `runs/policy_snapshots/`
- Backup config saat rollback: `runs/policy_backups/`
- Snapshot metadata termasuk:
  - `created_at_utc`
  - `policy_signature`
  - `policy_version`

## 4) Kriteria pass gate operasional

Sebelum shift handoff, pastikan:
- `policy-snapshot` sukses
- `policy-deploy-check` PASS
- `migration-check` PASS
- `make test`/`pytest` PASS pada branch yang akan di-deploy

## 5) Playbook siap pakai per role

### A. Shift On-Call (awal shift)

Tujuan: memastikan observability dan state awal aman.

1. Pengecekan sehat:
   ```bash
   palasik check --config config.yaml
   ```
2. Cek status + ringkasan metrik:
   ```bash
   palasik status --config config.yaml
   ```
3. Pastikan artifact penting ada:
   - `runs/metrics.json`
   - `runs/audit.jsonl`
   - `runs/policy_snapshots/` (untuk rollback cepat)

### B. Operator (deploy policy)

Urutan harian untuk perubahan policy:

1. Ambil snapshot baseline (wajib):
   ```bash
   python3 -m palasik.cli.main policy-snapshot --config config.yaml
   ```
2. Jalankan guard pre-deploy:
   ```bash
   python3 -m palasik.cli.main policy-deploy-check \
     --config config.yaml \
     --smoke-events docs/samples/policy-smoke-events.json \
     --max-deny-ratio 0.95 \
     --require-allow
   ```
3. Deploy config/policy ke environment target.
4. Verifikasi dua menit pertama:
   ```bash
   palasik check --config config.yaml
   palasik status --config config.yaml
   ```

### C. QA/Pasca Deploy

Verifikasi cepat 5–10 menit setelah deployment:

1. Jalankan smoke policy:
   ```bash
   python3 -m palasik.cli.main policy-deploy-check \
     --config config.yaml \
     --smoke-events docs/samples/policy-smoke-events.json \
     --max-deny-ratio 0.95 \
     --require-allow
   ```
2. Ambil bukti status saat ini (attach ke ticket/PR):
   ```bash
   palasik status --config config.yaml | tee /tmp/palasik-status-post-deploy.json
   ```
3. Simpan output test/review policy jika ada perubahan rule:
   ```bash
   python3 -m palasik.cli.main validate-policy --config config.yaml
   ```

### D. Tim Response (degradasi)

Kalau ada gejala deny spike / trust drop:

1. Ambil snapshot status sekarang:
   ```bash
   palasik status --config config.yaml > /tmp/palasik-status-before-incident.json
   ```
2. Rollback cepat ke snapshot terakhir yang valid:
   ```bash
   python3 -m palasik.cli.main policy-rollback \
     --config config.yaml \
     --snapshot runs/policy_snapshots/<snapshot_terakhir>.snapshot.yaml
   ```
3. Konfirmasi kembali sehat:
   ```bash
   palasik check --config config.yaml
   palasik status --config config.yaml
   ```
4. Catat incident:
   - timestamp
   - alasan rollback
   - evidence file: `/tmp/palasik-status-before-incident.json`
