# Deploy Edge PALASIK

Dokumen ini adalah draft awal Tahap 4 untuk Raspberry Pi atau host edge Linux lain.

## Tujuan

- Menjalankan API PALASIK sebagai service `systemd`
- Menyimpan audit dan metrics secara persisten
- Memisahkan config file dan env vars operasional
- Menahan kegagalan jaringan lokal dengan retry yang terukur

## Struktur yang disarankan

```text
/opt/palasik/                     # source + virtualenv
/etc/palasik/config.yaml          # config operasional
/etc/palasik/palasik.env          # env vars dan tuning runtime
/var/lib/palasik/runs/            # metrics.json, audit.jsonl, snapshot
/var/log/palasik/palasik.log      # log runtime
```

## Env vars operasional

Contoh awal tersedia di [deploy/systemd/palasik.env.example](/Users/davidrinaldi/Documents/PROJECT-DAVID/palasik-iot-framework/deploy/systemd/palasik.env.example:1).

Field yang biasanya diisi saat deployment nyata:

- `PALASIK_BROKER_HOST`, `PALASIK_BROKER_PORT`
- `PALASIK_METRICS_FILE`, `PALASIK_AUDIT_LOG`
- `PALASIK_ACTION_TIMEOUT`
- `PALASIK_ACTION_MAX_RETRIES`
- `PALASIK_ACTION_RETRY_BACKOFF_SECONDS`
- threshold risk dan event age sesuai profil lapangan

Di `config.yaml`, tetapkan juga mode health yang diinginkan:

```yaml
palasik:
  observability:
    alert:
      failed_action_rate_threshold: 0.5
      health_degraded_for_seconds: 60
      health_down_for_seconds: 0
  health:
    degraded_http_mode: ok   # pakai fail jika load balancer harus menganggap degraded = unavailable
```

Token rahasia seperti webhook bearer token, Telegram bot token, dan relay key tetap sebaiknya disimpan di `/etc/palasik/config.yaml` dengan permission ketat atau di secret manager lokal jika tersedia.

## Service systemd

Contoh unit ada di [deploy/systemd/palasik.service](/Users/davidrinaldi/Documents/PROJECT-DAVID/palasik-iot-framework/deploy/systemd/palasik.service:1).

Perilaku utamanya:

- menunggu `network-online.target`
- menjalankan `check-startup` sebelum proses utama start
- restart otomatis jika proses mati
- memuat env vars dari `/etc/palasik/palasik.env`
- menulis log ke `/var/log/palasik/palasik.log`

Untuk merender bundle install yang siap dipindahkan ke host edge:

```bash
python3 -m palasik.cli.main install-systemd --config-source config.yaml
```

Output default akan muncul di `deploy/systemd/rendered/`:

- `palasik.service`
- `palasik.env`
- `install_palasik_systemd.sh`

Script install tersebut sengaja berisi langkah `systemctl daemon-reload`, `enable`, dan copy file agar bootstrap di host target tidak perlu edit manual berulang.

## Langkah bootstrap Raspberry Pi

1. Siapkan user dan direktori:
   ```bash
   sudo useradd --system --home /opt/palasik --shell /usr/sbin/nologin palasik
   sudo mkdir -p /opt/palasik /etc/palasik /var/lib/palasik/runs /var/log/palasik
   sudo chown -R palasik:palasik /opt/palasik /var/lib/palasik /var/log/palasik
   ```
