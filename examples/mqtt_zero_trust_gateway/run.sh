#!/bin/bash

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[PALASIK] MQTT Zero Trust Gateway"
echo "[PALASIK] Using config: $BASE_DIR/config.yaml"
cd "$BASE_DIR" || exit 1
palasik run --config config.yaml
