---
name: setup-content-system
description: "Configure a cloneable ACS workspace before its first real production without creating content or media state."
---

# Setup Content System

Resolve only missing business, audience, offer/promise, channel-policy,
cadence, and delivery-default decisions. Keep unknowns unknown. Do not invent
posting authority.

1. Read `workspace/channel/PROFILE.md`, `STYLE_GUIDE.md`, `DESIGN.md`, and
   `workspace/learning/PROJECT_MEMORY.md`.
2. Update the profile and style files with resolved durable facts only.
3. Treat `workspace/channel/brand.json` as optional human-readable defaults;
   production graph validation never requires a named channel.
4. Run `npm run check:repository`. Do not create a production fixture.
5. For future video work, route Diffusion readiness through the
   `diffusion-studio` skill. Do not copy the editor into ACS.

Accepted visual direction is optional. If setup exposes a material design gap,
suggest the bounded ADS route without executing it automatically or blocking
otherwise complete ACS setup.

Setup is complete when the owner can state the next real outcome and the
repository checks pass. The production skill creates the first production only
after that outcome exists.
