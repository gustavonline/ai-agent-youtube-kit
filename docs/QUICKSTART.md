# Quickstart

## Repository proof

Install Node.js 22 or newer. The checks have no package dependencies:

```text
npm test
npm run check:graph
npm run check:repository
```

## Configure the clone

Use the setup skill to fill only resolved business, audience, promise, channel,
cadence, and delivery facts in `workspace/channel/`. Do not create a production
until a real outcome exists. Named channels are not required by the graph.

## Start a production

Create `workspace/productions/<slug>/` and copy the relevant templates. Add or
reference truthful local artifact files within that boundary, then write
`content-graph.json` using `docs/CONTENT_GRAPH.md` and the neutral fixture.

For ordinary video, use the `diffusion-studio` skill:

```text
node workspace/engine/scripts/diffusion-studio.mjs setup
node workspace/engine/scripts/diffusion-studio.mjs check
node workspace/engine/scripts/diffusion-studio.mjs open <production-project>
```

Open the returned one-time loopback URL only in the Codex built-in browser.
Make edits and exports through Electron/DAPI, not the browser shell. After the
human reviews the Diffusion export, register it as a master node and register
every derivative separately.

Validate before handoff:

```text
node workspace/engine/scripts/check-content-graph.mjs <production>/content-graph.json
node workspace/engine/scripts/check-content-graph.mjs <production>/content-graph.json <production>/publisher-handoff.json
```

The second command succeeds only when every selected node has its own approval.
It does not post.

## Optional helpers

Local Whisper setup and reference analysis remain available under
`workspace/engine/scripts/`. They may require Python/FFmpeg but are not needed
to validate or hand off a production.
