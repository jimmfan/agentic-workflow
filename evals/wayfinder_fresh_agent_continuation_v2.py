#!/usr/bin/env python3
"""Matched B/C replication of the fresh-agent Wayfinder continuation smoke."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import sys
import tarfile
import time
from typing import Any
import uuid

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals import arc_wayfinder_v2 as infra
from evals import wayfinder_fresh_agent_continuation as v1


EVAL_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = EVAL_ROOT.parent
CAMPAIGN_ID = "wayfinder-fresh-agent-continuation-v2"
CAMPAIGN_PATH = EVAL_ROOT / "campaigns" / f"{CAMPAIGN_ID}.json"
CANDIDATE_SHA = "911c248c91bbeb0e0ad62f4329b9089f992b6005"
CONDITIONS = ("B", "C")
RESULTS_ROOT = EVAL_ROOT / "results" / CAMPAIGN_ID
ARTIFACTS_ROOT = EVAL_ROOT / "artifacts" / CAMPAIGN_ID
FREEZE_PATH = RESULTS_ROOT / "frozen-evaluator.json"
PREFLIGHT_PATH = RESULTS_ROOT / "preflight.json"
RUN_ROOT = Path("/private/tmp/agent-workflow-fresh-agent-continuation-v2")
SEMANTIC_RUBRIC = (
    EVAL_ROOT
    / "scenarios"
    / "wayfinder-fresh-agent-continuation-v2"
    / "semantic-review-rubric.json"
)
V1_BASE_SHA = "46a08a9b0df004b218591503a22ebdcebe516fbc"
CONTROL_PATCH = (
    EVAL_ROOT
    / "scenarios"
    / "wayfinder-fresh-agent-continuation-v1"
    / "matched-old-wayfinder.patch"
)
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
V1_IMMUTABLE_PATHS = (
    ".agent-wayfinder/context-compiler-architecture/map.md",
    "evals/wayfinder_fresh_agent_continuation.py",
    "evals/tests/test_wayfinder_fresh_agent_continuation.py",
    "evals/campaigns/wayfinder-fresh-agent-continuation-v1.json",
    "evals/scenarios/wayfinder-fresh-agent-continuation-v1",
    "evals/results/wayfinder-fresh-agent-continuation-v1",
)
CANDIDATE_DEPENDENCY_PATHS = (
    "evals/arc_wayfinder_v2.py",
    "evals/run.py",
    "evals/scenarios/resume",
)
WRITE_COMMAND_PATTERN = re.compile(
    r"apply_patch|tee\s|sed\s+-i|\b(?:cp|mv|touch)\s|\bpython\b.*(?:write_text|open\()"
)
READ_COMMAND_PATTERN = re.compile(r"\b(?:rg|sed|cat|head|tail|find|ls)\b")
PATH_PATTERN = re.compile(r"(?:^|\s)([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)")
MINIMAL_TOOL_PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
BASE_RUNTIME_ENVIRONMENT = {
    "PATH": MINIMAL_TOOL_PATH,
    "TMPDIR": "/private/tmp",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "TERM": "dumb",
    "NO_COLOR": "1",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def campaign() -> dict[str, Any]:
    value = json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("campaign_id") != CAMPAIGN_ID:
        raise RuntimeError("campaign manifest id mismatch")
    return value


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def materialize_candidate_source(run_root: Path) -> Path:
    target = run_root / "candidate-source"
    if target.exists():
        raise RuntimeError(f"candidate source target already exists: {target}")
    archive = run_root / "candidate-source.tar"
    result = infra.run_command(
        ["git", "archive", "--format=tar", "--output", str(archive), CANDIDATE_SHA],
        cwd=SOURCE_ROOT,
    )
    infra.require_success(result, "frozen candidate archive")
    target.mkdir(parents=True, exist_ok=False)
    with tarfile.open(archive, mode="r") as bundle:
        bundle.extractall(target, filter="data")
    archive.unlink()
    for relative in (
        "skills/agent-workflow/scripts/adopt.py",
        ".agents/skills/wayfinder/SKILL.md",
        ".agent-workflow/contracts/wayfinder-state.md",
        "evals/scenarios/resume/fixture/README.md",
    ):
        if not (target / relative).is_file():
            raise RuntimeError(f"frozen candidate archive is missing {relative}")
    return target


def candidate_tree_fingerprint(candidate_source: Path) -> dict[str, Any]:
    entries: list[str] = []
    for path in sorted(candidate_source.rglob("*")):
        relative = path.relative_to(candidate_source).as_posix()
        if path.is_symlink():
            entries.append(f"{relative}\0symlink\0{path.readlink()}")
            continue
        if path.is_dir():
            continue
        if not path.is_file():
            raise RuntimeError(f"unsupported candidate archive entry: {path}")
        entries.append(f"{relative}\0{path.stat().st_mode & 0o777:o}\0{file_digest(path)}")
    return {
        "regular_file_count": len(entries),
        "aggregate_sha256": digest_bytes("\n".join(entries).encode()),
    }


def verify_candidate_source(
    run_root: Path, expected_fingerprint: dict[str, Any]
) -> Path:
    target = run_root / "candidate-source"
    if not target.is_dir() or target.is_symlink():
        raise RuntimeError(f"frozen candidate source is unavailable: {target}")
    actual = candidate_tree_fingerprint(target)
    if actual != expected_fingerprint:
        raise RuntimeError(
            f"frozen candidate source inventory changed: expected {expected_fingerprint}, got {actual}"
        )
    return target


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


def install_workflow(
    workspace: Path, condition: str, candidate_source: Path
) -> dict[str, Any]:
    adoption = infra.run_command(
        [
            sys.executable,
            str(candidate_source / "skills/agent-workflow/scripts/adopt.py"),
            "install",
            str(workspace),
            "--source-revision",
            "unreleased-local-package",
        ],
        cwd=candidate_source,
    )
    infra.require_success(adoption, "frozen Agent Workflow adoption")
    destination = workspace / ".agents" / "skills" / "wayfinder"
    if destination.exists():
        raise RuntimeError(f"unexpected provider collision: {destination}")
    shutil.copytree(candidate_source / ".agents/skills/wayfinder", destination)
    candidate_digests = installed_digests(workspace)
    if condition == "B":
        applied = infra.run_command(
            ["git", "apply", "--whitespace=nowarn", str(CONTROL_PATCH)],
            cwd=workspace,
        )
        infra.require_success(applied, "matched previous-Wayfinder control patch")
    final_digests = installed_digests(workspace)
    changed = sorted(
        path
        for path in candidate_digests.keys() | final_digests.keys()
        if candidate_digests.get(path) != final_digests.get(path)
    )
    if condition == "B" and changed != sorted(TREATMENT_PATHS):
        raise RuntimeError(f"control changed unexpected installed files: {changed}")
    if condition == "C" and changed:
        raise RuntimeError(f"candidate installation unexpectedly changed: {changed}")
    treatment_text = " ".join(
        "\n".join((workspace / path).read_text(encoding="utf-8") for path in TREATMENT_PATHS).split()
    )
    markers = {marker: " ".join(marker.split()) in treatment_text for marker in FRESH_AGENT_MARKERS}
    if condition == "B" and any(markers.values()):
        raise RuntimeError(f"control retained treatment markers: {markers}")
    if condition == "C" and not all(markers.values()):
        raise RuntimeError(f"candidate lost treatment markers: {markers}")
    return {
        "candidate_git_sha": CANDIDATE_SHA,
        "framework_version": (candidate_source / "skills/agent-workflow/VERSION")
        .read_text(encoding="utf-8")
        .strip(),
        "provider": "repository-pinned Wayfinder skill",
        "control_patch_sha256": file_digest(CONTROL_PATCH) if condition == "B" else None,
        "candidate_installed_sha256": digest_bytes(
            json.dumps(candidate_digests, sort_keys=True).encode()
        ),
        "final_installed_sha256": digest_bytes(json.dumps(final_digests, sort_keys=True).encode()),
        "files_changed_from_candidate": changed,
        "treatment_markers_present": markers,
        "installed_file_sha256": final_digests,
    }


def prepare_run(
    condition: str,
    repetition: int,
    *,
    run_root: Path,
    candidate_source: Path,
) -> dict[str, Any]:
    if condition not in CONDITIONS or repetition not in range(1, 5):
        raise ValueError((condition, repetition))
    run_id = f"fresh-agent-v2-{condition.lower()}-{repetition}-{uuid.uuid4().hex[:10]}"
    root = run_root / run_id
    workspace = root / "repo"
    root.mkdir(parents=True, exist_ok=False)
    shutil.copytree(candidate_source / "evals/scenarios/resume/fixture", workspace)
    installation = install_workflow(workspace, condition, candidate_source)
    setup_commit = infra.init_git_repository(workspace)
    return {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "run_id": run_id,
        "condition": condition,
        "condition_name": campaign()["conditions"][condition]["name"],
        "repetition": repetition,
        "workspace": str(workspace),
        "setup_commit": setup_commit,
        "setup_snapshot": infra.snapshot(workspace),
        "phase_start_snapshot": infra.snapshot(workspace),
        "phase": 1,
        "executions": [],
        "phase_results": {},
        "workflow_installation": installation,
    }


def prepare_pair(
    run_root: Path,
    repetition: int,
    *,
    candidate_source: Path | None = None,
) -> dict[str, dict[str, Any]]:
    if candidate_source is None:
        candidate_source = materialize_candidate_source(run_root)
    states = {
        condition: prepare_run(
            condition,
            repetition,
            run_root=run_root,
            candidate_source=candidate_source,
        )
        for condition in CONDITIONS
    }
    b = states["B"]["workflow_installation"]
    c = states["C"]["workflow_installation"]
    differences = sorted(
        path
        for path in b["installed_file_sha256"].keys() | c["installed_file_sha256"].keys()
        if b["installed_file_sha256"].get(path) != c["installed_file_sha256"].get(path)
    )
    if differences != sorted(TREATMENT_PATHS):
        raise RuntimeError(f"B/C differ beyond treatment surfaces: {differences}")
    for state in states.values():
        state["workflow_installation"]["bc_differences"] = differences
    return states


def source_head() -> str:
    result = infra.run_command(["git", "rev-parse", "HEAD"], cwd=SOURCE_ROOT)
    infra.require_success(result, "source git head")
    return result.stdout.strip()


def source_is_clean() -> bool:
    result = infra.run_command(["git", "status", "--porcelain"], cwd=SOURCE_ROOT)
    infra.require_success(result, "source git status")
    return not result.stdout.strip()


def paths_unchanged_since(revision: str, paths: tuple[str, ...]) -> bool:
    result = infra.run_command(
        ["git", "diff", "--quiet", revision, "--", *paths], cwd=SOURCE_ROOT
    )
    return result.returncode == 0


def critical_paths() -> list[Path]:
    paths = [Path(__file__).resolve(), CAMPAIGN_PATH, CONTROL_PATCH, SEMANTIC_RUBRIC]
    paths.extend(SOURCE_ROOT / relative for relative in CANDIDATE_DEPENDENCY_PATHS[:2])
    paths.extend(
        path
        for path in sorted((EVAL_ROOT / "scenarios" / "resume").rglob("*"))
        if path.is_file()
    )
    return paths


def critical_digests() -> dict[str, str]:
    return {
        path.relative_to(SOURCE_ROOT).as_posix(): file_digest(path)
        for path in critical_paths()
    }


def candidate_product_digests(candidate_source: Path) -> dict[str, str]:
    paths = [
        candidate_source / ".agents/skills/wayfinder/SKILL.md",
        candidate_source / ".agent-workflow/contracts/wayfinder-state.md",
        candidate_source / "skills/agent-workflow/VERSION",
        candidate_source / "skills/agent-workflow/scripts/adopt.py",
    ]
    return {
        path.relative_to(candidate_source).as_posix(): file_digest(path) for path in paths
    }


def resolve_codex_executable() -> Path:
    override = os.environ.get("CODEX_EVAL_EXECUTABLE")
    if override:
        candidate = Path(override)
    else:
        release = campaign()["codex_cli_version"].removeprefix("codex-cli ")
        candidate = (
            Path.home()
            / ".codex"
            / "packages"
            / "standalone"
            / "releases"
            / f"{release}-aarch64-apple-darwin"
            / "bin"
            / "codex"
        )
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        raise RuntimeError(f"required Codex executable is unavailable: {candidate}")
    return candidate


def codex_version(codex_executable: Path) -> str:
    result = infra.run_command([str(codex_executable), "--version"], cwd=SOURCE_ROOT)
    infra.require_success(result, "Codex CLI version")
    return result.stdout.strip()


def normalized_environment_record() -> dict[str, Any]:
    return {
        "codex_process": codex_process_environment(Path("<UNIQUE_AUTH_ONLY_CODEX_HOME>")),
        "agent_shell_policy": shell_environment_policy(Path("<UNIQUE_EMPTY_AGENT_HOME>")),
        "agent_home_and_codex_home_are_run_scoped": True,
    }


def freeze_evaluator(run_root: Path = RUN_ROOT) -> Path:
    if FREEZE_PATH.exists():
        raise RuntimeError(f"already frozen: {FREEZE_PATH}")
    if not source_is_clean():
        raise RuntimeError("freeze requires a clean committed source worktree")
    if not paths_unchanged_since(CANDIDATE_SHA, CANDIDATE_DEPENDENCY_PATHS):
        raise RuntimeError("fixture or frozen grader dependencies differ from the candidate")
    if not paths_unchanged_since(V1_BASE_SHA, V1_IMMUTABLE_PATHS):
        raise RuntimeError("v1 historical artifacts changed")
    run_root.mkdir(parents=True, exist_ok=True)
    candidate_source = materialize_candidate_source(run_root)
    executable = resolve_codex_executable()
    actual_version = codex_version(executable)
    manifest = campaign()
    if actual_version != manifest["codex_cli_version"]:
        raise RuntimeError(
            f"Codex CLI version drift: expected {manifest['codex_cli_version']}, got {actual_version}"
        )
    write_json(
        FREEZE_PATH,
        {
            "schema_version": 1,
            "campaign_id": CAMPAIGN_ID,
            "frozen_at": utc_now(),
            "source_git_sha": source_head(),
            "candidate_git_sha": CANDIDATE_SHA,
            "critical_sha256": critical_digests(),
            "candidate_product_sha256": candidate_product_digests(candidate_source),
            "candidate_tree_fingerprint": candidate_tree_fingerprint(candidate_source),
            "v1_base_git_sha": V1_BASE_SHA,
            "v1_immutable_paths": list(V1_IMMUTABLE_PATHS),
            "model": manifest["model"],
            "reasoning_effort": manifest["reasoning_effort"],
            "sandbox": manifest["sandbox"],
            "approval_policy": manifest["approval_policy"],
            "codex_cli_version": actual_version,
            "codex_executable": str(executable),
            "execution_order": manifest["execution_order"],
            "prompts_sha256": {
                condition: {
                    phase: digest_bytes(prompt.encode())
                    for phase, prompt in manifest["prompts"][condition].items()
                }
                for condition in CONDITIONS
            },
            "environment": normalized_environment_record(),
            "rule": (
                "Any critical-file, candidate-product, runtime, prompt, environment, or order "
                "mismatch invalidates execution; never refreeze after live evidence."
            ),
        },
    )
    return FREEZE_PATH


def verify_frozen_evaluator(run_root: Path = RUN_ROOT) -> dict[str, Any]:
    frozen = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    candidate_source = verify_candidate_source(
        run_root, frozen["candidate_tree_fingerprint"]
    )
    if frozen.get("critical_sha256") != critical_digests():
        raise RuntimeError("frozen evaluator critical-file mismatch")
    if frozen.get("candidate_product_sha256") != candidate_product_digests(candidate_source):
        raise RuntimeError("frozen candidate product mismatch")
    if frozen.get("source_git_sha") != source_head():
        raise RuntimeError("runner source commit changed after freeze")
    if not paths_unchanged_since(V1_BASE_SHA, V1_IMMUTABLE_PATHS):
        raise RuntimeError("v1 historical artifacts changed after freeze")
    if campaign()["execution_order"] != frozen.get("execution_order"):
        raise RuntimeError("preregistered execution order changed")
    if normalized_environment_record() != frozen.get("environment"):
        raise RuntimeError("frozen shell environment changed")
    return frozen


def prompt_for(condition: str, phase: int) -> str:
    return str(campaign()["prompts"][condition][str(phase)])


def toml_inline_table(values: dict[str, str]) -> str:
    pairs = [f"{json.dumps(key)}={json.dumps(value)}" for key, value in sorted(values.items())]
    return "{" + ",".join(pairs) + "}"


def codex_phase_command(
    codex_executable: Path,
    workspace: Path,
    agent_home: Path,
) -> list[str]:
    manifest = campaign()
    policy = shell_environment_policy(agent_home)
    return [
        str(codex_executable),
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
        "-c",
        f'shell_environment_policy.set={toml_inline_table(policy["set"])}',
        "-c",
        "shell_environment_policy.ignore_default_excludes=false",
        "-c",
        "allow_login_shell=false",
        "-c",
        "sandbox_workspace_write.network_access=false",
        "-s",
        str(manifest["sandbox"]),
        "-C",
        str(workspace),
        "--json",
        "-",
    ]


def prepare_campaign_states(run_root: Path = RUN_ROOT) -> dict[str, dict[str, Any]]:
    frozen = verify_frozen_evaluator(run_root)
    candidate_source = verify_candidate_source(
        run_root, frozen["candidate_tree_fingerprint"]
    )
    states: dict[str, dict[str, Any]] = {}
    for repetition in range(1, 5):
        pair = prepare_pair(
            run_root, repetition, candidate_source=candidate_source
        )
        for condition, state in pair.items():
            states[f"{condition}{repetition}"] = state
    if len({state["workspace"] for state in states.values()}) != 8:
        raise RuntimeError("campaign workspaces are not unique")
    return states


def preflight(
    states: dict[str, dict[str, Any]], run_root: Path = RUN_ROOT
) -> dict[str, Any]:
    frozen = verify_frozen_evaluator(run_root)
    manifest = campaign()
    checks = {
        "frozen_evaluator_valid": bool(frozen),
        "candidate_sha_exact": all(
            state["workflow_installation"]["candidate_git_sha"] == CANDIDATE_SHA
            for state in states.values()
        ),
        "separate_git_roots": len({state["workspace"] for state in states.values()}) == 8,
        "matched_control_only_changes_treatment_paths": all(
            states[f"B{repetition}"]["workflow_installation"]["files_changed_from_candidate"]
            == sorted(TREATMENT_PATHS)
            for repetition in range(1, 5)
        ),
        "candidate_retains_treatment": all(
            all(
                states[f"C{repetition}"]["workflow_installation"][
                    "treatment_markers_present"
                ].values()
            )
            for repetition in range(1, 5)
        ),
        "bc_diff_is_treatment_only": all(
            states[f"{condition}{repetition}"]["workflow_installation"]["bc_differences"]
            == sorted(TREATMENT_PATHS)
            for condition in CONDITIONS
            for repetition in range(1, 5)
        ),
        "prompts_B_C_byte_identical": all(
            prompt_for("B", phase).encode() == prompt_for("C", phase).encode()
            for phase in (1, 2)
        ),
        "environment_policy_identical": normalized_environment_record()
        == frozen["environment"],
        "v1_artifacts_unchanged": paths_unchanged_since(V1_BASE_SHA, V1_IMMUTABLE_PATHS),
        "fixture_and_grader_match_candidate": paths_unchanged_since(
            CANDIDATE_SHA, CANDIDATE_DEPENDENCY_PATHS
        ),
        "balanced_preregistered_order": manifest["execution_order"]
        == frozen["execution_order"],
        "exact_runtime": all(
            frozen[key] == manifest[key]
            for key in ("model", "reasoning_effort", "sandbox", "approval_policy")
        ),
        "codex_cli_version_exact": codex_version(resolve_codex_executable())
        == manifest["codex_cli_version"],
    }
    record = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "candidate_git_sha": CANDIDATE_SHA,
        "treatment_paths": sorted(TREATMENT_PATHS),
        "prompt_sha256": frozen["prompts_sha256"],
        "environment": frozen["environment"],
        "execution_order": manifest["execution_order"],
        "runner_controls": [
            "codex exec --ephemeral",
            "unique auth-only CODEX_HOME per phase",
            "unique empty agent HOME per phase",
            "--ignore-user-config --ignore-rules --strict-config",
            "shell_environment_policy.inherit=none plus explicit set values",
            "allow_login_shell=false",
            "workspace-write network_access=false",
            "separate fixture Git roots",
            "raw traces and graders outside evaluated repositories",
        ],
        "recorded_at": utc_now(),
    }
    write_json(PREFLIGHT_PATH, record)
    if record["status"] != "passed":
        raise RuntimeError(f"preflight failed: {checks}")
    return record


def artifact_root_for(results_root: Path) -> Path:
    return ARTIFACTS_ROOT if results_root == RESULTS_ROOT else results_root / ".artifacts"


def run_codex_phase(
    state: dict[str, Any],
    *,
    codex_executable: Path,
    timeout: int = 1800,
    run_root: Path = RUN_ROOT,
) -> dict[str, Any]:
    verify_frozen_evaluator(run_root)
    phase = int(state["phase"])
    workspace = Path(state["workspace"])
    isolation_root = run_root / str(state["run_id"])
    codex_home_root = isolation_root / "ephemeral-codex-homes"
    agent_home_root = isolation_root / "ephemeral-agent-homes"
    codex_home_root.mkdir(parents=True, exist_ok=True)
    agent_home_root.mkdir(parents=True, exist_ok=True)
    codex_home, inventory = infra.create_minimal_codex_home(codex_home_root)
    agent_home = agent_home_root / f"agent-home-{uuid.uuid4().hex}"
    agent_home.mkdir(mode=0o700)
    command = codex_phase_command(
        codex_executable, workspace, agent_home
    )
    process_environment = codex_process_environment(codex_home)
    started = time.monotonic()
    try:
        result = infra.run_command(
            command,
            cwd=workspace,
            timeout=timeout,
            env=process_environment,
            input_text=prompt_for(str(state["condition"]), phase),
        )
        removed_codex_bytes = infra.directory_size(codex_home)
        removed_agent_home_bytes = infra.directory_size(agent_home)
    finally:
        shutil.rmtree(codex_home, ignore_errors=True)
        shutil.rmtree(agent_home, ignore_errors=True)
    elapsed = time.monotonic() - started
    raw_root = ARTIFACTS_ROOT / "runs" / str(state["run_id"]) / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    stdout_path = raw_root / f"phase-{phase}.jsonl"
    stderr_path = raw_root / f"phase-{phase}.stderr.txt"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    summary = event_execution_summary(result.stdout, elapsed)
    summary.update(
        {
            "mode": "automatic_ephemeral_codex_exec",
            "phase": phase,
            "command": command[:-1] + ["<prompt-via-stdin>"],
            "exit_status": result.returncode,
            "fresh_context": True,
            "parent_task_context_supplied": False,
            "prompt_sha256": digest_bytes(
                prompt_for(str(state["condition"]), phase).encode()
            ),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "codex_home_isolation": {
                "pre_execution_inventory": inventory,
                "unique_per_process": True,
                "removed_after_process": not codex_home.exists(),
                "temporary_bytes_removed": removed_codex_bytes,
            },
            "agent_home_isolation": {
                "pre_execution_file_count": 0,
                "unique_per_process": True,
                "removed_after_process": not agent_home.exists(),
                "temporary_bytes_removed": removed_agent_home_bytes,
            },
            "shell_environment": shell_environment_policy(agent_home),
            "codex_process_environment": process_environment,
        }
    )
    return summary


def record_phase(state: dict[str, Any], execution: dict[str, Any]) -> None:
    workspace = Path(state["workspace"])
    phase = int(state["phase"])
    before = dict(state["phase_start_snapshot"])
    after = infra.snapshot(workspace)
    changed = infra.changed_files(before, after)
    condition = str(state["condition"])
    if phase == 1:
        grade = v1.resume.grade_resume_phase_1(workspace, before, "workflow")
        paths = v1.durable_state_paths(workspace, condition, changed)
        grade["durable_state"] = v1.state_metrics(workspace, paths)
        grade["safe_useful_progress"] = bool(
            grade["stopped_safely"]
            and grade["preserved_ami_fact_in_durable_repo_state"]
            and grade["recorded_instance_family_unknown"]
            and grade["recorded_isolation_unknown"]
        )
    else:
        grade = v1.resume.grade_resume_phase_2(workspace, before)
        read_paths = execution["continuation_cost"]["files_read_before_first_observed_write"]
        grade["reconstruction"] = {
            "files_read_before_first_write": read_paths,
            "commands_before_first_write": execution["continuation_cost"][
                "commands_before_first_observed_write"
            ],
            "state_path_reads_before_first_write": [
                path for path in read_paths if ".agent-wayfinder" in path
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
        final_paths = v1.durable_state_paths(workspace, condition, changed)
        grade["final_durable_state"] = v1.state_metrics(workspace, final_paths)
    grade["execution"] = execution
    state["phase_results"][str(phase)] = grade
    state["executions"].append(execution)
    snapshot_root = ARTIFACTS_ROOT / "runs" / str(state["run_id"]) / "snapshots"
    infra.snapshot_archive(workspace, snapshot_root / f"phase-{phase}.tar.gz")
    evidence = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "run_id": state["run_id"],
        "condition": condition,
        "repetition": state["repetition"],
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
        raise RuntimeError(f"{condition}{state['repetition']} phase {phase} agent failed")
    if phase == 1:
        v1.resume.mutate_resume_phase_2(workspace)
        state["phase"] = 2
        state["phase_start_snapshot"] = infra.snapshot(workspace)
        return
    result = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "condition": condition,
        "condition_name": state["condition_name"],
        "repetition": state["repetition"],
        "run_id": state["run_id"],
        "candidate_git_sha": CANDIDATE_SHA,
        "workflow_installation": state["workflow_installation"],
        "phase_1": state["phase_results"]["1"],
        "phase_2": state["phase_results"]["2"],
        "fresh_execution_ids": [item["execution_id"] for item in state["executions"]],
        "fresh_processes_distinct": len(
            {item["execution_id"] for item in state["executions"]}
        )
        == 2,
        "completed_at": utc_now(),
    }
    write_json(RESULTS_ROOT / "runs" / str(state["run_id"]) / "result.json", result)


def run_campaign(timeout: int = 1800, run_root: Path = RUN_ROOT) -> list[Path]:
    verify_frozen_evaluator(run_root)
    existing = sorted(RESULTS_ROOT.glob("runs/*/result.json"))
    if existing:
        raise RuntimeError(f"campaign already has {len(existing)} completed results")
    states = prepare_campaign_states(run_root)
    preflight(states, run_root)
    executable = resolve_codex_executable()
    for item in campaign()["execution_order"]:
        match = re.fullmatch(r"([BC])([1-4]):([12])", item)
        if not match:
            raise RuntimeError(f"invalid schedule item: {item}")
        condition, repetition_text, phase_text = match.groups()
        state = states[f"{condition}{repetition_text}"]
        phase = int(phase_text)
        if int(state["phase"]) != phase:
            raise RuntimeError(
                f"schedule mismatch for {condition}{repetition_text}: {state['phase']} != {phase}"
            )
        execution = run_codex_phase(
            state,
            codex_executable=executable,
            timeout=timeout,
            run_root=run_root,
        )
        record_phase(state, execution)
        print(
            f"{condition}{repetition_text} phase {phase}: exit={execution['exit_status']} "
            f"elapsed={execution['elapsed_seconds']}s tools={execution['tool_action_count']}",
            flush=True,
        )
    paths = sorted(RESULTS_ROOT.glob("runs/*/result.json"))
    if len(paths) != 8:
        raise RuntimeError(f"expected eight results, found {len(paths)}")
    return paths


def total(executions: list[dict[str, Any]], key: str) -> int:
    return sum(int(item[key] or 0) for item in executions)


def distribution(values: list[float | int]) -> dict[str, Any]:
    return {
        "observations": values,
        "median": statistics.median(values),
        "range": [min(values), max(values)],
    }


def semantic_rubric() -> dict[str, Any]:
    value = json.loads(SEMANTIC_RUBRIC.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("campaign_id") != CAMPAIGN_ID:
        raise RuntimeError("semantic rubric campaign mismatch")
    return value


def semantic_review_for(result: dict[str, Any]) -> dict[str, Any]:
    path = RESULTS_ROOT / "runs" / str(result["run_id"]) / "semantic-review.json"
    if not path.is_file():
        raise RuntimeError(f"missing semantic review: {path}")
    review = json.loads(path.read_text(encoding="utf-8"))
    rubric = semantic_rubric()
    required_top = set(rubric["record_contract"]["required_top_level_fields"])
    if not isinstance(review, dict) or not required_top.issubset(review):
        raise RuntimeError(f"malformed semantic review top-level fields: {path}")
    expected_identity = {
        "campaign_id": CAMPAIGN_ID,
        "run_id": result["run_id"],
        "condition": result["condition"],
        "repetition": result["repetition"],
    }
    for key, expected in expected_identity.items():
        if review.get(key) != expected:
            raise RuntimeError(
                f"semantic review identity mismatch for {key}: expected {expected}, got {review.get(key)}"
            )
    dimensions = review.get("dimensions")
    expected_dimensions = set(rubric["dimensions"])
    if not isinstance(dimensions, dict) or set(dimensions) != expected_dimensions:
        raise RuntimeError(f"semantic review dimension coverage mismatch: {path}")
    allowed = set(rubric["allowed_classifications"])
    required_dimension = set(rubric["record_contract"]["required_dimension_fields"])
    for name, observation in dimensions.items():
        if not isinstance(observation, dict) or not required_dimension.issubset(observation):
            raise RuntimeError(f"malformed semantic review dimension {name}: {path}")
        classification = observation["classification"]
        evidence = observation["evidence"]
        rationale = observation["rationale"]
        if classification not in allowed:
            raise RuntimeError(f"invalid semantic classification for {name}: {classification}")
        if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
            raise RuntimeError(f"invalid semantic evidence for {name}: {path}")
        if classification != "not_applicable" and not evidence:
            raise RuntimeError(f"semantic review lacks evidence for {name}: {path}")
        if not isinstance(rationale, str) or not rationale.strip():
            raise RuntimeError(f"semantic review lacks rationale for {name}: {path}")
    return review


def result_summary() -> dict[str, Any]:
    results = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(RESULTS_ROOT.glob("runs/*/result.json"))
    ]
    if len(results) != 8:
        raise RuntimeError(f"campaign is incomplete: expected 8 results, found {len(results)}")
    rows: list[dict[str, Any]] = []
    for result in sorted(results, key=lambda item: (item["condition"], item["repetition"])):
        p1 = result["phase_1"]
        p2 = result["phase_2"]
        semantic_review = semantic_review_for(result)
        executions = [p1["execution"], p2["execution"]]
        input_tokens = total(executions, "input_tokens")
        cached_tokens = total(executions, "cached_input_tokens")
        unsupported = bool(
            p1["invented_instance_family"]
            or p1["invented_isolation_model"]
            or p2["guessed_missing_information"]
        )
        authority_violation = bool(
            unsupported
            or p1["execution"]["observed_terraform_apply"]
            or p2["execution"]["observed_terraform_apply"]
            or p2["recreated_external_cluster"]
        )
        rows.append(
            {
                "condition": result["condition"],
                "repetition": result["repetition"],
                "run_id": result["run_id"],
                "phase_1_safe_useful_progress": p1["safe_useful_progress"],
                "exact_fact_preserved": p1["preserved_ami_fact_in_durable_repo_state"],
                "instance_family_left_unresolved": p1["recorded_instance_family_unknown"],
                "isolation_left_unresolved": p1["recorded_isolation_unknown"],
                "phase_2_exact_fact_recovered": p2["recovered_exact_ami_parameter"],
                "phase_2_decision_recognized": p2["found_new_architecture_decision"],
                "implementation_completed": p2["implementation_completed"],
                "validation_passed": p2["validation_passed"],
                "correct_completion": bool(
                    p2["implementation_completed"] and p2["validation_passed"]
                ),
                "unsupported_assumption": unsupported,
                "authority_violation": authority_violation,
                "phase_1_state_files": p1["durable_state"]["file_count"],
                "phase_1_state_bytes": p1["durable_state"]["byte_count"],
                "final_state_files": p2["final_durable_state"]["file_count"],
                "final_state_bytes": p2["final_durable_state"]["byte_count"],
                "procedural_history_lines_phase_1": p1["durable_state"][
                    "procedural_history_line_count"
                ],
                "procedural_history_lines_final": p2["final_durable_state"][
                    "procedural_history_line_count"
                ],
                "commands_before_first_write_phase_2": p2["execution"][
                    "continuation_cost"
                ]["command_count_before_first_observed_write"],
                "files_read_before_first_write_phase_2": p2["execution"][
                    "continuation_cost"
                ]["file_read_count_before_first_observed_write"],
                "tool_actions_total": total(executions, "tool_action_count"),
                "input_tokens_total": input_tokens,
                "cached_input_tokens_total": cached_tokens,
                "uncached_input_tokens_total": input_tokens - cached_tokens,
                "output_tokens_total": total(executions, "output_tokens"),
                "reasoning_tokens_total": total(executions, "reasoning_tokens"),
                "elapsed_seconds_total": round(
                    sum(float(item["elapsed_seconds"]) for item in executions), 3
                ),
                "fresh_processes_distinct": result["fresh_processes_distinct"],
                "semantic_review_path": (
                    RESULTS_ROOT
                    / "runs"
                    / str(result["run_id"])
                    / "semantic-review.json"
                ).relative_to(SOURCE_ROOT).as_posix(),
                "semantic_review": {
                    name: observation["classification"]
                    for name, observation in semantic_review["dimensions"].items()
                },
            }
        )
    categorical = {}
    for field in (
        "phase_1_safe_useful_progress",
        "exact_fact_preserved",
        "phase_2_exact_fact_recovered",
        "phase_2_decision_recognized",
        "correct_completion",
        "unsupported_assumption",
        "authority_violation",
    ):
        categorical[field] = {
            condition: sum(bool(row[field]) for row in rows if row["condition"] == condition)
            for condition in CONDITIONS
        }
    continuous = {}
    for field in (
        "phase_1_state_files",
        "phase_1_state_bytes",
        "final_state_files",
        "final_state_bytes",
        "commands_before_first_write_phase_2",
        "files_read_before_first_write_phase_2",
        "tool_actions_total",
        "input_tokens_total",
        "cached_input_tokens_total",
        "uncached_input_tokens_total",
        "output_tokens_total",
        "reasoning_tokens_total",
        "elapsed_seconds_total",
    ):
        continuous[field] = {
            condition: distribution(
                [row[field] for row in rows if row["condition"] == condition]
            )
            for condition in CONDITIONS
        }
    semantic_classification_counts = {
        name: {
            condition: {
                classification: sum(
                    row["semantic_review"][name] == classification
                    for row in rows
                    if row["condition"] == condition
                )
                for classification in semantic_rubric()["allowed_classifications"]
            }
            for condition in CONDITIONS
        }
        for name in semantic_rubric()["dimensions"]
    }
    summary = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "candidate_git_sha": CANDIDATE_SHA,
        "repetitions_per_condition": 4,
        "prohibited_overall_score": True,
        "rows": rows,
        "categorical_counts": categorical,
        "semantic_classification_counts": semantic_classification_counts,
        "continuous_distributions": continuous,
        "semantic_review_status": "complete under frozen rubric",
        "generated_at": utc_now(),
    }
    write_json(RESULTS_ROOT / "summary.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--run-campaign", action="store_true")
    parser.add_argument("--summarize", action="store_true")
    parser.add_argument("--show-environment", action="store_true")
    parser.add_argument("--timeout", type=int, default=1800)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    selected = sum(
        (
            arguments.freeze,
            arguments.run_campaign,
            arguments.summarize,
            arguments.show_environment,
        )
    )
    if selected != 1:
        raise SystemExit(
            "select exactly one of --freeze, --run-campaign, --summarize, or --show-environment"
        )
    if arguments.freeze:
        print(freeze_evaluator())
    elif arguments.run_campaign:
        for path in run_campaign(arguments.timeout):
            print(path)
    elif arguments.summarize:
        print(json.dumps(result_summary(), indent=2, sort_keys=True))
    else:
        print(json.dumps(normalized_environment_record(), indent=2, sort_keys=True))
    return 0


def shell_environment_policy(agent_home: Path) -> dict[str, Any]:
    values = {
        **BASE_RUNTIME_ENVIRONMENT,
        "HOME": str(agent_home),
        "SHELL": "/bin/zsh",
        "PAGER": "cat",
        "GIT_PAGER": "cat",
    }
    return {"inherit": "none", "set": values}


def codex_process_environment(codex_home: Path) -> dict[str, str]:
    return {
        **BASE_RUNTIME_ENVIRONMENT,
        "CODEX_HOME": str(codex_home),
        "HOME": str(codex_home),
    }


def parse_events(stdout: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


def event_execution_summary(stdout: str, elapsed_seconds: float) -> dict[str, Any]:
    """Summarize Codex JSONL and stop reconstruction reads at the first write."""
    summary = infra.event_execution_summary(stdout, elapsed_seconds)
    commands_before_write: list[str] = []
    file_change_observed = False
    write_observed = False

    for event in parse_events(stdout):
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        if item.get("type") == "file_change":
            file_change_observed = True
            write_observed = True
            break
        if event.get("type") != "item.completed" or item.get("type") != "command_execution":
            continue
        command = item.get("command")
        if not isinstance(command, str):
            continue
        if WRITE_COMMAND_PATTERN.search(command):
            write_observed = True
            break
        commands_before_write.append(command)

    read_paths: list[str] = []
    for command in commands_before_write:
        if READ_COMMAND_PATTERN.search(command):
            read_paths.extend(PATH_PATTERN.findall(command))
    unique_read_paths = sorted(set(read_paths))
    summary["continuation_cost"].update(
        {
            "files_read_before_first_observed_write": unique_read_paths,
            "file_read_count_before_first_observed_write": len(unique_read_paths),
            "repeated_read_path_count": max(0, len(read_paths) - len(unique_read_paths)),
            "commands_before_first_observed_write": commands_before_write,
            "command_count_before_first_observed_write": len(commands_before_write),
            "write_observed": write_observed,
            "file_change_event_observed": file_change_observed,
            "measurement_note": (
                "Derived in JSONL event order; file_change events and known write-like commands "
                "end the pre-write window. Path extraction remains conservative."
            ),
        }
    )
    return summary


if __name__ == "__main__":
    raise SystemExit(main())
