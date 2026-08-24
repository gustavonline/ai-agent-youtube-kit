# Learning Loop

This repo improves through project memory, not hidden state.

Use simple tracked files that a human can inspect, edit, and carry into a
branded clone:

- `workspace/learning/PROJECT_MEMORY.md` for durable brand and production lessons.
- `workspace/channel/STYLE_GUIDE.md` for channel-level lessons from references and performance.
- `workspace/references/REFERENCES.md` for the index of analyzed reference videos.
- `workspace/channel/DESIGN.md` for stable brand identity decisions.
- `workspace/learning/MOTION_PHILOSOPHY.md` for general motion principles.
- `workspace/engine/motion-adapters/video-projects/<slug>/DESIGN.md` for optional motion-adapter decisions.
- `workspace/productions/<slug>/learning.json` for the ACS run's local learning slots and
  workspace notes for session history.

## Before A New Content Run

Read in this order:

1. `workspace/channel/DESIGN.md`
2. `workspace/learning/PROJECT_MEMORY.md`
3. `workspace/learning/MOTION_PHILOSOPHY.md`
4. `workspace/channel/PROFILE.md`
5. `workspace/channel/STYLE_GUIDE.md`
6. relevant `workspace/references/*/analysis.md`
7. relevant optional `workspace/engine/motion-adapters/video-projects/<slug>/DESIGN.md`
8. source notes under the chosen ACS workspace

Use these files to choose caption style, pacing, callouts, grade direction, and
which prior examples to reuse.

## After A Finished Project

Update only what earned its place:

1. Append session facts to the workspace's local notes or `learning.json`.
2. Add one concise row to `workspace/learning/PROJECT_MEMORY.md` if the project created a reusable pattern.
3. Add one concise row to `workspace/channel/STYLE_GUIDE.md` if performance or references proved a channel-level pattern.
4. Update `workspace/channel/DESIGN.md` only when the brand itself changed.
5. Update `workspace/learning/MOTION_PHILOSOPHY.md` only when the lesson is general across videos.
6. Update an optional adapter `workspace/engine/motion-adapters/video-projects/<slug>/DESIGN.md` only for adapter-specific
   constraints.

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
  - Example workspace: <workspace slug>
```

## Reference Learning Entry Shape

Use this format in `workspace/channel/STYLE_GUIDE.md` when promoting a reference lesson:

```text
- Pattern: <short name>
  - Use when: <specific context>
  - Avoid when: <specific context>
  - Evidence: <reference analysis path or published video result>
```
