#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Missing python3"
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Missing ffmpeg. Install it with: brew install ffmpeg"
  exit 1
fi

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -U pip
"$VENV/bin/python" -m pip install -r "$ROOT/requirements/local-transcription.txt"

mkdir -p "$ROOT/.cache/whisper"

echo "Local transcription runtime is ready:"
echo "  $VENV/bin/python"
echo ""
echo "Example:"
echo "  .venv/bin/python scripts/transcribe-local-whisper.py examples/<slug>/sources --recursive --edit-dir examples/<slug>/local-whisper --model large --language da --pack"
