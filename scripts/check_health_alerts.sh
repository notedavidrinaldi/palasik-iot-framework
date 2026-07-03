#!/usr/bin/env bash
set -euo pipefail

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required." >&2
  exit 3
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required." >&2
  exit 3
fi

BASE_URL="${PALASIK_BASE_URL:-http://${PALASIK_HOST:-127.0.0.1}:${PALASIK_PORT:-8080}}"
HEALTH_URL="${BASE_URL}/health"
METRICS_URL="${BASE_URL}/metrics"
MAX_ATTEMPTS="${PALASIK_HEALTH_RETRIES:-10}"
SLEEP_SECONDS="${PALASIK_HEALTH_RETRY_SLEEP:-0.5}"
STRICT_UP_ONLY="${PALASIK_HEALTH_STRICT_UP_ONLY:-0}"

fetch_with_retry() {
  local url="$1"
  local attempt=1
  local output=""

  while [[ "${attempt}" -le "${MAX_ATTEMPTS}" ]]; do
    if output="$(curl --silent --show-error "${url}" 2>/dev/null)"; then
      printf '%s' "${output}"
      return 0
    fi
    if [[ "${attempt}" -lt "${MAX_ATTEMPTS}" ]]; then
      sleep "${SLEEP_SECONDS}"
    fi
    attempt=$((attempt + 1))
  done

  return 1
}

if ! health_payload="$(fetch_with_retry "${HEALTH_URL}")"; then
  echo "[PALASIK] health-alerts"
  jq -n \
    --arg status "UNREACHABLE" \
    --arg url "${HEALTH_URL}" \
    --arg retries "${MAX_ATTEMPTS}" \
    '{
      status: $status,
      message: "Health endpoint is not reachable",
      endpoint: $url,
      retries: ($retries | tonumber)
    }'
  exit 4
fi

if ! metrics_payload="$(fetch_with_retry "${METRICS_URL}")"; then
  echo "[PALASIK] health-alerts"
  jq -n \
    --arg status "UNREACHABLE" \
    --arg url "${METRICS_URL}" \
    --arg retries "${MAX_ATTEMPTS}" \
    '{
      status: $status,
      message: "Metrics endpoint is not reachable",
      endpoint: $url,
      retries: ($retries | tonumber)
    }'
  exit 4
fi

summary_json="$(
  jq -n \
    --argjson health "${health_payload}" \
    --argjson metrics_payload "${metrics_payload}" \
    '
    {
      status: $health.status,
      health_http_mode_hint: (if $health.status == "DOWN" then 503 else 200 end),
      status_since_utc: $health.health.status_since_utc,
      last_transition_utc: $health.health.last_transition_utc,
      last_reason: $health.health.last_reason,
      transition_count: $health.health.transition_count,
      latest_retry_issue: $health.actions.latest_retry_issue,
      failed_action_rate: $metrics_payload.metrics.failed_action_rate,
      actions_total: $metrics_payload.metrics.actions_total,
      actions_failed: $metrics_payload.metrics.actions_failed,
      alerts: (
        ($metrics_payload.metrics.alerts // [])
        | map(select(.type == "health_down" or .type == "health_degraded" or .type == "failed_action_rate"))
      )
    }
    '
)"

echo "[PALASIK] health-alerts"
echo "${summary_json}" | jq .

critical_count="$(echo "${summary_json}" | jq '[.alerts[] | select(.severity == "critical")] | length')"
warning_count="$(echo "${summary_json}" | jq '[.alerts[] | select(.severity != "critical")] | length')"
status_value="$(echo "${summary_json}" | jq -r '.status')"

if [[ "${STRICT_UP_ONLY}" == "1" && "${status_value}" != "UP" ]]; then
  exit 1
fi

if [[ "${status_value}" == "DOWN" || "${critical_count}" -gt 0 ]]; then
  exit 2
fi

if [[ "${status_value}" == "DEGRADED" || "${warning_count}" -gt 0 ]]; then
  exit 1
fi

exit 0
