# ACS production notes

**Production slug:** `business-freedom-content-e2e-r1`
**Started:** 2026-09-02
**Capture format:** preserved 42-second 1920×1080 master plus two 24-second 1080×1920 code-native derivatives, 30 fps

## Session log

| Date | Work | Artifact/review reference |
| --- | --- | --- |
| 2026-09-02 | Accepted the bounded owner brief and immutable ADS r1 handoff inside this production | `content-brief.md`, `design-acceptance.md` |
| 2026-09-02 | Selected only DESIGN.md and the three reviewed composition keyframes | `design-input/` |
| 2026-09-02 | Authored and type-checked the self-contained code-native motion source | `diffusion-project/`, `review/technical-review.md` |
| 2026-09-02 | DAPI-checked and exported the 42-second master; inspected renderer and MP4 frames across all eight beats | `artifacts/`, `proof/`, `review/final-review.md` |
| 2026-09-02 | Reviewed three useful keyframe artifacts independently | `artifacts/keyframes/`, `review/packaging-review.md` |
| 2026-09-02 | Extended the reviewed tracer into a graph-bound content family with two distinct vertical scripts, captions, a text post, a post visual, and a newsletter draft | `diffusion-family-project/`, `deliverables/`, `short-01-script.md`, `short-02-script.md` |

## Decisions

- Decision: use eight equal 5.25-second beats for a 42-second master.
  - Reason: preserves the ADS eight-beat story while giving each open caption at least 5.25 seconds.
- Decision: use no media nodes, custom fonts, HTML paint, WebGPU, shaders, cloud AI, or external assets.
  - Reason: honor the explicit acceptance-production runtime constraint and keep the hidden browser companion self-contained.
- Decision: preserve the landscape source/master bytes and add a separate ACS-owned r6 family project.
  - Reason: the reviewed tracer remains reproducible while new vertical scenes can be independently versioned and approved.

## Graph revisions

| Family version | Changed node/version | Reason |
| --- | --- | --- |
| 1 | Initial nodes | First rendered, reviewed production package |
| 2 | Brief/cut plan plus content-family nodes | Added two vertical adaptations, scripts/captions, post, post visual, newsletter, provenance, reviews, and supervised family handoff |

## Durable lessons

No channel or system-level lesson is promoted until lead Review confirms the experiment.