2. Salin source ke `/opt/palasik`, lalu buat virtualenv:
   ```bash
   cd /opt/palasik
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
3. Salin `config.yaml` dan `palasik.env`:
   ```bash
   sudo cp config.yaml /etc/palasik/config.yaml
   sudo cp deploy/systemd/palasik.env.example /etc/palasik/palasik.env
   sudo chmod 640 /etc/palasik/config.yaml /etc/palasik/palasik.env
   ```
4. Pasang unit service:
   ```bash
   python3 -m palasik.cli.main install-systemd --config-source config.yaml
   sudo bash deploy/systemd/rendered/install_palasik_systemd.sh
   sudo systemctl start palasik.service
   ```
5. Verifikasi:
   ```bash
   python3 -m palasik.cli.main check-startup --config /etc/palasik/config.yaml --host 0.0.0.0 --port 8080
   systemctl status palasik.service
   curl -s http://127.0.0.1:8080/health
   tail -f /var/log/palasik/palasik.log
   ```

## Smoke test lokal sebelum ke Raspberry Pi

Jalankan smoke suite minimal berikut di laptop atau VM Linux sebelum source dipindahkan ke host edge:

```bash
make edge-smoke
```

Script ini akan:

- memanggil `check-startup`
- menyalakan `serve-api` sementara
- memeriksa `/health` beserta HTTP status-nya
- mengirim `POST /dispatch`
- membaca `/audit` dan `/metrics`
- memastikan config rusak benar-benar gagal di `check-startup`

Jika ingin menjalankan manual:

```bash
bash scripts/smoke_serve_api.sh examples/mqtt_zero_trust_gateway/config.yaml
```

## Handling gangguan jaringan lokal

Kontrak health final:

- `UP` -> HTTP `200`
- `DEGRADED` -> HTTP `200` pada mode default `degraded_http_mode: ok`
- `DEGRADED` -> HTTP `503` jika `degraded_http_mode: fail`
- `DOWN` -> HTTP `503`

Pemisahan failure:

- `check-startup` fail-fast untuk config invalid, bind host/port bermasalah, route penting ke adapter tidak aktif, endpoint adapter aktif rusak, atau path wajib tidak writable.
- `GET /health` melaporkan degradasi runtime yang muncul setelah service hidup.

Field health yang penting untuk on-call:

- `health.status_since_utc`
- `health.last_transition_utc`
- `health.transition_count`
- `health.last_reason`

Alert dasar yang perlu disiapkan di dashboard/monitor:

- `health_down`
- `health_degraded`
- `failed_action_rate`

Panel minimum yang layak ada di dashboard edge:

- status health saat ini
- sejak kapan status itu aktif
- jumlah transisi health
- failed action rate
- retry issue terakhir

Query cepat untuk verifikasi di host target:

```bash
curl -s http://127.0.0.1:8080/health | jq '{status, health, latest_retry_issue: .actions.latest_retry_issue}'
```

```bash
curl -s http://127.0.0.1:8080/metrics | jq '.metrics | {
  health_status,
  health_transition_count,
  health_status_breakdown,
  failed_action_rate,
  alerts
}'
```

Atau pakai helper script:

```bash
bash scripts/check_health_alerts.sh
make edge-health
make edge-health-wait
make edge-health-strict
make edge-post-restart-check
make edge-post-restart-check-strict
```

Jika endpoint belum bisa dihubungi sama sekali, helper script akan keluar dengan `exit code 4` dan payload `status=UNREACHABLE`.

- Jika target webhook/relay sering timeout, naikkan `PALASIK_ACTION_TIMEOUT` sedikit demi sedikit.
- Gunakan `PALASIK_ACTION_MAX_RETRIES` dan `PALASIK_ACTION_RETRY_BACKOFF_SECONDS` untuk menahan flapping singkat.
- Pantau `GET /health`:
  - `status=DEGRADED` berarti ada action retry/failure terbaru atau storage runtime sedang bermasalah.
  - `actions.latest_retry_issue` membantu melihat event/action terakhir yang bermasalah.
- Jika jaringan target sedang putus lama, route action non-kritis bisa sementara diarahkan ke `logger` agar tidak memicu aksi lapangan yang salah.

## Checklist sebelum rollout edge

- `pytest` target Tahap 3 lulus
- `/health` menunjukkan path writable
- route action penting punya adapter aktif
- audit dan metrics tersimpan di storage persisten
- service restart otomatis setelah reboot
