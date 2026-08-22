#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -d "$ROOT/engine/motion-adapters" ]; then
  echo "Missing engine/motion-adapters boundary." >&2
  exit 1
fi

for adapter in "$ROOT"/video-projects/*; do
  [ -d "$adapter" ] || continue
  [ -f "$adapter/package.json" ] || continue
  echo "Checking optional motion adapter $(basename "$adapter")"
  (cd "$adapter" && npm run check)
done
