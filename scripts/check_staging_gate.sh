#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI (gh) is required." >&2
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required." >&2
  exit 1
fi

BRANCH="staging"

for arg in "$@"; do
  case "$arg" in
    --branch=*)
      BRANCH="${arg#*=}"
      ;;
    -h|--help)
      echo "Usage: $0 [--branch=<branch>]"
      echo "Defaults: --branch=staging"
      exit 0
      ;;
  esac
done

if ! REPO_JSON=$(gh repo view --json owner,name -q '{"owner": .owner.login, "name": .name}'); then
  echo "Error: unable to access repository context via GitHub CLI." >&2
  echo "Run 'gh auth login' or set GH_TOKEN with repo scope." >&2
  exit 4
fi
REPO=$(echo "$REPO_JSON" | jq -r '.owner + "/" + .name')
CHECK_NAME="migration-gate"

if [[ -z "$REPO" || "$REPO" == "/" ]]; then
  echo "Error: unable to determine repository from gh context." >&2
  exit 1
fi

if ! PROTECTION=$(gh api /repos/$REPO/branches/$BRANCH/protection --jq '.required_status_checks.contexts'); then
  echo "Error: failed to query branch protection for '$BRANCH' in '$REPO'." >&2
  echo "Run 'gh auth login' or set GH_TOKEN with repo scope." >&2
  exit 4
fi

if [[ "$PROTECTION" == "null" ]]; then
  echo "[migration-check] branch protection for '$BRANCH' is not enforcing required status checks."
  echo "Status: NOT_ENFORCED"
  exit 2
fi

HAS_CHECK=$(echo "$PROTECTION" | jq --arg chk "$CHECK_NAME" 'index($chk)')

if [[ "$HAS_CHECK" == "null" ]]; then
  echo "[migration-check] '$CHECK_NAME' is NOT required on branch '$BRANCH'."
  echo "Current required checks:"
  echo "$PROTECTION"
  echo "Status: NOT_ENFORCED"
  exit 3
fi

echo "[migration-check] '$CHECK_NAME' is required on branch '$BRANCH'."
echo "Status: OK"
