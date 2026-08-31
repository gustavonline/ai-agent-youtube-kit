---
name: freecut-studio
description: "Set up, check, open, use, or recover the one external FreeCut browser Studio for an ACS video outcome."
---

# FreeCut Studio

FreeCut is the only normal Studio for owner-recorded long-form, shorts,
trims/cuts, audio/music, captions/subtitles, overlays/assets, and supervised
export. There is no desktop-app requirement. FreeCut's external native
workspace is canonical; ACS stores no bridge manifest or editor copy.

## Fixed checkout

- macOS/Linux: `~/.local/share/freecut`
- Windows: `%LOCALAPPDATA%\freecut`
- origin: `https://github.com/walterlow/freecut.git`
- pinned revision: `4d62e8082c5eb387a96275bcbd323d28f6e41a62`
- declared package manager: `npm@11.8.0`

Never scan for or create a second checkout. Stop on wrong origin, dirty owner
state, or a revision mismatch. Never reset, stash, delete, or overwrite owner
state.

## Setup

Setup is an explicit write action. Clone the official repository to the fixed
path, check out the pin detached, then use the declared npm version:

```text
corepack npm@11.8.0 ci --ignore-scripts
corepack npm@11.8.0 run build
```

Lifecycle scripts must stay disabled during install; the explicit build still
runs. Preserve task evidence for origin, pin, lockfile, Node version, exact npm
version, install command, build command, and Git cleanliness. Do not invent a
provenance marker.

## Check

Keep check mode read-only:

```text
node workspace/engine/scripts/freecut-studio.mjs check
```

Also run `npm ls --omit=dev`, `npm run headless:test:node`, and preserve the full
`npm audit --omit=dev` output. At the pinned profile, the known public result is
eight findings (one moderate, five high, two critical). Treat finding-count or
dependency drift as stale evidence. Browser reachability remains separately
adjudicated: the known `adm-zip`/`tar` paths are Node/ONNX install-only;
`protobufjs` textual proto parsing, `seroval` SSR/dehydration, and
`sharp`/libvips are outside FreeCut's used SPA browser paths at this pin.

## Open and work

From the ACS repository root:

```text
node workspace/engine/scripts/freecut-studio.mjs serve
```

The launcher validates the fixed checkout, then runs the same cross-platform
Node/Vite command with no shell wrapper:

```text
npm run preview -- --host 127.0.0.1 --port 4173 --strictPort
```

After the server reports ready, open `http://127.0.0.1:4173/` in the Codex
in-app browser. Do not call an OS browser, bind a public interface, or automate
folder permissions. The human chooses the FreeCut workspace folder manually.

Preserve a single-writer handoff: human save/handoff, agent edit through
FreeCut API v1 with `expectedRevision`, then human reload/review. Do not bypass
revision conflicts or use a destructive in-place path.

After human approval, copy the export into the active production and register
it as a `master` node with its real hash, provenance, edges, and independent
review reference. Register excerpts/adaptations as separate derivative nodes;
master approval never approves them.

## Cross-platform evidence

The launcher uses `npm.cmd` only where Windows requires it; arguments and
loopback URL are otherwise identical. Inspect documented invocations with:

```text
node workspace/engine/scripts/freecut-studio.mjs describe --platform darwin
node workspace/engine/scripts/freecut-studio.mjs describe --platform linux
node workspace/engine/scripts/freecut-studio.mjs describe --platform win32
```

Configuration evidence is not physical execution. Report the OS actually
tested and disclose untested Windows/Linux browser/export behavior.

## Recover

Do not auto-upgrade or create a second checkout. On wrong origin, dirty state,
missing build, failed tests, or revision conflict, stop and report the smallest
manual recovery. Updating the pin requires a separately reviewed ACS change
and a complete revalidation.
