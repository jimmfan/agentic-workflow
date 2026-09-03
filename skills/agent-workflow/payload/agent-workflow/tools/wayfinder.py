#!/usr/bin/env python3
"""Initialize project-owned Wayfinder effort maps."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
import os
from pathlib import Path
import re
import stat
import sys


MINIMUM_PYTHON = (3, 11)
EFFORT_KEY = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NAME_PLACEHOLDER = "{{WAYFINDER_EFFORT_NAME}}"
REQUIRED_PLACEHOLDERS = (
    "{{REQUIRED_OBJECTIVE}}",
    "{{REQUIRED_SCOPE}}",
    "{{REQUIRED_CURRENT_STATE}}",
)


class WayfinderInitError(RuntimeError):
    """An initialization failure that must not overwrite project state."""


def path_exists(path: Path) -> bool:
    return os.path.lexists(path)


def require_directory(path: Path, label: str) -> None:
    try:
        details = os.lstat(path)
    except OSError as exc:
        raise WayfinderInitError(f"cannot inspect {label}: {exc}") from exc
    if stat.S_ISLNK(details.st_mode):
        raise WayfinderInitError(f"{label} is a symlink: {path}")
    if not stat.S_ISDIR(details.st_mode):
        raise WayfinderInitError(f"{label} is not a directory: {path}")


def require_regular_file(path: Path, label: str) -> None:
    try:
        details = os.lstat(path)
    except OSError as exc:
        raise WayfinderInitError(f"cannot inspect {label}: {exc}") from exc
    if stat.S_ISLNK(details.st_mode):
        raise WayfinderInitError(f"{label} is a symlink: {path}")
    if not stat.S_ISREG(details.st_mode):
        raise WayfinderInitError(f"{label} is not a regular file: {path}")


def installed_paths() -> tuple[Path, Path]:
    script = Path(os.path.abspath(__file__))
    tools = script.parent
    framework = tools.parent
    project = framework.parent
    if (
        script.name != "wayfinder.py"
        or tools.name != "tools"
        or framework.name != ".agent-workflow"
    ):
        raise WayfinderInitError(
            "helper must run from an installed .agent-workflow/tools/wayfinder.py"
        )
    require_directory(project, "project root")
    require_directory(framework, "installed .agent-workflow")
    require_directory(tools, "installed tools directory")
    require_regular_file(script, "Wayfinder helper")
    schema = framework / "schemas/wayfinder/map.md"
    require_directory(framework / "schemas", "installed schemas directory")
    require_directory(
        framework / "schemas/wayfinder", "installed Wayfinder schema directory"
    )
    require_regular_file(schema, "Wayfinder map schema")
    return project, schema


def validate_effort_key(value: str) -> None:
    if EFFORT_KEY.fullmatch(value) is None:
        raise WayfinderInitError(
            f"unsafe effort storage key {value!r}; use lowercase letters, numbers, "
            "and single hyphens"
        )


def validate_name(value: str) -> None:
    if (
        not value
        or value != value.strip()
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise WayfinderInitError(
            "effort name must be a non-empty single line without surrounding whitespace"
        )


def render_schema(schema_path: Path, name: str) -> str:
    try:
        schema = schema_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise WayfinderInitError(f"cannot read Wayfinder map schema: {exc}") from exc
    if schema.count(NAME_PLACEHOLDER) != 1 or any(
        schema.count(placeholder) != 1 for placeholder in REQUIRED_PLACEHOLDERS
    ):
        raise WayfinderInitError("Wayfinder map schema has invalid placeholders")
    return schema.replace(NAME_PLACEHOLDER, name)


def remove_created_paths(
    map_path: Path,
    effort_path: Path,
    root: Path,
    *,
    map_created: bool,
    effort_created: bool,
    root_created: bool,
) -> None:
    try:
        if map_created and map_path.is_file() and not map_path.is_symlink():
            map_path.unlink()
        if effort_created:
            effort_path.rmdir()
        if root_created:
            root.rmdir()
    except OSError:
        pass


def init_effort(project: Path, schema_path: Path, effort: str, name: str) -> Path:
    validate_effort_key(effort)
    validate_name(name)
    rendered = render_schema(schema_path, name)
    root = project / ".agent-wayfinder"
    effort_path = root / effort
    map_path = effort_path / "map.md"

    root_created = False
    effort_created = False
    map_created = False
    if path_exists(root):
        require_directory(root, "Wayfinder root")
    if path_exists(effort_path):
        raise WayfinderInitError(f"effort already exists: .agent-wayfinder/{effort}")

    try:
        if not path_exists(root):
            root.mkdir()
            root_created = True
        require_directory(root, "Wayfinder root")
        if path_exists(effort_path):
            raise WayfinderInitError(
                f"effort already exists: .agent-wayfinder/{effort}"
            )
        effort_path.mkdir()
        effort_created = True
        require_directory(effort_path, "Wayfinder effort")
        with map_path.open("x", encoding="utf-8", newline="\n") as handle:
            map_created = True
            handle.write(rendered)
    except WayfinderInitError:
        remove_created_paths(
            map_path,
            effort_path,
            root,
            map_created=map_created,
            effort_created=effort_created,
            root_created=root_created,
        )
        raise
    except (OSError, UnicodeError) as exc:
        remove_created_paths(
            map_path,
            effort_path,
            root,
            map_created=map_created,
            effort_created=effort_created,
            root_created=root_created,
        )
        raise WayfinderInitError(f"cannot create Wayfinder map: {exc}") from exc
    return map_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser(
        "init-effort", help="create one new Wayfinder effort map"
    )
    init.add_argument("--effort", required=True, help="stable effort storage key")
    init.add_argument("--name", required=True, help="human-readable effort name")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    if sys.version_info < MINIMUM_PYTHON:
        print("ERROR: Agent Workflow requires Python 3.11 or newer", file=sys.stderr)
        return 2
    args = build_parser().parse_args(argv)
    try:
        project, schema = installed_paths()
        if args.command == "init-effort":
            created = init_effort(project, schema, args.effort, args.name)
        else:
            raise WayfinderInitError(f"unsupported operation: {args.command}")
        print(f"CREATED {created.relative_to(project).as_posix()}")
        return 0
    except WayfinderInitError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
