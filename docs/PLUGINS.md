
---

## 📄 `docs/PLUGINS.md`

```md
# Plugin System

Plugin mengeksekusi aksi
berdasarkan keputusan policy.

---

## 🔌 Tujuan Plugin

- Logging
- Forwarding data
- Alerting
- Integrasi sistem eksternal

---

## 🧱 Interface Dasar

```python
class Plugin:
    def on_event(self, event, decision, context):
        ...
```

## 📌 Contoh Logger Plugin
```python
class LoggerPlugin:
    def on_event(self, event, decision, context):
        print(decision, event)
```


