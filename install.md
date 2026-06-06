# Install

Fresh setup for this AI Agent YouTube Kit.

This repo is designed for Codex with:

- HyperFrames for motion graphics and HTML-to-video rendering.
- Video Use for transcript-first editing, cuts, subtitles, color, and final assembly.
- A local brand system so every project can match your channel identity.

## 1. Clone

```bash
git clone https://github.com/gustavonline/ai-agent-youtube-kit.git
cd ai-agent-youtube-kit
```

If you are working from a local copy before the remote exists, just `cd` into the repo folder.

## 2. Verify Node And HyperFrames

HyperFrames needs Node.js 22 or newer.

```bash
node -v
npx --yes hyperframes --version
npx --yes hyperframes doctor
```

Codex has an official HyperFrames plugin in this environment. The CLI is still used inside each `video-projects/<project>/` folder.

## 3. Install FFmpeg

FFmpeg is required for HyperFrames rendering and Video Use final exports.

```bash
brew install ffmpeg
ffmpeg -version
ffprobe -version
```

## 4. Create The Local Video Use Plugin

Codex has an official HyperFrames plugin, but Video Use should be created as a local Codex plugin.

Paste this into Codex:

```text
Use the plugin-creator skill. Create a local Codex plugin called video-use from https://github.com/browser-use/video-use. Put it in ~/plugins/video-use, add it to the default personal marketplace, preserve the upstream SKILL.md/helpers/static files under skills/video-use, add accurate manifest metadata, validate the plugin, and tell me where to add ELEVENLABS_API_KEY. Do not transcribe anything yet.
```

Expected local shape:

```text
~/plugins/video-use/
  .codex-plugin/plugin.json
  assets/
  skills/
    video-use/
      SKILL.md
      install.md
      helpers/
      static/
      pyproject.toml
```

Expected marketplace file:

```text
~/.agents/plugins/marketplace.json
```

More detail: `docs/CODEX_PLUGIN_SETUP.md`.

## 5. Add Transcription Credentials

Video Use uses ElevenLabs Scribe for transcription.

Add the key only when you are ready to transcribe real footage:

```bash
ELEVENLABS_API_KEY=...
```

Use either:

- a `.env` file in the local Video Use plugin skill root, or
- an exported shell environment variable.

Do not put API keys in this repo.

## 6. Customize Branding

Before making a real video, edit:

```text
DESIGN.md
assets/brand-tokens.css
assets/README.md
docs/BRANDING.md
```

At minimum, decide:

- channel promise
- target audience
- colors
- fonts
- caption style
- logo/mark assets
- thumbnail direction
- examples to imitate and avoid

Recommended asset folders:

```text
assets/
  logo/
  backgrounds/
  fonts/
  audio/
  references/
```

Keep raw footage in `footage/<video-slug>/`, not in `assets/`.

## 7. Check Starter Projects

```bash
./scripts/check-projects.sh
```

The generated reference projects may have warnings. The custom `youtube-short-template` should pass cleanly.

## 8. Preview A Starter Project

```bash
cd video-projects/youtube-short-template
npm run dev
```

For checks:

```bash
npm run check
```

For render after FFmpeg is installed:

```bash
npm run render
```

## 9. Add Footage

```text
footage/<video-slug>/
  raw clips here
```

Do not start by rendering. Start with inventory and strategy.

Codex prompt:

```text
Use video-use and HyperFrames. Inventory footage/<video-slug>, propose a YouTube edit strategy, and identify which beats need motion graphics. Do not cut or render until I approve the plan.
```

## 10. Production Loop

1. Drop raw footage in `footage/<slug>/`.
2. Use Video Use to inventory, transcribe, and propose an edit.
3. Approve the strategy.
4. Use HyperFrames for motion graphics, UI explainers, lower thirds, title cards, and transitions.
5. Let Video Use assemble, subtitle, grade, and self-check the final timeline.
6. Keep final outputs under `footage/<slug>/edit/`.

