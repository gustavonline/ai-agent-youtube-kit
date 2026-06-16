# Agentic Video Editor Instructions

This is an AI-first, cloneable video workspace. Do not turn it into a hosted
web app unless the user explicitly asks. Prefer transparent files, local
scripts, and agent-readable markdown over dashboards, databases, auth, or
server state.

## Start Here

Before planning channel-specific work, read these files in order:

1. `DESIGN.md`
2. `PROJECT_MEMORY.md`
3. `MOTION_PHILOSOPHY.md`
4. `channel/PROFILE.md`
5. `channel/STYLE_GUIDE.md`
6. relevant docs under `docs/`

Use `content-pipeline/ideas.md` as the lightweight CreatorGrowth-style content
pipeline. Use `channel/REFERENCES.md` and `channel/references/` as the reference
analysis library.

## Workflow Router

- Reference video or competitor analysis: follow `docs/REFERENCE_ANALYSIS.md`
  and run `python3 scripts/analyze-reference-video.py <url-or-file>`.
- Own raw footage transcription: follow the Transcription section below.
- Edit planning: use `templates/video-brief.md` and `templates/cut-plan.md`.
- Motion graphics: read `MOTION_PHILOSOPHY.md`, the active project `DESIGN.md`,
  and use HyperFrames inside `video-projects/<project>/`.
- Packaging: follow `docs/PACKAGING.md` and write
  `footage/<slug>/edit/packaging-review.md`.
- Final review: follow `docs/FINAL_REVIEW.md` and write
  `footage/<slug>/edit/final-review.md`.
- Durable learning: follow `docs/LEARNING.md`.

## Reference Analysis

Use reference analysis to learn from selected videos before creating or evolving
a channel style.

```bash
python3 scripts/analyze-reference-video.py --check
python3 scripts/analyze-reference-video.py "<video-url>"
```

For long videos, focus the section:

```bash
python3 scripts/analyze-reference-video.py "<video-url>" --start 00:00 --end 01:30
```

The script writes artifacts under `channel/references/<slug>/`. Inspect frames
from `frames_manifest.json`, read `transcript.md`, fill `analysis.md`, add one
row to `channel/REFERENCES.md`, and promote only reusable lessons to
`channel/STYLE_GUIDE.md`.

Do not copy another creator's identity. Extract reusable mechanics: hook shape,
visual proof, pacing, structure, CTA placement, and packaging logic.

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

## Project Learning

Before planning a branded video, read `DESIGN.md`, `PROJECT_MEMORY.md`, and
`MOTION_PHILOSOPHY.md`, plus `channel/PROFILE.md` and `channel/STYLE_GUIDE.md`.
For project-specific work, also read the active `video-projects/<project>/DESIGN.md`
when it exists.

After a finished project, update learning only when it is durable:

- append factual session notes to `footage/<slug>/edit/project.md`
- add concise reusable lessons to `PROJECT_MEMORY.md`
- add concise channel-level lessons to `channel/STYLE_GUIDE.md`
- update `DESIGN.md` only for stable brand decisions
- update `MOTION_PHILOSOPHY.md` only for general motion principles

Keep memory small and concrete. Do not add vague process notes or one-off taste
reactions.

## Clone Setup

For a fresh branded clone:

1. Fill `channel/PROFILE.md`.
2. Add known performance data to `channel/published-videos.csv` if available.
3. Analyze 3-10 reference videos with `scripts/analyze-reference-video.py`.
4. Condense reusable lessons into `channel/STYLE_GUIDE.md`.
5. Tailor `DESIGN.md`, `assets/brand-tokens.css`, and starter projects.
6. Start the first video using `templates/video-brief.md`.

## Branding Copies

Keep the base editor generic. Create a separate clone or copy for each brand before
tailoring `DESIGN.md`, `assets/brand-tokens.css`, reference assets, or project
history. The branded clone's `PROJECT_MEMORY.md` should evolve as finished
projects accumulate.
