# Workflow

## Raw Footage To Final Video

1. Create a folder under `footage/<slug>/`.
2. Put source clips, screen recordings, B-roll, logos, and notes there.
3. Run local Whisper transcription and pack transcripts.
4. Ask Codex to use Video Use to inventory `edit/takes_packed.md`.
5. Review the proposed editorial strategy.
6. Approve the cut plan.
7. Build HyperFrames scenes for moments that need visual explanation.
8. Render or export HyperFrames overlays/assets.
9. Let Video Use assemble, subtitle, grade, and verify.

```bash
.venv/bin/python scripts/transcribe-local-whisper.py footage/<slug> --model large --pack
```

## Folder Pattern

```text
footage/<slug>/
  raw clips here
  edit/
    project.md
    takes_packed.md
    edl.json
    animations/
    final.mp4

video-projects/<slug>-graphics/
  index.html
  compositions/
  assets/
  renders/
```

## When To Use HyperFrames

- Animated hook/title
- Lower third
- YouTube subscribe/CTA
- System diagram
- Product UI animation
- Website capture-to-video
- Word-synced kinetic typography
- Overlay that would be painful in raw ffmpeg

## When To Let Video Use Handle It

- Cut decisions
- Removing filler words and dead air
- Transcript packing
- Planning from local Whisper transcripts
- Audio fades
- Subtitle burn-in on the final timeline
- Color grade per segment
- Final assembly and self-eval
