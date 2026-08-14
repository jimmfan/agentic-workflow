#!/usr/bin/env python3
"""Coordinate the core payload and best-effort optional provider skills."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
from typing import Iterable


SCRIPT_ROOT = Path(__file__).resolve().parent
ADOPT = SCRIPT_ROOT / "adopt.py"
PROVIDERS = SCRIPT_ROOT / "providers.py"
MINIMUM_PYTHON = (3, 11)
LOCAL_REVISION = "unreleased-local-package"


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except (AttributeError, OSError, ValueError):
                pass


def run(script: Path, arguments: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *arguments],
        text=True,
        capture_output=capture,
        errors="backslashreplace",
    )


def provider_attempt(command: str, target: Path, dry_run: bool) -> None:
    arguments = [command, str(target)]
    if dry_run:
        arguments.append("--dry-run")
    result = run(PROVIDERS, arguments)
    if result.returncode != 0 and not dry_run:
        print(
            "WARNING: Optional provider setup did not complete. The core router and local workflows remain usable.",
            file=sys.stderr,
        )


def install_or_update(command: str, target: Path, dry_run: bool, revision: str) -> int:
    arguments = [command, str(target), "--source-revision", revision]
    if dry_run:
        arguments.append("--dry-run")
    core = run(ADOPT, arguments)
    if core.returncode != 0:
        return core.returncode
    provider_attempt("install", target, dry_run)
    if not dry_run:
        print("OK: Core routing is ready.")
    return 0


def status(target: Path, revision: str) -> int:
    core = run(ADOPT, ["status", str(target), "--source-revision", revision])
    provider = run(PROVIDERS, ["status", str(target)])
    if provider.returncode != 0:
        print("WARNING: Optional provider status is unavailable; core status is unchanged.", file=sys.stderr)
    return core.returncode


def remove(target: Path, dry_run: bool, revision: str) -> int:
    provider_attempt("remove", target, dry_run)
    arguments = ["remove", str(target), "--source-revision", revision]
    if dry_run:
        arguments.append("--dry-run")
    return run(ADOPT, arguments).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install", "update", "status", "remove"))
    parser.add_argument("target", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source-revision", default=LOCAL_REVISION)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    configure_console()
    if sys.version_info < MINIMUM_PYTHON:
        print("ERROR: Agentic Workflow requires Python 3.11 or newer", file=sys.stderr)
        return 2
    args = build_parser().parse_args(argv)
    if args.command == "status":
        if args.dry_run:
            print("ERROR: status does not accept --dry-run", file=sys.stderr)
            return 2
        return status(args.target, args.source_revision)
    if args.command in {"install", "update"}:
        return install_or_update(args.command, args.target, args.dry_run, args.source_revision)
    return remove(args.target, args.dry_run, args.source_revision)


if __name__ == "__main__":
    raise SystemExit(main())
