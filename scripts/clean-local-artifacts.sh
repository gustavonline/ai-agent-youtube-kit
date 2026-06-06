#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

rm -rf "$ROOT/.venv" "$ROOT/.cache"
find "$ROOT/scripts" -type d -name "__pycache__" -prune -exec rm -rf {} +

if [ "${1:-}" = "--footage" ]; then
  shopt -s nullglob dotglob
  for path in "$ROOT"/footage/*; do
    [ "$(basename "$path")" = ".gitkeep" ] && continue
    rm -rf "$path"
  done
fi

echo "Cleaned repo-local runtime artifacts."
if [ "${1:-}" = "--footage" ]; then
  echo "Cleaned ignored footage artifacts."
fi
