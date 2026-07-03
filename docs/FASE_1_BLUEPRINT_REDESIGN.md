# Tahap 1 — Blueprint Redesign PALASIK

## Tujuan
Mentransformasi arsitektur PALASIK dari “event forwarding + filtering” menjadi **Policy & Event Decision Engine** (event → validasi → policy → risk score → keputusan → aksi → audit) pada Raspberry Pi.

## Output yang harus dihasilkan
1. Desain arsitektur modular final.
2. Kontrak data event/policy/keputusan.
3. API contract antarmodul.
4. Template policy dan contoh kasus.
5. Gate kesiapan untuk masuk Tahap 2 (implementasi).

## Rencana Eksekusi (Hari 1–7)

### Hari 1 — Finalisasi ruang lingkup
- [ ] Revisi definisi produk: dari Zero Trust Framework menjadi Decision Engine + Zero Trust sebagai sub-komponen.
- [ ] Tetapkan _DoD_ Tahap 1.
- [ ] Siapkan metrik awal: `latency_p95`, `policy_match_rate`, `decision_error_rate`, `fallback_activation_rate`.
- [ ] Output: keputusan desain + daftar kebutuhan non-negotiable.

### Hari 2 — Inventaris komponen lama vs baru
- [ ] Mapping komponen lama:
  - input/adapter
  - trust engine
  - policy engine
  - enforcement/plugin
  - logging/audit
- [ ] Tandai apa yang dipertahankan, refactor, ditambah.
- [ ] Output: matriks `retain/refactor/add` per modul.

### Hari 3 — Desain modul pipeline baru
- [ ] Buat diagram modul final:
  - `collector`
  - `validator`
  - `trust-context`
  - `policy-engine`
  - `risk-engine`
  - `correlation-engine`
  - `decision-router`
  - `action-dispatcher`
  - `audit-service`
- [ ] Definisikan timeout, fallback, error code per modul.
- [ ] Output: `docs/palasik-architecture-v1.svg` atau mermaid flow.

### Hari 4 — Kontrak Event & Context
- [ ] Finalkan `event schema` baru (v1.1 internal) dengan minimal:
  - `event_id`
  - `version`
  - `timestamp`
  - `type`
  - `topic`
  - `source.device_id`, `source.ip`, `source.protocol`
  - `value`
  - `location`
  - `metadata`
  - `trust_ctx`
- [ ] Definisikan `error_code`: `INVALID_SCHEMA`, `UNREGISTERED_DEVICE`, `BAD_SIGNATURE`, `EVENT_EXPIRED`, `DUPLICATE_EVENT`.
- [ ] Output: contoh event valid/invalid untuk 3 use case.

### Hari 5 — Desain policy sebagai kode
- [ ] Tetapkan struktur policy `yaml/json`:
  - `policy_id`, `version`, `scope`, `name`, `enabled`, `priority`
  - `conditions[]`, `actions[]`, `decision` (ALLOW/WARN/QUARANTINE/DENY/BLOCK_ALARM)
  - `risk_overrides`, `effective_from`, `effective_to`
- [ ] Tetapkan life-cycle: `draft -> testing -> active -> archived`.
- [ ] Buat konflik: prioritas + `default_action`.
- [ ] Output: 5 contoh policy siap uji.

### Hari 6 — Model keputusan (Decision Contract)
- [ ] Final `DecisionResult`:
  - `event_id`
  - `risk_score`
  - `risk_label`
  - `decision`
  - `matched_rules[]`
  - `actions[]`
  - `reason`
  - `trace_id`
- [ ] Final rule mapping risiko:
  - 0–25: `ALLOW`
  - 26–60: `WARN`
  - 61–80: `QUARANTINE`
  - 81–100: `DENY`
  - 100 + critical signal: `BLOCK_ALARM`
- [ ] Output: matriks keputusan + skenario konflik.

### Hari 7 — API Contract & Keamanan operasi
- [ ] Tetapkan endpoint minimal internal:
  - `POST /events/ingest`
  - `POST /events/evaluate`
  - `GET /decisions/{id}`
  - `GET /health`
  - `GET /audit`
  - `POST /policy/load`
- [ ] Final fallback:
  - Aset kritikal: fail = deny + alert + log.
  - Non-kritis: monitor + delay-forward.
- [ ] Output: `docs/PHASE1_API_CONTRACT.md`.

## Deliverable wajib Tahap 1
- `docs/FASE_1_BLUEPRINT_REDESIGN.md` (dokumen ini)
- `docs/schemas/event-v1.1.schema.json`
- `docs/schemas/decision-v1.schema.json`
- `docs/schemas/policy-v2.schema.json`
- `docs/samples/event-*.json` (door, freezer, vibration, rfid)
- `docs/samples/policy-*.yaml` (4 domain)
- `docs/PHASE1_API_CONTRACT.md`

## Kriteria Go/No-Go ke Tahap 2
- Semua kontrak data valid secara skema.
- Tidak ada ambiguitas fallback.
- Minimal 3 test case per use case: allow/warn/quarantine/deny.
- Owner architecture menandatangani keputusan akhir.
- Semua tim paham alur data dan lokasi failure handling.
