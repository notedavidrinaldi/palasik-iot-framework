#!/usr/bin/env bash
set -euo pipefail

OWNER="notedavidrinaldi"
REPO="palasik-iot-framework"
FILE="docs/GOOD_FIRST_ISSUES.md"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) tidak ditemukan. Install gh dulu dan login."
  exit 1
fi

if ! gh auth status >/tmp/gh_auth_status.txt 2>&1; then
  echo "Belum login gh. Jalankan: gh auth login"
  cat /tmp/gh_auth_status.txt
  exit 1
fi

# Daftar title dan body singkat
issues=(
  "docs: perbaiki typo kecil dan konsistensi istilah PALASIK|Perbaiki typo kecil dan konsistensi istilah di README/docs.|docs/GOOD_FIRST_ISSUES.md"
  "docs: tambah contoh event simulate untuk sensor temperatur|Tambahkan contoh sample event untuk simulasi sensor temperatur.|docs/GOOD_FIRST_ISSUES.md"
  "docs: contoh hasil output status dalam format JSON|Tambahkan contoh output status JSON dan cara bacanya.|docs/GOOD_FIRST_ISSUES.md"
  "docs: buat cheatsheet perintah operasi harian|Buat cheat sheet command check/status/simulate/deploy check untuk operator.|docs/GOOD_FIRST_ISSUES.md"
  "docs: tambah troubleshooting issue paling umum|Tambahkan 3+ troubleshooting paling umum saat check/run/simulate gagal.|docs/GOOD_FIRST_ISSUES.md"
  "docs: tambah catatan praktis konfigurasi MQTT adapter|Tambahkan panduan singkat konfigurasi MQTT adapter + contoh publish.|docs/GOOD_FIRST_ISSUES.md"
  "docs: tambahkan badge komunitas dan kontribusi|Tambahkan badge komunitas/stats/kontribusi di README.|docs/GOOD_FIRST_ISSUES.md"
  "docs: rapikan checklist pertumbuhan komunitas|Rapiin checklist 30 hari dan target pertumbuhan.|docs/GOOD_FIRST_ISSUES.md"
  "docs: tambah template ringkas untuk kontribusi dokumentasi|Buat template issue/pull request untuk kontribusi docs.|docs/GOOD_FIRST_ISSUES.md"
  "docs: audit link rusak di dokumentasi|Audit dan perbaiki tautan rusak yang ditemukan di dokumentasi utama.|docs/GOOD_FIRST_ISSUES.md"
)

for item in "${issues[@]}"; do
  IFS='|' read -r title body source <<<"$item"
  if gh issue list --repo "$OWNER/$REPO" --search "$title in:title" --state open --json title --jq '.[] .title' | rg -q "^${title}$"; then
    echo "⏭ issue exists: $title"
    continue
  fi

  body_text=$(cat <<EOF2
## Latar Belakang
$body

## Scope
- [x] Dokumentasi
- [ ] Code

## Definisi Sukses
- Penyesuaian ini tidak mengganggu fungsi inti.
- PR mudah direview.

## Referensi
Source: $source
EOF2
)

  gh issue create \
    --repo "$OWNER/$REPO" \
    --title "$title" \
    --body "$body_text" \
    --label "good first issue,area:docs"

  echo "✅ created: $title"
done

