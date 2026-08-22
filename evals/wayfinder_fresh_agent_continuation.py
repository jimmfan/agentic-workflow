#!/usr/bin/env python3
"""Controlled three-condition fresh-agent Wayfinder continuation smoke."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
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

from evals import arc_wayfinder_v2 as infra
from evals import run as resume


EVAL_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = EVAL_ROOT.parent
CAMPAIGN_ID = "wayfinder-fresh-agent-continuation-v1"
CAMPAIGN_PATH = EVAL_ROOT / "campaigns" / f"{CAMPAIGN_ID}.json"
SCENARIO_ROOT = EVAL_ROOT / "scenarios" / "resume"
FIXTURE_ROOT = SCENARIO_ROOT / "fixture"
CONTROL_PATCH = (
    EVAL_ROOT
    / "scenarios"
    / CAMPAIGN_ID
    / "matched-old-wayfinder.patch"
)
RESULTS_ROOT = EVAL_ROOT / "results" / CAMPAIGN_ID
ARTIFACTS_ROOT = EVAL_ROOT / "artifacts" / CAMPAIGN_ID
FREEZE_PATH = RESULTS_ROOT / "frozen-evaluator.json"
PREFLIGHT_PATH = RESULTS_ROOT / "preflight.json"
RUN_ROOT = Path(tempfile.gettempdir()) / "agent-workflow-fresh-agent-continuation-v1"
ADOPT_SCRIPT = SOURCE_ROOT / "skills" / "agent-workflow" / "scripts" / "adopt.py"
WAYFINDER_SOURCE = SOURCE_ROOT / ".agents" / "skills" / "wayfinder"
FRAMEWORK_VERSION_PATH = SOURCE_ROOT / "skills" / "agent-workflow" / "VERSION"
CONDITIONS = ("A", "B", "C")
WORKFLOW_CONDITIONS = {"B", "C"}
TREATMENT_PATHS = (
    ".agent-workflow/contracts/wayfinder-state.md",
    ".agents/skills/wayfinder/SKILL.md",
)
FRESH_AGENT_MARKERS = (
    "fresh-agent continuation",
    "Would a competent fresh agent need this information to continue the work correctly?",
    "procedural history",
    "prior agent narrative",
)
PROCEDURAL_PATTERN = re.compile(
    r"\b(?:I|we)\s+(?:read|ran|created|updated|checked|found|tried|used|changed)\b"
    r"|\b(?:previous agent|phase 1|this session|then I)\b",
    re.I,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def campaign() -> dict[str, Any]:
    value = read_json(CAMPAIGN_PATH)
    if value.get("campaign_id") != CAMPAIGN_ID:
        raise RuntimeError("campaign manifest id mismatch")
    return value


def prompt_for(condition: str, phase: int) -> str:
    return str(campaign()["prompts"][condition][str(phase)])


def artifact_root_for(results_root: Path) -> Path:
    return ARTIFACTS_ROOT if results_root == RESULTS_ROOT else results_root / ".artifacts"


def critical_paths() -> list[Path]:
    paths = [Path(__file__).resolve(), CAMPAIGN_PATH, CONTROL_PATCH]
    paths.extend(path for path in sorted(SCENARIO_ROOT.rglob("*")) if path.is_file())
    for relative in (
        "skills/agent-workflow/runtime-projections/wayfinder.md",
        "skills/agent-workflow/payload/agent-workflow/contracts/wayfinder-state.md",
        ".agents/skills/wayfinder/SKILL.md",
    ):
        paths.append(SOURCE_ROOT / relative)
    return paths


def critical_digests() -> dict[str, str]:
    return {
        path.relative_to(SOURCE_ROOT).as_posix(): file_digest(path)
        for path in critical_paths()
    }


def source_head() -> str:
    result = infra.run_command(["git", "rev-parse", "HEAD"], cwd=SOURCE_ROOT)
    infra.require_success(result, "source git head")
    return result.stdout.strip()


def freeze_evaluator() -> Path:
    if FREEZE_PATH.exists():
        raise RuntimeError(f"already frozen: {FREEZE_PATH}")
    manifest = campaign()
    head = source_head()
    if head != manifest["candidate_git_sha"]:
        raise RuntimeError(f"candidate drift: expected {manifest['candidate_git_sha']}, got {head}")
    write_json(
        FREEZE_PATH,
        {
            "schema_version": 1,
            "campaign_id": CAMPAIGN_ID,
            "frozen_at": utc_now(),
            "candidate_git_sha": head,
            "critical_sha256": critical_digests(),
            "model": manifest["model"],
            "reasoning_effort": manifest["reasoning_effort"],
            "sandbox": manifest["sandbox"],
            "approval_policy": manifest["approval_policy"],
            "rule": "Any critical-file mismatch invalidates execution; never refreeze this campaign after live evidence.",
        },
    )
    return FREEZE_PATH


def verify_frozen_evaluator() -> dict[str, Any]:
    frozen = read_json(FREEZE_PATH)
    if frozen.get("critical_sha256") != critical_digests():
        raise RuntimeError("frozen evaluator mismatch")
    if frozen.get("candidate_git_sha") != source_head():
        raise RuntimeError("candidate commit changed after freeze")
    return frozen


def installed_digests(workspace: Path) -> dict[str, str]:
    roots = (
        workspace / ".agent-workflow",
        workspace / ".agents",
        workspace / "AGENTS.md",
        workspace / "CLAUDE.md",
    )
    paths: list[Path] = []
    for root in roots:
        if root.is_file():
            paths.append(root)
        elif root.is_dir():
            paths.extend(path for path in root.rglob("*") if path.is_file())
    return {path.relative_to(workspace).as_posix(): file_digest(path) for path in sorted(paths)}


def install_workflow(workspace: Path, condition: str) -> dict[str, Any]:
    adoption = infra.run_command(
        [
            sys.executable,
            str(ADOPT_SCRIPT),
            "install",
            str(workspace),
            "--source-revision",
            "unreleased-local-package",
        ],
        cwd=SOURCE_ROOT,
    )
    infra.require_success(adoption, "Agent Workflow adoption")
    destination = workspace / ".agents" / "skills" / "wayfinder"
    if destination.exists():
        raise RuntimeError(f"unexpected provider collision: {destination}")
    shutil.copytree(WAYFINDER_SOURCE, destination)
    candidate_digests = installed_digests(workspace)
    if condition == "B":
        applied = infra.run_command(
            ["git", "apply", "--whitespace=nowarn", str(CONTROL_PATCH)],
            cwd=workspace,
        )
        infra.require_success(applied, "matched old-Wayfinder control patch")
    final_digests = installed_digests(workspace)
    changed = sorted(
        path
        for path in candidate_digests.keys() | final_digests.keys()
        if candidate_digests.get(path) != final_digests.get(path)
    )
    if condition == "B" and tuple(changed) != tuple(sorted(TREATMENT_PATHS)):
        raise RuntimeError(f"control changed unexpected installed files: {changed}")
    if condition == "C" and changed:
        raise RuntimeError(f"candidate installation unexpectedly changed: {changed}")
    treatment_text = " ".join(
        "\n".join((workspace / path).read_text(encoding="utf-8") for path in TREATMENT_PATHS).split()
    )
    markers_present = {
        marker: " ".join(marker.split()) in treatment_text for marker in FRESH_AGENT_MARKERS
    }
    if condition == "B" and any(markers_present.values()):
        raise RuntimeError(f"control retained treatment markers: {markers_present}")
    if condition == "C" and not all(markers_present.values()):
        raise RuntimeError(f"candidate lost treatment markers: {markers_present}")
    return {
        "candidate_git_sha": source_head(),
        "framework_version": FRAMEWORK_VERSION_PATH.read_text(encoding="utf-8").strip(),
        "provider": "repository-pinned Wayfinder skill",
        "control_patch_sha256": file_digest(CONTROL_PATCH) if condition == "B" else None,
        "candidate_installed_sha256": digest_bytes(json.dumps(candidate_digests, sort_keys=True).encode()),
        "final_installed_sha256": digest_bytes(json.dumps(final_digests, sort_keys=True).encode()),
        "files_changed_from_candidate": changed,
        "treatment_markers_present": markers_present,
        "installed_file_sha256": final_digests,
    }


def prepare_run(condition: str, run_root: Path = RUN_ROOT) -> dict[str, Any]:
    if condition not in CONDITIONS:
        raise ValueError(condition)
    run_id = f"fresh-agent-{condition.lower()}-1-{uuid.uuid4().hex[:10]}"
    root = run_root / run_id
    workspace = root / "repo"
    root.mkdir(parents=True, exist_ok=False)
    shutil.copytree(FIXTURE_ROOT, workspace)
    installation = install_workflow(workspace, condition) if condition in WORKFLOW_CONDITIONS else None
    setup_commit = infra.init_git_repository(workspace)
    state = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "run_id": run_id,
        "condition": condition,
        "condition_name": campaign()["conditions"][condition]["name"],
        "workspace": str(workspace),
        "setup_commit": setup_commit,
        "setup_snapshot": infra.snapshot(workspace),
        "phase_start_snapshot": infra.snapshot(workspace),
        "phase": 1,
        "executions": [],
        "phase_results": {},
        "workflow_installation": installation,
        "created_at": utc_now(),
    }
    return state


def prepare_trio(run_root: Path = RUN_ROOT) -> dict[str, dict[str, Any]]:
    states = {condition: prepare_run(condition, run_root) for condition in CONDITIONS}
    workspaces = {state["workspace"] for state in states.values()}
    if len(workspaces) != 3:
        raise RuntimeError("conditions do not have separate workspaces")
    b = states["B"]["workflow_installation"]
    c = states["C"]["workflow_installation"]
    assert isinstance(b, dict) and isinstance(c, dict)
    differences = sorted(
        path
        for path in b["installed_file_sha256"].keys() | c["installed_file_sha256"].keys()
        if b["installed_file_sha256"].get(path) != c["installed_file_sha256"].get(path)
    )
    if tuple(differences) != tuple(sorted(TREATMENT_PATHS)):
        raise RuntimeError(f"B/C differ beyond treatment surfaces: {differences}")
    return states


def preflight(states: dict[str, dict[str, Any]]) -> dict[str, Any]:
    prior_audit = EVAL_ROOT / "results" / "arc-wayfinder-e2e-v2" / "context-isolation-audit.json"
    checks = {
        "frozen_evaluator_valid": bool(verify_frozen_evaluator()),
        "separate_git_roots": len({state["workspace"] for state in states.values()}) == 3,
        "baseline_has_no_framework": not (Path(states["A"]["workspace"]) / ".agent-workflow").exists(),
        "matched_control_only_changes_treatment_paths": states["B"]["workflow_installation"]["files_changed_from_candidate"] == sorted(TREATMENT_PATHS),
        "candidate_retains_treatment": all(states["C"]["workflow_installation"]["treatment_markers_present"].values()),
        "prompts_B_C_identical": campaign()["prompts"]["B"] == campaign()["prompts"]["C"],
        "controller_and_grader_outside_workspaces": all(
            Path(state["workspace"]) not in Path(__file__).resolve().parents for state in states.values()
        ),
        "prior_same_runner_isolation_audit_passed": prior_audit.is_file() and read_json(prior_audit).get("status") == "passed",
    }
    record = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "runner_controls": [
            "codex exec --ephemeral",
            "unique auth-only CODEX_HOME per phase",
            "--ignore-user-config --ignore-rules --strict-config",
            "shell_environment_policy.inherit=none",
            "separate fixture Git roots",
            "raw traces and graders outside evaluated repositories",
        ],
        "prior_isolation_audit": str(prior_audit),
        "prior_isolation_audit_sha256": file_digest(prior_audit) if prior_audit.is_file() else None,
        "recorded_at": utc_now(),
    }
    write_json(PREFLIGHT_PATH, record)
    if record["status"] != "passed":
        raise RuntimeError(f"preflight failed: {checks}")
    return record


def run_codex_phase(
    state: dict[str, Any],
    *,
    codex_executable: str = "codex",
    timeout: int = 1800,
    run_root: Path = RUN_ROOT,
) -> dict[str, Any]:
    verify_frozen_evaluator()
    manifest = campaign()
    phase = int(state["phase"])
    workspace = Path(state["workspace"])
    command = [
        codex_executable,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--strict-config",
        "-m",
        str(manifest["model"]),
        "-c",
        f'model_reasoning_effort="{manifest["reasoning_effort"]}"',
        "-c",
        f'approval_policy="{manifest["approval_policy"]}"',
        "-c",
        'shell_environment_policy.inherit="none"',
        "-s",
        str(manifest["sandbox"]),
        "-C",
        str(workspace),
        "--json",
        "-",
    ]
    ephemeral_root = run_root / str(state["run_id"]) / "ephemeral-codex-homes"
    ephemeral_root.mkdir(parents=True, exist_ok=True)
    codex_home, inventory = infra.create_minimal_codex_home(ephemeral_root)
    started = time.monotonic()
    try:
        result = infra.run_command(
            command,
            cwd=workspace,
            timeout=timeout,
            env=infra.sanitized_agent_environment(codex_home),
            input_text=prompt_for(str(state["condition"]), phase),
        )
        removed_bytes = infra.directory_size(codex_home)
    finally:
        shutil.rmtree(codex_home, ignore_errors=True)
    elapsed = time.monotonic() - started
    raw_root = ARTIFACTS_ROOT / "runs" / str(state["run_id"]) / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    stdout_path = raw_root / f"phase-{phase}.jsonl"
    stderr_path = raw_root / f"phase-{phase}.stderr.txt"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    summary = infra.event_execution_summary(result.stdout, elapsed)
    summary.update(
        {
            "mode": "automatic_ephemeral_codex_exec",
            "phase": phase,
            "command": command[:-1] + ["<prompt-via-stdin>"],
            "exit_status": result.returncode,
            "fresh_context": True,
            "parent_task_context_supplied": False,
            "prompt_sha256": digest_bytes(prompt_for(str(state["condition"]), phase).encode()),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "codex_home_isolation": {
                "pre_execution_inventory": inventory,
                "unique_per_process": True,
                "removed_after_process": not codex_home.exists(),
                "temporary_bytes_removed": removed_bytes,
            },
        }
    )
    return summary


def durable_state_paths(workspace: Path, condition: str, changed: Iterable[str]) -> list[str]:
    if condition in WORKFLOW_CONDITIONS:
        return sorted(
            path.relative_to(workspace).as_posix()
            for path in (workspace / ".agent-wayfinder").rglob("*")
            if path.is_file()
        ) if (workspace / ".agent-wayfinder").is_dir() else []
    return sorted(resume.durable_note_paths(changed))


def state_metrics(workspace: Path, paths: Iterable[str]) -> dict[str, Any]:
    texts = infra.read_texts(workspace, paths)
    procedural: list[dict[str, Any]] = []
    for path, body in texts.items():
        for number, line in enumerate(body.splitlines(), start=1):
            if PROCEDURAL_PATTERN.search(line):
                procedural.append({"path": path, "line": number, "snippet": line.strip()[:300]})
    combined = "\n".join(texts.values())
    return {
        "paths": sorted(texts),
        "file_count": len(texts),
        "line_count": sum(len(body.splitlines()) for body in texts.values()),
        "byte_count": sum(len(body.encode()) for body in texts.values()),
        "exact_fact_occurrences": combined.count(resume.AMI_PARAMETER),
        "procedural_history_line_count": len(procedural),
        "procedural_history_evidence": procedural,
        "classifier_note": "Conservative lexical indicator, not a semantic quality score.",
    }


def record_phase(state: dict[str, Any], execution: dict[str, Any]) -> None:
    workspace = Path(state["workspace"])
    phase = int(state["phase"])
    before = dict(state["phase_start_snapshot"])
    after = infra.snapshot(workspace)
    changed = infra.changed_files(before, after)
    if phase == 1:
        grade = resume.grade_resume_phase_1(
            workspace,
            before,
            "workflow" if state["condition"] in WORKFLOW_CONDITIONS else "baseline",
        )
        paths = durable_state_paths(workspace, str(state["condition"]), changed)
        grade["durable_state"] = state_metrics(workspace, paths)
        grade["safe_useful_progress"] = bool(
            grade["stopped_safely"]
            and grade["preserved_ami_fact_in_durable_repo_state"]
            and grade["recorded_instance_family_unknown"]
            and grade["recorded_isolation_unknown"]
        )
        state["phase_1_durable_paths"] = paths
    else:
        grade = resume.grade_resume_phase_2(workspace, before)
        read_paths = execution["continuation_cost"]["files_read_before_first_observed_write"]
        grade["reconstruction"] = {
            "files_read_before_first_write": read_paths,
            "state_path_reads_before_first_write": [
                path for path in read_paths if ".agent-wayfinder" in path or "handoff" in path.lower()
            ],
            "repository_evidence_reads_before_first_write": [
                path for path in read_paths if path.startswith(("docs/", "terraform/", "README"))
            ],
        }
        grade["verification_quality"] = {
            "agent_validation_command_observed": execution["validation_command_observed"],
            "agent_validation_events": execution["validation_events"],
            "grader_static_assertions_passed": grade["static_assertions_passed"],
            "grader_terraform_fmt_exit_status": grade["terraform_fmt_exit_status"],
        }
    grade["execution"] = execution
    state["phase_results"][str(phase)] = grade
    state["executions"].append(execution)
    snapshot_root = ARTIFACTS_ROOT / "runs" / str(state["run_id"]) / "snapshots"
    infra.snapshot_archive(workspace, snapshot_root / f"phase-{phase}.tar.gz")
    evidence = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "run_id": state["run_id"],
        "condition": state["condition"],
        "phase": phase,
        "prompt_sha256": execution["prompt_sha256"],
        "before_snapshot": before,
        "after_snapshot": after,
        "changed_files": changed,
        "grade": grade,
        "execution": execution,
        "repository_head": infra.git_head(workspace),
        "recorded_at": utc_now(),
    }
    write_json(RESULTS_ROOT / "runs" / str(state["run_id"]) / f"phase-{phase}.json", evidence)
    if execution["exit_status"] != 0:
        raise RuntimeError(f"{state['condition']} phase {phase} agent failed")
    if phase == 1:
        resume.mutate_resume_phase_2(workspace)
        state["phase"] = 2
        state["phase_start_snapshot"] = infra.snapshot(workspace)
    else:
        result = {
            "schema_version": 1,
            "campaign_id": CAMPAIGN_ID,
            "condition": state["condition"],
            "condition_name": state["condition_name"],
            "run_id": state["run_id"],
            "candidate_git_sha": campaign()["candidate_git_sha"],
            "workflow_installation": state["workflow_installation"],
            "phase_1": state["phase_results"]["1"],
            "phase_2": state["phase_results"]["2"],
            "fresh_execution_ids": [item["execution_id"] for item in state["executions"]],
            "fresh_processes_distinct": len({item["execution_id"] for item in state["executions"]}) == 2,
            "completed_at": utc_now(),
        }
        write_json(RESULTS_ROOT / "runs" / str(state["run_id"]) / "result.json", result)


def run_smoke(timeout: int = 1800) -> list[Path]:
    verify_frozen_evaluator()
    if RUN_ROOT.exists():
        raise RuntimeError(f"run root already exists: {RUN_ROOT}")
    states = prepare_trio()
    preflight(states)
    for item in campaign()["execution_order"]:
        condition, phase_text = item.split(":", 1)
        state = states[condition]
        phase = int(phase_text)
        if int(state["phase"]) != phase:
            raise RuntimeError(f"schedule mismatch for {condition}: {state['phase']} != {phase}")
        execution = run_codex_phase(state, timeout=timeout)
        record_phase(state, execution)
        print(
            f"{condition} phase {phase}: exit={execution['exit_status']} "
            f"elapsed={execution['elapsed_seconds']}s tools={execution['tool_action_count']}",
            flush=True,
        )
    paths = sorted(RESULTS_ROOT.glob("runs/*/result.json"))
    if len(paths) != 3:
        raise RuntimeError(f"expected three results, found {len(paths)}")
    return paths


def result_summary() -> dict[str, Any]:
    results = [read_json(path) for path in sorted(RESULTS_ROOT.glob("runs/*/result.json"))]
    if len(results) != 3:
        raise RuntimeError("smoke is incomplete")
    rows: list[dict[str, Any]] = []
    for result in sorted(results, key=lambda item: item["condition"]):
        p1 = result["phase_1"]
        p2 = result["phase_2"]
        executions = [p1["execution"], p2["execution"]]
        rows.append(
            {
                "condition": result["condition"],
                "name": result["condition_name"],
                "phase_1_safe_useful_progress": p1["safe_useful_progress"],
                "exact_fact_preserved": p1["preserved_ami_fact_in_durable_repo_state"],
                "durable_state_files": p1["durable_state"]["file_count"],
                "durable_state_lines": p1["durable_state"]["line_count"],
                "durable_state_bytes": p1["durable_state"]["byte_count"],
                "procedural_history_lines": p1["durable_state"]["procedural_history_line_count"],
                "phase_2_exact_fact_recovered": p2["recovered_exact_ami_parameter"],
                "phase_2_decision_applied": p2["found_new_architecture_decision"],
                "implementation_completed": p2["implementation_completed"],
                "validation_passed": p2["validation_passed"],
                "files_read_before_first_write": p2["execution"]["continuation_cost"]["file_read_count_before_first_observed_write"],
                "tool_actions_total": sum(item["tool_action_count"] for item in executions),
                "input_tokens_total": sum(item["input_tokens"] or 0 for item in executions),
                "cached_input_tokens_total": sum(item["cached_input_tokens"] or 0 for item in executions),
                "output_tokens_total": sum(item["output_tokens"] or 0 for item in executions),
                "reasoning_tokens_total": sum(item["reasoning_tokens"] or 0 for item in executions),
                "elapsed_seconds_total": round(sum(item["elapsed_seconds"] for item in executions), 3),
                "fresh_processes_distinct": result["fresh_processes_distinct"],
            }
        )
    summary = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "candidate_git_sha": campaign()["candidate_git_sha"],
        "repetitions_per_condition": 1,
        "stop_after_smoke": True,
        "prohibited_overall_score": True,
        "rows": rows,
        "interpretation_rule": "One smoke can reveal feasibility, regressions, or confounds; it cannot establish repeatability or statistical causality.",
        "generated_at": utc_now(),
    }
    write_json(RESULTS_ROOT / "summary.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--run-smoke", action="store_true")
    parser.add_argument("--summarize", action="store_true")
    parser.add_argument("--timeout", type=int, default=1800)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    selected = sum((arguments.freeze, arguments.run_smoke, arguments.summarize))
    if selected != 1:
        raise SystemExit("select exactly one of --freeze, --run-smoke, or --summarize")
    if arguments.freeze:
        print(freeze_evaluator())
    elif arguments.run_smoke:
        for path in run_smoke(arguments.timeout):
            print(path)
    else:
        print(json.dumps(result_summary(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
