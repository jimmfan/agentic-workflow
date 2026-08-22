#!/usr/bin/env python3
"""Strict development, CI, and release verification for Agentic Workflow."""

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
from typing import Iterable, Mapping

# Keep verification itself from creating a generated cache when it imports the
# shared provider validation module below.
sys.dont_write_bytecode = True

from provider_snapshot import SnapshotTreeError, tree_digest, validate_local_references


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = PACKAGE_ROOT.parent.parent
PAYLOAD_ROOT = PACKAGE_ROOT / "payload"
MANIFEST = PAYLOAD_ROOT / "distribution" / "manifest.json"
MINIMUM_PYTHON = (3, 11)
MANIFEST_SCHEMA = 6
SEMVER = re.compile(r"\d+\.\d+\.\d+")
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")
INVOCATION_POLICIES = frozenset({"implicit", "user-only", "unavailable"})
# Frozen at a7deffc: 682 root words plus 1,487 detailed-router words.
PRE_THIN_AMBIGUOUS_ROUTE_WORDS = 2169
PRE_THIN_DIRECT_ROOT_WORDS = 682
REVIEWED_PROVIDER = {
    "name": "matt-pocock-skills",
    "repository": "mattpocock/skills",
    "version": "v1.2.3",
    "resolved_commit": "6acc160e4e0cd062dbbbd7a1b26ae92855edf07e",
    "tag_object": "835450ef244ab7335f75d95b83e7d979eae22a6d",
    "upstream_tree": "7e0251de7d262684e5e4a326c3ef1132314b9dc2",
    "snapshot_sha256": "42d7a91dbb898c92fa81354a0aa4547e33e3adf5136c2e3ea0c5a46e74aafcbc",
    "license_sha256": "0e7ac423bf2c6e223b7c5b156f8cf72da49d748e56a1641402c31f22ad07dbb5",
}
REQUIRED_PACKAGE_FILES = (
    "SKILL.md",
    "VERSION",
    "scripts/adopt.py",
    "scripts/bootstrap.py",
    "scripts/lifecycle.py",
    "scripts/providers.py",
    "scripts/provider_snapshot.py",
    "scripts/refresh_provider_snapshot.py",
    "scripts/verify_package.py",
    "runtime-projections/wayfinder.md",
    "tests/behavior.py",
    "payload/distribution/manifest.json",
    "payload/root/AGENTS.md.template",
    "payload/root/CLAUDE.md.template",
    "payload/agent-workflow/routing.md",
    "payload/agent-workflow/providers.json",
    "payload/agent-workflow/contracts/durable-state.md",
    "payload/agent-workflow/contracts/project-profile.md",
    "payload/agent-workflow/contracts/wayfinder-state.md",
)
REMOVED_RUNTIME_PATHS = (
    PAYLOAD_ROOT / "agent-workflow" / "runtime",
    PAYLOAD_ROOT / "agent-workflow" / "observability",
    PAYLOAD_ROOT / "hosts",
)


class VerificationError(RuntimeError):
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


def safe_relative(value: str) -> PurePosixPath:
    require(bool(value) and "\\" not in value, f"unsafe manifest path: {value!r}")
    path = PurePosixPath(value)
    require(
        not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts),
        f"unsafe manifest path: {value!r}",
    )
    return path


def package_path(value: object, label: str) -> Path:
    require(isinstance(value, str), f"{label} must be a relative path")
    return PACKAGE_ROOT.joinpath(*safe_relative(value).parts)


def version() -> str:
    package_version = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(SEMVER.fullmatch(package_version) is not None, "VERSION must use x.y.z")
    return package_version


