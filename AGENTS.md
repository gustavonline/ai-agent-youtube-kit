# AI Agent YouTube Kit Instructions

## Transcription

Use local Whisper transcription as the default workflow for this repo.

- Video Use upstream may mention `ELEVENLABS_API_KEY`; for this repo, do not require it for normal operation.
- Do not place API keys or secrets in this repo.
- For footage in `footage/<slug>/`, create transcripts with:

```bash
.venv/bin/python scripts/transcribe-local-whisper.py footage/<slug> --model large --pack
```

- Add `--language da` for Danish footage when appropriate.
- Whisper models should stay in repo-local `.cache/whisper/`, which is the script default.
- The transcript cache lives in `footage/<slug>/edit/transcripts/`.
- `takes_packed.md` is the primary transcript artifact for planning cuts.

Video Use can still handle editorial strategy, cut planning, subtitles, grading,
and final assembly after local transcripts have been generated. Avoid using
Video Use's ElevenLabs/Scribe transcription helper unless the user explicitly
asks for cloud transcription. If cloud transcription is requested, follow
`docs/CLOUD_TRANSCRIPTION.md` and keep credentials outside this repo.

## Branding Copies

Keep the base kit generic. Create a separate clone or copy for each brand before
tailoring `DESIGN.md`, `assets/brand-tokens.css`, reference assets, or project
history.
