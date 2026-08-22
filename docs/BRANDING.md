# Branding And Assets

Do this before producing the first real content run. The goal is to make every
ACS workspace inherit the channel identity instead of drifting into generic
agent-video styling.

## Brand Files

- `DESIGN.md` - human-readable brand and motion direction.
- `PROJECT_MEMORY.md` - reusable lessons from finished projects.
- `channel/PROFILE.md` - channel promise, audience, content lanes, and CTAs.
- `channel/brand.json` - ACS-owned, schema-validated channel policy, cadence,
  and delivery defaults copied into new workspaces.
- `channel/STYLE_GUIDE.md` - condensed reference and performance lessons.
- `assets/brand-tokens.css` - reusable CSS variables for HyperFrames projects.
- `assets/` - shared logos, background plates, screenshots, sound beds, and reference stills.
- `video-projects/<slug>/DESIGN.md` - optional HyperFrames adapter notes that
  should point back to the root design system.

## Recommended Asset Layout

```text
assets/
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
not `assets/`. The ignored `footage/` directory remains a legacy source-side
compatibility location.

## Brand Intake

Fill this out when changing direction:

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

Then update:

1. `channel/PROFILE.md`
2. `channel/brand.json`
3. `channel/STYLE_GUIDE.md`
4. `DESIGN.md`
5. `PROJECT_MEMORY.md`
6. `assets/brand-tokens.css`
7. Each active optional `video-projects/<slug>/DESIGN.md`

## HyperFrames Rules

- Read `DESIGN.md` before editing a composition.
- Use CSS tokens from `assets/brand-tokens.css` before adding new hex values.
- Keep project-local copies of `brand-tokens.css` in each HyperFrames project so old projects keep rendering even if the root brand evolves.
- Use local fonts with `@font-face` for final renders when typography matters.
- Do not ship borrowed temporary names, handles, logos, or colors from example projects.

## External Editor Adapter Rules

- Store source media under `examples/<slug>/sources/` (or another explicitly
  chosen ACS workspace).
- Keep ACS contracts and generated proof under the workspace; external editors
  may consume them but must not become the owner of ACS truth.
- Keep durable memory in `PROJECT_MEMORY.md` and factual session notes in the
  workspace's local notes when they exist.
- Treat HyperFrames renders as optional assets an external editor can assemble
  into a final timeline.

## Brand Change Checklist

- Root `DESIGN.md` updated.
- `channel/PROFILE.md` updated.
- `channel/STYLE_GUIDE.md` updated with reusable reference and performance lessons.
- `PROJECT_MEMORY.md` updated with durable lessons only.
- `assets/brand-tokens.css` updated.
- Logo and mark assets added.
- Project `DESIGN.md` files updated.
- Captions checked at phone size.
- Thumbnail frame planned before final export.
- No old brand strings found:

```bash
rg -n "temporary|TODO|YourLogo|example.com|your-channel" .
```
