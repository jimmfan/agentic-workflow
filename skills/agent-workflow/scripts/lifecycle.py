#!/usr/bin/env python3
"""Install, update, inspect, or remove Agent Workflow's managed surfaces."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PAYLOAD_ROOT = PACKAGE_ROOT / "payload"
DISTRIBUTION_MANIFEST = PAYLOAD_ROOT / "distribution" / "manifest.json"
FRAMEWORK_ROOT = PurePosixPath(".agent-workflow")
SKILLS_ROOT = PurePosixPath(".agents/skills")
AGENTS_PATH = PurePosixPath("AGENTS.md")
CLAUDE_PATH = PurePosixPath("CLAUDE.md")
COMPOSITE_PATHS = (AGENTS_PATH, CLAUDE_PATH)
MANAGED_BEGIN = b"<!-- agent-workflow:managed-begin -->"
MANAGED_END = b"<!-- agent-workflow:managed-end -->"
FORMER_PROJECT_MARKER = b"<!-- agent-workflow:project-instructions -->"
MARKER_PREFIX = b"<!-- agent-workflow:"
CLAUDE_MANAGED_BEGIN = MANAGED_BEGIN + b"\n"
CLAUDE_MANAGED_END = MANAGED_END + b"\n"
CLAUDE_PROJECT_BEGIN = b"\n" + FORMER_PROJECT_MARKER + b"\n"
DISTRIBUTION_SCHEMA = 7
MINIMUM_PYTHON = (3, 11)


class LifecycleError(RuntimeError):
    """A preflight or package failure that occurs before lifecycle mutation."""


class PartialMutationError(RuntimeError):
    """An ordinary filesystem failure after lifecycle mutation began."""


@dataclass(frozen=True)
class MarkerLine:
    value: bytes
    start: int
    line_end: int
    newline: bytes


@dataclass(frozen=True)
class CompositeParts:
    managed: bytes
    before: bytes
    after: bytes


@dataclass(frozen=True)
class Distribution:
    framework: Mapping[PurePosixPath, bytes]
    skills: Mapping[str, Mapping[PurePosixPath, bytes]]
    composites: Mapping[PurePosixPath, bytes]
    destinations: tuple[PurePosixPath, ...]

    @property
    def skill_names(self) -> tuple[str, ...]:
        return tuple(sorted(self.skills))

    @property
    def managed_surfaces(self) -> tuple[PurePosixPath, ...]:
        return (
            FRAMEWORK_ROOT,
            *(SKILLS_ROOT / name for name in self.skill_names),
            *COMPOSITE_PATHS,
        )


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except (AttributeError, OSError, ValueError):
                pass


def require_supported_python() -> None:
    if sys.version_info < MINIMUM_PYTHON:
        raise LifecycleError("Agent Workflow requires Python 3.11 or newer")


def safe_relative(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise LifecycleError(f"unsafe distribution path: {value!r}")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise LifecycleError(f"unsafe distribution path: {value!r}") from exc
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or path.as_posix() != value
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise LifecycleError(f"unsafe distribution path: {value!r}")
    return path


def load_distribution() -> Distribution:
    if DISTRIBUTION_MANIFEST.is_symlink() or not DISTRIBUTION_MANIFEST.is_file():
        raise LifecycleError(
            f"distribution manifest must be a regular file: {DISTRIBUTION_MANIFEST}"
        )
    try:
        raw = json.loads(DISTRIBUTION_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LifecycleError(f"cannot read distribution manifest: {exc}") from exc
    if not isinstance(raw, dict) or raw.get("schema_version") != DISTRIBUTION_SCHEMA:
        raise LifecycleError("unsupported distribution manifest schema")
    mappings = raw.get("framework_owned")
    if not isinstance(mappings, list):
        raise LifecycleError("distribution manifest needs a framework_owned array")

    framework: dict[PurePosixPath, bytes] = {}
    skills: dict[str, dict[PurePosixPath, bytes]] = {}
    composites: dict[PurePosixPath, bytes] = {}
    destinations: list[PurePosixPath] = []
    sources_seen: set[PurePosixPath] = set()
    targets_seen: set[PurePosixPath] = set()

    for item in mappings:
        if not isinstance(item, dict) or set(item) != {"source", "target"}:
            raise LifecycleError("distribution mappings require only source and target")
        source = safe_relative(item["source"])
        target = safe_relative(item["target"])
        if source in sources_seen or target in targets_seen:
            raise LifecycleError(
                "distribution mappings must have unique sources and targets"
            )
        sources_seen.add(source)
        targets_seen.add(target)

        source_path = PAYLOAD_ROOT.joinpath(*source.parts)
        if source_path.is_symlink() or not source_path.is_file():
            raise LifecycleError(f"payload source is missing or unsafe: {source}")
        try:
            data = source_path.read_bytes()
        except OSError as exc:
            raise LifecycleError(f"cannot read payload source {source}: {exc}") from exc

        if target in COMPOSITE_PATHS:
            expected = PurePosixPath("root") / f"{target.name}.template"
            if source != expected:
                raise LifecycleError(
                    f"invalid composite distribution mapping: {target}"
                )
            composites[target] = data
        elif target.parts[0] == FRAMEWORK_ROOT.as_posix() and len(target.parts) > 1:
            relative = PurePosixPath(*target.parts[1:])
            if source != PurePosixPath("agent-workflow") / relative:
                raise LifecycleError(
                    f"invalid framework distribution mapping: {target}"
                )
            framework[relative] = data
        elif target.parts[:2] == SKILLS_ROOT.parts and len(target.parts) > 3:
            name = target.parts[2]
            relative = PurePosixPath(*target.parts[3:])
            if source != PurePosixPath("skills") / name / relative:
                raise LifecycleError(f"invalid skill distribution mapping: {target}")
            skills.setdefault(name, {})[relative] = data
        else:
            raise LifecycleError(f"unsupported managed destination: {target}")
        destinations.append(target)

    if set(composites) != set(COMPOSITE_PATHS) or not framework or not skills:
        raise LifecycleError(
            "distribution manifest is missing a required managed surface"
        )
    for name, files in skills.items():
        if PurePosixPath("SKILL.md") not in files:
            raise LifecycleError(f"curated skill is missing SKILL.md: {name}")
    return Distribution(framework, skills, composites, tuple(destinations))


def validate_target(raw: Path) -> Path:
    expanded = raw.expanduser().absolute()
    if not expanded.exists() or expanded.is_symlink() or not expanded.is_dir():
        raise LifecycleError(
            f"target must be an existing regular non-symlink directory: {expanded}"
        )
    root = expanded.resolve()
    if root.parent == root:
        raise LifecycleError("refusing to operate on a filesystem root")
    return root


def run_git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
    except OSError as exc:
        raise LifecycleError(f"cannot run Git: {exc}") from exc


def git_boundary_issues(root: Path) -> list[str]:
    top = run_git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return ["target must be exactly a Git worktree root"]
    try:
        git_root = Path(top.stdout.strip()).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        return [f"cannot resolve the Git worktree root: {exc}"]
    if git_root != root:
        return ["target must be the exact Git worktree root"]
    head = run_git(root, "rev-parse", "--verify", "--quiet", "HEAD^{commit}")
    if head.returncode != 0:
        return ["Git worktree must have a valid HEAD commit"]
    return []


def path_exists(path: Path) -> bool:
    return os.path.lexists(path)


def require_path_kind(root: Path, relative: PurePosixPath, final_kind: str) -> None:
    current = root
    for index, part in enumerate(relative.parts):
        current = current / part
        if not path_exists(current):
            return
        try:
            details = os.lstat(current)
        except OSError as exc:
            raise LifecycleError(
                f"cannot inspect managed path {relative}: {exc}"
            ) from exc
        if stat.S_ISLNK(details.st_mode):
            raise LifecycleError(
                f"managed path contains a symlink: {current.relative_to(root)}"
            )
        is_final = index == len(relative.parts) - 1
        if not is_final and not stat.S_ISDIR(details.st_mode):
            raise LifecycleError(
                f"managed path parent is not a directory: {current.relative_to(root)}"
            )
        if is_final:
            expected = stat.S_ISDIR if final_kind == "directory" else stat.S_ISREG
            if not expected(details.st_mode):
                raise LifecycleError(
                    f"managed {final_kind} has an unsupported entry type: {relative}"
                )


def require_managed_roots_safe(root: Path, distribution: Distribution) -> None:
    require_path_kind(root, FRAMEWORK_ROOT, "directory")
    require_path_kind(root, PurePosixPath(".agents"), "directory")
    require_path_kind(root, SKILLS_ROOT, "directory")
    for name in distribution.skill_names:
        require_path_kind(root, SKILLS_ROOT / name, "directory")
    for relative in COMPOSITE_PATHS:
        require_path_kind(root, relative, "file")


def scan_regular_tree(root: Path, relative: PurePosixPath) -> None:
    start = root.joinpath(*relative.parts)
    if not path_exists(start):
        return

    def visit(path: Path, label: PurePosixPath) -> None:
        try:
            details = os.lstat(path)
        except OSError as exc:
            raise LifecycleError(f"cannot inspect managed path {label}: {exc}") from exc
        if stat.S_ISLNK(details.st_mode):
            raise LifecycleError(f"managed tree contains a symlink: {label}")
        if stat.S_ISREG(details.st_mode):
            return
        if not stat.S_ISDIR(details.st_mode):
            raise LifecycleError(f"managed tree contains a special entry: {label}")
        try:
            with os.scandir(path) as iterator:
                entries = sorted(iterator, key=lambda item: item.name)
        except OSError as exc:
            raise LifecycleError(
                f"cannot inspect managed directory {label}: {exc}"
            ) from exc
        for entry in entries:
            visit(Path(entry.path), label / entry.name)

    visit(start, relative)


def reserved_skill_collision(
    root: Path, distribution: Distribution
) -> PurePosixPath | None:
    if adoption_present(root, distribution):
        return None
    for name in distribution.skill_names:
        relative = SKILLS_ROOT / name
        if path_exists(root.joinpath(*relative.parts)):
            return relative
    return None


def reserved_skill_message(relative: PurePosixPath) -> str:
    return (
        f"reserved curated skill directory blocks adoption: {relative}; "
        "move or rename the project-owned skill before installation"
    )


def adoption_collision_message(root: Path, distribution: Distribution) -> str | None:
    collision = reserved_skill_collision(root, distribution)
    if collision is not None:
        return reserved_skill_message(collision)

    if not adoption_present(root, distribution) and path_exists(
        root.joinpath(*FRAMEWORK_ROOT.parts)
    ):
        return (
            "existing .agent-workflow directory blocks adoption; "
            "move or rename the project-owned directory before installation"
        )

    return None


def marker_lines(data: bytes) -> list[MarkerLine]:
    result: list[MarkerLine] = []
    start = 0
    while start < len(data):
        newline = data.find(b"\n", start)
        if newline < 0:
            end = len(data)
            next_start = end
        else:
            end = newline
            next_start = newline + 1
        value = data[start:end]
        line_ending = b"" if newline < 0 else b"\n"
        if newline >= 0 and value.endswith(b"\r"):
            value = value[:-1]
            line_ending = b"\r\n"
        if value.startswith(MARKER_PREFIX):
            result.append(MarkerLine(value, start, next_start, line_ending))
        if newline < 0:
            break
        start = next_start
    return result


def marker_error(
    relative: PurePosixPath, markers: list[MarkerLine], reason: str
) -> LifecycleError:
    managed_begin_count = sum(line.value == MANAGED_BEGIN for line in markers)
    managed_end_count = sum(line.value == MANAGED_END for line in markers)
    former_project_count = sum(line.value == FORMER_PROJECT_MARKER for line in markers)
    counts = (
        f"managed-begin={managed_begin_count}, managed-end={managed_end_count}, "
        f"former-project-instructions={former_project_count}, "
        f"total-agent-workflow={len(markers)}"
    )
    return LifecycleError(
        f"{relative}: managed policy markers are {reason}; "
        f"expected one unambiguous managed-begin/managed-end region; found {counts}"
    )


def is_one_blank_line(data: bytes) -> bool:
    return data in {b"\n", b"\r\n"}


def parse_former_three_marker_layout(
    data: bytes, markers: list[MarkerLine]
) -> CompositeParts | None:
    values = [line.value for line in markers]

    # The exact former standard layout identifies its generated third marker and
    # all project bytes after it without guessing.
    if values == [MANAGED_BEGIN, MANAGED_END, FORMER_PROJECT_MARKER]:
        begin, end, former_project = markers
        if begin.start == 0 and is_one_blank_line(
            data[end.line_end : former_project.start]
        ):
            return CompositeParts(
                data[begin.line_end : end.start],
                b"",
                data[former_project.line_end :],
            )

    # Historical LF-only marker detection could append an outer composite around an
    # existing CRLF composite. This exact nested shape has two generated managed
    # bodies and leaves the original project bytes after the inner former marker.
    historical_duplicate = [
        MANAGED_BEGIN,
        MANAGED_END,
        FORMER_PROJECT_MARKER,
        MANAGED_BEGIN,
        MANAGED_END,
        FORMER_PROJECT_MARKER,
    ]
    if values == historical_duplicate:
        outer_begin, outer_end, outer_project, inner_begin, inner_end, inner_project = (
            markers
        )
        if (
            outer_begin.start == 0
            and all(
                marker.newline == b"\n"
                for marker in (outer_begin, outer_end, outer_project)
            )
            and all(
                marker.newline == b"\r\n"
                for marker in (inner_begin, inner_end, inner_project)
            )
            and data[outer_end.line_end : outer_project.start] == b"\n"
            and outer_project.line_end == inner_begin.start
            and data[inner_end.line_end : inner_project.start] == b"\r\n"
        ):
            return CompositeParts(
                data[outer_begin.line_end : outer_end.start],
                b"",
                data[inner_project.line_end :],
            )

    return None


def parse_agents_composite(
    data: bytes, relative: PurePosixPath
) -> CompositeParts | None:
    markers = marker_lines(data)
    if not markers:
        return None
    known_values = {MANAGED_BEGIN, MANAGED_END, FORMER_PROJECT_MARKER}
    if any(line.value not in known_values for line in markers):
        raise marker_error(relative, markers, "unknown or partial")

    values = [line.value for line in markers]
    if values == [MANAGED_BEGIN, MANAGED_END]:
        begin, end = markers
        return CompositeParts(
            data[begin.line_end : end.start],
            data[: begin.start],
            data[end.line_end :],
        )

    former = parse_former_three_marker_layout(data, markers)
    if former is not None:
        return former

    raise marker_error(relative, markers, "missing, duplicated, or reordered")


def parse_claude_composite(
    data: bytes, relative: PurePosixPath
) -> CompositeParts | None:
    markers = marker_lines(data)
    if not markers:
        return None
    known_values = {MANAGED_BEGIN, MANAGED_END, FORMER_PROJECT_MARKER}
    if any(line.value not in known_values for line in markers):
        raise marker_error(relative, markers, "unknown or partial")
    former = parse_former_three_marker_layout(data, markers)
    if former is None:
        raise marker_error(relative, markers, "missing, duplicated, or reordered")
    return former


def parse_composite(data: bytes, relative: PurePosixPath) -> CompositeParts | None:
    if relative == CLAUDE_PATH:
        return parse_claude_composite(data, relative)
    return parse_agents_composite(data, relative)


def read_composite(root: Path, relative: PurePosixPath) -> bytes | None:
    path = root.joinpath(*relative.parts)
    if not path_exists(path):
        return None
    try:
        return path.read_bytes()
    except OSError as exc:
        raise LifecycleError(f"cannot read composite policy {relative}: {exc}") from exc


def adoption_present(root: Path, distribution: Distribution) -> bool:
    for relative in COMPOSITE_PATHS:
        current = read_composite(root, relative)
        if current is not None:
            parts = parse_composite(current, relative)
            if parts is not None:
                return True
    return directory_matches(root, FRAMEWORK_ROOT, distribution.framework)


def compose_policy(
    relative: PurePosixPath, managed: bytes, before: bytes, after: bytes
) -> bytes:
    if relative == CLAUDE_PATH:
        return (
            CLAUDE_MANAGED_BEGIN
            + managed.rstrip(b"\n")
            + b"\n"
            + CLAUDE_MANAGED_END
            + CLAUDE_PROJECT_BEGIN
            + after
        )
    return (
        before
        + MANAGED_BEGIN
        + b"\n"
        + managed.rstrip(b"\r\n")
        + b"\n"
        + MANAGED_END
        + b"\n"
        + after
    )


def plan_composites(
    root: Path, distribution: Distribution, remove: bool
) -> dict[PurePosixPath, bytes | None]:
    plan: dict[PurePosixPath, bytes | None] = {}
    for relative, managed in distribution.composites.items():
        current = read_composite(root, relative)
        if current is None:
            if not remove:
                plan[relative] = compose_policy(relative, managed, b"", b"")
            continue
        parts = parse_composite(current, relative)
        if parts is not None:
            if remove:
                project = parts.before + parts.after
                plan[relative] = project if project else None
            else:
                plan[relative] = compose_policy(
                    relative, managed, parts.before, parts.after
                )
        elif not remove:
            plan[relative] = compose_policy(relative, managed, b"", current)
    return plan


def inspect_managed_structure(root: Path, distribution: Distribution) -> None:
    require_managed_roots_safe(root, distribution)
    scan_regular_tree(root, FRAMEWORK_ROOT)
    for name in distribution.skill_names:
        scan_regular_tree(root, SKILLS_ROOT / name)
    plan_composites(root, distribution, remove=False)


def split_null_output(value: str) -> list[str]:
    return [item for item in value.split("\0") if item]


def managed_git_issues(root: Path, distribution: Distribution) -> list[str]:
    surfaces = [path.as_posix() for path in distribution.managed_surfaces]
    issues: list[str] = []

    untracked = run_git(
        root,
        "ls-files",
        "-z",
        "--others",
        "--exclude-standard",
        "--",
        *surfaces,
    )
    if untracked.returncode != 0:
        issues.append("Git could not inspect untracked managed files")
    else:
        paths = split_null_output(untracked.stdout)
        if paths:
            issues.append(f"untracked file under a managed surface: {paths[0]}")

    ignored = run_git(
        root,
        "ls-files",
        "-z",
        "--others",
        "--ignored",
        "--exclude-standard",
        "--",
        *surfaces,
    )
    if ignored.returncode != 0:
        issues.append("Git could not inspect ignored managed files")
    else:
        paths = split_null_output(ignored.stdout)
        if paths:
            issues.append(f"managed destination is ignored: {paths[0]}")

    candidates = {
        *distribution.destinations,
        FRAMEWORK_ROOT,
        SKILLS_ROOT,
        *(SKILLS_ROOT / name for name in distribution.skill_names),
        *COMPOSITE_PATHS,
    }
    for relative in sorted(candidates, key=lambda item: item.as_posix()):
        result = run_git(
            root,
            "check-ignore",
            "--no-index",
            "--quiet",
            "--",
            relative.as_posix(),
        )
        if result.returncode == 0:
            issues.append(f"managed destination is ignored: {relative}")
            break
        if result.returncode not in {0, 1}:
            issues.append(f"Git could not inspect ignore rules for {relative}")
            break
    return issues


def worktree_issue(root: Path) -> str | None:
    status_result = run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status_result.returncode != 0:
        return "Git could not inspect worktree cleanliness"
    if not status_result.stdout:
        return None
    if any(line.startswith("??") for line in status_result.stdout.splitlines()):
        return "worktree and index must be completely clean, including untracked files"
    return "worktree and index must be completely clean"


def require_mutation_safe(root: Path, distribution: Distribution) -> None:
    issues = git_boundary_issues(root)
    if issues:
        raise LifecycleError("; ".join(issues))

    inspect_managed_structure(root, distribution)
    issues = managed_git_issues(root, distribution)

    collision = adoption_collision_message(root, distribution)
    if collision is not None:
        issues.append(collision)

    dirty = worktree_issue(root)
    if dirty is not None:
        issues.append(dirty)

    if issues:
        raise LifecycleError("; ".join(dict.fromkeys(issues)))


def expected_directories(files: Mapping[PurePosixPath, bytes]) -> set[PurePosixPath]:
    result: set[PurePosixPath] = set()
    for relative in files:
        for parent in relative.parents:
            if parent != PurePosixPath("."):
                result.add(parent)
    return result


def directory_matches(
    root: Path, relative: PurePosixPath, expected: Mapping[PurePosixPath, bytes]
) -> bool:
    start = root.joinpath(*relative.parts)
    if not path_exists(start) or not start.is_dir():
        return False
    actual_files: dict[PurePosixPath, bytes] = {}
    actual_directories: set[PurePosixPath] = set()

    def visit(path: Path, child: PurePosixPath) -> None:
        with os.scandir(path) as iterator:
            entries = sorted(iterator, key=lambda item: item.name)
        for entry in entries:
            descendant = (
                child / entry.name if child.parts else PurePosixPath(entry.name)
            )
            details = entry.stat(follow_symlinks=False)
            if stat.S_ISDIR(details.st_mode):
                actual_directories.add(descendant)
                visit(Path(entry.path), descendant)
            elif stat.S_ISREG(details.st_mode):
                actual_files[descendant] = Path(entry.path).read_bytes()
            else:
                return

    visit(start, PurePosixPath())
    return actual_files == dict(
        expected
    ) and actual_directories == expected_directories(expected)


def drift_messages(root: Path, distribution: Distribution) -> list[str]:
    messages: list[str] = []
    if not directory_matches(root, FRAMEWORK_ROOT, distribution.framework):
        messages.append("REPAIR: managed directory differs: .agent-workflow")
    for name, files in sorted(distribution.skills.items()):
        relative = SKILLS_ROOT / name
        if not directory_matches(root, relative, files):
            messages.append(f"REPAIR: managed skill directory differs: {relative}")
    for relative, desired in distribution.composites.items():
        current = read_composite(root, relative)
        if current is None:
            messages.append(f"REPAIR: managed policy region differs: {relative}")
            continue
        parts = parse_composite(current, relative)
        if parts is None or current != compose_policy(
            relative, desired, parts.before, parts.after
        ):
            messages.append(f"REPAIR: managed policy region differs: {relative}")
    return messages


def status(root: Path, distribution: Distribution) -> int:
    print(f"STATUS {root}")
    boundary = git_boundary_issues(root)
    structural: list[str] = []
    drift: list[str] = []

    try:
        require_managed_roots_safe(root, distribution)
        scan_regular_tree(root, FRAMEWORK_ROOT)
        for name in distribution.skill_names:
            scan_regular_tree(root, SKILLS_ROOT / name)
        plan_composites(root, distribution, remove=False)

        collision = adoption_collision_message(root, distribution)
        if collision is not None:
            structural.append(collision)
        else:
            drift = drift_messages(root, distribution)
    except (LifecycleError, OSError) as exc:
        structural.append(str(exc))

    safety = list(boundary)
    if not boundary:
        safety.extend(managed_git_issues(root, distribution))
        dirty = worktree_issue(root)
        if dirty is not None:
            safety.append(dirty)

    for issue in dict.fromkeys(safety):
        print(f"BLOCKED: Git safety boundary would block mutation: {issue}")
    for issue in structural:
        print(f"CONFLICT: {issue}")
    for message in drift:
        print(message)

    if safety or structural or drift:
        if structural:
            print("Agent Workflow: unsafe/conflict")
        elif safety:
            print("Agent Workflow: blocked by Git safety boundary")
        else:
            print("Agent Workflow: repairable")
        return 1
    print("Agent Workflow: healthy")
    print("OK: No lifecycle action is required.")
    return 0


def ensure_parent_directories(path: Path, root: Path) -> None:
    missing: list[Path] = []
    current = path.parent
    while current != root and not path_exists(current):
        missing.append(current)
        current = current.parent
    if current != root:
        details = os.lstat(current)
        if stat.S_ISLNK(details.st_mode) or not stat.S_ISDIR(details.st_mode):
            raise OSError(
                f"unsafe parent for managed write: {current.relative_to(root)}"
            )
    for directory in reversed(missing):
        directory.mkdir(mode=0o755)


def atomic_write(path: Path, data: bytes, root: Path, mode: int = 0o644) -> None:
    ensure_parent_directories(path, root)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    finally:
        if path_exists(temporary_path):
            temporary_path.unlink()


def replace_directory(
    root: Path, relative: PurePosixPath, files: Mapping[PurePosixPath, bytes]
) -> None:
    target = root.joinpath(*relative.parts)
    if path_exists(target):
        shutil.rmtree(target)
    target.mkdir(parents=True, mode=0o755)
    for child, data in sorted(files.items(), key=lambda item: item[0].as_posix()):
        atomic_write(target.joinpath(*child.parts), data, root)


def apply_composites(root: Path, plan: Mapping[PurePosixPath, bytes | None]) -> None:
    for relative, desired in sorted(plan.items(), key=lambda item: item[0].as_posix()):
        target = root.joinpath(*relative.parts)
        if desired is None:
            if path_exists(target):
                target.unlink()
            continue
        mode = 0o644
        if path_exists(target):
            mode = stat.S_IMODE(os.lstat(target).st_mode)
        atomic_write(target, desired, root, mode)


def print_plan(command: str, root: Path, distribution: Distribution) -> None:
    print(f"{command.upper()} PLAN {root}")
    if command == "remove":
        print("- remove .agent-workflow/")
        for name in distribution.skill_names:
            print(f"- remove .agents/skills/{name}/")
        print("- remove managed regions from AGENTS.md and CLAUDE.md")
    else:
        print("- replace .agent-workflow/ with current package bytes")
        for name in distribution.skill_names:
            print(f"- replace .agents/skills/{name}/ with current package bytes")
        print("- converge managed regions in AGENTS.md and CLAUDE.md")


def converge(
    root: Path, distribution: Distribution, command: str, dry_run: bool
) -> None:
    require_mutation_safe(root, distribution)
    composite_plan = plan_composites(root, distribution, remove=False)
    if dry_run:
        print_plan(command, root, distribution)
        return
    try:
        replace_directory(root, FRAMEWORK_ROOT, distribution.framework)
        for name, files in sorted(distribution.skills.items()):
            replace_directory(root, SKILLS_ROOT / name, files)
        apply_composites(root, composite_plan)
    except (LifecycleError, OSError) as exc:
        raise PartialMutationError(str(exc)) from exc
    print(f"OK: Agent Workflow {command} completed.")


def remove(root: Path, distribution: Distribution, dry_run: bool) -> None:
    require_mutation_safe(root, distribution)
    composite_plan = plan_composites(root, distribution, remove=True)
    if dry_run:
        print_plan("remove", root, distribution)
        return
    try:
        framework = root.joinpath(*FRAMEWORK_ROOT.parts)
        if path_exists(framework):
            shutil.rmtree(framework)
        for name in distribution.skill_names:
            skill = root.joinpath(*(SKILLS_ROOT / name).parts)
            if path_exists(skill):
                shutil.rmtree(skill)
        apply_composites(root, composite_plan)
    except (LifecycleError, OSError) as exc:
        raise PartialMutationError(str(exc)) from exc
    print("OK: Agent Workflow managed surfaces removed.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install", "update", "status", "remove"))
    parser.add_argument("target", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    configure_console()
    try:
        require_supported_python()
        args = build_parser().parse_args(argv)
        if args.command == "status" and args.dry_run:
            raise LifecycleError("status does not accept --dry-run")
        root = validate_target(args.target)
        distribution = load_distribution()
        if args.command == "status":
            return status(root, distribution)
        if args.command == "remove":
            remove(root, distribution, args.dry_run)
        else:
            converge(root, distribution, args.command, args.dry_run)
        return 0
    except PartialMutationError as exc:
        print(
            "ERROR: lifecycle operation failed; partial changes may exist. "
            "Inspect git status, restore with Git, and retry from a clean worktree: "
            f"{exc}",
            file=sys.stderr,
        )
        return 2
    except LifecycleError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(
            f"ERROR: filesystem operation failed before mutation: {exc}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
