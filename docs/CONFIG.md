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


