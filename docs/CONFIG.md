# PALASIK Configuration

PALASIK mendukung konfigurasi melalui file YAML dan Environment Variable.

---

## Contoh config.yaml

```yaml
palasik:
  broker:
    host: localhost
    port: 1883
    topic: palasik/sensor/#

  policy:
    version: "1"
    default_deny: true
    default_action: DENY
    type: rule
    rules:
      - id: deny_unknown_device
        action: DENY
        reason_code: UNKNOWN_DEVICE
        condition:
          op: eq
          key: source.device_id
          value: unknown
      - id: allow_trusted_device
        action: ALLOW
        reason_code: TRUSTED_DEVICE
        condition:
          op: gte
          key: trust_score
          value: 0.75

  plugins:
    enabled:
      - logger
      - audit

  # Observability: metrik + alert dasar
  observability:
    metrics_file: runs/metrics.json
    alert:
      deny_spike_threshold: 0.45
      trust_score_drop_threshold: 0.25
      failed_action_rate_threshold: 0.5
      health_degraded_for_seconds: 60
      health_down_for_seconds: 0

  health:
    degraded_http_mode: ok

  decision_log: runs/decisions.jsonl
  audit_log: runs/audit.jsonl

  actions:
    timeout: 3.0
    max_retries: 3
    retry_backoff_seconds: 0.5
    idempotency_cache_size: 2048
    routes:
      create_ticket: webhook
      notify_telegram_ops: telegram
      notify_whatsapp_ops: whatsapp
      relay_off: relay
      plc_stop: relay
      http_forward: http_forward
    webhook:
      endpoint: https://ops.internal.example/hooks/palasik
      headers:
        Authorization: Bearer change-me
        X-PALASIK-Env: staging
    telegram:
      bot_token: 123456:replace-me
      chat_id: "-1001234567890"
    whatsapp:
      endpoint: https://graph.facebook.example/v1/messages
      headers:
        Authorization: Bearer change-me
    relay:
      endpoint: http://192.168.1.20/api/relay
      headers:
        X-Relay-Key: change-me
```

Catatan operasional:
- `actions.timeout` berlaku untuk adapter HTTP (`webhook`, `telegram`, `whatsapp`, `relay`) per attempt.
- `actions.max_retries` adalah jumlah total percobaan, termasuk attempt pertama.
- `actions.retry_backoff_seconds` memberi jeda antar retry.
- `actions.routes` memetakan nama action ke adapter. Untuk mode service, route penting yang menunjuk adapter tidak aktif akan ditolak oleh `check-startup` agar fail-fast.
- `actions.webhook`, `actions.telegram`, `actions.whatsapp`, dan `actions.relay` baru aktif jika field wajibnya terisi.
- `observability.alert.failed_action_rate_threshold` memicu alert jika rasio action gagal melewati ambang yang ditetapkan.
- `observability.alert.health_degraded_for_seconds` memicu alert jika status `DEGRADED` bertahan lebih lama dari ambang.
- `observability.alert.health_down_for_seconds` memicu alert jika status `DOWN` bertahan lebih lama dari ambang. Nilai `0` berarti langsung alert.
- `health.degraded_http_mode` mengatur HTTP status untuk runtime `DEGRADED`: `ok` mengembalikan `200`, `fail` mengembalikan `503`.

Environment Variable
```yaml
PALASIK_BROKER_HOST=localhost
PALASIK_BROKER_PORT=1883
PALASIK_POLICY_THRESHOLD=0.7
PALASIK_METRICS_FILE=runs/metrics.json
PALASIK_DENY_SPIKE_THRESHOLD=0.45
PALASIK_TRUST_DROP_THRESHOLD=0.25
PALASIK_AUDIT_LOG=runs/audit.jsonl
PALASIK_ACTION_TIMEOUT=3
PALASIK_ACTION_MAX_RETRIES=3
PALASIK_ACTION_RETRY_BACKOFF_SECONDS=0.5
PALASIK_EVENT_MAX_AGE_SECONDS=600
PALASIK_RISK_WARN_THRESHOLD=55
PALASIK_RISK_QUARANTINE_THRESHOLD=75
PALASIK_RISK_CRITICAL_THRESHOLD=92
PALASIK_RISK_CRITICAL_ACTION=BLOCK_ALARM
PALASIK_CORRELATION_WINDOW_SECONDS=120
PALASIK_CORRELATION_REPEAT_THRESHOLD=3
PALASIK_CORRELATION_RISK_THRESHOLD=75
```

