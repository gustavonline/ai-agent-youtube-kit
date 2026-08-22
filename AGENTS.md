# Agentic Content System Instructions

This is an AI-first, cloneable content production system. Do not turn it into
a hosted web app, phone-first editor, mini-Premiere, or publishing bot unless
the user explicitly asks. Prefer transparent contracts, local scripts, and
agent-readable Markdown over dashboards, databases, auth, or server state.

The v0.2 system boundary is the Python `agentic_content_system` CLI,
versioned JSON contracts, FFmpeg/ffprobe, local transcript adapters, static
review reports, and human approval. HyperFrames and full editors are optional
adapters, not product identity.

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

- New ACS workspace or example: read `docs/QUICKSTART.md`, `docs/ARCHITECTURE.md`,
  `docs/INPUT_OWNERSHIP.md`, `docs/CONTENT_FORMATS.md`, and the repository-local
  `.agents/skills/agentic-content-system/SKILL.md`; use the CLI flow in
  `docs/CLI.md`.
- Clone setup or pre-first-video configuration: use
  `.agents/skills/setup-content-system/SKILL.md`; resolve only missing business,
  audience, offer/promise, channel-policy, cadence, and delivery-default
  decisions, then run doctor and profile validation without creating a content
  workspace.
- Audit, check, health-check, drift, reconcile, or readiness request: read
  `.agents/skills/audit-content-system/SKILL.md`, set an explicit repository or
  one-workspace scope, and keep the audit strictly read-only. Do not run
  write-capable `verify`, `review-report`, or `export-result` as audit steps.
- Build proof: use `scripts/create-fixture-media.py` for a tiny ignored source
  under an ignored `examples/<slug>/` boundary and run the actual CLI from
  inspect through `export-result`.

- Reference video or competitor analysis: follow `docs/REFERENCE_ANALYSIS.md`
  and run `python3 scripts/analyze-reference-video.py <url-or-file>`.
- Raw capture/source transcription: follow the Transcription section below;
  `footage/` is retained only for legacy/source-side compatibility.
- Edit planning: use the declarative `edit-plan.json`; use
  `templates/video-brief.md` and `templates/cut-plan.md` for human context when
  useful.
- Motion graphics: read `MOTION_PHILOSOPHY.md`, the active content design, and
  use HyperFrames only through the optional seam documented in
  `engine/motion-adapters/`.
- Packaging: follow `docs/PACKAGING.md` and write the review in the active
  `examples/<slug>/` boundary (legacy `footage/<slug>/edit/` notes remain
  supported as source-side input).
- Final review: follow `docs/FINAL_REVIEW.md` and keep the result in the active
  example/workspace boundary.
- Real-video acceptance: follow `docs/REAL_VIDEO_ACCEPTANCE.md`; generated or
  public footage proves the engine, while owner-recorded footage is required
  for a real usability PASS.
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

- Upstream editor tooling may mention `ELEVENLABS_API_KEY`; for this repo, do not require it for normal operation.
- Do not place API keys or secrets in this repo.
- For a legacy source directory under `footage/<slug>/`, create transcripts
  with:

```bash
.venv/bin/python scripts/transcribe-local-whisper.py footage/<slug> --model large --pack
```

- Add `--language da` for Danish footage when appropriate.
- Whisper models should stay in repo-local `.cache/whisper/`, which is the script default.
- The legacy transcript cache lives in `footage/<slug>/edit/transcripts/`.
  For an ACS workspace, ingest the resulting open JSON into its canonical
  `transcripts/active.json` with `acs ingest-transcript`.
- `takes_packed.md` is an optional transcript view for planning cuts; the ACS
  transcript contract remains the runtime input.

An external editor adapter can still handle editorial strategy, cut planning,
subtitles, grading, and final assembly after local transcripts have been
generated. Avoid using a cloud transcription helper unless the user explicitly
asks for cloud transcription. If cloud transcription is requested, follow
`docs/CLOUD_TRANSCRIPTION.md` and keep credentials outside this repo.

## Project Learning

Before planning a branded video, read `DESIGN.md`, `PROJECT_MEMORY.md`, and
`MOTION_PHILOSOPHY.md`, plus `channel/PROFILE.md` and `channel/STYLE_GUIDE.md`.
For an optional HyperFrames motion workspace, also read its local
`video-projects/<slug>/DESIGN.md` when it exists. It is adapter material, not
an ACS content boundary.

After a finished project, update learning only when it is durable:

- append factual session notes to the active workspace's local notes (or the
  legacy `footage/<slug>/edit/project.md` when using that compatibility path)
- add concise reusable lessons to `PROJECT_MEMORY.md`
- add concise channel-level lessons to `channel/STYLE_GUIDE.md`
- update `DESIGN.md` only for stable brand decisions
- update `MOTION_PHILOSOPHY.md` only for general motion principles

Keep memory small and concrete. Do not add vague process notes or one-off taste
reactions.

## Clone Setup

For a fresh branded clone:

1. Fill `channel/PROFILE.md`.
2. Update and validate `channel/brand.json` from the resolved profile.
3. Add known performance data to `channel/published-videos.csv` if available.
4. Analyze 3-10 reference videos with `scripts/analyze-reference-video.py`.
5. Condense reusable lessons into `channel/STYLE_GUIDE.md`.
6. Tailor `DESIGN.md`, `assets/brand-tokens.css`, and optional starter projects.
7. Start the first video using `templates/video-brief.md` only after a real
   content outcome is requested.

## Branding Copies

Keep the base editor generic. Create a separate clone or copy for each brand before
tailoring `DESIGN.md`, `assets/brand-tokens.css`, reference assets, or project
history. The branded clone's `PROJECT_MEMORY.md` should evolve as finished
projects accumulate.
