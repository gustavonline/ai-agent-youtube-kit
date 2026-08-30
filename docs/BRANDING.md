# Branding And Assets

Do this before producing the first real content run. The goal is to make every
ACS workspace inherit accepted channel identity instead of drifting into
generic agent-video styling. ACS consumes and applies the direction; ADS or
another explicit design owner owns new portable visual judgment and reusable
visual assets.

FreeCut is the one normal supervised video Studio route. Remotion or
generic code-based motion may produce a bounded asset only when a concrete
deliverable needs it. Retained HyperFrames/editor material is migration/recovery
input only and is not part of ordinary brand setup.

## Brand Files

- `workspace/channel/DESIGN.md` - accepted human-readable brand and motion
  direction copied into ACS as a production snapshot.
- `workspace/learning/PROJECT_MEMORY.md` - reusable lessons from finished projects.
- `workspace/channel/PROFILE.md` - channel promise, audience, content lanes, and CTAs.
- `workspace/channel/brand.json` - ACS-owned, schema-validated channel policy, cadence,
  and delivery defaults copied into new workspaces.
- `workspace/channel/STYLE_GUIDE.md` - condensed reference and performance lessons.
- `workspace/channel/assets/brand-tokens.css` - accepted CSS variables for ACS
  outputs and any bounded code-based motion asset.
- `workspace/channel/assets/` - shared logos, background plates, screenshots, sound beds, and reference stills.
- `workspace/engine/motion-adapters/video-projects/<slug>/DESIGN.md` - retained
  legacy notes consulted only for explicit migration/recovery.

## Recommended Asset Layout

```text
workspace/channel/assets/
  brand-tokens.css
  logo/
    logo-light.png
    logo-dark.png
    mark.svg
  backgrounds/
    grid-dark.png
    studio-plate.png
  fonts/
    BrandSans-Regular.woff2
    BrandSans-Bold.woff2
  audio/
    intro-bed.wav
    click.wav
  references/
    channel-thumbnail-style.png
    favorite-video-frame.png
```

Keep large source media in the active ACS workspace's `sources/` directory,
not the shared channel asset area. Source media belongs under the production
workspace's `sources/` directory.

## Accepted Brand Intake

Use this to receive direction already accepted by the visual-design owner:

```text
Channel promise:
Audience:
Mood:
Energy level:
Primary colors:
Accent colors:
Fonts:
Logo files:
Caption style:
Thumbnail style:
Examples to imitate:
Examples to avoid:
```

Then copy the accepted values into:

1. `workspace/channel/PROFILE.md`
2. `workspace/channel/brand.json`
3. `workspace/channel/STYLE_GUIDE.md`
4. `workspace/channel/DESIGN.md`
5. `workspace/learning/PROJECT_MEMORY.md`
6. `workspace/channel/assets/brand-tokens.css`
7. For an explicit migration/recovery task only, the relevant retained
   `workspace/engine/motion-adapters/video-projects/<slug>/DESIGN.md`

If this intake exposes a material visual-design gap or requires new OpenPencil
work, AIOS may suggest a bounded ADS route. Do not run ADS automatically, make
it a mandatory predecessor, or create a cross-System contract. ACS may proceed
from already accepted direction supplied by any explicit design owner.

## Legacy HyperFrames Migration/Recovery Rules

- Use this section only for an explicitly requested migration/recovery task.
- Read `workspace/channel/DESIGN.md` before recovering a composition.
- Use CSS tokens from `workspace/channel/assets/brand-tokens.css` before adding new hex values.
- Keep project-local copies of `brand-tokens.css` so retained projects remain reproducible during recovery.
- Use local fonts with `@font-face` for final renders when typography matters.
- Do not ship borrowed temporary names, handles, logos, or colors from example projects.

## Legacy Editor/Motion Recovery Rules

- Use FreeCut for the normal supervised video edit; do not choose a retained
  editor or HyperFrames project as a parallel Studio.
- Store source media under `workspace/productions/<slug>/sources/` (or another explicitly
  chosen ACS workspace).
- Keep ACS contracts and generated proof under the workspace; external editors
  involved in explicit migration/recovery must not become the owner of ACS truth.
- Keep durable memory in `workspace/learning/PROJECT_MEMORY.md` and factual session notes in the
  workspace's local notes when they exist.
- Treat a recovered HyperFrames render as legacy input returned to the normal
  FreeCut/ACS flow, not an ordinary production option.

## Accepted Brand Change Checklist

- Root `workspace/channel/DESIGN.md` replaced with accepted direction.
- `workspace/channel/PROFILE.md` updated.
- `workspace/channel/STYLE_GUIDE.md` updated with reusable reference and performance lessons.
- `workspace/learning/PROJECT_MEMORY.md` updated with durable lessons only.
- `workspace/channel/assets/brand-tokens.css` replaced with accepted tokens.
- Logo and mark assets added.
- Any explicitly recovered legacy `DESIGN.md` updated from the accepted snapshot.
- Captions checked at phone size.
- Thumbnail frame planned before final export.
- No old brand strings found:

```bash
rg -n "temporary|TODO|YourLogo|example.com|your-channel" .
```