Prioritas Konfigurasi

- Environment Variable

- YAML

- Default Code


---

Challenge (Opsional)

Untuk policy `type: rule`, kamu bisa pakai keputusan `CHALLENGE` pada rule.

Tanpa handler, CHALLENGE akan diperlakukan sebagai diblok sementara sampai sistem
melakukan challenge.

Kunci event yang didukung:
- `challenge_passed: true` pada event untuk membiarkan event masuk
- atau set `context.challenge_handler` secara programmatic pada `PalasikContext`
  (callable: `(event, context, decision_record) -> bool`).

### Kontrak Baseline

- Fase 0 menetapkan policy baseline di [`FASE_0_FOUNDATION.md`](FASE_0_FOUNDATION.md)
- `default_deny` harus aktif (`true`) pada baseline.
- Setiap deny harus membawa `reason_code` dalam catatan keputusan/tindak lanjut di fase berikutnya.


## Decision Log (Opsional)

Untuk penelitian dan audit, aktifkan `decision_log`:

```yaml
palasik:
  decision_log: ./runs/decisions.jsonl
```

## Health Contract

Kontrak severity runtime:

- `UP` -> HTTP `200`
- `DEGRADED` -> HTTP `200` jika `palasik.health.degraded_http_mode=ok`
- `DEGRADED` -> HTTP `503` jika `palasik.health.degraded_http_mode=fail`
- `DOWN` -> HTTP `503`

Pemisahan operasional:

- `check-startup` fail-fast untuk config invalid, bind host/port tidak valid, route penting ke adapter tidak aktif, path wajib tidak writable, atau endpoint adapter aktif rusak.
- `GET /health` dipakai untuk runtime degradation seperti retry/failure action terakhir atau storage yang sempat bermasalah setelah service hidup.

Field observability baru yang muncul di `metrics`/`health`:

- `health_status`: status health terbaru yang sedang aktif.
- `health_status_since_utc`: timestamp kapan status saat ini mulai berlaku.
- `health_last_transition_utc`: timestamp perpindahan status terakhir.
- `health_transition_count`: jumlah total transisi health sejak runtime mulai.
- `health_status_breakdown`: counter transisi per status (`UP`, `DEGRADED`, `DOWN`).
- `health_last_reason`: alasan utama terakhir yang mendorong status health saat ini.
- `health_last_reasons`: daftar alasan health saat ini untuk inspeksi cepat.

Alert yang tersedia di `metrics.alerts`:

- `deny_spike`
- `trust_drop`
- `failed_action_rate`
- `health_degraded`
- `health_down`

Setiap event yang diproses akan menulis satu baris JSON (`event_id`, `trust_score`, `decision`, dll).

Contoh analisis dengan `experiments/decision_ledger.py`:

```bash
python experiments/decision_ledger.py runs/decisions.jsonl
python experiments/decision_ledger.py --format json runs/decisions.jsonl
```

Format ringkas per baris:

```json
{
  "event_id": "uuid",
  "trust_score": 0.82,
  "decision": "ALLOW",
  "policy_name": "allow_deny_policy",
  "rationale": ["trust_score=0.82 >= threshold=0.7: ALLOW"],
  "event_snapshot": {"type": "...", "topic": "...", "value": 10, "source": "..."},
  "challenge": null,
  "created_at_utc": "2026-..."
}
```
