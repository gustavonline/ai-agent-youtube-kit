# Agentic Video Editor

Local video workspace for Codex, Video Use, and HyperFrames.

This repo is set up as a repeatable agentic video editing workspace for AI workflow videos, motion graphics, raw footage editing, and channel-specific branding.

## What Lives Here

- `footage/` - raw recordings, screen captures, B-roll, and exports you do not commit.
- `video-projects/` - one HyperFrames project per motion graphics piece or final video package.
- `channel/` - channel profile, style guide, reference analyses, and published-video data.
- `content-pipeline/` - lightweight idea and packaging pipeline without a hosted app.
- `templates/` - reusable markdown templates for briefs, cut plans, packaging, final review, and reference analysis.
- `assets/` - shared brand tokens and reusable assets.
- `docs/` - production workflow, prompt patterns, and brand rules.
- `scripts/` - repo-level helper checks.

## The Production Stack

Use the tools for different jobs:

- Video Use: transcript-first editing, take selection, cuts, subtitles, audio fades, color, final `ffmpeg` render, and self-checks.
- HyperFrames: HTML/CSS/JS motion graphics, kinetic titles, product/UI animations, lower thirds, transitions, and platform-ready visual polish.
- Reference analyzer: local `yt-dlp` + `ffmpeg` frame/caption extraction for learning from selected videos.
- This repo: your working library of templates, brand rules, reference intelligence, prompts, and project history.

## Starter Projects

- `video-projects/short-form-template` - 9:16 short-form template for talking-head plus captions and motion graphics.
- `video-projects/agent-product-demo` - 16:9 product/demo promo starter generated from HyperFrames.
- `video-projects/agent-short-starter` - 16:9 kinetic motion reference generated from HyperFrames.

## First Setup

Do this before dropping in raw footage. The canonical fresh setup guide is:

- `SETUP.md`

### 1. Set Up Codex Plugins

Codex already has an official HyperFrames plugin available in this environment, but Video Use needs to be created as a local plugin.

Read:

- `docs/CODEX_PLUGIN_SETUP.md`

Fast prompt:

```text
Use the plugin-creator skill. Create a local Codex plugin called video-use from https://github.com/browser-use/video-use. Put it in ~/plugins/video-use, add it to the default personal marketplace, preserve the upstream SKILL.md/helpers/static files under skills/video-use, add accurate manifest metadata, and validate the plugin. Do not transcribe anything yet.
```

### 2. Install Runtime Dependencies

From this repo:

```bash
brew install ffmpeg
./scripts/setup-local-transcription.sh
npx --yes hyperframes doctor
```

This repo uses local Whisper transcription by default. Read `docs/LOCAL_TRANSCRIPTION.md` and transcribe footage with:

```bash
.venv/bin/python scripts/transcribe-local-whisper.py footage/<video-slug> --model large --pack
```

### 3. Tailor Branding

Before building real videos, update:

- `channel/PROFILE.md`
- `channel/STYLE_GUIDE.md`
- `DESIGN.md`
- `PROJECT_MEMORY.md`
- `assets/brand-tokens.css`
- `assets/README.md`
- `docs/BRANDING.md`

The goal is to make new HyperFrames scenes and Video Use edit decisions inherit your channel identity instead of defaulting to generic agent-video styling.

### 4. Analyze References

Before the first serious video, analyze a few reference videos and condense the
reusable lessons into `channel/STYLE_GUIDE.md`:

```bash
brew install yt-dlp ffmpeg
python3 scripts/analyze-reference-video.py --check
python3 scripts/analyze-reference-video.py "<reference-video-url>"
```

## Normal Workflow

1. Confirm HyperFrames and Video Use are available in Codex.
2. Confirm `channel/PROFILE.md`, `channel/STYLE_GUIDE.md`, and branding files are tailored enough for the video.
3. Scaffold the project with `python3 scripts/new-video.py <video-slug>`.
4. Put raw footage in `footage/<video-slug>/`.
5. Run local Whisper transcription and pack transcripts.
6. Ask Codex to use `video-use` to inventory the footage and propose an edit strategy.
7. Save the approved strategy to `footage/<slug>/edit/cut-plan.md`.
8. Use HyperFrames for title cards, lower thirds, animated diagrams, UI explainers, and transitions.
9. Let Video Use assemble the final edit and run its self-eval.
10. Run packaging review and final review.
11. Store finished motion projects under `video-projects/<video-slug>/` and final exports under the related `edit/` folder.
12. Update memory only with durable lessons.

## HyperFrames Commands

Run commands inside a specific project folder:

```bash
cd video-projects/short-form-template
npm run dev
npm run check
npm run render
```

`npm run render` needs FFmpeg. Preview and source editing can work before FFmpeg is installed.

## Good First Codex Prompt

```text
Use local Whisper transcripts from footage/my-video/edit/takes_packed.md, then use video-use and HyperFrames. Inventory the footage, propose an agentic video edit strategy, and identify which beats need motion graphics. Do not cut or render until I approve the plan.
```

## Useful Commands

```bash
python3 scripts/analyze-reference-video.py --check
python3 scripts/analyze-reference-video.py "<reference-video-url>"
python3 scripts/new-video.py my-video
.venv/bin/python scripts/transcribe-local-whisper.py footage/my-video --model large --pack
```

## Useful Docs

- `SETUP.md` - fresh setup from clone to first footage drop.
- `docs/CODEX_PLUGIN_SETUP.md` - create the local Video Use plugin after clone.
- `docs/REFERENCE_ANALYSIS.md` - analyze selected reference videos without a hosted app.
- `docs/LOCAL_TRANSCRIPTION.md` - local Whisper transcription workflow.
- `docs/CLOUD_TRANSCRIPTION.md` - optional cloud transcription guardrails.
- `docs/PACKAGING.md` - title and thumbnail review workflow.
- `docs/FINAL_REVIEW.md` - final advisory review before publishing.
- `docs/LEARNING.md` - project memory and continuous learning workflow.
- `docs/BRANDING.md` - tailor assets, tokens, captions, and identity.
- `docs/WORKFLOW.md` - production flow from raw footage to final render.
- `docs/PROMPTS.md` - reusable Codex prompts.
