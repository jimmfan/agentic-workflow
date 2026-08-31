#!/usr/bin/env python3
"""Strict development, CI, and release verification for Agent Workflow."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tomllib
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True

from legacy_transition import (
    FORMER_FRAMEWORK_VERSION,
    FORMER_PROVIDERS_SHA256,
    FROZEN_FIXTURE_PROOF_SHA256,
    LEGACY_PROVIDER_PROOF,
    LEGACY_PROVIDER_SKILLS,
    LEGACY_WORKFLOW_DIGESTS,
    PINNED_MAIN_COMMIT,
)


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = PACKAGE_ROOT.parent.parent
PAYLOAD_ROOT = PACKAGE_ROOT / "payload"
MANIFEST = PAYLOAD_ROOT / "distribution" / "manifest.json"
FIXTURE_ROOT = PACKAGE_ROOT / "tests/fixtures/pinned-main-installation"
MINIMUM_PYTHON = (3, 11)
MANIFEST_SCHEMA = 7
INSTALL_SCHEMA = 2
LOCAL_REVISION = "unreleased-local-package"
SEMVER = re.compile(r"\d+\.\d+\.\d+")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
MARKDOWN_LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")
FENCED_CODE = re.compile(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$")
INLINE_CODE = re.compile(r"`[^`\n]*`")
HOST_PREFIX = re.compile(r"(?<![A-Za-z0-9_.-])/(?:tdd|code-review)\b")

REQUIRED_PACKAGE_FILES = (
    "__init__.py",
    "SKILL.md",
    "VERSION",
    "cli.py",
    "scripts/__init__.py",
    "scripts/adopt.py",
    "scripts/bootstrap.py",
    "scripts/legacy_transition.py",
    "scripts/lifecycle.py",
    "scripts/verify_package.py",
    "tests/behavior.py",
    "tests/test_direct_distribution.py",
    "tests/fixtures/pinned-main-installation/proof.json",
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

DERIVED_SKILLS = frozenset(
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
REMOVED_SKILLS = frozenset({"setup-matt-pocock-skills", "teach", "triage"})
IMPLICIT_FRONTMATTER_SKILLS = frozenset(
    {"implement", "to-spec", "to-tickets", "wayfinder"}
)

EXPECTED_SKILL_DESCRIPTIONS = {
    "code-review": 'Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo\'s documented coding standards?) and Spec (does the code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".',
    "codebase-design": "Shared vocabulary for designing deep modules. Use when the user wants to design or improve a module's interface, find deepening opportunities, decide where a seam goes, make code more testable or AI-navigable, or when another skill needs the deep-module vocabulary.",
    "domain-modeling": "Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.",
    "grilling": "Grill the user through interdependent choices requiring human input or project decision authority that materially shape downstream work. Also use when the user explicitly asks to be grilled or stress-test a plan, decision, or idea.",
    "implement": "Implement a piece of work based on a spec or set of tickets.",
    "prototype": "Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.",
    "research": "Investigate substantive questions against high-trust primary sources and return cited findings in chat. Create a repository artifact only when the user explicitly requests durable research output.",
    "tdd": 'Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests.',
    "to-spec": "Turn the current conversation into a spec and publish it to the project issue tracker — no interview, just synthesis of what you've already discussed.",
    "to-tickets": "Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker — edges as text in one file per ticket locally, or native blocking links on a real tracker.",
    "wayfinder": "Keep a lightweight structured map when important unresolved questions, choices, dependencies, blockers, or conflicting conclusions are becoming unreliable to hold in ordinary context.",
    "workflow-debugging": "Diagnose an existing unexplained failure through an evidence-driven feedback loop and falsifiable hypotheses. Use for an observable failure, regression, or performance symptom whose cause is unknown; distinguish diagnosis from a fix with separate action authorization.",
    "workflow-discovery": "Resolve one bounded consequential project choice when explicit alternative and tradeoff analysis materially helps; operate standalone or inside Wayfinder without creating Agent Workflow durable coordination state.",
    "workflow-implementation": "Orchestrate one ready implementation scope through the curated implement skill and independent framework verification. Use after material consequential choices are resolved; skip trivial direct edits and unexplained failures.",
    "workflow-verification": "Independently verify the overall result against acceptance criteria, integration boundaries, expected artifacts, and skill compatibility. Use after meaningful implementation or when auditing completion; reuse existing evidence instead of mechanically repeating it.",
}

EXPECTED_OPENAI_INTERFACES = {
    "code-review": ("Code Review", "Review a diff on standards and spec"),
    "codebase-design": ("Codebase Design", "Vocabulary for deep-module design"),
    "domain-modeling": ("Domain Modeling", "Build and sharpen a domain model"),
    "grilling": (
        "Grilling",
        "Resolve interdependent decisions through structured questions",
    ),
    "implement": ("Implement", "Build work from a spec or tickets"),
    "prototype": ("Prototype", "Prototype to answer a design question"),
    "research": ("Research", "Research from high-trust sources"),
    "tdd": ("TDD", "Test-driven red-green-refactor"),
    "to-spec": ("To Spec", "Turn a conversation into a spec"),
    "to-tickets": ("To Tickets", "Split a plan into tracer-bullet tickets"),
    "wayfinder": ("Wayfinder", "Keep a lightweight map of complicated work"),
}

EXPECTED_PROJECT_LANGUAGE = frozenset(
    {
        "Wayfinder effort",
        "Map",
        "Objective",
        "Scope",
        "Consequential",
        "Current coordination state",
        "Ready work",
        "Dependency",
        "Blocker",
        "U# (unresolved question record)",
        "F# (fact record)",
        "Project decision authority",
        "Reconciliation",
        "Pruning",
        "Framework-owned",
        "Project-owned",
        "Durable",
        "Reconstructable",
    }
)

RETIRED_WAYFINDER_PATTERNS = (
    r"(?im)^##\s+Establish territory\s*$",
    r"(?im)^##\s+Resolve the frontier progressively\s*$",
    r"(?im)^-\s+\*\*(?:Destination|Territory|Ready frontier)\*\*",
    r"\bthe ready frontier\s+(?:is|contains|owns)\b",
    r"\blow-resolution\s+(?:map|maps|view|semantic)\b",
    r"\bre-ent(?:ry|er(?:s|ed|ing)?)\b",
    r"\b(?:ordinary|research|debugging)\s+fog\b",
    r"\b(?:resolve|frame|reconcile|return|native|current|ready|coherent)\s+(?:the\s+)?frontier\b",
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


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


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
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


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
    package_version = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(SEMVER.fullmatch(package_version) is not None, "VERSION must use x.y.z")
    return package_version


def expected_mappings() -> list[dict[str, str]]:
    mappings = [
        {"source": "root/AGENTS.md.template", "target": "AGENTS.md"},
        {"source": "root/CLAUDE.md.template", "target": "CLAUDE.md"},
    ]
    for path in sorted((PAYLOAD_ROOT / "skills").rglob("*")):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(PAYLOAD_ROOT).as_posix()
            mappings.append({"source": relative, "target": f".agents/{relative}"})
    workflow_root = PAYLOAD_ROOT / "agent-workflow"
    for path in sorted(workflow_root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(PAYLOAD_ROOT).as_posix()
            target = ".agent-workflow/" + path.relative_to(workflow_root).as_posix()
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
    require(
        sum(len(files) for files in EXPECTED_SKILL_FILES.values()) == 34,
        "accepted direct skill inventory must contain exactly 34 files",
    )


def check_inert_payload() -> None:
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


def check_source_project_language() -> None:
    context_path = REPOSITORY_ROOT / "CONTEXT.md"
    require(
        context_path.is_file() and not context_path.is_symlink(),
        "source terminology glossary is missing or unsafe",
    )
    context = context_path.read_text(encoding="utf-8")
    terms = frozenset(re.findall(r"^\*\*([^*]+)\*\*:", context, re.MULTILINE))
    require(
        terms == EXPECTED_PROJECT_LANGUAGE,
        "source terminology glossary differs from the accepted language",
    )
    source_policy = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    require(
        "<!-- agent-workflow:project-instructions -->" in source_policy,
        "source project instructions are missing",
    )
    project_policy = source_policy.split(
        "<!-- agent-workflow:project-instructions -->", 1
    )[1]
    normalized = " ".join(project_policy.split())
    for clause in (
        "## Project language",
        "Read `CONTEXT.md` before changing routing, Wayfinder, installed-skill integration, ownership, or framework-lifecycle concepts",
        "determine the actual concept from current source, behavior, tests, and accepted decisions",
        "identify the bounded technical or domain context that owns it",
        "Update `CONTEXT.md` only after the terminology decision is accepted",
    ):
        require(clause in normalized, f"source project language policy lacks: {clause}")
    distributed = (PAYLOAD_ROOT / "root/AGENTS.md.template").read_text(encoding="utf-8")
    require(
        "CONTEXT.md" not in distributed
        and "## Project language" not in distributed
        and not any(PAYLOAD_ROOT.rglob("CONTEXT.md")),
        "source project language policy or glossary must not be distributed",
    )


def check_manifest() -> None:
    actual = load_json(MANIFEST, "distribution manifest")
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
            "invalid manifest mapping",
        )
        source = safe_relative(item["source"], "manifest source")
        target = safe_relative(item["target"], "manifest target")
        require(
            target.parts[0] != ".agent-wayfinder",
            "manifest must not own durable project state",
        )
        sources.append(source.as_posix())
        targets.append(target.as_posix())
    require(len(sources) == len(set(sources)), "manifest source paths are duplicated")
    require(len(targets) == len(set(targets)), "manifest target paths are duplicated")


def check_filesystem() -> None:
    for path in PACKAGE_ROOT.rglob("*"):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        require(
            not path.is_symlink(),
            f"package contains a symlink: {path.relative_to(PACKAGE_ROOT)}",
        )
        if path.is_file() and os.name != "nt":
            mode = stat.S_IMODE(path.stat().st_mode)
            require(
                mode == 0o644,
                f"package file mode must be 0644: {path.relative_to(PACKAGE_ROOT)}",
            )
    for script in PACKAGE_ROOT.rglob("*.py"):
        compile(script.read_text(encoding="utf-8"), str(script), "exec")


def parse_frontmatter(path: Path) -> tuple[list[str], str]:
    text = path.read_text(encoding="utf-8")
    require(text.startswith("---\n"), f"curated skill lacks frontmatter: {path}")
    end = text.find("\n---\n", 4)
    require(end >= 0, f"curated skill lacks closing frontmatter: {path}")
    return text[4:end].splitlines(), text


def validate_local_links(root: Path) -> None:
    resolved_root = root.resolve()
    for path in root.rglob("*.md"):
        text = INLINE_CODE.sub(
            "", FENCED_CODE.sub("", path.read_text(encoding="utf-8"))
        )
        for destination in MARKDOWN_LINK.findall(text):
            destination = destination.split("#", 1)[0]
            if not destination or "://" in destination or destination.startswith("mailto:"):
                continue
            candidate = (path.parent / destination).resolve()
            require(
                candidate == resolved_root or resolved_root in candidate.parents,
                f"curated skill link escapes its skill root: {path}: {destination}",
            )
            require(
                candidate.exists(),
                f"curated skill link target is missing: {path}: {destination}",
            )


def check_direct_skills() -> None:
    skills_root = PAYLOAD_ROOT / "skills"
    actual_names = {path.name for path in skills_root.iterdir() if path.is_dir()}
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
        frontmatter, _text = parse_frontmatter(root / "SKILL.md")
        require(
            f"name: {name}" in frontmatter,
            f"curated skill name differs from its directory: {name}",
        )
        for retired in (
            "github-path:",
            "github-pinned:",
            "github-ref:",
            "github-repo:",
            "github-tree-sha:",
        ):
            require(
                not any(retired in line for line in frontmatter),
                f"curated skill {name} retains obsolete provenance metadata: {retired}",
            )
        if name in IMPLICIT_FRONTMATTER_SKILLS:
            require(
                "disable-model-invocation: false" in frontmatter,
                f"curated skill {name} lost its effective implicit invocation behavior",
            )
        expected_frontmatter = {
            f"description: {EXPECTED_SKILL_DESCRIPTIONS[name]}",
            f"name: {name}",
        }
        if name in IMPLICIT_FRONTMATTER_SKILLS:
            expected_frontmatter.add("disable-model-invocation: false")
        require(
            len(frontmatter) == len(expected_frontmatter)
            and set(frontmatter) == expected_frontmatter,
            f"curated skill {name} behavior-bearing frontmatter differs from the accepted effective version",
        )
        if "agents/openai.yaml" in expected_files:
            metadata = (root / "agents/openai.yaml").read_text(encoding="utf-8")
            require(
                metadata.startswith("interface:\n"),
                f"curated Codex metadata is malformed: {name}",
            )
            require(
                "allow_implicit_invocation: true" not in metadata,
                f"curated skill {name} adds redundant default-true invocation metadata",
            )
            display_name, short_description = EXPECTED_OPENAI_INTERFACES[name]
            expected_metadata = {
                "interface:",
                f'  display_name: "{display_name}"',
                f'  short_description: "{short_description}"',
            }
            metadata_lines = metadata.splitlines()
            require(
                len(metadata_lines) == len(expected_metadata)
                and set(metadata_lines) == expected_metadata,
                f"curated Codex metadata differs from the accepted effective version: {name}",
            )
        validate_local_links(root)


def fixture_snapshot(root: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []

    def visit(directory: Path, relative: PurePosixPath | None = None) -> None:
        try:
            with os.scandir(directory) as iterator:
                children = sorted(iterator, key=lambda item: item.name)
        except OSError as exc:
            raise VerificationError(f"cannot inspect frozen fixture: {exc}") from exc
        for child in children:
            child_relative = PurePosixPath(child.name) if relative is None else relative / child.name
            details = child.stat(follow_symlinks=False)
            if stat.S_ISDIR(details.st_mode):
                entries.append({"path": child_relative.as_posix(), "type": "directory"})
                visit(Path(child.path), child_relative)
            elif stat.S_ISREG(details.st_mode):
                entries.append(
                    {
                        "path": child_relative.as_posix(),
                        "type": "file",
                        "sha256": digest(Path(child.path).read_bytes()),
                    }
                )
            elif stat.S_ISLNK(details.st_mode):
                entries.append({"path": child_relative.as_posix(), "type": "symlink"})
            else:
                entries.append({"path": child_relative.as_posix(), "type": "special"})

    visit(root)
    return sorted(entries, key=lambda item: str(item["path"]))


def check_frozen_fixture() -> None:
    proof_path = FIXTURE_ROOT / "proof.json"
    require(
        digest(proof_path.read_bytes()) == FROZEN_FIXTURE_PROOF_SHA256,
        "frozen fixture proof-file SHA-256 differs from the accepted digest",
    )
    proof = load_json(proof_path, "frozen fixture proof")
    require(
        set(proof) == {"schema_version", "source_commit", "former_providers_sha256", "entries"},
        "frozen fixture proof fields are incomplete or unexpected",
    )
    require(proof["schema_version"] == 1, "unsupported frozen fixture proof schema")
    require(
        proof["source_commit"] == PINNED_MAIN_COMMIT,
        "frozen fixture source commit differs from production transition proof",
    )
    require(
        proof["former_providers_sha256"] == FORMER_PROVIDERS_SHA256,
        "frozen fixture declaration digest differs from production transition proof",
    )
    entries = proof["entries"]
    require(isinstance(entries, list), "frozen fixture entries must be an array")
    paths: list[str] = []
    for entry in entries:
        require(isinstance(entry, dict), "frozen fixture entry must be an object")
        entry_type = entry.get("type")
        expected_fields = {"path", "type", "sha256"} if entry_type == "file" else {"path", "type"}
        require(
            set(entry) == expected_fields,
            "frozen fixture entry fields are incomplete or unexpected",
        )
        path = safe_relative(entry["path"], "frozen fixture path").as_posix()
        require(
            entry_type in {"file", "directory"},
            f"frozen fixture contains an unsafe entry type: {path}",
        )
        if entry_type == "file":
            require(
                isinstance(entry["sha256"], str)
                and SHA256_PATTERN.fullmatch(entry["sha256"]) is not None,
                f"frozen fixture contains an invalid file digest: {path}",
            )
        paths.append(path)
    require(paths == sorted(paths), "frozen fixture proof paths must be sorted")
    require(len(paths) == len(set(paths)), "frozen fixture proof paths are duplicated")
    actual = fixture_snapshot(FIXTURE_ROOT / "project")
    require(actual == entries, "frozen fixture bytes or filesystem shape differ from proof")

    entry_map = {
        str(entry["path"]): (
            str(entry["type"]),
            entry.get("sha256") if entry["type"] == "file" else None,
        )
        for entry in entries
    }
    legacy_prefixes = tuple(f".agents/skills/{name}" for name in LEGACY_PROVIDER_SKILLS)
    fixture_legacy = {
        path: value
        for path, value in entry_map.items()
        if any(path == prefix or path.startswith(prefix + "/") for prefix in legacy_prefixes)
    }
    require(
        fixture_legacy == dict(LEGACY_PROVIDER_PROOF),
        "frozen fixture legacy trees differ from immutable production proof",
    )
    for path, checksum in LEGACY_WORKFLOW_DIGESTS.items():
        require(
            entry_map.get(path) == ("file", checksum),
            f"frozen fixture workflow evidence differs at {path}",
        )
    declaration = FIXTURE_ROOT / "project/.agent-workflow/providers.json"
    require(
        digest(declaration.read_bytes()) == FORMER_PROVIDERS_SHA256,
        "frozen former declaration bytes differ from independently verified digest",
    )
    former_manifest = load_json(
        FIXTURE_ROOT / "project/.agent-workflow/install-manifest.json",
        "frozen former install manifest",
    )
    require(
        former_manifest.get("schema_version") == 1
        and former_manifest.get("framework_version") == FORMER_FRAMEWORK_VERSION
        and former_manifest.get("source_revision") == LOCAL_REVISION,
        "frozen former install identity differs from the supported transition",
    )
    external = former_manifest.get("external_files")
    require(isinstance(external, dict), "frozen former external evidence is malformed")
    require(
        {
            path: details.get("sha256")
            for path, details in external.items()
            if isinstance(details, dict)
        }
        == dict(LEGACY_WORKFLOW_DIGESTS),
        "frozen former workflow evidence differs from production transition proof",
    )


def check_attribution() -> None:
    notice = (PAYLOAD_ROOT / "agent-workflow/THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    normalized = " ".join(notice.split())
    for name in sorted(DERIVED_SKILLS):
        require(f"`{name}`" in notice, f"third-party notice omits retained derived skill: {name}")
    for name in sorted(REMOVED_SKILLS):
        require(f"`{name}`" in notice, f"third-party notice omits fixture-only historical skill: {name}")
    for clause in (
        "https://github.com/mattpocock/skills",
        "release `v1.2.3`",
        "Copyright (c) 2026 Matt Pocock",
        "those three skills are not part of the current runtime payload",
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


def require_order(label: str, text: str, clauses: Sequence[str]) -> None:
    positions = [text.find(clause) for clause in clauses]
    require(
        all(position >= 0 for position in positions) and positions == sorted(positions),
        f"{label} destination precedence is missing or reordered",
    )


def check_semantic_contracts() -> None:
    research = normalized_text("skills/research/SKILL.md")
    require_clauses(
        "Research",
        research,
        (
            "Return sourced research findings in chat by default.",
            "Do not create a standalone research file unless the user explicitly requests a durable research artifact.",
            "repository writes have action authorization",
            "Do not create raw or temporary research files inside the repository.",
        ),
    )

    wayfinder_path = PAYLOAD_ROOT / "skills/wayfinder/SKILL.md"
    wayfinder_raw = wayfinder_path.read_text(encoding="utf-8")
    wayfinder = " ".join(wayfinder_raw.split())
    require_clauses(
        "Wayfinder",
        wayfinder,
        (
            "Wayfinder is Agent Workflow's sole durable coordination layer.",
            "Route before inspecting state; an existing map never selects Wayfinder.",
            "read the state contract before effort state",
            "If the state contract is unavailable, fail closed",
            "create the artifact designated to maintain the result or return evidence",
            "Authorization to perform an action does not commit a project choice",
            "Host permission supplies neither.",
            "Implementation consumes one ready scope and its acceptance criteria; Verification follows material execution.",
        ),
    )
    for pattern in RETIRED_WAYFINDER_PATTERNS:
        require(
            re.search(pattern, wayfinder_raw, re.IGNORECASE) is None,
            f"Wayfinder retains retired canonical language: {pattern}",
        )
    for incompatible in ("child issue of the map", "map is the parent issue"):
        require(incompatible not in wayfinder.lower(), "Wayfinder contains incompatible tracker mechanics")

    to_spec = normalized_text("skills/to-spec/SKILL.md")
    to_tickets = normalized_text("skills/to-tickets/SKILL.md")
    precedence = ("the current user request", "project instructions", "project-owned configuration", "no destination")
    for label, text in (("To Spec", to_spec), ("To Tickets", to_tickets)):
        require_order(label, text, precedence)
        require_clauses(
            label,
            text,
            (
                "conflicting destinations, stop and ask which project source governs",
                "A known destination does not authorize publication.",
                "present the complete",
                "create no temporary repository file",
                "project defines their semantics",
                "authorized",
            ),
        )
    require_clauses(
        "To Tickets",
        to_tickets,
        (
            "blocking-link creation, status changes, and labels require authorization",
            "Use the platform's native blocking or sub-issue relationship",
        ),
    )

    code_review = normalized_text("skills/code-review/SKILL.md")
    require_clauses(
        "Code Review",
        code_review,
        (
            "Tracker access is optional source lookup, not a prerequisite for either axis.",
            "The Standards axis never fails merely because no tracker is configured or reachable.",
            "Return the review in chat by default.",
            "only when that action is separately authorized",
        ),
    )

    implement_path = PAYLOAD_ROOT / "skills/implement/SKILL.md"
    implement = " ".join(implement_path.read_text(encoding="utf-8").split())
    require(not HOST_PREFIX.search(implement), "Implement retains a host-specific skill prefix")
    require_clauses(
        "Implement",
        implement,
        (
            "Use `tdd` where possible",
            "use `code-review` to review the work",
            "Commit only when the current user request or accepted project policy authorizes it.",
            "Otherwise leave the work uncommitted and report its status.",
            "owns the inner build, test, and review loop",
            "does not select the outer workflow route, create durable coordination state, authorize actions, or perform Agent Workflow's independent acceptance verification",
        ),
    )

    routing = normalized_text("agent-workflow/routing.md")
    require_clauses(
        "Routing",
        routing,
        (
            "Meaningful Implementation runs Verification once.",
            "New causal uncertainty returns to Debugging; a material unresolved choice returns to Discovery or Wayfinder",
            "workflow-discovery`, `workflow-debugging`, `workflow-implementation`, and `workflow-verification` become `discovery`, `debugging`, `implement`, and `verification`",
            "`<skill>-handoff`",
            "`<skill>-unavailable`",
            "`<skill>-blocked`",
            "Specifications, tickets, research results, maps, and reviews remain in their project or external locations. The artifact designated to maintain the result remains authoritative",
        ),
    )
    implementation = normalized_text("skills/workflow-implementation/SKILL.md")
    require_clauses(
        "Implementation integration",
        implementation,
        (
            "Return a material unresolved choice to Discovery or Wayfinder",
            "an unexplained failure to Debugging",
            "Invoke the installed `implement` skill once",
            "Invoke `workflow-verification` once",
            "the artifact designated to maintain the result",
        ),
    )
    verification = normalized_text("skills/workflow-verification/SKILL.md")
    require_clauses(
        "Verification integration",
        verification,
        (
            "Return implementation defects to `workflow-implementation`",
            "decision defects to `workflow-discovery`",
            "an unexplained symptom to `workflow-debugging`",
            "the artifact designated to maintain the result",
        ),
    )


def iter_current_text_paths() -> Iterable[Path]:
    roots = (
        REPOSITORY_ROOT / "README.md",
        REPOSITORY_ROOT / "CONTEXT.md",
        REPOSITORY_ROOT / "docs",
        REPOSITORY_ROOT / "architecture-decisions",
        REPOSITORY_ROOT / "AGENTS.md",
        PACKAGE_ROOT / "SKILL.md",
        PAYLOAD_ROOT / "root",
        PAYLOAD_ROOT / "agent-workflow",
        PAYLOAD_ROOT / "skills",
    )
    for root in roots:
        paths = (root,) if root.is_file() else tuple(root.rglob("*")) if root.is_dir() else ()
        for path in paths:
            if not path.is_file() or path.suffix not in {".md", ".template", ".yaml"}:
                continue
            if path.name == "THIRD_PARTY_NOTICES.md":
                continue
            yield path


def check_retired_architecture_and_conventions() -> None:
    for relative in (
        "provider-snapshots",
        "runtime-projections",
        "scripts/provider_snapshot.py",
        "scripts/providers.py",
        "scripts/refresh_provider_snapshot.py",
        "tests/test_providers.py",
        "payload/agent-workflow/providers.json",
        "payload/skills/setup-matt-pocock-skills",
        "payload/skills/teach",
        "payload/skills/triage",
    ):
        path = PACKAGE_ROOT / relative
        require(
            not path.exists() and not path.is_symlink(),
            f"retired runtime architecture remains: {relative}",
        )
    for path in iter_current_text_paths():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(REPOSITORY_ROOT)
        for literal in (".scratch/", "skill-owned artifact", "skill lifecycle"):
            require(
                literal.lower() not in text.lower(),
                f"current surface retains forbidden convention {literal!r}: {relative}",
            )
        for literal in (
            "artifact designated to maintain a result",
            "artifact designated to maintain it",
            "artifact designated to maintain them",
            "artifact designated to maintain the specialist result",
            "artifacts designated to maintain their results",
            "artifacts designated to maintain lasting results",
            "artifacts that maintain accepted results",
            "artifacts that maintain lasting results",
            "artifacts that maintain relevant results",
            "artifact that maintains the referenced result",
            "artifact that maintains the lasting result",
            "locations designated to maintain their results",
            "designated maintaining artifact",
        ):
            require(
                literal.lower() not in text.lower(),
                "current surface substitutes for required result-artifact terminology "
                f"{literal!r}: {relative}",
            )
        require(
            HOST_PREFIX.search(text) is None,
            f"current surface retains host-specific tdd/code-review invocation: {relative}",
        )
        require(
            "setup, tdd, and code review" not in text.lower(),
            f"current surface retains stale Setup verification check: {relative}",
        )
        for retired in (
            ".agent-workflow/providers.json",
            "provider-native",
            "refresh_provider_snapshot.py",
            "provider-snapshots/",
        ):
            require(
                retired.lower() not in text.lower(),
                f"current surface retains retired runtime architecture {retired!r}: {relative}",
            )


def install_integrity(manifest: Mapping[str, object]) -> str:
    value = {
        key: manifest[key]
        for key in ("schema_version", "framework_version", "source_revision", "external_files", "composites")
    }
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return digest(encoded)


def managed_region(path: Path) -> bytes:
    data = path.read_bytes()
    begin = b"<!-- agent-workflow:managed-begin -->\n"
    end = b"<!-- agent-workflow:managed-end -->\n"
    require(
        data.count(begin) == 1 and data.count(end) == 1 and data.startswith(begin),
        f"checked-in composite has invalid managed markers: {path.name}",
    )
    return data[len(begin) : data.index(end)]


def check_checked_in_projection() -> None:
    installed_framework = REPOSITORY_ROOT / ".agent-workflow"
    installed_skills = REPOSITORY_ROOT / ".agents/skills"
    require(
        installed_framework.is_dir() and not installed_framework.is_symlink(),
        "checked-in framework projection is missing or unsafe",
    )
    require(
        installed_skills.is_dir() and not installed_skills.is_symlink(),
        "checked-in skill projection is missing or unsafe",
    )
    require(
        {path.name for path in installed_skills.iterdir() if path.is_dir()} == set(EXPECTED_SKILL_FILES),
        "checked-in projection does not contain exactly the fifteen curated skills",
    )
    mappings = expected_mappings()
    expected_internal: set[str] = {"install-manifest.json"}
    expected_external: dict[str, str] = {}
    for mapping in mappings:
        source = PAYLOAD_ROOT / mapping["source"]
        target = REPOSITORY_ROOT / mapping["target"]
        if mapping["target"] in {"AGENTS.md", "CLAUDE.md"}:
            require(
                managed_region(target) == source.read_bytes().rstrip(b"\n") + b"\n",
                f"checked-in managed composite region is stale: {mapping['target']}",
            )
        else:
            require(
                target.is_file() and not target.is_symlink() and target.read_bytes() == source.read_bytes(),
                f"checked-in projection differs from direct payload: {mapping['target']}",
            )
        if mapping["target"].startswith(".agent-workflow/"):
            expected_internal.add(PurePosixPath(mapping["target"]).relative_to(".agent-workflow").as_posix())
        elif mapping["target"].startswith(".agents/skills/"):
            expected_external[mapping["target"]] = digest(source.read_bytes())
    actual_internal = {
        path.relative_to(installed_framework).as_posix()
        for path in installed_framework.rglob("*")
        if path.is_file()
    }
    require(
        actual_internal == expected_internal,
        "checked-in .agent-workflow inventory differs from current direct payload",
    )
    manifest = load_json(installed_framework / "install-manifest.json", "checked-in install manifest")
    require(
        set(manifest) == {"schema_version", "framework_version", "source_revision", "external_files", "composites", "integrity_sha256"},
        "checked-in install manifest fields are incomplete or unexpected",
    )
    require(
        manifest["schema_version"] == INSTALL_SCHEMA
        and manifest["framework_version"] == version()
        and manifest["source_revision"] == LOCAL_REVISION,
        "checked-in install identity differs from the canonical source projection",
    )
    require(
        manifest["integrity_sha256"] == install_integrity(manifest),
        "checked-in install manifest integrity digest is invalid",
    )
    external = manifest["external_files"]
    require(isinstance(external, dict), "checked-in external evidence is malformed")
    require(
        set(external) == set(expected_external) and len(external) == 34,
        "checked-in deletion provenance does not cover exactly 34 direct skill files",
    )
    for path, checksum in expected_external.items():
        require(
            external[path] == {"created": True, "sha256": checksum},
            f"checked-in deletion provenance differs at {path}",
        )
    require(
        manifest["composites"] == {"AGENTS.md": {"created": False}, "CLAUDE.md": {"created": True}},
        "checked-in composite creation provenance differs from the exact transition",
    )
    status = subprocess.run(
        [sys.executable, str(PACKAGE_ROOT / "scripts/lifecycle.py"), "status", str(REPOSITORY_ROOT)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        errors="backslashreplace",
    )
    require(
        status.returncode == 0,
        "checked-in source projection is not healthy: " + (status.stderr.strip() or status.stdout.strip()),
    )


def check_behavior_scenarios() -> None:
    behavior = subprocess.run(
        [sys.executable, str(PACKAGE_ROOT / "tests/behavior.py"), "validate"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        errors="backslashreplace",
    )
    require(
        behavior.returncode == 0,
        "behavioral scenario validation failed: " + (behavior.stderr.strip() or behavior.stdout.strip()),
    )
    positive_fields = (
        "name",
        "request",
        "starting_state",
        "verification_command",
        "state_must_include",
        "report_must_include",
    )
    positive_assertions = {
        "glob_any_contains",
        "glob_any_matches",
        "glob_contains",
        "glob_count",
        "path_contains",
        "path_exists",
    }
    scenario_root = PACKAGE_ROOT / "tests/scenarios"
    for path in sorted(scenario_root.glob("*.toml")):
        scenario = tomllib.loads(path.read_text(encoding="utf-8"))
        active_values: list[str] = []
        for field in positive_fields:
            value = scenario.get(field, "")
            if isinstance(value, str):
                active_values.append(value)
            elif isinstance(value, list):
                active_values.extend(item for item in value if isinstance(item, str))
        for assertion in scenario.get("assertions", []):
            if not isinstance(assertion, dict) or assertion.get("kind") not in positive_assertions:
                continue
            if assertion.get("kind") == "glob_count" and assertion.get("count") == 0:
                continue
            active_values.extend(
                value
                for key in ("path", "value")
                if isinstance((value := assertion.get(key)), str)
            )
        active_text = "\n".join(active_values)
        for literal in (".scratch/", "skill-owned artifact", "skill lifecycle"):
            require(
                literal.lower() not in active_text.lower(),
                f"active behavioral scenario retains forbidden convention {literal!r}: "
                f"{path.relative_to(REPOSITORY_ROOT)}",
            )
        require(
            HOST_PREFIX.search(active_text) is None,
            "active behavioral scenario retains host-specific tdd/code-review invocation: "
            f"{path.relative_to(REPOSITORY_ROOT)}",
        )
        for retired in (".agent-workflow/providers.json", "provider-native"):
            require(
                retired.lower() not in active_text.lower(),
                f"active behavioral scenario retains retired runtime architecture {retired!r}: "
                f"{path.relative_to(REPOSITORY_ROOT)}",
            )


def check_markdown_links() -> None:
    roots = (
        REPOSITORY_ROOT / "README.md",
        REPOSITORY_ROOT / "docs",
        PACKAGE_ROOT / "SKILL.md",
        PAYLOAD_ROOT / "agent-workflow",
        PAYLOAD_ROOT / "skills",
    )
    paths: list[Path] = []
    for root in roots:
        if root.is_file():
            paths.append(root)
        elif root.is_dir():
            paths.extend(root.rglob("*.md"))
    for path in paths:
        text = INLINE_CODE.sub("", FENCED_CODE.sub("", path.read_text(encoding="utf-8")))
        for destination in MARKDOWN_LINK.findall(text):
            destination = destination.split("#", 1)[0]
            if not destination or "://" in destination or destination.startswith("mailto:"):
                continue
            candidate = (path.parent / destination).resolve()
            require(
                candidate.exists(),
                f"broken local Markdown link in {path.relative_to(REPOSITORY_ROOT)}: {destination}",
            )


def run_tests() -> None:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(PACKAGE_ROOT / "tests"), "-p", "test_*.py", "-v"],
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
            check_inert_payload,
            check_structure,
            check_source_project_language,
            check_manifest,
            check_filesystem,
            check_direct_skills,
            check_frozen_fixture,
            check_attribution,
            check_semantic_contracts,
            check_retired_architecture_and_conventions,
            check_checked_in_projection,
            check_behavior_scenarios,
            check_markdown_links,
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
