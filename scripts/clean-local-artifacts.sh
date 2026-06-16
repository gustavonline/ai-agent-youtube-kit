#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLEAN_FOOTAGE=0
CLEAN_REFERENCES=0

for arg in "$@"; do
  case "$arg" in
    --footage) CLEAN_FOOTAGE=1 ;;
    --references) CLEAN_REFERENCES=1 ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: $0 [--footage] [--references]" >&2
      exit 2
      ;;
  esac
done

rm -rf "$ROOT/.venv" "$ROOT/.cache"
find "$ROOT/scripts" -type d -name "__pycache__" -prune -exec rm -rf {} +

if [ "$CLEAN_FOOTAGE" = "1" ]; then
  shopt -s nullglob dotglob
  for path in "$ROOT"/footage/*; do
    [ "$(basename "$path")" = ".gitkeep" ] && continue
    rm -rf "$path"
  done
fi

if [ "$CLEAN_REFERENCES" = "1" ]; then
  find "$ROOT/channel/references" -type d \( -name "download" -o -name "frames" -o -name "local-whisper" \) -prune -exec rm -rf {} + 2>/dev/null || true
fi

echo "Cleaned repo-local runtime artifacts."
if [ "$CLEAN_FOOTAGE" = "1" ]; then
  echo "Cleaned ignored footage artifacts."
fi
if [ "$CLEAN_REFERENCES" = "1" ]; then
  echo "Cleaned ignored reference analysis artifacts."
fi
