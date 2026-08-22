#!/usr/bin/env bash
set -euo pipefail

# Historical compatibility name. ACS examples are the canonical content
# boundary; HyperFrames workspaces are checked separately as optional adapters.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${ACS_PYTHON:-$ROOT/.venv/bin/python}"
if [ ! -x "$PYTHON" ]; then
  PYTHON="$(command -v python3 || true)"
fi
if [ -z "$PYTHON" ]; then
  echo "Missing Python 3; create .venv or set ACS_PYTHON." >&2
  exit 1
fi

found_example=0
for example in "$ROOT"/examples/*; do
  [ -d "$example" ] || continue
  [ -f "$example/brand.json" ] || continue
  found_example=1
  echo "Validating ACS example $(basename "$example")"
  "$PYTHON" -m agentic_content_system validate "$example" --contracts-only
done

if [ "$found_example" = "0" ]; then
  echo "No ACS examples found; use scripts/new-content-example.py <slug>."
fi

if command -v node >/dev/null 2>&1 && command -v npx >/dev/null 2>&1; then
  "$ROOT/scripts/check-motion-adapters.sh"
else
  echo "Skipping optional HyperFrames checks (node/npx not installed)."
fi
