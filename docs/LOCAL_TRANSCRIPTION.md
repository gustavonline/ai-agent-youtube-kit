# Local Transcription

This repo uses local Whisper transcription by default. Do not add transcription
API keys to this repo.

## Install

FFmpeg is required:

```bash
brew install ffmpeg
```

Install the repo-local Python runtime:

```bash
./workspace/engine/scripts/setup-local-transcription.sh
```

This creates:

```text
.venv/
workspace/engine/.cache/whisper/
```

Both directories live inside the repo clone and are ignored by git. Deleting the
clone removes the Python packages and Whisper model cache.

To remove local runtime/cache artifacts without deleting the clone:

```bash
./workspace/engine/scripts/clean-local-artifacts.sh
```

To also remove ignored footage and edit outputs:

```bash
./workspace/engine/scripts/clean-local-artifacts.sh --footage
```

## Transcribe An ACS Workspace

Put source media in the workspace:

```text
workspace/productions/<content-slug>/sources/
```

Run local transcription from the repo root:

```bash
.venv/bin/python workspace/engine/scripts/transcribe-local-whisper.py workspace/productions/<content-slug>/sources --recursive --edit-dir workspace/productions/<content-slug>/local-whisper --model large --pack
```

For Danish footage, pass the language explicitly:

```bash
.venv/bin/python workspace/engine/scripts/transcribe-local-whisper.py workspace/productions/<content-slug>/sources --recursive --edit-dir workspace/productions/<content-slug>/local-whisper --model large --language da --pack
```

The script writes:

```text
workspace/productions/<content-slug>/local-whisper/transcripts/<clip-name>.json
workspace/productions/<content-slug>/local-whisper/takes_packed.md
```

`takes_packed.md` is the primary transcript view for edit decisions.

The first run with `--model large` downloads the model to
`workspace/engine/.cache/whisper/`. Use the single cross-platform
`ACS_WHISPER_CACHE_DIR` override when a user-level cache is preferred, or use
`--model-cache-dir` for one invocation:

```bash
ACS_WHISPER_CACHE_DIR=/path/to/user-cache .venv/bin/python workspace/engine/scripts/transcribe-local-whisper.py workspace/productions/<content-slug>/sources --recursive --edit-dir workspace/productions/<content-slug>/local-whisper --model large --pack
```

In Windows PowerShell, set `$env:ACS_WHISPER_CACHE_DIR` to a local path before
the same Python command. An old repository-root `.cache/whisper/` is not
deleted automatically: check whether another local tool uses it, then migrate
or remove it manually with the operating system's normal file tools.

## Notes

- Transcripts are cached. Use `--force` to re-transcribe changed or improved takes.
- The generated JSON is compatible with the repository's optional packer and
  can be normalized directly with `acs ingest-transcript workspace/productions/<slug> ...`.
- The helper still accepts a direct media file or an older source directory
  when existing local work needs it.
- Local Whisper does not perform speaker diarization in this workflow; transcripts
  are marked as `speaker_0`.
- Use `--model large-v3`, `--device mps`, or `--fp16 false` if those fit your Mac
  setup better.
- See `docs/CLOUD_TRANSCRIPTION.md` only when cloud transcription is explicitly
  requested.
