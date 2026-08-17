"""Shared deterministic validation for bundled provider directory trees."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re


class SnapshotTreeError(RuntimeError):
    pass


MARKDOWN_LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")
TEXT_SUFFIXES = frozenset({".json", ".md", ".toml", ".txt", ".yaml", ".yml"})


def tree_digest(root: Path) -> str:
    if root.is_symlink() or not root.is_dir():
        raise SnapshotTreeError(f"provider tree is missing or unsafe: {root}")
    digest = sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        if path.is_symlink():
            raise SnapshotTreeError(f"provider tree contains a symlink: {path}")
        if path.is_dir():
            digest.update(b"D\0" + relative + b"\0")
        elif path.is_file():
            digest.update(b"F\0" + relative + b"\0" + sha256(path.read_bytes()).digest())
        else:
            raise SnapshotTreeError(f"provider tree contains an unsupported entry: {path}")
    return digest.hexdigest()


def validate_local_references(skill_root: Path) -> None:
    """Reject resource references that are missing or escape one skill directory."""
    root = skill_root.resolve()
    for path in sorted(skill_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            raise SnapshotTreeError(f"provider text resource is not UTF-8: {path}") from exc
        if "../" in text or "..\\" in text:
            raise SnapshotTreeError(f"provider resource may escape its skill directory: {path}")
        for raw_destination in MARKDOWN_LINK.findall(text):
            destination = raw_destination.strip().split(maxsplit=1)[0].strip("<>")
            destination = destination.split("#", 1)[0].split("?", 1)[0]
            if (
                not destination
                or "://" in destination
                or destination.startswith(("#", "/", "mailto:"))
                or destination == "link"
                or destination.startswith("./src/")
            ):
                continue
            target = (path.parent / destination).resolve()
            if target != root and root not in target.parents:
                raise SnapshotTreeError(f"provider reference escapes its skill directory: {path}: {destination}")
            if not target.exists():
                raise SnapshotTreeError(f"provider reference is missing from its skill directory: {path}: {destination}")
