# Agentic Content System Instructions

This is an AI-first, cloneable content production system. Do not turn it into
a hosted web app, phone-first editor, mini-Premiere, or publishing bot unless
the user explicitly asks. Prefer transparent contracts, local scripts, and
agent-readable Markdown over dashboards, databases, auth, or server state.

The system boundary is the Python `agentic_content_system` CLI, versioned JSON
contracts, FFmpeg/ffprobe, local transcript adapters, the external FreeCut
browser Studio, static review reports, and human approval. FreeCut is the one
normal Studio for video; legacy editor/motion material is migration or
recovery input, not a parallel production choice.

ACS owns deliverable content production and proof. Agentic Design System (ADS)
owns new portable visual direction and reusable visual assets; an accepted
`workspace/channel/DESIGN.md` is production input and a local snapshot, not a
transfer of visual-design ownership to ACS.

## Start Here

Before planning channel-specific work, read these files in order:

1. `workspace/channel/DESIGN.md`
2. `workspace/learning/PROJECT_MEMORY.md`
3. `workspace/learning/MOTION_PHILOSOPHY.md`
4. `workspace/channel/PROFILE.md`
5. `workspace/channel/STYLE_GUIDE.md`
6. relevant docs under `docs/`

Use `workspace/content-pipeline/ideas.md` as the lightweight CreatorGrowth-style content
pipeline. Use `workspace/references/REFERENCES.md` and `workspace/references/` as the reference
analysis library.

## Workflow Router

The repository-local skill index at `.agents/skills/README.md` defines ACS
ownership and routes each direct skill without introducing a plugin dependency.

- New ACS production workspace: read `docs/QUICKSTART.md`, `docs/ARCHITECTURE.md`,
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
- Visual-direction boundary: ACS may start from already accepted direction. If
  content work exposes a material visual-design gap or needs new OpenPencil
  work, AIOS may suggest the bounded sibling ADS route. Either System may be
  entered first; never execute the sibling automatically or impose a
  deterministic ADS-to-ACS chain. A standalone caller may supply equivalent
  accepted `DESIGN.md` direction and selected assets without ADS or AIOS.
- Build proof: use `workspace/engine/scripts/create-fixture-media.py` for a tiny ignored source
  under an ignored `workspace/productions/<slug>/` boundary and run the actual CLI from
  inspect through `export-result`.

- Reference video or competitor analysis: follow `docs/REFERENCE_ANALYSIS.md`
  and run `python3 workspace/engine/scripts/analyze-reference-video.py <url-or-file>`.
- Raw capture/source transcription: follow the Transcription section below;
  `workspace/productions/` is the canonical source-side boundary.
- Edit planning: use the declarative `edit-plan.json`; use
  `workspace/engine/templates/video-brief.md` and `workspace/engine/templates/cut-plan.md` for human context when
  useful.
- Studio editing and motion: use `.agents/skills/freecut-studio/SKILL.md` and
  the active content design. Legacy HyperFrames material under
  `workspace/engine/motion-adapters/` is retained only for explicit
  migration/recovery.
- Packaging: follow `docs/PACKAGING.md` and write the review in the active
  `workspace/productions/<slug>/` boundary.
- Final review: follow `docs/FINAL_REVIEW.md` and keep the result in the active
  production workspace boundary.
- Real-video acceptance: follow `docs/REAL_VIDEO_ACCEPTANCE.md`; generated or
  public footage proves the engine, while owner-recorded footage is required
  for a real usability PASS.
- Durable learning: follow `docs/LEARNING.md`.

## Reference Analysis

Use reference analysis to learn from selected videos before creating or evolving
a channel style.

```bash
python3 workspace/engine/scripts/analyze-reference-video.py --check
python3 workspace/engine/scripts/analyze-reference-video.py "<video-url>"
```

For long videos, focus the section:

