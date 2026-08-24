"""Stable command-line interface for the Agentic Content System."""

from __future__ import annotations

import argparse
import difflib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .adapters import import_adapter_output
from .derive import derive_project
from .errors import ACSUserError
from .inspect import inspect_project
from .io import copy_file, read_json, write_json
from .media import binary_path
from .package import package_project, verify_package
from .paths import GENERATED_DIRS, display_path, inside_project, project_file, resolve_project
from .project import ProjectContracts, current_approval_hash, load_contracts, require_valid_brand_profile, require_valid_project
from .render import render_project
from .report import create_review_report
from .result import export_result
from .scaffold import load_brand_profile, scaffold_project
from .schemas import load_schema
from .transcript import (
    RAW_TRANSCRIPT_RELATIVE,
    REVIEWED_TRANSCRIPT_RELATIVE,
    build_raw_record,
    build_reviewed_record,
    load_and_normalize,
    load_current_reviewed_transcript,
    is_asr_transcript,
)
from .validation import require_valid


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acs",
        description="Local-first Agentic Content System: contracts, approved renders, derivatives, and publish-ready handoff.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Check Python, FFmpeg, ffprobe, and optional local Whisper readiness.")
    doctor.add_argument("--json", action="store_true", dest="as_json", help="Print machine-readable checks.")

    init = sub.add_parser("init", help="Create a portable ACS workspace contract and folder scaffold.")
    init.add_argument("project", metavar="workspace", help="ACS content workspace; relative or absolute paths are supported.")
    init.add_argument("--brand", metavar="path", help="Copy and validate an ACS-owned brand profile into workspace brand.json.")
    init.add_argument("--force", action="store_true", help="Replace existing contract files in the target workspace.")

    profile = sub.add_parser("validate-profile", help="Validate a clone-owned workspace/channel/brand.json profile without writing a workspace.")
    profile.add_argument("profile", metavar="brand-profile")

    inspect = sub.add_parser("inspect", help="Probe source media and write inspection.json.")
    inspect.add_argument("project", metavar="workspace")

    validate = sub.add_parser("validate", help="Validate all workspace contracts and cross-references.")
    validate.add_argument("project", metavar="workspace")
    validate.add_argument("--contracts-only", action="store_true", help="Skip source-file existence checks for an initial scaffold.")

    plan = sub.add_parser("plan", help="Show approval state, approve a reviewed plan, or diff the previous snapshot.")
    plan.add_argument("project", metavar="workspace")
    plan.add_argument("--approve", action="store_true", help="Record explicit approval for the current edit plan.")
    plan.add_argument("--by", default="", help="Approver identity required with --approve.")
    plan.add_argument("--note", default="", help="Approval note.")
    plan.add_argument("--diff", action="store_true", help="Show the current plan against the previous approval snapshot.")

    ingest = sub.add_parser("ingest-transcript", help="Normalize JSON/Whisper/Markdown/SRT/VTT into transcripts/active.json.")
    ingest.add_argument("project", metavar="workspace")
    ingest.add_argument("transcript")
    ingest.add_argument(
        "--replace-raw",
        action="store_true",
        help="Explicitly archive the prior immutable raw record before replacing it.",
    )

    review_transcript = sub.add_parser(
        "review-transcript",
        help="Register a bounded reviewed transcript truth against the immutable raw record.",
    )
    review_transcript.add_argument("project", metavar="workspace")
    review_transcript.add_argument("transcript")
    review_transcript.add_argument("--by", required=True, help="Reviewer identity.")
    review_transcript.add_argument(
        "--status",
        choices=["reviewed", "partially_reviewed", "partial", "rejected"],
        default="reviewed",
        help="Reviewed truth state; partial is accepted only when the selected ranges are covered.",
    )
    review_transcript.add_argument("--note", default="", help="Human-readable review note.")

    adapter = sub.add_parser(
        "import-adapter",
        help="Supervisedly import a rendered adapter output plus its JSON plan/manifest into normal ACS proof.",
    )
    adapter.add_argument("project", metavar="workspace")
    adapter.add_argument("output", metavar="rendered-output")
    adapter.add_argument("--manifest", required=True, help="Adapter JSON plan or output manifest.")
    adapter.add_argument("--adapter", required=True, help="Named adapter, for example video-edit-cli.")
    adapter.add_argument("--version", default="", help="Optional adapter version or snapshot label.")
    adapter.add_argument("--by", required=True, help="Reviewer who approved this import.")
    adapter.add_argument("--provenance", default="", help="Source/provenance note bound to the imported result.")

    render = sub.add_parser("render", help="Render approved long-form and/or vertical short media with FFmpeg.")
    render.add_argument("project", metavar="workspace")
    render.add_argument("--kind", choices=["all", "long", "short"], default="all")
    render.add_argument("--force", action="store_true", help="Re-render even when the deterministic record is current.")

    derive = sub.add_parser("derive", help="Create deterministic text derivatives from an approved plan and transcript.")
    derive.add_argument("project", metavar="workspace")

    package = sub.add_parser("package", help="Build a publish-ready local package for enabled routes only.")
    package.add_argument("project", metavar="workspace")

    verify = sub.add_parser("verify", help="Verify package hashes, enabled routes, provenance, and no external posting.")
    verify.add_argument("project", metavar="workspace")

    report = sub.add_parser("review-report", help="Write a static local HTML review report.")
    report.add_argument("project", metavar="workspace")

    result = sub.add_parser("export-result", help="Export hashed proof, route results, review status, and learning.")
    result.add_argument("project", metavar="workspace")

    clean = sub.add_parser("clean", help="Remove generated outputs while preserving contracts, sources, and transcripts.")
    clean.add_argument("project", metavar="workspace")
    clean.add_argument(
        "--outputs",
        action="store_true",
        help="Confirm removal of renders, derivatives, package, reports, results, and inspection.",
    )
    return parser


