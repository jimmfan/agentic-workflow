#!/usr/bin/env python3
"""One-run Scenario 17 replication using the frozen B-new harness contract."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
SOURCE_ROOT = HERE.parents[3]
SUITE_ROOT = HERE.parents[1]
HISTORICAL_ROOT = HERE.parent / "itbench-wayfinder-auto-regression-v1"
HISTORICAL_RUNNER = HISTORICAL_ROOT / "run.py"
HISTORICAL_MANIFEST = HISTORICAL_ROOT / "frozen-manifest.json"
HISTORICAL_EXECUTION = HISTORICAL_ROOT / "results/runs/s17-b-new-r1/execution.json"
HISTORICAL_NATIVE = HISTORICAL_ROOT / "results/grades/s17-b-new-r1/native.json"
HISTORICAL_FORENSICS = HISTORICAL_ROOT / "reports/token-forensics/s17-b-new-r1.json"

CAMPAIGN_ID = "itbench-s17-token-replication-v1"
RUN_ID = "s17-b-new-replication-r1"
SCENARIO = 17
TIMEOUT_SECONDS = 1800
MANIFEST_PATH = HERE / "frozen-manifest.json"
PREFLIGHT_PATH = HERE / "preflight.json"
INTEGRITY_PATH = HERE / "post-run-integrity.json"
RESULT_ROOT = HERE / "results" / RUN_ID
ARTIFACT_ROOT = SOURCE_ROOT / "evals/artifacts" / CAMPAIGN_ID / "runs" / RUN_ID
TEMP_ROOT = Path(tempfile.gettempdir()) / ".itbench-s17-token-replication-v1"
CONTROL_PATH = TEMP_ROOT / "control.json"
WORKSPACE = TEMP_ROOT / "workspace"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


historical = load_module(HISTORICAL_RUNNER, "itbench_b_new_historical")
base = historical.base


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


def current_product() -> dict[str, Any]:
    product = historical.protected_product_fingerprint()
    product["tested_branch"] = base.command_output(["git", "branch", "--show-current"], cwd=SOURCE_ROOT)
    return product


def protected_product_equal(frozen: dict[str, Any], current: dict[str, Any]) -> bool:
    keys = ("source_git_sha", "framework_version", "payload_tree_sha256", "projected_skills_tree_sha256")
    return all(frozen.get(key) == current.get(key) for key in keys)


def scenario_records(manifest: dict[str, Any], visibility_key: str) -> list[dict[str, Any]]:
    marker = f"Scenario-{SCENARIO}/"
    return [item for item in manifest["dataset"][visibility_key] if marker in str(item["path"])]


def freeze() -> Path:
    if MANIFEST_PATH.exists():
        raise RuntimeError(f"replication is already frozen: {MANIFEST_PATH}")
    old = read_json(HISTORICAL_MANIFEST)
    historical_execution = read_json(HISTORICAL_EXECUTION)
    historical_native = read_json(HISTORICAL_NATIVE)
    historical_forensics = read_json(HISTORICAL_FORENSICS)
    if old["prompts"]["neutral_sha256"] != sha256_bytes(base.NEUTRAL_PROMPT.encode()):
        raise RuntimeError("neutral prompt no longer matches the historical campaign")
    product = current_product()
    if product["tested_branch"] != "feature/wayfinder-auto":
        raise RuntimeError("replication must run from feature/wayfinder-auto")
    failed_contracts = [
        name for name, passed in product["contract_observations"]["checks"].items() if not passed
    ]
    if failed_contracts:
        raise RuntimeError(f"product contract checks failed: {', '.join(failed_contracts)}")
    value = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "frozen_at": utc_now(),
        "status": "frozen_before_single_scored_run",
        "treatment": {
            "condition": "B-new replication",
            "agentic_workflow": True,
            "explicit_wayfinder": False,
            "scored_runs": 1,
            "scenario": SCENARIO,
        },
        "dataset": {
            "repo": old["dataset"]["repo"],
            "revision": old["dataset"]["revision"],
            "scenario": SCENARIO,
            "public_root": old["dataset"]["public_root"],
            "snapshot_execution_mode": old["dataset"]["snapshot_execution_mode"],
            "agent_visible_files": scenario_records(old, "agent_visible_files"),
            "controller_ground_truth_files": scenario_records(old, "controller_ground_truth_files"),
            "deterministic_matcher_spec": old["dataset"]["deterministic_matcher_specs"][str(SCENARIO)],
        },
        "product": product,
        "runtime": {
            "model": historical.MODEL,
            "reasoning_effort": historical.REASONING_EFFORT,
            "codex_cli": base.codex_version("codex"),
            "historical_codex_cli": old["runtime"]["codex_cli"],
            "sandbox": "workspace-write",
            "approval_policy": "never",
            "timeout_seconds": TIMEOUT_SECONDS,
            "retry_policy": "one retry only for failure before thread.started; never retry a completed or timed-out model run",
            "context_policy": "fresh codex exec --ephemeral and unique minimal CODEX_HOME",
            "shell_environment_policy": "inherit PATH/TMPDIR/LANG/LC_ALL/TERM only",
            "network_policy": "prohibited by task contract and no network credentials inherited",
        },
        "prompts": {
            "neutral_template": base.NEUTRAL_PROMPT,
            "neutral_sha256": sha256_bytes(base.NEUTRAL_PROMPT.encode()),
            "explicit_prefix": None,
        },
        "historical_comparison": {
            "execution_sha256": sha256_file(HISTORICAL_EXECUTION),
            "native_grade_sha256": sha256_file(HISTORICAL_NATIVE),
            "token_forensics_sha256": sha256_file(HISTORICAL_FORENSICS),
            "input_tokens": historical_forensics["measured"]["tokens"]["input"],
            "cached_input_tokens": historical_forensics["measured"]["tokens"]["cached_input"],
            "uncached_input_tokens": historical_forensics["derived"]["tokens"]["uncached_input"],
            "output_tokens": historical_forensics["measured"]["tokens"]["output"],
            "elapsed_seconds": historical_execution["elapsed_seconds"],
            "tool_actions": historical_forensics["measured"]["tools"]["calls"],
            "tool_output_bytes": historical_forensics["measured"]["tools"]["output_bytes"],
            "largest_tool_outputs": historical_forensics["measured"]["tools"]["largest_outputs"],
            "failed_commands": historical_forensics["measured"]["tools"]["failed_calls"],
            "route_markers": historical_execution["capabilities"]["route_markers"],
            "diagnosis": historical_execution["diagnosis"],
            "native_score": historical_native["native_score"],
            "native_success": historical_native["success"],
        },
        "protocol_sha256": sha256_file(HERE / "protocol.md"),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "native_scoring": old["native_scoring"],
    }
    write_json(MANIFEST_PATH, value)
    print(MANIFEST_PATH)
    return MANIFEST_PATH


def verify_product_unchanged(manifest: dict[str, Any]) -> None:
    current = current_product()
    if not protected_product_equal(manifest["product"], current):
        raise RuntimeError("frozen product fingerprint changed")


def prepare() -> Path:
    manifest = read_json(MANIFEST_PATH)
    verify_product_unchanged(manifest)
    if CONTROL_PATH.exists() or WORKSPACE.exists():
        raise RuntimeError("replication control or workspace already exists")
    WORKSPACE.mkdir(parents=True)
    installation = base.install_workflow(WORKSPACE)
    setup_commit = base.init_git_workspace(WORKSPACE)
    snapshot = Path(manifest["dataset"]["public_root"]) / f"Scenario-{SCENARIO}"
    output = WORKSPACE / "diagnosis.json"
    prompt = base.NEUTRAL_PROMPT.format(snapshot_path=snapshot, output_path=output)
    record = {
        "run_id": RUN_ID,
        "status": "prepared",
        "workspace": str(WORKSPACE),
        "snapshot_path": str(snapshot),
        "output_path": str(output),
        "prompt": prompt,
        "prompt_sha256": sha256_bytes(prompt.encode()),
        "setup_commit": setup_commit,
        "setup_snapshot": base.snapshot_tree(WORKSPACE),
        "workflow_installation": installation,
        "attempts": [],
    }
    write_json(CONTROL_PATH, record)
    print(CONTROL_PATH)
    return CONTROL_PATH


def preflight() -> Path:
    manifest = read_json(MANIFEST_PATH)
    record = read_json(CONTROL_PATH)
    verify_product_unchanged(manifest)
    snapshot = Path(record["snapshot_path"])
    expected = {str(item["path"]): item for item in manifest["dataset"]["agent_visible_files"]}
    file_checks: dict[str, bool] = {}
    for relative_path, item in expected.items():
        public_relative_path = relative_path.removeprefix("sre/")
        path = Path(manifest["dataset"]["public_root"]) / public_relative_path
        file_checks[relative_path] = (
            path.is_file()
            and path.stat().st_size == int(item["bytes"])
            and sha256_file(path) == item["sha256"]
            and not (path.stat().st_mode & 0o222)
        )
    workspace_paths = {path.relative_to(WORKSPACE).as_posix() for path in WORKSPACE.rglob("*")}
    forbidden_fragments = ("diagnosis", "ground_truth", "token-forensics", "report", "transcript")
    installed_files = record["workflow_installation"]["installed_file_sha256"]
    projected_skills = manifest["product"]["projected_skill_file_sha256"]
    installed_projection_matches = all(
        installed_files.get(f".agents/skills/{relative_path}") == digest
        for relative_path, digest in projected_skills.items()
    )
    installed_payload_matches = all(
        installed_files.get(f".ai-workflow/{relative_path.removeprefix('ai-workflow/')}") == digest
        for relative_path, digest in manifest["product"]["payload_file_sha256"].items()
        if relative_path.startswith("ai-workflow/")
    )
    checks = {
        "branch_is_feature_wayfinder_auto": manifest["product"]["tested_branch"] == "feature/wayfinder-auto",
        "exactly_one_scenario": manifest["dataset"]["scenario"] == SCENARIO,
        "dataset_revision_frozen": manifest["dataset"]["revision"] == base.DATASET_REVISION,
        "neutral_prompt_unchanged": manifest["prompts"]["neutral_sha256"] == sha256_bytes(base.NEUTRAL_PROMPT.encode()),
        "prompt_contains_no_explicit_wayfinder": "$wayfinder" not in record["prompt"].casefold(),
        "snapshot_exists": snapshot.is_dir(),
        "snapshot_ground_truth_absent": not any(path.name.casefold() in {"ground_truth.yaml", "groundtruth.yaml"} for path in snapshot.rglob("*")),
        "all_frozen_snapshot_files_match": bool(file_checks) and all(file_checks.values()),
        "installed_tree_hash_is_consistent": record["workflow_installation"]["installed_tree_sha256"]
        == sha256_bytes(json.dumps(installed_files, sort_keys=True).encode()),
        "installed_projected_skills_match_frozen": installed_projection_matches,
        "installed_payload_files_match_frozen": installed_payload_matches,
        "no_prior_wayfinder_state": not (WORKSPACE / ".ai-workflow-state/wayfinder").exists(),
        "no_historical_evidence_in_workspace": not any(
            fragment in path.casefold() for path in workspace_paths for fragment in forbidden_fragments
        ),
        "strict_isolated_command_contract": base.codex_command("codex", WORKSPACE) == [
            "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules", "--strict-config",
            "-m", historical.MODEL, "-c", f'model_reasoning_effort="{historical.REASONING_EFFORT}"',
            "-c", 'approval_policy="never"', "-c", 'shell_environment_policy.inherit="none"',
            "-s", "workspace-write", "-C", str(WORKSPACE), "--json", "-",
        ],
        "historical_evidence_anchors_match": all([
            sha256_file(HISTORICAL_EXECUTION) == manifest["historical_comparison"]["execution_sha256"],
            sha256_file(HISTORICAL_NATIVE) == manifest["historical_comparison"]["native_grade_sha256"],
            sha256_file(HISTORICAL_FORENSICS) == manifest["historical_comparison"]["token_forensics_sha256"],
        ]),
    }
    value = {
        "created_at": utc_now(),
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "snapshot_file_checks": file_checks,
        "evaluated_workspace_paths": sorted(workspace_paths),
        "product_revision": manifest["product"]["source_git_sha"],
        "codex_cli": manifest["runtime"]["codex_cli"],
        "historical_codex_cli": manifest["runtime"]["historical_codex_cli"],
        "note": "Static isolation verification avoids launching a second evaluated Codex process.",
    }
    write_json(PREFLIGHT_PATH, value)
    print(PREFLIGHT_PATH)
    if value["status"] != "passed":
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"preflight failed: {', '.join(failed)}")
    return PREFLIGHT_PATH


def run_agent(codex_executable: str = "codex", timeout: int = TIMEOUT_SECONDS) -> Path:
    manifest = read_json(MANIFEST_PATH)
    preflight_value = read_json(PREFLIGHT_PATH)
    record = read_json(CONTROL_PATH)
    verify_product_unchanged(manifest)
    if preflight_value.get("status") != "passed":
        raise RuntimeError("preflight must pass before execution")
    if record["status"] not in {"prepared", "infrastructure_failed"}:
        raise RuntimeError(f"run is not executable: {record['status']}")
    if record["status"] == "infrastructure_failed" and len(record["attempts"]) >= 2:
        raise RuntimeError("infrastructure retry already consumed")
    attempt = len(record["attempts"]) + 1
    before_snapshot = base.snapshot_tree(Path(record["snapshot_path"]))
    ephemeral_parent = TEMP_ROOT / f"ephemeral-attempt-{attempt}"
    ephemeral_parent.mkdir(parents=True, exist_ok=True)
    codex_home, codex_inventory = base.create_minimal_codex_home(ephemeral_parent)
    command = base.codex_command(codex_executable, WORKSPACE)
    started_at = utc_now()
    started = time.monotonic()
    timed_out = False
    try:
        result = base.run_command(
            command,
            cwd=WORKSPACE,
            timeout=timeout,
            env=base.sanitized_environment(codex_home),
            input_text=record["prompt"],
        )
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(command, 124, error.stdout or "", error.stderr or "")
        timed_out = True
    finally:
        shutil.rmtree(codex_home, ignore_errors=True)
    elapsed = round(time.monotonic() - started, 3)
    raw_root = ARTIFACT_ROOT / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    (raw_root / "codex.jsonl").write_text(result.stdout, encoding="utf-8")
    (raw_root / "codex.stderr.txt").write_text(result.stderr, encoding="utf-8")
    summary = base.event_summary(result.stdout)
    diagnosis = None
    diagnosis_valid = False
    output_path = Path(record["output_path"])
    if output_path.is_file():
        try:
            diagnosis = json.loads(output_path.read_text(encoding="utf-8"))
            diagnosis_valid = isinstance(diagnosis, dict)
        except json.JSONDecodeError:
            pass
    current_workspace = base.snapshot_tree(WORKSPACE)
    after_snapshot = base.snapshot_tree(Path(record["snapshot_path"]))
    changed_files = sorted(
        path for path in set(record["setup_snapshot"]) | set(current_workspace)
        if record["setup_snapshot"].get(path) != current_workspace.get(path)
    )
    model_execution_started = bool(summary.get("execution_id"))
    infrastructure_failure = result.returncode != 0 and not model_execution_started and not timed_out
    execution = {
        "run_id": RUN_ID,
        "scenario": SCENARIO,
        "condition": "B-new replication",
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
        "capabilities": historical.capability_observations(summary, WORKSPACE),
        "diagnosis_valid_json_object": diagnosis_valid,
        "diagnosis": diagnosis,
        "workspace_changed_files": changed_files,
        "files_created_outside_required_diagnosis": [path for path in changed_files if path != "diagnosis.json"],
        "snapshot_tree_sha256_before": sha256_bytes(json.dumps(before_snapshot, sort_keys=True).encode()),
        "snapshot_tree_sha256_after": sha256_bytes(json.dumps(after_snapshot, sort_keys=True).encode()),
        "snapshot_unchanged": before_snapshot == after_snapshot,
        "artifacts": {
            "root": str(ARTIFACT_ROOT),
            "codex_jsonl": str(raw_root / "codex.jsonl"),
            "codex_stderr": str(raw_root / "codex.stderr.txt"),
            "workspace": str(ARTIFACT_ROOT / "workspace"),
        },
    }
    write_json(RESULT_ROOT / "execution.json", execution)
    base.copy_workspace_evidence(WORKSPACE, ARTIFACT_ROOT / "workspace")
    record["attempts"].append({
        "attempt": attempt,
        "model_execution_started": model_execution_started,
        "infrastructure_failure_before_model_execution": infrastructure_failure,
        "exit_status": result.returncode,
    })
    record["status"] = "infrastructure_failed" if infrastructure_failure else (
        "completed" if result.returncode == 0 else "agent_failed"
    )
    write_json(CONTROL_PATH, record)
    print(RESULT_ROOT / "execution.json")
    return RESULT_ROOT / "execution.json"


def grade_native() -> Path:
    manifest = read_json(MANIFEST_PATH)
    execution = read_json(RESULT_ROOT / "execution.json")
    grade = {
        "run_id": RUN_ID,
        "scenario": SCENARIO,
        "condition": "B-new replication",
        "diagnosis_valid_json_object": execution["diagnosis_valid_json_object"],
        **base.native_grade(execution.get("diagnosis"), manifest["dataset"]["deterministic_matcher_spec"]),
    }
    path = RESULT_ROOT / "native.json"
    write_json(path, grade)
    print(path)
    return path


def post_run_integrity() -> Path:
    manifest = read_json(MANIFEST_PATH)
    record = read_json(CONTROL_PATH)
    execution = read_json(RESULT_ROOT / "execution.json")
    verify_product_unchanged(manifest)
    checks = {
        "exactly_one_attempt_started_model": sum(bool(item["model_execution_started"]) for item in record["attempts"]) == 1,
        "scenario_17_only": execution["scenario"] == SCENARIO,
        "snapshot_unchanged": execution["snapshot_unchanged"],
        "only_diagnosis_changed": execution["workspace_changed_files"] == ["diagnosis.json"],
        "no_extra_workspace_files": execution["files_created_outside_required_diagnosis"] == [],
        "protocol_unchanged": manifest["protocol_sha256"] == sha256_file(HERE / "protocol.md"),
        "runner_unchanged": manifest["runner_sha256"] == sha256_file(Path(__file__).resolve()),
        "historical_evidence_unchanged": all([
            sha256_file(HISTORICAL_EXECUTION) == manifest["historical_comparison"]["execution_sha256"],
            sha256_file(HISTORICAL_NATIVE) == manifest["historical_comparison"]["native_grade_sha256"],
            sha256_file(HISTORICAL_FORENSICS) == manifest["historical_comparison"]["token_forensics_sha256"],
        ]),
    }
    value = {"created_at": utc_now(), "status": "passed" if all(checks.values()) else "failed", "checks": checks}
    write_json(INTEGRITY_PATH, value)
    print(INTEGRITY_PATH)
    if value["status"] != "passed":
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"post-run integrity failed: {', '.join(failed)}")
    return INTEGRITY_PATH


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--freeze", action="store_true")
    actions.add_argument("--prepare", action="store_true")
    actions.add_argument("--preflight", action="store_true")
    actions.add_argument("--run", action="store_true")
    actions.add_argument("--grade-native", action="store_true")
    actions.add_argument("--post-run-integrity", action="store_true")
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
    elif args.run:
        run_agent(args.codex_executable, args.timeout)
    elif args.grade_native:
        grade_native()
    elif args.post_run_integrity:
        post_run_integrity()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
