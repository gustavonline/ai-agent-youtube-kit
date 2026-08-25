#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
VENV="$ROOT/.venv"
WHISPER_CACHE_DIR="${ACS_WHISPER_CACHE_DIR:-$ROOT/workspace/engine/.cache/whisper}"

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
"$VENV/bin/python" -m pip install -r "$ROOT/workspace/engine/requirements/local-transcription.txt"

mkdir -p "$WHISPER_CACHE_DIR"

echo "Local transcription runtime is ready:"
echo "  $VENV/bin/python"
echo "  Whisper model cache: $WHISPER_CACHE_DIR"
echo ""
echo "Example:"
echo "  .venv/bin/python workspace/engine/scripts/transcribe-local-whisper.py workspace/productions/<slug>/sources --recursive --edit-dir workspace/productions/<slug>/local-whisper --model large --language da --pack"
