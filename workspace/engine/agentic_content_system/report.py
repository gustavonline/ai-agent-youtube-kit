"""Static, local browser review report."""

from __future__ import annotations

import html
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .inspect import require_current_inspection
from .io import read_json, sha256_file, write_json
from .paths import display_path
from .project import ProjectContracts, require_valid_project
from .render import prune_disabled_render_outputs
from .schemas import load_schema
from .validation import require_valid


ACTIVE_GENERATED_HANDOFF_FILES = (
    "reports/review.html",
    "reports/review.json",
    "results/run-result.json",
    "results/index.md",
)

QA_PROOF_FILES = (
    "qa/visual-review.json",
    "qa/visual-review.md",
)


def qa_review_proof(contracts: ProjectContracts) -> list[dict[str, str]]:
    """Return optional human/machine visual-QA files as hash-bound proof."""

    proof: list[dict[str, str]] = []
    for relative in QA_PROOF_FILES:
        path = contracts.directory / relative
        if path.is_file():
            proof.append({"path": relative, "sha256": sha256_file(path)})
    return proof


def render_review_proof(contracts: ProjectContracts, record: dict[str, Any]) -> list[dict[str, Any]]:
    """Summarize current output/caption bindings for the static review record."""

    proof: list[dict[str, Any]] = []
    for kind in ("long", "short"):
        if not contracts.edit_plan.get(f"{kind}_form", {}).get("enabled"):
            continue
        item = record.get("renders", {}).get(kind)
        if not isinstance(item, dict):
            continue
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        captions = item.get("captions") if isinstance(item.get("captions"), dict) else {}
        proof.append(
            {
                "kind": kind,
                "output": item.get("output", ""),
                "output_sha256": item.get("output_sha256", ""),
                "framing": metadata.get("framing", {}),
                "captions": {
                    "enabled": bool(captions.get("enabled", False)),
                    "intent": captions.get("intent", {}),
                    "intent_hash": captions.get("caption_intent_hash", ""),
                    "reviewed_revision": captions.get("reviewed_transcript_revision", 0),
                    "reviewed_sha256": captions.get("reviewed_transcript_sha256", ""),
                    "cue_count": captions.get("cue_count", 0),
                    "sidecar_path": captions.get("sidecar_path", ""),
                    "sidecar_sha256": captions.get("sidecar_sha256", ""),
                    "renderer": captions.get("renderer", "none"),
                    "text_filter": bool(captions.get("text_filter", False)),
                    "font_proof": captions.get("font_proof", {}),
                    "render_fingerprint": item.get("caption_fingerprint", {}),
                },
            }
        )
    return proof


def invalidate_active_handoff(contracts: ProjectContracts) -> None:
    """Remove generated review/result claims after a new package is installed.

    Contract files, source media, transcripts, learning, and any human notes
    under other filenames are deliberately left untouched. The caller invokes
    this only after the new ``publish/`` directory has been installed.
    """

    targets: list[tuple[str, Path]] = []
    for relative in ACTIVE_GENERATED_HANDOFF_FILES:
        path = contracts.directory / relative
        if path.exists() or path.is_symlink():
            if not path.is_file() and not path.is_symlink():
                raise ACSUserError(f"Generated handoff path is not a file: {relative}")
            targets.append((relative, path))

    # Move the generated claims aside as one bounded same-filesystem batch.
    # If one move fails, restore every move already made before propagating;
    # package rollback can therefore preserve the prior handoff as a whole.
    backup_dir = Path(tempfile.mkdtemp(prefix=".handoff-invalidation-", dir=str(contracts.directory)))
    moved: list[tuple[Path, Path]] = []
    try:
        for relative, path in targets:
            backup = backup_dir / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            path.replace(backup)
            moved.append((path, backup))
    except Exception:
        for original, backup in reversed(moved):
            if backup.exists() or backup.is_symlink():
                backup.replace(original)
        raise
    finally:
        shutil.rmtree(backup_dir, ignore_errors=True)


def _video_card(label: str, source: str) -> str:
    safe_source = html.escape(source, quote=True)
    return (
        f"<article><h3>{html.escape(label)}</h3>"
        f"<video controls preload=metadata src=\"../{safe_source}\"></video>"
        f"<p><a href=\"../{safe_source}\">Open {html.escape(label)} file</a></p></article>"
    )


