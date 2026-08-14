#!/usr/bin/env python3
"""Resolve, validate, and run one Agentic Workflow lifecycle operation."""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
from typing import Optional, Sequence, Tuple
from urllib.parse import quote
from urllib.request import Request, urlopen


REPOSITORY = "jimmfan/agentic-workflow"
DEFAULT_REF = "main"
LOCAL_SOURCE_REVISION = "unreleased-local-package"
PACKAGE_MARKER = ("skills", "agentic-workflow")
MAX_ARCHIVE_BYTES = 20 * 1024 * 1024
MAX_MEMBER_BYTES = 5 * 1024 * 1024
MAX_MEMBERS = 500
EXECUTABLE_PACKAGE_PATHS = frozenset()
MINIMUM_PYTHON = (3, 11)
RUNTIME_PACKAGE_REQUIREMENTS = (
    (PurePosixPath("scripts/lifecycle.py"), "lifecycle entrypoint"),
    (PurePosixPath("scripts/adopt.py"), "framework reconciliation entrypoint"),
    (PurePosixPath("payload/distribution/manifest.json"), "lifecycle mapping metadata"),
)
ARCHIVE_MODE_VARIANTS = {
    0o644: {0o644, 0o664},
    0o755: {0o755, 0o775},
}


class BootstrapError(RuntimeError):
    """A bounded bootstrap failure with an actionable message."""


