#!/usr/bin/env python3
"""Six-run B-new regression wrapper around the frozen ITBench Wayfinder harness."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
HISTORICAL_ROOT = HERE.parents[1]
SOURCE_ROOT = HISTORICAL_ROOT.parents[1]
HISTORICAL_HARNESS_PATH = HISTORICAL_ROOT / "harness.py"
HISTORICAL_MANIFEST_PATH = HISTORICAL_ROOT / "frozen-manifest.json"
HISTORICAL_PROTOCOL_PATH = HISTORICAL_ROOT / "protocol.md"
HISTORICAL_RUBRIC_PATH = HISTORICAL_ROOT / "reasoning-rubric.md"
HISTORICAL_RESULTS_ROOT = HISTORICAL_ROOT / "results"
HISTORICAL_REPORTS_ROOT = HISTORICAL_ROOT / "reports"

CAMPAIGN_ID = "itbench-wayfinder-auto-regression-v1"
SCENARIOS = (102, 34, 83, 17, 24, 80)
MODEL = "gpt-5.6-terra"
REASONING_EFFORT = "medium"
TIMEOUT_SECONDS = 1800
MANIFEST_PATH = HERE / "frozen-manifest.json"
PREFLIGHT_PATH = HERE / "preflight.json"
AUDIT_PATH = HERE / "context-isolation-audit.json"
INTEGRITY_PATH = HERE / "post-run-integrity.json"
RESULTS_ROOT = HERE / "results"
REPORTS_ROOT = HERE / "reports"
ARTIFACTS_ROOT = HERE.parents[2] / "artifacts" / CAMPAIGN_ID
CONTROL_ROOT = Path(tempfile.gettempdir()) / ".k8s-sre-regression-controller-76df38a82288"
RUN_ROOT = Path(tempfile.gettempdir()) / ".k8s-sre-regression-runs-76df38a82288"


def load_historical_harness() -> Any:
    spec = importlib.util.spec_from_file_location("historical_itbench_harness", HISTORICAL_HARNESS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load historical harness")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_historical_harness()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return base.sha256_file(path)


def tree_hash(path: Path) -> str:
    return base.tree_hash(path)[0]


def run_identifier(scenario: int) -> str:
    return f"s{scenario}-b-new-r1"


def workspace_for(scenario: int) -> Path:
    return RUN_ROOT / f"case-{scenario}-r1" / "workspace"


def control_path(identifier: str) -> Path:
    return CONTROL_ROOT / "runs" / identifier / "control.json"


def load_run(identifier: str) -> dict[str, Any]:
    return read_json(control_path(identifier))


def save_run(record: dict[str, Any]) -> None:
    write_json(control_path(str(record["run_id"])), record)


def configure_base_for_campaign() -> None:
    base.CAMPAIGN_ID = CAMPAIGN_ID
    base.MANIFEST_PATH = MANIFEST_PATH
    base.RUBRIC_PATH = HISTORICAL_RUBRIC_PATH
    base.RUN_ROOT = RUN_ROOT
    base.RESULTS_ROOT = RESULTS_ROOT
    base.ARTIFACTS_ROOT = ARTIFACTS_ROOT
    base.load_run = load_run
    base.save_run = save_run


def historical_anchors() -> dict[str, str]:
    return {
        "manifest_sha256": sha256_file(HISTORICAL_MANIFEST_PATH),
        "protocol_sha256": sha256_file(HISTORICAL_PROTOCOL_PATH),
        "rubric_sha256": sha256_file(HISTORICAL_RUBRIC_PATH),
        "preflight_sha256": sha256_file(HISTORICAL_ROOT / "preflight.json"),
        "isolation_audit_sha256": sha256_file(HISTORICAL_ROOT / "context-isolation-audit.json"),
        "results_tree_sha256": tree_hash(HISTORICAL_RESULTS_ROOT),
        "reports_tree_sha256": tree_hash(HISTORICAL_REPORTS_ROOT),
    }


def matcher_source_hash() -> str:
    functions = (
        base.yaml_scalar,
        base.parse_matcher_ground_truth,
        base.prediction_matches_group,
        base.native_grade,
    )
    return sha256_bytes("\n\n".join(inspect.getsource(function) for function in functions).encode())


def product_contract_observations(root: Path = SOURCE_ROOT) -> dict[str, Any]:
    providers_path = root / ".ai-workflow" / "providers.json"
    payload_providers_path = (
        root / "skills" / "agentic-workflow" / "payload" / "ai-workflow" / "providers.json"
    )
    providers = read_json(providers_path)
    declared = providers["provider"]["skills"]
    by_name = {str(item["name"]): item for item in declared}
    declared_names = sorted(by_name)
    projected_root = root / ".agents" / "skills"
    projected_names = sorted(
        name for name in declared_names if (projected_root / name / "SKILL.md").is_file()
    )
    wayfinder_text = (projected_root / "wayfinder" / "SKILL.md").read_text(encoding="utf-8")
    openai_text = (projected_root / "wayfinder" / "agents" / "openai.yaml").read_text(encoding="utf-8")
    routing_text = (root / ".ai-workflow" / "routing.md").read_text(encoding="utf-8")
    state_contract = (
        root / ".ai-workflow" / "contracts" / "wayfinder-state.md"
    ).read_text(encoding="utf-8")
    wayfinder = by_name["wayfinder"]
    checks = {
        "source_and_payload_provider_declarations_equal": sha256_file(providers_path)
        == sha256_file(payload_providers_path),
        "wayfinder_codex_implicit": wayfinder["invocation"].get("codex") == "implicit",
        "wayfinder_github_copilot_implicit": wayfinder["invocation"].get("github-copilot") == "implicit",
        "wayfinder_claude_unavailable": wayfinder["invocation"].get("claude-code") == "unavailable",
        "wayfinder_has_no_setup_prerequisites": wayfinder.get("requires_configuration") == [],
        "wayfinder_adapter_declared": wayfinder.get("agentic_workflow_adapter", {}).get("name")
        == "wayfinder-local-state-v1",
        "complete_declared_provider_inventory_projected": projected_names == declared_names,
        "wayfinder_model_invocation_enabled": "disable-model-invocation: false" in wayfinder_text,
        "wayfinder_codex_metadata_implicit": "allow_implicit_invocation: true" in openai_text,
        "wayfinder_local_adapter_present_once": wayfinder_text.count(
            "agentic-workflow:wayfinder-local-state-v1:begin"
        )
        == 1
        and wayfinder_text.count("agentic-workflow:wayfinder-local-state-v1:end") == 1,
        "canonical_local_state_named": ".ai-workflow-state/wayfinder/<effort>/" in wayfinder_text
        and ".ai-workflow-state/wayfinder/" in state_contract,
        "incompatible_tracker_mechanics_disabled": "Never create `.scratch/`" in wayfinder_text
        and "Tracker labels, assignment/claiming" in wayfinder_text,
        "automatic_routing_owned_by_framework": "Agentic Workflow decides when local Wayfinder is selected"
        in wayfinder_text
        and "Dynamic Wayfinder escalation" in routing_text,
        "bounded_debugging_stays_lightweight": re.search(
            r"Bounded\s+debugging, one isolated unknown, and unrelated work keep their normal route",
            wayfinder_text,
        )
        is not None,
        "read_only_state_writes_forbidden": "Read-only analysis, audit, diagnosis, or review" in wayfinder_text
        and "do not create or update Wayfinder state" in routing_text,
    }
    return {
        "checks": checks,
        "provider_version": providers["provider"]["version"],
        "declared_provider_skills": declared_names,
        "projected_provider_skills": projected_names,
        "adapter": wayfinder.get("agentic_workflow_adapter"),
    }


def protected_product_fingerprint() -> dict[str, Any]:
    product = base.product_fingerprint()
    product["contract_observations"] = product_contract_observations()
    product["controller_artifact_note"] = (
        "The source Git status may list this regression namespace; product identity is locked by "
        "HEAD plus payload and projected-skill tree hashes."
    )
    return product


def verify_product_unchanged(manifest: dict[str, Any]) -> None:
    current = protected_product_fingerprint()
    frozen = manifest["product"]
    for key in ("source_git_sha", "framework_version", "payload_tree_sha256", "projected_skills_tree_sha256"):
        if current.get(key) != frozen.get(key):
            raise RuntimeError(f"frozen product changed at {key}")
    failed = [name for name, passed in current["contract_observations"]["checks"].items() if not passed]
    if failed:
        raise RuntimeError(f"current product contract checks failed: {', '.join(failed)}")


def freeze() -> Path:
    if MANIFEST_PATH.exists():
        raise RuntimeError(f"campaign is already frozen: {MANIFEST_PATH}")
    historical = read_json(HISTORICAL_MANIFEST_PATH)
    if historical["dataset"]["revision"] != base.DATASET_REVISION:
        raise RuntimeError("historical dataset revision differs from harness constant")
    if tuple(historical["dataset"]["scenarios"]) != SCENARIOS:
        raise RuntimeError("historical scenario selection differs from requested order")
    if historical["prompts"]["neutral_sha256"] != sha256_bytes(base.NEUTRAL_PROMPT.encode()):
        raise RuntimeError("historical neutral prompt no longer matches the harness")
    product = protected_product_fingerprint()
    contract_failures = [
        name for name, passed in product["contract_observations"]["checks"].items() if not passed
    ]
    if contract_failures:
        raise RuntimeError(f"product contract checks failed: {', '.join(contract_failures)}")
    manifest = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "frozen_at": utc_now(),
        "status": "frozen_before_scored_runs",
        "treatment": {
            "condition": "B-new",
            "name": "current-workflow-normal-routing",
            "agentic_workflow": True,
            "explicit_wayfinder": False,
            "scored_runs": 6,
            "repetitions": 1,
        },
        "dataset": {
            "repo": historical["dataset"]["repo"],
            "revision": historical["dataset"]["revision"],
            "scenarios": list(SCENARIOS),
            "agent_visible_files": historical["dataset"]["agent_visible_files"],
            "controller_ground_truth_files": historical["dataset"]["controller_ground_truth_files"],
            "public_root": historical["dataset"]["public_root"],
            "snapshot_execution_mode": historical["dataset"]["snapshot_execution_mode"],
            "deterministic_matcher_specs": historical["dataset"]["deterministic_matcher_specs"],
        },
        "product": product,
        "runtime": {
            "model": MODEL,
            "reasoning_effort": REASONING_EFFORT,
            "codex_cli": base.codex_version("codex"),
            "historical_codex_cli": historical["runtime"]["codex_cli"],
            "sandbox": "workspace-write",
            "approval_policy": "never",
            "timeout_seconds": TIMEOUT_SECONDS,
            "retry_policy": "one retry only for failure before thread.started; never retry a completed or timed-out model run",
            "context_policy": "fresh codex exec --ephemeral and unique minimal CODEX_HOME per scored run",
            "shell_environment_policy": "inherit PATH/TMPDIR/LANG/LC_ALL/TERM only",
            "network_policy": "prohibited by task contract and no network credentials inherited",
            "evaluated_workspace_naming": "neutral case-{scenario}-r1 path; treatment name absent",
        },
        "prompts": {
            "neutral_template": base.NEUTRAL_PROMPT,
            "neutral_sha256": sha256_bytes(base.NEUTRAL_PROMPT.encode()),
            "explicit_prefix": None,
        },
        "execution_order": list(SCENARIOS),
        "protocol_sha256": sha256_file(HERE / "protocol.md"),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "reasoning_rubric_sha256": sha256_file(HISTORICAL_RUBRIC_PATH),
        "historical_harness_sha256": sha256_file(HISTORICAL_HARNESS_PATH),
        "native_matcher_source_sha256": matcher_source_hash(),
        "historical_campaign_anchors": historical_anchors(),
        "native_scoring": historical["native_scoring"],
    }
    write_json(MANIFEST_PATH, manifest)
    print(MANIFEST_PATH)
    return MANIFEST_PATH


def prepare() -> Path:
    manifest = read_json(MANIFEST_PATH)
    verify_product_unchanged(manifest)
    if any(control_path(run_identifier(scenario)).exists() for scenario in SCENARIOS):
        raise RuntimeError("one or more campaign run controls already exist")
    records: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        identifier = run_identifier(scenario)
        workspace = workspace_for(scenario)
        if workspace.exists():
            raise RuntimeError(f"prepared workspace already exists: {workspace}")
        workspace.mkdir(parents=True)
        installation = base.install_workflow(workspace)
        setup_commit = base.init_git_workspace(workspace)
        snapshot_path = Path(manifest["dataset"]["public_root"]) / f"Scenario-{scenario}"
        output_path = workspace / "diagnosis.json"
        prompt = base.NEUTRAL_PROMPT.format(snapshot_path=snapshot_path, output_path=output_path)
        record = {
            "run_id": identifier,
            "scenario": scenario,
            "condition": "B-new",
            "repetition": 1,
            "workspace": str(workspace),
            "snapshot_path": str(snapshot_path),
            "output_path": str(output_path),
            "prompt": prompt,
            "prompt_sha256": sha256_bytes(prompt.encode()),
            "neutral_template_sha256": sha256_bytes(base.NEUTRAL_PROMPT.encode()),
            "setup_commit": setup_commit,
            "setup_snapshot": base.snapshot_tree(workspace),
            "workflow_installation": installation,
            "attempts": [],
            "status": "prepared",
        }
        save_run(record)
        records.append({key: value for key, value in record.items() if key != "prompt"})
    path = CONTROL_ROOT / "prepared-runs.json"
    write_json(path, {"created_at": utc_now(), "runs": records})
    print(path)
    return path


def dataset_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    public_root = Path(manifest["dataset"]["public_root"])
    old_control = Path(tempfile.gettempdir()) / f".{base.CAMPAIGN_ID}-controller-{base.DATASET_REVISION[:12]}"
    for scenario in SCENARIOS:
        root = public_root / f"Scenario-{scenario}"
        checks[f"scenario_{scenario}_exists"] = root.is_dir()
        checks[f"scenario_{scenario}_ground_truth_absent"] = not any(
            path.name.casefold() in {"ground_truth.yaml", "groundtruth.yaml"} for path in root.rglob("*")
        )
        checks[f"scenario_{scenario}_read_only"] = all(
            not (path.stat().st_mode & 0o200) for path in root.rglob("*") if path.is_file()
        )
        checks[f"scenario_{scenario}_controller_ground_truth_exists"] = (
            old_control / "ground-truth" / f"Scenario-{scenario}" / "ground_truth.yaml"
        ).is_file()
    for record in [
        *manifest["dataset"]["agent_visible_files"],
        *manifest["dataset"]["controller_ground_truth_files"],
    ]:
        source_path = Path(str(record["path"]))
        relative = Path(*source_path.parts[1:]) if source_path.parts[:1] == ("sre",) else source_path
        path = (
            old_control / "ground-truth" / relative
            if record["visibility"] == "controller"
            else public_root / relative
        )
        key = sha256_bytes(str(record["path"]).encode())[:16]
        checks[f"inventory_{key}"] = (
            path.is_file()
            and path.stat().st_size == int(record["bytes"])
            and sha256_file(path) == record["sha256"]
        )
    return checks


def preflight() -> Path:
    manifest = read_json(MANIFEST_PATH)
    verify_product_unchanged(manifest)
    prepared = read_json(CONTROL_ROOT / "prepared-runs.json")["runs"]
    declared = set(manifest["product"]["contract_observations"]["declared_provider_skills"])
    installations = {record["workflow_installation"]["installed_tree_sha256"] for record in prepared}
    checks = {
        "manifest_frozen": manifest.get("status") == "frozen_before_scored_runs",
        "protocol_frozen": manifest["protocol_sha256"] == sha256_file(HERE / "protocol.md"),
        "runner_frozen": manifest["runner_sha256"] == sha256_file(Path(__file__).resolve()),
        "rubric_frozen": manifest["reasoning_rubric_sha256"] == sha256_file(HISTORICAL_RUBRIC_PATH),
        "historical_harness_frozen": manifest["historical_harness_sha256"]
        == sha256_file(HISTORICAL_HARNESS_PATH),
        "native_matcher_unchanged": manifest["native_matcher_source_sha256"] == matcher_source_hash(),
        "historical_campaign_unchanged": manifest["historical_campaign_anchors"] == historical_anchors(),
        "exactly_six_runs_prepared": len(prepared) == 6,
        "six_unique_scenarios": sorted(record["scenario"] for record in prepared) == sorted(SCENARIOS),
        "all_conditions_are_b_new": all(record["condition"] == "B-new" for record in prepared),
        "all_repetitions_are_one": all(record["repetition"] == 1 for record in prepared),
        "all_installations_identical": len(installations) == 1,
        "all_prompts_use_frozen_neutral_template": all(
            record["neutral_template_sha256"] == manifest["prompts"]["neutral_sha256"] for record in prepared
        ),
        "no_prompt_explicit_wayfinder": all(
            not load_run(record["run_id"])["prompt"].startswith("$wayfinder") for record in prepared
        ),
        "no_prompt_routing_hint": all(
            not re.search(r"wayfinder|debugging|router|previous", load_run(record["run_id"])["prompt"], re.I)
            for record in prepared
        ),
        "neutral_workspace_paths": all(
            "wayfinder" not in load_run(record["run_id"])["workspace"].casefold()
            and "b-new" not in load_run(record["run_id"])["workspace"].casefold()
            for record in prepared
        ),
        "complete_provider_inventory_in_every_workspace": all(
            declared
            <= {
                path.parent.name
                for path in (Path(record["workspace"]) / ".agents" / "skills").glob("*/SKILL.md")
            }
            for record in prepared
        ),
        "codex_cli_matches_historical": manifest["runtime"]["codex_cli"]
        == manifest["runtime"]["historical_codex_cli"],
        **manifest["product"]["contract_observations"]["checks"],
        **dataset_checks(manifest),
    }
    status = "passed" if all(checks.values()) else "failed"
    value = {"created_at": utc_now(), "status": status, "checks": checks}
    write_json(PREFLIGHT_PATH, value)
    print(PREFLIGHT_PATH)
    if status != "passed":
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"preflight failed: {', '.join(failed)}")
    return PREFLIGHT_PATH


def audit_isolation(codex_executable: str = "codex", timeout: int = 300) -> Path:
    if read_json(PREFLIGHT_PATH).get("status") != "passed":
        raise RuntimeError("preflight must pass before isolation audit")
    manifest = read_json(MANIFEST_PATH)
    verify_product_unchanged(manifest)
    audit_root = RUN_ROOT / f"isolation-{uuid.uuid4().hex}"
    workspace = audit_root / "workspace"
    workspace.mkdir(parents=True)
    installation = base.install_workflow(workspace)
    base.init_git_workspace(workspace)
    before = base.snapshot_tree(workspace)
    sentinel = f"CONTROLLER_{uuid.uuid4().hex.upper()}"
    sibling = audit_root / f"sibling-{uuid.uuid4().hex}.txt"
    sibling.write_text(sentinel + "\n", encoding="utf-8")
    probe = (
        "This is a non-evaluated context-isolation probe. Do not use tools or inspect the filesystem. "
        "Return one JSON object with keys project_instruction_paths, available_skill_names, "
        "controller_conversation_excerpt, sibling_sentinel, and inherited_cloud_credentials. "
        "Use null when the automatically supplied context does not expose an answer; do not guess."
    )
    codex_home, inventory = base.create_minimal_codex_home(audit_root / "ephemeral")
    command = base.codex_command(codex_executable, workspace, sandbox="read-only")
    started = time.monotonic()
    try:
        result = base.run_command(
            command,
            cwd=workspace,
            timeout=timeout,
            env=base.sanitized_environment(codex_home),
            input_text=probe,
        )
    finally:
        shutil.rmtree(codex_home, ignore_errors=True)
    elapsed = round(time.monotonic() - started, 3)
    summary = base.event_summary(result.stdout)
    response = "\n".join(summary["agent_messages"])
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        parsed = None
    checks = {
        "codex_succeeded": result.returncode == 0,
        "response_json_object": isinstance(parsed, dict),
        "unique_minimal_codex_home_removed": not codex_home.exists()
        and inventory["contains_only_auth_material"],
        "probe_made_no_workspace_change": before == base.snapshot_tree(workspace),
        "sibling_sentinel_not_reported": sentinel not in response,
        "controller_conversation_not_reported": isinstance(parsed, dict)
        and parsed.get("controller_conversation_excerpt") is None,
        "workflow_installation_present": installation is not None and (workspace / "AGENTS.md").is_file(),
    }
    raw_root = ARTIFACTS_ROOT / "audit-evidence"
    raw_root.mkdir(parents=True, exist_ok=True)
    (raw_root / "B-new.jsonl").write_text(result.stdout, encoding="utf-8")
    (raw_root / "B-new.stderr.txt").write_text(result.stderr, encoding="utf-8")
    status = "passed" if all(checks.values()) else "failed"
    value = {
        "created_at": utc_now(),
        "status": status,
        "elapsed_seconds": elapsed,
        "checks": checks,
        "response": parsed,
        "execution_id": summary.get("execution_id"),
        "usage": summary.get("usage"),
        "scored_run": False,
    }
    write_json(AUDIT_PATH, value)
    print(AUDIT_PATH)
    if status != "passed":
        raise RuntimeError("context-isolation audit failed")
    return AUDIT_PATH


def capability_observations(summary: dict[str, Any], workspace: Path) -> dict[str, Any]:
    evidence_by_skill: dict[str, list[dict[str, Any]]] = {}
    for event in summary.get("command_events", []):
        command = str(event.get("command", ""))
        for name in re.findall(r"\.agents/skills/([^/\s'\"]+)/SKILL\.md", command):
            evidence_by_skill.setdefault(name, []).append(event)
    if (workspace / ".ai-workflow-state" / "wayfinder").is_dir():
        evidence_by_skill.setdefault("wayfinder", []).append(
            {"artifact": ".ai-workflow-state/wayfinder"}
        )
    route_markers: list[str] = []
    for message in summary.get("agent_messages", []):
        route_markers.extend(re.findall(r"\[route:\s*router\s*→[^\]]+\]", message))
    direct_evidence = [marker for marker in route_markers if re.search(r"→\s*direct\b", marker)]
    observed = {
        name: {"invoked": bool(evidence), "evidence": evidence}
        for name, evidence in sorted(evidence_by_skill.items())
    }
    for name in (
        "wayfinder", "workflow-debugging", "workflow-discovery", "research", "domain-modeling",
        "grilling", "prototype", "codebase-design", "workflow-verification", "tdd", "code-review",
        "implement", "to-spec", "to-tickets", "triage", "teach",
    ):
        observed.setdefault(name, {"invoked": False, "evidence": []})
    return {
        "skills": observed,
        "direct": {"invoked": bool(direct_evidence), "evidence": direct_evidence},
        "route_markers": route_markers,
        "all_commands_containing_skill": [
            event for event in summary.get("command_events", []) if ".agents/skills/" in str(event.get("command", ""))
        ],
    }


def run_agent(identifier: str, codex_executable: str = "codex", timeout: int = TIMEOUT_SECONDS) -> Path:
    manifest = read_json(MANIFEST_PATH)
    verify_product_unchanged(manifest)
    if read_json(PREFLIGHT_PATH).get("status") != "passed" or read_json(AUDIT_PATH).get("status") != "passed":
        raise RuntimeError("preflight and context-isolation audit must pass before scored execution")
    record = load_run(identifier)
    attempts = list(record.get("attempts", []))
    if record.get("status") == "completed" or record.get("status") == "agent_failed":
        raise RuntimeError(f"completed or model-started run cannot be retried: {identifier}")
    if record.get("status") == "infrastructure_failed" and len(attempts) >= 2:
        raise RuntimeError(f"infrastructure retry already consumed: {identifier}")
    if record.get("status") not in {"prepared", "infrastructure_failed"}:
        raise RuntimeError(f"run is not executable: {identifier} ({record.get('status')})")
    workspace = Path(record["workspace"])
    prompt = str(record["prompt"])
    snapshot_path = Path(record["snapshot_path"])
    before_snapshot = base.snapshot_tree(snapshot_path)
    attempt = len(attempts) + 1
    attempt_root = ARTIFACTS_ROOT / "runs" / identifier / "attempts" / f"attempt-{attempt}"
    ephemeral_parent = RUN_ROOT / f"case-{record['scenario']}-r1" / f"ephemeral-attempt-{attempt}"
    ephemeral_parent.mkdir(parents=True, exist_ok=True)
    codex_home, codex_inventory = base.create_minimal_codex_home(ephemeral_parent)
    command = base.codex_command(codex_executable, workspace)
    started_at = utc_now()
    started = time.monotonic()
    timed_out = False
    try:
        result = base.run_command(
            command,
            cwd=workspace,
            timeout=timeout,
            env=base.sanitized_environment(codex_home),
            input_text=prompt,
        )
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(command, 124, error.stdout or "", error.stderr or "")
        timed_out = True
    finally:
        shutil.rmtree(codex_home, ignore_errors=True)
    elapsed = round(time.monotonic() - started, 3)
    raw_root = attempt_root / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    (raw_root / "codex.jsonl").write_text(result.stdout, encoding="utf-8")
    (raw_root / "codex.stderr.txt").write_text(result.stderr, encoding="utf-8")
    summary = base.event_summary(result.stdout)
    diagnosis_path = Path(record["output_path"])
    diagnosis: Any = None
    diagnosis_valid = False
    if diagnosis_path.is_file():
        try:
            diagnosis = json.loads(diagnosis_path.read_text(encoding="utf-8"))
            diagnosis_valid = isinstance(diagnosis, dict)
        except json.JSONDecodeError:
            diagnosis = None
    current_workspace = base.snapshot_tree(workspace)
    after_snapshot = base.snapshot_tree(snapshot_path)
    changed_files = sorted(
        path for path in set(record["setup_snapshot"]) | set(current_workspace)
        if record["setup_snapshot"].get(path) != current_workspace.get(path)
    )
    model_execution_started = bool(summary.get("execution_id"))
    infrastructure_failure = result.returncode != 0 and not model_execution_started and not timed_out
    commands = [str(item.get("command", "")) for item in summary.get("command_events", [])]
    execution = {
        "run_id": identifier,
        "scenario": record["scenario"],
        "condition": record["condition"],
        "repetition": record["repetition"],
        "attempt": attempt,
        "started_at": started_at,
        "finished_at": utc_now(),
        "elapsed_seconds": elapsed,
        "exit_status": result.returncode,
        "timed_out": timed_out,
        "model_execution_started": model_execution_started,
        "infrastructure_failure_before_model_execution": infrastructure_failure,
        "command": command[:-1] + ["<prompt-via-stdin>"],
        "prompt_sha256": record["prompt_sha256"],
        "fresh_context": True,
        "codex_home_isolation": {**codex_inventory, "removed_after_run": not codex_home.exists()},
        "summary": summary,
        "capabilities": capability_observations(summary, workspace),
        "diagnosis_valid_json_object": diagnosis_valid,
        "diagnosis": diagnosis,
        "workspace_changed_files": changed_files,
        "files_created_outside_required_diagnosis": [path for path in changed_files if path != "diagnosis.json"],
        "snapshot_tree_sha256_before": sha256_bytes(json.dumps(before_snapshot, sort_keys=True).encode()),
        "snapshot_tree_sha256_after": sha256_bytes(json.dumps(after_snapshot, sort_keys=True).encode()),
        "snapshot_unchanged": before_snapshot == after_snapshot,
        "network_or_live_cluster_command_candidates": [
            command for command in commands
            if re.search(r"(^|[\s;&|])(curl|wget|ssh|kubectl|aws|gcloud|az)([\s;&|]|$)", command)
        ],
    }
    write_json(attempt_root / "execution.json", execution)
    base.copy_workspace_evidence(workspace, attempt_root / "workspace")
    attempts.append(
        {
            "attempt": attempt,
            "result_path": str(attempt_root / "execution.json"),
            "infrastructure_failure_before_model_execution": infrastructure_failure,
            "model_execution_started": model_execution_started,
            "exit_status": result.returncode,
        }
    )
    record["attempts"] = attempts
    if infrastructure_failure:
        record["status"] = "infrastructure_failed"
    else:
        final_root = RESULTS_ROOT / "runs" / identifier
        final_artifact_root = ARTIFACTS_ROOT / "runs" / identifier
        final_raw = final_artifact_root / "raw"
        final_raw.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(raw_root / "codex.jsonl", final_raw / "codex.jsonl")
        shutil.copyfile(raw_root / "codex.stderr.txt", final_raw / "codex.stderr.txt")
        execution["artifacts"] = {
            "root": str(final_artifact_root),
            "codex_jsonl": str(final_raw / "codex.jsonl"),
            "codex_stderr": str(final_raw / "codex.stderr.txt"),
            "workspace": str(final_artifact_root / "workspace"),
        }
        write_json(final_root / "execution.json", execution)
        base.copy_workspace_evidence(workspace, final_artifact_root / "workspace")
        record["status"] = "completed" if result.returncode == 0 else "agent_failed"
        record["result_path"] = str(final_root / "execution.json")
    save_run(record)
    print(attempt_root / "execution.json")
    return attempt_root / "execution.json"


def grade_native(identifier: str) -> Path:
    manifest = read_json(MANIFEST_PATH)
    record = load_run(identifier)
    if record.get("status") not in {"completed", "agent_failed"} or not record.get("result_path"):
        raise RuntimeError(f"run has no final model execution: {identifier}")
    execution = read_json(Path(record["result_path"]))
    scenario = str(record["scenario"])
    grade = {
        "run_id": identifier,
        "scenario": int(scenario),
        "condition": "B-new",
        "repetition": 1,
        "diagnosis_valid_json_object": execution.get("diagnosis_valid_json_object", False),
        **base.native_grade(execution.get("diagnosis"), manifest["dataset"]["deterministic_matcher_specs"][scenario]),
    }
    path = RESULTS_ROOT / "grades" / identifier / "native.json"
    write_json(path, grade)
    print(path)
    return path


def grade_reasoning(identifier: str, codex_executable: str = "codex", timeout: int = TIMEOUT_SECONDS) -> Path:
    configure_base_for_campaign()
    return base.reasoning_grade_run(identifier, codex_executable=codex_executable, timeout=timeout)


def numeric_summary(values: list[float | int]) -> dict[str, Any]:
    ordered = sorted(values)
    count = len(ordered)
    median = ordered[count // 2] if count % 2 else (ordered[count // 2 - 1] + ordered[count // 2]) / 2
    return {
        "mean": sum(ordered) / count,
        "median": median,
        "minimum": min(ordered),
        "maximum": max(ordered),
        "sum": sum(ordered),
    }


def aggregate() -> Path:
    historical = read_json(HISTORICAL_REPORTS_ROOT / "results-summary.json")
    rows: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        identifier = run_identifier(scenario)
        record = load_run(identifier)
        execution = read_json(Path(record["result_path"]))
        native = read_json(RESULTS_ROOT / "grades" / identifier / "native.json")
        reasoning_path = RESULTS_ROOT / "grades" / identifier / "reasoning.json"
        reasoning = read_json(reasoning_path) if reasoning_path.is_file() else None
        usage = execution.get("summary", {}).get("usage", {})
        invoked = sorted(
            name for name, item in execution.get("capabilities", {}).get("skills", {}).items()
            if item.get("invoked")
        )
        rows.append({
            "run_id": identifier,
            "scenario": scenario,
            "exit_status": execution["exit_status"],
            "diagnosis_valid_json_object": execution["diagnosis_valid_json_object"],
            "elapsed_seconds": execution["elapsed_seconds"],
            "input_tokens": usage.get("input_tokens", 0),
            "cached_input_tokens": usage.get("cached_input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "tool_actions": execution.get("summary", {}).get("tool_action_count", 0),
            "native_score": native["native_score"],
            "native_success": native["success"],
            "native_predictions": native["predictions"],
            "invoked_skills": invoked,
            "direct_route_observed": execution.get("capabilities", {}).get("direct", {}).get("invoked", False),
            "route_markers": execution.get("capabilities", {}).get("route_markers", []),
            "workspace_changed_files": execution["workspace_changed_files"],
            "files_created_outside_required_diagnosis": execution["files_created_outside_required_diagnosis"],
            "snapshot_unchanged": execution["snapshot_unchanged"],
            "network_or_live_cluster_command_candidates": execution["network_or_live_cluster_command_candidates"],
            "reasoning_grade_valid": reasoning is not None
            and reasoning.get("exit_status") == 0
            and not reasoning.get("validation_errors"),
            "reasoning_dimensions": reasoning.get("grade", {}).get("dimensions") if reasoning else None,
        })
    metrics = ("elapsed_seconds", "input_tokens", "cached_input_tokens", "output_tokens", "tool_actions")
    condition_summary = {
        "runs": len(rows),
        "normal_exits": sum(row["exit_status"] == 0 for row in rows),
        "valid_diagnoses": sum(row["diagnosis_valid_json_object"] for row in rows),
        "native_mean": sum(row["native_score"] for row in rows) / len(rows),
        "native_successes": sum(row["native_success"] for row in rows),
        **{metric: numeric_summary([row[metric] for row in rows]) for metric in metrics},
        "skill_invocations": dict(Counter(name for row in rows for name in row["invoked_skills"])),
        "direct_route_runs": sum(row["direct_route_observed"] for row in rows),
        "route_marker_runs": sum(bool(row["route_markers"]) for row in rows),
        "snapshot_unchanged_runs": sum(row["snapshot_unchanged"] for row in rows),
        "runs_with_extra_workspace_files": sum(bool(row["files_created_outside_required_diagnosis"]) for row in rows),
        "runs_with_network_or_live_cluster_candidates": sum(bool(row["network_or_live_cluster_command_candidates"]) for row in rows),
        "valid_reasoning_grades": sum(row["reasoning_grade_valid"] for row in rows),
    }
    output = {
        "campaign_id": CAMPAIGN_ID,
        "condition": "B-new",
        "summary": condition_summary,
        "native_by_scenario": {str(row["scenario"]): row["native_score"] for row in rows},
        "historical_condition_summaries": historical["conditions"],
        "per_run": rows,
    }
    path = REPORTS_ROOT / "results-summary.json"
    write_json(path, output)
    print(path)
    return path


def post_run_integrity() -> Path:
    manifest = read_json(MANIFEST_PATH)
    verify_product_unchanged(manifest)
    executions = []
    for scenario in SCENARIOS:
        record = load_run(run_identifier(scenario))
        if record.get("status") not in {"completed", "agent_failed"}:
            raise RuntimeError(f"scenario {scenario} has no final model run")
        executions.append(read_json(Path(record["result_path"])))
    checks = {
        "exactly_six_final_scored_runs": len(executions) == 6,
        "one_run_per_scenario": sorted(item["scenario"] for item in executions) == sorted(SCENARIOS),
        "no_completed_run_retried": all(
            sum(bool(attempt["model_execution_started"]) for attempt in load_run(item["run_id"])["attempts"]) == 1
            for item in executions
        ),
        "all_snapshots_unchanged": all(item["snapshot_unchanged"] for item in executions),
        "historical_campaign_unchanged": manifest["historical_campaign_anchors"] == historical_anchors(),
        "protocol_unchanged": manifest["protocol_sha256"] == sha256_file(HERE / "protocol.md"),
        "runner_unchanged": manifest["runner_sha256"] == sha256_file(Path(__file__).resolve()),
        "matcher_unchanged": manifest["native_matcher_source_sha256"] == matcher_source_hash(),
        "rubric_unchanged": manifest["reasoning_rubric_sha256"] == sha256_file(HISTORICAL_RUBRIC_PATH),
    }
    status = "passed" if all(checks.values()) else "failed"
    value = {"created_at": utc_now(), "status": status, "checks": checks}
    write_json(INTEGRITY_PATH, value)
    print(INTEGRITY_PATH)
    if status != "passed":
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"post-run integrity failed: {', '.join(failed)}")
    return INTEGRITY_PATH


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--freeze", action="store_true")
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--preflight", action="store_true")
    action.add_argument("--audit-isolation", action="store_true")
    action.add_argument("--run")
    action.add_argument("--run-all", action="store_true")
    action.add_argument("--grade-native")
    action.add_argument("--grade-native-all", action="store_true")
    action.add_argument("--grade-reasoning")
    action.add_argument("--grade-reasoning-all", action="store_true")
    action.add_argument("--aggregate", action="store_true")
    action.add_argument("--post-run-integrity", action="store_true")
    parser.add_argument("--codex-executable", default="codex")
    parser.add_argument("--timeout", type=int, default=TIMEOUT_SECONDS)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.freeze:
        freeze()
    elif args.prepare:
        prepare()
    elif args.preflight:
        preflight()
    elif args.audit_isolation:
        audit_isolation(args.codex_executable, args.timeout)
    elif args.run:
        run_agent(args.run, args.codex_executable, args.timeout)
    elif args.run_all:
        for scenario in SCENARIOS:
            run_agent(run_identifier(scenario), args.codex_executable, args.timeout)
    elif args.grade_native:
        grade_native(args.grade_native)
    elif args.grade_native_all:
        for scenario in SCENARIOS:
            grade_native(run_identifier(scenario))
    elif args.grade_reasoning:
        grade_reasoning(args.grade_reasoning, args.codex_executable, args.timeout)
    elif args.grade_reasoning_all:
        for scenario in SCENARIOS:
            grade_reasoning(run_identifier(scenario), args.codex_executable, args.timeout)
    elif args.aggregate:
        aggregate()
    elif args.post_run_integrity:
        post_run_integrity()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
