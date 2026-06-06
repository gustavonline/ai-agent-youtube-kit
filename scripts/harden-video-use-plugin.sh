#!/usr/bin/env bash
set -euo pipefail

PLUGIN_ROOT="${1:-$HOME/plugins/video-use}"
SKILL_FILE="$PLUGIN_ROOT/skills/video-use/SKILL.md"

if [ ! -f "$SKILL_FILE" ]; then
  echo "Video Use SKILL.md not found at: $SKILL_FILE"
  echo "Create the local video-use plugin first, then rerun this script."
  exit 1
fi

MARKER_BEGIN="<!-- ai-agent-youtube-kit-local-whisper-policy:start -->"
MARKER_END="<!-- ai-agent-youtube-kit-local-whisper-policy:end -->"

if grep -q "$MARKER_BEGIN" "$SKILL_FILE"; then
  echo "Video Use plugin already has the ai-agent-youtube-kit local Whisper policy."
  exit 0
fi

cat <<'EOF' >> "$SKILL_FILE"

<!-- ai-agent-youtube-kit-local-whisper-policy:start -->
## ai-agent-youtube-kit Local Transcription Policy

When working in an `ai-agent-youtube-kit` repo, local Whisper is the default
transcription workflow.

- Do not require `ELEVENLABS_API_KEY` for normal operation in this repo.
- Do not run `helpers/transcribe.py` or `helpers/transcribe_batch.py` unless the
  user explicitly asks for cloud transcription.
- Use the repo script instead:
  `.venv/bin/python scripts/transcribe-local-whisper.py footage/<slug> --model large --pack`
- For Danish footage, add `--language da`.
- Treat ElevenLabs/Scribe as an explicit opt-in cloud alternative only.

After local transcripts exist, continue using Video Use normally for inventory,
strategy, cut planning, subtitles, grading, render, and self-eval.
<!-- ai-agent-youtube-kit-local-whisper-policy:end -->
EOF

echo "Patched Video Use plugin with ai-agent-youtube-kit local Whisper policy:"
echo "  $SKILL_FILE"