def _load(project_arg: str):
    project_dir = resolve_project(project_arg)
    if not project_dir.is_dir():
        raise ACSUserError(f"Workspace directory not found: {project_dir}")
    return load_contracts(project_dir), project_dir


def _print_json(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def command_doctor(as_json: bool) -> int:
    checks = {
        "python": {"ok": sys.version_info >= (3, 10), "detail": sys.version.split()[0]},
        "ffmpeg": {"ok": binary_path("ffmpeg") is not None, "detail": binary_path("ffmpeg") or "not found"},
        "ffprobe": {"ok": binary_path("ffprobe") is not None, "detail": binary_path("ffprobe") or "not found"},
        "local_whisper_optional": {
            "ok": True,
            "detail": "Use workspace/engine/scripts/transcribe-local-whisper.py with the repo-local .venv when desired.",
        },
    }
    if as_json:
        _print_json(checks)
    else:
        for name, item in checks.items():
            print(f"{'OK' if item['ok'] else 'MISSING'} {name}: {item['detail']}")
    return 0 if all(item["ok"] for item in checks.values()) else 1


def command_init(args: argparse.Namespace) -> int:
    brand = load_brand_profile(args.brand) if args.brand else None
    project_dir = scaffold_project(args.project, brand=brand, force=args.force)
    print(f"Initialized Agentic Content System workspace: {project_dir}")
    print("Next steps:")
    print(f"  1. Add source media at {display_path(project_dir, project_dir / 'sources')}")
    print(f"  2. Edit {display_path(project_dir, project_dir / 'project.json')} and {display_path(project_dir, project_dir / 'edit-plan.json')}")
    print("  3. Ingest a transcript, review, and run: acs plan <workspace> --approve --by <name>")
    return 0


def command_validate_profile(profile_arg: str) -> int:
    profile_path = Path(profile_arg).expanduser().resolve()
    brand = load_brand_profile(profile_path)
    require_valid_brand_profile(brand)
    print(f"Valid brand profile: {profile_path}")
    return 0


def command_inspect(args: argparse.Namespace) -> int:
    contracts, _ = _load(args.project)
    output = inspect_project(contracts)
    print(f"Inspected sources: {output}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    contracts, _ = _load(args.project)
    require_valid_project(contracts, require_sources=not args.contracts_only)
    print(f"Valid: {contracts.directory}")
    return 0


def command_plan(args: argparse.Namespace) -> int:
    contracts, project_dir = _load(args.project)
    plan_path = project_file(project_dir, "edit_plan")
    if args.diff:
        previous = project_dir / "edit-plan.previous.json"
        if previous.exists():
            old = previous.read_text(encoding="utf-8").splitlines(keepends=True)
            new = plan_path.read_text(encoding="utf-8").splitlines(keepends=True)
            print("".join(difflib.unified_diff(old, new, fromfile=str(previous), tofile=str(plan_path))))
        else:
            print("No previous plan snapshot; current plan is the first version.")
    if args.approve:
        if not args.by.strip():
            raise ACSUserError("--approve requires --by <approver>.")
        require_valid_project(contracts, require_sources=True)
        if plan_path.exists():
            (project_dir / "edit-plan.previous.json").write_text(plan_path.read_text(encoding="utf-8"), encoding="utf-8")
        plan = contracts.edit_plan
        previous_revision = int(plan.get("approval", {}).get("approval_revision", 0) or 0)
        plan["approval"] = {
            "status": "approved",
            "approved_by": args.by.strip(),
            "approved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "note": args.note.strip() or plan.get("approval", {}).get("note", ""),
            "approval_hash": "",
            "approval_revision": previous_revision + 1,
        }
        plan["approval"]["approval_hash"] = current_approval_hash(
            ProjectContracts(contracts.directory, contracts.brand, contracts.project, plan)
        )
        require_valid(plan, load_schema("edit-plan"), "edit-plan")
        write_json(plan_path, plan)
        print(f"Approved edit plan: {plan_path}")
    else:
        print(json.dumps(contracts.edit_plan.get("approval", {}), indent=2, sort_keys=True))
    return 0


def command_ingest(args: argparse.Namespace) -> int:
    contracts, project_dir = _load(args.project)
    require_valid_project(contracts, require_sources=True)
    input_path = Path(args.transcript).expanduser().resolve()
    normalized = load_and_normalize(input_path)
    raw_record = build_raw_record(
        normalized,
        project_dir=project_dir,
        project=contracts.project,
        input_path=input_path,
    )
    raw_path = project_dir / RAW_TRANSCRIPT_RELATIVE
    if raw_path.exists():
        previous_raw = read_json(raw_path)
        if previous_raw.get("content_hash") != raw_record.get("content_hash"):
            if not args.replace_raw:
                raise ACSUserError(
                    "Immutable raw transcript already exists with different content. "
                    "Pass --replace-raw to archive it before ingesting a new raw input."
                )
            archive = project_dir / "transcripts" / "raw-revisions" / f"raw-{previous_raw.get('content_hash', 'unknown')[:16]}.json"
            if not archive.exists():
                copy_file(raw_path, archive)
        else:
            raw_record = previous_raw
    write_json(raw_path, raw_record)
    # Keep the long-standing active.json path as a raw adapter view. It is
    # deliberately not used by publish-ready text or captions.
    target = inside_project(project_dir, contracts.project["transcript"]["path"], label="project.transcript.path")
    target.parent.mkdir(parents=True, exist_ok=True)
    write_json(target, normalized)
    if not is_asr_transcript(normalized, input_path):
        reviewed_path = project_dir / REVIEWED_TRANSCRIPT_RELATIVE
        previous_revision = 0
        if reviewed_path.exists():
            try:
                previous_revision = int(read_json(reviewed_path).get("revision", 0) or 0)
            except ACSUserError:
                previous_revision = 0
        reviewed = build_reviewed_record(
            normalized,
            raw_record=raw_record,
            project_dir=project_dir,
            project=contracts.project,
            reviewer="provided-transcript",
            status="reviewed",
            note="Provided transcript registered as reviewed truth; replace with human corrections when needed.",
            revision=previous_revision + 1,
        )
        write_json(reviewed_path, reviewed)
    print(f"Ingested transcript: {target}")
    print(f"Segments: {len(normalized['segments'])}")
    print(f"Raw transcript: {raw_path}")
    if is_asr_transcript(normalized, input_path):
        print("ASR input remains raw; run `acs review-transcript` before publish-ready steps.")
    else:
        print(f"Reviewed truth: {project_dir / REVIEWED_TRANSCRIPT_RELATIVE}")
    return 0


def command_review_transcript(args: argparse.Namespace) -> int:
    contracts, project_dir = _load(args.project)
    require_valid_project(contracts, require_sources=True)
    raw_path = project_dir / RAW_TRANSCRIPT_RELATIVE
    if not raw_path.exists():
        raise ACSUserError("Review requires an immutable raw transcript; run `acs ingest-transcript` first.")
    raw_record = read_json(raw_path)
    normalized = load_and_normalize(Path(args.transcript).expanduser().resolve())
    reviewed_path = project_dir / REVIEWED_TRANSCRIPT_RELATIVE
    previous_revision = 0
    if reviewed_path.exists():
        previous_revision = int(read_json(reviewed_path).get("revision", 0) or 0)
    reviewed = build_reviewed_record(
        normalized,
        raw_record=raw_record,
        project_dir=project_dir,
        project=contracts.project,
        reviewer=args.by,
        status=args.status,
        note=args.note,
        revision=previous_revision + 1,
    )
    write_json(reviewed_path, reviewed)
    print(f"Reviewed transcript revision {reviewed['revision']}: {reviewed_path}")
    print(f"Status: {reviewed['status']}; coverage ranges: {len(reviewed['coverage'])}")
    return 0


def command_import_adapter(args: argparse.Namespace) -> int:
    contracts, _ = _load(args.project)
    manifest = Path(args.manifest).expanduser().resolve()
    provenance = args.provenance.strip() or "Supervised local adapter output; source rights remain owned by the ACS production."
    record = import_adapter_output(
        contracts,
        Path(args.output),
        manifest,
        adapter=args.adapter,
        reviewer=args.by,
        provenance=provenance,
        adapter_version=args.version,
    )
    print(f"Imported adapter result: {record}")
    return 0


def command_render(args: argparse.Namespace) -> int:
    contracts, _ = _load(args.project)
    kinds = ["long", "short"] if args.kind == "all" else [args.kind]
    results = render_project(contracts, kinds, force=args.force)
    _print_json(results)
    return 0


def command_derive(args: argparse.Namespace) -> int:
    contracts, _ = _load(args.project)
    outputs = derive_project(contracts)
    for path in outputs:
        print(f"Derived: {path}")
    return 0


def command_package(args: argparse.Namespace) -> int:
    contracts, _ = _load(args.project)
    manifest = package_project(contracts)
    print(f"Publish-ready package: {manifest}")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    contracts, _ = _load(args.project)
    assets = verify_package(contracts)
    print(f"Verified publish package: {len(assets)} assets; external posting: false")
    return 0


def command_report(args: argparse.Namespace) -> int:
    contracts, _ = _load(args.project)
    report = create_review_report(contracts)
    print(f"Review report: {report}")
    return 0


def command_export_result(args: argparse.Namespace) -> int:
    contracts, _ = _load(args.project)
    result = export_result(contracts)
    print(f"Exported run result: {result}")
    return 0


def command_clean(args: argparse.Namespace) -> int:
    if not args.outputs:
        raise ACSUserError("Cleaning is intentionally explicit. Re-run with `clean <workspace> --outputs`.")
    _, project_dir = _load(args.project)
    for name in GENERATED_DIRS:
        path = project_dir / name
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    inspection = project_dir / "inspection.json"
    if inspection.exists():
        inspection.unlink()
    print(f"Cleaned generated outputs from: {project_dir}")
    print("Preserved: brand.json, project.json, edit-plan.json, sources/, transcripts/")
    return 0


COMMANDS = {
    "doctor": lambda args: command_doctor(args.as_json),
    "init": command_init,
    "validate-profile": lambda args: command_validate_profile(args.profile),
    "inspect": command_inspect,
    "validate": command_validate,
    "plan": command_plan,
    "ingest-transcript": command_ingest,
    "review-transcript": command_review_transcript,
    "import-adapter": command_import_adapter,
    "render": command_render,
    "derive": command_derive,
    "package": command_package,
    "verify": command_verify,
    "review-report": command_report,
    "export-result": command_export_result,
    "clean": command_clean,
}


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        return COMMANDS[args.command](args)
    except ACSUserError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
