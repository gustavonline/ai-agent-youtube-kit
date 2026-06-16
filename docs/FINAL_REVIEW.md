# Final Review

Final review is the file-based version of CreatorGrowth's AI Final Review. It
is an advisory gate before publishing, not a hosted dashboard.

## When To Run

Run final review after a candidate export exists and before marking the project
finished.

```text
footage/<slug>/edit/final.mp4
```

## Inputs

Read:

1. `DESIGN.md`
2. `PROJECT_MEMORY.md`
3. `MOTION_PHILOSOPHY.md`
4. `channel/PROFILE.md`
5. `channel/STYLE_GUIDE.md`
6. `channel/published-videos.csv`
7. relevant reference analyses under `channel/references/`
8. `footage/<slug>/edit/project.md`
9. `footage/<slug>/edit/cut-plan.md`
10. `footage/<slug>/edit/packaging-review.md`

## Output

Write:

```text
footage/<slug>/edit/final-review.md
```

Use:

```text
templates/final-review.md
```

## Review Rubric

Score each category from 1-10:

- Hook: first seconds create a clear reason to keep watching.
- Pacing: no obvious dead air, repeated point, or confusing jump.
- Clarity: the viewer can explain the promise after watching.
- Visual fit: captions, graphics, screen recordings, and grade match the brand.
- Audio/captions: speech is intelligible and captions are readable on phone.
- Packaging fit: title/thumbnail truthfully match the final edit.
- Channel fit: it belongs in this channel's style and audience promise.

## Procedure

1. Watch the final export or inspect representative frames if full playback is not available.
2. Compare the edit to the approved cut plan.
3. Check captions and on-screen text at mobile size.
4. Check that motion graphics clarify rather than decorate.
5. Compare packaging to the actual final edit.
6. Write timestamped findings with required fixes.
7. Mark publish readiness.

## Learning

Append factual session notes to:

```text
footage/<slug>/edit/project.md
```

Promote only durable lessons:

- `PROJECT_MEMORY.md` for reusable production/editing patterns.
- `channel/STYLE_GUIDE.md` for channel-level content style.
- `DESIGN.md` only for stable brand decisions.
- `MOTION_PHILOSOPHY.md` only for general motion principles.
