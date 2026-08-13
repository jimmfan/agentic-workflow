#!/usr/bin/env python3
"""Coordinate framework payload and curated upstream provider lifecycle."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
from pathlib import Path
import subprocess
import sys
from typing import Iterable, Optional, Sequence


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
ADOPTER = PACKAGE_ROOT / "scripts" / "adopt.py"
PROVIDERS = PACKAGE_ROOT / "scripts" / "providers.py"
INSTALL_MANIFEST = Path("ai-workflow/install-manifest.json")
PROJECT_SEEDS = (
    (Path("payload/ai-workflow/templates/project-profile.md"), Path("ai-workflow/project-profile.md")),
    (Path("payload/ai-workflow/templates/active-state.md"), Path("ai-workflow/state/active.md")),
)


class LifecycleError(RuntimeError):
    """A coordinated lifecycle operation failed."""


def command(script: Path, action: str, root: Path, dry_run: bool, revision: str) -> list[str]:
    value = [sys.executable, str(script), action, str(root)]
    if script == ADOPTER:
        value.extend(("--source-revision", revision))
    if dry_run:
        value.append("--dry-run")
    return value


def run_checked(
    script: Path,
    action: str,
    root: Path,
    dry_run: bool,
    revision: str,
    *,
    quiet: bool = False,
) -> None:
    result = subprocess.run(
        command(script, action, root, dry_run, revision),
        capture_output=quiet,
        text=True,
    )
    if result.returncode != 0:
        detail = ""
        if quiet:
            detail = "\n".join(
                part.strip() for part in (result.stdout, result.stderr) if part and part.strip()
            )
        raise LifecycleError(
            f"{script.name} {action} failed with exit code {result.returncode}"
            + (f": {detail}" if detail else "")
        )


def status(root: Path, revision: str) -> int:
    payload = subprocess.run(command(ADOPTER, "status", root, False, revision)).returncode
    providers = subprocess.run(command(PROVIDERS, "status", root, False, revision)).returncode
    if payload == 2 or providers == 2:
        return 2
    return 0 if payload == 0 and providers == 0 else 1


def rendered_seed(source: Path, target: Path) -> bytes:
    data = (PACKAGE_ROOT / source).read_bytes()
    if target == Path("ai-workflow/state/active.md"):
        today = dt.datetime.now(dt.timezone.utc).date().isoformat().encode("ascii")
        data = data.replace(b"YYYY-MM-DD", today)
    return data


def remove_empty_parents(path: Path, root: Path) -> None:
    current = path.parent
    while current != root and current != root.parent:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def rollback_new_seeds(root: Path, originally_absent: Iterable[Path]) -> None:
    for relative in originally_absent:
        source = next(source for source, target in PROJECT_SEEDS if target == relative)
        destination = root / relative
        if (
            destination.is_file()
            and not destination.is_symlink()
            and hashlib.sha256(destination.read_bytes()).digest()
            == hashlib.sha256(rendered_seed(source, relative)).digest()
        ):
            destination.unlink()
            remove_empty_parents(destination, root)


def install(root: Path, dry_run: bool, revision: str) -> None:
    if dry_run:
        run_checked(ADOPTER, "install", root, True, revision)
        run_checked(PROVIDERS, "install", root, True, revision)
        return
    existed = (root / INSTALL_MANIFEST).exists()
    originally_absent = {
        target for _source, target in PROJECT_SEEDS if not (root / target).exists()
    }
    run_checked(ADOPTER, "install", root, True, revision, quiet=True)
    run_checked(PROVIDERS, "install", root, True, revision, quiet=True)
    run_checked(ADOPTER, "install", root, False, revision)
    try:
        run_checked(PROVIDERS, "install", root, False, revision)
    except LifecycleError as error:
        if not existed:
            rollback = subprocess.run(
                command(ADOPTER, "remove", root, False, revision),
                capture_output=True,
                text=True,
            )
            if rollback.returncode != 0:
                detail = "\n".join(
                    part.strip() for part in (rollback.stdout, rollback.stderr) if part and part.strip()
                )
                raise LifecycleError(
                    f"provider installation failed and payload rollback also failed: {error}; {detail}"
                ) from error
            rollback_new_seeds(root, originally_absent)
        raise
    print("✓ Agentic Workflow payload and curated upstream providers are ready.")


def update(root: Path, dry_run: bool, revision: str) -> None:
    run_checked(ADOPTER, "update", root, True, revision, quiet=not dry_run)
    run_checked(PROVIDERS, "update", root, dry_run, revision)
    if dry_run:
        return
    run_checked(ADOPTER, "update", root, False, revision)
    print("✓ Agentic Workflow payload and curated upstream providers are updated and verified.")


def remove(root: Path, dry_run: bool, revision: str) -> None:
    run_checked(ADOPTER, "remove", root, True, revision, quiet=not dry_run)
    run_checked(PROVIDERS, "remove", root, dry_run, revision)
    if dry_run:
        return
    run_checked(ADOPTER, "remove", root, False, revision)
    print("✓ Agentic Workflow and its unchanged framework-installed providers were removed.")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "update", "status", "remove"))
    parser.add_argument("target", nargs="?", default=Path.cwd(), type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source-revision", default="unreleased-local-package", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.action == "status" and args.dry_run:
        raise LifecycleError("--dry-run is not valid for status")
    root = args.target.expanduser().resolve()
    if not root.is_dir():
        raise LifecycleError(f"target project directory does not exist: {root}")
    if root == Path(root.anchor):
        raise LifecycleError("refusing to operate on a filesystem root")
    if args.action == "install":
        install(root, args.dry_run, args.source_revision)
    elif args.action == "update":
        update(root, args.dry_run, args.source_revision)
    elif args.action == "status":
        return status(root, args.source_revision)
    else:
        remove(root, args.dry_run, args.source_revision)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LifecycleError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
