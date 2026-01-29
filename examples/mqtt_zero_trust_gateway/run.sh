#!/bin/bash
#!/bin/bash

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[PALASIK] MQTT Zero Trust Gateway"
echo "[PALASIK] Using config: $BASE_DIR/config.yaml"

palasik run --config "$BASE_DIR/config.yaml"
echo "[PALASIK] MQTT Zero Trust Gateway"
echo "[PALASIK] Using config.yaml"

palasik run --config config.yaml
