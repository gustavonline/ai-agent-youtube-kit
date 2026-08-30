---
name: freecut-studio
description: "Set up, check, open, use, maintain, or recover the one external FreeCut Studio checkout for an ACS video outcome."
---

# FreeCut Studio

Use FreeCut as the one normal browser Studio for ACS video work. The current
owner-facing agent session supervises the browser; AIOS may be that session
when present, while ACS and this skill remain independently invocable when the
owner starts elsewhere. FreeCut's external native workspace and project files
remain canonical. Keep workspace, project, and revision paths only in the
active task context. Do not create ACS bridge contracts, manifests, persistent
bindings, or FreeCut copies inside AIOS/ACS.

FreeCut is unnecessary for non-video outcomes. Select one mode below for a
video task.

## Setup

Use exactly `~/.local/share/freecut` on macOS and Linux. Never scan for other
copies, clone below AIOS/ACS, or create a suffixed/versioned second checkout.
The official origin is `https://github.com/walterlow/freecut.git`; the currently
pinned, functionally proven revision is
`4d62e8082c5eb387a96275bcbd323d28f6e41a62`. The accepted operating profile is
the browser app at this exact pin, dependency graph, install mode, browser
bundle, and reachability adjudication. Any drift reopens the readiness gate.

Setup is a write action and requires setup authority in the current task. If
the fixed path is absent, clone the official repository there, check out the
pinned revision detached, then read its `packageManager` and attest the exact
declared npm version; the current pin declares `npm@11.8.0`. Use that exact npm
version for both install and build. When ambient `npm --version` matches, run
`npm ci --ignore-scripts` followed by `npm run build`. When it differs, invoke
the declared version one-off with `corepack npm@11.8.0 ci --ignore-scripts`
followed by `corepack npm@11.8.0 run build`; do not replace or activate npm
globally. Dependency lifecycle scripts, including the ONNX install path, must
not run, while FreeCut's normal build remains explicit. If the path exists,
reuse it and validate it first. Stop if it is not the official repository, has
uncommitted owner state, or cannot safely reach the pinned revision. Never
delete, reset, stash, overwrite, or silently repair owner state.

Safe install provenance must come from deliberate Setup evidence showing the
exact pin, lockfile graph, declared `packageManager`, actual npm version used,
and exact install/build invocations. Do not infer it from `node_modules`, build
artifacts, timestamps, or Git cleanliness, and do not invent a marker or JSON
file. If that provenance is unavailable for an existing checkout, report that
Setup must be deliberately rerun with authority.

Finish Setup by running Check. Setup remains not-ready while any
required proof or the pinned reachability adjudication is missing or stale.

## Check

Keep this mode read-only. At the fixed path, verify all of the following and
report missing or stale evidence as a failure:

- exact official `origin`, exact pinned `HEAD`, and a clean Git status;
- required Node/npm availability, Corepack when needed, and the pinned
  `packageManager` value. Setup evidence must show that the npm version actually
  invoked matches the exact declaration, currently 11.8.0; generic
  package-manager compatibility is insufficient;
- lockfile/install consistency (`npm ls --omit=dev`), built Studio artifacts,
  and trustworthy Setup evidence for the exact-version `ci --ignore-scripts`
  followed by the explicit `run build`;
- FreeCut API v1 capabilities plus `npm run headless:test:node` contract proof,
  currently 43/43 at the exact pin;
- the full `npm audit --omit=dev` output preserved in task evidence. Keep the
  current eight public findings visible; do not collapse accepted risk into a
  claim of zero vulnerabilities;
- the documented browser reachability adjudication: `adm-zip` and `tar` are on
  the Node/ONNX install-only path; `protobufjs` affects textual proto parsing,
  not FreeCut's used minimal binary decoder; `seroval` is on SSR/dehydration
  paths outside the SPA; and `sharp`/libvips is excluded by the
  `transformers.web.js` browser export. The `tar.replace` and member-selection
  advisories also do not match the concrete ONNX call shape.

The current direct safe-install proof used npm 11.8.0 with Node 22.21.1 on
macOS: it built normally, passed 43/43 headless tests, served the loopback
preview with HTTP 200, and left Git clean. Physical Linux/amd64 installation,
build, headless-test, and preview execution remain unverified in the evidence
available to this outcome; do not infer them from ACS's cross-platform CLI or
CI configuration. Treat the macOS result as evidence only for the exact
accepted profile, not a future pin.

Report public audit findings and actual browser reachability separately. Accept
the pinned browser-only profile only while the complete audit evidence and
adjudication above remain intact. A pin, dependency-graph, install-mode,
browser-bundle, or reachability change reopens the gate and requires deliberate
revalidation; finding-count drift also makes the recorded audit evidence stale.

Disclose unavailable network, browser, OS, or export proof. A missing, dirty,
wrong-origin, stale, dependency-incomplete, unbuilt, contract-failing, or
unadjudicated checkout is not healthy. Missing safe install provenance requires
a deliberate Setup rerun. Do not install, fetch, build, repair, or create
provenance files in check mode.

## Open / Work

Reuse the fixed checkout only after it passes Check, then use its built local
browser server. Bind only to loopback (`npm run preview -- --host 127.0.0.1 --port 4173
--strictPort`), open it in the Codex in-app browser, and let the human choose
the external FreeCut workspace folder manually. Native FreeCut files remain the
source of truth. Do not automate folder permission, claim an MCP integration,
or route this workflow through MCP.

Preserve a single-writer handoff: the human saves and hands off; the agent reads
the current project revision and writes through FreeCut API v1 only with
`expectedRevision`; then the human reloads/reopens and reviews. Never use the
legacy destructive `--in-place` path or bypass a revision conflict.

After the human reviews and approves the FreeCut export, return it through the
ordinary ACS source path:

1. Copy the reviewed video as an ordinary file under the active production's
   `sources/` folder.
2. Add that relative source path to `project.json.sources` with truthful normal
   rights/provenance fields, then point `edit-plan.json.source` and every
   intended `long_form.segments[].source` and `short_form.segments[].source` at
   it.
3. Run `acs inspect <workspace>` again. Ingest or regenerate the transcript for
   the returned source, use `acs review-transcript` when reviewed transcript
   truth is applicable, and obtain a fresh `acs plan --approve` decision.
4. Run the existing `acs render`, `acs derive`, `acs package`, `acs verify`,
   `acs review-report`, `acs export-result`, and `acs semantic-eval` flow.

The normal FreeCut return path must never use `acs import-adapter`, a FreeCut
manifest, reference JSON, schema, bridge, or any other integration layer.

## Maintain / Recover

Do not auto-upgrade. Fetch and update the same fixed checkout only after a newer
commit has been deliberately validated and this skill's pinned SHA is updated
in a reviewed ACS change. Never create a second checkout or delete, reset,
stash, or overwrite owner state.

On wrong origin, dirty state, divergence, failed build, or revision conflict,
stop and report the smallest manual recovery. Break a writer lock only as an
explicit recovery after confirming the recorded writer is dead; retain the
expected-revision guard. Legacy HyperFrames or other editor material is
migration/recovery input only, never a normal parallel Studio route.
