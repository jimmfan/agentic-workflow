#!/usr/bin/env python3
"""Validate the self-contained Agentic Workflow distribution package."""

from __future__ import annotations

import argparse
import ast
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
DECISION_SCENARIOS_PATH = PACKAGE_ROOT / "tests" / "decision-contract-scenarios.json"
PROVIDERS_PATH = PAYLOAD_ROOT / "ai-workflow" / "providers.json"
OBSERVABILITY_ANALYZER = PAYLOAD_ROOT / "ai-workflow" / "observability" / "analyze.py"
OBSERVABILITY_GUIDE = PAYLOAD_ROOT / "ai-workflow" / "observability" / "README.md"
SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
SKILLS = (
    "workflow-debugging",
    "workflow-discovery",
    "workflow-implementation",
    "workflow-verification",
)
DISTRIBUTION_MANIFEST_SCHEMA = 5
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
MINIMUM_PYTHON = (3, 11)
CANONICAL_FRAMEWORK_REPOSITORY = "jimmfan/agentic-workflow"
LEGACY_FRAMEWORK_REPOSITORY = "jimmfan/agentic-workflow-instructions"
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
PROVIDER_HOSTS = {
    "claude-code": {
        "availability": "unavailable",
        "discovery": ".claude/skills",
        "explicit_prefix": "/",
        "invocation_source": "SKILL.md:disable-model-invocation",
    },
    "codex": {
        "availability": "available",
        "discovery": ".agents/skills",
        "explicit_prefix": "$",
        "invocation_source": "agents/openai.yaml:policy.allow_implicit_invocation",
    },
    "github-copilot": {
        "availability": "available",
        "discovery": ".agents/skills",
        "explicit_prefix": "/",
        "invocation_source": "SKILL.md:disable-model-invocation",
    },
}
PROVIDER_CONFIGURATION = {
    "domain": {
        "path": "docs/agents/domain.md",
        "provisioned_by": "setup-matt-pocock-skills",
    },
    "issue-tracker": {
        "path": "docs/agents/issue-tracker.md",
        "provisioned_by": "setup-matt-pocock-skills",
    },
    "triage-labels": {
        "enabled_by": "triage",
        "path": "docs/agents/triage-labels.md",
        "provisioned_by": "setup-matt-pocock-skills",
    },
}
USER_ONLY_PROVIDER_SKILLS = {
    "setup-matt-pocock-skills",
    "wayfinder",
    "teach",
    "to-spec",
    "to-tickets",
    "implement",
    "triage",
}
PROVIDER_REQUIREMENTS = {
    "setup-matt-pocock-skills": [],
    "wayfinder": ["domain", "issue-tracker"],
    "teach": [],
    "research": [],
    "to-spec": ["domain", "issue-tracker", "triage-labels"],
    "to-tickets": ["domain", "issue-tracker", "triage-labels"],
    "implement": ["issue-tracker"],
    "tdd": [],
    "code-review": ["issue-tracker"],
    "grilling": [],
    "domain-modeling": [],
    "prototype": [],
    "codebase-design": [],
    "triage": ["domain", "issue-tracker", "triage-labels"],
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
    "triage",
}


class VerificationError(RuntimeError):
    """A package invariant failed."""


def require_supported_python() -> None:
    if sys.version_info < MINIMUM_PYTHON:
        found = ".".join(str(part) for part in sys.version_info[:3])
        raise VerificationError(f"Python 3.11 or newer is required; found Python {found}")


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
    if source == "hosts/vscode-agentic-workflow.json":
        return ".github/hooks/agentic-workflow.json"
    match = re.fullmatch(r"skills/([^/]+)/(.*)", source)
    if match:
        return f".agents/skills/{match.group(1)}/{match.group(2)}"
    if source == "ai-workflow" or source.startswith("ai-workflow/"):
        return "." + source
    return source


def version() -> str:
    package_version = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(SEMVER.fullmatch(package_version) is not None, f"invalid package VERSION: {package_version!r}")
    return package_version


