
---

## 📄 `docs/POLICY_ENGINE.md`

```md
# Policy Engine

Policy Engine mengubah trust score
menjadi keputusan eksplisit.

---

## 🎯 Filosofi

- Policy harus eksplisit
- Tidak ada implicit allow
- Mudah diaudit & diuji

---

## 🧱 Allow / Deny Policy

```python
from palasik.policy.allow_deny import AllowDenyPolicy

policy = AllowDenyPolicy(threshold=0.7)
policy.decide(0.9, {}, None)  # ALLOW
policy.decide(0.2, {}, None)  # DENY
```
