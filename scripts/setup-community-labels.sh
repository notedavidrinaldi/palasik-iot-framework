#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) tidak ditemukan. Install gh lalu login sebelum lanjut."
  exit 1
fi

if ! gh auth status >/tmp/gh_auth_status.txt 2>&1; then
  echo "Belum login ke GitHub CLI. Jalankan: gh auth login"
  cat /tmp/gh_auth_status.txt
  exit 1
fi

OWNER="notedavidrinaldi"
REPO="palasik-iot-framework"

labels=(
  "good first issue|8FEECE|Tugas sangat cocok untuk kontributor baru"
  "help wanted|0E8A16|Membutuhkan kontribusi komunitas"
  "question|D876E3|Pertanyaan atau clarification dari user"
  "area:docs|A2EEEF|Pekerjaan terkait dokumentasi"
  "area:plugin|FBCA04|Pekerjaan terkait plugin PALASIK"
  "area:policy|D4C5F9|Pekerjaan terkait trust/policy engine"
  "discussion-needed|5319E7|Butuh diskusi komunitas sebelum eksekusi"
)

for entry in "${labels[@]}"; do
  IFS='|' read -r name color description <<<"$entry"
  if gh label list --repo "$OWNER/$REPO" --json name --jq '.[] .name' | rg -q "^$name$"; then
    echo "⏭ label exists: $name"
  else
    gh label create "$name" --repo "$OWNER/$REPO" --color "$color" --description "$description"
    echo "✅ created: $name"
  fi

done

echo "Selesai. Cek di Settings > Labels"
