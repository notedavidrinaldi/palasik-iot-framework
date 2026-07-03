#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${1:-config.yaml}"
HOST="${PALASIK_SMOKE_HOST:-127.0.0.1}"
PORT="${PALASIK_SMOKE_PORT:-18080}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
BASE_URL="http://${HOST}:${PORT}"
TMP_DIR="${TMPDIR:-/tmp}"
HEALTH_FILE="${TMP_DIR}/palasik-health-${PORT}.json"
HEALTH_CODE_FILE="${TMP_DIR}/palasik-health-code-${PORT}.txt"
DISPATCH_FILE="${TMP_DIR}/palasik-dispatch-${PORT}.json"
AUDIT_FILE="${TMP_DIR}/palasik-audit-${PORT}.json"
METRICS_FILE="${TMP_DIR}/palasik-metrics-${PORT}.json"
INVALID_CONFIG_PATH="${TMP_DIR}/palasik-invalid-${PORT}.yaml"

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]]; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT

"${PYTHON_BIN}" -m palasik.cli.main check-startup --config "${CONFIG_PATH}" --host "${HOST}" --port "${PORT}" --allow-relative-paths
"${PYTHON_BIN}" -m palasik.cli.main serve-api --config "${CONFIG_PATH}" --host "${HOST}" --port "${PORT}" >/dev/null 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 30); do
  if curl --silent --show-error -o "${HEALTH_FILE}" -w "%{http_code}" "${BASE_URL}/health" >"${HEALTH_CODE_FILE}"; then
    break
  fi
  sleep 0.5
done

curl --silent --show-error -o "${HEALTH_FILE}" -w "%{http_code}" "${BASE_URL}/health" >"${HEALTH_CODE_FILE}"
curl --fail --silent \
  -H "Content-Type: application/json" \
  -d '{"actions":["local_smoke"],"event":{"type":"manual.dispatch","source":{"device_id":"ops-console","ip":"127.0.0.1"},"value":1}}' \
  "${BASE_URL}/dispatch" >"${DISPATCH_FILE}"
curl --fail --silent "${BASE_URL}/audit?limit=5" >"${AUDIT_FILE}"
curl --fail --silent "${BASE_URL}/metrics" >"${METRICS_FILE}"

"${PYTHON_BIN}" - "${CONFIG_PATH}" "${INVALID_CONFIG_PATH}" <<'PY'
import sys
import yaml

config_path, invalid_config_path = sys.argv[1:]
with open(config_path, encoding="utf-8") as handle:
    payload = yaml.safe_load(handle)

payload["palasik"]["policy"]["default_deny"] = False
with open(invalid_config_path, "w", encoding="utf-8") as handle:
    yaml.safe_dump(payload, handle)
PY

if "${PYTHON_BIN}" -m palasik.cli.main check-startup --config "${INVALID_CONFIG_PATH}" --host "${HOST}" --port "${PORT}" --allow-relative-paths >/dev/null 2>&1; then
  echo "[PALASIK] smoke-serve-api: FAIL - invalid config unexpectedly passed check-startup" >&2
  exit 1
fi

"${PYTHON_BIN}" - "${HEALTH_FILE}" "${HEALTH_CODE_FILE}" "${DISPATCH_FILE}" "${AUDIT_FILE}" "${METRICS_FILE}" <<'PY'
import json
import sys

health_path, health_code_path, dispatch_path, audit_path, metrics_path = sys.argv[1:]
health = json.load(open(health_path, encoding="utf-8"))
health_code = int(open(health_code_path, encoding="utf-8").read().strip())
dispatch = json.load(open(dispatch_path, encoding="utf-8"))
audit = json.load(open(audit_path, encoding="utf-8"))
metrics = json.load(open(metrics_path, encoding="utf-8"))

assert health["status"] in {"UP", "DEGRADED", "DOWN"}, health
expected_health_code = 503 if health["status"] == "DOWN" else 200
assert health_code == expected_health_code, (health_code, health)
assert dispatch["status"] == "OK", dispatch
assert dispatch["results"], dispatch
assert audit["count"] >= 1, audit
assert metrics["status"] == "OK", metrics

print("[PALASIK] smoke-serve-api: PASS")
print(json.dumps(
    {
        "health_http_code": health_code,
        "health_status": health["status"],
        "dispatch_results": dispatch["results"],
        "audit_count": audit["count"],
        "events_total": metrics["metrics"].get("events_total"),
        "actions_total": metrics["metrics"].get("actions_total"),
    },
    indent=2,
    sort_keys=True,
))
PY
