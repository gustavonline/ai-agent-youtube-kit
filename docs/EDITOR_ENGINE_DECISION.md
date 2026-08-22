# Editor and Engine Decision Record

**Decision:** keep the Agentic Content System (ACS) v0.1 core narrow: versioned
declarative contracts, a Python cross-platform CLI, and FFmpeg/ffprobe as the
deterministic media boundary. Treat full editors and motion systems as
supervised, optional adapters.

**Research snapshot:** 2026-08-21

This is a dated technical repository comparison. License, star count, README
status, and feature statements below are GitHub snapshots, not permanent truth
or quality proof. Stars are included only to make the snapshot auditable; they
do not establish reliability, safety, maturity, or product fit. The record is
separate from the creator research in
[`docs/RESEARCH_PROVENANCE.md`](RESEARCH_PROVENANCE.md), which preserves its
own distinction between creator claims, transcript observations, and ACS
design decisions.

## Constraint and decision

ACS has to support authentic, useful solo-founder or small-business content
across macOS, Windows, and Linux. The system must be headless and
agent-readable, deterministic from transparent inputs, low setup and
maintenance, and modular enough to add supervised adapters. It must not become
a phone-first editor, a mini-Premiere, or a full studio. v0.1 must have no
hidden cloud/API dependency and no external posting; a later publisher needs a
separate authorization. FFmpeg/ffprobe provide the explicit media boundary,
while contracts, approval, provenance, rights, transcripts, hashes, and static
review files remain inspectable workspace truth.

The decision is therefore to keep the narrow contract + FFmpeg core. ACS owns
the versioned project/edit/publish/result contracts, approval and verification
rules, deterministic segment assembly, route policy, and proof. Upstream
context, including an AIOS task, is copied into those local contracts by the
judgment layer and is not a runtime dependency.
Local Whisper remains optional. An editor or motion engine may translate the
contract or supply an asset, but it may not silently own workspace truth. This
keeps the v0.1 execution path cloneable without requiring a desktop shell,
database, queue, cloud key, or full-editor operating model.

## Evaluation criteria

| Criterion | v0.1 bar | Why it matters |
| --- | --- | --- |
| Agent-readable/headless | File contracts and a stable CLI; no required GUI or hidden state | Agents and humans must inspect, diff, approve, and recover a run |
| Determinism | Pinned intent plus source hashes produce reproducible FFmpeg outputs and verification | A proof handoff must be trustworthy and rerunnable |
| Cross-platform/setup | Python 3 plus FFmpeg/ffprobe on macOS, Windows, and Linux | A clone should not inherit a Tauri/Node/Rust or hosted service operations burden |
| Scope and authenticity | Useful footage, proof, and buyer relevance; no mini-Premiere or animation-led default | The product serves content decisions and capture variety, not editor feature breadth |
| Modularity | Explicit import/export seams with one local owner for each truth | Future editors, local transcription, motion, and publishers can be supervised adapters |
| Trust/autonomy | No hidden cloud/API requirement, arbitrary shell execution, or v0.1 posting | Approval and separate authorization must remain visible and bounded |

## Dated candidate comparison

