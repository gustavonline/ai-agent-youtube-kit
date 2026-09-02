# Technical review — landscape master and vertical family

**Production:** `business-freedom-content-e2e-r1`
**Reviewer:** `diffusion-content-family-r1`
**Reviewed:** 2026-09-02

## Runtime provenance

- External fork checkout: clean branch `codex/diffusion-upstream-browser-companion-r6` at `71a306fb33d06f969114a47e9eba85aa47cef395`.
- Official `origin`: `https://github.com/diffusionstudio/editor.git`; merge-base and reviewed official main: `635a2907d9dd717879d6f7bdf9a78ee42910415c`.
- Fork remote: `https://github.com/onlinesourdough/editor.git`; live branch equals the pin.
- DAPI/desktop version: `0.204.1`; Node `v22.21.1`; npm lock install and declared desktop package command succeeded.
- Build-time browser values were read from upstream `.env.example` into the process only. No `.env` or credential file was written.
- The external checkout remained Git-clean after build, DAPI check, capture, and export.

## Preserved landscape master

- Source `diffusion-project/index.tsx`: unchanged at `sha256:d879ae2ecf2e3815628e0e53892f3f55a104c62f10d2ecb5a135a6cbc06f3edb`.
- DAPI check on r6: 305 nodes, depth 5, duration 42 seconds, no issues.
- Delivery MP4 remains unchanged at `sha256:ebbbdafebeaafa21b49b7776d4f1b7b05a8197a4111666c10e80b0955aeb26c9`.
- Delivery technique: H.264/yuv420p, 1920×1080, 30 fps, 1,260 frames, 42.000 seconds, silent by design, 4,709,752 bytes.
- A separate r6 proof-export wrote `/tmp/business-freedom-master-r6-proof.mp4`: same technique, dimensions, frames, duration, and size; encoder bytes differed at `sha256:34ced9811f36cbf3e07573fe5d66524e293dcf0cc1599be9cc6e63d43a07e846`. It is not a delivery node and did not overwrite the reviewed master.
- Delivery and proof export both decoded without error and reported no black spans under `blackdetect=d=0.05:pix_th=0.10:pic_th=0.98`.

## New ACS-owned family source

- `diffusion-family-project/index.tsx`: `sha256:fcd2dc725815f4ea7042e5ee824f1673e21bf0896d686eb6f72ba70fa24a8c17`.
- `diffusion-family-project/package.json`: `sha256:a55d7d0e70a111d2b1f120f5541a2e8e1156bb2b0a1c88596921385ab6e0efaf`.
- Syntax parse: PASS with the pinned checkout's esbuild.
- Runtime surface: native scene/sequence/group/shape/text/keyframe nodes and Inter/system font only.
- Forbidden surface scan: no media node, HTML/htmlPaint, WebGPU, shader, cloud AI, credit call, remote URL, or retained `node_modules` link.
- Short 01 DAPI check: 143 nodes, depth 4, 24 seconds, no issues.
- Short 02 DAPI check: 122 nodes, depth 4, 24 seconds, no issues.
- Post visual DAPI check: 26 nodes, depth 3, 3 seconds, no issues.

## Encoded short 01

- MP4: `sha256:367e8897f6785e5a312cf5b7d5ce4aec124d9ec2212d22127c19f0969852e99f`.
- H.264/yuv420p, 1080×1920, 30 fps, 720 frames, 24.000 seconds, no audio, 1,760,757 bytes.
- Full decode: PASS. Black scan: no spans. Seven MP4-derived representative frames: PASS.

## Encoded short 02

- MP4: `sha256:e80d7f4ed91985f89da555c0552c8c9b3291df01234d96c9362585f837585e8d`.
- H.264/yuv420p, 1080×1920, 30 fps, 720 frames, 24.000 seconds, no audio, 1,835,371 bytes.
- Full decode: PASS. Black scan: no spans. Seven MP4-derived representative frames: PASS.

## Built-in-browser companion acceptance

- Built-in-browser session `c389fe33-8b59-4a9c-8594-a4f0aba901aa`, revision 1, bundle `77656690caa111a6d69ae71c036d82dc3793932234df1ed89e775834a83f6ecb`: `canonicalCompiled`, `hostApplied`, and `browserApplied` were exactly equal; lifecycle `ready`.
- The Electron host stayed `hidden` and local-only, with zero egress attempts. DAPI remained authoritative and healthy on the ACS-owned family project.
- Human-only interaction proof: play at 0.009 seconds, pause at 10.225 seconds, and a direct playhead scrub through 11.300–14.633 seconds were present in structured companion logs.
- Visual inspection in the Codex built-in browser showed the live cream/orange/black code-native preview and timeline. The project menu contained only `View`; the adjacent tool menu contained only `Move` and `Hand`. No browser export, write, AI, checkout, auth, arbitrary-path, or DAPI surface was exposed.
- Closing the built-in-browser tab changed lifecycle to `disconnected-fresh-session-required` without terminating DAPI. Explicit repository-launcher stop then removed the loopback listener and companion resources while DAPI remained healthy.
- A separate unopened launcher smoke parsed the machine-readable one-time URL, including a 32-byte fragment capability, and exercised `open`, `status`, `logs`, and `stop`. Status reported hidden/local-only, `awaiting-renderer`, and zero egress; stop reported inactive, and the following status remained inactive.

## Independent source/config decision

- `business-freedom-family-motion-source` version 1: `approved`.
- `business-freedom-family-export-config` version 1: `approved`.
- `business-freedom-runtime-provenance` version 1, `sha256:ad7a87678eaed6b5630caba62ac79e7f73f8964558aafc9bbc7153e983ec7bfd`: `approved`.

These approvals cover only the named source/config/provenance bytes. Each
delivery video has its own review. Publishing authorization is not granted.
