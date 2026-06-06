#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v node >/dev/null 2>&1; then
  echo "Missing node"
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "Missing npx"
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Warning: ffmpeg is missing. HyperFrames render and Video Use export will not work."
fi

for project in "$ROOT"/video-projects/*; do
  [ -d "$project" ] || continue
  [ -f "$project/package.json" ] || continue
  echo "Checking $(basename "$project")"
  (cd "$project" && npm run check)
done

