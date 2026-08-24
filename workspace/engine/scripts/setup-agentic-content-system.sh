#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Missing python3. Install Python 3.10 or newer." >&2
  exit 1
fi

python3 -m venv .venv
"$ROOT/.venv/bin/python" -m pip install -e .
"$ROOT/.venv/bin/python" -m agentic_content_system --help
echo "Agentic Content System setup is ready."
