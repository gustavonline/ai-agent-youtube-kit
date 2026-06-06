# Workflow

## Raw Footage To Final Video

1. Create a folder under `footage/<slug>/`.
2. Put source clips, screen recordings, B-roll, logos, and notes there.
3. Ask Codex to use Video Use to inventory and transcribe.
4. Review the proposed editorial strategy.
5. Approve the cut plan.
6. Build HyperFrames scenes for moments that need visual explanation.
7. Render or export HyperFrames overlays/assets.
8. Let Video Use assemble, subtitle, grade, and verify.

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
- Audio fades
- Subtitle burn-in on the final timeline
- Color grade per segment
- Final assembly and self-eval

