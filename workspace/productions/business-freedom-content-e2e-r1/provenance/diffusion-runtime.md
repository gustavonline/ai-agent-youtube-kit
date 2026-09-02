# Diffusion runtime provenance

## Preserved landscape tracer

- ACS-owned source: `diffusion-project/index.tsx`
- Source SHA-256: `d879ae2ecf2e3815628e0e53892f3f55a104c62f10d2ecb5a135a6cbc06f3edb`
- Reviewed runtime revision: Diffusion r5 `67a8a669ed81318406560f2669fc3c505e3abed1`
- Exact 42-second MP4 SHA-256: `ebbbdafebeaafa21b49b7776d4f1b7b05a8197a4111666c10e80b0955aeb26c9`
- Truth boundary: code-native motion/landscape tracer, not owner-recorded talking-head acceptance.

The landscape source and MP4 bytes are preserved unchanged from lead Review.

## Content-family adaptations

- ACS-owned source: `diffusion-family-project/index.tsx`
- External fork: `https://github.com/onlinesourdough/editor.git`
- Tested branch: `codex/diffusion-upstream-browser-companion-r6`
- Exact revision: `71a306fb33d06f969114a47e9eba85aa47cef395`
- Official upstream: `https://github.com/diffusionstudio/editor.git`
- Reviewed upstream base: `635a2907d9dd717879d6f7bdf9a78ee42910415c`
- Upstream PR: `https://github.com/diffusionstudio/editor/pull/54`

The external editor repository remains separately owned and unchanged in Git.
Electron/DAPI are authoritative for compilation, capture, and export. The
ordinary browser companion is read-only and human-facing. The ACS project uses
only native shapes and text; it contains no media, HTML paint, WebGPU, shaders,
cloud AI, credits, remote URL, or editable ADS dependency.

ADS is optional at system level. This production uses only its already accepted
immutable DESIGN snapshot and three selected reference keyframes recorded in
`design_handoff`.
