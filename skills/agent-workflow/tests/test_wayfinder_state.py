from __future__ import annotations

from pathlib import Path
import re
import shutil
import tempfile
import tomllib
from typing import Callable
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
CONTRACT = PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md"
INSTALLED_CONTRACT = REPOSITORY_ROOT / ".agent-workflow/contracts/wayfinder-state.md"
RUNTIME = PACKAGE_ROOT / "runtime-projections/wayfinder.md"
GENERATED_SKILL = REPOSITORY_ROOT / ".agents/skills/wayfinder/SKILL.md"
MAP_FIRST_ADR = REPOSITORY_ROOT / "architecture-decisions/0011-use-map-first-wayfinder-state.md"
CURRENT_WAYFINDER_DOC_SECTIONS = {
    "Agent Workflow README contents": (
        REPOSITORY_ROOT / ".agent-workflow/README.md",
        "## Contents",
    ),
    "packaged Agent Workflow README contents": (
        PACKAGE_ROOT / "payload/agent-workflow/README.md",
        "## Contents",
    ),
    "filesystem ownership": (
        REPOSITORY_ROOT / "docs/architecture.md",
        "## Filesystem ownership",
    ),
    "behavioral testing layers": (
        REPOSITORY_ROOT / "docs/behavioral-testing.md",
        "## Testing layers",
    ),
    "behavioral scenario format": (
        REPOSITORY_ROOT / "docs/behavioral-testing.md",
        "## Human-authored scenario format",
    ),
    "verification acceptance boundary": (
        REPOSITORY_ROOT / "docs/verification.md",
        "## Acceptance boundary",
    ),
    "Wayfinder behavior tests": (
        PACKAGE_ROOT / "tests/README.md",
        "## Behavior harness and Wayfinder behavior",
    ),
    "human behavioral contracts": (
        PACKAGE_ROOT / "tests/README.md",
        "## Human behavioral contracts and live smoke tests",
    ),
    "map-first ADR consequences": (
        MAP_FIRST_ADR,
        "## Consequences",
    ),
}
CURRENT_WAYFINDER_SCENARIOS = {
    "answered authority question": (
        PACKAGE_ROOT
        / "tests/scenarios/wayfinder-answered-unknown-authority-choice.toml"
    ),
    "whole-effort ending": (
        PACKAGE_ROOT
        / "tests/scenarios/wayfinder-answered-unknown-settlement.toml"
    ),
    "unsupported fact": (
        PACKAGE_ROOT / "tests/scenarios/wayfinder-fact-conflict.toml"
    ),
}
CURRENT_WAYFINDER_LANGUAGE_SURFACES = {
    "packaged contract": CONTRACT,
    "installed contract": INSTALLED_CONTRACT,
    "runtime projection": RUNTIME,
    "installed routing policy": REPOSITORY_ROOT / ".agent-workflow/routing.md",
    "packaged routing policy": PACKAGE_ROOT / "payload/agent-workflow/routing.md",
    "distributed root policy": PACKAGE_ROOT / "payload/root/AGENTS.md.template",
    "installed implementation workflow": (
        REPOSITORY_ROOT / ".agents/skills/workflow-implementation/SKILL.md"
    ),
    "packaged implementation workflow": (
        PACKAGE_ROOT / "payload/skills/workflow-implementation/SKILL.md"
    ),
}
RETIRED_CANONICAL_WAYFINDER_PATTERNS = (
    r"(?im)^##\s+Establish territory\s*$",
    r"(?im)^##\s+Resolve the frontier progressively\s*$",
    r"(?im)^-\s+\*\*(?:Destination|Territory|Ready frontier)\*\*",
    r"\bthe ready frontier\s+(?:is|contains|owns)\b",
    r"\blow-resolution\s+(?:map|maps|view|semantic)\b",
    r"\b(?:map(?:\.md)?|effort map)\b[^.\n]{0,80}\bre-entry point\b",
    r"\bre-entry point\b[^.\n]{0,80}\b(?:map(?:\.md)?|effort map)\b",
    r"\b(?:establish|same|stable)\s+(?:the\s+)?destination\b",
    r"\bderive\b[^.\n]{0,40}\bfrom\s+(?:the\s+)?destination\b",
    r"\bdestination\s+(?:and|or)\s+(?:scope|boundary)\b",
    r"\b(?:ordinary|research|debugging)\s+fog\b",
    r"\b(?:resolve|frame|reconcile|return|native|current|ready|coherent)\s+(?:the\s+)?frontier\b",
    r"\bfrontier\s+(?:can|may|is|work|state)\b",
)
FIXTURES = PACKAGE_ROOT / "tests/fixtures"
TYPE_DIRECTORIES = {"U": "unknowns", "E": "evidence", "F": "facts", "D": "decisions"}
LEDGER_PATHS = {"F": "facts.md", "D": "decisions.md"}
LEDGER_TITLES = {"F": "Facts", "D": "Decisions"}
CURRENT_ID = re.compile(r"^([UEFD])([1-9][0-9]*)-([^.]+)\.md$")
LEDGER_HEADING = re.compile(r"^## ([FD])([1-9][0-9]*) — (\S.*)$")


class UnsafeWayfinderState(RuntimeError):
    pass


def markdown_section(text: str, heading: str) -> str:
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start:] if end < 0 else text[start:end]


def validate_effort_location(effort: Path, *, require_root: bool = False) -> None:
    if ".agent-wayfinder" not in effort.parts:
        if effort.is_symlink():
            raise UnsafeWayfinderState("effort path crosses a symlink")
        if require_root:
            raise UnsafeWayfinderState("effort path is not below Wayfinder root")
        return
    cursor = effort
    found_root = False
    while True:
        if cursor.is_symlink():
            raise UnsafeWayfinderState("effort path crosses a symlink")
        if cursor.name == ".agent-wayfinder":
            if cursor.parent.is_symlink():
                raise UnsafeWayfinderState("effort path crosses a symlink")
            found_root = True
            break
        parent = cursor.parent
        if parent == cursor:
            break
        cursor = parent
    if require_root and not found_root:
        raise UnsafeWayfinderState("effort path is not below Wayfinder root")


def validate_effort(effort: Path) -> bool:
    validate_effort_location(effort)
    map_path = effort / "map.md"
    if map_path.is_symlink() or not map_path.is_file():
        raise UnsafeWayfinderState("effort has no safe map")
    return True


def exact_effort(repository: Path, relative: Path) -> Path:
    if (
        relative.is_absolute()
        or len(relative.parts) < 2
        or relative.parts[0] != ".agent-wayfinder"
    ):
        raise UnsafeWayfinderState("effort path is not below Wayfinder root")
    if repository.is_symlink():
        raise UnsafeWayfinderState("effort path crosses a symlink")
    if not repository.is_dir():
        raise UnsafeWayfinderState("unsafe repository root")
    cursor = repository
    for part in relative.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            raise UnsafeWayfinderState("effort path is not below Wayfinder root")
        cursor = cursor / part
        if cursor.is_symlink():
            raise UnsafeWayfinderState("effort path crosses a symlink")
    validate_effort(cursor)
    return cursor


def select_effort(candidates: list[Path], objective: str, scope: str) -> Path | None:
    matches: list[Path] = []
    for effort in candidates:
        map_path = effort / "map.md"
        if not map_path.exists() and not map_path.is_symlink():
            continue
        validate_effort(effort)
        map_text = map_path.read_text(encoding="utf-8").casefold()
        if objective.casefold() in map_text and scope.casefold() in map_text:
            matches.append(effort)
    if len(matches) > 1:
        raise UnsafeWayfinderState("ambiguous effort selection")
    return matches[0] if matches else None


def parse_ledger_sections(text: str, kind: str) -> list[tuple[int, str, str]]:
    lines = text.splitlines(keepends=True)
    starts: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        match = LEDGER_HEADING.fullmatch(line.rstrip("\r\n"))
        if match is None or match.group(1) != kind:
            raise UnsafeWayfinderState(f"malformed current {kind} identifier")
        starts.append((index, int(match.group(2)), match.group(3)))
    identifiers = [identifier for _, identifier, _ in starts]
    if len(identifiers) != len(set(identifiers)):
        raise UnsafeWayfinderState(f"duplicate current {kind} identifier")
    sections: list[tuple[int, str, str]] = []
    for position, (start, identifier, title) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        sections.append((identifier, title, "".join(lines[start:end])))
    return sections


def ledger_sections(effort: Path, kind: str) -> list[tuple[int, str, str]]:
    path = effort / LEDGER_PATHS[kind]
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        raise UnsafeWayfinderState(f"unsafe {kind} ledger")
    return parse_ledger_sections(path.read_text(encoding="utf-8"), kind)


def without_ledger_sections(
    original: str,
    sections: list[tuple[int, str, str]],
    identifiers: set[int],
) -> str:
    updated = original
    for identifier, _title, section in sections:
        if identifier in identifiers:
            updated = updated.replace(section, "", 1)
    return updated


def read_current_ids(effort: Path, kind: str) -> list[int]:
    if kind in LEDGER_PATHS:
        return [item[0] for item in ledger_sections(effort, kind)]
    return sorted(current_ids(effort, kind))


