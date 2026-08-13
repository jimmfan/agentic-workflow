#!/usr/bin/env python3
"""Validate the self-contained Agentic Workflow distribution package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
from typing import Dict, Iterable, List, Mapping, Optional, Sequence


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PAYLOAD_ROOT = PACKAGE_ROOT / "payload"
MANIFEST_PATH = PAYLOAD_ROOT / "distribution" / "manifest.json"
ROUTE_SCENARIOS_PATH = PACKAGE_ROOT / "tests" / "route-observability-scenarios.json"
PROVIDERS_PATH = PAYLOAD_ROOT / "ai-workflow" / "providers.json"
SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
SKILLS = (
    "workflow-debugging",
    "workflow-discovery",
    "workflow-implementation",
    "workflow-verification",
)
SEEDS = (
    {"source": "ai-workflow/templates/project-profile.md", "target": "ai-workflow/project-profile.md"},
    {"source": "ai-workflow/templates/active-state.md", "target": "ai-workflow/state/active.md"},
)
RETIRED = (
    ".agents/skills/workflow-decomposition/SKILL.md",
    ".agents/skills/workflow-review/SKILL.md",
    ".agents/skills/workflow-teach/SKILL.md",
    ".agents/skills/hermes-delegation/SKILL.md",
    "ai-workflow/templates/learning-record.md",
    "ai-workflow/templates/ticket-record.md",
    "adapters/hermes/profile-config.yaml",
    "adapters/hermes/request.schema.json",
    "adapters/hermes/result.schema.json",
    "adapters/hermes/smoke-request.json",
    "docs/architecture.md",
    "docs/decisions/0002-use-checksummed-copy-adoption.md",
    "docs/decisions/0003-use-internal-reference-inspired-workflows.md",
    "docs/decisions/0005-add-decomposition-and-independent-review.md",
    "docs/decisions/0006-use-inert-bootstrap-payload.md",
    "docs/integrations/hermes.md",
    "docs/routing.md",
    "docs/verification.md",
    "scripts/hermes_adapter.py",
)
EXECUTABLE_PACKAGE_PATHS = frozenset()
WINDOWS_ORDINARY_MODES = {0o444, 0o555, 0o666, 0o777}
PROVIDER_REPOSITORY = "mattpocock/skills"
PROVIDER_VERSION = "v1.2.3"
PROVIDER_REVISION = "6acc160e4e0cd062dbbbd7a1b26ae92855edf07e"
PROVIDER_CAPABILITIES = {
    "code-review": "code-review",
    "implementation": "implement",
    "learning": "teach",
    "planning": "wayfinder",
    "research": "research",
    "specification": "to-spec",
    "test-driven-development": "tdd",
    "tickets": "to-tickets",
}
PROVIDER_SKILLS = {
    "setup-matt-pocock-skills",
    "wayfinder",
    "teach",
    "research",
    "to-spec",
    "to-tickets",
    "implement",
    "tdd",
    "code-review",
    "grilling",
    "domain-modeling",
    "prototype",
    "codebase-design",
}


class VerificationError(RuntimeError):
    """A package invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reviewed_filesystem_mode(
    path: Path,
    *,
    expected: int,
    posix_modes_meaningful: Optional[bool] = None,
) -> int:
    mode = stat.S_IMODE(path.stat().st_mode)
    if posix_modes_meaningful is None:
        posix_modes_meaningful = os.name != "nt"
    if posix_modes_meaningful:
        require(mode == expected, f"package entry mode must be {expected:04o}, found {mode:04o}: {path}")
        return mode
    allowed = WINDOWS_ORDINARY_MODES
    require(
        mode in allowed,
        "package entry mode must be an ordinary Windows mode "
        f"({', '.join(f'{item:04o}' for item in sorted(allowed))}), found {mode:04o}: {path}",
    )
    return expected


def safe_relative(raw: str) -> PurePosixPath:
    require(isinstance(raw, str), f"manifest path must be a string: {raw!r}")
    path = PurePosixPath(raw)
    require(bool(raw) and not path.is_absolute() and ".." not in path.parts and "." not in path.parts and "\\" not in raw, f"unsafe manifest path: {raw!r}")
    return path


