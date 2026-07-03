#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI (gh) is required." >&2
  echo "Install: https://cli.github.com/" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required." >&2
  exit 1
fi

BRANCH="staging"
DRYRUN="false"

for arg in "$@"; do
  case "$arg" in
    --branch=*)
      BRANCH="${arg#*=}"
      ;;
    --dry-run)
      DRYRUN="true"
      ;;
    -h|--help)
      echo "Usage: $0 [--branch=<branch>] [--dry-run]"
      echo "Defaults: --branch=staging"
      exit 0
      ;;
  esac
done

if REPO_JSON=$(gh repo view --json owner,name -q '{"owner": .owner.login, "name": .name}' 2>/dev/null); then
  REPO=$(echo "$REPO_JSON" | jq -r '.owner + "/" + .name')
else
  if [[ "$DRYRUN" == "false" ]]; then
    echo "Error: unable to determine repository from GitHub CLI." >&2
    echo "Run inside a git repo with authenticated gh CLI." >&2
    echo "Or provide a local git remote URL with 'git remote get-url origin'." >&2
    exit 1
  fi

  REMOTE_URL="$(git remote get-url origin 2>/dev/null || true)"
  if [[ -z "$REMOTE_URL" ]]; then
    echo "Error: unable to determine repository from GitHub CLI or git remote origin." >&2
    exit 1
  fi
  if [[ "$REMOTE_URL" == git@github.com:* ]]; then
    REMOTE_PATH="${REMOTE_URL#git@github.com:}"
  elif [[ "$REMOTE_URL" == https://github.com/* ]]; then
    REMOTE_PATH="${REMOTE_URL#https://github.com/}"
  elif [[ "$REMOTE_URL" == http://github.com/* ]]; then
    REMOTE_PATH="${REMOTE_URL#http://github.com/}"
  else
    echo "Error: unsupported git remote format: $REMOTE_URL" >&2
    exit 1
  fi
  REMOTE_PATH="${REMOTE_PATH%.git}"
  REMOTE_PATH="${REMOTE_PATH#/}"
  REPO="${REMOTE_PATH}"
fi

CHECK_NAME="migration-gate"

PAYLOAD="$(cat <<'PAYLOAD'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["migration-gate"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true,
  "lock_branch": false
}
PAYLOAD
)"

if [[ "$DRYRUN" == "true" ]]; then
  echo "Repository: $REPO"
  echo "Target branch: $BRANCH"
  echo "Required check: $CHECK_NAME"
  echo "$PAYLOAD" | jq .
  exit 0
fi

gh api \
  --method PATCH /repos/$REPO/branches/$BRANCH/protection \
  --header "Accept: application/vnd.github+json" \
  --input <(echo "$PAYLOAD")

echo "Branch protection for $REPO@$BRANCH updated."
echo "Ensured required check: $CHECK_NAME"
