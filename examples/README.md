# Examples

Examples are deliberately curated standalone proof, not operational production
workspaces. Configure a clone first with `workspace/channel/PROFILE.md` and
`workspace/channel/brand.json`; create a real production only for a stated
content outcome:

```text
python -m agentic_content_system validate-profile workspace/channel/brand.json
python -m agentic_content_system init workspace/productions/my-content --brand workspace/channel/brand.json
```

Each curated example must carry its own `README.md` and `proof.json` and remain
understandable without importing this repository. Operational ACS workspaces
belong under `workspace/productions/<slug>/`; a production is promoted here
only by deliberate choice.

Use `python workspace/engine/tracer.py promote-example --run-id <id> --slug
<slug>` for that explicit promotion after a successful full route. The tracer
creates only `README.md` and `proof.json`; it never copies sources or generated
production outputs into the curated boundary.

The repository does not commit large demo media for new work. Use
`workspace/engine/scripts/create-fixture-media.py` or a rights-safe source with pinned
provenance for local proof. Follow `docs/REAL_VIDEO_ACCEPTANCE.md` for later
owner-recorded acceptance.
