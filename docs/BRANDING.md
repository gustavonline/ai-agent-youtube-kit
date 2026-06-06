# Branding And Assets

Do this before producing your first real video. The goal is to make every new project inherit your channel identity instead of drifting into generic AI-video styling.

## Brand Files

- `DESIGN.md` - human-readable brand and motion direction.
- `assets/brand-tokens.css` - reusable CSS variables for HyperFrames projects.
- `assets/` - shared logos, background plates, screenshots, sound beds, and reference stills.
- `video-projects/<project>/DESIGN.md` - project-specific notes that should point back to the root design system.

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

Keep large raw footage in `footage/`, not `assets/`.

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

1. `DESIGN.md`
2. `assets/brand-tokens.css`
3. Each active `video-projects/<project>/DESIGN.md`

## HyperFrames Rules

- Read `DESIGN.md` before editing a composition.
- Use CSS tokens from `assets/brand-tokens.css` before adding new hex values.
- Keep project-local copies of `brand-tokens.css` in each HyperFrames project so old projects keep rendering even if the root brand evolves.
- Use local fonts with `@font-face` for final renders when typography matters.
- Do not ship borrowed placeholder names, handles, logos, or colors from example projects.

## Video Use Rules

- Store raw footage under `footage/<slug>/`.
- Let Video Use write outputs under `footage/<slug>/edit/`.
- Keep project memory in `edit/project.md`.
- Treat HyperFrames renders as assets Video Use can assemble into the final timeline.

## Brand Change Checklist

- Root `DESIGN.md` updated.
- `assets/brand-tokens.css` updated.
- Logo and mark assets added.
- Project `DESIGN.md` files updated.
- Captions checked at phone size.
- Thumbnail frame planned before final export.
- No old brand strings found:

```bash
rg -n "AIS|aiautomationsociety|Nate|placeholder|TODO|YourLogo|figma.com" .
```

