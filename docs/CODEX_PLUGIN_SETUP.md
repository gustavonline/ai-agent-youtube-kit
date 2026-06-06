# Codex Plugin Setup

OpenAI Codex currently has an official HyperFrames plugin, but Video Use is not an official Codex plugin in this setup. After cloning this repo, create the local Video Use plugin first so Codex has both halves of the video workflow available.

## Target State

You want:

- Official HyperFrames plugin available in Codex.
- Local Video Use plugin installed from `browser-use/video-use`.
- FFmpeg available on `PATH`.
- `ELEVENLABS_API_KEY` ready before transcription.

## Fast Codex Prompt

Use this in Codex after cloning this repo:

```text
Use the plugin-creator skill. Create a local Codex plugin called video-use from https://github.com/browser-use/video-use. Put it in ~/plugins/video-use, add it to the default personal marketplace, preserve the upstream SKILL.md/helpers/static files under skills/video-use, add accurate manifest metadata, validate the plugin, and tell me where to add ELEVENLABS_API_KEY. Do not transcribe anything yet.
```

That is the preferred workflow because Codex can use its local `plugin-creator` validator and marketplace conventions.

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

For transcription, Video Use needs ElevenLabs Scribe:

```bash
ELEVENLABS_API_KEY=...
```

You can keep the key in the Video Use plugin skill root `.env` or export it in your shell. Do not put API keys in this repo.

## First-Run Order

1. Clone this kit.
2. Create/install the local `video-use` plugin using the Codex prompt above.
3. Confirm the official HyperFrames plugin is available in Codex.
4. Install FFmpeg.
5. Customize `DESIGN.md` and `assets/brand-tokens.css`.
6. Drop raw footage into `footage/<slug>/`.
7. Ask Video Use to inventory and propose a strategy.
8. Use HyperFrames for motion graphics after the edit plan is approved.

