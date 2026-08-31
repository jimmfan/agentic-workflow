#!/usr/bin/env python3
"""Verify the current Agent Workflow package and checked-in projection."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = PACKAGE_ROOT.parent.parent
PAYLOAD_ROOT = PACKAGE_ROOT / "payload"
MANIFEST = PAYLOAD_ROOT / "distribution" / "manifest.json"
MINIMUM_PYTHON = (3, 11)
MANIFEST_SCHEMA = 7
SEMVER = re.compile(r"\d+\.\d+\.\d+")
MARKDOWN_LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")
FENCED_CODE = re.compile(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$")
INLINE_CODE = re.compile(r"`[^`\n]*`")
MANAGED_BEGIN = b"<!-- agent-workflow:managed-begin -->\n"
MANAGED_END = b"<!-- agent-workflow:managed-end -->\n"
PROJECT_BEGIN = b"\n<!-- agent-workflow:project-instructions -->\n"
MARKER_PREFIX = b"<!-- agent-workflow:"

REQUIRED_PACKAGE_FILES = (
    "__init__.py",
    "SKILL.md",
    "VERSION",
    "cli.py",
    "scripts/__init__.py",
    "scripts/bootstrap.py",
    "scripts/lifecycle.py",
    "scripts/verify_package.py",
    "payload/distribution/manifest.json",
    "payload/root/AGENTS.md.template",
    "payload/root/CLAUDE.md.template",
    "payload/agent-workflow/README.md",
    "payload/agent-workflow/THIRD_PARTY_NOTICES.md",
    "payload/agent-workflow/routing.md",
    "payload/agent-workflow/contracts/wayfinder-state.md",
)

EXPECTED_BASE_PAYLOAD_FILES = frozenset(
    {
        "agent-workflow/README.md",
        "agent-workflow/THIRD_PARTY_NOTICES.md",
        "agent-workflow/contracts/wayfinder-state.md",
        "agent-workflow/routing.md",
        "distribution/manifest.json",
        "root/AGENTS.md.template",
        "root/CLAUDE.md.template",
    }
)

EXPECTED_SKILL_FILES = {
    "code-review": frozenset({"SKILL.md", "agents/openai.yaml"}),
    "codebase-design": frozenset(
        {"DEEPENING.md", "DESIGN-IT-TWICE.md", "SKILL.md", "agents/openai.yaml"}
    ),
    "domain-modeling": frozenset(
        {"ADR-FORMAT.md", "CONTEXT-FORMAT.md", "SKILL.md", "agents/openai.yaml"}
    ),
    "grilling": frozenset({"SKILL.md", "agents/openai.yaml"}),
    "implement": frozenset({"SKILL.md", "agents/openai.yaml"}),
    "prototype": frozenset(
        {"LOGIC.md", "SKILL.md", "UI.md", "agents/openai.yaml"}
    ),
    "research": frozenset({"SKILL.md", "agents/openai.yaml"}),
    "tdd": frozenset({"SKILL.md", "agents/openai.yaml", "mocking.md", "tests.md"}),
    "to-spec": frozenset({"SKILL.md", "agents/openai.yaml"}),
    "to-tickets": frozenset({"SKILL.md", "agents/openai.yaml"}),
    "wayfinder": frozenset({"SKILL.md", "agents/openai.yaml"}),
    "workflow-debugging": frozenset({"SKILL.md"}),
    "workflow-discovery": frozenset({"SKILL.md"}),
    "workflow-implementation": frozenset({"SKILL.md"}),
    "workflow-verification": frozenset({"SKILL.md"}),
}

ATTRIBUTED_SKILLS = frozenset(
    {
        "code-review",
        "codebase-design",
        "domain-modeling",
        "grilling",
        "implement",
        "prototype",
        "research",
        "tdd",
        "to-spec",
        "to-tickets",
        "wayfinder",
    }
)


class VerificationError(RuntimeError):
    pass


class DuplicateKeyError(ValueError):
    pass


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except (AttributeError, OSError, ValueError):
                pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def safe_relative(value: object, label: str = "path") -> PurePosixPath:
    require(
        isinstance(value, str)
        and bool(value)
        and "\\" not in value
        and "\x00" not in value,
        f"unsafe {label}: {value!r}",
    )
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise VerificationError(f"unsafe {label}: {value!r}") from exc
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and bool(path.parts)
        and path.as_posix() == value
        and all(part not in {"", ".", ".."} for part in path.parts),
        f"unsafe {label}: {value!r}",
    )
    return path


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path, label: str) -> Mapping[str, object]:
    require(path.is_file() and not path.is_symlink(), f"missing or unsafe {label}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys
        )
    except (UnicodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        raise VerificationError(f"cannot read {label}: {exc}") from exc
    require(isinstance(value, dict), f"{label} must contain an object")
    return value


def version() -> str:
    value = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(SEMVER.fullmatch(value) is not None, "VERSION must use x.y.z")
    return value


def expected_mappings() -> list[dict[str, str]]:
    mappings = [
        {"source": "root/AGENTS.md.template", "target": "AGENTS.md"},
        {"source": "root/CLAUDE.md.template", "target": "CLAUDE.md"},
    ]
    for path in sorted((PAYLOAD_ROOT / "skills").rglob("*")):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(PAYLOAD_ROOT).as_posix()
            mappings.append({"source": relative, "target": f".agents/{relative}"})
    framework_root = PAYLOAD_ROOT / "agent-workflow"
    for path in sorted(framework_root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(PAYLOAD_ROOT).as_posix()
            target = ".agent-workflow/" + path.relative_to(framework_root).as_posix()
            mappings.append({"source": relative, "target": target})
    return sorted(mappings, key=lambda item: item["target"])


def generated_manifest() -> Mapping[str, object]:
    return {"schema_version": MANIFEST_SCHEMA, "framework_owned": expected_mappings()}


def refresh_manifest() -> None:
    MANIFEST.write_text(
        json.dumps(generated_manifest(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Refreshed {MANIFEST.relative_to(PACKAGE_ROOT)}")


def expected_payload_files() -> frozenset[str]:
    skill_files = {
        f"skills/{name}/{relative}"
        for name, files in EXPECTED_SKILL_FILES.items()
        for relative in files
    }
    return EXPECTED_BASE_PAYLOAD_FILES | skill_files


def check_structure() -> None:
    for relative in REQUIRED_PACKAGE_FILES:
        path = PACKAGE_ROOT / relative
        require(
            path.is_file() and not path.is_symlink(),
            f"missing or unsafe package file: {relative}",
        )
    version()
    duplicate_version = PAYLOAD_ROOT / "VERSION"
    require(
        not duplicate_version.exists() and not duplicate_version.is_symlink(),
        "payload/VERSION must remain absent; package VERSION is the single source of truth",
    )
    actual = {
        path.relative_to(PAYLOAD_ROOT).as_posix()
        for path in PAYLOAD_ROOT.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    expected = expected_payload_files()
    require(
        actual == expected,
        "authored payload differs from the exact current package surface: "
        f"expected={sorted(expected)!r}, actual={sorted(actual)!r}",
    )


def check_activation_sensitive_payload() -> None:
    for path in PAYLOAD_ROOT.rglob("*"):
        if path.name in {"AGENTS.md", "CLAUDE.md"}:
            raise VerificationError(
                "activation-sensitive payload path must remain absent: "
                f"{path.relative_to(PACKAGE_ROOT)}"
            )
    for directory in (".agents", ".github"):
        path = PAYLOAD_ROOT / directory
        require(
            not path.exists() and not path.is_symlink(),
            f"activation-sensitive payload path must remain absent: payload/{directory}",
        )


def check_manifest() -> None:
    actual = load_json(MANIFEST, "distribution manifest")
    require(
        set(actual) == {"schema_version", "framework_owned"},
        "distribution manifest contains installation history or unexpected fields",
    )
    require(
        actual == generated_manifest(),
        "distribution manifest is stale; run verify_package.py --refresh-manifest",
    )
    mappings = actual["framework_owned"]
    require(isinstance(mappings, list), "manifest mappings must be an array")
    sources: list[str] = []
    targets: list[str] = []
    for item in mappings:
        require(
            isinstance(item, dict) and set(item) == {"source", "target"},
            "manifest entries must contain only source and target",
        )
        source = safe_relative(item["source"], "manifest source")
        target = safe_relative(item["target"], "manifest target")
        target_value = target.as_posix()
        allowed_target = (
            target_value in {"AGENTS.md", "CLAUDE.md"}
            or target_value.startswith(".agent-workflow/")
            or (
                len(target.parts) >= 4
                and target.parts[:2] == (".agents", "skills")
                and target.parts[2] in EXPECTED_SKILL_FILES
            )
        )
        require(allowed_target, f"manifest target is outside managed surfaces: {target}")
        sources.append(source.as_posix())
        targets.append(target_value)
    require(len(sources) == len(set(sources)), "manifest source paths are duplicated")
    require(len(targets) == len(set(targets)), "manifest target paths are duplicated")


def parse_frontmatter(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    require(text.startswith("---\n"), f"curated skill lacks frontmatter: {path}")
    end = text.find("\n---\n", 4)
    require(end >= 0, f"curated skill lacks closing frontmatter: {path}")
    return text[4:end].splitlines()


def markdown_destinations(path: Path) -> Iterable[str]:
    text = INLINE_CODE.sub("", FENCED_CODE.sub("", path.read_text(encoding="utf-8")))
    for destination in MARKDOWN_LINK.findall(text):
        destination = destination.split("#", 1)[0]
        if destination and "://" not in destination and not destination.startswith("mailto:"):
            yield destination


def validate_skill_links(root: Path) -> None:
    resolved_root = root.resolve()
    for path in root.rglob("*.md"):
        for destination in markdown_destinations(path):
            candidate = (path.parent / destination).resolve()
            require(
                candidate == resolved_root or resolved_root in candidate.parents,
                f"curated skill link escapes its skill root: {path}: {destination}",
            )
            require(
                candidate.exists(),
                f"curated skill link target is missing: {path}: {destination}",
            )


def check_curated_skills() -> None:
    skills_root = PAYLOAD_ROOT / "skills"
    require(
        skills_root.is_dir() and not skills_root.is_symlink(),
        "curated skill payload is missing or unsafe",
    )
    actual_names = {
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and not path.is_symlink()
    }
    require(
        actual_names == set(EXPECTED_SKILL_FILES),
        "curated skill inventory differs from the accepted fifteen-skill inventory",
    )
    for name, expected_files in EXPECTED_SKILL_FILES.items():
        root = skills_root / name
        actual_files = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() or path.is_symlink()
        }
        require(
            actual_files == expected_files,
            f"curated skill {name} is incomplete or contains unexpected files",
        )
        for relative in expected_files:
            path = root / relative
            require(
                path.is_file() and not path.is_symlink() and bool(path.read_bytes()),
                f"curated skill {name} contains a missing, empty, or unsafe file: {relative}",
            )
        frontmatter = parse_frontmatter(root / "SKILL.md")
        require(
            f"name: {name}" in frontmatter,
            f"curated skill name differs from its directory: {name}",
        )
        require(
            any(
                line.startswith("description: ") and line != "description: "
                for line in frontmatter
            ),
            f"curated skill lacks a description: {name}",
        )
        validate_skill_links(root)


def check_local_links() -> None:
    roots = (
        REPOSITORY_ROOT / "README.md",
        REPOSITORY_ROOT / "docs",
        PACKAGE_ROOT / "SKILL.md",
        PAYLOAD_ROOT / "agent-workflow",
    )
    paths: list[Path] = []
    for root in roots:
        if root.is_file():
            paths.append(root)
        elif root.is_dir():
            paths.extend(root.rglob("*.md"))
    for path in paths:
        for destination in markdown_destinations(path):
            candidate = (path.parent / destination).resolve()
            require(
                candidate.exists(),
                f"broken local Markdown link in {path.relative_to(REPOSITORY_ROOT)}: {destination}",
            )


def check_attribution() -> None:
    notice = (PAYLOAD_ROOT / "agent-workflow/THIRD_PARTY_NOTICES.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(notice.split())
    for name in sorted(ATTRIBUTED_SKILLS):
        require(
            f"`{name}`" in notice,
            f"third-party notice omits attributed skill: {name}",
        )
    for clause in (
        "https://github.com/mattpocock/skills",
        "release `v1.2.3`",
        "Copyright (c) 2026 Matt Pocock",
    ):
        require(clause in normalized, f"third-party attribution lacks: {clause}")
    canonical_permission = " ".join(
        """Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.""".split()
    )
    canonical_disclaimer = " ".join(
        """THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""".split()
    )
    require(
        canonical_permission in normalized,
        "third-party attribution lacks the canonical MIT permission terms",
    )
    require(
        canonical_disclaimer in normalized,
        "third-party attribution lacks the canonical MIT warranty disclaimer",
    )


def normalized_text(relative: str) -> str:
    return " ".join((PAYLOAD_ROOT / relative).read_text(encoding="utf-8").split())


def require_clauses(label: str, text: str, clauses: Sequence[str]) -> None:
    for clause in clauses:
        require(clause in text, f"{label} lacks load-bearing contract: {clause}")


def check_semantic_contracts() -> None:
    research = normalized_text("skills/research/SKILL.md")
    require_clauses(
        "Research",
        research,
        (
            "Do not create a standalone research file unless the user explicitly requests a durable research artifact.",
            "repository writes have action authorization",
        ),
    )

    wayfinder = normalized_text("skills/wayfinder/SKILL.md")
    require_clauses(
        "Wayfinder",
        wayfinder,
        (
            "Wayfinder is Agent Workflow's sole durable coordination layer.",
            "Never copy the accepted project record designated to maintain the result into the map.",
        ),
    )

    for label, relative in (
        ("to-spec", "skills/to-spec/SKILL.md"),
        ("to-tickets", "skills/to-tickets/SKILL.md"),
    ):
        text = normalized_text(relative)
        require(".scratch/" not in text, f"{label} infers a .scratch/ destination")
        require(
            "ready-for-agent" not in text,
            f"{label} hard-codes the ready-for-agent label",
        )
        require_clauses(
            label,
            text,
            (
                "destination named by the user",
                "documented by the project",
                "Publish only when",
                "authorizes it",
                "otherwise return",
                "in chat",
                "Do not invent",
                "local destination",
                "label",
                "status",
            ),
        )

    implement = normalized_text("skills/implement/SKILL.md")
    require_clauses(
        "Implement",
        implement,
        (
            "Commit only when the current user request or accepted project policy authorizes it.",
            "Otherwise leave the work uncommitted and report its status.",
        ),
    )

    root_routing = normalized_text("root/AGENTS.md.template")
    require_clauses("Root routing", root_routing, ("Report only what executed",))
    routing = normalized_text("agent-workflow/routing.md")
    require_clauses(
        "Routing",
        routing,
        (
            "Selecting a skill is not execution: include it in the route marker only when its method actually ran.",
        ),
    )


def tree_files(root: Path) -> frozenset[str]:
    require(
        root.is_dir() and not root.is_symlink(),
        f"missing or unsafe directory: {root}",
    )
    files: set[str] = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        require(not path.is_symlink(), f"projection contains a symlink: {path}")
        if path.is_file():
            files.add(relative)
        elif not path.is_dir():
            raise VerificationError(f"projection contains a special entry: {path}")
    return frozenset(files)


def require_tree_equal(source: Path, target: Path, label: str) -> None:
    source_files = tree_files(source)
    target_files = tree_files(target)
    require(
        source_files == target_files,
        f"checked-in {label} inventory differs from current payload",
    )
    for relative in source_files:
        require(
            (source / relative).read_bytes() == (target / relative).read_bytes(),
            f"checked-in projection differs from direct payload: {target / relative}",
        )


def managed_region(path: Path) -> bytes:
    data = path.read_bytes()
    managed_end = data.find(MANAGED_END, len(MANAGED_BEGIN))
    project_begin = data.find(PROJECT_BEGIN, managed_end + len(MANAGED_END))
    require(
        data.count(MARKER_PREFIX) == 3
        and data.count(MANAGED_BEGIN) == 1
        and data.count(MANAGED_END) == 1
        and data.count(PROJECT_BEGIN) == 1
        and data.startswith(MANAGED_BEGIN)
        and managed_end >= 0
        and project_begin == managed_end + len(MANAGED_END),
        f"checked-in composite has invalid managed markers: {path.name}",
    )
    return data[len(MANAGED_BEGIN) : managed_end]


def check_checked_in_projection() -> None:
    installed_framework = REPOSITORY_ROOT / ".agent-workflow"
    installed_skills = REPOSITORY_ROOT / ".agents/skills"
    require(
        not (installed_framework / "install-manifest.json").exists(),
        "checked-in projection must not contain an install manifest",
    )
    require_tree_equal(
        PAYLOAD_ROOT / "agent-workflow", installed_framework, ".agent-workflow"
    )
    require(
        installed_skills.is_dir() and not installed_skills.is_symlink(),
        "checked-in skill projection is missing or unsafe",
    )
    for name in EXPECTED_SKILL_FILES:
        require_tree_equal(
            PAYLOAD_ROOT / "skills" / name,
            installed_skills / name,
            f"skill projection for {name}",
        )
    for source_relative, target_name in (
        ("root/AGENTS.md.template", "AGENTS.md"),
        ("root/CLAUDE.md.template", "CLAUDE.md"),
    ):
        source = (PAYLOAD_ROOT / source_relative).read_bytes().rstrip(b"\n") + b"\n"
        target = REPOSITORY_ROOT / target_name
        require(
            target.is_file()
            and not target.is_symlink()
            and managed_region(target) == source,
            f"checked-in managed composite region is stale: {target_name}",
        )


def run_tests() -> None:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(PACKAGE_ROOT / "tests"),
            "-p",
            "test_*.py",
        ],
        cwd=REPOSITORY_ROOT,
        env=environment,
    )
    require(result.returncode == 0, "test suite failed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-manifest", action="store_true")
    parser.add_argument("--tests", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    configure_console()
    if sys.version_info < MINIMUM_PYTHON:
        print("ERROR: Agent Workflow requires Python 3.11 or newer", file=sys.stderr)
        return 2
    args = build_parser().parse_args(argv)
    try:
        if args.refresh_manifest:
            refresh_manifest()
        for check in (
            check_activation_sensitive_payload,
            check_curated_skills,
            check_structure,
            check_manifest,
            check_local_links,
            check_attribution,
            check_semantic_contracts,
            check_checked_in_projection,
        ):
            check()
        if args.tests:
            run_tests()
        print("OK: Agent Workflow package verification passed.")
        return 0
    except (VerificationError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