def readable_slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def create_current_record(
    effort: Path,
    kind: str,
    title: str,
    body: str,
    *,
    before_create: Callable[[], None] | None = None,
    before_final_write: Callable[[], None] | None = None,
) -> str:
    if kind not in TYPE_DIRECTORIES:
        raise UnsafeWayfinderState("unknown Wayfinder record type")
    if kind in ("U", "E"):
        path = create_current_child(
            effort,
            kind,
            readable_slug(title),
            body,
            before_create=before_create,
        )
        return path.name.split("-", 1)[0]
    path = effort / LEDGER_PATHS[kind]
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise UnsafeWayfinderState(f"unsafe {kind} ledger")
    observed = path.read_bytes() if path.exists() else None
    existing = observed.decode("utf-8") if observed is not None else ""
    sections = parse_ledger_sections(existing, kind)
    identifier = max((item[0] for item in sections), default=0) + 1
    if before_final_write is not None:
        before_final_write()
    current = path.read_bytes() if path.exists() else None
    if current != observed:
        raise UnsafeWayfinderState("ledger changed before write")
    prefix = existing.rstrip() if existing else f"# {LEDGER_TITLES[kind]}"
    content = (
        f"{prefix}\n\n## {kind}{identifier} — {title}\n\n"
        f"{body.rstrip()}\n"
    )
    if observed is None:
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except FileExistsError as error:
            raise UnsafeWayfinderState("ledger changed before write") from error
    else:
        path.write_text(content, encoding="utf-8")
    return f"{kind}{identifier}"


def heading_anchor(kind: str, identifier: int, title: str) -> str:
    heading = f"{kind}{identifier} — {title}".lower()
    without_punctuation = "".join(
        character
        for character in heading
        if character.isalnum() or character in {" ", "-"}
    )
    return without_punctuation.replace(" ", "-")


def ledger_references(
    effort: Path,
    kind: str,
    identifier: int,
    title: str,
    ledger_without_target: str,
    known_references: list[Path] | None = None,
) -> list[Path]:
    token = re.compile(rf"(?<![A-Z0-9]){kind}{identifier}(?![0-9])")
    ledger_name = LEDGER_PATHS[kind]
    anchor = heading_anchor(kind, identifier, title)
    references: list[Path] = []
    paths = list(current_markdown(effort))
    paths.extend(known_references or [])
    for path in dict.fromkeys(paths):
        if path.is_symlink() or not path.is_file():
            raise UnsafeWayfinderState(f"unsafe reference path: {path}")
        text = (
            ledger_without_target
            if path == effort / ledger_name
            else path.read_text(encoding="utf-8")
        )
        if token.search(text) or f"{ledger_name}#{anchor}" in text:
            references.append(path)
    return references


def prune_ledger_section(
    effort: Path,
    kind: str,
    identifier: int,
    *,
    known_references: list[Path] | None = None,
) -> bool:
    path = effort / LEDGER_PATHS[kind]
    if not path.exists():
        return False
    if path.is_symlink() or not path.is_file():
        raise UnsafeWayfinderState(f"unsafe {kind} ledger")
    original_bytes = path.read_bytes()
    original = original_bytes.decode("utf-8")
    sections = parse_ledger_sections(original, kind)
    matches = [item for item in sections if item[0] == identifier]
    if not matches:
        return False
    _, title, section = matches[0]
    updated = without_ledger_sections(original, sections, {identifier})
    if ledger_references(
        effort,
        kind,
        identifier,
        title,
        updated,
        known_references,
    ):
        raise UnsafeWayfinderState("current references remain")
    observed_current = current_markdown(effort)
    if observed_current.get(path) != original_bytes:
        raise UnsafeWayfinderState("current state changed during reconciliation")
    observed_known = {
        reference: reference.read_bytes()
        for reference in known_references or []
        if not reference.is_relative_to(effort)
    }
    if current_markdown(effort) != observed_current:
        raise UnsafeWayfinderState("current state changed during reconciliation")
    if any(
        not reference.is_file() or reference.read_bytes() != observed
        for reference, observed in observed_known.items()
    ):
        raise UnsafeWayfinderState("known reference changed during reconciliation")
    if ledger_references(
        effort,
        kind,
        identifier,
        title,
        updated,
        known_references,
    ):
        raise UnsafeWayfinderState("current references appeared during reconciliation")
    if updated.strip() in {"", f"# {LEDGER_TITLES[kind]}"}:
        path.unlink()
    else:
        path.write_text(updated, encoding="utf-8")
    return True


def update_ledger_section(
    effort: Path,
    kind: str,
    identifier: int,
    body: str,
) -> None:
    path = effort / LEDGER_PATHS[kind]
    if path.is_symlink() or not path.is_file():
        raise UnsafeWayfinderState(f"unsafe {kind} ledger")
    original_bytes = path.read_bytes()
    original = original_bytes.decode("utf-8")
    matches = [
        item for item in parse_ledger_sections(original, kind) if item[0] == identifier
    ]
    if len(matches) != 1:
        raise UnsafeWayfinderState("ledger section is not current and unique")
    _, title, section = matches[0]
    replacement = f"## {kind}{identifier} — {title}\n\n{body.rstrip()}\n"
    updated = original.replace(section, replacement, 1)
    if path.read_bytes() != original_bytes:
        raise UnsafeWayfinderState("current state changed during reconciliation")
    path.write_text(updated, encoding="utf-8")


def replace_map(
    effort: Path,
    expected: bytes,
    updated: bytes,
) -> None:
    path = effort / "map.md"
    if path.is_symlink() or not path.is_file() or path.read_bytes() != expected:
        raise UnsafeWayfinderState("map changed before write")
    path.write_bytes(updated)


def current_child_paths(
    effort: Path,
    kind: str,
    *,
    strict: bool = False,
) -> list[Path]:
    directory = effort / TYPE_DIRECTORIES[kind]
    if not directory.exists():
        return []
    if directory.is_symlink() or not directory.is_dir():
        raise UnsafeWayfinderState(f"unsafe {kind} directory")

    result: list[Path] = []
    identifiers: list[int] = []
    for child in directory.iterdir():
        match = CURRENT_ID.fullmatch(child.name)
        identity_like = re.match(r"^[UE][0-9]", child.name) is not None
        if child.is_symlink() or not child.is_file():
            if strict and identity_like:
                raise UnsafeWayfinderState(f"unsafe child path: {child.name}")
            continue
        if match is None or match.group(1) != kind:
            if strict and identity_like:
                raise UnsafeWayfinderState(
                    f"unrecognized child filename: {child.name}"
                )
            continue
        result.append(child)
        identifiers.append(int(match.group(2)))
    if strict and len(identifiers) != len(set(identifiers)):
        raise UnsafeWayfinderState(f"duplicate current {kind} identifier")
    return sorted(result)


def current_ids(effort: Path, kind: str) -> list[int]:
    return [
        int(CURRENT_ID.fullmatch(path.name).group(2))
        for path in current_child_paths(effort, kind, strict=True)
    ]


def next_current_id(effort: Path, kind: str) -> int:
    ids = current_ids(effort, kind)
    return max(ids, default=0) + 1


def create_current_child(
    effort: Path,
    kind: str,
    slug: str,
    body: str,
    before_create: Callable[[], None] | None = None,
    before_exclusive_create: Callable[[], None] | None = None,
) -> Path:
    if kind not in {"U", "E"}:
        raise UnsafeWayfinderState("F/D records belong in their current ledgers")
    directory = effort / TYPE_DIRECTORIES[kind]
    directory.mkdir(parents=True, exist_ok=True)
    candidate = next_current_id(effort, kind)
    path = directory / f"{kind}{candidate}-{slug}.md"
    if before_create is not None:
        before_create()
    if next_current_id(effort, kind) != candidate:
        raise UnsafeWayfinderState("current child identifiers changed before create")
    if before_exclusive_create is not None:
        before_exclusive_create()
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(body)
    except FileExistsError as error:
        raise UnsafeWayfinderState("current child already exists") from error
    return path


def current_markdown(
    effort: Path, *, excluding: Path | None = None
) -> dict[Path, bytes]:
    result: dict[Path, bytes] = {}
    paths = [effort / "map.md", effort / "facts.md", effort / "decisions.md"]
    paths.extend(current_child_paths(effort, "U"))
    paths.extend(current_child_paths(effort, "E"))
    for path in paths:
        if path == excluding:
            continue
        if not path.exists() and not path.is_symlink():
            continue
        if path.is_symlink() or not path.is_file():
            raise UnsafeWayfinderState(f"unsafe reference path: {path}")
        result[path] = path.read_bytes()
    return result


def references_to(
    effort: Path,
    target: Path,
    known_references: list[Path] | None = None,
) -> list[Path]:
    match = CURRENT_ID.fullmatch(target.name)
    if match is None:
        raise UnsafeWayfinderState("pruning path has no canonical current ID")
    identifier = f"{match.group(1)}{match.group(2)}"
    token = re.compile(rf"(?<![A-Z0-9]){re.escape(identifier)}(?![0-9])")
    relative_path = target.relative_to(effort).as_posix()
    references: list[Path] = []
    current = current_markdown(effort, excluding=target)
    for path in known_references or []:
        if path.is_symlink() or not path.is_file():
            raise UnsafeWayfinderState(f"unsafe reference path: {path}")
        current[path] = path.read_bytes()
    for path, content in current.items():
        text = content.decode("utf-8")
        if token.search(text) or target.name in text or relative_path in text:
            references.append(path)
    return references


