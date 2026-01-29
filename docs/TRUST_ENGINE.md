
---

## 📄 `docs/TRUST_ENGINE.md`

```md
# Trust Engine

Trust Engine bertugas menghitung **trust score**
berdasarkan event dan konteks.

---

## 🎯 Tujuan

- Menilai perilaku event
- Menghasilkan skor numerik
- Tidak mengambil keputusan akhir

---

## 🧱 Interface Dasar

```python
class TrustEvaluator:
    def evaluate(self, event: dict, context) -> float:
        ...
```

## 📌 Contoh Implementasi
```python
class SimpleTrustEvaluator(TrustEvaluator):
    def evaluate(self, event, context):
        value = event.get("value", 0)
        return 0.9 if value <= 100 else 0.2
```


