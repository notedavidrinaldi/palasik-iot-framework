#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="palasik"
INSTALL_ROOT="/opt/palasik"
ETC_DIR="/etc/palasik"
STATE_DIR="/var/lib/palasik/runs"
LOG_DIR="/var/log/palasik"
SERVICE_USER="palasik"
SERVICE_GROUP="palasik"
CONFIG_SOURCE="/Users/davidrinaldi/Documents/PROJECT-DAVID/palasik-iot-framework/config.yaml"
ENV_SOURCE="/Users/davidrinaldi/Documents/PROJECT-DAVID/palasik-iot-framework/deploy/systemd/rendered/palasik.env"
SERVICE_SOURCE="/Users/davidrinaldi/Documents/PROJECT-DAVID/palasik-iot-framework/deploy/systemd/rendered/palasik.service"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Script ini harus dijalankan sebagai root (sudo)." >&2
  exit 1
fi

if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
  useradd --system --home "$INSTALL_ROOT" --shell /usr/sbin/nologin "$SERVICE_USER"
fi

mkdir -p "$INSTALL_ROOT" "$ETC_DIR" "$STATE_DIR" "$LOG_DIR"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_ROOT" "$STATE_DIR" "$LOG_DIR"

cp "$CONFIG_SOURCE" "$ETC_DIR/config.yaml"
cp "$ENV_SOURCE" "$ETC_DIR/$SERVICE_NAME.env"
cp "$SERVICE_SOURCE" "/etc/systemd/system/$SERVICE_NAME.service"

chmod 640 "$ETC_DIR/config.yaml" "$ETC_DIR/$SERVICE_NAME.env"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME.service"

echo "Bundle systemd terpasang."
echo "Lanjutkan dengan:"
echo "  python3 -m palasik.cli.main check-startup --config $ETC_DIR/config.yaml --host 0.0.0.0 --port 8080"
echo "  systemctl start $SERVICE_NAME.service"
echo "  systemctl status $SERVICE_NAME.service"
