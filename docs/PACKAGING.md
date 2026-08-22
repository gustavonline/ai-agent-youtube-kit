# Packaging

This is the AI-first packaging layer around an ACS content workspace: titles,
thumbnails, and click psychology live in files instead of a hosted dashboard.
The executable publish package is produced by `acs package`; this document is
the optional human/agent packaging review around that handoff.

## Inputs

Before packaging a video, read:

1. `channel/PROFILE.md`
2. `channel/STYLE_GUIDE.md`
3. `channel/published-videos.csv`
4. relevant `channel/references/*/analysis.md`
5. the workspace `edit-plan.json`, `content-brief.md`, and `recording-plan.md`
6. `DESIGN.md`
7. `PROJECT_MEMORY.md`

## Output

Write the optional human review to:

```text
examples/<slug>/packaging-review.md
```

Use:

```text
templates/packaging-review.md
```

## Title Bench

Generate 6-12 titles before choosing one. Score them against:

- clarity: viewer understands the topic immediately
- specificity: concrete tool, result, number, problem, or contrast
- curiosity: there is a gap worth clicking
- truthfulness: the title matches the actual edit
- channel fit: it sounds like this channel, not a generic viral account
- search/context: useful keywords are present when relevant

Good title patterns:

- `I Built <specific system> To <specific result>`
- `<Tool/idea> Is Better When You Use It Like This`
- `I Tested <thing> So You Do Not Have To`
- `<number> <things> That Changed <workflow>`
- `Stop <common behavior>. Do <specific alternative>.`

Avoid:

- vague AI hype
- impossible claims
- titles that require too much background
- cleverness that hides the actual topic
- copying a reference title too closely

## Thumbnail Bench

Generate 3-6 thumbnail concepts before choosing one. Score them against:

- one readable visual idea
- strong contrast at phone size
- proof object: screen, result, artifact, score, before/after, or recognizable tool
- minimal text, preferably 1-4 words
- consistent with `DESIGN.md` and `channel/STYLE_GUIDE.md`
- honest relationship to the video

Useful visual patterns:

- artifact hero: show the thing built or generated
- before/after: old workflow versus new workflow
- scorecard: clear rating, stamp, or pass/fail
- tool contrast: tool A versus tool B, but only when the video really compares them
- workflow map: small system diagram when the system is the story

Avoid:

- tiny UI text
- cluttered grids
- stock-looking backgrounds
- logos or faces copied from references without rights
- designs that work only at desktop size

## Packaging Review Procedure

1. Summarize the actual promise of the edit.
2. Generate title candidates from different patterns.
3. Generate thumbnail concepts from different visual mechanisms.
4. Score each title and concept.
5. Pick the strongest title/thumbnail pair.
6. List exact changes needed before publish.
7. Save the chosen pair in `examples/<slug>/packaging-review.md` (or the
   corresponding local workspace).

## Learning

After publishing, compare performance against `channel/published-videos.csv`.
Only promote lessons to `channel/STYLE_GUIDE.md` when they are supported by
reference analysis or real channel results.