def payload_files() -> List[str]:
    excluded = {"VERSION", "distribution/manifest.json"}
    return sorted(
        path.relative_to(PAYLOAD_ROOT).as_posix()
        for path in PAYLOAD_ROOT.rglob("*")
        if path.is_file() and not path.is_symlink() and path.relative_to(PAYLOAD_ROOT).as_posix() not in excluded
    )


def target_for(source: str) -> str:
    if source == "root/AGENTS.md.template":
        return "AGENTS.md"
    if source == "root/CLAUDE.md.template":
        return "CLAUDE.md"
    match = re.fullmatch(r"skills/([^/]+)/(.*)", source)
    if match:
        return f".agents/skills/{match.group(1)}/{match.group(2)}"
    return source


def version() -> str:
    package_version = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(SEMVER.fullmatch(package_version) is not None, f"invalid package VERSION: {package_version!r}")
    return package_version


def generated_manifest() -> Mapping[str, object]:
    sources = payload_files()
    owned = [{"source": source, "target": target_for(source)} for source in sources]
    checksum_paths = set(sources)
    checksum_paths.update(seed["source"] for seed in SEEDS)
    return {
        "schema_version": 2,
        "framework_version": version(),
        "framework_owned": owned,
        "project_seeds": list(SEEDS),
        "checksums": {relative: sha256(PAYLOAD_ROOT / relative) for relative in sorted(checksum_paths)},
        "retired_framework_owned": list(RETIRED),
    }


