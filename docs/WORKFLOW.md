# Workflow

## Clone To Channel Workflow

1. Fill `channel/PROFILE.md`.
2. Add known published-video data to `channel/published-videos.csv`.
3. Analyze 3-10 reference videos with `scripts/analyze-reference-video.py`.
4. Condense reusable lessons into `channel/STYLE_GUIDE.md`.
5. Tailor `DESIGN.md`, `PROJECT_MEMORY.md`, and `assets/brand-tokens.css`.
6. Copy a starter project from `video-projects/short-form-template`.

## Reference Video To Style Lesson

```bash
python3 scripts/analyze-reference-video.py "<reference-video-url>"
```

Then fill:

```text
channel/references/<slug>/analysis.md
```

Update:

```text
channel/REFERENCES.md
channel/STYLE_GUIDE.md
```

## Raw Footage To Final Video

1. Run `python3 scripts/new-video.py <slug>`.
2. Put source clips, screen recordings, B-roll, logos, and notes in `footage/<slug>/`.
3. Fill `footage/<slug>/edit/video-brief.md`.
4. Run local Whisper transcription and pack transcripts.
5. Ask Codex to use Video Use to inventory `edit/takes_packed.md`.
6. Review the proposed editorial strategy.
7. Save the approved cut plan to `edit/cut-plan.md`.
8. Build HyperFrames scenes for moments that need visual explanation.
9. Render or export HyperFrames overlays/assets.
10. Let Video Use assemble, subtitle, grade, and verify.
11. Run packaging review.
12. Run final review.

```bash
.venv/bin/python scripts/transcribe-local-whisper.py footage/<slug> --model large --pack
```

## Folder Pattern

```text
footage/<slug>/
  raw clips here
  edit/
    project.md
    video-brief.md
    takes_packed.md
    cut-plan.md
    packaging-review.md
    final-review.md
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
- Platform subscribe/CTA
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

## When To Use Reference Analysis

- Learning a channel style from selected examples
- Breaking down hooks, CTAs, pacing, captions, and proof mechanics
- Building `channel/STYLE_GUIDE.md`
- Finding reusable thumbnail/title patterns

Do not use reference analysis as a substitute for editing your own raw footage.
