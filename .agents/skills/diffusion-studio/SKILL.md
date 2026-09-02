---
name: diffusion-studio
description: "Set up, check, open, inspect, or stop the pinned external Diffusion Studio route for an ACS video production."
---

# Diffusion Studio

Use the reviewed external Diffusion fork as ACS's only ordinary video Studio.
Read [`docs/DIFFUSION_STUDIO.md`](../../../docs/DIFFUSION_STUDIO.md) before
setup, a re-pin, or browser-companion work.

Run the small launcher from the ACS root:

```text
node workspace/engine/scripts/diffusion-studio.mjs setup
node workspace/engine/scripts/diffusion-studio.mjs check
node workspace/engine/scripts/diffusion-studio.mjs open workspace/productions/<slug>/diffusion-project
node workspace/engine/scripts/diffusion-studio.mjs status
node workspace/engine/scripts/diffusion-studio.mjs logs
node workspace/engine/scripts/diffusion-studio.mjs stop
```

`setup` is an explicit external write and refuses a mismatched checkout.
Other commands stop on the wrong pin, remotes, upstream base, dirty owner state,
or missing build. Never vendor editor code in ACS, auto-update the checkout,
reset owner state, or launch an OS browser.

`open` returns a one-time URL as JSON. Open it only in Codex's built-in
browser. Electron/DAPI remain authoritative; the companion is a local-only,
read-only human shell for preview, play/pause, scrub, and inspection. Require a
hidden or truthfully reported minimized-fallback host, `egressAttempts: 0`,
matching compiled/applied identities, explicit stop cleanup, and DAPI survival.

After human review, register every export and derivative separately with its
real hash, provenance, edges, and independent review. Approval never inherits,
and publishing still requires separate authority.
