"""Workspace scaffolding for standalone ACS runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .io import write_json
from .paths import GENERATED_DIRS, resolve_project, slugify


def default_brand(project_id: str, *, example: str | None = None) -> dict[str, Any]:
    if example == "gustav":
        name = "Gustav Online example channel"
        owner = "Gustav Online"
        intent = "Turn bounded business context into useful, buyer-relevant systems content."
        reasons = {
            "youtube": "Primary home for approved long-form explanations and selected shorts.",
            "linkedin": "Primary professional route for practical proof, context, and buyer learning.",
            "instagram": "Optional short route; enable only when the derivative has a clear visual and audience fit.",
            "tiktok": "Disabled: the current buyer/context fit is stronger on YouTube and LinkedIn; do not assume every edit becomes TikTok content.",
        }
    else:
        name = "Example brand"
        owner = "Clone owner"
        intent = "Turn bounded business context into useful, buyer-relevant content."
        reasons = {
            "youtube": "Primary long-form and selected short route; change this policy for the clone.",
            "linkedin": "Professional context and proof route; change this policy for the clone.",
            "instagram": "Optional short route; enable only when there is a clear fit.",
            "tiktok": "Disabled by default until the brand has a documented fit and reason to enable it.",
        }
    return {
        "schema_version": "1.0",
        "brand_id": project_id,
        "name": name,
        "owner": owner,
        "channel_intent": intent,
        "cadence": {
            "core_videos_per_week": 3,
            "planning_horizon_weeks": 26,
            "useful_short_target": 22,
            "note": "Three core videos per week for 26 weeks is 78 core videos; add 22 useful shorts for a 100-asset planning target.",
        },
        "channels": [
            {"id": "youtube", "enabled": True, "reason": reasons["youtube"], "allowed_asset_types": ["long", "short"]},
            {"id": "linkedin", "enabled": True, "reason": reasons["linkedin"], "allowed_asset_types": ["text"]},
            {"id": "instagram", "enabled": False, "reason": reasons["instagram"], "allowed_asset_types": ["short"]},
            {"id": "tiktok", "enabled": False, "reason": reasons["tiktok"], "allowed_asset_types": []},
        ],
    }


def default_project(project_id: str, brand: dict[str, Any], *, example: str | None = None) -> dict[str, Any]:
    delivery_routes: list[dict[str, Any]] = []
    for channel in brand["channels"]:
        if not channel["enabled"]:
            continue
        if example == "gustav" and channel["id"] == "youtube":
            delivery_routes.append(
                {
                    "channel": "youtube",
                    "delivery_mode": "scheduled",
                    "scheduled_at": "2026-09-01T09:00:00",
                    "timezone": "Europe/Copenhagen",
                }
            )
        else:
            delivery_routes.append({"channel": channel["id"], "delivery_mode": "manual"})
    return {
        "schema_version": "1.0",
        "project_id": project_id,
        "title": "Useful system walkthrough",
        "promise": "Show one practical system, the proof it creates, and the next step.",
        "audience": "A solo founder or small-business operator who wants useful AI-enabled workflows.",
        "format": "solo-direct-to-camera",
        "content_group": "teach-explain",
        "status": "draft",
        "sources": [
            {
                "path": "sources/source.mp4",
                "kind": "camera",
                "role": "primary",
                "rights": {
                    "status": "owned",
                    "owner": brand["owner"],
                    "license": "owner-provided-original",
                    "source_url": "",
                    "attribution": "",
                },
            }
        ],
        "transcript": {"path": "transcripts/active.json", "format": "acs-transcript/1.0"},
        "delivery_intent": {"schema_version": "1.0", "routes": delivery_routes},
        "notes": "Replace the example promise, audience, source rights, format, and delivery intent before a real content run.",
    }


def default_edit_plan(project_id: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "plan_id": f"{project_id}-plan",
        "project_id": project_id,
        "approval": {
            "status": "draft",
            "approved_by": "",
            "approved_at": "",
            "note": "Edit this declarative plan, then approve it explicitly before rendering or packaging.",
            "approval_hash": "",
            "approval_revision": 0,
        },
        "source": "sources/source.mp4",
        "long_form": {
            "enabled": True,
            "output": "renders/long.mp4",
            "segments": [{"source": "sources/source.mp4", "start": 0, "duration": 0}],
        },
        "short_form": {
            "enabled": True,
            "output": "renders/short-vertical.mp4",
            "segments": [{"source": "sources/source.mp4", "start": 0, "duration": 30}],
        },
        "points": [
            "State the promise and why it matters.",
            "Show the mechanism or proof.",
            "Give the next useful step.",
        ],
        "proof": [
            "Capture a visible mechanism, result, case, or other concrete proof for the promise."
        ],
        "cta": "Use the next useful step that fits the viewer's context.",
        "transcript_ref": "transcripts/active.json",
        "notes": "Keep the default structure promise + proof + plan; add a contextual CTA and an outro to a useful next video.",
    }


def default_content_brief(project: dict[str, Any], edit_plan: dict[str, Any]) -> str:
    return (
        "# Content Brief\n\n"
        "Complete this brief before capture. The judgment layer (Codex or another agent) may refine it,\n"
        "but the workspace keeps the bounded decision visible and local.\n\n"
        f"- Buyer/audience: {project['audience']}\n"
        f"- Promise: {project['promise']}\n"
        f"- Capture format: {project['format']}\n"
        f"- Practical group: {project['content_group']}\n"
        "- Buyer problem: <fill from the resolved business context or source notes>\n"
        f"- Proof required: {'; '.join(edit_plan.get('proof', []))}\n\n"
        "## Three-point outline\n\n"
        + "\n".join(f"{index}. {point}" for index, point in enumerate(edit_plan["points"], start=1))
        + f"\n\n## Contextual CTA\n\n{edit_plan['cta']}\n"
    )


def default_recording_plan(project: dict[str, Any], edit_plan: dict[str, Any]) -> str:
    return (
        "# Recording Plan\n\n"
        "Use this pre-capture outline before adding source media. Record the proof needed for the promise,\n"
        "then use `edit-plan.json` to choose the approved takes/segments.\n\n"
        f"1. Hook/promise: {project['promise']}\n"
        "2. Context: name the buyer problem and why it matters now.\n"
        f"3. Proof/mechanism: {'; '.join(edit_plan.get('proof', []))}\n"
        + "\n".join(f"{index + 4}. {point}" for index, point in enumerate(edit_plan["points"]))
        + f"\n{len(edit_plan['points']) + 4}. CTA/outro: {edit_plan['cta']}\n\n"
        "Capture checklist:\n\n"
        "- [ ] Rights/provenance recorded for every source.\n"
        "- [ ] Audio and visual proof are usable.\n"
        "- [ ] Transcript can be created or supplied.\n"
        "- [ ] Channel policy and approval owner are known.\n"
    )


def scaffold_project(path: str | Path, *, example: str | None = None, force: bool = False) -> Path:
    project_dir = resolve_project(path)
    project_id = slugify(project_dir.name)
    if project_dir.exists() and any(project_dir.iterdir()) and not force:
        raise ACSUserError(f"Workspace directory is not empty: {project_dir}. Use --force only when replacement is intended.")
    project_dir.mkdir(parents=True, exist_ok=True)
    brand = default_brand(project_id, example=example)
    project = default_project(project_id, brand, example=example)
    edit_plan = default_edit_plan(project_id)
    write_json(project_dir / "brand.json", brand)
    write_json(project_dir / "project.json", project)
    write_json(project_dir / "edit-plan.json", edit_plan)
    for name in ("sources", "transcripts", "context", *GENERATED_DIRS):
        directory = project_dir / name
        directory.mkdir(parents=True, exist_ok=True)
        keep = directory / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
    (project_dir / "sources" / "README.md").write_text(
        "# Sources\n\nPut source media here and keep provenance/rights in `../project.json`.\n",
        encoding="utf-8",
    )
    (project_dir / "transcripts" / "README.md").write_text(
        "# Transcripts\n\nUse `acs ingest-transcript <workspace> <file>` to create `active.json`.\n",
        encoding="utf-8",
    )
    (project_dir / "context" / "README.md").write_text(
        "# Optional source notes\n\n"
        "This folder may hold human-readable context or caller notes for the judgment layer. "
        "ACS does not parse it, validate it, hash it, or use it as runtime truth. Copy only the "
        "resolved values needed for this run into the ACS-owned project contracts.\n",
        encoding="utf-8",
    )
    for name, content in (
        ("content-brief.md", default_content_brief(project, edit_plan)),
        ("recording-plan.md", default_recording_plan(project, edit_plan)),
    ):
        path = project_dir / name
        if force or not path.exists():
            path.write_text(content, encoding="utf-8")
    learning_path = project_dir / "learning.json"
    if force or not learning_path.exists():
        write_json(
            learning_path,
            {"what_worked": "", "what_to_change": "", "next_experiment": ""},
        )
    (project_dir / "README.md").write_text(
        f"# {project['title']}\n\n"
        "This is a local Agentic Content System workspace. Edit the JSON contracts, add source media,\n"
        "ingest a transcript, and approve `edit-plan.json` before consequential render/package steps.\n\n"
        "The workspace does not post externally; `publish/` is a validated handoff package.\n",
        encoding="utf-8",
    )
    return project_dir
