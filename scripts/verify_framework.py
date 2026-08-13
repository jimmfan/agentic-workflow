#!/usr/bin/env python3
"""Run deterministic structural and safety checks for the workflow framework."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_SKILLS = (
    "workflow-discovery",
    "workflow-teach",
    "workflow-decomposition",
    "workflow-implementation",
    "workflow-debugging",
    "workflow-verification",
    "workflow-review",
)
SKILLS = WORKFLOW_SKILLS + ("hermes-delegation",)
REQUIRED_PROFILE_HEADINGS = (
    "Purpose and success",
    "Technology and architecture",
    "Important paths",
    "Terminology",
    "Constraints and policy",
    "Delivery workflow",
    "Commands",
    "Debugging model",
    "Decision considerations",
    "Profile maintenance",
)
COMMAND_FIELDS = (
    "Purpose",
    "Action",
    "Kind",
    "Working directory",
    "Prerequisites",
    "Environment",
    "Scope",
    "Safety",
    "Approval required",
    "Timeout",
    "Success",
    "Unavailable",
    "Side effects and reversal",
)
CORE_PATHS = (
    Path("AGENTS.md"),
    Path("ai-workflow/README.md"),
    Path("ai-workflow/contracts/project-profile.md"),
    Path("ai-workflow/state/README.md"),
    Path("ai-workflow/templates/active-state.md"),
    Path("ai-workflow/templates/decision-record.md"),
    Path("ai-workflow/templates/learning-record.md"),
    Path("ai-workflow/templates/project-profile.md"),
    Path("ai-workflow/templates/ticket-record.md"),
    Path("ai-workflow/templates/work-item.md"),
) + tuple(Path(".agents/skills") / skill / "SKILL.md" for skill in SKILLS)

INTEGRATION_SCENARIO_FIELDS = {
    "id",
    "requirement",
    "prompt",
    "setup",
    "expected_runtime",
    "expected_route",
    "expected_behavior",
    "expected_safety_outcome",
    "expected_result_outcome",
    "evaluation_category",
    "evaluation_method",
    "evidence",
}
INTEGRATION_RUNTIMES = {
    "codex",
    "codex-hermes-codex",
    "codex-native-subagent",
    "framework",
    "hermes-codex",
}
INTEGRATION_ROUTES = {
    "adapter-safety-audit",
    "approval-required",
    "context-overhead-audit",
    "credential-safety-audit",
    "delegation-decision->hermes-delegation",
    "hermes-delegation",
    "hermes-delegation->fallback",
    "hermes-delegation->incomplete",
    "hermes-delegation->parent-resume",
    "hermes-delegation->recursion-block",
    "hermes-delegation->safety-failure",
    "hermes-delegation->state-reconciliation",
    "hermes-delegation->verification",
    "hermes-preflight->fallback",
    "hermes-preflight->incompatible",
    "hermes-profile-audit",
    "host-adapter-audit",
    "implementation->verification->review",
    "manual-hermes->codex",
    "normal",
    "normal-research",
    "repository-exploration",
    "shared-skill-audit",
    "state-resume",
}
INTEGRATION_EVALUATION_CATEGORIES = {
    "adapter-simulation",
    "live-hermes",
    "manual-codex",
    "manual-cross-runtime",
    "static-analysis",
}


class VerificationFailure(AssertionError):
    """A deterministic framework invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationFailure(message)


def read(relative: Path) -> str:
    path = ROOT / relative
    require(path.is_file(), f"missing file: {relative}")
    return path.read_text(encoding="utf-8")


def check_required_files() -> None:
    required = set(CORE_PATHS) | {
        Path("README.md"),
        Path("VERSION"),
        Path("distribution/manifest.json"),
        Path("adapters/hermes/profile-config.yaml"),
        Path("adapters/hermes/request.schema.json"),
        Path("adapters/hermes/result.schema.json"),
        Path("adapters/hermes/smoke-request.json"),
        Path("ai-workflow/VERSION"),
        Path("ai-workflow/project-profile.md"),
        Path("ai-workflow/state/active.md"),
        Path("scripts/adopt.py"),
        Path("scripts/hermes_adapter.py"),
        Path("tests/acceptance-scenarios.json"),
        Path("tests/hermes-acceptance-scenarios.json"),
        Path("tests/hermes-repo-read-scenarios.json"),
        Path("tests/hermes-learning-scenarios.json"),
        Path("tests/README.md"),
        Path("docs/architecture.md"),
        Path("docs/codex-research.md"),
        Path("docs/integrations/hermes.md"),
        Path("docs/routing.md"),
        Path("docs/platform-research.md"),
        Path("docs/reference-research.md"),
        Path("docs/verification.md"),
        Path("docs/decisions/0001-use-instructions-and-agent-skills.md"),
        Path("docs/decisions/0002-use-checksummed-copy-adoption.md"),
        Path("docs/decisions/0003-use-internal-reference-inspired-workflows.md"),
        Path("docs/decisions/0004-codex-primary-with-optional-hermes.md"),
        Path("docs/decisions/0005-add-decomposition-and-independent-review.md"),
        Path("examples/application-project/project-profile.md"),
        Path("examples/infrastructure-project/project-profile.md"),
        Path("LICENSE.md"),
    }
    missing = sorted(str(path) for path in required if not (ROOT / path).is_file())
    require(not missing, "missing required files: " + ", ".join(missing))