def configure_console() -> None:
    """Keep terminal output writable when the active encoding is restrictive."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except (AttributeError, OSError, ValueError):
                pass


def require_supported_python() -> None:
    if sys.version_info < MINIMUM_PYTHON:
        found = ".".join(str(part) for part in sys.version_info[:3])
        raise BootstrapError(f"Python 3.11 or newer is required; found Python {found}")


def request_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "agentic-workflow-bootstrap"})
    try:
        with urlopen(request, timeout=30) as response:
            data = response.read(MAX_ARCHIVE_BYTES + 1)
    except OSError as exc:
        raise BootstrapError(f"could not download {url}: {exc}") from exc
    if len(data) > MAX_ARCHIVE_BYTES:
        raise BootstrapError(f"download exceeded {MAX_ARCHIVE_BYTES} bytes")
    return data


def resolve_revision(ref: str) -> str:
    if re.fullmatch(r"[0-9a-f]{40}", ref):
        return ref
    url = f"https://api.github.com/repos/{REPOSITORY}/commits/{quote(ref, safe='')}"
    try:
        value = json.loads(request_bytes(url).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BootstrapError(f"GitHub returned an invalid commit response for {ref!r}") from exc
    revision = value.get("sha") if isinstance(value, dict) else None
    if not isinstance(revision, str) or re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        raise BootstrapError(f"GitHub did not resolve {ref!r} to a commit")
    return revision


def select_source(action: str, target: Path, ref: str, archive_url: Optional[str]) -> Tuple[str, str]:
    if archive_url:
        revision = ref if re.fullmatch(r"[0-9a-f]{40}", ref) else LOCAL_SOURCE_REVISION
        return revision, archive_url
    revision = resolve_revision(ref)
    return revision, f"https://codeload.github.com/{REPOSITORY}/tar.gz/{revision}"


def package_relative(name: str) -> Optional[PurePosixPath]:
    path = PurePosixPath(name)
    parts = path.parts
    for index in range(len(parts) - 1):
        if parts[index : index + 2] == PACKAGE_MARKER:
            relative = PurePosixPath(*parts[index + 2 :])
            return relative if relative.parts else None
    return None


def ensure_directory(path: Path, package: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    current = path
    while current != package.parent:
        current.chmod(0o755)
        current = current.parent


def reviewed_archive_mode(member: tarfile.TarInfo, relative: PurePosixPath) -> int:
    mode = stat.S_IMODE(member.mode)
    expected = 0o755 if member.isdir() or relative.as_posix() in EXECUTABLE_PACKAGE_PATHS else 0o644
    allowed = ARCHIVE_MODE_VARIANTS[expected]
    if mode not in allowed:
        kind = "directory" if member.isdir() else "file"
        raise BootstrapError(
            f"archive package {kind} mode must represent {expected:04o}, found {mode:04o}: {member.name}"
        )
    return expected


def extract_package(archive: bytes, destination: Path) -> Path:
    package = destination / "agentic-workflow"
    ensure_directory(package, package)
    seen = set()
    total = 0
    try:
        opened = tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz")
    except tarfile.TarError as exc:
        raise BootstrapError(f"download is not a valid gzip tar archive: {exc}") from exc
    with opened:
        members = opened.getmembers()
        if len(members) > MAX_MEMBERS:
            raise BootstrapError(f"archive contains more than {MAX_MEMBERS} entries")
        for member in members:
            archive_path = PurePosixPath(member.name)
            relative = package_relative(member.name)
            if relative is None:
                continue
            if (
                archive_path.is_absolute()
                or ".." in archive_path.parts
                or "." in archive_path.parts
                or relative.is_absolute()
                or ".." in relative.parts
                or "." in relative.parts
            ):
                raise BootstrapError(f"archive contains an unsafe package path: {member.name}")
            if member.issym() or member.islnk() or not (member.isdir() or member.isfile()):
                raise BootstrapError(f"archive contains an unsupported package entry: {member.name}")
            mode = reviewed_archive_mode(member, relative)
            target = package.joinpath(*relative.parts)
            if target in seen:
                raise BootstrapError(f"archive contains duplicate package path: {relative}")
            seen.add(target)
            if member.isdir():
                ensure_directory(target, package)
                continue
            if member.size > MAX_MEMBER_BYTES or total + member.size > MAX_ARCHIVE_BYTES:
                raise BootstrapError(f"archive package content is too large: {relative}")
            source = opened.extractfile(member)
            if source is None:
                raise BootstrapError(f"cannot read archive member: {relative}")
            data = source.read(MAX_MEMBER_BYTES + 1)
            if len(data) != member.size:
                raise BootstrapError(f"archive member size changed while reading: {relative}")
            total += len(data)
            ensure_directory(target.parent, package)
            target.write_bytes(data)
            target.chmod(mode)
    if not seen:
        raise BootstrapError("archive does not contain skills/agentic-workflow")
    return package


def validate_runtime_package(package: Path) -> None:
    """Check only the package files required to start lifecycle reconciliation."""
    for relative, label in RUNTIME_PACKAGE_REQUIREMENTS:
        path = package.joinpath(*relative.parts)
        if not path.exists() and not path.is_symlink():
            raise BootstrapError(
                f"required {label} missing from downloaded package: {relative}"
            )
        if path.is_symlink() or not path.is_file():
            raise BootstrapError(
                f"required {label} is not a regular file in downloaded package: {relative}"
            )
        try:
            with path.open("rb") as handle:
                handle.read(1)
        except OSError as exc:
            raise BootstrapError(
                f"required {label} cannot be read from downloaded package: {relative}: {exc}"
            ) from exc


def run_package(package: Path, action: str, target: Path, dry_run: bool, revision: str) -> int:
    validate_runtime_package(package)
    lifecycle = package / "scripts" / "lifecycle.py"
    command = [sys.executable, str(lifecycle), action, str(target), "--source-revision", revision]
    if dry_run:
        command.append("--dry-run")
    return subprocess.run(command).returncode


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", default="install", choices=("install", "update", "status", "remove"))
    parser.add_argument("target", nargs="?", default=Path.cwd(), type=Path)
    parser.add_argument("--dry-run", action="store_true", help="show the operation without changing files")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Git tag, branch, or commit for install/update")
    parser.add_argument("--archive-url", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    require_supported_python()
    configure_console()
    args = parse_args(argv or sys.argv[1:])
    target = args.target.expanduser().absolute()
    if target.is_symlink() or not target.is_dir():
        raise BootstrapError(f"target must be an existing regular non-symlink directory: {target}")
    if target == Path(target.anchor):
        raise BootstrapError("refusing to operate on a filesystem root")
    revision, archive_url = select_source(args.action, target, args.ref, args.archive_url)
    archive = request_bytes(archive_url)
    with tempfile.TemporaryDirectory(prefix="agentic-workflow-") as temporary:
        package = extract_package(archive, Path(temporary))
        return run_package(package, args.action, target, args.dry_run, revision)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BootstrapError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
