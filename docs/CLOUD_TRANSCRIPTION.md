# Cloud Transcription

Local Whisper is the default transcription workflow for this kit.

Use cloud transcription only when you explicitly want it, for example:

- better speaker diarization than the local Whisper workflow provides
- a project where ElevenLabs Scribe quality is preferred
- a user-approved workflow where an API key is acceptable

## Guardrails

- Do not put API keys in this repo.
- Do not require cloud transcription for normal operation.
- Do not ask for `ELEVENLABS_API_KEY` just because Video Use upstream docs mention it.
- Only use ElevenLabs/Scribe when the user explicitly asks for cloud transcription.

## Where To Put The Key

If cloud transcription is deliberately enabled, keep the key outside this repo.

Preferred locations:

```text
~/plugins/video-use/skills/video-use/.env
```

or an exported shell environment variable:

```bash
export ELEVENLABS_API_KEY=...
```

Never commit `.env` files or API keys.
