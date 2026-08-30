# Optional Codex Tooling

Agentic Content System v0.3 does not require a Codex plugin. Install FFmpeg and
use the Python CLI for the local contract/render/package boundary. For video,
FreeCut is the one normal supervised Studio route; the repository-local
`freecut-studio` skill owns its fixed external checkout model.

Remotion or generic code-based motion may remain a bounded ACS production
technique when a concrete deliverable needs one asset; it is not another editor
or prerequisite. Existing HyperFrames and other editor material is retained
only for explicit migration/recovery. Do not install a parallel editor plugin,
create a bridge contract, or turn legacy material into an active route.

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
