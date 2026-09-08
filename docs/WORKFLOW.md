# Workflow

1. Choose the buyer problem, proof, practical content group, and capture format.
2. Draft the content brief and cut plan. Recording itself is an owner activity,
   not an automated ACS step.
3. Keep source rights/provenance explicit. Add an optional local transcript.
4. For ordinary video, edit through Diffusion's authoritative Electron/DAPI
   route under human supervision. Use the local read-only browser companion for
   inspection when useful.
5. Review the Diffusion export. Copy it into the production as an ordinary file.
6. Build/update `content-graph.json`: stable IDs, versions, real hashes,
   provenance, per-node review, and explicit edges.
7. Validate, perform final editorial review, and resolve findings.
8. Create `publisher-handoff.json` with only independently approved nodes.
9. Validate graph plus handoff and return exact paths/hashes to the caller.
10. Stop. Publishing requires separate human authorization and remains outside
    ACS.

At the decision, graph/handoff, and final-review steps, use [Working
discipline](WORKING_DISCIPLINE.md) only for a material decision, reported
content-domain defect, or evidence that needs its specific judgment. Record the
result in the existing production record; routine content work needs no new
process or notes file.

No step invokes in-repository media rendering, derivative generation, package
generation, a recovery ledger, or an automatic publisher. Repeats are ordinary graph revisions: preserve
stable IDs, increment changed versions, refresh hashes/reviews, and retain the
review references the owner wants to keep.

Use the upstream HyperFrames specialist route only for a full code-animated
video or bounded overlay. Return its reviewed output as an ordinary graph node.