```bash
python3 workspace/engine/scripts/analyze-reference-video.py "<video-url>" --start 00:00 --end 01:30
```

The script writes artifacts under `workspace/references/<slug>/`. Inspect frames
from `frames_manifest.json`, read `transcript.md`, fill `analysis.md`, add one
row to `workspace/references/REFERENCES.md`, and promote only reusable lessons to
`workspace/channel/STYLE_GUIDE.md`.

Do not copy another creator's identity. Extract reusable mechanics: hook shape,
visual proof, pacing, structure, CTA placement, and packaging logic.

## Transcription

Use local Whisper transcription as the default workflow for this repo.

- Upstream editor tooling may mention `ELEVENLABS_API_KEY`; for this repo, do not require it for normal operation.
- Do not place API keys or secrets in this repo.
- For source media under `workspace/productions/<slug>/sources/`, create local
  transcripts with:

```bash
.venv/bin/python workspace/engine/scripts/transcribe-local-whisper.py workspace/productions/<slug>/sources --model large --pack
```

- Add `--language da` for Danish footage when appropriate.
- Whisper models should stay in ignored `workspace/engine/.cache/whisper/` by default; use `ACS_WHISPER_CACHE_DIR` for one portable override.
- The optional editor transcript cache lives in
  `workspace/productions/<slug>/edit/transcripts/`. For an ACS production,
  ingest the resulting open JSON into its canonical `transcripts/active.json`
  with `acs ingest-transcript`.
- `takes_packed.md` is an optional transcript view for planning cuts; the ACS
  transcript contract remains the runtime input.

FreeCut Studio handles normal supervised timeline editing after local
transcripts have been generated. Avoid using a cloud transcription helper unless the user explicitly
asks for cloud transcription. If cloud transcription is requested, follow
`docs/CLOUD_TRANSCRIPTION.md` and keep credentials outside this repo.

## Project Learning

Before planning a branded video, read `workspace/channel/DESIGN.md`,
`workspace/learning/PROJECT_MEMORY.md`, and
`workspace/learning/MOTION_PHILOSOPHY.md`, plus `workspace/channel/PROFILE.md`
and `workspace/channel/STYLE_GUIDE.md`.
Read a legacy HyperFrames workspace design only for explicitly requested
migration/recovery. It is not an ACS content boundary or normal Studio route.

After a finished project, update learning only when it is durable:

- append factual session notes to the active production workspace's local notes
- add concise reusable lessons to `workspace/learning/PROJECT_MEMORY.md`
- add concise channel-level lessons to `workspace/channel/STYLE_GUIDE.md`
- replace `workspace/channel/DESIGN.md` only with direction accepted by the
  visual-design owner
- update `workspace/learning/MOTION_PHILOSOPHY.md` only for general motion principles

Keep memory small and concrete. Do not add vague process notes or one-off taste
reactions.

## Clone Setup

For a fresh branded clone:

1. Fill `workspace/channel/PROFILE.md`.
2. Update and validate `workspace/channel/brand.json` from the resolved profile.
3. Add known performance data to `workspace/channel/published-videos.csv` if available.
4. Analyze 3-10 reference videos with `workspace/engine/scripts/analyze-reference-video.py`.
5. Condense reusable lessons into `workspace/channel/STYLE_GUIDE.md`.
6. Copy accepted portable visual direction and selected assets into
   `workspace/channel/DESIGN.md`, `workspace/channel/assets/brand-tokens.css`,
   and optional starter projects; route unresolved visual judgment as described
   above.
7. Start the first video using `workspace/engine/templates/video-brief.md` only after a real
   content outcome is requested.

## Branding Copies

Keep the base editor generic. Create a separate clone or copy for each brand before
accepting brand-specific `workspace/channel/DESIGN.md`, `workspace/channel/assets/brand-tokens.css`, reference assets, or project
history. The branded clone's `workspace/learning/PROJECT_MEMORY.md` should evolve as finished
projects accumulate.
