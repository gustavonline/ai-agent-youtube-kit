#!/usr/bin/env bash
set -euo pipefail

# Historical compatibility name. ACS productions are the canonical content
# boundary; curated examples and retained HyperFrames migration/recovery inputs
# are checked separately.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PYTHON="${ACS_PYTHON:-$ROOT/.venv/bin/python}"
if [ ! -x "$PYTHON" ]; then
  PYTHON="$(command -v python3 || true)"
fi
if [ -z "$PYTHON" ]; then
  echo "Missing Python 3; create .venv or set ACS_PYTHON." >&2
  exit 1
fi

found_production=0
for production in "$ROOT"/workspace/productions/*; do
  [ -d "$production" ] || continue
  [ -f "$production/brand.json" ] || continue
  found_production=1
  echo "Validating ACS production $(basename "$production")"
  "$PYTHON" -m agentic_content_system validate "$production" --contracts-only
done

if [ "$found_production" = "0" ]; then
  echo "No ACS productions found; use workspace/engine/scripts/new-content-example.py <slug>."
fi

if command -v node >/dev/null 2>&1 && command -v npx >/dev/null 2>&1; then
  "$ROOT/workspace/engine/scripts/check-motion-adapters.sh"
else
  echo "Skipping retained HyperFrames migration/recovery checks (node/npx not installed)."
fi
