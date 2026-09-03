#!/usr/bin/env python3
"""Initialize project-owned Wayfinder effort maps."""

import argparse
from pathlib import Path
import re
import sys


EFFORT_KEY = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NAME_PLACEHOLDER = "{{WAYFINDER_EFFORT_NAME}}"


class WayfinderInitError(RuntimeError):
    """An initialization failure that must not overwrite project state."""


def validate_arguments(effort: str, name: str) -> None:
    if EFFORT_KEY.fullmatch(effort) is None:
        raise WayfinderInitError(
            f"unsafe effort storage key {effort!r}; use lowercase letters, numbers, "
            "and single hyphens"
        )
    if (
        not name
        or name != name.strip()
        or any(ord(character) < 32 or ord(character) == 127 for character in name)
    ):
        raise WayfinderInitError(
            "effort name must be a non-empty single line without surrounding whitespace"
        )


def cleanup_created(paths: list[Path], map_path: Path) -> None:
    for path in reversed(paths):
        try:
            if path == map_path:
                path.unlink()
            else:
                path.rmdir()
        except OSError:
            pass


def init_effort(project: Path, schema_path: Path, effort: str, name: str) -> Path:
    validate_arguments(effort, name)
    try:
        rendered = schema_path.read_text(encoding="utf-8").replace(
            NAME_PLACEHOLDER, name
        )
    except (OSError, UnicodeError) as exc:
        raise WayfinderInitError(f"cannot read Wayfinder map schema: {exc}") from exc

    root = project / ".agent-wayfinder"
    effort_path = root / effort
    map_path = effort_path / "map.md"
    created: list[Path] = []

    try:
        if root.is_symlink():
            raise WayfinderInitError(f"Wayfinder root is a symlink: {root}")
        if root.exists() and not root.is_dir():
            raise WayfinderInitError(f"Wayfinder root is not a directory: {root}")
        if not root.exists():
            root.mkdir()
            created.append(root)
        if root.is_symlink() or not root.is_dir():
            raise WayfinderInitError(f"unsafe Wayfinder root: {root}")
        if effort_path.exists() or effort_path.is_symlink():
            raise WayfinderInitError(
                f"effort already exists: .agent-wayfinder/{effort}"
            )

        effort_path.mkdir()
        created.append(effort_path)
        with map_path.open("x", encoding="utf-8", newline="\n") as handle:
            created.append(map_path)
            handle.write(rendered)
    except (OSError, UnicodeError, WayfinderInitError) as exc:
        cleanup_created(created, map_path)
        if isinstance(exc, WayfinderInitError):
            raise
        raise WayfinderInitError(f"cannot create Wayfinder map: {exc}") from exc

    return map_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init-effort",))
    parser.add_argument("--effort", required=True, help="stable effort storage key")
    parser.add_argument("--name", required=True, help="human-readable effort name")
    args = parser.parse_args(argv)

    framework = Path(__file__).absolute().parents[1]
    project = framework.parent
    schema = framework / "schemas/wayfinder/map.md"
    try:
        created = init_effort(project, schema, args.effort, args.name)
        print(f"CREATED {created.relative_to(project).as_posix()}")
        return 0
    except WayfinderInitError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
