# API Contract — Tahap 1 (Desain)

## Tujuan
Menyatukan cara antar layanan berbicara agar Tahap 2 tidak berubah-ubah.

## Endpoint internal minimum

### `POST /events/ingest`
- Input: event raw
- Output: `202 Accepted` + envelope keputusan awal

Request
```json
{
  "event": { /* schema event-v1.1 */ },
  "trace_id": "trace-uuid"
}
```

Response
```json
{
  "status": "queued",
  "event_id": "evt-...",
  "trace_id": "trace-uuid"
}
```

### `POST /events/evaluate`
- Input: event tervalidasi
- Output: `DecisionResult`

Response
```json
{
  "event_id": "evt-...",
  "decision": "ALLOW",
  "risk_score": 14,
  "risk_label": "LOW",
  "matched_rules": ["rule-01"],
  "reason": ["policy=allow-known-device"],
  "actions": ["none"],
  "trace_id": "trace-uuid",
  "correlation_id": null,
  "created_at_utc": "2026-07-03T03:12:00Z"
}
```

### `GET /decisions/{event_id}`
- Mengambil keputusan dan aksi final dari audit store.

### `GET /health`
- Menampilkan status modul: collector, validator, policy, risk, decision, action, audit.

### `GET /audit`
- Query params: `start`, `end`, `limit`, `decision`, `source_device`.

### `POST /policy/load`
- Input: `policy-v2` yaml/json.
- Output status dan validation result.

## Error envelope

Semua endpoint mengembalikan format:
```json
{
  "ok": false,
  "error_code": "INVALID_SCHEMA",
  "message": "...",
  "trace_id": "trace-uuid"
}
```