def ledger_anchor_references(
    effort: Path,
    kind: str,
    identifier: int,
    title: str,
    known_references: list[Path] | None = None,
) -> list[Path]:
    fragment = f"{LEDGER_PATHS[kind]}#{heading_anchor(kind, identifier, title)}"
    paths = current_markdown(effort)
    for path in known_references or []:
        if path.is_symlink() or not path.is_file():
            raise UnsafeWayfinderState(f"unsafe reference path: {path}")
        paths[path] = path.read_bytes()
    return [
        path
        for path, content in paths.items()
        if fragment in content.decode("utf-8")
    ]


def rename_ledger_heading(
    effort: Path,
    kind: str,
    identifier: int,
    title: str,
    *,
    known_references: list[Path] | None = None,
) -> str:
    if kind not in LEDGER_PATHS:
        raise UnsafeWayfinderState("only F/D records have ledger headings")
    path = effort / LEDGER_PATHS[kind]
    if path.is_symlink() or not path.is_file():
        raise UnsafeWayfinderState(f"unsafe {kind} ledger")
    original_bytes = path.read_bytes()
    original = original_bytes.decode("utf-8")
    matches = [
        item for item in parse_ledger_sections(original, kind) if item[0] == identifier
    ]
    if len(matches) != 1:
        raise UnsafeWayfinderState("ledger heading is not current and unique")
    _, old_title, section = matches[0]
    if ledger_anchor_references(
        effort, kind, identifier, old_title, known_references
    ):
        raise UnsafeWayfinderState("current anchor references remain")
    old_heading = f"## {kind}{identifier} — {old_title}"
    new_heading = f"## {kind}{identifier} — {title}"
    updated = original.replace(
        section,
        section.replace(old_heading, new_heading, 1),
        1,
    )
    observed_current = current_markdown(effort)
    if observed_current.get(path) != original_bytes:
        raise UnsafeWayfinderState("current state changed during reconciliation")
    observed_known = {
        reference: reference.read_bytes()
        for reference in known_references or []
    }
    if current_markdown(effort) != observed_current:
        raise UnsafeWayfinderState("current state changed during reconciliation")
    if any(
        not reference.is_file() or reference.read_bytes() != observed
        for reference, observed in observed_known.items()
    ):
        raise UnsafeWayfinderState("known reference changed during reconciliation")
    if ledger_anchor_references(
        effort, kind, identifier, old_title, known_references
    ):
        raise UnsafeWayfinderState("current anchor references appeared")
    path.write_text(updated, encoding="utf-8")
    return heading_anchor(kind, identifier, title)


def rename_current_child(
    effort: Path,
    target: Path,
    slug: str,
    *,
    known_references: list[Path] | None = None,
) -> Path:
    match = CURRENT_ID.fullmatch(target.name)
    if match is None or match.group(1) not in {"U", "E"}:
        raise UnsafeWayfinderState("renaming path has no canonical current ID")
    if readable_slug(slug) != slug or not slug:
        raise UnsafeWayfinderState("rename requires a readable slug")
    current_child_paths(effort, match.group(1), strict=True)
    if not target.is_file() or target.is_symlink():
        raise UnsafeWayfinderState("unsafe rename target")
    if references_to(effort, target, known_references):
        raise UnsafeWayfinderState("current references remain")
    observed_target = target.read_bytes()
    observed_current = current_markdown(effort, excluding=target)
    observed_known = {
        reference: reference.read_bytes()
        for reference in known_references or []
    }
    renamed = target.with_name(f"{match.group(1)}{match.group(2)}-{slug}.md")
    if renamed.exists() or renamed.is_symlink():
        raise UnsafeWayfinderState("rename target already exists")
    if target.read_bytes() != observed_target:
        raise UnsafeWayfinderState("rename target changed")
    if current_markdown(effort, excluding=target) != observed_current:
        raise UnsafeWayfinderState("current state changed during reconciliation")
    if any(
        not reference.is_file() or reference.read_bytes() != observed
        for reference, observed in observed_known.items()
    ):
        raise UnsafeWayfinderState("known reference changed during reconciliation")
    if references_to(effort, target, known_references):
        raise UnsafeWayfinderState("current references appeared during reconciliation")
    target.rename(renamed)
    return renamed


def prune_current_child(
    effort: Path,
    target: Path,
    *,
    known_references: list[Path] | None = None,
    before_final_check: Callable[[], None] | None = None,
) -> bool:
    match = CURRENT_ID.fullmatch(target.name)
    if match is not None and match.group(1) in LEDGER_PATHS:
        raise UnsafeWayfinderState("F/D records belong in their current ledgers")
    if match is None or match.group(1) not in {"U", "E"}:
        raise UnsafeWayfinderState("pruning path has no canonical current ID")
    current_child_paths(effort, match.group(1), strict=True)
    if not target.exists():
        return False
    references = references_to(effort, target, known_references)
    if references:
        raise UnsafeWayfinderState(f"current references remain: {references}")

    observed_target = target.read_bytes()
    observed_current = current_markdown(effort, excluding=target)
    observed_known = {
        reference: reference.read_bytes()
        for reference in known_references or []
    }
    if before_final_check is not None:
        before_final_check()
    if not target.exists() or target.read_bytes() != observed_target:
        raise UnsafeWayfinderState("pruning child changed during reconciliation")
    if current_markdown(effort, excluding=target) != observed_current:
        raise UnsafeWayfinderState("current state changed during reconciliation")
    if any(
        not reference.is_file() or reference.read_bytes() != observed
        for reference, observed in observed_known.items()
    ):
        raise UnsafeWayfinderState("known reference changed during reconciliation")
    if references_to(effort, target, known_references):
        raise UnsafeWayfinderState(
            "current references appeared during reconciliation"
        )

    target.unlink()
    parent = target.parent
    if not any(parent.iterdir()):
        parent.rmdir()
    return True


def end_effort_state(
    effort: Path,
    *,
    known_references: list[Path] | None = None,
    continuity_owners: list[Path] | None = None,
    before_final_check: Callable[[], None] | None = None,
    before_map_removal: Callable[[], None] | None = None,
) -> None:
    validate_effort_location(effort, require_root=True)
    validate_effort(effort)
    reference_paths = list(
        dict.fromkeys([*(known_references or []), *(continuity_owners or [])])
    )
    for reference in reference_paths:
        if reference.is_symlink() or not reference.is_file():
            raise UnsafeWayfinderState(f"unsafe reference path: {reference}")
    if any(owner.is_relative_to(effort) for owner in continuity_owners or []):
        raise UnsafeWayfinderState("continuity owner must outlive the effort")
    validate_effort_location(effort, require_root=True)
    validate_effort(effort)
    for kind in ("U", "E"):
        current_child_paths(effort, kind, strict=True)
    observed_current = current_markdown(effort)
    observed_known = {
        reference: reference.read_bytes() for reference in reference_paths
    }
    unresolved = [
        path.name.split("-", 1)[0]
        for path in current_child_paths(effort, "U", strict=True)
    ]
    owner_text = "\n".join(
        owner.read_text(encoding="utf-8") for owner in continuity_owners or []
    )
    if any(
        re.search(rf"(?<![A-Z0-9]){re.escape(identifier)}(?![0-9])", owner_text)
        is None
        for identifier in unresolved
    ):
        raise UnsafeWayfinderState(
            "unresolved coordination lacks an observable continuity owner"
        )
    root_index = max(
        index
        for index, part in enumerate(effort.parts)
        if part == ".agent-wayfinder"
    )
    effort_relative = Path(*effort.parts[root_index:])
    target_links = {
        (effort_relative / path.relative_to(effort)).as_posix()
        for path in observed_current
    }
    for reference, content in observed_known.items():
        text = content.decode("utf-8")
        if any(target in text for target in target_links):
            raise UnsafeWayfinderState("current references remain")

    ledger_updates: dict[Path, bytes | None] = {}
    for kind, name in LEDGER_PATHS.items():
        path = effort / name
        if path not in observed_current:
            continue
        original = observed_current[path].decode("utf-8")
        sections = ledger_sections(effort, kind)
        updated = without_ledger_sections(
            original,
            sections,
            {identifier for identifier, _title, _section in sections},
        )
        for identifier, title, _section in sections:
            token = re.compile(rf"(?<![A-Z0-9]){kind}{identifier}(?![0-9])")
            anchor = f"{name}#{heading_anchor(kind, identifier, title)}"
            if token.search(updated) or anchor in updated:
                raise UnsafeWayfinderState("unknown ledger content references a record")
        ledger_updates[path] = (
            None
            if updated.strip() in {"", f"# {LEDGER_TITLES[kind]}"}
            else updated.encode("utf-8")
        )

    if before_final_check is not None:
        before_final_check()
    validate_effort_location(effort, require_root=True)
    for kind in ("U", "E"):
        current_child_paths(effort, kind, strict=True)
    if current_markdown(effort) != observed_current:
        raise UnsafeWayfinderState("current state changed during reconciliation")
    if any(
        not reference.is_file() or reference.read_bytes() != observed
        for reference, observed in observed_known.items()
    ):
        raise UnsafeWayfinderState("known reference changed during reconciliation")

    map_path = effort / "map.md"
    for path in observed_current:
        if path == map_path or path in ledger_updates:
            continue
        path.unlink()
    for path, content in ledger_updates.items():
        if content is None:
            path.unlink()
        else:
            path.write_bytes(content)
    for directory_name in ("unknowns", "evidence"):
        directory = effort / directory_name
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    if before_map_removal is not None:
        before_map_removal()
    map_path.unlink()


class WayfinderStateContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = CONTRACT.read_text(encoding="utf-8")
        self.normalized = " ".join(self.contract.split())

    def test_exact_effort_path_stays_below_root_and_crosses_no_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            root = project / ".agent-wayfinder"
            effort = root / "release-direction"
            effort.mkdir(parents=True)
            (effort / "map.md").write_text("# Release direction\n", encoding="utf-8")

            self.assertEqual(
                exact_effort(project, Path(".agent-wayfinder/release-direction")),
                effort,
            )
            outside = project / "outside"
            outside.mkdir()
            (outside / "map.md").write_text("# Outside\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "below Wayfinder root"):
                exact_effort(project, Path("outside"))

            target = root / "target"
            target.mkdir()
            (target / "map.md").write_text("# Target\n", encoding="utf-8")
            (root / "linked").symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(UnsafeWayfinderState, "symlink"):
                exact_effort(project, Path(".agent-wayfinder/linked"))

            linked_project = Path(temporary) / "linked-project"
            linked_project.symlink_to(project, target_is_directory=True)
            with self.assertRaisesRegex(UnsafeWayfinderState, "symlink"):
                exact_effort(
                    linked_project,
                    Path(".agent-wayfinder/release-direction"),
                )

            map_target = project / "map-target.md"
            map_target.write_text("# Symlink target\n", encoding="utf-8")
            map_link_effort = root / "map-link"
            map_link_effort.mkdir()
            (map_link_effort / "map.md").symlink_to(map_target)
            with self.assertRaisesRegex(UnsafeWayfinderState, "safe map"):
                exact_effort(project, Path(".agent-wayfinder/map-link"))

    def test_bounded_effort_selection_resumes_only_one_clear_current_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / ".agent-wayfinder"
            current = root / "current"
            mapless = root / "retired"
            other = root / "other"
            for effort in (current, mapless, other):
                effort.mkdir(parents=True)
            (current / "map.md").write_text(
                "# Release direction\n\n"
                "## Objective\n\nPublish the approved release.\n\n"
                "## Scope\n\nPackaging only.\n",
                encoding="utf-8",
            )
            (mapless / "project-notes.md").write_text(
                "Project-owned content remains after settlement.\n",
                encoding="utf-8",
            )
            (other / "map.md").write_text(
                "# Other work\n\n"
                "## Objective\n\nUpdate documentation.\n\n"
                "## Scope\n\nDocumentation only.\n",
                encoding="utf-8",
            )

            self.assertEqual(
                select_effort(
                    [other, current],
                    "Publish the approved release",
                    "Packaging only",
                ),
                current,
            )
            self.assertIsNone(
                select_effort(
                    [mapless],
                    "Publish the approved release",
                    "Packaging only",
                )
            )
            linked = root / "linked"
            linked.symlink_to(current, target_is_directory=True)
            with self.assertRaisesRegex(UnsafeWayfinderState, "symlink"):
                select_effort(
                    [linked],
                    "Publish the approved release",
                    "Packaging only",
                )
            real_parent = root / "real-parent"
            nested = real_parent / "nested"
            nested.mkdir(parents=True)
            shutil.copy2(current / "map.md", nested / "map.md")
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaisesRegex(UnsafeWayfinderState, "symlink"):
                select_effort(
                    [linked_parent / "nested"],
                    "Publish the approved release",
                    "Packaging only",
                )
            linked_project = Path(temporary) / "linked-project"
            linked_project.symlink_to(root.parent, target_is_directory=True)
            with self.assertRaisesRegex(UnsafeWayfinderState, "symlink"):
                select_effort(
                    [linked_project / ".agent-wayfinder/current"],
                    "Publish the approved release",
                    "Packaging only",
                )
            duplicate = root / "duplicate"
            duplicate.mkdir()
            shutil.copy2(current / "map.md", duplicate / "map.md")
            with self.assertRaisesRegex(UnsafeWayfinderState, "ambiguous effort"):
                select_effort(
                    [current, duplicate],
                    "Publish the approved release",
                    "Packaging only",
                )

    def test_existing_map_with_older_orientation_headings_remains_recognized(
        self,
    ) -> None:
        effort = (
            FIXTURES
            / "wayfinder-effort-selection/.agent-wayfinder/wayfinder-runtime-projection"
        )
        map_text = (effort / "map.md").read_text(encoding="utf-8")

        self.assertIn("## Destination", map_text)
        self.assertIn("## Territory", map_text)
        self.assertTrue(validate_effort(effort))

    def test_current_child_rename_requires_reconciled_references(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            effort = project / ".agent-wayfinder/effort"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            map_path = effort / "map.md"
            target = unknowns / "U1-old-title.md"
            external = project / "current.md"
            map_path.write_text(
                "# Rename\n\n[Question](unknowns/U1-old-title.md) remains open.\n",
                encoding="utf-8",
            )
            target.write_text("# U1: Current question\n", encoding="utf-8")
            external.write_text(
                "[Question](.agent-wayfinder/effort/unknowns/U1-old-title.md)\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                rename_current_child(
                    effort,
                    target,
                    "current-question",
                    known_references=[external],
                )

            map_path.write_text(
                "# Rename\n\nThe current question remains open.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                rename_current_child(
                    effort,
                    target,
                    "current-question",
                    known_references=[external],
                )
            external.write_text("The current question remains open.\n", encoding="utf-8")
            renamed = rename_current_child(
                effort,
                target,
                "current-question",
                known_references=[external],
            )
            self.assertEqual(renamed, unknowns / "U1-current-question.md")
            self.assertFalse(target.exists())
            self.assertEqual(
                renamed.read_text(encoding="utf-8"),
                "# U1: Current question\n",
            )

    def test_current_child_rename_does_not_overwrite_an_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            (effort / "map.md").write_text("# Rename collision\n", encoding="utf-8")
            source = unknowns / "U1-old-title.md"
            target = unknowns / "U1-current-title.md"
            source.write_bytes(b"source bytes\n")
            target.write_bytes(b"existing target bytes\n")

            with self.assertRaisesRegex(
                UnsafeWayfinderState,
                "duplicate current U|already exists",
            ):
                rename_current_child(effort, source, "current-title")

            self.assertEqual(source.read_bytes(), b"source bytes\n")
            self.assertEqual(target.read_bytes(), b"existing target bytes\n")

    def test_ledger_heading_rename_requires_reconciled_anchor_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            effort = project / ".agent-wayfinder/effort"
            effort.mkdir(parents=True)
            map_path = effort / "map.md"
            external = project / "current.md"
            ledger = effort / "facts.md"
            old_link = "facts.md#f1--old-title"
            map_path.write_text(f"# Rename\n\n[Fact]({old_link})\n", encoding="utf-8")
            external.write_text(
                "[Fact](.agent-wayfinder/effort/facts.md#f1--old-title)\n",
                encoding="utf-8",
            )
            remaining = (
                "## F2 — Unrelated fact\n\n"
                "[F1](facts.md#f1--old-title) is related.\n"
            )
            ledger.write_text(
                "# Facts\n\n## F1 — Old title\n\nCurrent.\n\n" + remaining,
                encoding="utf-8",
            )

            with self.assertRaisesRegex(UnsafeWayfinderState, "anchor references"):
                rename_ledger_heading(
                    effort, "F", 1, "Current title", known_references=[external]
                )
            map_path.write_text("# Rename\n\nThe fact remains current.\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "anchor references"):
                rename_ledger_heading(
                    effort, "F", 1, "Current title", known_references=[external]
                )
            external.write_text("The fact remains current.\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "anchor references"):
                rename_ledger_heading(
                    effort, "F", 1, "Current title", known_references=[external]
                )
            ledger.write_text(
                ledger.read_text(encoding="utf-8").replace(
                    "[F1](facts.md#f1--old-title) is related.",
                    "F1 remains related.",
                ),
                encoding="utf-8",
            )

            anchor = rename_ledger_heading(
                effort, "F", 1, "Current title", known_references=[external]
            )
            self.assertEqual(anchor, "f1--current-title")
            self.assertIn("## F1 — Current title", ledger.read_text(encoding="utf-8"))
            self.assertIn("## F2 — Unrelated fact", ledger.read_text(encoding="utf-8"))
            self.assertIn("F1 remains related.", ledger.read_text(encoding="utf-8"))

    def test_new_effort_can_remain_map_only_or_create_a_fact_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Map only\n", encoding="utf-8")

            self.assertTrue(validate_effort(effort))
            self.assertEqual(list(effort.iterdir()), [effort / "map.md"])

            created = create_current_record(
                effort,
                "F",
                "The map can stand alone",
                "- Source: README.md\n\n"
                "A map-only effort is valid.\n",
            )

            self.assertEqual(created, "F1")
            self.assertEqual(
                (effort / "facts.md").read_text(encoding="utf-8"),
                "# Facts\n\n"
                "## F1 — The map can stand alone\n\n"
                "- Source: README.md\n\n"
                "A map-only effort is valid.\n",
            )

    def test_fact_correction_updates_narrows_or_prunes_the_same_identifier(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Current conclusion\n", encoding="utf-8")
            facts = effort / "facts.md"
            facts.write_text(
                "# Facts\n\n"
                "## F1 — Supported environments\n\n"
                "- Source: compatibility.md\n"
                "- Scope: All environments\n\n"
                "The package works in every supported environment.\n",
                encoding="utf-8",
            )

            update_ledger_section(
                effort,
                "F",
                1,
                "- Source: compatibility.md\n"
                "- Scope: Linux environments\n"
                "- Limitations: macOS remains unresolved\n\n"
                "The package works in supported Linux environments.\n",
            )

            current = facts.read_text(encoding="utf-8")
            self.assertEqual(read_current_ids(effort, "F"), [1])
            self.assertIn("## F1 — Supported environments", current)
            self.assertIn("Scope: Linux environments", current)
            self.assertNotIn("every supported environment", current)

            self.assertTrue(prune_ledger_section(effort, "F", 1))
            self.assertFalse(facts.exists())

    def test_decision_ledger_allocates_after_the_highest_valid_unique_heading(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Decisions\n", encoding="utf-8")
            ledger = effort / "decisions.md"
            ledger.write_text(
                "# Decisions\n\n"
                "## D1 — First choice\n\n- Authority: project-policy.md\n\nFirst.\n\n"
                "## D3 — Third choice\n\n- Authority: project-policy.md\n\nThird.\n",
                encoding="utf-8",
            )

            created = create_current_record(
                effort,
                "D",
                "Fourth choice",
                "- Authority: User, 2026-08-25, request\n"
                "- Revisit when: Tests disagree\n\nFourth.\n",
            )
            self.assertEqual(created, "D4")
            self.assertIn("## D4 — Fourth choice", ledger.read_text(encoding="utf-8"))

            ledger.write_text(
                ledger.read_text(encoding="utf-8")
                + "\n## D4 — Duplicate\n\nDuplicate.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(UnsafeWayfinderState, "duplicate current D"):
                create_current_record(effort, "D", "Blocked", "Blocked.\n")

            ledger.write_text(
                "# Decisions\n\n## D0 — Malformed\n\nMalformed.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(UnsafeWayfinderState, "malformed current D"):
                create_current_record(effort, "D", "Blocked", "Blocked.\n")

    def test_current_decision_updates_or_prunes_without_status_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Current decisions\n", encoding="utf-8")
            decisions = effort / "decisions.md"
            decisions.write_text(
                "# Decisions\n\n"
                "## D1 — Delivery boundary\n\n"
                "- Authority: project-policy.md\n\nUse the original boundary.\n",
                encoding="utf-8",
            )

            update_ledger_section(
                effort,
                "D",
                1,
                "- Authority: project-owner.md\n"
                "- Based on: revised-scope.md\n"
                "- Consequences: the current boundary is narrower\n\n"
                "Use the revised boundary.\n",
            )
            self.assertEqual(read_current_ids(effort, "D"), [1])
            self.assertIn("Use the revised boundary", decisions.read_text(encoding="utf-8"))

            self.assertEqual(
                create_current_record(
                    effort,
                    "D",
                    "Independent release choice",
                    "- Authority: release-policy.md\n\nPublish after verification.\n",
                ),
                "D2",
            )
            (effort / "map.md").write_text(
                "# Current decisions\n\nOnly D2 remains current.\n",
                encoding="utf-8",
            )
            self.assertTrue(prune_ledger_section(effort, "D", 1))
            self.assertEqual(read_current_ids(effort, "D"), [2])

    def test_unrecognized_project_content_is_not_interpreted_as_current_references(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            unknown = effort / "unrecognized-project-data/note.md"
            unknown.parent.mkdir(parents=True)
            unknown.write_bytes(
                b"Project-owned prose that happens to mention F1.\n"
            )
            (effort / "map.md").write_text("# Independent pruning\n", encoding="utf-8")
            ledger = effort / "facts.md"
            ledger.write_text(
                "# Facts\n\n## F1 — Current fact\n\n"
                "- Source: source.md\n\nCurrent.\n",
                encoding="utf-8",
            )

            self.assertTrue(prune_ledger_section(effort, "F", 1))
            self.assertFalse(ledger.exists())
            self.assertEqual(
                unknown.read_bytes(),
                b"Project-owned prose that happens to mention F1.\n",
            )

    def test_ledger_pruning_removes_only_the_reconciled_section_and_empty_ledger(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            effort = project / ".agent-wayfinder/effort"
            effort.mkdir(parents=True)
            docs = project / "docs"
            docs.mkdir()
            external = docs / "current.md"
            map_path = effort / "map.md"
            map_path.write_text(
                "# Pruning\n\n"
                "Read [the first fact](facts.md#f1--first-fact).\n",
                encoding="utf-8",
            )
            external.write_text(
                "[First fact](../.agent-wayfinder/effort/facts.md#f1--first-fact)\n",
                encoding="utf-8",
            )
            ledger = effort / "facts.md"
            remaining_section = (
                "## F3 — Remaining fact\n\n"
                "- Source: source.md\n\nRemaining.\n"
            )
            ledger.write_text(
                "# Facts\n\n"
                "## F1 — First fact\n\n- Source: source.md\n\nFirst.\n\n"
                + remaining_section,
                encoding="utf-8",
            )

            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                prune_ledger_section(effort, "F", 1, known_references=[external])

            map_path.write_text("# Pruning\n\nOnly F3 remains.\n", encoding="utf-8")
            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                prune_ledger_section(effort, "F", 1, known_references=[external])
            external.write_text("The first fact was reconciled.\n", encoding="utf-8")
            self.assertTrue(
                prune_ledger_section(effort, "F", 1, known_references=[external])
            )
            remaining = ledger.read_text(encoding="utf-8")
            self.assertEqual(remaining, "# Facts\n\n" + remaining_section)

            map_path.write_text("# Pruning\n\nNo ledger facts remain.\n", encoding="utf-8")
            self.assertTrue(prune_ledger_section(effort, "F", 3))
            self.assertFalse(ledger.exists())
            self.assertFalse(prune_ledger_section(effort, "F", 3))

            preamble = (
                "# Facts\n\n"
                "Project note that is not part of the selected record.\n\n"
            )
            ledger.write_text(
                preamble
                + "## F5 — Pruning fact\n\n- Source: source.md\n\nPrune me.\n",
                encoding="utf-8",
            )
            self.assertTrue(prune_ledger_section(effort, "F", 5))
            self.assertEqual(ledger.read_text(encoding="utf-8"), preamble)

    def test_ledger_append_rereads_before_write_and_preserves_a_changed_claim(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Changed append\n", encoding="utf-8")
            ledger = effort / "facts.md"
            ledger.write_text(
                "# Facts\n\n## F1 — First\n\n- Source: source.md\n\nFirst.\n",
                encoding="utf-8",
            )

            def changed_claim() -> None:
                ledger.write_text(
                    ledger.read_text(encoding="utf-8").rstrip()
                    + "\n\n## F2 — Competing\n\n- Source: source.md\n\nCompeting.\n",
                    encoding="utf-8",
                )

            with self.assertRaisesRegex(UnsafeWayfinderState, "ledger changed"):
                create_current_record(
                    effort,
                    "F",
                    "Would overwrite",
                    "- Source: source.md\n\nUnsafe.\n",
                    before_final_write=changed_claim,
                )

            self.assertEqual(read_current_ids(effort, "F"), [1, 2])
            self.assertNotIn("Would overwrite", ledger.read_text(encoding="utf-8"))

    def test_current_children_use_separate_unknown_and_evidence_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Current records\n", encoding="utf-8")
            self.assertEqual(
                create_current_record(effort, "U", "Independent question", "Question.\n"),
                "U1",
            )
            self.assertEqual(
                create_current_record(effort, "E", "Substantial evidence", "Evidence.\n"),
                "E1",
            )
            self.assertTrue((effort / "unknowns/U1-independent-question.md").is_file())
            self.assertTrue((effort / "evidence/E1-substantial-evidence.md").is_file())
            self.assertFalse((effort / "unknowns.md").exists())
            self.assertFalse((effort / "evidence.md").exists())

    def test_map_replacement_rejects_changed_current_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            map_path = effort / "map.md"
            map_path.write_text("# Current map\n", encoding="utf-8")
            expected = map_path.read_bytes()
            map_path.write_text("# Changed map\n", encoding="utf-8")

            with self.assertRaisesRegex(UnsafeWayfinderState, "map changed"):
                replace_map(effort, expected, b"# Would overwrite\n")

            self.assertEqual(map_path.read_bytes(), b"# Changed map\n")

    def test_current_child_creation_does_not_overwrite_a_late_exact_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Child creation\n", encoding="utf-8")
            target = effort / "unknowns/U1-late-question.md"

            def create_target() -> None:
                target.write_text("Competing current content.\n", encoding="utf-8")

            with self.assertRaisesRegex(UnsafeWayfinderState, "already exists"):
                create_current_child(
                    effort,
                    "U",
                    "late-question",
                    "Would overwrite.\n",
                    before_exclusive_create=create_target,
                )

            self.assertEqual(
                target.read_text(encoding="utf-8"),
                "Competing current content.\n",
            )

    def test_current_child_creation_rejects_a_late_duplicate_identifier(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Child creation\n", encoding="utf-8")
            competing = effort / "unknowns/U1-competing-question.md"
            planned = effort / "unknowns/U1-planned-question.md"

            def create_same_identifier() -> None:
                competing.write_text("Competing current content.\n", encoding="utf-8")

            with self.assertRaisesRegex(UnsafeWayfinderState, "identifiers changed"):
                create_current_child(
                    effort,
                    "U",
                    "planned-question",
                    "Planned current content.\n",
                    before_create=create_same_identifier,
                )

            self.assertFalse(planned.exists())
            self.assertEqual(
                competing.read_text(encoding="utf-8"),
                "Competing current content.\n",
            )

    def test_current_state_allocation_skips_gaps_and_may_reuse_pruned_highest(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            effort.mkdir()
            (effort / "map.md").write_text("# Allocation\n", encoding="utf-8")

            first = create_current_record(
                effort,
                "D",
                "First",
                "- Authority: test fixture\n\nFirst.\n",
            )
            second = create_current_record(
                effort,
                "D",
                "Second",
                "- Authority: test fixture\n\nSecond.\n",
            )
            third = create_current_record(
                effort,
                "D",
                "Third",
                "- Authority: test fixture\n\nThird.\n",
            )
            preserved = {
                identifier: section
                for identifier, _, section in ledger_sections(effort, "D")
                if identifier in {1, 3}
            }

            self.assertEqual(
                (first, second, third),
                ("D1", "D2", "D3"),
            )
            self.assertTrue(prune_ledger_section(effort, "D", 2))
            fourth = create_current_record(
                effort,
                "D",
                "Fourth",
                "- Authority: test fixture\n\nFourth.\n",
            )
            self.assertEqual(fourth, "D4")

            self.assertTrue(prune_ledger_section(effort, "D", 4))
            replacement = create_current_record(
                effort,
                "D",
                "Replacement",
                "- Authority: test fixture\n\nNew meaning.\n",
            )

            self.assertEqual(replacement, "D4")
            current = {
                identifier: section
                for identifier, _, section in ledger_sections(effort, "D")
            }
            self.assertEqual(current[1].rstrip(), preserved[1].rstrip())
            self.assertEqual(current[3].rstrip(), preserved[3].rstrip())
            self.assertTrue((effort / "decisions.md").is_file())

    def test_answered_unknown_pruning_requires_reconciled_references_and_is_idempotent(
        self,
    ) -> None:
        fixture = FIXTURES / "wayfinder-reference-settlement"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            shutil.copytree(fixture, root)
            effort = root / ".agent-wayfinder/release-direction"
            unknown = effort / "unknowns/U17-source-constraint.md"
            evidence = effort / "evidence/E12-source-observation.md"
            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                prune_current_child(effort, unknown)

            (effort / "map.md").write_text(
                "# Release direction settlement\n\n"
                "## Current state\n\n"
                "[F8](facts.md#f8--published-source-selects-staged-release) and "
                "[D4](decisions.md#d4--adopt-the-staged-release-direction) "
                "remain current.\n",
                encoding="utf-8",
            )
            fact = effort / "facts.md"
            fact.write_text(
                fact.read_text(encoding="utf-8").replace(
                    "- Derived from: E12",
                    "- Source: [source.txt](../../source.txt)",
                ),
                encoding="utf-8",
            )
            decision = effort / "decisions.md"
            decision.write_text(
                decision.read_text(encoding="utf-8").replace(
                    "- Based on: U17, F8", "- Based on: F8"
                ),
                encoding="utf-8",
            )
            unknown.write_text(
                unknown.read_text(encoding="utf-8")
                .replace("Related: E12, F8, D4", "Related: F8, D4")
                .replace(
                    "E12 establishes that the release mode is staged.",
                    "The answer is recorded in current state.",
                ),
                encoding="utf-8",
            )
            evidence.write_text(
                evidence.read_text(encoding="utf-8").replace(
                    "Related: U17, F8", "Related: F8"
                ),
                encoding="utf-8",
            )
            self.assertTrue(prune_current_child(effort, evidence))
            self.assertTrue(prune_current_child(effort, unknown))
            self.assertFalse(prune_current_child(effort, evidence))
            source_link = (fact.parent / "../../source.txt").resolve()
            self.assertEqual(source_link, (root / "source.txt").resolve())
            self.assertTrue(source_link.is_file())
            self.assertNotIn("U17", decision.read_text(encoding="utf-8"))

    def test_uncommitted_child_can_be_pruned_without_a_prior_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            unknown = unknowns / "U1-transient.md"
            unknown.write_text("# U1: Transient question\n", encoding="utf-8")

            self.assertTrue(prune_current_child(effort, unknown))
            self.assertFalse(unknown.exists())

    def test_current_child_pruning_requires_known_external_reconciliation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            effort = project / ".agent-wayfinder/effort"
            unknown = effort / "unknowns/U1-current-question.md"
            unknown.parent.mkdir(parents=True)
            (effort / "map.md").write_text("# Settlement\n", encoding="utf-8")
            unknown.write_text("# U1: Current question\n", encoding="utf-8")
            external = project / "current.md"
            external.write_text(
                "[Question](.agent-wayfinder/effort/unknowns/U1-current-question.md)\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                prune_current_child(
                    effort,
                    unknown,
                    known_references=[external],
                )
            external.write_text("The question is settled.\n", encoding="utf-8")
            self.assertTrue(
                prune_current_child(
                    effort,
                    unknown,
                    known_references=[external],
                )
            )

    def test_answered_unknown_without_independent_outcome_can_settle_to_map_only(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "map-only"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            map_path = effort / "map.md"
            unknown = unknowns / "U1-source-constraint.md"
            map_path.write_text("# Map only\n\nU1 remains open.\n", encoding="utf-8")
            unknown.write_text("# U1: Source constraint?\n", encoding="utf-8")
            map_path.write_text(
                "# Map only\n\nThe source constraint is resolved.\n",
                encoding="utf-8",
            )
            self.assertTrue(prune_current_child(effort, unknown))

            self.assertEqual(
                [path.relative_to(effort).as_posix() for path in effort.iterdir()],
                ["map.md"],
            )

    def test_empty_unknowns_directory_has_no_current_state_meaning(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "empty-unknowns"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            map_path = effort / "map.md"
            map_path.write_text(
                "# Empty unknowns\n\nThe ready work has no blocker.\n",
                encoding="utf-8",
            )

            self.assertEqual(current_ids(effort, "U"), [])
            self.assertEqual(next_current_id(effort, "U"), 1)
            self.assertEqual(current_markdown(effort), {map_path: map_path.read_bytes()})
            self.assertTrue(unknowns.is_dir())

    def test_pruning_rechecks_current_state_before_removal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            unknowns = effort / "unknowns"
            unknowns.mkdir(parents=True)
            map_path = effort / "map.md"
            map_path.write_text("# Changed pruning\n", encoding="utf-8")
            unknown = unknowns / "U1-transient.md"
            unknown.write_text("# U1: Transient question\n", encoding="utf-8")

            def changed_reference() -> None:
                map_path.write_text(
                    map_path.read_text(encoding="utf-8") + "\nU1 is still needed.\n",
                    encoding="utf-8",
                )

            with self.assertRaisesRegex(UnsafeWayfinderState, "current state changed"):
                prune_current_child(
                    effort, unknown, before_final_check=changed_reference
                )
            self.assertTrue(unknown.exists())

    def test_settlement_ends_effort_and_preserves_unknown_bytes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            effort = project / ".agent-wayfinder/release-direction"
            unknown = effort / "project-notes.bin"
            (effort / "unknowns").mkdir(parents=True)
            (effort / "evidence").mkdir()
            (effort / "map.md").write_text("# Release direction\n", encoding="utf-8")
            (effort / "facts.md").write_text(
                "# Facts\n\n## F1 — Current fact\n\n- Source: source.md\n\nCurrent.\n",
                encoding="utf-8",
            )
            (effort / "decisions.md").write_text(
                "# Decisions\n\n## D1 — Current choice\n\n"
                "- Authority: project-policy.md\n\nChosen.\n",
                encoding="utf-8",
            )
            (effort / "unknowns/U1-question.md").write_text(
                "# U1: Question?\n", encoding="utf-8"
            )
            (effort / "evidence/E1-source.md").write_text(
                "# E1: Source\n\n- Source: source.md\n", encoding="utf-8"
            )
            unknown.write_bytes(b"\x00project-owned\xff\n")
            canonical = project / "release-direction.md"
            canonical.write_text(
                "U1 was dispositioned.\n\n"
                "[Current map](.agent-wayfinder/release-direction/map.md)\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(UnsafeWayfinderState, "current references"):
                end_effort_state(
                    effort,
                    known_references=[canonical],
                    continuity_owners=[canonical],
                )
            canonical.write_text(
                "# Release direction\n\nU1 was dispositioned; the lasting outcome is owned here.\n",
                encoding="utf-8",
            )
            end_effort_state(
                effort,
                known_references=[canonical],
                continuity_owners=[canonical],
            )

            self.assertTrue(effort.is_dir())
            self.assertEqual(unknown.read_bytes(), b"\x00project-owned\xff\n")
            for relative in (
                "map.md",
                "facts.md",
                "decisions.md",
                "unknowns/U1-question.md",
                "evidence/E1-source.md",
            ):
                self.assertFalse((effort / relative).exists())
            with self.assertRaisesRegex(UnsafeWayfinderState, "safe map"):
                validate_effort(effort)

    def test_effort_ending_aborts_before_removal_when_current_state_changes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / ".agent-wayfinder/current-effort"
            effort.mkdir(parents=True)
            map_path = effort / "map.md"
            facts = effort / "facts.md"
            fact_preamble = (
                "# Facts\n\n"
                "Project-owned ledger note that is not a Wayfinder record.\n\n"
            )
            map_path.write_text("# Current effort\n", encoding="utf-8")
            facts.write_text(
                fact_preamble
                + "## F1 — Current fact\n\n- Source: source.md\n\nCurrent.\n",
                encoding="utf-8",
            )

            def changed_state() -> None:
                map_path.write_text(
                    "# Current effort\n\nThe ready work changed.\n", encoding="utf-8"
                )

            with self.assertRaisesRegex(UnsafeWayfinderState, "current state changed"):
                end_effort_state(
                    effort,
                    before_final_check=changed_state,
                )

            self.assertTrue(map_path.is_file())
            self.assertTrue(facts.is_file())
            self.assertIn("## F1 — Current fact", facts.read_text(encoding="utf-8"))
            end_effort_state(effort)
            self.assertFalse(map_path.exists())
            self.assertEqual(facts.read_text(encoding="utf-8"), fact_preamble)

    def test_effort_ending_removes_the_map_after_other_recognized_state(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            effort = root / ".agent-wayfinder/current-effort"
            (effort / "unknowns").mkdir(parents=True)
            map_path = effort / "map.md"
            fact_path = effort / "facts.md"
            unknown_path = effort / "unknowns/U1-current-question.md"
            map_path.write_text("# Current effort\n", encoding="utf-8")
            fact_path.write_text(
                "# Facts\n\n## F1 — Current fact\n\n- Source: source.md\n\nCurrent.\n",
                encoding="utf-8",
            )
            unknown_path.write_text("# U1: Current question?\n", encoding="utf-8")
            owner = root / "current-outcome.md"
            owner.write_text("U1 remains with this owner.\n", encoding="utf-8")

            def observe_before_map_removal() -> None:
                self.assertTrue(map_path.is_file())
                self.assertFalse(fact_path.exists())
                self.assertFalse(unknown_path.exists())

            end_effort_state(
                effort,
                continuity_owners=[owner],
                before_map_removal=observe_before_map_removal,
            )
            self.assertFalse(map_path.exists())

    def test_effort_ending_rejects_a_symlinked_effort_before_any_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / ".agent-wayfinder"
            target = root / "target"
            target.mkdir(parents=True)
            map_path = target / "map.md"
            map_path.write_text("# Target\n", encoding="utf-8")
            linked = root / "linked"
            linked.symlink_to(target, target_is_directory=True)

            with self.assertRaisesRegex(UnsafeWayfinderState, "symlink"):
                end_effort_state(linked)

            self.assertTrue(map_path.is_file())

            nested_target = root / "real-parent/nested"
            nested_target.mkdir(parents=True)
            nested_map = nested_target / "map.md"
            nested_map.write_text("# Nested target\n", encoding="utf-8")
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(root / "real-parent", target_is_directory=True)
            with self.assertRaisesRegex(UnsafeWayfinderState, "symlink"):
                end_effort_state(
                    linked_parent / "nested",
                )
            self.assertTrue(nested_map.is_file())

    def test_noncanonical_child_ambiguity_is_scoped_to_the_affected_container(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / "effort"
            directory = effort / "unknowns"
            directory.mkdir(parents=True)
            (effort / "map.md").write_text("# Scoped ambiguity\n", encoding="utf-8")
            opaque = directory / "notes.md"
            opaque.write_bytes(b"\x00not a canonical child\xff\n")
            self.assertEqual(next_current_id(effort, "U"), 1)
            self.assertEqual(current_markdown(effort), {
                effort / "map.md": b"# Scoped ambiguity\n",
            })

            malformed = directory / "U1.md"
            malformed.write_bytes(b"malformed bytes\n")
            with self.assertRaisesRegex(
                UnsafeWayfinderState, "unrecognized child filename"
            ):
                next_current_id(effort, "U")
            self.assertEqual(malformed.read_bytes(), b"malformed bytes\n")

            malformed.unlink()
            first = directory / "U1-first.md"
            duplicate = directory / "U1-duplicate.md"
            first.write_bytes(b"first bytes\n")
            duplicate.write_bytes(b"duplicate bytes\n")
            with self.assertRaisesRegex(UnsafeWayfinderState, "duplicate current U"):
                next_current_id(effort, "U")
            self.assertEqual(first.read_bytes(), b"first bytes\n")
            self.assertEqual(duplicate.read_bytes(), b"duplicate bytes\n")

            self.assertEqual(create_current_record(
                effort,
                "F",
                "Independent fact",
                "- Source: source.md\n\nCurrent.\n",
            ), "F1")
            self.assertTrue(prune_ledger_section(effort, "F", 1))
            self.assertEqual(opaque.read_bytes(), b"\x00not a canonical child\xff\n")
            self.assertEqual(first.read_bytes(), b"first bytes\n")
            self.assertEqual(duplicate.read_bytes(), b"duplicate bytes\n")

    def test_effort_ending_requires_continuity_and_preserves_inner_opaque_bytes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            effort = Path(temporary) / ".agent-wayfinder/current-effort"
            (effort / "unknowns").mkdir(parents=True)
            (effort / "map.md").write_text(
                "# Current effort\n\nA consequential question remains.\n",
                encoding="utf-8",
            )
            (effort / "unknowns/U1-current-question.md").write_text(
                "# U1: Current question?\n", encoding="utf-8"
            )
            opaque = effort / "unknowns/notes.md"
            opaque.write_bytes(b"\x00opaque project bytes\xff\n")
            opaque_target = Path(temporary) / "opaque-target.md"
            opaque_target.write_text("opaque symlink target\n", encoding="utf-8")
            opaque_link = effort / "unknowns/reference.md"
            opaque_link.symlink_to(opaque_target)

            with self.assertRaisesRegex(UnsafeWayfinderState, "continuity"):
                end_effort_state(effort)
            self.assertTrue((effort / "map.md").is_file())

            owner = Path(temporary) / "current-outcome.md"
            owner.write_text(
                "# Current outcome\n\nU1 remains owned by the project authority.\n",
                encoding="utf-8",
            )
            end_effort_state(effort, continuity_owners=[owner])
            self.assertFalse((effort / "map.md").exists())
            self.assertFalse((effort / "unknowns/U1-current-question.md").exists())
            self.assertEqual(opaque.read_bytes(), b"\x00opaque project bytes\xff\n")
            self.assertTrue(opaque_link.is_symlink())
            self.assertEqual(opaque_target.read_text(encoding="utf-8"), "opaque symlink target\n")
            self.assertTrue((effort / "unknowns").is_dir())

    def test_contract_keeps_stable_top_level_navigation(self) -> None:
        headings = (
            "## State model and boundaries",
            "## Effort shape and selection",
            "## Current knowledge",
            "## Reconciliation and pruning",
        )
        self.assertEqual(
            [
                line
                for line in self.contract.splitlines()
                if line.startswith("## ") and not line.startswith("### ")
            ],
            list(headings),
        )

    def test_contract_keeps_the_stable_state_surface(self) -> None:
        for required in (
            ".agent-wayfinder/<effort>/map.md",
            "optional `facts.md`",
            "optional `decisions.md`",
            "`unknowns/U<ID>-<slug>.md`",
            "`evidence/E<ID>-<slug>.md`",
            "A map-only effort is valid",
            "Without `map.md`",
        ):
            self.assertIn(required, self.normalized)

    def test_contract_keeps_current_knowledge_and_authority_boundaries(self) -> None:
        current_knowledge = " ".join(
            markdown_section(self.contract, "## Current knowledge").lower().split()
        )
        for identifier in ("`u#`:", "`e#`:", "`f#`:", "`d#`:"):
            self.assertIn(identifier, current_knowledge)
        for authority_boundary in (
            "actual project authority",
            "alternatives still under consideration",
            "research findings",
            "evidence changes",
            "hypotheses",
            "recommendations",
            "agent inference",
            "routine implementation judgment",
            "factual support",
            "evidence may inform a choice",
            "accept residual uncertainty",
            "cannot create it",
        ):
            self.assertIn(authority_boundary, current_knowledge)

        state_model = " ".join(
            markdown_section(
                self.contract,
                "## State model and boundaries",
            ).lower().split()
        )
        self.assertIn("raw transcripts", state_model)
        self.assertIn("private agent memory", state_model)

    def test_contract_uses_current_wayfinder_terminology(self) -> None:
        generated = GENERATED_SKILL.read_text(encoding="utf-8")
        generated_body = generated.split("\n---\n", 1)[1]
        authoritative_instructions = {
            "packaged contract": self.contract,
            "installed contract": INSTALLED_CONTRACT.read_text(encoding="utf-8"),
            "runtime": RUNTIME.read_text(encoding="utf-8"),
            "generated runtime": generated_body,
        }
        for name, instructions in authoritative_instructions.items():
            with self.subTest(surface=name):
                lowered = instructions.lower()
                self.assertIn("reconciliation", lowered)
                self.assertIn("pruning", lowered)
                self.assertNotRegex(lowered, r"\bretir\w*\b")
                self.assertNotIn("settlement", lowered)

    def test_current_wayfinder_surfaces_use_concept_specific_orientation_language(
        self,
    ) -> None:
        generated = GENERATED_SKILL.read_text(encoding="utf-8")
        surfaces = {
            **CURRENT_WAYFINDER_LANGUAGE_SURFACES,
            "generated runtime": generated.split("\n---\n", 1)[1],
        }
        legitimate_noncanonical_uses = (
            "The deployment destination is /srv/application.",
            "The pinned provider calls its tracker concept `frontier`.",
            "The research fixture studies territorial fog forecasts.",
        )
        for prose in legitimate_noncanonical_uses:
            for pattern in RETIRED_CANONICAL_WAYFINDER_PATTERNS:
                with self.subTest(prose=prose, pattern=pattern):
                    self.assertIsNone(re.search(pattern, prose, re.IGNORECASE))

        for name, source in surfaces.items():
            text = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
            for pattern in RETIRED_CANONICAL_WAYFINDER_PATTERNS:
                with self.subTest(surface=name, pattern=pattern):
                    self.assertIsNone(re.search(pattern, text, re.IGNORECASE))

        provider_research = (
            REPOSITORY_ROOT / "docs/provider-research.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Wayfinder v1.2.3 defines", provider_research)
        self.assertIn("frontier", provider_research)

        for path in (
            MAP_FIRST_ADR,
            REPOSITORY_ROOT
            / "architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md",
        ):
            decision = markdown_section(
                path.read_text(encoding="utf-8"), "## Decision"
            ).casefold()
            for current_term in ("objective", "scope", "ready work"):
                with self.subTest(adr=path.name, term=current_term):
                    self.assertIn(current_term, decision)

    def test_default_map_orientation_and_ready_work_semantics_are_explicit(
        self,
    ) -> None:
        effort_shape = markdown_section(self.contract, "## Effort shape and selection")
        orientation = re.findall(r"^- \*\*([^*]+)\*\*", effort_shape, re.MULTILINE)
        self.assertEqual(
            orientation[:7],
            [
                "Objective",
                "Scope",
                "Areas and relationships",
                "Current state",
                "Blockers and dependencies",
                "Ready work",
                "Key links",
            ],
        )
        normalized = " ".join(effort_shape.split())
        ready_work = normalized.split("Ready work means", 1)[1].split(
            "## Current knowledge", 1
        )[0]
        for condition in (
            "unresolved dependency",
            "consequential uncertainty",
            "missing authority",
            "Independent ready work",
            "unrelated work remains blocked",
        ):
            with self.subTest(ready_work_condition=condition):
                self.assertIn(condition, ready_work)
        self.assertIn("A blocker is an unresolved dependency or missing authority", normalized)
        self.assertIn("prevents particular work from proceeding", normalized)
        self.assertIn(
            "When resuming a Wayfinder effort, read `map.md` first",
            self.normalized,
        )

        reconciliation = markdown_section(
            self.contract,
            "## Reconciliation and pruning",
        )
        for heading in (
            "### Reconcile affected state",
            "### Apply record-specific changes",
            "### Prune one record",
            "### Keep or end the effort",
        ):
            self.assertIn(heading, reconciliation)

    def test_current_wayfinder_documentation_uses_pruning_terminology(self) -> None:
        for name, (path, heading) in CURRENT_WAYFINDER_DOC_SECTIONS.items():
            with self.subTest(surface=name):
                passage = markdown_section(
                    path.read_text(encoding="utf-8"),
                    heading,
                ).lower()
                self.assertRegex(passage, r"\bprun\w*\b")
                self.assertNotRegex(passage, r"\bretir\w*\b")

        adr = MAP_FIRST_ADR.read_text(encoding="utf-8").lower()
        self.assertNotIn("dispositioned", adr)
        self.assertNotIn("settlement", adr)

    def test_current_wayfinder_scenario_descriptions_use_pruning_and_ending(
        self,
    ) -> None:
        scenario_descriptions: dict[str, str] = {}
        for name, path in CURRENT_WAYFINDER_SCENARIOS.items():
            with self.subTest(scenario=name):
                scenario = tomllib.loads(path.read_text(encoding="utf-8"))
                description = "\n".join(
                    str(scenario[field]) for field in ("name", "request")
                ).lower()
                scenario_descriptions[name] = description
                self.assertRegex(description, r"\bprun\w*\b")
                self.assertNotRegex(description, r"\bretir\w*\b")
        self.assertIn(
            "end the effort",
            scenario_descriptions["whole-effort ending"],
        )

    def test_current_scenarios_use_domain_language_without_renaming_historical_ids(
        self,
    ) -> None:
        scenarios = {
            path.stem: tomllib.loads(path.read_text(encoding="utf-8"))
            for path in (PACKAGE_ROOT / "tests/scenarios").glob("*.toml")
        }
        revised_areas = scenarios["wayfinder-domain-modeling-revises-territory"]
        self.assertEqual(
            revised_areas["id"], "wayfinder-domain-modeling-revises-territory"
        )
        self.assertIn("areas and relationships", revised_areas["name"].casefold())

        new_effort = scenarios["wayfinder-new-effort"]
        self.assertIn("objective, scope", new_effort["request"].casefold())
        self.assertIn("ready work", new_effort["verification_command"].casefold())

        ticket_handoff = scenarios["wayfinder-contract-smoke"]
        self.assertIn(
            "ticket ordering and readiness", ticket_handoff["request"].casefold()
        )

    def test_contract_keeps_pruning_boundaries(self) -> None:
        pruning = markdown_section(
            self.contract,
            "## Reconciliation and pruning",
        ).lower()
        for boundary in (
            "unrelated efforts",
            "entire repository",
            "git history",
            "recursively delete",
            "tombstones",
            "redirects",
            "archives",
        ):
            self.assertIn(boundary, pruning)

    def test_contract_keeps_identifier_and_anchor_representation(self) -> None:
        for required in (
            "effort-local, positive, and unique within their type",
            "`## F<ID> — <title>`",
            "`## D<ID> — <title>`",
            "one greater than the highest current same-type identifier",
            "repository-relative link",
        ):
            self.assertIn(required, self.normalized)
        self.assertEqual(
            heading_anchor("D", 4, "Adopt the selected approach"),
            "d4--adopt-the-selected-approach",
        )

    def test_contract_keeps_current_state_integrity_and_project_data_boundaries(
        self,
    ) -> None:
        self.assertNotIn(
            "does not coordinate simultaneous writers",
            self.contract.lower(),
        )
        self.assertNotIn("wayfinder-mutation-lock", self.contract.lower())

    def test_residual_uncertainty_and_effort_recognition_fixtures_preserve_behavior(
        self,
    ) -> None:
        residual = (
            FIXTURES
            / "wayfinder-accepted-residual-uncertainty/.agent-wayfinder/"
            "pilot-capacity"
        )
        unknown = residual / "unknowns/U1-peak-concurrency.md"
        approval = (
            FIXTURES
            / "wayfinder-accepted-residual-uncertainty/project-approval.md"
        ).read_text(encoding="utf-8")
        self.assertTrue(unknown.is_file())
        self.assertIn("non-production pilot only", approval)

        state_root = FIXTURES / "wayfinder-settlement/.agent-wayfinder"
        blocked_map = state_root / "blocked-provider-direction/map.md"
        mapless = state_root / "retired-provider-direction"
        self.assertTrue(blocked_map.is_file())
        self.assertIn("checksum", blocked_map.read_text(encoding="utf-8"))
        self.assertFalse((mapless / "map.md").exists())
        self.assertIn(
            "project-owned note",
            (mapless / "project-notes.txt").read_text(encoding="utf-8"),
        )

    def test_authored_installed_and_generated_surfaces_are_consistent(self) -> None:
        self.assertEqual(CONTRACT.read_bytes(), INSTALLED_CONTRACT.read_bytes())
        self.assertEqual(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_bytes(),
            (REPOSITORY_ROOT / ".agent-workflow/routing.md").read_bytes(),
        )
        self.assertEqual(
            (PACKAGE_ROOT / "payload/agent-workflow/README.md").read_bytes(),
            (REPOSITORY_ROOT / ".agent-workflow/README.md").read_bytes(),
        )
        source_policy = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        managed = source_policy.split("<!-- agent-workflow:managed-begin -->", 1)[1]
        managed = managed.split("<!-- agent-workflow:managed-end -->", 1)[0].strip()
        packaged_policy = (
            PACKAGE_ROOT / "payload/root/AGENTS.md.template"
        ).read_text(encoding="utf-8").strip()
        self.assertEqual(packaged_policy, managed)
        runtime = RUNTIME.read_text(encoding="utf-8")
        generated = GENERATED_SKILL.read_text(encoding="utf-8")
        generated_body = generated.split("\n---\n", 1)[1]
        self.assertEqual(runtime, generated_body)
        for heading in (
            "## Operating rules",
            "## Establish areas and relationships",
            "## Resolve the current question progressively",
            "## Reconcile and hand off",
        ):
            self.assertIn(heading, runtime)
        self.assertNotIn("settlement", runtime.lower())


if __name__ == "__main__":
    unittest.main()
