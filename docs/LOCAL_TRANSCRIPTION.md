# Local transcription

Local Whisper is the default optional transcription helper. It is not required
by ACS graph validation and is not a media-render fallback.

On macOS/Linux:

```text
./workspace/engine/scripts/setup-local-transcription.sh
.venv/bin/python workspace/engine/scripts/transcribe-local-whisper.py workspace/productions/<slug>/sources --recursive --edit-dir workspace/productions/<slug>/local-whisper --model large --pack
```

Add `--language da` for Danish when appropriate. Windows users create a local
venv, install `workspace/engine/requirements/local-transcription.txt`, and use
`.venv\Scripts\python.exe` with the same script arguments.

Models default to ignored `workspace/engine/.cache/whisper/`. Override with
`ACS_WHISPER_CACHE_DIR`. Keep credentials outside the repository.

Register a generated transcript as a graph `transcript` node only when the
production uses it. Hash the exact bytes and record its provenance/review. Raw
ASR is not silently treated as human-reviewed truth.
