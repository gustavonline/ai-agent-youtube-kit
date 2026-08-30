# Packaging

This is the AI-first packaging layer around an ACS content workspace: titles,
thumbnails, and click psychology live in files instead of a hosted dashboard.
The executable publish package is produced by `acs package`; this document is
the optional human/agent packaging review around that handoff.

## Inputs

Before packaging a video, read:

1. `workspace/channel/PROFILE.md`
2. `workspace/channel/STYLE_GUIDE.md`
3. `workspace/channel/published-videos.csv`
4. relevant `workspace/references/*/analysis.md`
5. the workspace `edit-plan.json`, `content-brief.md`, and `recording-plan.md`
6. `workspace/channel/DESIGN.md`
7. `workspace/learning/PROJECT_MEMORY.md`

## Output

Write the optional human review to:

```text
workspace/productions/<slug>/packaging-review.md
```

Use:

```text
workspace/engine/templates/packaging-review.md
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
- consistent with `workspace/channel/DESIGN.md` and `workspace/channel/STYLE_GUIDE.md`
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

### Bounded thumbnail ownership example

ACS chooses the content promise, headline/copy, CTA, subject or proof object,
target format, and delivery constraints. When accepted direction already
supports the concept, ACS records the reviewed choice in `packaging-review.md`
and `edit-plan.json.creative_direction.thumbnail_choice` and proceeds without
ADS. When the concept instead needs new composition, hierarchy, typography,
color, or imagery treatment, AIOS may suggest only that bounded work to ADS.
ADS returns ordinary accepted `DESIGN.md` direction and the selected reviewed
asset; editable OpenPencil source and design proof stay with its design owner.
ACS then records the reviewed choice and packages the content through its
existing approval and proof flow.

This suggestion never runs ADS automatically or makes it a predecessor. If
OpenPencil is unavailable or unselected, ADS or another explicit design owner
may return equivalent portable direction and an ordinary asset; unrelated ACS
content continues. Do not add a cross-System schema, asset adapter, or posting
automation for this handoff.

## Packaging Review Procedure

1. Summarize the actual promise of the edit.
2. Generate title candidates from different patterns.
3. Generate thumbnail concepts from different visual mechanisms.
4. Score each title and concept.
5. Pick the strongest title/thumbnail pair.
6. List exact changes needed before publish.
7. Save the chosen pair in `workspace/productions/<slug>/packaging-review.md` (or the
   corresponding local workspace).

## Learning

After publishing, compare performance against `workspace/channel/published-videos.csv`.
Only promote lessons to `workspace/channel/STYLE_GUIDE.md` when they are supported by
reference analysis or real channel results.
