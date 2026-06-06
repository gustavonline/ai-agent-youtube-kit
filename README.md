# AI Agent YouTube Kit

Local video workspace for Codex, Video Use, and HyperFrames.

This repo is modeled after Nate Herkai's student-kit idea, but it is set up for your own repeatable YouTube workflow instead of copying AIS/Nate branding.

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

From this repo:

```bash
brew install ffmpeg
npx --yes hyperframes doctor
```

For Video Use transcription, set `ELEVENLABS_API_KEY` in the Video Use plugin skill root or in your shell environment when you are ready to transcribe real footage.

## Normal Workflow

1. Put raw footage in `footage/<video-slug>/`.
2. Ask Codex to use `video-use` to inventory the footage and propose an edit strategy.
3. Approve the strategy before it cuts anything.
4. Use HyperFrames for title cards, lower thirds, animated diagrams, UI explainers, and transitions.
5. Let Video Use assemble the final edit and run its self-eval.
6. Store finished motion projects under `video-projects/<video-slug>/` and final exports under the related `edit/` folder.

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