def refresh_manifest() -> None:
    payload_version = version() + "\n"
    (PAYLOAD_ROOT / "VERSION").write_text(payload_version, encoding="utf-8")
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(generated_manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_manifest() -> Mapping[str, object]:
    try:
        value = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read package manifest: {exc}") from exc
    require(isinstance(value, dict), "package manifest must be a JSON object")
    return value


def parse_frontmatter(path: Path) -> Mapping[str, str]:
    text = path.read_text(encoding="utf-8")
    require(text.startswith("---\n"), f"missing YAML frontmatter: {path}")
    parts = text.split("---\n", 2)
    require(len(parts) == 3, f"unterminated YAML frontmatter: {path}")
    block = parts[1]
    fields: Dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def check_structure() -> None:
    required = [
        PACKAGE_ROOT / "SKILL.md",
        PACKAGE_ROOT / "VERSION",
        PACKAGE_ROOT / "scripts" / "adopt.py",
        PACKAGE_ROOT / "scripts" / "bootstrap.py",
        PACKAGE_ROOT / "scripts" / "lifecycle.py",
        PACKAGE_ROOT / "scripts" / "providers.py",
        PACKAGE_ROOT / "scripts" / "verify_package.py",
        PAYLOAD_ROOT / "root" / "AGENTS.md.template",
        PAYLOAD_ROOT / "root" / "CLAUDE.md.template",
        PAYLOAD_ROOT / "VERSION",
        MANIFEST_PATH,
        PAYLOAD_ROOT / "ai-workflow" / "README.md",
        PAYLOAD_ROOT / "ai-workflow" / "providers.json",
    ]
    required.extend(PAYLOAD_ROOT / "skills" / name / "SKILL.md" for name in SKILLS)
    for path in required:
        require(path.is_file() and not path.is_symlink(), f"missing regular package file: {path.relative_to(PACKAGE_ROOT)}")
    package_fields = parse_frontmatter(PACKAGE_ROOT / "SKILL.md")
    require(package_fields.get("name") == "agentic-workflow", "bootstrap skill name must be agentic-workflow")
    for name in SKILLS:
        path = PAYLOAD_ROOT / "skills" / name / "SKILL.md"
        fields = parse_frontmatter(path)
        require(fields.get("name") == name, f"skill name does not match directory: {name}")
        require(bool(fields.get("description")), f"skill lacks description: {name}")


def check_filesystem_entries() -> None:
    for path in PACKAGE_ROOT.rglob("*"):
        relative = path.relative_to(PACKAGE_ROOT).as_posix()
        require(not path.is_symlink(), f"package must not contain symlinks: {relative}")
        if path.is_dir():
            reviewed_filesystem_mode(path, expected=0o755)
        elif path.is_file():
            expected = 0o755 if relative in EXECUTABLE_PACKAGE_PATHS else 0o644
            reviewed_filesystem_mode(path, expected=expected)
        else:
            raise VerificationError(f"package contains a special filesystem entry: {relative}")


def check_manifest() -> None:
    payload_version = (PAYLOAD_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(payload_version == version(), "payload VERSION must equal package VERSION")
    actual = load_manifest()
    expected = generated_manifest()
    require(actual == expected, "manifest/version/checksums drifted; run verify_package.py --refresh-manifest")
    mappings = actual["framework_owned"]  # type: ignore[index]
    require(isinstance(mappings, list), "framework_owned must be an array")
    targets = []
    for item in mappings:
        require(isinstance(item, dict) and set(item) == {"source", "target"}, "framework_owned entries need source and target")
        source = safe_relative(item["source"])
        target = safe_relative(item["target"])
        require((PAYLOAD_ROOT / source).is_file(), f"manifest-owned source is missing: {source}")
        require(
            not target.parts or target.parts[0] != "docs",
            f"framework-owned content must not install into the generic docs namespace: {target}",
        )
        targets.append(target)
    require(len(targets) == len(set(targets)), "framework_owned target paths must be unique")
    seeds = actual["project_seeds"]  # type: ignore[index]
    require(isinstance(seeds, list), "project_seeds must be an array")
    for item in seeds:
        require(isinstance(item, dict) and set(item) == {"source", "target"}, "project_seeds entries need source and target")
        target = safe_relative(item["target"])
        require(
            not target.parts or target.parts[0] != "docs",
            f"framework project seeds must not install into the generic docs namespace: {target}",
        )


def check_inert_payload() -> None:
    allowed_package_entries = {"SKILL.md", "VERSION", "examples", "payload", "scripts", "tests"}
    require({path.name for path in PACKAGE_ROOT.iterdir()} <= allowed_package_entries, "package root contains an unexpected entry")
    allowed_payload_entries = {"VERSION", "ai-workflow", "distribution", "root", "skills"}
    require({path.name for path in PAYLOAD_ROOT.iterdir()} == allowed_payload_entries, "payload top-level entries drifted")
    require(not (PAYLOAD_ROOT / "AGENTS.md").exists(), "payload must not contain an active root AGENTS.md")
    require(not (PAYLOAD_ROOT / "CLAUDE.md").exists(), "payload must not contain an active root CLAUDE.md")
    require(not (PAYLOAD_ROOT / ".agents").exists(), "payload must not contain an active .agents tree")
    require(not (PAYLOAD_ROOT / ".github").exists(), "payload must not contain an active .github customization tree")
    nested_agents = [path for path in PAYLOAD_ROOT.rglob("AGENTS.md")]
    require(not nested_agents, "payload contains an active AGENTS.md instead of an inert template")
    nested_claude = [path for path in PAYLOAD_ROOT.rglob("CLAUDE.md")]
    require(not nested_claude, "payload contains an active CLAUDE.md instead of an inert template")
    symlinks = [path.relative_to(PACKAGE_ROOT).as_posix() for path in PACKAGE_ROOT.rglob("*") if path.is_symlink()]
    require(not symlinks, "package must not contain symlinks: " + ", ".join(symlinks))


def check_workflow_contract() -> None:
    policy = (PAYLOAD_ROOT / "root" / "AGENTS.md.template").read_text(encoding="utf-8")
    require(len(policy.encode("utf-8")) < 5000, "installed root policy exceeds the compact v0 budget")
    for name in SKILLS:
        require(name in policy, f"root policy does not route to {name}")
    for provider in ("wayfinder", "teach", "research", "to-spec", "to-tickets", "implement", "tdd", "code-review"):
        require(provider in policy, f"root policy does not route or compose upstream {provider}")
    catalog_path = PACKAGE_ROOT / "tests" / "acceptance-scenarios.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read acceptance catalog: {exc}") from exc
    require(isinstance(catalog, list) and len(catalog) == 32, "acceptance catalog must contain 32 core scenarios")
    require([item.get("id") for item in catalog if isinstance(item, dict)] == list(range(1, 33)), "acceptance scenario IDs must be sequential")
    required = {"id", "requirement", "prompt", "setup", "expected_route", "expected_behavior", "evidence"}
    for item in catalog:
        require(isinstance(item, dict) and set(item) == required, "acceptance scenario fields drifted")
        require(all(str(item[field]).strip() for field in required - {"id"}), f"acceptance scenario {item.get('id')} has an empty field")
    routes = " ".join(str(item["expected_route"]) for item in catalog)
    for route in ("normal", "teach", "discovery", "debugging", "to-tickets", "implementation", "verification", "code-review"):
        require(route in routes, f"acceptance catalog lacks the {route} route")

    route_instruction = re.search(
        r"Append `\[route: router → …\]`.*?(?=\n\n)",
        policy,
        re.DOTALL,
    )
    require(route_instruction is not None, "root policy lacks the compact route-output format")
    route_instruction_text = " ".join(route_instruction.group(0).split())
    require(len(route_instruction.group(0).encode("utf-8")) <= 300, "always-on route instruction exceeds 300 bytes")
    require(len(route_instruction_text.split()) <= 40, "always-on route instruction exceeds 40 words")
    require("effective workflow stages already used" in route_instruction_text, "route output does not distinguish effective use")
    require("Explain routing only when requested" in route_instruction_text, "route output could add an unsolicited explanation")
    require("never reassess it" in route_instruction_text, "route output could trigger another routing pass")
    require("load skills, run workflows, or write state to produce" in route_instruction_text, "route output could trigger extra execution")
    for skill_path in (PAYLOAD_ROOT / "skills").glob("*/SKILL.md"):
        require("[route: router" not in skill_path.read_text(encoding="utf-8"), f"route contract is duplicated in {skill_path}")

    try:
        route_scenarios = json.loads(ROUTE_SCENARIOS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read route observability catalog: {exc}") from exc
    require(isinstance(route_scenarios, list) and len(route_scenarios) == 5, "route observability catalog must contain five scenarios")
    route_required = {"id", "requirement", "prompt", "setup", "expected_route_output", "expected_behavior"}
    require(
        [item.get("id") for item in route_scenarios if isinstance(item, dict)]
        == ["wayfinder", "implementation", "multi-stage", "effective-only", "no-trigger"],
        "route observability scenario IDs drifted",
    )
    route_line = re.compile(r"^\[route: router(?: → [a-z][a-z0-9-]*)+\]$")
    for item in route_scenarios:
        require(
            isinstance(item, dict) and set(item) == route_required,
            "route observability scenario fields drifted",
        )
        require(
            all(str(item[field]).strip() for field in route_required),
            f"route observability scenario {item.get('id')} has an empty field",
        )
        output = str(item["expected_route_output"])
        require(route_line.fullmatch(output) is not None, f"invalid route output: {output}")
        require(len(output) <= 120, f"route output exceeds compact budget: {output}")
        require(output.count(" → ") <= 5, f"route output exceeds five compact labels: {output}")

    outputs = {item["id"]: item["expected_route_output"] for item in route_scenarios}
    require(outputs["wayfinder"] == "[route: router → wayfinder]", "Wayfinder output contract drifted")
    require(
        outputs["implementation"] == "[route: router → implement → verification]",
        "Implementation output contract drifted",
    )
    require(outputs["multi-stage"].count(" → ") >= 4, "multi-stage output must report each effective stage")
    require(outputs["effective-only"] == "[route: router → teach]", "effective-only output must exclude unselected skills")
    require(outputs["no-trigger"] == "[route: router → direct]", "observability-only handling must remain direct")


def check_provider_contract() -> None:
    try:
        declaration = json.loads(PROVIDERS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read provider declaration: {exc}") from exc
    require(
        isinstance(declaration, dict)
        and set(declaration) == {"schema_version", "capabilities", "provider"}
        and declaration.get("schema_version") == 1,
        "provider declaration has unknown fields or an unsupported schema",
    )
    require(
        declaration.get("capabilities") == PROVIDER_CAPABILITIES,
        "provider capability routing drifted from the curated set",
    )
    provider = declaration.get("provider")
    require(isinstance(provider, dict), "provider declaration needs a provider object")
    require(
        set(provider) == {"minimum_gh_version", "name", "repository", "revision", "skills", "version"},
        "provider declaration fields drifted",
    )
    require(provider.get("repository") == PROVIDER_REPOSITORY, "provider repository drifted")
    require(provider.get("version") == PROVIDER_VERSION, "provider tag drifted")
    require(provider.get("revision") == PROVIDER_REVISION, "provider immutable revision drifted")
    require(provider.get("name") == "matt-pocock-skills", "provider name drifted")
    minimum = provider.get("minimum_gh_version")
    require(
        isinstance(minimum, str) and SEMVER.fullmatch(minimum) is not None,
        "provider minimum GitHub CLI version must be semantic",
    )
    require(
        tuple(int(part) for part in minimum.split(".")) >= (2, 90, 0),
        "provider minimum GitHub CLI version predates gh skill",
    )
    skills = provider.get("skills")
    require(isinstance(skills, list), "provider skills must be an array")
    names = set()
    paths = set()
    for item in skills:
        require(
            isinstance(item, dict) and set(item) == {"files", "name", "path", "tree_sha"},
            "provider skill entries need files, name, path, and tree_sha",
        )
        name = item.get("name")
        path = item.get("path")
        tree_sha = item.get("tree_sha")
        files = item.get("files")
        require(isinstance(name, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is not None, f"invalid provider skill name: {name!r}")
        require(isinstance(path, str), f"provider path for {name} must be a string")
        safe_relative(path)
        require(path.startswith("skills/"), f"provider skill path must select an upstream skill directory: {path}")
        require(isinstance(tree_sha, str) and re.fullmatch(r"[0-9a-f]{40}", tree_sha) is not None, f"invalid tree SHA for provider skill {name}")
        require(isinstance(files, list) and "SKILL.md" in files, f"provider skill {name} lacks a complete file inventory")
        checked_files = []
        for raw in files:
            require(isinstance(raw, str), f"provider skill {name} has a non-string file path")
            checked_files.append(safe_relative(raw).as_posix())
        require(checked_files == sorted(set(checked_files)), f"provider skill {name} file inventory must be sorted and unique")
        require(name not in names and path not in paths, f"duplicate provider skill name or path: {name}")
        names.add(name)
        paths.add(path)
    require(names == PROVIDER_SKILLS, "provider curated skill set drifted")
    require(
        names.isdisjoint(SKILLS),
        "local workflow skills must not duplicate curated upstream skill names",
    )
    require(
        all(value in names for value in PROVIDER_CAPABILITIES.values()),
        "a provider capability selects a missing skill",
    )
    implementation = (PAYLOAD_ROOT / "skills" / "workflow-implementation" / "SKILL.md").read_text(encoding="utf-8")
    require(
        "owns the build loop, its appropriate use of\n`tdd`, and its closing `code-review`" in implementation,
        "local implementation adapter must delegate upstream TDD and code review without duplicating them",
    )


def check_wayfinder_ownership_contract() -> None:
    policy = (PAYLOAD_ROOT / "root" / "AGENTS.md.template").read_text(encoding="utf-8")
    guide = (PAYLOAD_ROOT / "ai-workflow" / "README.md").read_text(encoding="utf-8")
    state = (PAYLOAD_ROOT / "ai-workflow" / "state" / "README.md").read_text(encoding="utf-8")
    discovery = (
        PAYLOAD_ROOT / "skills" / "workflow-discovery" / "SKILL.md"
    ).read_text(encoding="utf-8")
    normalized_guide = " ".join(guide.split())
    normalized_state = " ".join(state.split())
    normalized_discovery = " ".join(discovery.split())

    native_terms = (
        "tracker issue ID or URL",
        "linked issue title",
        "wayfinder:map",
        "wayfinder:research",
        "wayfinder:prototype",
        "wayfinder:grilling",
        "wayfinder:task",
        "Destination",
        "Decisions so far",
        "Not yet specified",
        "Out of scope",
    )
    for term in native_terms:
        require(term in normalized_guide, f"Wayfinder legend lacks canonical term: {term}")

    for term in ("issue IDs", "URLs", "linked titles", "`wayfinder:*` labels"):
        require(term in normalized_discovery, f"Discovery lacks Wayfinder pass-through term: {term}")
    require(
        "Do not allocate `DEC`, `TKT`, `UNK`, or another framework alias" in normalized_discovery,
        "Discovery does not prohibit framework aliases for Wayfinder state",
    )
    require(
        "never wrap or replace an identifier owned by Wayfinder" in normalized_state,
        "state allocator is not scoped away from Wayfinder-owned identifiers",
    )
    require("Jira key such as `ARC-384`" in state, "state contract lacks external Jira identity example")
    require("GitHub issue such as `#384`" in state, "state contract lacks external GitHub identity example")
    for prefix in ("DEC-NNNN", "IMP-NNNN", "DBG-NNNN", "IDP-NNNN"):
        require(prefix in state, f"distinct framework identifier was lost: {prefix}")

    detailed_terms = ("wayfinder:map", "wayfinder:research", "wayfinder:prototype", "wayfinder:grilling", "wayfinder:task")
    for term in detailed_terms:
        require(term not in policy, f"detailed Wayfinder taxonomy leaked into always-on root policy: {term}")

    package_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in PACKAGE_ROOT.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml"}
    )
    for pattern in (r"\bT\s*(?:→|->)\s*TKT\b", r"\bU\s*(?:→|->)\s*UNK\b"):
        require(re.search(pattern, package_text) is None, "Wayfinder-to-framework translation mapping is forbidden")

    catalog = json.loads(
        (PACKAGE_ROOT / "tests" / "acceptance-scenarios.json").read_text(encoding="utf-8")
    )
    scenario = next(item for item in catalog if item.get("id") == 19)
    scenario_text = " ".join(str(scenario[field]) for field in scenario if field != "id")
    for term in ("ARC-384", "#384", "DEC", "TKT", "UNK", "unchanged origin and return target"):
        require(term in scenario_text, f"Wayfinder acceptance coverage lacks: {term}")


def check_no_external_runtime() -> None:
    forbidden_paths = []
    forbidden_text = []
    allowed_metadata = {Path(__file__).resolve(), MANIFEST_PATH.resolve()}
    for path in PACKAGE_ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(PACKAGE_ROOT).as_posix()
        if "hermes" in relative.lower():
            forbidden_paths.append(relative)
        if path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8")
            if "hermes" in text.lower() and path.resolve() not in allowed_metadata:
                forbidden_text.append(relative)
    require(not forbidden_paths, "forbidden external-runtime paths packaged: " + ", ".join(forbidden_paths))
    require(not forbidden_text, "forbidden external-runtime references packaged: " + ", ".join(forbidden_text))


def check_markdown_links() -> None:
    pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    failures = []
    for path in PACKAGE_ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for raw in pattern.findall(text):
            target = raw.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:") or target.startswith("/"):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(PACKAGE_ROOT.resolve())
            except ValueError:
                failures.append(f"{path.relative_to(PACKAGE_ROOT)} -> {raw} (escapes package)")
                continue
            if not resolved.exists():
                failures.append(f"{path.relative_to(PACKAGE_ROOT)} -> {raw}")
    require(not failures, "broken package Markdown links: " + "; ".join(failures))


def check_installed_skill_references() -> None:
    manifest = load_manifest()
    mappings = manifest["framework_owned"]
    seeds = manifest["project_seeds"]
    available = {
        item["target"]
        for item in [*mappings, *seeds]  # type: ignore[misc]
        if isinstance(item, dict) and isinstance(item.get("target"), str)
    }
    pattern = re.compile(r"`((?:ai-workflow|docs)/[^`\n]*\.md)`")
    failures = []
    for path in (PAYLOAD_ROOT / "skills").rglob("SKILL.md"):
        for reference in pattern.findall(path.read_text(encoding="utf-8")):
            if "<" in reference or ">" in reference:
                continue
            if reference not in available:
                failures.append(f"{path.relative_to(PAYLOAD_ROOT)} -> {reference}")
    require(not failures, "unresolved installed skill references: " + "; ".join(failures))


def run_tests() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(PACKAGE_ROOT / "tests"), "-p", "test_*.py", "-v"],
        cwd=PACKAGE_ROOT,
    )
    require(result.returncode == 0, "package lifecycle tests failed")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-manifest", action="store_true", help="derive payload metadata from package VERSION and files")
    parser.add_argument("--tests", action="store_true", help="also run lifecycle integration tests")
    return parser.parse_args(argv)


def main(argv: Iterable[str] = ()) -> int:
    args = parse_args(list(argv))
    if args.refresh_manifest:
        refresh_manifest()
    checks = (
        check_structure,
        check_filesystem_entries,
        check_manifest,
        check_inert_payload,
        check_workflow_contract,
        check_provider_contract,
        check_wayfinder_ownership_contract,
        check_no_external_runtime,
        check_markdown_links,
        check_installed_skill_references,
    )
    for check in checks:
        check()
        print(f"OK: {check.__name__}")
    if args.tests:
        run_tests()
        print("OK: lifecycle integration tests")
    print("OK: distributable package is internally consistent.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except VerificationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