def create_review_report(contracts: ProjectContracts) -> Path:
    require_valid_project(contracts, require_sources=True)
    inspection_path = require_current_inspection(contracts)
    prune_disabled_render_outputs(contracts)
    manifest_path = contracts.directory / "publish" / "manifest.json"
    package_state: dict[str, Any] | None = None
    if manifest_path.exists():
        # Reuse the complete package verifier before writing report bytes. A
        # report must not mix current inspection/provenance with an older
        # manifest, render, derivative, handoff, or passed verification.
        from .package import validate_current_package

        package_state = validate_current_package(contracts)
        manifest = package_state["manifest"]
        publisher_handoff_path = package_state["publisher_handoff_path"]
        publisher_handoff = package_state["publisher_handoff"]
    else:
        manifest = {}
        publisher_handoff_path = contracts.directory / "publish" / "publisher-handoff.json"
        publisher_handoff = {}
    record_path = contracts.directory / "renders" / "render-record.json"
    record: dict[str, Any] = read_json(record_path) if record_path.exists() else {}
    inspection: dict[str, Any] = read_json(inspection_path)
    render_proof = render_review_proof(contracts, record)
    qa_proof = qa_review_proof(contracts)

    videos = []
    for kind, item in record.get("renders", {}).items():
        if not contracts.edit_plan.get(f"{kind}_form", {}).get("enabled"):
            continue
        caption_note = ""
        captions = item.get("captions") or {}
        if captions.get("sidecar_path"):
            caption_note = (
                f"<p>Captions: <a href=\"../{html.escape(captions['sidecar_path'], quote=True)}\">"
                f"{html.escape(captions['sidecar_path'])}</a>; revision "
                f"{html.escape(str(captions.get('reviewed_transcript_revision', 'unknown')))}; "
                f"renderer {html.escape(str(captions.get('renderer', 'none')))}.</p>"
            )
        videos.append(_video_card(f"{kind.title()} render", item.get("output", "")) + caption_note)
    handoff_routes = {route.get("channel"): route for route in publisher_handoff.get("routes", [])}
    route_items: list[str] = []
    for route in manifest.get("routes", []):
        delivery = handoff_routes.get(route["channel"], {})
        schedule = delivery.get("delivery_mode", "unknown")
        if delivery.get("delivery_mode") == "scheduled":
            schedule += f" at {delivery.get('scheduled_at', '')} ({delivery.get('timezone', '')})"
        references = ", ".join(route.get("assets", []) or [route.get("post_path", "text")])
        route_items.append(
            f"<li><strong>{html.escape(route['channel'])}</strong>: {html.escape(references)}"
            f"<br><small>Delivery: {html.escape(schedule)}; awaiting separate authorization; not posted.</small></li>"
        )
    routes = "".join(route_items) or "<li>No publish package yet.</li>"
    disabled = "".join(
        f"<li><strong>{html.escape(item['channel'])}</strong>: {html.escape(item['reason'])}</li>"
        for item in manifest.get("disabled_channels", [])
    ) or "<li>No disabled-channel data yet.</li>"
    source_rows_parts: list[str] = []
    for item in inspection.get("sources", []):
        rights = item.get("rights", {})
        source_url = str(rights.get("source_url", ""))
        source_link = (
            f'<a href="{html.escape(source_url, quote=True)}">source</a>'
            if source_url.startswith(("https://", "http://"))
            else "—"
        )
        source_rows_parts.append(
            f"<tr><td>{html.escape(item.get('path', ''))}</td>"
            f"<td>{html.escape(rights.get('status', ''))}</td>"
            f"<td>{html.escape(rights.get('owner', ''))}</td>"
            f"<td>{html.escape(rights.get('license', ''))}</td>"
            f"<td>{source_link}</td>"
            f"<td>{html.escape(str(item.get('media', {}).get('duration_seconds', '')))}s</td></tr>"
        )
    source_rows = "".join(source_rows_parts) or "<tr><td colspan=6>Run acs inspect to populate source metadata.</td></tr>"
    adapter_items = "".join(
        f"<li>{html.escape(asset.get('kind', 'adapter'))}: <code>{html.escape(asset.get('path', ''))}</code></li>"
        for asset in manifest.get("assets", [])
        if asset.get("kind") in {"adapter", "adapter-manifest"}
    ) or "<li>No adapter import.</li>"
    qa_items = "".join(
        f"<li><a href=\"../{html.escape(item['path'], quote=True)}\">"
        f"{html.escape(item['path'])}</a> ({html.escape(item['sha256'])})</li>"
        for item in qa_proof
    ) or "<li>No visual-QA artifact registered.</li>"
    title = html.escape(contracts.project["title"])
    approval = contracts.edit_plan["approval"]
    manifest_status = manifest.get("verification", {}).get("status", "not_packaged")
    report_dir = contracts.directory / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} · Agentic Content System review</title>
  <style>
    :root {{ color-scheme: dark; font-family: system-ui, sans-serif; background: #0a0d10; color: #f4f7fa; }}
    body {{ max-width: 1100px; margin: 0 auto; padding: 2rem; line-height: 1.5; }}
    a {{ color: #2ee7d2; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }}
    article, section {{ background: #121821; border: 1px solid #263342; border-radius: 10px; padding: 1rem; }}
    video {{ width: 100%; max-height: 420px; background: #000; }}
    code {{ color: #ffb020; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ text-align: left; padding: .45rem; border-bottom: 1px solid #263342; }}
    .status {{ color: #2ee7d2; font-weight: 700; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p>Static local review report generated by Agentic Content System v0.3. No external posting is performed.</p>
  <section>
    <p>Plan approval: <span class="status">{html.escape(approval.get('status', 'unknown'))}</span> by {html.escape(approval.get('approved_by', '—'))}</p>
    <p>Publish verification: <span class="status">{html.escape(manifest_status)}</span></p>
    <p>Project: <code>{html.escape(contracts.project['project_id'])}</code></p>
  </section>
  <h2>Rendered outputs</h2>
  <div class="grid">{''.join(videos) or '<article>No renders yet.</article>'}</div>
  <h2>Enabled handoff routes</h2>
  <section><ul>{routes}</ul></section>
  <section><p>Supervised publisher handoff: <span class="status">{html.escape(publisher_handoff.get('status', 'not generated'))}</span>; external posting: false.</p></section>
  <h2>Disabled routes</h2>
  <section><ul>{disabled}</ul></section>
  <h2>Source provenance</h2>
  <section><table><thead><tr><th>Path</th><th>Rights</th><th>Owner</th><th>License</th><th>Source</th><th>Duration</th></tr></thead><tbody>{source_rows}</tbody></table></section>
  <h2>Supervised adapter imports</h2>
  <section><ul>{adapter_items}</ul></section>
  <h2>Visual QA proof</h2>
  <section><ul>{qa_items}</ul></section>
</body>
</html>
"""
    html_path = report_dir / "review.html"
    html_path.write_text(body, encoding="utf-8")
    verification_path = contracts.directory / "publish" / "verification.json"
    manifest_approval = manifest.get("approval", {})
    approval_revision = int(approval.get("approval_revision", 0) or 0)
    write_json(
        report_dir / "review.json",
        {
            "schema_version": "1.0",
            "project_id": contracts.project["project_id"],
            "html": display_path(contracts.directory, html_path),
            "html_sha256": sha256_file(html_path),
            "manifest_id": manifest.get("manifest_id", ""),
            "manifest_sha256": sha256_file(manifest_path) if manifest_path.exists() else "",
            "inspection_sha256": sha256_file(inspection_path),
            "manifest_approval_hash": manifest_approval.get("approval_hash", ""),
            "manifest_approval_revision": int(manifest_approval.get("approval_revision", 0) or 0),
            "approval_hash": approval.get("approval_hash", ""),
            "approval_revision": approval_revision,
            "policy_hash": manifest.get("policy_hash", ""),
            "provenance_hash": manifest.get("provenance_hash", ""),
            "delivery_intent_hash": manifest.get("delivery_intent_hash", ""),
            "publisher_handoff_path": manifest.get("publisher_handoff_path", "publish/publisher-handoff.json"),
            "publisher_handoff_sha256": sha256_file(publisher_handoff_path) if publisher_handoff_path.exists() else "",
            "verification_status": manifest_status,
            "verification_sha256": sha256_file(verification_path) if verification_path.exists() else "",
            "render_proof": render_proof,
            "qa_proof": qa_proof,
        },
    )
    review_record = read_json(report_dir / "review.json")
    require_valid(review_record, load_schema("review-record"), "review record")
    return html_path
