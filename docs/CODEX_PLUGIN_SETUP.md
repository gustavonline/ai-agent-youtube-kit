# Optional Codex Tooling

Agentic Content System v0.3 does not require a Codex plugin or an external
editor,
HyperFrames to run its contract/CLI/render/package workflow. Install FFmpeg and
use the Python CLI first.

The existing HyperFrames projects remain useful for optional motion assets. If
an external editor or transcription plugin is deliberately added, keep it as an
adapter: it must consume local contracts, return inspectable files, and never
become a hidden database or required service.

## Local Whisper

The repo's existing local workflow is the supported default for optional
transcription:

```text
./workspace/engine/scripts/setup-local-transcription.sh
.venv/bin/python workspace/engine/scripts/transcribe-local-whisper.py workspace/productions/<slug>/sources --recursive --edit-dir workspace/productions/<slug>/local-whisper --model large --pack
python -m agentic_content_system ingest-transcript workspace/productions/<slug> workspace/productions/<slug>/local-whisper/transcripts/<clip>.json
```

Models stay in the ignored `workspace/engine/.cache/whisper/` cache by default
(override with `ACS_WHISPER_CACHE_DIR`), and no API key belongs in this repository.
Cloud transcription is opt-in only; see `docs/CLOUD_TRANSCRIPTION.md`.
