# AI Agent YouTube Kit

Local video workspace for Codex, Video Use, and HyperFrames.

This repo is set up as a repeatable YouTube production workspace for AI agent videos, motion graphics, raw footage editing, and channel-specific branding.

## What Lives Here

- `footage/` - raw recordings, screen captures, B-roll, and exports you do not commit.
- `video-projects/` - one HyperFrames project per motion graphics piece or final video package.
- `assets/` - shared brand tokens and reusable assets.
- `docs/` - production workflow, prompt patterns, and brand rules.
- `scripts/` - repo-level helper checks.

## The Production Stack

Use the tools for different jobs:

- Video Use: transcript-first editing, take selection, cuts, subtitles, audio fades, color, final `ffmpeg` render, and self-checks.
- HyperFrames: HTML/CSS/JS motion graphics, kinetic titles, product/UI animations, lower thirds, transitions, and YouTube visual polish.
- This repo: your working library of templates, brand rules, examples, prompts, and project history.

## Starter Projects

- `video-projects/youtube-short-template` - 9:16 short-form template for talking-head plus captions and motion graphics.
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
Use the plugin-creator skill. Create a local Codex plugin called video-use from https://github.com/browser-use/video-use. Put it in ~/plugins/video-use, add it to the default personal marketplace, preserve the upstream SKILL.md/helpers/static files under skills/video-use, add accurate manifest metadata, validate the plugin, and tell me where to add ELEVENLABS_API_KEY. Do not transcribe anything yet.
```

### 2. Install Runtime Dependencies

From this repo:

```bash
brew install ffmpeg
npx --yes hyperframes doctor
```

For Video Use transcription, set `ELEVENLABS_API_KEY` in the Video Use plugin skill root or in your shell environment when you are ready to transcribe real footage.

### 3. Tailor Branding

Before building real videos, update:

- `DESIGN.md`
- `assets/brand-tokens.css`
- `assets/README.md`
- `docs/BRANDING.md`

The goal is to make new HyperFrames scenes and Video Use edit decisions inherit your channel identity instead of defaulting to generic AI-video styling.

## Normal Workflow

1. Confirm HyperFrames and Video Use are available in Codex.
2. Confirm branding files are tailored enough for the video.
3. Put raw footage in `footage/<video-slug>/`.
4. Ask Codex to use `video-use` to inventory the footage and propose an edit strategy.
5. Approve the strategy before it cuts anything.
6. Use HyperFrames for title cards, lower thirds, animated diagrams, UI explainers, and transitions.
7. Let Video Use assemble the final edit and run its self-eval.
8. Store finished motion projects under `video-projects/<video-slug>/` and final exports under the related `edit/` folder.

## HyperFrames Commands

Run commands inside a specific project folder:

```bash
cd video-projects/youtube-short-template
npm run dev
npm run check
npm run render
```

`npm run render` needs FFmpeg. Preview and source editing can work before FFmpeg is installed.

## Good First Codex Prompt

```text
Use video-use and HyperFrames. Inventory footage/my-video, propose a YouTube edit strategy, and identify which beats need motion graphics. Do not cut or render until I approve the plan.
```

## Useful Docs

- `SETUP.md` - fresh setup from clone to first footage drop.
- `docs/CODEX_PLUGIN_SETUP.md` - create the local Video Use plugin after clone.
- `docs/BRANDING.md` - tailor assets, tokens, captions, and identity.
- `docs/WORKFLOW.md` - production flow from raw footage to final render.
- `docs/PROMPTS.md` - reusable Codex prompts.