| Candidate | Snapshot evidence on 2026-08-21 | Fit against the criteria | v0.1 decision |
| --- | --- | --- | --- |
| [OpenCut-app/OpenCut](https://github.com/OpenCut-app/OpenCut) | MIT; 85,396 GitHub stars; the current README describes a ground-up rewrite. Editor API, plugins, Rust cross-platform work, and MCP/headless capabilities are described as upcoming; the classic version is archived. | Strong future candidate, but the API/headless surface and rewrite status are not a stable, narrow dependency boundary for this release. | Future adapter/candidate; not safe as the v0.1 core today. |
| [chatman-media/timeline-studio](https://github.com/chatman-media/timeline-studio) | MIT; 201 GitHub stars; Tauri/Next/Rust/Bun stack with headless contracts and a broad 100+ AI-tool/full-studio surface. | Promising and relevant to supervised timelines, but substantially more operational scope and autonomy than the ACS contract + FFmpeg path needs. | Document an adapter seam; do not vendor or depend on it. |
| [openreelio/openreelio](https://github.com/openreelio/openreelio) | MIT; 68 GitHub stars; explicitly pre-alpha, with Tauri/Rust/React/SQLite and headless CLI/MCP ambitions. | Useful direction for a human/agent timeline adapter, but pre-alpha maturity and its application stack are not a low-maintenance v0.1 core. | Revisit as a supervised adapter after maturity evidence; it is not a stable core dependency yet. |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0; 41,951 GitHub stars; Node 22+, deterministic HTML/CSS/motion rendering, and agent skills. | Good for a bounded explanatory overlay, but ACS defaults to authentic footage and buyer-relevant proof rather than animation-led production. | Keep as an optional motion/overlay adapter, never product identity. |
| [poseljacob/agentic-video-editor](https://github.com/poseljacob/agentic-video-editor) | MIT; 475 GitHub stars; Python/Gemini/FFmpeg, with an ad-focused ensemble and cloud API-key/retry autonomy. | A useful reference for declarative EditPlan and review loops, but cloud dependency, retry autonomy, and ad-first product assumptions violate the default trust and product fit. | Reuse concepts selectively; do not adopt its runtime or autonomy model. |
| [pifferologo/ai-agent-video-editor](https://github.com/pifferologo/ai-agent-video-editor) | MIT; 140 GitHub stars; the `video-use` transcript/EDL/FFmpeg agent workflow with ElevenLabs and Node, plus optional Redis. | Its transparent transcript/EDL shape is useful, but required-cloud-adjacent tooling and optional service state are outside the stdlib-first core. | Reuse the transparent transcript/EDL concept where useful; retain local Whisper and no required cloud key. |

The comparison does not claim that a candidate is bad. It records why each
candidate is or is not an appropriate owner of ACS v0.1 truth under the stated
constraints. In particular, a large star count is not evidence that a project
is safe to embed, and a small count is not evidence that it lacks promise.

## Rejection rationale and ownership

Building a full editor ourselves would expand v0.1 into timeline UX, media
state, persistence, undo/redo, packaging, and platform-specific maintenance.
Vendoring a full editor now would import that scope, its release risks, and
possibly its UI/runtime assumptions before ACS has demonstrated a need. Both
choices are rejected for v0.1.

ACS owns the narrow declarative contract and FFmpeg boundary: source
provenance/rights, ordered edit segments, approval, deterministic media,
policy-driven derivatives, manifest and supervised-publisher handoff, hashes,
verification, and static review. The persistent AIOS Space owns durable
company/offer/buyer/channel defaults and learning; a task-level caller supplies
resolved context that the judgment layer copies into the local project; a human
owns consequential approval and any later publishing authorization. Adapters
may read or write explicitly named contract files and must return hashes and
failures without becoming a hidden source of truth.

## Adapter seams

- **FFmpeg/ffprobe:** required core boundary for inspection and deterministic
  long-form/vertical output.
- **OpenCut:** a future translator between ACS edit contracts and a stable
  headless/API or MCP surface; no runtime dependency until that surface is
  released and verified.
- **Timeline Studio and OpenReelio:** supervised import/export adapters for a
  human timeline when their contracts are mature enough; ACS remains the
  approval and provenance owner.
- **HyperFrames:** optional HTML/CSS motion or overlay asset for a specific
  explanatory beat; it does not replace authentic capture or become the
  default editor.
- **Local Whisper and transcript/EDL workflows:** optional input adapters that
  produce agent-readable transcript/cut intent; they do not require cloud
  credentials or own final approval.
- **Supervised publisher:** consumes only the current
`publish/publisher-handoff.json`, honors enabled routes and manual/scheduled
  intent, and requires authorization outside ACS. v0.1 keeps
  `external_posting: false`.

## Revisit triggers

Reconsider the boundary only when evidence changes the constraint decision:

1. OpenCut ships a stable, documented headless/MCP/API release with reproducible
   cross-platform installation, contract import/export, tests, and a clear
   ownership boundary that does not require ACS to adopt a full studio.
2. OpenReelio moves beyond pre-alpha with a stable release, dependable
   cross-platform behavior, inspectable storage/contract semantics, and a
   supervised mode that preserves ACS approval and provenance.
3. Repeated real ACS productions show that approved non-contiguous cuts and
   adapters are insufficient without a human timeline, with the cost measured
   in recoverable project friction rather than feature enthusiasm.
4. The local FFmpeg path becomes the demonstrated bottleneck for a required
   content job, and a candidate can solve that job without adding hidden
   network, auth, database, or publishing autonomy.

A trigger starts a new evidence review; it does not authorize automatic
``vendor now`` behavior. Until then, ACS remains a local-first execution
contract with FFmpeg at the media boundary.

## Conclusion

For v0.1, **build a full editor ourselves** and **vendor a full editor now**
are both rejected. ACS owns the narrow declarative contract and FFmpeg
boundary, with future editors and motion systems behind explicit, supervised
adapter seams.