def generated_manifest() -> Mapping[str, object]:
    sources = payload_files()
    owned = [{"source": source, "target": target_for(source)} for source in sources]
    return {
        "schema_version": DISTRIBUTION_MANIFEST_SCHEMA,
        "framework_version": version(),
        "framework_owned": owned,
        "checksums": {relative: sha256(PAYLOAD_ROOT / relative) for relative in sources},
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
        PAYLOAD_ROOT / "ai-workflow" / "routing.md",
        PAYLOAD_ROOT / "ai-workflow" / "providers.json",
        PAYLOAD_ROOT / "ai-workflow" / "runtime" / "controller.py",
        PAYLOAD_ROOT / "ai-workflow" / "runtime" / "capabilities.json",
        PAYLOAD_ROOT / "ai-workflow" / "runtime" / "README.md",
        PAYLOAD_ROOT / "hosts" / "vscode-agentic-workflow.json",
        OBSERVABILITY_ANALYZER,
        OBSERVABILITY_GUIDE,
        DECISION_SCENARIOS_PATH,
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


def check_repository_identity_contract() -> None:
    bootstrap = PACKAGE_ROOT / "scripts" / "bootstrap.py"
    tree = ast.parse(bootstrap.read_text(encoding="utf-8"), filename=str(bootstrap))
    assignments = {
        target.id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and target.id == "REPOSITORY"
    }
    require(
        assignments.get("REPOSITORY") == CANONICAL_FRAMEWORK_REPOSITORY,
        "bootstrap repository identity drifted from jimmfan/agentic-workflow",
    )

    repository_root = PACKAGE_ROOT.parent.parent
    source_layout_package = repository_root / "skills" / "agentic-workflow"
    if source_layout_package.exists() and source_layout_package.resolve() == PACKAGE_ROOT.resolve():
        root_readme = (repository_root / "README.md").read_text(encoding="utf-8")
        require(
            LEGACY_FRAMEWORK_REPOSITORY not in root_readme,
            "root README still references the legacy GitHub repository slug",
        )
        canonical_bootstrap = (
            "https://raw.githubusercontent.com/"
            f"{CANONICAL_FRAMEWORK_REPOSITORY}/main/skills/agentic-workflow/scripts/bootstrap.py"
        )
        require(
            canonical_bootstrap in root_readme,
            "root README lacks the canonical public bootstrap URL",
        )


def check_python_runtime_contract() -> None:
    entry_points = [
        PACKAGE_ROOT / "scripts" / "adopt.py",
        PACKAGE_ROOT / "scripts" / "bootstrap.py",
        PACKAGE_ROOT / "scripts" / "lifecycle.py",
        PACKAGE_ROOT / "scripts" / "providers.py",
        PACKAGE_ROOT / "scripts" / "verify_package.py",
        PAYLOAD_ROOT / "ai-workflow" / "runtime" / "controller.py",
        OBSERVABILITY_ANALYZER,
    ]
    for path in entry_points:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        assignments = {
            target.id: ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name) and target.id == "MINIMUM_PYTHON"
        }
        require(
            assignments.get("MINIMUM_PYTHON") == MINIMUM_PYTHON,
            f"entry point must declare Python {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]} minimum: {path}",
        )
        main = next(
            (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"),
            None,
        )
        first_statement = main.body[0] if main is not None and main.body else None
        require(
            isinstance(first_statement, ast.Expr)
            and isinstance(first_statement.value, ast.Call)
            and isinstance(first_statement.value.func, ast.Name)
            and first_statement.value.func.id == "require_supported_python",
            f"entry point must check Python before other work: {path}",
        )


def check_prerequisite_documentation_contract() -> None:
    declaration = json.loads(PROVIDERS_PATH.read_text(encoding="utf-8"))
    provider = declaration.get("provider")
    require(isinstance(provider, dict), "provider declaration needs a provider object")
    gh_minimum = provider.get("minimum_gh_version")
    require(
        isinstance(gh_minimum, str) and SEMVER.fullmatch(gh_minimum) is not None,
        "provider minimum GitHub CLI version must be semantic",
    )
    python_minimum = f"{MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]}"
    current_contracts = [
        PACKAGE_ROOT / "SKILL.md",
        PAYLOAD_ROOT / "ai-workflow" / "README.md",
    ]
    repository_root = PACKAGE_ROOT.parent.parent
    source_layout_package = repository_root / "skills" / "agentic-workflow"
    in_source_checkout = (
        source_layout_package.exists()
        and source_layout_package.resolve() == PACKAGE_ROOT.resolve()
    )
    if in_source_checkout:
        current_contracts.extend(
            (repository_root / "README.md", repository_root / "docs" / "verification.md")
        )
    python_pattern = re.compile(r"Python\s+3\.(\d+)(?:\+|\s+or newer)", re.IGNORECASE)
    gh_pattern = re.compile(r"GitHub CLI\s+(\d+\.\d+\.\d+)(?:\+|\s+or newer)", re.IGNORECASE)
    for path in current_contracts:
        text = path.read_text(encoding="utf-8")
        python_versions = {f"3.{match}" for match in python_pattern.findall(text)}
        require(
            not python_versions or python_versions == {python_minimum},
            f"documented Python minimum drifted in {path.relative_to(repository_root)}: "
            + ", ".join(sorted(python_versions)),
        )
        gh_versions = set(gh_pattern.findall(text))
        require(
            not gh_versions or gh_versions == {gh_minimum},
            f"documented GitHub CLI minimum drifted in {path.relative_to(repository_root)}: "
            + ", ".join(sorted(gh_versions)),
        )
    package_skill = (PACKAGE_ROOT / "SKILL.md").read_text(encoding="utf-8")
    installed_readme = (PAYLOAD_ROOT / "ai-workflow" / "README.md").read_text(encoding="utf-8")
    require(
        f"Python {python_minimum}" in package_skill
        and f"GitHub CLI {gh_minimum}" in package_skill,
        "package skill must state the enforced Python and GitHub CLI minimums",
    )
    require(
        f"Python {python_minimum}" in installed_readme
        and f"GitHub CLI {gh_minimum}" in installed_readme,
        "installed README must state the enforced Python and GitHub CLI minimums",
    )
    if in_source_checkout:
        root_readme = (repository_root / "README.md").read_text(encoding="utf-8")
        require(
            f"Python {python_minimum}+" in root_readme
            and f"GitHub CLI {gh_minimum}" in root_readme,
            "root README must state the enforced Python and GitHub CLI minimums",
        )


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
    require(
        all(not target.parts or target.parts[0] != ".ai-workflow-state" for target in targets),
        "framework-owned files must not be installed into durable project state",
    )
    require(
        "project_seeds" not in actual,
        "distribution manifest must not declare lifecycle-created project state",
    )


def check_inert_payload() -> None:
    allowed_package_entries = {"SKILL.md", "VERSION", "examples", "payload", "scripts", "tests"}
    require({path.name for path in PACKAGE_ROOT.iterdir()} <= allowed_package_entries, "package root contains an unexpected entry")
    allowed_payload_entries = {"VERSION", "ai-workflow", "distribution", "hosts", "root", "skills"}
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


def check_enforcement_contract() -> None:
    controller = PAYLOAD_ROOT / "ai-workflow" / "runtime" / "controller.py"
    capabilities_path = PAYLOAD_ROOT / "ai-workflow" / "runtime" / "capabilities.json"
    hook_path = PAYLOAD_ROOT / "hosts" / "vscode-agentic-workflow.json"
    adapters = (
        PAYLOAD_ROOT / "ai-workflow" / "runtime" / "adapters" / "codex-hooks.example.json",
        PAYLOAD_ROOT / "ai-workflow" / "runtime" / "adapters" / "claude-settings.example.json",
    )
    for path in (capabilities_path, hook_path, *adapters):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise VerificationError(
                f"cannot read enforcement JSON {path.relative_to(PACKAGE_ROOT)}: {exc}"
            ) from exc
        require(isinstance(value, dict), f"enforcement JSON must be an object: {path}")

    capabilities = json.loads(capabilities_path.read_text(encoding="utf-8"))
    expected_hosts = {
        "github-copilot-vscode",
        "codex",
        "claude-code",
        "github-copilot-cli",
        "github-copilot-cloud",
    }
    require(
        set(capabilities) == {"hosts", "reference_host", "schema_version"}
        and capabilities["schema_version"] == 1,
        "enforcement capability document has an unsupported schema",
    )
    hosts = capabilities["hosts"]
    require(isinstance(hosts, dict) and set(hosts) == expected_hosts, "host enforcement matrix drifted")
    require(
        capabilities["reference_host"] == "github-copilot-vscode"
        and hosts["github-copilot-vscode"]["adapter"] == "active"
        and hosts["github-copilot-vscode"]["lifecycle"] == "Preview",
        "VS Code Copilot must remain the Preview reference adapter",
    )
    require(
        hosts["codex"]["adapter"] == "opt-in-template"
        and hosts["claude-code"]["adapter"] == "opt-in-template"
        and hosts["github-copilot-cli"]["adapter"] == "shared-file-not-release-validated"
        and hosts["github-copilot-cloud"]["adapter"] == "shared-file-not-release-validated",
        "secondary and separate-host adapter claims drifted",
    )

    hook = json.loads(hook_path.read_text(encoding="utf-8"))
    require(
        set(hook) == {"hooks", "version"}
        and hook["version"] == 1
        and isinstance(hook["hooks"], dict),
        "VS Code hook shape drifted",
    )
    expected_events = {"SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"}
    require(set(hook["hooks"]) == expected_events, "VS Code enforcement event set drifted")
    expected_command = "python3 .ai-workflow/runtime/controller.py hook --host vscode"
    for event, entries in hook["hooks"].items():
        require(isinstance(entries, list) and len(entries) == 1, f"{event} needs one hook command")
        entry = entries[0]
        require(
            isinstance(entry, dict)
            and set(entry) == {"command", "cwd", "timeout", "type", "windows"}
            and entry["type"] == "command"
            and entry["command"] == expected_command
            and entry["cwd"] == "."
            and entry["timeout"] == 10,
            f"invalid VS Code hook command for {event}",
        )
    manifest_target = target_for("hosts/vscode-agentic-workflow.json")
    require(
        manifest_target == ".github/hooks/agentic-workflow.json",
        "VS Code hook must install at its unique active workspace path",
    )

    source = controller.read_text(encoding="utf-8")
    ast.parse(source, filename=str(controller))
    for term in (
        "checkpoint",
        "repository-write",
        "provider_outcomes",
        "durable_grant",
        "verification",
        "stop_hook_active",
        "tempfile.gettempdir()",
    ):
        require(term in source, f"controller contract lacks {term!r}")
    policy = (PAYLOAD_ROOT / "root" / "AGENTS.md.template").read_text(encoding="utf-8")
    require(
        ".ai-workflow/runtime/README.md" in policy
        and "when hooks do not run" in policy,
        "installed policy lacks the runtime pointer and degraded-mode contract",
    )


def check_workflow_contract() -> None:
    policy = (PAYLOAD_ROOT / "root" / "AGENTS.md.template").read_text(encoding="utf-8")
    routing = (PAYLOAD_ROOT / "ai-workflow" / "routing.md").read_text(encoding="utf-8")
    normalized_policy = " ".join(policy.split())
    normalized_routing = " ".join(routing.split())
    require(len(policy.encode("utf-8")) < 3200, "installed root policy exceeds the orchestration-kernel budget")
    for name in SKILLS:
        require(name in routing, f"progressive routing contract does not route to {name}")
    require(
        "`workflow-discovery`, `workflow-debugging`, `workflow-implementation`, and "
        "`workflow-verification` become `discovery`, `debugging`, `implement`, and "
        "`verification`."
        in normalized_routing,
        "progressive routing contract does not define stable compact local labels",
    )
    for provider in ("wayfinder", "teach", "research", "to-spec", "to-tickets", "implement", "tdd", "code-review"):
        require(provider in routing, f"progressive routing contract does not route or compose upstream {provider}")
    for detailed_term in (
        "wayfinder",
        "setup-matt-pocock-skills",
        "Claude Code",
        "Copilot CLI",
        "code-review",
        "active.md",
    ):
        require(
            detailed_term not in policy,
            f"root orchestration kernel duplicates conditional detail: {detailed_term}",
        )
    catalog_path = PACKAGE_ROOT / "tests" / "acceptance-scenarios.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read acceptance catalog: {exc}") from exc
    require(isinstance(catalog, list) and catalog, "acceptance catalog must contain core scenarios")
    ids = [item.get("id") for item in catalog if isinstance(item, dict)]
    require(
        ids == list(range(1, len(catalog) + 1)),
        "acceptance scenario IDs must be sequential",
    )
    required = {"id", "requirement", "prompt", "setup", "expected_route", "expected_behavior", "evidence"}
    for item in catalog:
        require(isinstance(item, dict) and set(item) == required, "acceptance scenario fields drifted")
        require(all(str(item[field]).strip() for field in required - {"id"}), f"acceptance scenario {item.get('id')} has an empty field")
    routes = " ".join(str(item["expected_route"]) for item in catalog)
    for route in ("normal", "teach", "discovery", "debugging", "to-tickets", "implementation", "verification", "code-review"):
        require(route in routes, f"acceptance catalog lacks the {route} route")

    invariants_heading = "## Universal invariants"
    require(policy.count(invariants_heading) == 1, "root policy needs one prominent invariant section")
    require(
        policy.index(invariants_heading) < 500,
        "universal invariants are not near the beginning of the root policy",
    )
    for term in (
        "Every request MUST be evaluated through the Agentic Workflow router.",
        "`direct` is a first-class route.",
        "MUST NOT expand the authority granted by the user's request",
        "Execution and completion claims MUST be truthful",
        "Provider execution MUST NOT be simulated",
        "continue with truthful host-native capability",
        "durable state MUST be preserved",
        "Material completion claims MUST reflect actual evidence",
    ):
        require(term in normalized_policy, f"root invariant contract lacks: {term}")
    require(
        len(re.findall(r"\bMUST(?: NOT)?\b", policy)) == 6
        and not re.search(r"\b(?:ALWAYS|NEVER)\b", policy),
        "root hard requirements must remain limited to the six audited invariants",
    )
    for heading in ("## Routing defaults", "## Load only when relevant", "## Route visibility"):
        require(policy.count(heading) == 1, f"root policy needs exactly one {heading} section")
    for pointer in (
        ".ai-workflow/routing.md",
        ".ai-workflow/runtime/README.md",
        ".ai-workflow/state/README.md",
        ".ai-workflow/contracts/project-profile.md",
    ):
        require(pointer in policy, f"root policy lacks progressive-loading pointer: {pointer}")

    final_heading = "## Route visibility"
    final_contract = policy[policy.index(final_heading) :]
    final_contract_text = " ".join(final_contract.split())
    require(len(final_contract.encode("utf-8")) <= 400, "route visibility contract exceeds 400 bytes")
    require(
        policy.rstrip().endswith("do no extra work merely to produce it."),
        "route visibility is not the last root-policy section",
    )
    require(
        re.findall(r"`(\[route: router → [^`\n]+\])`", final_contract)
        == ["[route: router → <executed path>]"],
        "root route visibility must contain only the generic optional marker",
    )
    for term in (
        "may include a truthful",
        "absence is not an error",
        ".ai-workflow/routing.md",
        "no extra work merely to produce",
    ):
        require(term in final_contract_text, f"route visibility contract lacks: {term}")
    for skill_path in (PAYLOAD_ROOT / "skills").glob("*/SKILL.md"):
        require("[route: router" not in skill_path.read_text(encoding="utf-8"), f"route contract is duplicated in {skill_path}")

    try:
        route_scenarios = json.loads(ROUTE_SCENARIOS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read route observability catalog: {exc}") from exc
    require(isinstance(route_scenarios, list) and route_scenarios, "route observability catalog must contain scenarios")
    route_required = {
        "id",
        "requirement",
        "prompt",
        "setup",
        "optional_route_diagnostic",
        "expected_behavior",
    }
    required_route_ids = {
        "direct",
        "wayfinder-handoff",
        "wayfinder-research-handoff",
        "standalone-research",
        "standalone-tdd",
        "debugging",
        "user-only-handoff",
        "setup-handoff",
        "profile-readiness",
        "profile-progressive-update",
        "read-only",
        "limited-host-unavailable",
        "provider-integrity-error",
        "active-state-conflict",
    }
    require(
        required_route_ids
        <= {item.get("id") for item in route_scenarios if isinstance(item, dict)},
        "route observability scenarios lack required semantic host coverage",
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
        output = item["optional_route_diagnostic"]
        if output is not None:
            require(isinstance(output, str) and output.strip(), "route diagnostic must be text or null")
            require(route_line.fullmatch(output) is not None, f"invalid route output: {output}")
            require(len(output) <= 120, f"route output exceeds compact budget: {output}")
            require(output.count(" → ") <= 5, f"route output exceeds five compact labels: {output}")

    outputs = {item["id"]: item["optional_route_diagnostic"] for item in route_scenarios}
    require(
        outputs["wayfinder-handoff"] == "[route: router → host-native-planning]",
        "normal planning intent must permit host-native fallback",
    )
    require(
        outputs["wayfinder-research-handoff"]
        == "[route: router → host-native-planning → research]",
        "provider fallback must preserve an available supporting capability",
    )
    require(
        outputs["standalone-research"] == "[route: router → research]",
        "standalone implicitly invocable Research output drifted",
    )
    require(
        outputs["standalone-tdd"] == "[route: router → tdd → verification]",
        "standalone TDD must retain independent Verification",
    )
    require(
        outputs["limited-host-unavailable"] == "[route: router → host-native-research]",
        "unavailable-host diagnostics must show host-native fallback",
    )
    require(
        outputs["provider-integrity-error"] == "[route: router → wayfinder-blocked]",
        "provider-integrity failure output must not imply execution",
    )
    require(
        outputs["active-state-conflict"] == "[route: router → discovery-blocked]",
        "active-state conflict output must not imply execution",
    )
    require(outputs["direct"] is None, "direct work must allow omitted route diagnostics")

    try:
        decision_scenarios = json.loads(DECISION_SCENARIOS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read decision contract catalog: {exc}") from exc
    decision_required = {
        "id",
        "category",
        "prompt",
        "setup",
        "dominant_activity",
        "capabilities",
        "provider_invocations",
        "host",
        "route_result",
        "executed",
        "repository_state_effect",
        "external_scope",
        "expected_behavior",
    }
    categories_required = {
        "direct-with-missing-setup",
        "wayfinder-handoff",
        "workflow-plus-capability",
        "standalone-research",
        "standalone-debugging",
        "standalone-teach-handoff",
        "setup-required-handoff",
        "implementation-handoff",
        "read-only-discovery",
        "scoped-external-read",
        "external-mutation-denied",
        "active-state-conflict",
        "canonical-artifact-ownership",
        "limited-host-local-unavailable",
    }
    require(isinstance(decision_scenarios, list), "decision contract catalog must be an array")
    categories = set()
    for item in decision_scenarios:
        require(
            isinstance(item, dict) and set(item) == decision_required,
            "decision contract scenario fields drifted",
        )
        categories.add(item["category"])
        require(
            isinstance(item["id"], str)
            and item["id"]
            and isinstance(item["dominant_activity"], str)
            and item["dominant_activity"],
            "decision scenario identifiers and dominant activities must be non-empty strings",
        )
        require(
            isinstance(item["capabilities"], list)
            and all(isinstance(value, str) and value for value in item["capabilities"]),
            f"decision scenario {item['id']} capabilities must be an array of names",
        )
        provider_invocations = item["provider_invocations"]
        require(
            isinstance(provider_invocations, list),
            f"decision scenario {item['id']} provider_invocations must be an array",
        )
        provider_names = []
        for invocation in provider_invocations:
            require(
                isinstance(invocation, dict)
                and set(invocation) == {"executed", "invocation", "name", "policy"},
                f"decision scenario {item['id']} has invalid provider invocation fields",
            )
            require(
                isinstance(invocation["name"], str)
                and invocation["name"]
                and invocation["policy"] in {"implicit", "unavailable", "user-only"}
                and invocation["invocation"]
                in {"explicit", "implicit", "not-invoked", "unavailable", "user-only-handoff"}
                and isinstance(invocation["executed"], bool),
                f"decision scenario {item['id']} has an invalid provider invocation",
            )
            provider_names.append(invocation["name"])
            if invocation["invocation"] in {"explicit", "implicit"}:
                require(
                    invocation["executed"],
                    f"executed provider invocation must be recorded as executed: {item['id']}",
                )
            else:
                require(
                    not invocation["executed"],
                    f"unexecuted provider result cannot claim execution: {item['id']}",
                )
        require(
            len(provider_names) == len(set(provider_names)),
            f"decision scenario {item['id']} repeats a provider invocation",
        )
        require(isinstance(item["executed"], bool), f"decision scenario {item['id']} executed must be boolean")
        require(
            item["host"] in set(PROVIDER_HOSTS) | {"host-neutral"},
            f"decision scenario {item['id']} has an unknown host",
        )
        require(
            item["route_result"]
            in {
                "blocked",
                "direct",
                "executed",
                "host-native-fallback",
                "local",
                "unavailable",
                "user-only-handoff",
            },
            f"decision scenario {item['id']} has an invalid route result",
        )
        require(
            item["repository_state_effect"]
            in {"none", "authorized-write", "provider-native-artifact", "read-only", "repository-write"},
            f"decision scenario {item['id']} has an invalid repository state effect",
        )
        require(
            item["external_scope"] in {"none", "named-read", "unauthorized-mutation"},
            f"decision scenario {item['id']} has an invalid external scope",
        )
        if item["route_result"] == "user-only-handoff":
            require(not item["executed"], f"user-only handoff cannot claim execution: {item['id']}")
            require(
                item["repository_state_effect"] == "none",
                f"route selection handoff cannot write state: {item['id']}",
            )
        if item["route_result"] == "host-native-fallback":
            require(item["executed"], f"host-native fallback must continue work: {item['id']}")
            require(
                all(not invocation["executed"] for invocation in provider_invocations),
                f"host-native fallback cannot claim provider execution: {item['id']}",
            )
        if item["category"] in {"read-only-discovery", "active-state-conflict"}:
            require(
                item["repository_state_effect"] == "none",
                f"negative state scenario must preserve repository state: {item['id']}",
            )
        if item["external_scope"] == "unauthorized-mutation":
            require(
                item["executed"]
                and item["route_result"] == "direct"
                and item["repository_state_effect"] == "read-only",
                f"denied external mutation must preserve the authorized read-only route: {item['id']}",
            )
        if item["route_result"] == "executed":
            require(item["executed"], f"executed route result must execute: {item['id']}")
        if item["route_result"] in {"blocked", "unavailable"}:
            require(not item["executed"], f"blocked or unavailable workflow cannot execute: {item['id']}")
            require(
                item["repository_state_effect"] == "none",
                f"blocked or unavailable workflow cannot write state: {item['id']}",
            )
        if any(invocation["executed"] for invocation in provider_invocations):
            require(item["executed"], f"executed provider requires an executed route: {item['id']}")
    require(
        categories_required <= categories,
        "decision contract catalog lacks required semantic categories: "
        + ", ".join(sorted(categories_required - categories)),
    )
    provider_contract = json.loads(PROVIDERS_PATH.read_text(encoding="utf-8"))
    declared_skills = {
        item["name"]: item
        for item in provider_contract.get("provider", {}).get("skills", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    for item in decision_scenarios:
        for invocation in item["provider_invocations"]:
            selected = invocation["name"]
            policy = invocation["policy"]
            actual_invocation = invocation["invocation"]
            require(selected in declared_skills, f"decision scenario selects unknown provider: {selected}")
            if item["host"] == "host-neutral":
                declared_modes = {
                    declared_skills[selected].get("invocation", {}).get(host)
                    for host, contract in PROVIDER_HOSTS.items()
                    if contract["availability"] == "available"
                }
                require(
                    len(declared_modes) == 1
                    and policy == next(iter(declared_modes)),
                    f"host-neutral decision scenario {item['id']} evades or disagrees with primary-host invocation policy",
                )
            else:
                declared_invocation = declared_skills[selected].get("invocation", {}).get(item["host"])
                require(
                    policy == declared_invocation,
                    f"decision scenario {item['id']} disagrees with declared {item['host']} invocation policy",
                )
            if policy == "user-only":
                allowed_results = {"explicit", "not-invoked", "user-only-handoff"}
            elif policy == "implicit":
                allowed_results = {"explicit", "implicit"}
            else:
                allowed_results = {"unavailable"}
            require(
                actual_invocation in allowed_results,
                f"decision scenario {item['id']} has an invalid invocation for its declared policy",
            )
    composed = next(
        item for item in decision_scenarios if item["category"] == "workflow-plus-capability"
    )
    require(
        composed["provider_invocations"]
        == [
            {
                "name": "wayfinder",
                "policy": "user-only",
                "invocation": "explicit",
                "executed": True,
            },
            {
                "name": "research",
                "policy": "implicit",
                "invocation": "implicit",
                "executed": True,
            },
        ],
        "workflow-plus-capability scenario must validate each provider invocation",
    )
    standalone_research = next(
        item for item in decision_scenarios if item["category"] == "standalone-research"
    )
    require(
        standalone_research["provider_invocations"]
        == [
            {
                "name": "research",
                "policy": "implicit",
                "invocation": "explicit",
                "executed": True,
            }
        ],
        "implicit-capable provider must permit an explicit named invocation",
    )


def check_provider_contract() -> None:
    try:
        declaration = json.loads(PROVIDERS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read provider declaration: {exc}") from exc
    require(
        isinstance(declaration, dict)
        and set(declaration)
        == {"schema_version", "capabilities", "configuration", "hosts", "provider"}
        and declaration.get("schema_version") == 4,
        "provider declaration has unknown fields or an unsupported schema",
    )
    require(
        declaration.get("capabilities") == PROVIDER_CAPABILITIES,
        "provider capability routing drifted from the curated set",
    )
    require(declaration.get("hosts") == PROVIDER_HOSTS, "provider host capability declaration drifted")
    require(
        declaration.get("configuration") == PROVIDER_CONFIGURATION,
        "provider configuration dependency declaration drifted",
    )
    provider = declaration.get("provider")
    require(isinstance(provider, dict), "provider declaration needs a provider object")
    require(
        set(provider) == {"minimum_gh_version", "name", "repository", "skills", "version"},
        "provider declaration fields drifted",
    )
    require(provider.get("repository") == PROVIDER_REPOSITORY, "provider repository drifted")
    require(provider.get("version") == PROVIDER_VERSION, "provider tag drifted")
    require(provider.get("name") == "matt-pocock-skills", "provider name drifted")
    minimum = provider.get("minimum_gh_version")
    require(
        isinstance(minimum, str) and SEMVER.fullmatch(minimum) is not None,
        "provider minimum GitHub CLI version must be semantic",
    )
    require(
        tuple(int(part) for part in minimum.split(".")) >= (2, 97, 0),
        "provider minimum GitHub CLI version predates the reviewed security baseline",
    )
    skills = provider.get("skills")
    require(isinstance(skills, list), "provider skills must be an array")
    names = set()
    paths = set()
    for item in skills:
        require(
            isinstance(item, dict)
            and set(item)
            == {
                "invocation",
                "name",
                "path",
                "requires_configuration",
            },
            "provider skill entries need invocation, name, path, and requirements",
        )
        name = item.get("name")
        path = item.get("path")
        invocation = item.get("invocation")
        requirements = item.get("requires_configuration")
        require(isinstance(name, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is not None, f"invalid provider skill name: {name!r}")
        require(isinstance(path, str), f"provider path for {name} must be a string")
        safe_relative(path)
        require(path.startswith("skills/"), f"provider skill path must select an upstream skill directory: {path}")
        require(
            isinstance(invocation, dict) and set(invocation) == set(PROVIDER_HOSTS),
            f"provider skill {name} invocation must cover every declared host",
        )
        expected_invocation = "user-only" if name in USER_ONLY_PROVIDER_SKILLS else "implicit"
        require(
            invocation.get("codex") == expected_invocation
            and invocation.get("github-copilot") == expected_invocation
            and invocation.get("claude-code") == "unavailable",
            f"provider skill {name} invocation semantics drifted",
        )
        require(
            isinstance(requirements, list)
            and requirements == sorted(set(requirements))
            and all(value in PROVIDER_CONFIGURATION for value in requirements),
            f"provider skill {name} has invalid configuration requirements",
        )
        require(
            requirements == PROVIDER_REQUIREMENTS.get(name),
            f"provider skill {name} configuration requirements drifted",
        )
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
    require("triage" not in PROVIDER_CAPABILITIES.values(), "triage is a dependency, not a root-routed capability")
    by_name = {str(item["name"]): item for item in skills}
    for consumer in ("to-spec", "to-tickets"):
        require(
            "triage-labels" in by_name[consumer]["requires_configuration"],
            f"{consumer} can be installed without its triage-label vocabulary",
        )
    triage_config = PROVIDER_CONFIGURATION["triage-labels"]
    require(
        triage_config.get("enabled_by") == "triage"
        and triage_config.get("provisioned_by") == "setup-matt-pocock-skills"
        and "triage" in names,
        "triage-label configuration dependency graph is incomplete",
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


def check_observability_contract() -> None:
    try:
        tree = ast.parse(OBSERVABILITY_ANALYZER.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        raise VerificationError(f"cannot parse optional observability analyzer: {exc}") from exc
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    allowed = {
        "__future__",
        "argparse",
        "dataclasses",
        "hashlib",
        "json",
        "pathlib",
        "re",
        "statistics",
        "sys",
        "typing",
    }
    require(imports <= allowed, "optional observability analyzer must use the Python standard library only")
    analyzer = OBSERVABILITY_ANALYZER.read_text(encoding="utf-8")
    for forbidden in (
        "sqlite3",
        "subprocess",
        "urllib",
        "socket",
        ".write_text(",
        ".write_bytes(",
        "/Users/",
        "/tmp/",
        "C:\\\\",
    ):
        require(forbidden not in analyzer, f"optional observability analyzer crosses its read-only boundary: {forbidden}")
    require("1.133" not in analyzer, "observability capability detection must not use a VS Code version gate")
    require('"capabilities"' in analyzer, "observability output must report detected capabilities")
    require('decode("utf-8-sig")' in analyzer, "observability analyzer must accept a UTF-8 BOM")
    require("splitlines(keepends=True)" in analyzer, "observability analyzer must normalize platform line endings")
    guide = OBSERVABILITY_GUIDE.read_text(encoding="utf-8")
    for term in (
        "github.copilot.chat.otel.captureContent",
        "outer-invoke-fallback",
        "no skill event observed",
        "Developer: Reload Window",
        "outside all\nsource repositories",
        "VS Code 1.133.x",
        "cross-platform by design",
        "live-tested only on Apple Silicon macOS",
    ):
        require(term in guide, f"optional observability guide lacks required boundary: {term}")
    runtime = "\n".join(
        [
            (PAYLOAD_ROOT / "root" / "AGENTS.md.template").read_text(encoding="utf-8"),
            *[
                path.read_text(encoding="utf-8")
                for path in (PAYLOAD_ROOT / "skills").glob("*/SKILL.md")
            ],
        ]
    )
    require(
        "observability/analyze.py" not in runtime,
        "portable router and workflow skills must not invoke the optional analyzer",
    )


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
    available = {
        item["target"]
        for item in mappings  # type: ignore[union-attr]
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
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(PACKAGE_ROOT / "tests"), "-p", "test_*.py", "-v"],
        cwd=PACKAGE_ROOT,
        env=environment,
    )
    require(result.returncode == 0, "package lifecycle tests failed")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-manifest", action="store_true", help="derive payload metadata from package VERSION and files")
    parser.add_argument("--tests", action="store_true", help="also run lifecycle integration tests")
    return parser.parse_args(argv)


def main(argv: Iterable[str] = ()) -> int:
    require_supported_python()
    args = parse_args(list(argv))
    if args.refresh_manifest:
        refresh_manifest()
    checks = (
        check_structure,
        check_repository_identity_contract,
        check_python_runtime_contract,
        check_prerequisite_documentation_contract,
        check_filesystem_entries,
        check_manifest,
        check_inert_payload,
        check_enforcement_contract,
        check_workflow_contract,
        check_provider_contract,
        check_wayfinder_ownership_contract,
        check_observability_contract,
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
