
---

## 📄 `docs/CONCEPTS.md`

```md
# Core Concepts in PALASIK

Dokumen ini menjelaskan konsep inti
yang menjadi fondasi desain PALASIK.

---

## 🔐 Zero Trust

PALASIK menerapkan prinsip:

> **Never trust, always verify**

Tidak ada event atau device yang dipercaya
hanya karena berada di jaringan internal.

---

## 📦 Event

Event adalah representasi standar
dari data yang diterima sistem.

Contoh event:
```json
{
  "value": 42,
  "timestamp": 1710000000,
  "source": "sensor-01"
}
```

## 🔍 Trust Score

Trust score adalah nilai numerik:

- Rentang: 0.0 – 1.0

- Semakin tinggi → semakin dipercaya

Trust bukan keputusan, hanya sinyal evaluasi.

## ⚖️ Policy Decision

Policy mengubah trust score menjadi keputusan eksplisit.

Trust Score	Decision
≥ threshold	ALLOW
< threshold	DENY

