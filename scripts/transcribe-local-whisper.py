#!/usr/bin/env python3
"""Transcribe footage locally with Whisper for the Agentic Content System.

Outputs agent-readable cached transcripts at:

    <source-dir>/edit/transcripts/<clip-stem>.json

The JSON preserves the word-list shape used by the existing optional editor
packer, while keeping transcription fully local.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


MEDIA_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".webm",
    ".avi",
    ".wav",
    ".mp3",
    ".m4a",
    ".aac",
    ".aiff",
    ".flac",
}


REPO_ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        sys.exit(f"Missing command: {cmd[0]}")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"Command failed with exit code {exc.returncode}: {' '.join(cmd)}")


def collect_media(path: Path, recursive: bool) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() not in MEDIA_EXTENSIONS:
            sys.exit(f"Unsupported media file: {path}")
        return [path]

    if not path.is_dir():
        sys.exit(f"Input path not found: {path}")

    globber = path.rglob("*") if recursive else path.glob("*")
    files = [
        candidate
        for candidate in globber
        if candidate.is_file() and candidate.suffix.lower() in MEDIA_EXTENSIONS
    ]
    return sorted(files)


def default_edit_dir(input_path: Path) -> Path:
    if input_path.is_file():
        return input_path.parent / "edit"
    return input_path / "edit"


def extract_audio(media_path: Path, wav_path: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(media_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(wav_path),
        ]
    )


def load_whisper_model(model_name: str, device: str, model_cache_dir: Path):
    try:
        import whisper  # type: ignore
    except ImportError:
        sys.exit(
            "Python package 'openai-whisper' is not installed.\n"
            "Install the repo-local runtime with: ./scripts/setup-local-transcription.sh"
        )

    if not hasattr(whisper, "load_model"):
        sys.exit(
            "Imported a Python package named 'whisper', but it is not OpenAI Whisper.\n"
            "Install the expected repo-local runtime with: ./scripts/setup-local-transcription.sh"
        )

    model_cache_dir.mkdir(parents=True, exist_ok=True)

    if device == "auto":
        return whisper.load_model(model_name, download_root=str(model_cache_dir))
    return whisper.load_model(model_name, device=device, download_root=str(model_cache_dir))


def whisper_words(result: dict[str, Any]) -> list[dict[str, Any]]:
    words: list[dict[str, Any]] = []
    for segment in result.get("segments", []):
        for item in segment.get("words", []) or []:
            start = item.get("start")
            end = item.get("end")
            text = item.get("word") or item.get("text") or ""
            if start is None or end is None or not text:
                continue
            words.append(
                {
                    "type": "word",
                    "text": str(text).strip(),
                    "start": float(start),
                    "end": float(end),
                    "speaker_id": "speaker_0",
                }
            )
    return words


def transcribe_one(
    model: Any,
    media_path: Path,
    out_path: Path,
    language: str | None,
    fp16: str,
) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        audio_path = Path(tmp) / f"{media_path.stem}.wav"
        print(f"extracting audio: {media_path.name}", flush=True)
        extract_audio(media_path, audio_path)

        options: dict[str, Any] = {
            "word_timestamps": True,
            "verbose": False,
        }
        if language:
            options["language"] = language
        if fp16 != "auto":
            options["fp16"] = fp16 == "true"

        print(f"transcribing locally with Whisper: {media_path.name}", flush=True)
        result = model.transcribe(str(audio_path), **options)

    payload = {
        "text": result.get("text", ""),
        "language": result.get("language", language),
        "words": whisper_words(result),
        "metadata": {
            "engine": "local-whisper",
            "source": str(media_path),
            "note": "Local Whisper transcript kept in an open word-timestamp JSON shape.",
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved: {out_path} ({len(payload['words'])} words)", flush=True)


def pack_transcripts(edit_dir: Path) -> None:
    helper = Path.home() / "plugins/video-use/skills/video-use/helpers/pack_transcripts.py"
    if not helper.exists():
        print(
            "Skipping optional transcript pack step: editor packer was not found at "
            f"{helper}",
            file=sys.stderr,
        )
        return
    run([sys.executable, str(helper), "--edit-dir", str(edit_dir)])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local Whisper transcription for Agentic Content System."
    )
    parser.add_argument("input", type=Path, help="Media file or ACS source/legacy footage directory.")
    parser.add_argument(
        "--edit-dir",
        type=Path,
        default=None,
        help="Edit directory. Default: <input-dir>/edit.",
    )
    parser.add_argument(
        "--model",
        default="large",
        help="Whisper model name. Default: large. Examples: large, large-v3, medium.",
    )
    parser.add_argument(
        "--model-cache-dir",
        type=Path,
        default=REPO_ROOT / ".cache/whisper",
        help="Where Whisper models are stored. Default: repo-local .cache/whisper.",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Optional language code, e.g. da or en. Omit for auto-detect.",
    )
    parser.add_argument(
        "--device",
        default="auto",
        help="Whisper device. Default: auto. Examples: cpu, cuda, mps.",
    )
    parser.add_argument(
        "--fp16",
        choices=["auto", "true", "false"],
        default="auto",
        help="Force Whisper fp16 behavior. Use false on CPU if needed.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="When input is a directory, scan recursively.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-transcribe even if cached transcript JSON already exists.",
    )
    parser.add_argument(
        "--pack",
        action="store_true",
        help="After transcription, run the optional editor packer to create takes_packed.md.",
    )
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg is required and was not found on PATH.")

    input_path = args.input.expanduser().resolve()
    edit_dir = (args.edit_dir or default_edit_dir(input_path)).expanduser().resolve()
    media_files = collect_media(input_path, args.recursive)
    if not media_files:
        sys.exit(f"No supported media files found in {input_path}")

    transcripts_dir = edit_dir / "transcripts"
    pending: list[tuple[Path, Path]] = []

    for media_path in media_files:
        out_path = transcripts_dir / f"{media_path.stem}.json"
        if out_path.exists() and not args.force:
            print(f"cached: {out_path}")
            continue
        pending.append((media_path, out_path))

    if pending:
        model_cache_dir = args.model_cache_dir.expanduser().resolve()
        model = load_whisper_model(args.model, args.device, model_cache_dir)
    else:
        model = None

    for media_path, out_path in pending:
        transcribe_one(
            model=model,
            media_path=media_path,
            out_path=out_path,
            language=args.language,
            fp16=args.fp16,
        )

    if args.pack:
        pack_transcripts(edit_dir)


if __name__ == "__main__":
    main()
