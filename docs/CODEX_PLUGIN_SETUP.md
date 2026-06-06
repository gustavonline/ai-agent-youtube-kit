# Codex Plugin Setup

OpenAI Codex currently has an official HyperFrames plugin, but Video Use is not an official Codex plugin in this setup. After cloning this repo, create the local Video Use plugin first so Codex has both halves of the video workflow available.

## Target State

You want:

- Official HyperFrames plugin available in Codex.
- Local Video Use plugin installed from `browser-use/video-use`.
- FFmpeg available on `PATH`.
- Local Whisper available for transcription.

## Fast Codex Prompt

Use this in Codex after cloning this repo:

```text
Use the plugin-creator skill. Create a local Codex plugin called video-use from https://github.com/browser-use/video-use. Put it in ~/plugins/video-use, add it to the default personal marketplace, preserve the upstream SKILL.md/helpers/static files under skills/video-use, add accurate manifest metadata, and validate the plugin. Do not transcribe anything yet.
```

That is the preferred workflow because Codex can use its local `plugin-creator` validator and marketplace conventions.

## Local Whisper Default

Video Use upstream may still document ElevenLabs/Scribe as its transcription
helper. This repo intentionally defaults to local Whisper instead. The repo's
`AGENTS.md`, `docs/LOCAL_TRANSCRIPTION.md`, and prompts define that default.
Treat the plugin as a tool; keep this repo's workflow rules in this repo.

## Manual Shape

The local plugin should end up like this:

```text
~/plugins/video-use/
  .codex-plugin/plugin.json
  assets/
    video-use-banner.png
  skills/
    video-use/
      SKILL.md
      install.md
      helpers/
      skills/manim-video/
      static/
      pyproject.toml
```

The personal marketplace entry should live at:

```text
~/.agents/plugins/marketplace.json
```

The entry should point to:

```json
{
  "name": "video-use",
  "source": {
    "source": "local",
    "path": "./plugins/video-use"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

## Runtime Prerequisites

Install FFmpeg before rendering or final Video Use exports:

```bash
brew install ffmpeg
```

Verify:

```bash
ffmpeg -version
ffprobe -version
npx --yes hyperframes doctor
```

Install local Whisper for transcription:

```bash
./scripts/setup-local-transcription.sh
```

This kit transcribes footage locally through
`scripts/transcribe-local-whisper.py`, stores Whisper models in repo-local
`.cache/whisper/`, then lets Video Use consume the packed transcript. Do not put
API keys in this repo.

## First-Run Order

1. Clone this kit.
2. Create/install the local `video-use` plugin using the Codex prompt above.
3. Confirm the official HyperFrames plugin is available in Codex.
4. Install FFmpeg.
5. Install local Whisper.
6. Customize `DESIGN.md`, `PROJECT_MEMORY.md`, and `assets/brand-tokens.css`.
7. Drop raw footage into `footage/<slug>/`.
8. Run local Whisper transcription and packing.
9. Ask Video Use to inventory the packed transcript and propose a strategy.
10. Use HyperFrames for motion graphics after the edit plan is approved.
