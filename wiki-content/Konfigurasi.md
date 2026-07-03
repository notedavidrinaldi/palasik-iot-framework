# Konfigurasi PALASIK

Konfigurasi utama bisa dikelola lewat YAML dan environment variable.

## Contoh minimal

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

## Urutan prioritas

1. Environment variable
2. File YAML
3. Nilai default runtime

## Catatan

- Nilai kunci yang umum: threshold trust/policy, deny spike threshold, plugin yang aktif.
- Lihat dokumentasi konfigurasi lengkap untuk daftar variabel lingkungan.