def expected_mappings() -> list[dict[str, str]]:
    mappings = [
        {"source": "root/AGENTS.md.template", "target": "AGENTS.md"},
        {"source": "root/CLAUDE.md.template", "target": "CLAUDE.md"},
    ]
    skills_root = PAYLOAD_ROOT / "skills"
    for skill in sorted(skills_root.glob("*/SKILL.md")):
        mappings.append(
            {
                "source": skill.relative_to(PAYLOAD_ROOT).as_posix(),
                "target": f".agents/skills/{skill.parent.name}/SKILL.md",
            }
        )
    workflow_root = PAYLOAD_ROOT / "agent-workflow"
    for path in sorted(workflow_root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(PAYLOAD_ROOT).as_posix()
            target = ".agent-workflow/" + path.relative_to(workflow_root).as_posix()
            mappings.append({"source": relative, "target": target})
    return sorted(mappings, key=lambda item: item["target"])


def generated_manifest() -> Mapping[str, object]:
    return {
        "schema_version": MANIFEST_SCHEMA,
        "framework_version": version(),
        "framework_owned": expected_mappings(),
    }


def refresh_manifest() -> None:
    MANIFEST.write_text(
        json.dumps(generated_manifest(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Refreshed {MANIFEST.relative_to(PACKAGE_ROOT)}")


def check_structure() -> None:
    for relative in REQUIRED_PACKAGE_FILES:
        path = PACKAGE_ROOT / relative
        require(path.is_file() and not path.is_symlink(), f"missing or unsafe package file: {relative}")
    duplicate_version = PAYLOAD_ROOT / "VERSION"
    require(
        not duplicate_version.exists() and not duplicate_version.is_symlink(),
        "payload/VERSION must remain absent; package VERSION is the single source of truth",
    )
    for path in REMOVED_RUNTIME_PATHS:
        require(
            not path.is_symlink()
            and (
                not path.exists()
                or (
                    path.is_dir()
                    and not any(child.is_file() or child.is_symlink() for child in path.rglob("*"))
                )
            ),
            f"deferred v0 subsystem remains packaged: {path}",
        )
    require(
        not (PAYLOAD_ROOT / "agent-workflow/templates/active-state.md").exists(),
        "retired active-index template remains packaged",
    )
    for retired_template in ("decision-record.md", "work-item.md"):
        require(
            not (PAYLOAD_ROOT / "agent-workflow/templates" / retired_template).exists(),
            f"retired specialist-state template remains packaged: {retired_template}",
        )
    require(not (REPOSITORY_ROOT / "docs" / "enforcement.md").exists(), "obsolete controller documentation remains")
    require(not (REPOSITORY_ROOT / "docs" / "observability.md").exists(), "obsolete observability documentation remains")


def check_manifest() -> None:
    try:
        actual = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read distribution manifest: {exc}") from exc
    require(actual == generated_manifest(), "distribution manifest is stale; run verify_package.py --refresh-manifest")
    mappings = actual["framework_owned"]
    sources: list[str] = []
    targets: list[str] = []
    for item in mappings:
        require(isinstance(item, dict) and set(item) == {"source", "target"}, "invalid manifest mapping")
        source = safe_relative(item["source"])
        target = safe_relative(item["target"])
        require(target.parts[0] != ".wayfinder", "manifest must not own durable project state")
        require(".agent-workflow/state" not in target.as_posix(), "manifest must not recreate obsolete workflow state")
        sources.append(source.as_posix())
        targets.append(target.as_posix())
    require(len(sources) == len(set(sources)), "manifest source paths are duplicated")
    require(len(targets) == len(set(targets)), "manifest target paths are duplicated")


def check_filesystem() -> None:
    for path in PACKAGE_ROOT.rglob("*"):
        # Python caches are generated, globally ignored, and absent from the
        # explicit distribution map. They must not make an otherwise valid
        # local verification fail after an ordinary focused test command.
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        require(not path.is_symlink(), f"package contains a symlink: {path.relative_to(PACKAGE_ROOT)}")
        if path.is_file():
            mode = stat.S_IMODE(path.stat().st_mode)
            if os.name != "nt":
                require(mode == 0o644, f"package file mode must be 0644: {path.relative_to(PACKAGE_ROOT)}")
    for script in PACKAGE_ROOT.rglob("*.py"):
        compile(script.read_text(encoding="utf-8"), str(script), "exec")


def check_router_contract() -> None:
    agents = (PAYLOAD_ROOT / "root" / "AGENTS.md.template").read_text(encoding="utf-8")
    routing = (PAYLOAD_ROOT / "agent-workflow" / "routing.md").read_text(encoding="utf-8")
    durable = (PAYLOAD_ROOT / "agent-workflow" / "contracts" / "durable-state.md").read_text(encoding="utf-8")
    wayfinder = (PAYLOAD_ROOT / "agent-workflow" / "contracts" / "wayfinder-state.md").read_text(encoding="utf-8")
    normalized_agents = " ".join(agents.split())
    normalized_routing = " ".join(routing.split())
    normalized_durable = " ".join(durable.split())
    require("MUST route every request" in agents, "root policy lacks mandatory routing")
    require("`direct`" in agents and "minimum useful process" in routing, "router lacks the minimum/direct contract")
    require("MUST NOT" in agents and "authority" in agents, "root policy lacks the authorization boundary")
    for required in (
        "Direct is default",
        "encountering the topic alone never forces a specialist",
        "one obvious specialist inside an already selected Wayfinder effort",
        "Read `.agent-workflow/routing.md` only when",
        "never selection by count alone",
        "any hard signal or at least two soft signals",
        "Read-only work changes no state",
        "only before current project-state writes",
    ):
        require(required in normalized_agents, f"thin root router lacks required boundary: {required}")
    require(
        len(agents.split()) <= PRE_THIN_AMBIGUOUS_ROUTE_WORDS // 5,
        "thin root router exceeds the prior ambiguity-gate context budget",
    )
    require(
        len(agents.split()) <= PRE_THIN_DIRECT_ROOT_WORDS * 65 // 100,
        "thin root router reduces confidently Direct context by less than 35%",
    )
    require(
        "avoid routing loops" in normalized_routing.lower()
        and "according to the coordination threshold" in normalized_routing.lower(),
        "detailed router lacks conditional specialist transitions",
    )
    require(".wayfinder/" in durable, "durable-state contract lacks the canonical state root")
    require("no global active index" in durable, "durable-state contract retains a global active index")
    require(
        "Wayfinder is the sole framework-owned durable coordination layer" in normalized_durable,
        "durable-state contract lacks sole-coordinator ownership",
    )
    require(
        "never delete, migrate, rewrite, validate, allocate from, resume, or normalize them" in normalized_durable,
        "durable-state contract lacks legacy record preservation",
    )
    require("wayfinder-state.md" in agents and "unrelated map" in agents, "root policy lacks Wayfinder loading guidance")
    normalized_wayfinder = " ".join(wayfinder.split())
    for required in (
        "unknowns/",
        "evidence/",
        "facts/",
        "decisions/",
        "`map.md` alone is a complete and valid Wayfinder effort",
        "Do not read every",
        "Do not create or update `.wayfinder/active.md`",
        "Facts must link",
        "reciprocal backlinks",
        "mark the F# `disputed`",
        "review dependent decisions",
        "does not duplicate those work items in Wayfinder",
        "Use `to-tickets` only when clear work benefits from dependency ordering",
        "exact contents already exist in Git",
        "never leave a dangling current link",
        "A retired number is not reserved",
        ".wayfinder-mutation-lock/",
        "never allow two current records",
        "effort-local current-state shorthand",
        "canonical filesystem path",
        "outside the selected effort needs a reference",
        "Do not scan the repository or Git history",
        "## Specialist result boundary",
        "continue directly or load one materially useful specialist",
        "No DEC, IMP, DBG, or replacement record is allocated",
    ):
        require(
            required in normalized_wayfinder,
            f"Wayfinder state contract lacks required boundary: {required}",
        )
    combined = agents + routing + durable + wayfinder
    require(
        "runtime/README.md" not in combined and ".agent-workflow/runtime" not in combined,
        "router still depends on the removed controller payload",
    )


def check_provider_declaration() -> None:
    path = PAYLOAD_ROOT / "agent-workflow" / "providers.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(raw, dict) and raw.get("schema_version") == 7, "unsupported provider declaration")
    provider = raw.get("provider")
    capabilities = raw.get("capabilities")
    hosts = raw.get("hosts")
    configuration = raw.get("configuration")
    require(
        isinstance(provider, dict)
        and isinstance(capabilities, dict)
        and isinstance(hosts, dict)
        and hosts
        and isinstance(configuration, dict),
        "provider declaration is incomplete",
    )
    configuration_names = set(configuration)
    repository = provider.get("repository")
    provider_version = provider.get("version")
    require(
        isinstance(repository, str) and re.fullmatch(r"[^/]+/[^/]+", repository) is not None,
        "invalid provider repository",
    )
    require(
        isinstance(provider_version, str) and re.fullmatch(r"v\d+\.\d+\.\d+", provider_version) is not None,
        "provider version must be pinned",
    )
    for field in ("name", "repository", "version", "resolved_commit", "tag_object", "upstream_tree"):
        require(
            provider.get(field) == REVIEWED_PROVIDER[field],
            f"provider {field} differs from the reviewed release identity",
        )
    for field in ("resolved_commit", "tag_object", "upstream_tree"):
        require(
            isinstance(provider.get(field), str)
            and re.fullmatch(r"[0-9a-f]{40}", provider[field]) is not None,
            f"provider {field} must be a full Git object ID",
        )
    snapshot = provider.get("snapshot")
    require(
        isinstance(snapshot, dict) and set(snapshot) == {"path", "sha256"},
        "provider snapshot declaration is incomplete",
    )
    snapshot_root = package_path(snapshot.get("path"), "provider snapshot path")
    require(
        isinstance(snapshot.get("sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", snapshot["sha256"]) is not None,
        "provider snapshot checksum must be a SHA-256 digest",
    )
    require(
        snapshot["sha256"] == REVIEWED_PROVIDER["snapshot_sha256"],
        "provider snapshot checksum differs from the reviewed release identity",
    )
    license_info = provider.get("license")
    require(
        isinstance(license_info, dict)
        and set(license_info) == {"name", "path", "sha256"}
        and license_info.get("name") == "MIT",
        "provider license declaration must identify MIT text",
    )
    license_path = package_path(license_info.get("path"), "provider license path")
    require(license_path.is_file() and not license_path.is_symlink(), "bundled provider license is missing or unsafe")
    license_text = license_path.read_text(encoding="utf-8")
    require(
        isinstance(license_info.get("sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", license_info["sha256"]) is not None
        and sha256(license_path.read_bytes()).hexdigest() == license_info["sha256"],
        "bundled provider license checksum differs from the declaration",
    )
    require(
        license_info["sha256"] == REVIEWED_PROVIDER["license_sha256"],
        "provider license checksum differs from the reviewed release identity",
    )
    require(
        "MIT License" in license_text and "Copyright (c) 2026 Matt Pocock" in license_text,
        "bundled provider license text is incomplete",
    )
    host_names = set(hosts)
    require(all(isinstance(name, str) and name for name in host_names), "invalid provider host name")
    skills = provider.get("skills")
    require(isinstance(skills, list) and skills, "provider skills must be a non-empty array")
    names: set[str] = set()
    for item in skills:
        require(isinstance(item, dict), "provider skill entries must be objects")
        name = item.get("name")
        require(isinstance(name, str) and bool(name) and PurePosixPath(name).name == name, "invalid provider skill name")
        require(name not in names, f"duplicate provider skill: {name}")
        names.add(name)
        provider_path = item.get("path")
        require(isinstance(provider_path, str), f"provider skill {name} needs a path")
        safe_relative(provider_path)
        invocation = item.get("invocation")
        require(isinstance(invocation, dict), f"provider skill {name} lacks invocation policy")
        require(set(invocation) == host_names, f"provider skill {name} invocation hosts differ from declaration")
        require(
            all(isinstance(policy, str) and policy in INVOCATION_POLICIES for policy in invocation.values()),
            f"invalid invocation policy for {name}",
        )
        requirements = item.get("requires_configuration")
        require(
            isinstance(requirements, list)
            and all(isinstance(requirement, str) for requirement in requirements)
            and len(requirements) == len(set(requirements))
            and all(requirement in configuration_names for requirement in requirements),
            f"provider skill {name} has invalid configuration requirements",
        )
        adapter = item.get("agentic_workflow_adapter")
        require(
            adapter is None or isinstance(adapter, dict),
            f"provider skill {name} agentic_workflow_adapter must be an object",
        )
        if isinstance(adapter, dict):
            adapter_name = adapter.get("name")
            if adapter_name == "wayfinder-runtime-projection-v1":
                valid_adapter = (
                    set(adapter) == {"name", "projection_source", "upstream_body_sha256"}
                    and isinstance(adapter.get("upstream_body_sha256"), str)
                    and re.fullmatch(r"[0-9a-f]{64}", adapter["upstream_body_sha256"])
                    is not None
                    and adapter.get("projection_source") == "runtime-projections/wayfinder.md"
                    and name == "wayfinder"
                )
            else:
                valid_adapter = (
                    set(adapter) == {"name"}
                    and adapter_name == "implicit-invocation-v1"
                    and name in {"to-spec", "to-tickets", "implement"}
                )
            require(
                valid_adapter
                and invocation.get("codex") == "implicit"
                and invocation.get("github-copilot") == "implicit"
                and invocation.get("claude-code") == "unavailable",
                f"provider skill {name} adapter does not match supported host policies",
            )
    require(set(capabilities.values()) <= names, "capability points to an undeclared provider skill")
    require(
        snapshot_root.is_dir() and not snapshot_root.is_symlink(),
        "bundled provider snapshot is missing or unsafe",
    )
    require(
        {path.name for path in snapshot_root.iterdir()} == names,
        "bundled provider inventory differs from the declaration",
    )
    require(
        tree_digest(snapshot_root) == snapshot["sha256"],
        "bundled provider snapshot checksum differs from the declaration",
    )
    for item in skills:
        name = item["name"]
        validate_local_references(snapshot_root / name)
        skill_file = snapshot_root / name / "SKILL.md"
        openai_file = snapshot_root / name / "agents" / "openai.yaml"
        require(skill_file.is_file() and not skill_file.is_symlink(), f"bundled provider skill is missing: {name}")
        require(openai_file.is_file() and not openai_file.is_symlink(), f"bundled Codex metadata is missing: {name}")
        frontmatter = skill_file.read_text(encoding="utf-8").split("\n---\n", 1)[0]
        for expected in (
            f"name: {name}",
            f"    github-path: {item['path']}",
            f"    github-pinned: {provider_version}",
            f"    github-ref: refs/tags/{provider_version}",
            f"    github-repo: https://github.com/{repository}",
        ):
            require(expected in frontmatter.splitlines(), f"bundled provider metadata differs for {name}: {expected}")
        require(
            re.search(r"^    github-tree-sha: [0-9a-f]{40}$", frontmatter, re.MULTILINE) is not None,
            f"bundled provider tree provenance is missing for {name}",
        )
    installed_declaration = REPOSITORY_ROOT / ".agent-workflow" / "providers.json"
    if installed_declaration.exists():
        require(
            installed_declaration.is_file()
            and not installed_declaration.is_symlink()
            and installed_declaration.read_bytes() == path.read_bytes(),
            "source and packaged provider declarations differ",
        )
    wayfinder = next((item for item in skills if item.get("name") == "wayfinder"), None)
    require(
        isinstance(wayfinder, dict)
        and wayfinder.get("agentic_workflow_adapter", {}).get("name")
        == "wayfinder-runtime-projection-v1"
        and wayfinder.get("invocation", {}).get("codex") == "implicit"
        and wayfinder.get("invocation", {}).get("github-copilot") == "implicit",
        "Wayfinder must declare the Agentic Workflow runtime-projection adapter",
    )
    wayfinder_adapter = wayfinder["agentic_workflow_adapter"]
    projection_source = package_path(
        wayfinder_adapter.get("projection_source"),
        "Wayfinder runtime projection source",
    )
    require(
        projection_source.is_file() and not projection_source.is_symlink(),
        "owned Wayfinder runtime projection is missing or unsafe",
    )
    projection_text = projection_source.read_text(encoding="utf-8")
    require(
        projection_text.startswith("# Wayfinder\n")
        and projection_text.endswith("\n")
        and "\n---\n" not in projection_text,
        "owned Wayfinder runtime projection is malformed",
    )
    for required in (
        "framework-owned runtime projection",
        "derived from Matt Pocock's Wayfinder methodology",
        "## Core invariants",
        "## Establish territory",
        "## Resolve the frontier progressively",
        "## Reconcile and hand off",
        "Optional U/E/F/D preserves only independently useful knowledge",
        "Specialists own their methods and native artifacts",
        "create no framework continuity record",
        "coherent ready frontier",
        "one or more ready scopes",
        "Each Implementation handoff consumes one coherent scope",
        "Verification follows execution",
        "Use `to-tickets`",
        "It defines effort selection, paths, identifiers, locking",
    ):
        require(
            required in " ".join(projection_text.split()),
            f"owned Wayfinder runtime lacks required contract: {required}",
        )
    for contract_only_detail in (
        ".wayfinder-mutation-lock",
        "highest currently present",
        "retired number",
        "final scan and removal",
    ):
        require(
            contract_only_detail not in projection_text,
            f"owned Wayfinder runtime duplicates state-contract mechanics: {contract_only_detail}",
        )
    for incompatible in (
        "shared map on the repo's issue tracker",
        "labelled `wayfinder:map`",
        "Each ticket is a **child issue**",
        "Each ticket carries a `wayfinder:<type>` label",
        "A session **claims** a ticket by assigning it",
        "tracker's **native** dependency relationship",
        "run `/setup-matt-pocock-skills`",
        "default to the local-markdown tracker",
        "post the answer as a **resolution comment**",
        "**close** the issue",
    ):
        require(
            incompatible not in projection_text,
            "owned Wayfinder runtime contains incompatible tracker mechanics",
        )
    upstream_wayfinder = snapshot_root / "wayfinder" / "SKILL.md"
    upstream_bytes = upstream_wayfinder.read_bytes()
    separator = upstream_bytes.find(b"\n---\n", 4)
    require(separator >= 0, "bundled Wayfinder skill lacks valid frontmatter")
    upstream_body = upstream_bytes[separator + len(b"\n---\n") :]
    require(
        sha256(upstream_body).hexdigest() == wayfinder_adapter["upstream_body_sha256"],
        "Wayfinder upstream body fingerprint differs from the reviewed input",
    )
    for name in ("to-spec", "to-tickets", "implement"):
        skill = next((item for item in skills if item.get("name") == name), None)
        require(
            isinstance(skill, dict)
            and skill.get("agentic_workflow_adapter", {}).get("name")
            == "implicit-invocation-v1"
            and skill.get("invocation", {}).get("codex") == "implicit"
            and skill.get("invocation", {}).get("github-copilot") == "implicit",
            f"{name} must declare the implicit-invocation adapter",
        )


def check_scenario_catalogs() -> None:
    tests = PACKAGE_ROOT / "tests"

    acceptance_name = "acceptance-scenarios.json"
    acceptance = json.loads((tests / acceptance_name).read_text(encoding="utf-8"))
    require(isinstance(acceptance, list) and acceptance, f"{acceptance_name} must contain cases")
    acceptance_ids: list[str] = []
    for item in acceptance:
        require(isinstance(item, dict), f"invalid case in {acceptance_name}")
        for field in ("id", "operation", "expected"):
            require(
                isinstance(item.get(field), str) and bool(item[field].strip()),
                f"{acceptance_name} case needs a non-empty {field}",
            )
        acceptance_ids.append(item["id"])
    require(len(acceptance_ids) == len(set(acceptance_ids)), f"duplicate case id in {acceptance_name}")

    decision_name = "decision-contract-scenarios.json"
    decisions = json.loads((tests / decision_name).read_text(encoding="utf-8"))
    require(isinstance(decisions, list) and decisions, f"{decision_name} must contain decisions")
    required_strings = (
        "id",
        "category",
        "prompt",
        "setup",
        "dominant_activity",
        "host",
        "route_result",
        "repository_state_effect",
        "external_scope",
        "expected_behavior",
    )
    decision_ids: list[str] = []
    for item in decisions:
        require(isinstance(item, dict), f"invalid decision in {decision_name}")
        for field in required_strings:
            require(
                isinstance(item.get(field), str) and bool(item[field].strip()),
                f"{decision_name} decision needs a non-empty {field}",
            )
        require(
            isinstance(item.get("capabilities"), list)
            and all(isinstance(value, str) and value for value in item["capabilities"]),
            f"{decision_name} decision needs a capabilities array",
        )
        invocations = item.get("provider_invocations")
        require(isinstance(invocations, list), f"{decision_name} decision needs provider_invocations")
        for invocation in invocations:
            require(isinstance(invocation, dict), f"invalid provider invocation in {decision_name}")
            require(
                all(
                    isinstance(invocation.get(field), str) and bool(invocation[field].strip())
                    for field in ("name", "policy", "invocation")
                )
                and isinstance(invocation.get("executed"), bool),
                f"invalid provider invocation in {decision_name}",
            )
        require(isinstance(item.get("executed"), bool), f"{decision_name} decision needs executed")
        decision_ids.append(item["id"])
    require(len(decision_ids) == len(set(decision_ids)), f"duplicate decision id in {decision_name}")


def check_behavior_scenarios() -> None:
    tests = PACKAGE_ROOT / "tests"
    behavior = subprocess.run(
        [sys.executable, str(tests / "behavior.py"), "validate"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        errors="backslashreplace",
    )
    require(
        behavior.returncode == 0,
        "behavioral scenario validation failed: "
        + (behavior.stderr.strip() or behavior.stdout.strip()),
    )


def check_markdown_links() -> None:
    roots = [REPOSITORY_ROOT / "README.md", REPOSITORY_ROOT / "docs", PACKAGE_ROOT / "SKILL.md", PAYLOAD_ROOT / "agent-workflow"]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(path for path in root.rglob("*.md") if path.is_file())
    for path in files:
        text = path.read_text(encoding="utf-8")
        for destination in MARKDOWN_LINK.findall(text):
            destination = destination.split("#", 1)[0]
            if not destination or "://" in destination or destination.startswith("mailto:"):
                continue
            candidate = (path.parent / destination).resolve()
            require(candidate.exists(), f"broken local Markdown link in {path.relative_to(REPOSITORY_ROOT)}: {destination}")


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
        print("ERROR: Agentic Workflow requires Python 3.11 or newer", file=sys.stderr)
        return 2
    args = build_parser().parse_args(argv)
    try:
        if args.refresh_manifest:
            refresh_manifest()
        for check in (
            check_structure,
            check_manifest,
            check_filesystem,
            check_router_contract,
            check_provider_declaration,
            check_scenario_catalogs,
            check_behavior_scenarios,
            check_markdown_links,
        ):
            check()
        if args.tests:
            run_tests()
        print("OK: Agentic Workflow package verification passed.")
        return 0
    except (VerificationError, SnapshotTreeError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
