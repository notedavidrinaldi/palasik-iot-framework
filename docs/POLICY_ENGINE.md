
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

## Rule-Based Policy (Adaptive Enforcement)

Contoh policy DSL:

```yaml
palasik:
  policy:
    type: rule
    default_action: DENY
    rules:
      - name: suspicious_payload
        when:
          event_value_gt: 100
        action: RESTRICT
      - name: low_trust
        when:
          trust_below: 0.2
        action: QUARANTINE
```

Decision yang didukung: `ALLOW`, `MONITOR`, `RESTRICT`, `CHALLENGE`, `QUARANTINE`, `DENY`.

Contoh CHALLENGE:

```yaml
palasik:
  policy:
    type: rule
    default_action: DENY
    rules:
      - name: new device pattern
        when:
          trust_below_eq: 0.6
        action: CHALLENGE
```

Jika engine menerima event dengan `challenge_passed: true`, keputusan akan naik menjadi `ALLOW`.
