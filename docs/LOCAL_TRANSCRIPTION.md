# Local Transcription

This kit uses local Whisper transcription by default. Do not add transcription
API keys to this repo.

## Install

FFmpeg is required:

```bash
brew install ffmpeg
```

Install the repo-local Python runtime:

```bash
./scripts/setup-local-transcription.sh
```

This creates:

```text
.venv/
.cache/whisper/
```

Both directories live inside the repo clone and are ignored by git. Deleting the
clone removes the Python packages and Whisper model cache.

To remove local runtime/cache artifacts without deleting the clone:

```bash
./scripts/clean-local-artifacts.sh
```

To also remove ignored footage and edit outputs:

```bash
./scripts/clean-local-artifacts.sh --footage
```

## Transcribe Footage

Put raw footage in:

```text
footage/<video-slug>/
```

Run local transcription from the repo root:

```bash
.venv/bin/python scripts/transcribe-local-whisper.py footage/<video-slug> --model large --pack
```

For Danish footage, pass the language explicitly:

```bash
.venv/bin/python scripts/transcribe-local-whisper.py footage/<video-slug> --model large --language da --pack
```

The script writes:

```text
footage/<video-slug>/edit/transcripts/<clip-name>.json
footage/<video-slug>/edit/takes_packed.md
```

`takes_packed.md` is the primary transcript view for edit decisions.

The first run with `--model large` downloads the model to `.cache/whisper/`.
Override that only when you intentionally want a different cache location:

```bash
.venv/bin/python scripts/transcribe-local-whisper.py footage/<video-slug> --model large --model-cache-dir .cache/whisper --pack
```

## Notes

- Transcripts are cached. Use `--force` to re-transcribe changed or improved takes.
- The generated JSON is compatible with Video Use transcript packing.
- Local Whisper does not perform speaker diarization in this workflow; transcripts
  are marked as `speaker_0`.
- Use `--model large-v3`, `--device mps`, or `--fp16 false` if those fit your Mac
  setup better.