def parse_frontmatter(text: str, path: Path) -> Mapping[str, str]:
    parts = text.split("---", 2)
    require(len(parts) == 3 and not parts[0].strip(), f"invalid frontmatter delimiters: {path}")
    values: Dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        require(":" in line, f"invalid frontmatter line in {path}: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    require(set(values) == {"name", "description"}, f"frontmatter fields must be name and description only: {path}")
    return values


def check_skill_metadata() -> None:
    for skill in SKILLS:
        relative = Path(".agents/skills") / skill / "SKILL.md"
        text = read(relative)
        values = parse_frontmatter(text, relative)
        require(values["name"] == skill, f"skill name does not match directory: {relative}")
        require(re.fullmatch(r"[a-z0-9-]{1,64}", skill) is not None, f"invalid skill name: {skill}")
        require(40 <= len(values["description"]) <= 1024, f"skill description length invalid: {skill}")
        require("use " in values["description"].lower(), f"skill description lacks trigger guidance: {skill}")
        require("TODO" not in text, f"placeholder remains in {relative}")


def headings(text: str, level: int) -> List[str]:
    marker = "#" * level
    return re.findall(rf"^{marker} (.+?)\s*$", text, flags=re.MULTILINE)


def command_blocks(text: str) -> List[Tuple[str, str]]:
    match = re.search(r"^## Commands\s*$\n(.*?)(?=^## |\Z)", text, flags=re.MULTILINE | re.DOTALL)
    require(match is not None, "profile lacks Commands section")
    section = match.group(1)
    return re.findall(r"^### `([^`]+)`\s*$\n(.*?)(?=^### |\Z)", section, flags=re.MULTILINE | re.DOTALL)


def check_profile(path: Path, require_commands: bool = True) -> None:
    text = read(path)
    present = headings(text, 2)
    missing = [heading for heading in REQUIRED_PROFILE_HEADINGS if heading not in present]
    require(not missing, f"{path} lacks profile headings: {', '.join(missing)}")
    blocks = command_blocks(text)
    if require_commands:
        require(blocks, f"{path} needs at least one complete command entry")
    identifiers: Set[str] = set()
    for identifier, block in blocks:
        require(re.fullmatch(r"[a-z0-9-]+", identifier) is not None, f"invalid command id {identifier} in {path}")
        require(identifier not in identifiers, f"duplicate command id {identifier} in {path}")
        identifiers.add(identifier)
        for field in COMMAND_FIELDS:
            require(re.search(rf"^- {re.escape(field)}:", block, flags=re.MULTILINE) is not None, f"{identifier} lacks {field} in {path}")
        safety_match = re.search(r"^- Safety: `([^`]+)`", block, flags=re.MULTILINE)
        require(safety_match is not None, f"{identifier} Safety must be a backticked enum in {path}")
        safety = safety_match.group(1)
        require(safety in {"read-only", "locally-mutating", "externally-mutating", "destructive"}, f"unknown safety {safety} in {path}")
        approval_match = re.search(r"^- Approval required: `?(yes|no)`?\s*$", block, flags=re.MULTILINE)
        require(approval_match is not None, f"invalid approval field for {identifier} in {path}")
        scope_match = re.search(r"^- Scope: `([^`]+)`", block, flags=re.MULTILINE)
        require(scope_match is not None, f"{identifier} Scope must be a backticked enum in {path}")
        scope = scope_match.group(1)
        require(scope in {"repository-local", "host-local", "external"}, f"unknown scope {scope} in {path}")
        if safety in {"externally-mutating", "destructive"} or scope == "external":
            require(approval_match.group(1) == "yes", f"{identifier} must require approval in {path}")


def check_profiles_and_contract() -> None:
    contract = read(Path("ai-workflow/contracts/project-profile.md"))
    for field in COMMAND_FIELDS:
        require(f"- {field}:" in contract, f"command contract lacks {field}")
    for safety in ("read-only", "locally-mutating", "externally-mutating", "destructive"):
        require(f"`{safety}`" in contract, f"command contract lacks safety class {safety}")
    require("Any entry marked `Approval required: yes` waits" in contract, "contract does not honor explicit approval for every safety class")
    require("Every `external`-scope action also waits" in contract, "contract does not require approval for external reads")
    require("canonical location for durable" in contract and "workflow records link" in contract, "profile contract lacks project-owned durable specification policy")
    require(
        "implementation-ticket destination" in contract and "Native issue bodies remain" in contract,
        "profile contract lacks canonical ticket ownership policy",
    )
    require(
        "proportional independent review" in contract and "must not let review replace executable Verification" in contract,
        "profile contract lacks independent-review policy",
    )
    verification_skill = read(Path(".agents/skills/workflow-verification/SKILL.md"))
    require("Any entry with `Approval required: yes` waits" in verification_skill, "Verification skill does not honor explicit approval for every safety class")
    check_profile(Path("ai-workflow/project-profile.md"))
    check_profile(Path("examples/application-project/project-profile.md"))
    check_profile(Path("examples/infrastructure-project/project-profile.md"))
    check_profile(Path("ai-workflow/templates/project-profile.md"), require_commands=False)


def parse_label_map(text: str) -> Mapping[str, str]:
    result: Dict[str, str] = {}
    for key, value in re.findall(r"^- ([^:]+):\s*(.*?)\s*$", text, flags=re.MULTILINE):
        result[key] = value
    return result


def check_state_contract() -> None:
    contract = read(Path("ai-workflow/state/README.md"))
    for token in ("DEC-NNNN", "IMP-NNNN", "TKT-NNNN", "DBG-NNNN", "LRN-NNNN", "IDP-NNNN", "invalid", "stale", "conflicting", "archive"):
        require(token in contract, f"state contract lacks {token}")
    for status in ("proposed", "provisional", "accepted", "rejected", "superseded", "completed"):
        require(f"`{status}`" in contract, f"state contract lacks status {status}")
    active = parse_label_map(read(Path("ai-workflow/state/active.md")))
    required = {
        "State version",
        "Active workflow",
        "Active record",
        "Interrupted workflow",
        "Interrupted record",
        "Pending question",
        "Resume target",
        "Last reviewed",
        "Review after",
        "Notes",
    }
    require(required.issubset(active), "active state lacks fields: " + ", ".join(sorted(required - set(active))))
    require(active["State version"] == "1", "unsupported active state version")
    require(active["Active workflow"] == "none", "framework repository should finish idle")
    require("Specifications are project-owned" in contract and "never an active" in contract, "state contract lacks durable-specification or supplemental-IDP boundary")
    for token in ("actionable frontier", "self-dependencies", "cycles", "native ticket system", "never copies complete ticket bodies"):
        require(token in contract, f"state contract lacks decomposition invariant {token!r}")
    for workflow in ("decomposition", "review"):
        require(f"`{workflow}`" in contract, f"state contract lacks {workflow} workflow enum")
    verification_skill = read(Path(".agents/skills/workflow-verification/SKILL.md"))
    require(
        "controlled-promotion" in verification_skill
        and "During read-only work, report candidates" in verification_skill,
        "Verification lacks the non-mutating IDP candidate boundary",
    )
    ticket_template = read(Path("ai-workflow/templates/ticket-record.md"))
    for token in ("Type: implementation-ticket", "Approved requirements", "Blocked by", "Active blocker", "Recovery condition", "Acceptance criteria and evidence", "Review disposition", "Resume target"):
        require(token in ticket_template, f"ticket template lacks {token}")
    work_item = read(Path("ai-workflow/templates/work-item.md"))
    require("Current ticket" in work_item and "Current frontier" in work_item, "IMP template lacks current-ticket/frontier lifecycle fields")

    def graph_state(tickets: Mapping[str, Mapping[str, object]]) -> Tuple[str, Set[str], Set[str]]:
        identifiers = set(tickets)
        visiting: Set[str] = set()
        visited: Set[str] = set()

        def visit(identifier: str) -> None:
            require(identifier not in visiting, f"ticket graph cycle at {identifier}")
            if identifier in visited:
                return
            visiting.add(identifier)
            raw_blockers = tickets[identifier].get("blocked_by", [])
            require(isinstance(raw_blockers, list), f"ticket {identifier} blockers must be a list")
            for blocker in raw_blockers:
                require(isinstance(blocker, str) and blocker in identifiers, f"ticket {identifier} has missing blocker {blocker!r}")
                require(blocker != identifier, f"ticket {identifier} depends on itself")
                visit(blocker)
            visiting.remove(identifier)
            visited.add(identifier)

        for identifier in identifiers:
            visit(identifier)

        frontier: Set[str] = set()
        active: Set[str] = set()
        incomplete: Set[str] = set()
        exceptional_blockers: Set[str] = set()
        for identifier, ticket in tickets.items():
            status = ticket.get("status")
            require(status in {"draft", "ready", "active", "blocked", "completed", "superseded"}, f"ticket {identifier} has invalid status")
            blocker = ticket.get("active_blocker")
            recovery = ticket.get("recovery")
            require((status == "blocked") == bool(blocker), f"ticket {identifier} blocked status and active blocker disagree")
            require(bool(blocker) == bool(recovery), f"ticket {identifier} active blocker lacks recovery condition")
            dependencies = ticket.get("blocked_by", [])
            require(isinstance(dependencies, list), f"ticket {identifier} blockers must be a list")
            if status not in {"completed", "superseded"}:
                incomplete.add(identifier)
            if status == "active":
                require(
                    all(tickets[item].get("status") == "completed" for item in dependencies),
                    f"active ticket {identifier} has incomplete dependencies",
                )
                active.add(identifier)
            if status == "blocked":
                exceptional_blockers.add(identifier)
            if status == "ready" and not blocker and all(tickets[item].get("status") == "completed" for item in dependencies):
                frontier.add(identifier)
        if not incomplete:
            return "complete", active, frontier
        if active or frontier:
            return "actionable", active, frontier
        if exceptional_blockers:
            return "blocked", active, frontier
        return "invalid", active, frontier

    valid = {
        "TKT-0001": {"status": "ready", "blocked_by": [], "active_blocker": None, "recovery": None},
        "TKT-0002": {"status": "ready", "blocked_by": ["TKT-0001"], "active_blocker": None, "recovery": None},
    }
    require(graph_state(valid) == ("actionable", set(), {"TKT-0001"}), "ready frontier fixture is wrong")
    in_progress = {key: dict(value) for key, value in valid.items()}
    in_progress["TKT-0001"]["status"] = "active"
    require(graph_state(in_progress) == ("actionable", {"TKT-0001"}, set()), "active ticket was misclassified as empty-frontier failure")
    advanced = {key: dict(value) for key, value in valid.items()}
    advanced["TKT-0001"]["status"] = "completed"
    require(graph_state(advanced) == ("actionable", set(), {"TKT-0002"}), "completed dependency did not expose next frontier")
    blocked = {
        "TKT-0001": {"status": "blocked", "blocked_by": [], "active_blocker": "environment unavailable", "recovery": "environment health restored"},
    }
    require(graph_state(blocked)[0] == "blocked", "named exceptional blocker was not classified as blocked")
    require(graph_state({"TKT-0001": {"status": "draft", "blocked_by": [], "active_blocker": None, "recovery": None}})[0] == "invalid", "draft-only graph invented a frontier")
    invalid_graphs = (
        {"TKT-0001": {"status": "ready", "blocked_by": ["TKT-9999"], "active_blocker": None, "recovery": None}},
        {"TKT-0001": {"status": "ready", "blocked_by": ["TKT-0001"], "active_blocker": None, "recovery": None}},
        {
            "TKT-0001": {"status": "ready", "blocked_by": ["TKT-0002"], "active_blocker": None, "recovery": None},
            "TKT-0002": {"status": "ready", "blocked_by": ["TKT-0001"], "active_blocker": None, "recovery": None},
        },
        {
            "TKT-0001": {"status": "ready", "blocked_by": [], "active_blocker": None, "recovery": None},
            "TKT-0002": {"status": "active", "blocked_by": ["TKT-0001"], "active_blocker": None, "recovery": None},
        },
        {"TKT-0001": {"status": "blocked", "blocked_by": [], "active_blocker": "environment unavailable", "recovery": None}},
    )
    for invalid_graph in invalid_graphs:
        try:
            graph_state(invalid_graph)
        except VerificationFailure:
            pass
        else:
            raise VerificationFailure("invalid ticket graph fixture was accepted")
    decision_template = read(Path("ai-workflow/templates/decision-record.md"))
    require("Acceptance authority" in decision_template and "consequential decision" in decision_template, "decision template lacks explicit acceptance authority")


def check_acceptance_catalog() -> None:
    raw = json.loads(read(Path("tests/acceptance-scenarios.json")))
    require(isinstance(raw, list), "acceptance catalog must be an array")
    require([item.get("id") for item in raw] == list(range(1, 33)), "acceptance scenario IDs must be exactly 1 through 32")
    required = {"id", "requirement", "prompt", "setup", "expected_route", "expected_behavior", "evidence"}
    for item in raw:
        require(isinstance(item, dict), "each acceptance scenario must be an object")
        require(required == set(item), f"scenario {item.get('id')} fields differ from the contract")
        for key in required - {"id"}:
            require(isinstance(item[key], str) and item[key].strip(), f"scenario {item['id']} has empty {key}")
    combined = "\n".join(item["requirement"] for item in raw)
    for phrase in ("trivial documentation", "explicit learning", "architectural choice", "knowledge gap", "unexplained existing failure", "fully evidenced", "Plan, Build, Verify, and Review", "high-risk one-line", "routing precedence", "later chat", "malformed", "verification configuration", "approval-required", "project profile", "assumptions leak", "conditionally loaded", "third-party skills", "does not overwrite", "upstream Wayfinder", "Upstream Teach", "Durable specifications", "developer-platform friction", "consequential architecture decision", "read-only audit", "durable decomposition", "actionable frontier", "invalid dependency graph", "diagnosis-only", "optional TDD", "independent review", "canonical specification and workflow"):
        require(phrase.lower() in combined.lower(), f"acceptance catalog does not cover: {phrase}")
    by_id = {item["id"]: item for item in raw}
    expected_routes = {
        1: "normal",
        5: "debugging->verification->review",
        7: "implementation->verification->review",
        9: "teach->discovery->implementation->verification->review",
        25: "decomposition->implementation",
        26: "implementation->verification->review",
        27: "state-validation",
        28: "debugging",
        29: "implementation->verification->review",
        30: "review-or-parent-sanity-check",
        31: "review->implementation->verification->review",
        32: "implementation->verification->review",
    }
    for identifier, route in expected_routes.items():
        require(by_id[identifier]["expected_route"] == route, f"scenario {identifier} route must be {route}")
    require("do not change files" in by_id[28]["prompt"] and "snapshots match" in by_id[28]["evidence"], "diagnosis-only acceptance does not enforce nonmutation")
    require("justified option" in by_id[29]["expected_behavior"] and "without inventing a test framework" in by_id[29]["expected_behavior"], "optional TDD acceptance is too weak or mandatory")
    require("/to-spec" in by_id[32]["prompt"] and "/implement" in by_id[32]["prompt"] and "unavailable" in by_id[32]["setup"], "excluded upstream explicit-request fallback is not covered")
    require("fixture evidence supports selecting a cache" in by_id[9]["setup"], "scenario 9 does not determine its post-Discovery branch")
    require("one-coherent-session" in by_id[32]["setup"], "scenario 32 does not determine whether fallback Decomposition is needed")


def check_integration_acceptance_catalog() -> None:
    raw = json.loads(read(Path("tests/hermes-acceptance-scenarios.json")))
    require(isinstance(raw, list), "integration acceptance catalog must be an array")
    require(
        [item.get("id") for item in raw if isinstance(item, dict)] == list(range(1, 31)),
        "integration acceptance scenario IDs must be exactly 1 through 30 in order",
    )
    for item in raw:
        require(isinstance(item, dict), "each integration acceptance scenario must be an object")
        identifier = item.get("id")
        require(set(item) == INTEGRATION_SCENARIO_FIELDS, f"integration scenario {identifier} fields differ from the contract")
        require(isinstance(identifier, int) and not isinstance(identifier, bool), f"integration scenario ID is not an integer: {identifier!r}")
        for key in INTEGRATION_SCENARIO_FIELDS - {"id"}:
            require(
                isinstance(item[key], str) and item[key].strip() == item[key] and bool(item[key]),
                f"integration scenario {identifier} has an empty or untrimmed {key}",
            )
        require(
            item["expected_runtime"] in INTEGRATION_RUNTIMES,
            f"integration scenario {identifier} has unknown expected_runtime {item['expected_runtime']!r}",
        )
        require(
            item["expected_route"] in INTEGRATION_ROUTES,
            f"integration scenario {identifier} has unknown expected_route {item['expected_route']!r}",
        )
        require(
            item["evaluation_category"] in INTEGRATION_EVALUATION_CATEGORIES,
            f"integration scenario {identifier} has unknown evaluation_category {item['evaluation_category']!r}",
        )
    require(
        {item["expected_runtime"] for item in raw} == INTEGRATION_RUNTIMES,
        "integration catalog no longer exercises every runtime enum",
    )
    require(
        {item["evaluation_category"] for item in raw} == INTEGRATION_EVALUATION_CATEGORIES,
        "integration catalog no longer exercises every evaluation category enum",
    )
    by_id = {item["id"]: item for item in raw}
    for identifier in (2, 9):
        require(
            by_id[identifier]["expected_route"] == "implementation->verification->review",
            f"meaningful integration scenario {identifier} omits proportional Review",
        )


def check_generic_core() -> None:
    banned = ("EKS", "Kubernetes", "Terraform", "AWS", "ARC", "pytest", "Ruff", "mypy", "Helm", "kubectl", "npm")
    for relative in CORE_PATHS:
        text = read(relative)
        for token in banned:
            require(re.search(rf"\b{re.escape(token)}\b", text, flags=re.IGNORECASE) is None, f"domain/tool token {token!r} leaked into reusable core file {relative}")
    runtime = "\n".join(read(path) for path in CORE_PATHS)
    require("mattpocock" not in runtime.lower(), "third-party source became a runtime dependency")
    discovery = read(Path(".agents/skills/workflow-discovery/SKILL.md"))
    teach = read(Path(".agents/skills/workflow-teach/SKILL.md"))
    require("explicitly invokes" in discovery and "never mirror" in discovery and "unavailable" in discovery, "Discovery lacks the optional explicit upstream Wayfinder boundary")
    require(
        "explicitly invokes" in teach and "never mirror" in teach and "unavailable" in teach,
        "Teach lacks the optional explicit upstream boundary",
    )
    require(
        "user accepts it" in discovery and "project policy delegates" in discovery,
        "Discovery can accept consequential decisions without named authority",
    )
    implementation = read(Path(".agents/skills/workflow-implementation/SKILL.md"))
    require(
        "durable specification" in implementation and "project-owned location" in implementation and "without copying" in implementation,
        "Implementation lacks the canonical durable-specification boundary",
    )
    require(
        "stable observable seam" in implementation
        and "independent source of truth" in implementation
        and "Never invent a test framework" in implementation,
        "Implementation lacks the optional evidence-driven TDD boundary",
    )
    require(
        "validated `ready` frontier ticket" in implementation
        and "already-`active` ticket may" in implementation,
        "Implementation cannot distinguish new frontier work from active-ticket resume",
    )
    decomposition = read(Path(".agents/skills/workflow-decomposition/SKILL.md"))
    normalized_decomposition = " ".join(decomposition.split())
    for token in ("one coherent implementation session", "canonical", "actionable frontier", "cycles", "without copying"):
        require(token in normalized_decomposition, f"Decomposition lacks {token!r}")
    require(
        "spanning multiple coherent implementation sessions" in normalized_decomposition,
        "Decomposition trigger is broader than the approved multi-session boundary",
    )
    debugging = read(Path(".agents/skills/workflow-debugging/SKILL.md"))
    normalized_debugging = " ".join(debugging.split())
    for token in ("exact symptom", "minimize", "falsifiable hypotheses", "Instrument", "fast local red command is not mandatory", "diagnosis-only"):
        require(token.lower() in debugging.lower(), f"Debugging lacks {token!r}")
    require(
        "do not create a record, edit instrumentation, write diagnostic artifacts" in normalized_debugging
        and "pause and request separate authorization" in normalized_debugging,
        "Debugging diagnosis-only boundary can mutate before fix authorization",
    )
    review = read(Path(".agents/skills/workflow-review/SKILL.md"))
    normalized_review = " ".join(review.split())
    for token in ("owner of executable evidence", "correctness", "security", "validation gaps", "unintended scope", "parent rechecks", "trivial"):
        require(token.lower() in review.lower(), f"Review lacks {token!r}")
    require(
        "authority named in the project profile" in normalized_review
        and "unresolved material limitation remains blocking" in normalized_review,
        "Review can complete without profile-authorized limitation acceptance",
    )
    policy = read(Path("AGENTS.md"))
    require("`/to-spec` and `/implement` do not replace" in policy, "root policy lacks explicit excluded-upstream boundary")
    hermes_skill = read(Path(".agents/skills/hermes-delegation/SKILL.md"))
    require(
        "GitHub Copilot" in hermes_skill and "do not invoke the adapter" in hermes_skill and "Codex-parent" in hermes_skill,
        "Hermes skill lacks the Copilot host boundary",
    )


def check_context_budget_and_duplication() -> None:
    policy = read(Path("AGENTS.md"))
    require(len(policy.splitlines()) <= 55, "always-loaded AGENTS.md exceeds 55 lines")
    require(len(policy.encode("utf-8")) <= 3500, "always-loaded AGENTS.md exceeds 3500 bytes")
    for detail in (
        "Hermes Agent v0.20.0",
        "profile-config.yaml",
        "request.schema.json",
        "result.schema.json",
        "app-server",
        "--toolsets",
    ):
        require(detail not in policy, f"progressively disclosed Hermes detail leaked into AGENTS.md: {detail}")
    paths = (Path("AGENTS.md"),) + tuple(Path(".agents/skills") / skill / "SKILL.md" for skill in SKILLS)
    occurrences: Dict[str, List[str]] = {}
    for path in paths:
        for line in read(path).splitlines():
            normalized = " ".join(line.lower().split())
            if len(normalized) >= 80 and not normalized.startswith("description:"):
                occurrences.setdefault(normalized, []).append(str(path))
    duplicates = {line: locations for line, locations in occurrences.items() if len(set(locations)) > 1}
    require(not duplicates, "exact long-line context duplication found: " + repr(duplicates))


def check_distribution_manifest() -> None:
    manifest = json.loads(read(Path("distribution/manifest.json")))
    require(set(manifest) == {"schema_version", "framework_version", "framework_owned", "project_seeds"}, "distribution manifest has unknown or missing fields")
    require(manifest.get("schema_version") == 1, "distribution schema must be 1")
    version = read(Path("VERSION")).strip()
    require(manifest.get("framework_version") == version, "distribution version differs from VERSION")
    require(read(Path("ai-workflow/VERSION")).strip() == version, "installed VERSION differs from source VERSION")
    owned = manifest.get("framework_owned")
    require(isinstance(owned, list) and len(owned) == len(set(owned)), "framework_owned must be a unique list")
    required_owned = {str(path) for path in CORE_PATHS} | {
        "ai-workflow/VERSION",
        "docs/integrations/hermes.md",
        "scripts/hermes_adapter.py",
    }
    require(required_owned.issubset(set(owned)), "distribution manifest omits framework-owned runtime files: " + ", ".join(sorted(required_owned - set(owned))))
    def safe_manifest_path(raw: object) -> bool:
        if not isinstance(raw, str) or not raw or "\\" in raw:
            return False
        value = PurePosixPath(raw)
        return not value.is_absolute() and "." not in value.parts and ".." not in value.parts

    for raw in owned:
        require(safe_manifest_path(raw), f"unsafe owned path {raw!r}")
        require((ROOT / raw).is_file() and not (ROOT / raw).is_symlink(), f"manifest-owned file missing or symlinked: {raw}")
    seeds = manifest.get("project_seeds")
    require(isinstance(seeds, list) and seeds, "project seeds must be a nonempty list")
    targets: Set[str] = set()
    sources: Set[str] = set()
    for item in seeds:
        require(isinstance(item, dict) and set(item) == {"source", "target"}, "invalid project seed entry")
        for field in ("source", "target"):
            value = item[field]
            require(safe_manifest_path(value), f"unsafe seed {field}: {value!r}")
        require((ROOT / item["source"]).is_file() and not (ROOT / item["source"]).is_symlink(), f"seed source missing or symlinked: {item['source']}")
        require(item["source"] not in sources, f"duplicate seed source: {item['source']}")
        require(item["target"] not in targets, f"duplicate seed target: {item['target']}")
        sources.add(item["source"])
        targets.add(item["target"])
        require(item["target"] not in owned, f"project-owned seed is also framework-owned: {item['target']}")


def run_adopt(args: Sequence[str]) -> subprocess.CompletedProcess:
    return run_adopt_from(ROOT, args)


def run_adopt_from(source: Path, args: Sequence[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(source / "scripts/adopt.py"), *args],
        cwd=str(source),
        capture_output=True,
        text=True,
        timeout=20,
    )


def check_adoption_lifecycle() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-workflow-verification-") as temporary:
        target = Path(temporary) / "consumer"
        profile = target / "ai-workflow/project-profile.md"
        profile.parent.mkdir(parents=True)
        profile.write_text("# custom project profile\n", encoding="utf-8")

        dry = run_adopt(["install", str(target)])
        require(dry.returncode == 0 and "DRY RUN" in dry.stdout, f"install dry run failed: {dry.stderr}")
        require(not (target / "AGENTS.md").exists(), "install dry run changed files")

        install = run_adopt(["install", str(target), "--apply"])
        require(install.returncode == 0, f"install failed: {install.stderr}")
        require(profile.read_text(encoding="utf-8") == "# custom project profile\n", "install overwrote project profile")
        require((target / "ai-workflow/state/active.md").is_file(), "install did not seed active state")
        require((target / "docs/integrations/hermes.md").is_file(), "install omitted the guide required by the Hermes skill")
        require((target / ".agents/skills/workflow-decomposition/SKILL.md").is_file(), "install omitted Decomposition")
        require((target / ".agents/skills/workflow-review/SKILL.md").is_file(), "install omitted Review")
        require((target / "ai-workflow/templates/ticket-record.md").is_file(), "install omitted the ticket template")
        active = (target / "ai-workflow/state/active.md").read_text(encoding="utf-8")
        require("YYYY-MM-DD" not in active and re.search(r"Last reviewed: [0-9]{4}-[0-9]{2}-[0-9]{2}", active) is not None, "install left an invalid active-state date placeholder")
        require((target / "ai-workflow/install-manifest.json").is_file(), "install manifest missing")

        status = run_adopt(["status", str(target)])
        require(status.returncode == 0 and "Installation is clean." in status.stdout, f"clean status failed: {status.stderr}")

        update = run_adopt(["update", str(target), "--apply"])
        require(update.returncode == 0, f"clean update failed: {update.stderr}")

        policy = target / "AGENTS.md"
        custom_policy = policy.read_text(encoding="utf-8") + "\nProject-local customization.\n"
        policy.write_text(custom_policy, encoding="utf-8")
        dirty_status = run_adopt(["status", str(target)])
        require(dirty_status.returncode == 1 and "differs" in dirty_status.stdout, "dirty status did not return exit status 1")
        conflict = run_adopt(["update", str(target), "--apply"])
        require(conflict.returncode == 2 and "locally changed" in conflict.stderr, "update did not refuse a local framework change")
        require(policy.read_text(encoding="utf-8") == custom_policy, "conflicting update overwrote local change")

        remove_dry = run_adopt(["remove", str(target)])
        require(remove_dry.returncode == 0 and "DRY RUN" in remove_dry.stdout, f"remove dry run failed: {remove_dry.stderr}")
        require((target / "ai-workflow/install-manifest.json").is_file(), "remove dry run changed files")

        remove = run_adopt(["remove", str(target), "--apply"])
        require(remove.returncode == 0, f"remove failed: {remove.stderr}")
        require(profile.read_text(encoding="utf-8") == "# custom project profile\n", "remove deleted project profile")
        require((target / "ai-workflow/state/active.md").is_file(), "remove deleted project state")
        require(policy.read_text(encoding="utf-8") == custom_policy, "remove deleted modified framework file")
        require(not (target / "ai-workflow/install-manifest.json").exists(), "remove left installation manifest")
        require(not (target / ".agents/skills/workflow-teach/SKILL.md").exists(), "remove left unchanged framework skill")
        require(not (target / ".agents/skills/workflow-review/SKILL.md").exists(), "remove left unchanged Review skill")


def check_adoption_existing_policy_and_provenance() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-workflow-policy-verification-") as temporary:
        custom_target = Path(temporary) / "custom"
        policy = custom_target / "AGENTS.md"
        policy.parent.mkdir(parents=True)
        original = b"# Existing project instructions\n\nKeep this exact project rule.\n"
        policy.write_bytes(original)
        install = run_adopt(["install", str(custom_target), "--apply"])
        require(install.returncode == 0 and "merge framework policy" in install.stdout, f"custom-policy install failed: {install.stderr}")
        combined = policy.read_bytes()
        require(original in combined and b"ai-workflow:managed-begin" in combined, "install did not preserve existing policy content")
        update = run_adopt(["update", str(custom_target), "--apply"])
        require(update.returncode == 0, f"composite-policy update failed: {update.stderr}")
        remove = run_adopt(["remove", str(custom_target), "--apply"])
        require(remove.returncode == 0, f"composite-policy removal failed: {remove.stderr}")
        require(policy.read_bytes() == original, "removal did not restore the exact pre-install policy")

        identical_target = Path(temporary) / "identical"
        identical_policy = identical_target / "AGENTS.md"
        identical_policy.parent.mkdir(parents=True)
        source_policy = (ROOT / "AGENTS.md").read_bytes()
        identical_policy.write_bytes(source_policy)
        install_identical = run_adopt(["install", str(identical_target), "--apply"])
        require(install_identical.returncode == 0 and "preserve it on removal" in install_identical.stdout, f"identical install failed: {install_identical.stderr}")
        remove_identical = run_adopt(["remove", str(identical_target), "--apply"])
        require(remove_identical.returncode == 0, f"identical removal failed: {remove_identical.stderr}")
        require(identical_policy.read_bytes() == source_policy, "removal deleted a byte-identical file that predated install")


def check_adoption_tamper_and_preflight_guards() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-workflow-tamper-verification-") as temporary:
        target = Path(temporary) / "consumer"
        target.mkdir()
        install = run_adopt(["install", str(target), "--apply"])
        require(install.returncode == 0, f"tamper-test install failed: {install.stderr}")
        valuable = target / "valuable.txt"
        valuable.write_text("project data\n", encoding="utf-8")
        digest = hashlib.sha256(valuable.read_bytes()).hexdigest()
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["framework_files"]["valuable.txt"] = {"sha256": digest, "source_sha256": digest, "origin": "created"}
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        remove = run_adopt(["remove", str(target), "--apply"])
        require(remove.returncode == 2 and "refusing deletion" in remove.stderr, "tampered manifest was accepted for deletion")
        require(valuable.read_text(encoding="utf-8") == "project data\n", "tampered manifest deleted an unrelated project file")

        blocked = Path(temporary) / "blocked"
        blocked.mkdir()
        (blocked / ".agents").write_text("not a directory\n", encoding="utf-8")
        partial = run_adopt(["install", str(blocked), "--apply"])
        require(partial.returncode == 2 and "not a directory" in partial.stderr, "invalid target parent did not fail clearly")
        require(not (blocked / "AGENTS.md").exists(), "preflight failure left a partial installation")
        require(not (blocked / "ai-workflow/install-manifest.json").exists(), "preflight failure wrote a manifest")


def copy_framework(destination: Path) -> Path:
    source = destination / "framework"
    shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
    return source


def check_adoption_update_evolution_and_version_guard() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-workflow-evolution-verification-") as temporary:
        base = Path(temporary)
        source = copy_framework(base)
        target = base / "consumer"
        target.mkdir()
        install = run_adopt_from(source, ["install", str(target), "--apply"])
        require(install.returncode == 0, f"evolution-test install failed: {install.stderr}")
        installed_version = json.loads((target / "ai-workflow/install-manifest.json").read_text(encoding="utf-8"))["framework_version"]
        old_readme = (target / "ai-workflow/README.md").read_bytes()

        manifest_path = source / "distribution/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["framework_owned"].remove("ai-workflow/README.md")
        seed_dir = source / "distribution/evolution-seeds"
        seed_dir.mkdir()
        (seed_dir / "reclassified.md").write_text("new default that must not overwrite old content\n", encoding="utf-8")
        (seed_dir / "new.md").write_text("new project seed\n", encoding="utf-8")
        manifest["project_seeds"].extend([
            {"source": "distribution/evolution-seeds/reclassified.md", "target": "ai-workflow/README.md"},
            {"source": "distribution/evolution-seeds/new.md", "target": "ai-workflow/new-project-owned.md"},
        ])
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        update = run_adopt_from(source, ["update", str(target), "--apply"])
        require(update.returncode == 0, f"ownership-transition update failed: {update.stderr}")
        require((target / "ai-workflow/README.md").read_bytes() == old_readme, "owned-to-project transition overwrote or deleted content")
        require((target / "ai-workflow/new-project-owned.md").read_text(encoding="utf-8") == "new project seed\n", "update did not add a new project seed")
        installed = json.loads((target / "ai-workflow/install-manifest.json").read_text(encoding="utf-8"))
        require("ai-workflow/README.md" not in installed["framework_files"], "reclassified file remained framework-owned")

        (source / "VERSION").write_text("0.0.1\n", encoding="utf-8")
        manifest["framework_version"] = "0.0.1"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        downgrade = run_adopt_from(source, ["update", str(target), "--apply"])
        require(downgrade.returncode == 2 and "refusing downgrade" in downgrade.stderr, "update accepted a version downgrade")
        current = json.loads((target / "ai-workflow/install-manifest.json").read_text(encoding="utf-8"))
        require(current["framework_version"] == installed_version, "downgrade changed installed version")


def check_adoption_transaction_rollback_and_revision() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-workflow-transaction-verification-") as temporary:
        base = Path(temporary)
        module_path = ROOT / "scripts/adopt.py"
        spec = importlib.util.spec_from_file_location("adopt_transaction_test", module_path)
        require(spec is not None and spec.loader is not None, "could not load adopter for rollback test")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        target = base / "transaction"
        target.mkdir()
        target = target.resolve()
        first = target / "first.txt"
        second = target / "second.txt"
        first.write_text("original first\n", encoding="utf-8")
        second.write_text("original second\n", encoding="utf-8")
        first.chmod(0o640)
        second.chmod(0o600)
        original_atomic_write = module.atomic_write

        module.apply_transaction(target, [("first.txt", b"replacement first\n")], (), {"first.txt": 0o755})
        require(first.read_text(encoding="utf-8") == "replacement first\n", "replacement transaction did not write data")
        require(stat.S_IMODE(first.stat().st_mode) == 0o640, "replacement transaction did not preserve the target mode")

        created = target / "created-tool"
        module.apply_transaction(target, [("created-tool", b"#!/bin/sh\n")], (), {"created-tool": 0o755})
        require(created.read_bytes() == b"#!/bin/sh\n", "transaction did not create the requested file")
        require(stat.S_IMODE(created.stat().st_mode) == 0o755, "new transaction target did not use its reviewed source mode")

        original_atomic_write(first, b"original first\n", 0o640)
        original_atomic_write(second, b"original second\n", 0o600)
        transient = target / "transient-tool"
        calls = {"count": 0}

        def fail_third_write(path: Path, data: bytes, mode: int = module.DEFAULT_CREATED_MODE) -> None:
            calls["count"] += 1
            if calls["count"] == 3:
                raise OSError("injected write failure")
            original_atomic_write(path, data, mode)

        module.atomic_write = fail_third_write
        try:
            try:
                module.apply_transaction(
                    target,
                    [
                        ("first.txt", b"changed first\n"),
                        ("transient-tool", b"#!/bin/sh\n"),
                        ("second.txt", b"changed second\n"),
                    ],
                    (),
                    {"transient-tool": 0o755},
                )
            except module.AdoptionError as error:
                require("rolled back" in str(error), f"transaction failure did not report rollback: {error}")
            else:
                raise VerificationFailure("injected transaction failure unexpectedly succeeded")
        finally:
            module.atomic_write = original_atomic_write
        require(first.read_text(encoding="utf-8") == "original first\n", "transaction rollback did not restore the first file")
        require(second.read_text(encoding="utf-8") == "original second\n", "transaction failure changed the second file")
        require(not transient.exists(), "transaction rollback did not remove a newly created file")
        require(stat.S_IMODE(first.stat().st_mode) == 0o640, "transaction rollback did not restore the first file mode")
        require(stat.S_IMODE(second.stat().st_mode) == 0o600, "transaction rollback did not restore the second file mode")

        calls = {"count": 0}

        def interrupt_second_write(path: Path, data: bytes, mode: int = module.DEFAULT_CREATED_MODE) -> None:
            calls["count"] += 1
            if calls["count"] == 2:
                raise KeyboardInterrupt("injected interrupt")
            original_atomic_write(path, data, mode)

        module.atomic_write = interrupt_second_write
        try:
            try:
                module.apply_transaction(
                    target,
                    [("first.txt", b"interrupted first\n"), ("second.txt", b"interrupted second\n")],
                    (),
                )
            except KeyboardInterrupt:
                pass
            else:
                raise VerificationFailure("injected transaction interrupt unexpectedly succeeded")
        finally:
            module.atomic_write = original_atomic_write
        require(first.read_text(encoding="utf-8") == "original first\n", "interrupt rollback did not restore the first file")
        require(second.read_text(encoding="utf-8") == "original second\n", "interrupt rollback changed the second file")
        require(stat.S_IMODE(first.stat().st_mode) == 0o640, "interrupt rollback did not restore the first file mode")
        require(stat.S_IMODE(second.stat().st_mode) == 0o600, "interrupt rollback did not restore the second file mode")

        mode_source = copy_framework(base / "mode-source")
        executable_source = mode_source / "ai-workflow/README.md"
        executable_source.chmod(0o755)
        mode_target = base / "mode-consumer"
        mode_target.mkdir()
        mode_install = run_adopt_from(mode_source, ["install", str(mode_target), "--apply"])
        require(mode_install.returncode == 0, f"mode-preservation install failed: {mode_install.stderr}")
        require(
            stat.S_IMODE((mode_target / "ai-workflow/README.md").stat().st_mode) == 0o755,
            "install did not preserve a reviewed executable source mode",
        )
        require(
            stat.S_IMODE((mode_target / "AGENTS.md").stat().st_mode) == 0o644,
            "install did not preserve a reviewed non-executable source mode",
        )
        require(
            stat.S_IMODE((mode_target / "ai-workflow/install-manifest.json").stat().st_mode) == 0o644,
            "install manifest did not use the safe default mode",
        )

        (mode_source / "AGENTS.md").chmod(0o600)
        unreviewed_target = base / "unreviewed-mode-consumer"
        unreviewed_target.mkdir()
        rejected = run_adopt_from(mode_source, ["install", str(unreviewed_target), "--apply"])
        require(
            rejected.returncode == 2 and "mode must be one of" in rejected.stderr,
            "install accepted an unreviewed source file mode",
        )
        require(not (unreviewed_target / "AGENTS.md").exists(), "source-mode rejection left a partial installation")

        source = copy_framework(base / "revision-source")
        for command in (
            ["git", "init"],
            ["git", "config", "user.email", "verification@example.invalid"],
            ["git", "config", "user.name", "Framework Verification"],
            ["git", "add", "."],
            ["git", "commit", "-m", "verification baseline"],
        ):
            result = subprocess.run(command, cwd=str(source), capture_output=True, text=True, timeout=20)
            require(result.returncode == 0, f"revision test setup failed for {' '.join(command)}: {result.stderr}")
        with (source / "AGENTS.md").open("a", encoding="utf-8") as handle:
            handle.write("\nDirty source marker.\n")
        revision_target = base / "revision-consumer"
        revision_target.mkdir()
        install = run_adopt_from(source, ["install", str(revision_target), "--apply"])
        require(install.returncode == 0, f"dirty-source install failed: {install.stderr}")
        installed = json.loads((revision_target / "ai-workflow/install-manifest.json").read_text(encoding="utf-8"))
        require(installed["source_revision"].endswith("-dirty"), "dirty source was recorded as a clean immutable revision")


def check_adoption_symlink_guards() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-workflow-symlink-verification-") as temporary:
        target = Path(temporary) / "consumer"
        outside = Path(temporary) / "outside"
        target.mkdir()
        outside.mkdir()
        (target / ".agents").symlink_to(outside, target_is_directory=True)
        result = run_adopt(["install", str(target), "--apply"])
        require(result.returncode == 2 and "symlink" in result.stderr, "install did not reject a symlinked target ancestor")
        require(not (outside / "skills").exists(), "install wrote through a target symlink")


def check_adoption_legacy_layout_migration() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-workflow-legacy-migration-") as temporary:
        target = Path(temporary) / "consumer"
        legacy_policy = target / ".github/copilot-instructions.md"
        legacy_skill = target / ".github/skills/workflow-teach/SKILL.md"
        legacy_skill.parent.mkdir(parents=True)
        managed = b"# Legacy managed workflow\n"
        project = b"# Preserved project Copilot guidance\n\nKeep this rule.\n"
        composite = (
            b"<!-- ai-workflow:managed-begin -->\n"
            + managed
            + b"<!-- ai-workflow:managed-end -->\n\n"
            + b"<!-- ai-workflow:project-instructions -->\n"
            + project
        )
        legacy_policy.write_bytes(composite)
        legacy_skill.write_text("legacy unchanged skill\n", encoding="utf-8")
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest = {
            "schema_version": 1,
            "framework_version": "0.1.0",
            "source_revision": "legacy-verification-fixture",
            "installed_at": "2026-08-11T00:00:00+00:00",
            "framework_files": {
                ".github/copilot-instructions.md": {
                    "sha256": hashlib.sha256(composite).hexdigest(),
                    "source_sha256": hashlib.sha256(managed).hexdigest(),
                    "origin": "composite",
                },
                ".github/skills/workflow-teach/SKILL.md": {
                    "sha256": hashlib.sha256(legacy_skill.read_bytes()).hexdigest(),
                    "source_sha256": hashlib.sha256(legacy_skill.read_bytes()).hexdigest(),
                    "origin": "created",
                },
            },
            "project_owned": ["ai-workflow/project-profile.md", "ai-workflow/state/active.md"],
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        update = run_adopt(["update", str(target), "--apply"])
        require(update.returncode == 0, f"legacy layout migration failed: {update.stderr}")
        require(legacy_policy.read_bytes() == composite, "legacy composite policy was changed without separately reviewed ownership evidence")
        require(legacy_skill.read_text(encoding="utf-8") == "legacy unchanged skill\n", "legacy framework path was changed without separately reviewed ownership evidence")
        require((target / "AGENTS.md").is_file(), "legacy migration did not install the shared root policy")
        require((target / ".agents/skills/workflow-teach/SKILL.md").is_file(), "legacy migration did not install canonical skills")
        installed = json.loads(manifest_path.read_text(encoding="utf-8"))
        require(installed["framework_version"] == read(Path("VERSION")).strip(), "legacy migration did not update the version")
        require(not any(path.startswith(".github/") for path in installed["framework_files"]), "legacy paths remain framework-owned after migration")
        require(
            ".github/copilot-instructions.md" in installed["project_owned"]
            and ".github/skills/workflow-teach/SKILL.md" in installed["project_owned"],
            "preserved legacy paths were not reclassified as project-owned",
        )


REQUEST_SCHEMA_FIELDS = {
    "schema_version",
    "task_id",
    "objective",
    "delegation_reason",
    "scope",
    "project_context",
    "known_facts",
    "constraints",
    "prohibited_actions",
    "repository_modification_allowed",
    "network_reads_authorized",
    "external_writes_authorized",
    "expected_output",
    "state_references",
    "evidence_requirements",
}
RESULT_SCHEMA_FIELDS = {
    "schema_version",
    "task_id",
    "status",
    "conclusions",
    "evidence",
    "sources",
    "assumptions",
    "tools_used",
    "repository_files_inspected",
    "unresolved_uncertainty",
    "recommendations",
    "actions_performed",
    "prohibited_actions_not_performed",
    "parent_verification_required",
}


def check_strict_object_schema(path: Path, expected_properties: Set[str]) -> Mapping[str, object]:
    schema = json.loads(read(path))
    require(isinstance(schema, dict), f"{path} must contain a JSON object")
    require(
        set(schema) == {"$schema", "$id", "title", "type", "additionalProperties", "required", "properties"},
        f"{path} has unknown or missing top-level schema fields",
    )
    require(schema["type"] == "object" and schema["additionalProperties"] is False, f"{path} must be a closed object schema")
    properties = schema["properties"]
    required = schema["required"]
    require(isinstance(properties, dict) and set(properties) == expected_properties, f"{path} properties differ from the adapter contract")
    require(isinstance(required, list) and len(required) == len(set(required)), f"{path} required must be a unique array")
    require(set(required) == expected_properties, f"{path} must require every declared property")
    return schema


def check_hermes_contracts_and_repo_read_gate() -> None:
    request = check_strict_object_schema(Path("adapters/hermes/request.schema.json"), REQUEST_SCHEMA_FIELDS)
    result = check_strict_object_schema(Path("adapters/hermes/result.schema.json"), RESULT_SCHEMA_FIELDS)
    request_properties = request["properties"]
    result_properties = result["properties"]
    require(isinstance(request_properties, dict) and isinstance(result_properties, dict), "Hermes schema properties are malformed")
    require(request_properties["repository_modification_allowed"] == {"const": False}, "request schema permits repository modification")
    require(request_properties["network_reads_authorized"] == {"const": True}, "request schema does not require authorized network reads")
    require(request_properties["external_writes_authorized"] == {"const": False}, "request schema permits external writes")
    require(result_properties["prohibited_actions_not_performed"] == {"const": True}, "result schema does not require prohibition confirmation")

    adapter = read(Path("scripts/hermes_adapter.py"))
    require('EXPECTED_VERSION_LINE = "Hermes Agent v0.20.0 (2026.8.3)"' in adapter, "adapter is not pinned to audited Hermes v0.20.0")
    require('PROVIDER = "openai-codex"' in adapter, "adapter is not pinned to the OpenAI/Codex provider")
    require('TOOLSETS = "web,memory,skills"' in adapter, "adapter research toolsets differ from the reviewed minimum")
    repo_read = re.search(
        r"^def command_repo_read\(.*?\n(?=^def )",
        adapter,
        flags=re.MULTILINE | re.DOTALL,
    )
    require(repo_read is not None, "adapter lacks an explicit repo-read compatibility gate")
    gate = repo_read.group(0)
    for token in ('"state": "unavailable"', "Codex app-server :read-only", "isolated CODEX_HOME", "write canaries", "return 4"):
        require(token in gate, f"repo-read compatibility gate lacks {token!r}")
    require("run_hermes(" not in gate and "preflight(" not in gate and "Popen(" not in gate, "repo-read gate can invoke a runtime despite being unavailable")

    skill = read(Path(".agents/skills/hermes-delegation/SKILL.md"))
    require("`disabled`" in skill and "`research`" in skill and "`repo-read`" in skill, "Hermes skill lacks the three capability levels")
    require("repo-read" in skill and "unavailable" in skill, "Hermes skill does not expose the compatibility-gated repo-read status")
    require("Write-capable Hermes repository delegation is outside this MVP." in skill, "Hermes skill does not reject write-capable repository delegation")
    profile = read(Path("adapters/hermes/profile-config.yaml"))
    for token in (
        "external_dirs: []",
        "write_approval: true",
        "guard_agent_created: true",
        "curator:",
        "enabled: true",
        "prune_builtins: false",
    ):
        require(token in profile, f"Hermes profile lacks private-learning boundary {token!r}")
    require(".agents/skills" not in profile, "Hermes profile exposes the shared skill tree as a mutable external directory")
    smoke = json.loads(read(Path("adapters/hermes/smoke-request.json")))
    require(isinstance(smoke, dict) and set(smoke) == REQUEST_SCHEMA_FIELDS, "Hermes smoke request fields differ from the request contract")
    require(smoke["repository_modification_allowed"] is False and smoke["external_writes_authorized"] is False, "Hermes smoke request permits writes")
    repo_read_cases = json.loads(read(Path("tests/hermes-repo-read-scenarios.json")))
    require(isinstance(repo_read_cases, list) and [item.get("id") for item in repo_read_cases] == ["RR-1", "RR-2", "RR-3"], "repo-read acceptance cases are incomplete")
    learning_cases = json.loads(read(Path("tests/hermes-learning-scenarios.json")))
    require(isinstance(learning_cases, list) and [item.get("id") for item in learning_cases] == ["HL-1", "HL-2", "HL-3", "HL-4", "HL-5"], "Hermes private-learning acceptance cases are incomplete")
    policy = read(Path("AGENTS.md"))
    verification = read(Path(".agents/skills/workflow-verification/SKILL.md"))
    for token in ("reusable", "duplication", "staleness", "narrowest", "reviewable"):
        require(token in policy + verification, f"controlled-learning policy lacks {token!r}")


HERMES_DOUBLE = r'''#!/usr/bin/env python3
import datetime as dt
import json
import os
from pathlib import Path
import signal
import sys
import time

args = sys.argv[1:]
profile_root = Path(os.environ["HERMES_HOME"])
control_path = profile_root / "double-control.json"
control = json.loads(control_path.read_text(encoding="utf-8")) if control_path.exists() else {}
log_path = control.get("log")
forbidden_names = {
    "OPENAI_API_KEY", "AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN", "CODEX_API_KEY",
    "HERMES_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY",
}
record = {
    "argv": args,
    "chain": os.environ.get("AI_ENGINEERING_WORKFLOW_CHAIN"),
    "cwd": str(Path.cwd()),
    "hermes_home": str(profile_root),
    "home": os.environ.get("HOME"),
    "codex_home": os.environ.get("CODEX_HOME"),
    "tmpdir": os.environ.get("TMPDIR"),
    "path": os.environ.get("PATH"),
    "forbidden_env": sorted(forbidden_names.intersection(os.environ)),
}
if log_path:
    with Path(log_path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")

mode = control.get("mode", "success")
if args == ["--version"]:
    print("Hermes Agent v0.19.0 (2026.7.1)" if mode == "incompatible" else
          "Hermes Agent v0.20.0 (2026.8.3)")
    raise SystemExit(0)

if mode in {"mutate", "interrupt-mutate"}:
    name = "interrupt-write.txt" if mode == "interrupt-mutate" else "unauthorized-hermes-write.txt"
    Path(control["repo"], name).write_text("hostile write\n", encoding="utf-8")
    if mode == "interrupt-mutate":
        os.kill(os.getppid(), signal.SIGINT)
        time.sleep(10)
if mode == "chmod-mutate":
    Path(control["repo"], "baseline.txt").chmod(0o600)
if mode == "fifo-mutate":
    os.mkfifo(Path(control["repo"], "unauthorized-hermes-fifo"))
if mode == "oversize":
    sys.stdout.write("x" * 1100000)
    sys.stdout.flush()
    time.sleep(10)

url = "https://example.invalid/source"
if mode == "credential-url":
    url = "https://example.invalid/source?ToKeN=fixture-secret"
elif mode == "presigned-url":
    url = "https://example.invalid/source?X-Amz-Credential=fixture&X-Amz-Signature=fixture"
elif mode == "fragment-token-url":
    url = "https://example.invalid/source#access_token=fixture-secret"
elif mode == "malformed-url":
    url = "https://[::1"
tools = ["web"] if mode == "pseudo-tool" else ["web_search"]
today = dt.date.today().isoformat()
result = {
    "schema_version": 1,
    "task_id": "VERIFY-HERMES-1",
    "status": "success",
    "conclusions": ["The controlled research result is complete."],
    "evidence": [{
        "claim": "The fixture completed.",
        "support": "The deterministic double returned its reviewed result envelope.",
        "source_urls": [url],
    }],
    "sources": [{
        "title": "Controlled source",
        "url": url,
        "publisher": "Framework verification fixture",
        "accessed": today,
    }],
    "assumptions": [],
    "tools_used": tools,
    "repository_files_inspected": [],
    "unresolved_uncertainty": [],
    "recommendations": ["Parent Codex should verify material claims."],
    "actions_performed": ["Read a controlled external source."],
    "prohibited_actions_not_performed": True,
    "parent_verification_required": ["Validate the cited source."],
}
print(json.dumps(result, sort_keys=True))
'''


def write_hermes_double(path: Path) -> None:
    path.write_text(HERMES_DOUBLE, encoding="utf-8")
    path.chmod(0o755)


def create_adapter_fixture(base: Path) -> Tuple[Path, Path, Path, Path, Path]:
    profile_root = base / "isolated-hermes"
    install_root = profile_root / "hermes-agent"
    install_root.mkdir(parents=True, mode=0o700)
    executable = install_root / "hermes-double"
    write_hermes_double(executable)
    venv_bin = install_root / "venv" / "bin"
    venv_bin.mkdir(parents=True)
    write_hermes_double(venv_bin / "python")
    (install_root / "hermes").write_text("# pinned source launcher fixture\n", encoding="utf-8")
    profile_dir = profile_root / "profiles" / "ai-engineering-workflow"
    profile_dir.mkdir(parents=True, mode=0o700)
    profile_root.chmod(0o700)
    profile_dir.chmod(0o700)
    for private in (profile_root / "home", profile_root / "codex-home", profile_root / "tmp"):
        private.mkdir(mode=0o700)
    shutil.copy2(ROOT / "adapters/hermes/profile-config.yaml", profile_dir / "config.yaml")
    (profile_dir / ".no-bundled-skills").write_text("", encoding="utf-8")
    auth = {
        "providers": {
            "openai-codex": {
                "tokens": {
                    "access_token": "fixture-access-token",
                    "refresh_token": "fixture-refresh-token",
                }
            }
        }
    }
    auth_path = profile_dir / "auth.json"
    auth_path.write_text(json.dumps(auth), encoding="utf-8")
    auth_path.chmod(0o600)
    repository = base / "repository"
    repository.mkdir()
    (repository / "baseline.txt").write_text("unchanged\n", encoding="utf-8")
    request = base / "request.json"
    payload = {
        "schema_version": 1,
        "task_id": "VERIFY-HERMES-1",
        "objective": "Research one controlled compatibility claim.",
        "delegation_reason": "The fixture verifies the bounded adapter contract.",
        "scope": ["One controlled external source."],
        "project_context": [],
        "known_facts": [],
        "constraints": ["Do not inspect or modify the repository."],
        "prohibited_actions": ["Do not invoke Codex or perform external writes."],
        "repository_modification_allowed": False,
        "network_reads_authorized": True,
        "external_writes_authorized": False,
        "expected_output": ["Return the strict result contract."],
        "state_references": [],
        "evidence_requirements": ["Cite the controlled source."],
    }
    request.write_text(json.dumps(payload), encoding="utf-8")
    log = base / "calls.jsonl"
    return executable, profile_root, repository, request, log


def configure_double(profile_root: Path, log: Path, mode: str = "success", repository: Optional[Path] = None) -> None:
    payload = {"log": str(log), "mode": mode}
    if repository is not None:
        payload["repo"] = str(repository)
    (profile_root / "double-control.json").write_text(json.dumps(payload), encoding="utf-8")


def run_adapter(args: Sequence[str], environment: Optional[Mapping[str, str]] = None) -> subprocess.CompletedProcess:
    process_environment = os.environ.copy()
    if environment:
        process_environment.update(environment)
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/hermes_adapter.py"), *args],
        cwd=str(ROOT),
        env=process_environment,
        capture_output=True,
        text=True,
        timeout=20,
    )


def double_calls(path: Path) -> List[Mapping[str, object]]:
    if not path.exists():
        return []
    values = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    require(all(isinstance(item, dict) for item in values), "Hermes double call log is malformed")
    return values


def research_arguments(executable: Path, profile_root: Path, repository: Path, request: Path) -> List[str]:
    return [
        "research",
        "--hermes",
        str(executable),
        "--profile-root",
        str(profile_root),
        "--repo",
        str(repository),
        "--request",
        str(request),
        "--network-authorized",
        "--timeout",
        "20",
    ]


def check_hermes_adapter_preflight_simulations() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-workflow-hermes-preflight-") as temporary:
        base = Path(temporary)
        executable, profile_root, repository, request, log = create_adapter_fixture(base)
        profile_dir = profile_root / "profiles" / "ai-engineering-workflow"
        configure_double(profile_root, log)

        absent = run_adapter(
            ["status", "--hermes", "hermes-verification-definitely-absent", "--profile-root", str(profile_root)],
        )
        require(absent.returncode == 3, f"absent Hermes status was not optional-disabled: {absent.stderr}")
        absent_payload = json.loads(absent.stdout)
        require(absent_payload["state"] == "disabled" and absent_payload["capability"] == "research", "absent Hermes status payload is not safely degraded")
        require((repository / "baseline.txt").read_text(encoding="utf-8") == "unchanged\n", "absent Hermes preflight changed the repository")

        unavailable_repo_read = run_adapter(
            ["repo-read", "--hermes", str(executable), "--profile-root", str(base / "missing-profile")],
        )
        require(unavailable_repo_read.returncode == 4, "repo-read compatibility gate did not return incompatible status")
        repo_read_payload = json.loads(unavailable_repo_read.stdout)
        require(repo_read_payload["state"] == "unavailable" and repo_read_payload["capability"] == "repo-read", "repo-read gate reported a usable capability")
        require(not double_calls(log), "repo-read compatibility gate invoked Hermes")

        configure_double(profile_root, log, "incompatible")
        incompatible = run_adapter(
            ["status", "--hermes", str(executable), "--profile-root", str(profile_root)]
        )
        require(incompatible.returncode == 4 and "incompatible Hermes version" in incompatible.stdout, "incompatible Hermes version did not fail closed")
        calls = double_calls(log)
        require(len(calls) == 1 and calls[0]["argv"] == ["--version"], "incompatible Hermes continued past the version probe")

        log.unlink()
        configure_double(profile_root, log)
        auth_path = profile_dir / "auth.json"
        saved_auth = auth_path.read_bytes()
        auth_path.write_text("{malformed", encoding="utf-8")
        malformed_auth = run_adapter(
            ["status", "--hermes", str(executable), "--profile-root", str(profile_root)]
        )
        require(
            malformed_auth.returncode == 5 and "malformed" in malformed_auth.stdout,
            "malformed local auth store did not fail closed",
        )
        require(not double_calls(log), "malformed auth store invoked Hermes before rejection")
        auth_path.write_bytes(saved_auth)

        generated_config = (profile_dir / "config.yaml").read_text(encoding="utf-8").replace(
            "model:\n", "model:\n  provider: openai-codex\n  base_url: https://chatgpt.com/backend-api/codex\n", 1
        )
        (profile_dir / "config.yaml").write_text(generated_config, encoding="utf-8")
        generated = run_adapter(
            ["status", "--hermes", str(executable), "--profile-root", str(profile_root)]
        )
        require(
            generated.returncode == 5 and "byte-identical" in generated.stdout,
            "auth-mutated generated profile was accepted before canonical replacement",
        )
        require(not double_calls(log), "unsafe generated profile invoked Hermes before rejection")
        shutil.copy2(ROOT / "adapters/hermes/profile-config.yaml", profile_dir / "config.yaml")

        configure_double(profile_root, log)
        ready = run_adapter(
            ["status", "--hermes", str(executable), "--profile-root", str(profile_root)],
        )
        require(ready.returncode == 0, f"valid Hermes preflight failed: {ready.stderr}")
        ready_payload = json.loads(ready.stdout)
        require(
            ready_payload["state"] == "ready"
            and ready_payload["provider"] == "openai-codex"
            and ready_payload["toolsets"] == ["web", "memory", "skills"]
            and ready_payload["repository_access"] == "none",
            "valid Hermes preflight reported an unexpected capability",
        )
        require(
            ready_payload["authentication"] == "locally-configured-unverified"
            and ready_payload["network_probe_performed"] is False
            and ready_payload["source_attested"] is False,
            "status did not clearly classify local-only auth and the explicit test override",
        )

        log.unlink()
        pool = {
            "credential_pool": {
                "openai-codex": [{"access_token": "fixture-pool-access-token"}]
            }
        }
        auth_path.write_text(json.dumps(pool), encoding="utf-8")
        pool_ready = run_adapter(
            ["status", "--hermes", str(executable), "--profile-root", str(profile_root)]
        )
        require(pool_ready.returncode == 0, "valid profile-local openai-codex credential pool was rejected")
        require(json.loads(pool_ready.stdout)["authentication_store"] == "credential-pool", "credential pool classification was lost")


def load_hermes_adapter_module() -> Any:
    spec = importlib.util.spec_from_file_location("hermes_adapter_verification", ROOT / "scripts/hermes_adapter.py")
    require(spec is not None and spec.loader is not None, "cannot load Hermes adapter for helper verification")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check_hermes_official_runtime_attestation() -> None:
    module = load_hermes_adapter_module()
    with tempfile.TemporaryDirectory(prefix="ai-workflow-hermes-source-") as temporary:
        base = Path(temporary)
        executable, profile_root, _repository, _request, _log = create_adapter_fixture(base)
        layout = module.configured_layout(profile_root, "ai-engineering-workflow")
        python_link = profile_root / "hermes-agent/venv/bin/python"
        python_link.unlink()
        managed_python = profile_root / "uv-python/cpython-3.11/bin/python3"
        managed_python.parent.mkdir(parents=True)
        write_hermes_double(managed_python)
        python_link.symlink_to(os.path.relpath(managed_python, python_link.parent))
        command = module.hermes_command(None, layout)
        require(
            command == (
                str(layout.install_root / "venv/bin/python"),
                str(layout.install_root / "hermes"),
            ),
            f"default Hermes command does not match official installer layout: {command!r}",
        )
        python_link.unlink()
        python_link.symlink_to(Path("/usr/bin/python3"))
        try:
            module.hermes_command(None, layout)
        except module.AdapterError as error:
            require("escapes the profile root" in str(error), "escaping Python symlink failed for the wrong reason")
        else:
            raise VerificationFailure("escaping venv Python symlink was accepted")
        python_link.unlink()
        python_link.symlink_to(os.path.relpath(managed_python, python_link.parent))
        (profile_root / "hermes-agent/.git").mkdir()
        original = module.run_bounded_process
        calls: List[List[str]] = []

        def clean_git(argv: Sequence[str], **_kwargs: object) -> Any:
            calls.append(list(argv))
            stdout = module.EXPECTED_SOURCE_REVISION + "\n" if "rev-parse" in argv else ""
            return module.ProcessResult(0, stdout, "")

        module.run_bounded_process = clean_git
        try:
            module.attest_source_checkout(layout)
            require(any("rev-parse" in call for call in calls), "source attestation omitted exact HEAD lookup")
            require(any("--untracked-files=all" in call for call in calls), "source attestation omitted untracked source check")
            status_calls = [call for call in calls if "status" in call]
            require(
                status_calls and all("--no-optional-locks" in call for call in status_calls),
                "source cleanliness attestation permits Git to refresh repository metadata",
            )

            def dirty_git(argv: Sequence[str], **_kwargs: object) -> Any:
                stdout = module.EXPECTED_SOURCE_REVISION + "\n" if "rev-parse" in argv else "?? injected_module.py\n"
                return module.ProcessResult(0, stdout, "")

            module.run_bounded_process = dirty_git
            try:
                module.attest_source_checkout(layout)
            except module.AdapterError as error:
                require("tracked or untracked changes" in str(error), "dirty source failed for the wrong reason")
            else:
                raise VerificationFailure("dirty pinned Hermes source was accepted")

            def wrong_head(argv: Sequence[str], **_kwargs: object) -> Any:
                stdout = "0" * 40 + "\n" if "rev-parse" in argv else ""
                return module.ProcessResult(0, stdout, "")

            module.run_bounded_process = wrong_head
            try:
                module.attest_source_checkout(layout)
            except module.AdapterError as error:
                require("revision mismatch" in str(error), "wrong source HEAD failed for the wrong reason")
            else:
                raise VerificationFailure("wrong Hermes source HEAD was accepted")
        finally:
            module.run_bounded_process = original

        real_repository = base / "real-git-repository"
        empty_template = base / "empty-git-template"
        empty_template.mkdir()
        git_environment = {
            "PATH": module.SYSTEM_BINARY_PATH,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "LANG": "C",
        }
        initialized = subprocess.run(
            [
                str(module._system_git()),
                "init",
                f"--template={empty_template}",
                str(real_repository),
            ],
            capture_output=True,
            text=True,
            timeout=20,
            env=git_environment,
        )
        require(initialized.returncode == 0, f"real-Git guard fixture initialization failed: {initialized.stderr}")
        tracked = real_repository / "tracked.txt"
        tracked.write_bytes(b"tracked bytes\n")
        tracked.chmod(0o640)
        added = subprocess.run(
            [str(module._system_git()), "-C", str(real_repository), "add", "tracked.txt"],
            capture_output=True,
            text=True,
            timeout=20,
            env=git_environment,
        )
        require(added.returncode == 0, f"real-Git guard fixture add failed: {added.stderr}")
        tracked_metadata = tracked.stat()
        os.utime(
            tracked,
            ns=(tracked_metadata.st_atime_ns, tracked_metadata.st_mtime_ns + 2_000_000_000),
        )
        hardlink_source = real_repository / "hardlink-source.txt"
        hardlink_source.write_bytes(b"linked bytes\n")
        os.link(hardlink_source, real_repository / "hardlink-alias.txt")
        (real_repository / "tracked-link").symlink_to("tracked.txt")
        fifo = real_repository / "special-fifo"
        if hasattr(os, "mkfifo"):
            os.mkfifo(fifo)

        before_status_probe = module.snapshot_repository(real_repository)
        tracked_snapshot = before_status_probe["tracked.txt"]
        require(
            tracked_snapshot[0] == "file"
            and tracked_snapshot[1] == hashlib.sha256(b"tracked bytes\n").hexdigest()
            and tracked_snapshot[2] == 0o640,
            "real-Git canary does not cover repository bytes and mode metadata",
        )
        require(
            before_status_probe["hardlink-source.txt"][3] == 2
            and before_status_probe["hardlink-alias.txt"][3] == 2,
            "real-Git canary does not cover hard-link metadata",
        )
        require(before_status_probe["tracked-link"][0] == "symlink", "real-Git canary lacks symlink metadata")
        if hasattr(os, "mkfifo"):
            require(before_status_probe["special-fifo"][0] == "fifo", "real-Git canary lacks special-file metadata")

        module.git_status(real_repository)
        after_status_probe = module.snapshot_repository(real_repository)
        require(
            before_status_probe == after_status_probe,
            "repository Git status probe mutated byte, mode, link, or special-file state",
        )


def check_hermes_adapter_success_and_argv() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-workflow-hermes-success-") as temporary:
        base = Path(temporary)
        executable, profile_root, repository, request, log = create_adapter_fixture(base)
        resolved_root = profile_root.resolve()
        configure_double(profile_root, log)
        result = run_adapter(
            research_arguments(executable, profile_root, repository, request),
            {
                "OPENAI_API_KEY": "verification-sentinel-must-not-propagate",
                "AWS_SECRET_ACCESS_KEY": "verification-sentinel-must-not-propagate",
                "GITHUB_TOKEN": "verification-sentinel-must-not-propagate",
            },
        )
        require(result.returncode == 0, f"valid structured Hermes result failed: {result.stderr}")
        payload = json.loads(result.stdout)
        require(payload["status"] == "success" and payload["task_id"] == "VERIFY-HERMES-1", "valid Hermes result was not returned intact")
        require((repository / "baseline.txt").read_text(encoding="utf-8") == "unchanged\n", "successful research changed the protected repository")

        calls = double_calls(log)
        require(len(calls) == 2, f"successful research expected local version and invocation calls; got {len(calls)}")
        require(all("auth" not in call["argv"] for call in calls), "local-only status invoked Hermes auth and could have performed network I/O")
        require(
            calls[0]["argv"] == ["--version"]
            and Path(calls[0]["cwd"]) == resolved_root / "tmp",
            "Hermes version probe did not run from the isolated temporary root",
        )
        invocation = calls[1]
        argv = invocation["argv"]
        require(isinstance(argv, list), "captured Hermes argv is not an array")
        require(
            argv[:4] == ["-p", "ai-engineering-workflow", "chat", "-q"]
            and argv[5] == "-Q"
            and argv[6::2] == ["--provider", "--toolsets", "--source", "--max-turns"],
            f"Hermes invocation argv shape changed: {argv!r}",
        )
        require(argv[1] == "ai-engineering-workflow", "Hermes invocation used the wrong profile")
        require(argv[argv.index("--provider") + 1] == "openai-codex", "Hermes invocation permitted a provider fallback")
        toolsets = argv[argv.index("--toolsets") + 1].split(",")
        require(toolsets == ["web", "memory", "skills"], f"Hermes invocation toolsets changed: {toolsets!r}")
        unsafe_toolsets = {"file", "terminal", "browser", "delegation", "safe", "codex"}
        require(not unsafe_toolsets.intersection(toolsets), "Hermes invocation contains a write-capable or recursive toolset")
        unsafe_flags = {"--yolo", "-y", "-z", "-w", "--in", "--usage-file", "--accept-hooks", "--unsafe", "--no-approval", "--sandbox-bypass"}
        require(not unsafe_flags.intersection(argv), "Hermes invocation contains an unsafe execution flag")
        prompt = argv[argv.index("-q") + 1]
        require("Perform external web research only" in prompt and "Do not invoke Codex" in prompt, "delegated prompt lacks external-only or recursion boundaries")
        require(invocation["chain"] == "codex>hermes", "Hermes invocation lacks the recursion marker")
        require(invocation["forbidden_env"] == [], f"caller credential environment reached Hermes: {invocation['forbidden_env']}")
        require(invocation["hermes_home"] == str(resolved_root), "Hermes runtime did not receive the validated isolated root")
        require(invocation["home"] == str(resolved_root / "home"), "Hermes runtime did not receive the private HOME")
        require(invocation["codex_home"] == str(resolved_root / "codex-home"), "Hermes runtime did not receive the isolated CODEX_HOME")
        require(invocation["tmpdir"] == str(resolved_root / "tmp"), "Hermes runtime did not receive the safe temporary root")
        require(
            invocation["path"] == os.pathsep.join((str(resolved_root / "hermes-agent/venv/bin"), "/usr/bin:/bin:/usr/sbin:/sbin")),
            f"Hermes runtime inherited a nondeterministic PATH: {invocation['path']!r}",
        )
        require(not Path(invocation["cwd"]).is_relative_to(repository), "Hermes runtime started inside the protected repository")
        require(Path(invocation["cwd"]).is_relative_to(resolved_root / "tmp"), "Hermes runtime cwd did not use the isolated temp root")


def check_hermes_adapter_failure_guards() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-workflow-hermes-guards-") as temporary:
        base = Path(temporary)
        executable, profile_root, repository, request, log = create_adapter_fixture(base)
        configure_double(profile_root, log)

        recursion = run_adapter(
            research_arguments(executable, profile_root, repository, request),
            {"AI_ENGINEERING_WORKFLOW_CHAIN": "codex>hermes"},
        )
        require(recursion.returncode == 8 and "recursive delegation refused" in recursion.stderr, "recursion guard did not fail before invocation")
        require(not double_calls(log), "recursion guard invoked Hermes")

        no_network_args = research_arguments(executable, profile_root, repository, request)
        no_network_args.remove("--network-authorized")
        no_network = run_adapter(no_network_args)
        require(no_network.returncode == 9 and "network reads require explicit" in no_network.stderr, "missing network acknowledgement did not fail closed")
        require(not double_calls(log), "missing network acknowledgement still invoked Hermes")

        mutation_log = base / "mutation-calls.jsonl"
        configure_double(profile_root, mutation_log, "mutate", repository)
        hostile = run_adapter(
            research_arguments(executable, profile_root, repository, request),
        )
        require(hostile.returncode == 12 and "repository mutation guard failed" in hostile.stderr, "hostile repository mutation was not rejected")
        require("unauthorized-hermes-write.txt" in hostile.stderr, "mutation guard did not name the changed path")
        require((repository / "unauthorized-hermes-write.txt").is_file(), "hostile test double did not exercise the mutation guard")

        interrupt_log = base / "interrupt-calls.jsonl"
        configure_double(profile_root, interrupt_log, "interrupt-mutate", repository)
        interrupted = run_adapter(research_arguments(executable, profile_root, repository, request))
        require(
            interrupted.returncode == 12 and "repository mutation guard failed" in interrupted.stderr,
            "BaseException interrupted the mandatory post-mutation guard",
        )

        for mode, expected in (
            ("oversize", "bounded output limit"),
            ("pseudo-tool", "outside the research allowlist"),
            ("credential-url", "not HTTP(S)"),
            ("presigned-url", "not HTTP(S)"),
            ("fragment-token-url", "not HTTP(S)"),
            ("malformed-url", "not HTTP(S)"),
        ):
            mode_log = base / f"{mode}-calls.jsonl"
            configure_double(profile_root, mode_log, mode, repository)
            rejected = run_adapter(research_arguments(executable, profile_root, repository, request))
            require(
                rejected.returncode in {10, 11} and expected in rejected.stderr,
                f"{mode} output was not rejected safely: {rejected.stderr}",
            )

        for mode, changed_path in (
            ("chmod-mutate", "baseline.txt"),
            ("fifo-mutate", "unauthorized-hermes-fifo"),
        ):
            mode_log = base / f"{mode}-calls.jsonl"
            configure_double(profile_root, mode_log, mode, repository)
            rejected = run_adapter(research_arguments(executable, profile_root, repository, request))
            require(
                rejected.returncode == 12
                and "repository mutation guard failed" in rejected.stderr
                and changed_path in rejected.stderr,
                f"{mode} repository mutation evaded the guard: {rejected.stderr}",
            )

        configure_double(profile_root, base / "hardlink-calls.jsonl")
        source = base / "hardlink-source"
        source.write_text("linked\n", encoding="utf-8")
        linked = profile_root / "profiles/ai-engineering-workflow/SOUL.md"
        os.link(source, linked)
        hardlinked = run_adapter(
            ["status", "--hermes", str(executable), "--profile-root", str(profile_root)]
        )
        require(
            hardlinked.returncode == 5 and "hard link" in hardlinked.stdout,
            "unlisted profile-artifact hardlink was not rejected",
        )


def check_documentation_and_placeholders() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".py", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        bracket_placeholder = "[TO" + "DO"
        label_placeholder = "TO" + "DO:"
        require(bracket_placeholder not in text and label_placeholder not in text, f"unfinished placeholder in {path.relative_to(ROOT)}")
    platform = read(Path("docs/platform-research.md"))
    require(re.search(r"Inspected 2026-08-1[12]", platform) is not None, "platform research inspection date missing")
    for feature in ("Codex", "AGENTS.md", ".agents/skills", "Agent Skills", "Subagents", "app-server", "sandbox", "approvals", "Copilot", "Agent plugins", "Personal instructions"):
        require(feature in platform, f"platform research lacks {feature}")
    hermes = read(Path("docs/integrations/hermes.md"))
    for token in (
        "v0.20.0",
        "3c27eb6234bf91b8ceee9e9071591b31e9b148cb",
        "`disabled`",
        "`research`",
        "`repo-read`",
        "CODEX_HOME",
        "skills.write_approval",
        "profile-private",
        "separate parent-Codex change",
    ):
        require(token in hermes, f"Hermes integration guide lacks {token}")
    references = read(Path("docs/reference-research.md"))
    require("84fdeffd12f2ee307994d1eb6feb48173b6e0502" in references, "third-party immutable revision missing")
    for token in ("Wayfinder", "Teach", "to-spec", "to-tickets", "diagnosing-bugs", "tdd", "code-review", "implement", "writing-for-agents", "MIT"):
        require(token in references, f"reference research is incomplete: {token}")
    for token in ("2026-08-12", "disable-model-invocation: true", "allow_implicit_invocation: false", "dedicated", "temporary", "explicit opt-in"):
        require(token in references, f"current Wayfinder/Teach audit lacks {token!r}")
    license_text = read(Path("LICENSE.md"))
    for token in (
        "# MIT License",
        "Copyright (c) 2026 James Fan",
        "Permission is hereby granted, free of charge",
        'THE SOFTWARE IS PROVIDED "AS IS"',
    ):
        require(token in license_text, f"MIT license is incomplete: {token!r}")
    readme = read(Path("README.md"))
    require("[MIT License](LICENSE.md)" in readme, "README does not identify the repository's MIT license")
    require("[reference research](docs/reference-research.md)" in readme, "README does not link the retained third-party attribution")
    require("no Hermes source is\nredistributed here" in readme, "README does not state the Hermes redistribution boundary")
    require("No Hermes source, binary, skill, or installer is redistributed" in hermes, "Hermes guide lacks the redistribution boundary")


def check_markdown_links() -> None:
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            if target.startswith(("https://", "http://", "#")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            destination = (path.parent / clean).resolve()
            try:
                destination.relative_to(ROOT)
            except ValueError as exc:
                raise VerificationFailure(f"relative link escapes repository in {path.relative_to(ROOT)}: {target}") from exc
            require(destination.exists(), f"broken relative link in {path.relative_to(ROOT)}: {target}")


CHECKS: Sequence[Tuple[str, Callable[[], None]]] = (
    ("required files", check_required_files),
    ("Agent Skill metadata", check_skill_metadata),
    ("project profiles and command contract", check_profiles_and_contract),
    ("durable state contract", check_state_contract),
    ("32-scenario acceptance catalog", check_acceptance_catalog),
    ("30-scenario Codex/Hermes integration catalog", check_integration_acceptance_catalog),
    ("generic core boundary and optional dependency absence", check_generic_core),
    ("always-on context budget and duplication", check_context_budget_and_duplication),
    ("Hermes schemas and repo-read compatibility gate", check_hermes_contracts_and_repo_read_gate),
    ("Hermes optional, version, profile, and auth preflight simulations", check_hermes_adapter_preflight_simulations),
    ("Hermes official runtime source and interpreter attestation", check_hermes_official_runtime_attestation),
    ("Hermes structured result and exact invocation contract", check_hermes_adapter_success_and_argv),
    ("Hermes recursion, network, provider, and mutation guards", check_hermes_adapter_failure_guards),
    ("distribution manifest and ownership", check_distribution_manifest),
    ("adoption, conflict, update, and removal lifecycle", check_adoption_lifecycle),
    ("existing policy merge and pre-install provenance", check_adoption_existing_policy_and_provenance),
    ("tampered-manifest and partial-install guards", check_adoption_tamper_and_preflight_guards),
    ("ownership evolution and downgrade guards", check_adoption_update_evolution_and_version_guard),
    ("transaction rollback and dirty-source revision", check_adoption_transaction_rollback_and_revision),
    ("adoption symlink guards", check_adoption_symlink_guards),
    ("legacy Copilot-layout migration", check_adoption_legacy_layout_migration),
    ("documentation, research, and licensing completeness", check_documentation_and_placeholders),
    ("local Markdown links", check_markdown_links),
)


def main() -> int:
    failures: List[str] = []
    for name, check in CHECKS:
        try:
            check()
        except Exception as error:  # Keep later checks useful after one failure.
            failures.append(f"{name}: {error}")
            print(f"FAIL: {name}: {error}")
        else:
            print(f"PASS: {name}")
    if failures:
        print(f"FAILED: {len(failures)} verification check(s).")
        return 1
    print("OK: all framework verification checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
