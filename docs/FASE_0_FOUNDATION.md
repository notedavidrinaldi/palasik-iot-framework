# Fase 0 — PALASIK Baseline (Kick-off)

Dokumen ini menetapkan baseline eksekusi **Fase 0 (1–2 hari)** agar fase 1–4 bisa dimulai tanpa ambiguitas.

## 1) Scope Fase 0 (Disepakati)
- Menyetujui kebutuhan minimum yang harus ada sebelum fitur fase 1 diluncurkan.
- Menyiapkan kontrak payload dan policy agar semua tim (core, ops, test, dan docs) sevisi.
- Menetapkan aturan mutu minimum yang harus lulus sebelum PR masuk staging.
- Menyediakan template `config.yaml` yang memuat metadata baseline.

## 2) Cakupan & Batasan
### Included
- Kontrak **Event v1** (JSON standard).
- Kontrak **Policy v1** (YAML/JSON policy representation).
- Checklist migrasi/checkpoint siap pakai (termasuk `make migration-check`).
- Kebijakan default-deny dinyatakan `true` pada baseline.
- Setiap keputusan DENY harus disertai `reason_code`.

### Not Included (Fase 0)
- CLI command baru selain `init`, `run` sudah ada.
- Simulator/dry-run dan lint policy.
- Status endpoint, metrics dashboard, rollback kebijakan.
- Alerting dan policy audit trail aktif.

## 3) Kontrak Event v1 (JSON)
Minimal payload event yang didukung di PALASIK Phase 1+:

```json
{
  "version": "1",
  "event_id": "evt-01H8K1N9PZ...",
  "timestamp": "2026-07-01T10:20:00Z",
  "type": "sensor.sample",
  "topic": "palasik/sensor/temp",
  "source": {
    "device_id": "edge-sensor-01",
    "ip": "192.168.1.10",
    "protocol": "mqtt"
  },
  "value": 42.0,
  "metadata": {
    "tenant": "pilot-a",
    "location": "factory-1"
  }
}
```

### Field Wajib Event v1
1. `version` — versi kontrak event, wajib `"1"`.
2. `event_id` — string unik untuk audit.
3. `timestamp` — `ISO 8601` UTC.
4. `type` — event type (string).
5. `source.device_id` — identitas device.
6. `source.ip` — alamat sumber.

### Field Opsional Event v1
- `topic`, `value`, `metadata`, `raw`, `challenge_passed`.

### Aturan Validasi Fase 0
- JSON harus valid.
- `timestamp` parseable ISO-8601 UTC.
- Nilai numerik pada `value` harus numeric.

Skema mesin validasi dapat dimuat dari:
- [`docs/schemas/event-v1.schema.json`](docs/schemas/event-v1.schema.json)

## 4) Kontrak Policy v1 (YAML)
Minimal schema policy yang distandarkan untuk fase berikutnya:

```yaml
version: 1
policy_id: palasik-baseline
default_deny: true
actions: [ALLOW, MONITOR, RESTRICT, CHALLENGE, QUARANTINE, DENY]
default_action: DENY
rules:
  - id: deny_unknown_device
    action: DENY
    reason_code: UNKNOWN_DEVICE
    priority: 100
    condition:
      op: equals
      key: source.device_id
      value: unknown

  - id: allow_trusted_device
    action: ALLOW
    reason_code: TRUSTED_DEVICE
    priority: 10
    condition:
      op: gte
      key: trust_score
      value: 0.75
```

### Field Wajib Rule v1
- `id`
- `action`
- `reason_code`
- `condition`

### Aturan Validasi Fase 0
- `default_deny` **harus** bernilai `true`.
- Jika tidak ada rule yang match, engine fallback ke `default_action`.
- `action` diseragamkan dari enum Decision PALASIK.
- Semua deny harus punya `reason_code` (dipersiapkan lint-policy fase berikutnya).

Skema mesin validasi dapat dimuat dari:
- [`docs/schemas/policy-v1.schema.json`](docs/schemas/policy-v1.schema.json)

## 5) Checklist Sukses Fase 0
1. `make migration-check` jalan sukses.
2. Tim menyetujui `event schema v1` dan `policy v1`.
3. File `palasik init` menghasilkan template dengan `policy.version` + `default_deny`.
4. Kontrak reason-code dipahami sebagai wajib untuk deny.
5. Tidak ada perubahan API besar yang menghalangi fase 1.

## 6) Hasil Wajib yang Tersimpan di Repo
- Dokumen kontrak: Event v1 + Policy v1.
- Skema validasi machine-readable (.json).
- Checklist fase 0 tersimpan dan dipakai sebagai acuan PR awal.
- Template onboarding (`palasik init`) siap pakai.

## 7) Task Board Fase 0 (Siap Dieksekusi)

### To Do
- [ ] Final approval: checklist fitur prioritas P0 dan urutan implementasi fase 1–4 (Owner: Lead).
- [ ] Finalisasi schema field wajib event v1 (Owner: Engineering).
- [ ] Finalisasi schema field wajib policy v1 (Owner: Security + Engineering).
- [ ] Tambahkan `policy.version` dan `default_deny` pada template onboarding (Owner: CLI Owner).
- [ ] Sinkronisasi dokumen PR checklist dan migrasi gate (Owner: Contributor Ops).

### Doing
- [ ] Menyusun contoh event/policy minimal di repo (Owner: Security).

### Done
- [x] Membuat baseline dokumen Fase 0 (`FASE_0_FOUNDATION.md`).
- [x] Menyediakan JSON schema untuk `event` dan `policy` v1.
- [x] Menghubungkan schema ke dokumen referensi (`docs/README.md`, `docs/CONFIG.md`).

### Estimasi Waktu (jam)
- Fase 0: 4–6 jam.
- Buffer koreksi lintas-tim: 2 jam.
