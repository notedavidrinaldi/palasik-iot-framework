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
    type: allow_deny
    threshold: 0.7

  plugins:
    enabled:
      - logger
```

Environment Variable
```yaml
PALASIK_BROKER_HOST=localhost
PALASIK_BROKER_PORT=1883
PALASIK_POLICY_THRESHOLD=0.7
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



## Decision Log (Opsional)

Untuk penelitian dan audit, aktifkan `decision_log`:

```yaml
palasik:
  decision_log: ./runs/decisions.jsonl
```

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
