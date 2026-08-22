# Examples

Examples are technical evidence and local scaffolding references, not owner
acceptance workspaces. Configure a clone first with `channel/PROFILE.md` and
`channel/brand.json`; create a real workspace only for a stated content
outcome:

```text
python -m agentic_content_system validate-profile channel/brand.json
python -m agentic_content_system init examples/my-content --brand channel/brand.json
```

`examples/acs-public-source-proof-20260822/` is retained locally as a rights-documented
public-source engine proof. It demonstrates contracts, FFmpeg output,
enabled-route filtering, currentness, review, and supervised handoff. It is
not proof that owner-recorded footage is usable for a real business.

The repository does not commit large demo media for new work. Use
`scripts/create-fixture-media.py` or a rights-safe source with pinned
provenance for local proof. Follow `docs/REAL_VIDEO_ACCEPTANCE.md` for later
owner-recorded acceptance.
