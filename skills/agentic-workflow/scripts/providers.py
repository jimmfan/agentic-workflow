#!/usr/bin/env python3
"""Best-effort installation and inspection of optional upstream skills."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from typing import Iterable


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DECLARATION = PACKAGE_ROOT / "payload" / "ai-workflow" / "providers.json"
MINIMUM_PYTHON = (3, 11)


class ProviderError(RuntimeError):
    pass


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except (AttributeError, OSError, ValueError):
                pass


def safe_component(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or PurePosixPath(value).name != value:
        raise ProviderError(f"invalid {label}: {value!r}")
    return value


def load_provider() -> tuple[str, str, list[tuple[str, str]]]:
    if DECLARATION.is_symlink() or not DECLARATION.is_file():
        raise ProviderError("provider declaration is missing or unsafe")
    try:
        raw = json.loads(DECLARATION.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProviderError(f"cannot read provider declaration: {exc}") from exc
    provider = raw.get("provider") if isinstance(raw, dict) else None
    if not isinstance(provider, dict):
        raise ProviderError("provider declaration needs a provider object")
    repository = provider.get("repository")
    version = provider.get("version")
    skills = provider.get("skills")
    if not isinstance(repository, str) or repository.count("/") != 1:
        raise ProviderError("provider repository must use owner/name form")
    if not isinstance(version, str) or not version:
        raise ProviderError("provider version must be a non-empty immutable ref")
    if not isinstance(skills, list):
        raise ProviderError("provider skills must be an array")
    result: list[tuple[str, str]] = []
    for item in skills:
        if not isinstance(item, dict):
            raise ProviderError("provider skill entries must be objects")
        name = safe_component(item.get("name"), "provider skill name")
        path = item.get("path")
        if not isinstance(path, str):
            raise ProviderError(f"provider skill {name} needs a path")
        relative = PurePosixPath(path)
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise ProviderError(f"provider skill {name} has an unsafe path")
        result.append((name, path))
    if len({name for name, _path in result}) != len(result):
        raise ProviderError("provider skill names must be unique")
    return repository, version, result


def validate_root(raw: Path) -> Path:
    if not raw.exists() or raw.is_symlink() or not raw.is_dir():
        raise ProviderError(f"target must be an existing regular directory: {raw}")
    root = raw.resolve()
    if root.parent == root:
        raise ProviderError("refusing to use a filesystem root as the project target")
    for relative in (Path(".agents"), Path(".agents/skills")):
        path = root / relative
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise ProviderError(f"optional provider destination is unsafe: {relative}")
    return root


def destination_state(root: Path, name: str) -> str:
    directory = root / ".agents" / "skills" / name
    if not directory.exists() and not directory.is_symlink():
        return "missing"
    if directory.is_symlink() or not directory.is_dir():
        return "incompatible"
    skill = directory / "SKILL.md"
    if skill.is_symlink() or not skill.is_file():
        return "incompatible"
    return "present"


def status(root: Path) -> int:
    repository, version, skills = load_provider()
    present = 0
    missing = 0
    incompatible = 0
    for name, _path in skills:
        state = destination_state(root, name)
        if state == "present":
            present += 1
        elif state == "missing":
            missing += 1
        else:
            incompatible += 1
    print(f"Optional provider: {repository}@{version}")
    print(f"Optional provider skills: {present} present, {missing} missing, {incompatible} preserved incompatible")
    if missing:
        print("INFO: Missing provider skills do not block core routing; rerun install to offer installation.")
    if incompatible:
        print("WARNING: Same-named unknown provider content was preserved.")
    return 0


def install(root: Path, dry_run: bool) -> int:
    repository, version, skills = load_provider()
    missing: list[tuple[str, str]] = []
    for name, path in skills:
        state = destination_state(root, name)
        if state == "missing":
            missing.append((name, path))
        else:
            print(f"preserve optional provider skill {name}: {state}")
    if not missing:
        print("OK: Optional provider skills are already present or conservatively preserved.")
        return 0
    if dry_run:
        for name, _path in missing:
            print(f"would offer optional provider installation: {name}")
        return 0

    gh = shutil.which("gh")
    if gh is None:
        print("WARNING: GitHub CLI with `gh skill` is unavailable; optional providers were skipped.", file=sys.stderr)
        return 1

    failed = False
    for name, path in missing:
        # Recheck immediately before the external tool writes. Existing content is
        # always preserved; provider installation has no ownership database.
        if destination_state(root, name) != "missing":
            print(f"WARNING: preserving provider destination that appeared during install: {name}", file=sys.stderr)
            failed = True
            continue
        command = [
            gh,
            "skill",
            "install",
            repository,
            path,
            "--pin",
            version,
            "--scope",
            "project",
            "--agent",
            "codex",
        ]
        result = subprocess.run(command, cwd=root, text=True, capture_output=True, errors="backslashreplace")
        if result.returncode != 0:
            detail = " ".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
            print(f"WARNING: optional provider install failed for {name}: {detail}", file=sys.stderr)
            failed = True
        else:
            print(f"installed optional provider skill {name} from {repository}@{version}")
    return 1 if failed else 0


def remove(root: Path, dry_run: bool) -> int:
    _repository, _version, skills = load_provider()
    present = [name for name, _path in skills if destination_state(root, name) != "missing"]
    prefix = "would preserve" if dry_run else "preserved"
    if present:
        print(f"{prefix} optional provider directories: {', '.join(present)}")
    print("INFO: Provider removal is intentionally manual because v0 keeps no ownership database.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install", "status", "remove"))
    parser.add_argument("target", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    configure_console()
    if sys.version_info < MINIMUM_PYTHON:
        print("ERROR: Agentic Workflow requires Python 3.11 or newer", file=sys.stderr)
        return 2
    try:
        args = build_parser().parse_args(argv)
        root = validate_root(args.target)
        if args.command == "status":
            if args.dry_run:
                raise ProviderError("status does not accept --dry-run")
            return status(root)
        if args.command == "remove":
            return remove(root, args.dry_run)
        return install(root, args.dry_run)
    except ProviderError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
