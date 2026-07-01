# DEMIT Super App Architecture

DEMIT adalah kerangka **super app** dengan beberapa aplikasi (app modules) di dalam satu runtime.

## Konsep
- Setiap aplikasi punya lifecycle: `start`, `handle_event`, `stop`.
- Runtime men-routing event berdasarkan field `app` atau `route`.
- Aplikasi PALASIK menjadi guard pertama untuk event IoT.

## Config contoh (`demit.yaml`)

```yaml
demit:
  apps:
    - palasik

apps:
  palasik:
    type: palasik
    config_file: "config.yaml"
    plugins_path: "plugins"
    routes:
      - palasik
```

Event minimal untuk route ke PALASIK:

```json
{
  "route": "palasik",
  "type": "mqtt",
  "value": 42
}
```

Jika `app` tidak diset dan hanya ada 1 aplikasi, event otomatis ke aplikasi itu.
Jika ada banyak aplikasi, `route` bisa dipakai untuk broadcast terarah ke aplikasi yang cocok.
