# Mulai dalam 5 Menit (PALASIK Fase 1)

## 1) Inisialisasi

```bash
palasik init
```

Ini membuat `config.yaml` dengan policy baseline:

- `version: "1"`
- `default_deny: true`
- `policy_id: palasik-baseline`
- sample rules `deny_unknown_device` dan `allow_trusted_device`

## 2) Cek health

```bash
palasik check
```

Output utama yang diharapkan:

- `check: PASS`
- keputusan kesehatan dengan reason code

## 3) Simulasi keputusan

```bash
cp docs/samples/event-valid.json sample_event.json
palasik simulate sample_event.json
```

Contoh output:

```json
{
  "decision": "ALLOW",
  "policy_name": "rule_policy",
  "reason_code": "TRUSTED_DEVICE",
  "event_id": "evt-...",
  "event_version": "1",
  "rationale": [
    "rule='allow_trusted_device' matched",
    "action=ALLOW",
    "trust_score=0.9",
    "reason_code=TRUSTED_DEVICE"
  ],
  "trust_score": 0.9
}
```

## 4) Status observability

```bash
palasik status
```

Output utama:

```json
{
  "command": "status",
  "status": "UP",
  "metrics": {
    "events_total": 10,
    "events_allowed": 9,
    "events_denied": 1,
    "avg_latency_ms": 1.2,
    "reason_code_breakdown": {
      "TRUSTED_DEVICE": 9,
      "UNKNOWN_DEVICE": 1
    },
    "alerts": []
  }
}
```

## 5) Jalankan agent

```bash
palasik run
```
