# Final Review

Final review is a file-based advisory gate for an ACS workspace. It is a local
review step before separate publishing authorization, not a hosted dashboard.

## When To Run

Run final review after a candidate export exists. Record the semantic
evaluation after final review and before marking the deliberate attempt
successful.

```text
<workspace>/renders/long.mp4
```

## Inputs

Read:

1. `workspace/channel/DESIGN.md`
2. `workspace/learning/PROJECT_MEMORY.md`
3. `workspace/learning/MOTION_PHILOSOPHY.md`
4. `workspace/channel/PROFILE.md`
5. `workspace/channel/STYLE_GUIDE.md`
6. `workspace/channel/published-videos.csv`
7. relevant reference analyses under `workspace/references/`
8. `<workspace>/learning.json` and any local session notes
9. `<workspace>/edit-plan.json`
10. `<workspace>/packaging-review.md`, when supplied
11. `<workspace>/results/run-result.json`

## Output

Write:

```text
workspace/productions/<slug>/final-review.md
```

Use:

```text
workspace/engine/templates/final-review.md
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
8. Write the separate semantic assessment and run `acs semantic-eval`; a
   passing static review alone does not accept the content result.

## Learning

Append factual session notes to the workspace's local notes or `learning.json`:

```text
workspace/productions/<slug>/learning.json
```

Promote only durable lessons:

- `workspace/learning/PROJECT_MEMORY.md` for reusable production/editing patterns.
- `workspace/channel/STYLE_GUIDE.md` for channel-level content style.
- `workspace/channel/DESIGN.md` only for stable brand decisions.
- `workspace/learning/MOTION_PHILOSOPHY.md` only for general motion principles.
