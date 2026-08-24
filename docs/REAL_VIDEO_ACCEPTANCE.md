# Real-video acceptance protocol

Use this protocol for a later owner usability check. It is generic and does
not create a personal acceptance workspace during repository setup.

## Source guidance

Use owner-recorded footage for the usability run: camera, screen capture,
podcast, demo, or another format that matches the content decision. Keep the
source in the local workspace `sources/` directory, record rights and
provenance in `project.json`, and do not commit large or private media.
Generated fixtures and rights-cleared public footage are suitable for testing
the engine. They are technical evidence, not owner usability evidence.

## Exact end-to-end checks

From the repository root, with the clone defaults configured:

```text
python -m agentic_content_system doctor
python -m agentic_content_system validate-profile workspace/channel/brand.json
python -m agentic_content_system init <workspace> --brand workspace/channel/brand.json
```

Resolve the real promise, audience, format, source rights, edit plan, and
delivery intent in the workspace. Then run exactly:

```text
python -m agentic_content_system inspect <workspace>
python -m agentic_content_system validate <workspace>
python -m agentic_content_system ingest-transcript <workspace> <transcript>
python -m agentic_content_system plan <workspace> --approve --by <reviewer>
python -m agentic_content_system render <workspace> --kind all
python -m agentic_content_system derive <workspace>
python -m agentic_content_system package <workspace>
python -m agentic_content_system verify <workspace>
python -m agentic_content_system review-report <workspace>
python -m agentic_content_system export-result <workspace>
```

Inspect the actual rendered video and static review report. Confirm that the
content promise is clear, source rights are correct, captions are readable,
the output matches the approved edit plan, and the handoff is useful to a
human publisher.

## Rerun and currentness checks

- Run `inspect` again after changing declared source bytes, order, kind, role,
  rights, or provenance.
- Re-approve after changing `brand.json`, `project.json`, delivery intent, or
  `edit-plan.json`.
- Re-run `render`, `derive`, and `package` after their inputs change. A fresh
  package invalidates older review and result claims until the final three
  checks run again.
- Confirm repeated unchanged runs are deterministic or report an explicit
  current/cached result; stale approvals and hashes must fail closed.

## Enabled and disabled channels

Check `brand.json`, `project.json`, `publish/manifest.json`, and
`publish/publisher-handoff.json` together:

- every enabled channel has exactly one delivery intent and a valid route;
- disabled channels have a human-readable policy reason;
- disabled channels appear only in `disabled_channels`, never in active routes;
- adding a disabled channel to `project.json.delivery_intent` does not make it
  a delivery route; packaging and verification must still exclude it.

## No external posting

The acceptance run must not log in, call a publisher, upload, schedule, or
post externally. Confirm `external_posting: false`, `not_posted: true`, and
`status: awaiting-separate-authorization` in the publisher handoff. Any later
posting requires separate human authorization outside ACS.

## Honest PASS boundary

Generated fixture media and the retained public-source run can prove the
contract engine, FFmpeg boundary, enabled-route filtering, deterministic
reruns, review records, and supervised handoff. A real usability PASS is
honest only after the owner completes the same checks with owner-recorded
footage and confirms the resulting video and posts are usable for the stated
business, audience, offer, and channel policy.
