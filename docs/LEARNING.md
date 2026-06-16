# Learning Loop

This repo improves through project memory, not hidden state.

Use simple tracked files that a human can inspect, edit, and carry into a
branded clone:

- `PROJECT_MEMORY.md` for durable brand and production lessons.
- `channel/STYLE_GUIDE.md` for channel-level lessons from references and performance.
- `channel/REFERENCES.md` for the index of analyzed reference videos.
- `DESIGN.md` for stable brand identity decisions.
- `MOTION_PHILOSOPHY.md` for general motion principles.
- `video-projects/<project>/DESIGN.md` for project-specific decisions.
- `footage/<slug>/edit/project.md` for session notes and render history.

## Before A New Project

Read in this order:

1. `DESIGN.md`
2. `PROJECT_MEMORY.md`
3. `MOTION_PHILOSOPHY.md`
4. `channel/PROFILE.md`
5. `channel/STYLE_GUIDE.md`
6. relevant `channel/references/*/analysis.md`
7. relevant `video-projects/<template>/DESIGN.md`
8. source footage notes under `footage/<slug>/`

Use these files to choose caption style, pacing, callouts, grade direction, and
which prior examples to reuse.

## After A Finished Project

Update only what earned its place:

1. Append session facts to `footage/<slug>/edit/project.md`.
2. Add one concise row to `PROJECT_MEMORY.md` if the project created a reusable pattern.
3. Add one concise row to `channel/STYLE_GUIDE.md` if performance or references proved a channel-level pattern.
4. Update `DESIGN.md` only when the brand itself changed.
5. Update `MOTION_PHILOSOPHY.md` only when the lesson is general across videos.
6. Update a project `DESIGN.md` only for project-specific constraints.

Do not turn every render into a new rule. Keep the memory small enough that it
actually gets read.

## What Counts As A Lesson

Good lessons are concrete:

- a caption chunking style that stayed readable
- a motion pattern that clarified a repeated concept
- a cut strategy that improved pacing
- a color/grade choice that worked for the channel
- a mistake that should not be repeated
- a reference-derived hook or CTA mechanic that fits this channel
- a packaging pattern supported by channel performance

Weak lessons are vague:

- "make it more dynamic"
- "use better animations"
- "improve branding"
- "look more premium"

Rewrite weak lessons into specific decisions before adding them.

## Project Memory Entry Shape

Use this format when adding a reusable lesson:

```text
- Pattern: <short name>
  - Works when: <specific context>
  - Avoid when: <specific context>
  - Example project: <project or footage slug>
```

## Reference Learning Entry Shape

Use this format in `channel/STYLE_GUIDE.md` when promoting a reference lesson:

```text
- Pattern: <short name>
  - Use when: <specific context>
  - Avoid when: <specific context>
  - Evidence: <reference analysis path or published video result>
```
