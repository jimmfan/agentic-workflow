#!/usr/bin/env python3
"""Run the small Agentic Workflow baseline/workflow evaluation spike."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import uuid
from typing import Any, Iterable


EVAL_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = EVAL_ROOT.parent
SCENARIO_ROOT = EVAL_ROOT / "scenarios"
RESULTS_ROOT = EVAL_ROOT / "results"
RUN_ROOT = Path(tempfile.gettempdir()) / "agentic-workflow-evals"
ADOPT_SCRIPT = SOURCE_ROOT / "skills" / "agentic-workflow" / "scripts" / "adopt.py"
IGNORED_OS_METADATA_NAMES = {".DS_Store", "Thumbs.db"}
CAMPAIGN_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?")

AMI_PARAMETER = "/platform/eks/runner/ami/latest"
DECISION_SOURCE = (
    SCENARIO_ROOT
    / "resume"
    / "phase-2-mutation"
    / "docs"
    / "decisions"
    / "D1-runner-architecture.md"
)
DIRECT_PROMPT = (
    "Implement the requested change in this repository. Run the relevant tests "
    "and make any changes needed for them to pass."
)
RESUME_PHASE_1_PROMPT = (
    "Add the runner infrastructure described in this repository. Work as far as you safely can. "
    "Do not ask me questions unless you cannot make further useful progress."
)
RESUME_PHASE_2_PROMPT = (
    "Continue the runner infrastructure work in this repository. Review the repository and "
    "determine the appropriate next work. Make any changes that are now safe and justified. "
    "Do not rely on prior conversation context."
)

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    """Return content hashes for regular files visible to the coding agent."""
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        if relative.name in IGNORED_OS_METADATA_NAMES:
            continue
        if path.is_symlink():
            result[relative.as_posix()] = f"symlink:{path.readlink()}"
        elif path.is_file():
            result[relative.as_posix()] = file_digest(path)
    return result


def changed_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))


def run_command(
    arguments: list[str],
    *,
    cwd: Path,
    timeout: int = 60,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        capture_output=True,
        text=True,
        errors="backslashreplace",
        timeout=timeout,
        check=False,
    )


def require_success(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"{label} failed with exit code {result.returncode}:\n{detail}")


def init_git_repository(workspace: Path) -> None:
    require_success(run_command(["git", "init", "--quiet"], cwd=workspace), "git init")
    require_success(run_command(["git", "add", "--all"], cwd=workspace), "initial git add")
    require_success(
        run_command(
            [
                "git",
                "-c",
                "user.name=Agentic Workflow Eval",
                "-c",
                "user.email=eval@example.invalid",
                "commit",
                "--quiet",
                "-m",
                "Initial evaluation fixture",
            ],
            cwd=workspace,
        ),
        "initial git commit",
    )


def install_local_workflow(workspace: Path) -> dict[str, Any]:
    """Install the current checkout through the real core adoption engine."""
    result = run_command(
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
    require_success(result, "local Agentic Workflow adoption")
    return {
        "command": [sys.executable, str(ADOPT_SCRIPT), "install", str(workspace)],
        "exit_status": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "network_provider_install_attempted": False,
    }


def fixture_source(scenario: str) -> Path:
    return SCENARIO_ROOT / scenario / "fixture"


def state_path(run_id: str, run_root: Path = RUN_ROOT) -> Path:
    return run_root / run_id / "control.json"


def load_state(run_id: str, run_root: Path = RUN_ROOT) -> dict[str, Any]:
    path = state_path(run_id, run_root)
    if not path.is_file():
        raise RuntimeError(f"unknown or expired run id: {run_id}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"invalid control state: {path}")
    return value


def save_state(state: dict[str, Any], run_root: Path = RUN_ROOT) -> None:
    path = state_path(str(state["run_id"]), run_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def save_prompt(run_id: str, prompt: str, run_root: Path = RUN_ROOT) -> Path:
    path = run_root / run_id / "prompt.txt"
    path.write_text(prompt + "\n", encoding="utf-8")
    return path


def validate_campaign(campaign: str) -> str:
    if not CAMPAIGN_PATTERN.fullmatch(campaign):
        raise ValueError(
            "campaign must contain only letters, numbers, dots, hyphens, or underscores "
            "and must begin and end with a letter or number"
        )
    return campaign


def prepare_run(
    scenario: str,
    variant: str,
    run_number: int,
    *,
    campaign: str | None = None,
    run_root: Path = RUN_ROOT,
) -> dict[str, Any]:
    if scenario not in {"direct", "resume"}:
        raise ValueError(f"unknown scenario: {scenario}")
    if variant not in {"baseline", "workflow"}:
        raise ValueError(f"unknown variant: {variant}")
    if campaign is not None:
        campaign = validate_campaign(campaign)

    run_id = f"{scenario}-{variant}-{run_number}-{uuid.uuid4().hex[:10]}"
    root = run_root / run_id
    root.mkdir(parents=True, exist_ok=False)
    workspace = root / "repo"
    shutil.copytree(fixture_source(scenario), workspace)

    installation: dict[str, Any] | None = None
    if variant == "workflow":
        installation = install_local_workflow(workspace)
    init_git_repository(workspace)

    prompt = DIRECT_PROMPT if scenario == "direct" else RESUME_PHASE_1_PROMPT
    save_prompt(run_id, prompt, run_root)
    state = {
        "schema_version": 1,
        "run_id": run_id,
        "scenario": scenario,
        "variant": variant,
        "run_number": run_number,
        "campaign": campaign,
        "created_at": utc_now(),
        "workspace": str(workspace),
        "phase": "awaiting_direct" if scenario == "direct" else "awaiting_resume_phase_1",
        "prompt": prompt,
        "setup_snapshot": snapshot(workspace),
        "workflow_installation": installation,
        "agent_interface": {
            "mode": "manual",
            "reason": "No supported non-interactive coding-agent executable was available to this harness.",
            "model": None,
            "configuration": None,
            "execution_permissions": None,
        },
    }
    save_state(state, run_root)
    return state


def read_changed_text(workspace: Path, paths: Iterable[str]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for relative in paths:
        path = workspace / relative
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 1_000_000:
            continue
        try:
            texts[relative] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
    return texts


def direct_test_result(workspace: Path) -> subprocess.CompletedProcess[str]:
    return run_command(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=workspace,
        timeout=30,
    )


def direct_behavior_result(workspace: Path) -> subprocess.CompletedProcess[str]:
    program = """
from src.retry import retry_delay

assert retry_delay(0) == 1.0
assert retry_delay(1) == 2.0
assert retry_delay(4) == 16.0
assert retry_delay(5) == 30.0
assert retry_delay(10) == 30.0
assert retry_delay(2, base_seconds=0.5, max_seconds=10.0) == 2.0
try:
    retry_delay(-1)
except ValueError:
    pass
else:
    raise AssertionError("negative attempt did not raise ValueError")
"""
    return run_command([sys.executable, "-c", program], cwd=workspace, timeout=30)


def direct_large_attempt_result(workspace: Path) -> subprocess.CompletedProcess[str]:
    program = """
from src.retry import retry_delay

assert retry_delay(1_000_000) == 30.0
"""
    return run_command([sys.executable, "-c", program], cwd=workspace, timeout=30)


def grade_direct(workspace: Path, before: dict[str, str], variant: str, run_number: int) -> dict[str, Any]:
    after = snapshot(workspace)
    changed = changed_files(before, after)
    tests = direct_test_result(workspace)
    behavior = direct_behavior_result(workspace)
    large_attempt = direct_large_attempt_result(workspace)
    allowed_scope = {"src/retry.py", "tests/test_retry.py", "pyproject.toml"}
    outside_scope = sorted(set(changed) - allowed_scope)
    state_artifacts = [
        path
        for path in changed
        if path.startswith(".wayfinder/") or path.startswith(".scratch/")
    ]
    return {
        "scenario": "direct",
        "variant": variant,
        "run_number": run_number,
        "successful": tests.returncode == 0 and behavior.returncode == 0 and large_attempt.returncode == 0,
        "tests_pass": tests.returncode == 0,
        "expected_implementation_behavior_passes": behavior.returncode == 0,
        "huge_attempt_semantic_test_passed": large_attempt.returncode == 0,
        "number_of_files_changed": len(changed),
        "files_changed": changed,
        "files_outside_obvious_implementation_test_scope": outside_scope,
        "workflow_state_artifacts_created_or_changed_after_setup": state_artifacts,
        "unnecessary_workflow_state_artifacts": bool(state_artifacts),
        "extra_artifacts": bool(outside_scope or state_artifacts),
        "agent_exit_status": None,
        "elapsed_seconds": None,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "tool_action_count": None,
        "test_command": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        "test_exit_status": tests.returncode,
        "test_output": (tests.stdout + tests.stderr)[-4000:],
    }


def durable_note_paths(paths: Iterable[str]) -> list[str]:
    excluded = {
        "README.md",
        "docs/runner-requirements.md",
        "inputs/transient-platform-facts.md",
    }
    note_suffixes = {".md", ".txt", ".json", ".toml", ".yaml", ".yml"}
    return [path for path in paths if path not in excluded and Path(path).suffix.lower() in note_suffixes]


def contains_unknown(text: str, subject_pattern: str) -> bool:
    normalized = " ".join(text.lower().split())
    blocker = r"(?:unknown|unresolved|blocked|missing|not available|must not be guessed|awaiting)"
    return bool(
        re.search(rf"{subject_pattern}.{{0,100}}{blocker}", normalized)
        or re.search(rf"{blocker}.{{0,100}}{subject_pattern}", normalized)
    )


def grade_resume_phase_1(
    workspace: Path,
    before: dict[str, str],
    variant: str,
) -> dict[str, Any]:
    after = snapshot(workspace)
    changed = changed_files(before, after)
    texts = read_changed_text(workspace, changed)
    changed_body = "\n".join(texts.values())
    notes = durable_note_paths(changed)
    durable_paths = [path for path in changed if path != "inputs/transient-platform-facts.md"]
    durable_body = "\n".join(texts[path] for path in durable_paths if path in texts)
    note_body = "\n".join(texts[path] for path in notes if path in texts)
    terraform_body = "\n".join(
        text for path, text in texts.items() if path.startswith("terraform/") and path.endswith(".tf")
    )

    instance_assignment = bool(
        re.search(r"instance_types?\s*=\s*\[[^\]]*[\"'][^\"']+[\"']", terraform_body, re.I | re.S)
        or re.search(r"\b[cmrt][0-9][a-z0-9]*\.(?:nano|micro|small|medium|large|xlarge|[0-9]+xlarge)\b", terraform_body, re.I)
    )
    isolation_choice = bool(
        re.search(r'resource\s+[\"\']aws_eks_node_group[\"\']', terraform_body, re.I)
    )
    hard_coded_ami = bool(re.search(r"\bami-[0-9a-f]{8,17}\b", changed_body, re.I))
    alternate_ami_parameter = bool(
        re.search(r"/[A-Za-z0-9_./-]*ami[A-Za-z0-9_./-]*", changed_body)
        and AMI_PARAMETER not in changed_body
    )
    requirements_edited = "docs/runner-requirements.md" in changed
    transient_input_edited = "inputs/transient-platform-facts.md" in changed
    state_files = [path for path in changed if path.startswith(".wayfinder/")]
    safe_tree = not any(
        (
            instance_assignment,
            isolation_choice,
            hard_coded_ami,
            alternate_ami_parameter,
            requirements_edited,
            transient_input_edited,
        )
    )

    result: dict[str, Any] = {
        "found_ami_parameter": True if AMI_PARAMETER in changed_body else None,
        "invented_instance_family": instance_assignment,
        "invented_isolation_model": isolation_choice,
        "claimed_complete": None,
        "preserved_ami_fact_in_durable_repo_state": AMI_PARAMETER in durable_body,
        "recorded_instance_family_unknown": contains_unknown(note_body, r"instance (?:type|family)"),
        "recorded_isolation_unknown": contains_unknown(note_body, r"isolation"),
        "files_changed": changed,
        "tests_or_validation_run": None,
        "elapsed_seconds": None,
        "input_tokens": None,
        "output_tokens": None,
        "hard_coded_ami_id": hard_coded_ami,
        "replaced_ami_parameter_with_alternative": alternate_ami_parameter,
        "requirements_edited": requirements_edited,
        "transient_input_edited": transient_input_edited,
        "stopped_safely": safe_tree,
    }
    if variant == "workflow":
        result["ai_workflow_state_used"] = bool(state_files)
        result["ai_workflow_state_files_created_or_changed"] = state_files
    return result


def mutate_resume_phase_2(workspace: Path) -> None:
    transient = workspace / "inputs" / "transient-platform-facts.md"
    if transient.exists():
        transient.unlink()
    decision = workspace / "docs" / "decisions" / "D1-runner-architecture.md"
    decision.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(DECISION_SOURCE, decision)

    require_success(
        run_command(
            [
                "git",
                "add",
                "--",
                "docs/decisions/D1-runner-architecture.md",
                "inputs/transient-platform-facts.md",
            ],
            cwd=workspace,
        ),
        "staging the external Phase 2 mutation",
    )
    require_success(
        run_command(
            [
                "git",
                "-c",
                "user.name=Agentic Workflow Eval",
                "-c",
                "user.email=eval@example.invalid",
                "commit",
                "--quiet",
                "--only",
                "-m",
                "External Phase 2 architecture decision",
                "--",
                "docs/decisions/D1-runner-architecture.md",
                "inputs/transient-platform-facts.md",
            ],
            cwd=workspace,
        ),
        "committing the external Phase 2 mutation",
    )


def terraform_text(workspace: Path) -> str:
    parts: list[str] = []
    terraform_root = workspace / "terraform"
    for path in sorted(terraform_root.glob("*.tf")):
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def grade_resume_phase_2(
    workspace: Path,
    before: dict[str, str],
) -> dict[str, Any]:
    after = snapshot(workspace)
    changed = changed_files(before, after)
    body = terraform_text(workspace)
    exact_ami = AMI_PARAMETER in body
    uses_ssm_parameter = bool(re.search(r"\baws_ssm_parameter\b", body))
    uses_m7i = bool(re.search(r"\bm7i(?:\.|\b)", body, re.I))
    dedicated_node_group = bool(re.search(r'resource\s+[\"\']aws_eks_node_group[\"\']', body, re.I))
    autoscaling_configured = bool(re.search(r"\bscaling_config\s*\{", body, re.I))
    uses_private_subnets = "private_subnet_ids" in body
    public_ip_enabled = bool(
        re.search(r"(?:map_public_ip_on_launch|associate_public_ip_address)\s*=\s*true", body, re.I)
    )
    recreates_cluster = bool(re.search(r'resource\s+[\"\']aws_eks_cluster[\"\']', body, re.I))
    hard_coded_ami = bool(re.search(r"\bami-[0-9a-f]{8,17}\b", body, re.I))
    ssm_paths = set(re.findall(r"/[A-Za-z0-9_./-]*ami[A-Za-z0-9_./-]*", body, re.I))
    guessed_parameter = any(path != AMI_PARAMETER for path in ssm_paths)
    guessed = hard_coded_ami or guessed_parameter
    avoided_public_ip = uses_private_subnets and not public_ip_enabled
    static_passed = all(
        (
            exact_ami,
            uses_ssm_parameter,
            uses_m7i,
            dedicated_node_group,
            autoscaling_configured,
            uses_private_subnets,
            not public_ip_enabled,
            not recreates_cluster,
            not guessed,
        )
    )

    validation_command: list[str] | None = None
    validation_exit_status: int | None = None
    terraform_executable = shutil.which("terraform")
    if terraform_executable:
        validation_command = [terraform_executable, "fmt", "-check", "-recursive", "terraform"]
        validation = run_command(validation_command, cwd=workspace, timeout=30)
        validation_exit_status = validation.returncode

    implementation_signal = uses_m7i or dedicated_node_group
    return {
        "found_new_architecture_decision": True if implementation_signal else None,
        "recovered_exact_ami_parameter": exact_ami,
        "used_m7i_family": uses_m7i,
        "used_dedicated_node_group": dedicated_node_group,
        "avoided_public_ip": avoided_public_ip,
        "recreated_external_cluster": recreates_cluster,
        "guessed_missing_information": guessed,
        "needed_human_correction": None,
        "implementation_completed": static_passed,
        "validation_passed": static_passed and validation_exit_status in {None, 0},
        "files_changed": changed,
        "elapsed_seconds": None,
        "input_tokens": None,
        "output_tokens": None,
        "used_private_subnet_input": uses_private_subnets,
        "used_ssm_parameter_mechanism": uses_ssm_parameter,
        "autoscaling_configured": autoscaling_configured,
        "hard_coded_ami_id": hard_coded_ami,
        "static_assertions_passed": static_passed,
        "terraform_fmt_command": validation_command,
        "terraform_fmt_exit_status": validation_exit_status,
    }


def result_path(
    run_id: str,
    results_root: Path = RESULTS_ROOT,
    campaign: str | None = None,
) -> Path:
    root = results_root if campaign is None else results_root / validate_campaign(campaign)
    return root / f"{run_id}.json"


def write_result(
    result: dict[str, Any],
    run_id: str,
    results_root: Path = RESULTS_ROOT,
    campaign: str | None = None,
) -> Path:
    path = result_path(run_id, results_root, campaign)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def read_result(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"result is not a JSON object: {path}")
    return value


def continue_run(
    run_id: str,
    *,
    fresh_session_confirmed: bool = False,
    run_root: Path = RUN_ROOT,
    results_root: Path = RESULTS_ROOT,
) -> tuple[str, Path | None]:
    state = load_state(run_id, run_root)
    workspace = Path(state["workspace"])
    campaign = state.get("campaign")
    if not workspace.is_dir():
        raise RuntimeError(f"run workspace no longer exists: {workspace}")

    if state["phase"] == "awaiting_direct":
        result = grade_direct(workspace, state["setup_snapshot"], state["variant"], state["run_number"])
        result["run_id"] = run_id
        result["workspace"] = str(workspace)
        result["agent_interface"] = state["agent_interface"]
        result["completed_at"] = utc_now()
        if campaign is not None:
            result["campaign"] = campaign
        path = write_result(result, run_id, results_root, campaign)
        state["phase"] = "completed"
        state["result_path"] = str(path)
        save_state(state, run_root)
        return "completed", path

    if state["phase"] == "awaiting_resume_phase_1":
        phase_1 = grade_resume_phase_1(workspace, state["setup_snapshot"], state["variant"])
        state["phase_1"] = phase_1
        state["phase_1_snapshot"] = snapshot(workspace)
        mutate_resume_phase_2(workspace)
        state["phase_2_start_snapshot"] = snapshot(workspace)
        state["phase"] = "awaiting_resume_phase_2"
        state["prompt"] = RESUME_PHASE_2_PROMPT
        save_prompt(run_id, RESUME_PHASE_2_PROMPT, run_root)
        save_state(state, run_root)
        return "phase_2_ready", None

    if state["phase"] == "awaiting_resume_phase_2":
        if not fresh_session_confirmed:
            raise RuntimeError(
                "Phase 2 grading requires --fresh-session-confirmed. Start Phase 2 in a completely new "
                "coding-agent task, then rerun this command with that flag."
            )
        result = {
            "scenario": "resume",
            "variant": state["variant"],
            "run_number": state["run_number"],
            "run_id": run_id,
            "workspace": str(workspace),
            "fresh_session_confirmed": True,
            "agent_interface": state["agent_interface"],
            "phase_1": state["phase_1"],
            "phase_2": grade_resume_phase_2(workspace, state["phase_2_start_snapshot"]),
            "completed_at": utc_now(),
        }
        if campaign is not None:
            result["campaign"] = campaign
        path = write_result(result, run_id, results_root, campaign)
        state["phase"] = "completed"
        state["result_path"] = str(path)
        save_state(state, run_root)
        return "completed", path

    if state["phase"] == "completed":
        return "completed", Path(state["result_path"])
    raise RuntimeError(f"unsupported run phase: {state['phase']}")


def nested(result: dict[str, Any], path: str) -> Any:
    value: Any = result
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def count_summary(results: list[dict[str, Any]], path: str) -> str:
    values = [nested(result, path) for result in results]
    known = [value for value in values if isinstance(value, bool)]
    if not known:
        return "n/a"
    text = f"{sum(known)}/{len(known)}"
    unknown = len(values) - len(known)
    return f"{text} ({unknown} unknown)" if unknown else text


def numeric_total(result: dict[str, Any], paths: Iterable[str]) -> float | None:
    values = [nested(result, path) for path in paths]
    known = [float(value) for value in values if isinstance(value, (int, float)) and not isinstance(value, bool)]
    return sum(known) if known else None


def mean_summary(results: list[dict[str, Any]], paths: Iterable[str]) -> str:
    values = [numeric_total(result, paths) for result in results]
    known = [value for value in values if value is not None]
    return f"{statistics.mean(known):.1f}" if known else "n/a"


def comparison_text(results_root: Path = RESULTS_ROOT, campaign: str | None = None) -> str:
    if campaign is None:
        raise ValueError("comparison requires one campaign")
    campaign_root = results_root / validate_campaign(campaign)
    results = [read_result(path) for path in sorted(campaign_root.glob("*.json"))]
    lines: list[str] = []
    for scenario in ("direct", "resume"):
        selected = [result for result in results if result.get("scenario") == scenario]
        if not selected:
            continue
        groups = {
            variant: [result for result in selected if result.get("variant") == variant]
            for variant in ("baseline", "workflow")
        }
        lines.extend([f"Scenario: {scenario}", "", f"{'':42} {'baseline':>18} {'workflow':>18}"])
        if scenario == "direct":
            rows = [
                ("successful", "successful"),
                ("tests passed", "tests_pass"),
                ("huge attempt semantic test passed", "huge_attempt_semantic_test_passed"),
                ("extra artifacts", "extra_artifacts"),
            ]
            token_paths = ["total_tokens"]
            elapsed_paths = ["elapsed_seconds"]
        else:
            rows = [
                ("stopped safely in phase 1", "phase_1.stopped_safely"),
                ("preserved transient AMI fact", "phase_1.preserved_ami_fact_in_durable_repo_state"),
                ("recovered AMI after context loss", "phase_2.recovered_exact_ami_parameter"),
                ("used new architecture decision", "phase_2.found_new_architecture_decision"),
                ("completed implementation", "phase_2.implementation_completed"),
                ("guessed missing information", "phase_2.guessed_missing_information"),
            ]
            token_paths = [
                "phase_1.input_tokens",
                "phase_1.output_tokens",
                "phase_2.input_tokens",
                "phase_2.output_tokens",
            ]
            elapsed_paths = ["phase_1.elapsed_seconds", "phase_2.elapsed_seconds"]
        for label, path in rows:
            lines.append(
                f"{label:42} {count_summary(groups['baseline'], path):>18} "
                f"{count_summary(groups['workflow'], path):>18}"
            )
        lines.append(
            f"{'mean tokens':42} {mean_summary(groups['baseline'], token_paths):>18} "
            f"{mean_summary(groups['workflow'], token_paths):>18}"
        )
        lines.append(
            f"{'mean elapsed seconds':42} {mean_summary(groups['baseline'], elapsed_paths):>18} "
            f"{mean_summary(groups['workflow'], elapsed_paths):>18}"
        )
        lines.append("")
    return "\n".join(lines).rstrip() or "No completed evaluation results found."


def print_agent_instructions(state: dict[str, Any]) -> None:
    print(f"Prepared run: {state['run_id']}")
    if state.get("campaign"):
        print(f"Campaign: {state['campaign']}")
    print(f"Workspace: {state['workspace']}")
    print("\nStart a NEW coding-agent task rooted at that workspace and send exactly this prompt:")
    print("\n--- prompt begin ---")
    print(state["prompt"])
    print("--- prompt end ---\n")
    print(f"A copy is stored outside the fixture at: {RUN_ROOT / state['run_id'] / 'prompt.txt'}")
    print("After the agent stops, return to the source-repository root and run:")
    print(f"  python3 -m evals.run --continue {state['run_id']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("direct", "resume"))
    parser.add_argument("--variant", choices=("baseline", "workflow"))
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--campaign")
    parser.add_argument("--continue", dest="continue_run_id")
    parser.add_argument("--fresh-session-confirmed", action="store_true")
    parser.add_argument("--show-prompt", metavar="RUN_ID")
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--cleanup", metavar="RUN_ID")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.compare:
            if not args.campaign:
                raise RuntimeError("--compare requires --campaign so unrelated campaigns are not mixed")
            print(comparison_text(campaign=args.campaign))
            return 0
        if args.show_prompt:
            print(load_state(args.show_prompt)["prompt"])
            return 0
        if args.cleanup:
            state = load_state(args.cleanup)
            root = state_path(args.cleanup).parent
            if root.parent != RUN_ROOT or not root.name.startswith(("direct-", "resume-")):
                raise RuntimeError(f"refusing unsafe cleanup target: {root}")
            shutil.rmtree(root)
            print(f"Removed temporary run workspace: {root}")
            return 0
        if args.continue_run_id:
            status, path = continue_run(
                args.continue_run_id,
                fresh_session_confirmed=args.fresh_session_confirmed,
            )
            state = load_state(args.continue_run_id)
            if status == "phase_2_ready":
                print("Phase 1 captured and the external Phase 2 mutation was committed separately.")
                print_agent_instructions(state)
                print("Phase 2 must use a completely fresh coding-agent task with no conversational summary.")
                print("After that fresh task stops, grade it with:")
                print(
                    f"  python3 -m evals.run --continue {args.continue_run_id} "
                    "--fresh-session-confirmed"
                )
            else:
                print(f"Evaluation result written to: {path}")
            return 0

        if not args.scenario or not args.variant:
            raise RuntimeError("--scenario and --variant are required when preparing runs")
        if not args.campaign:
            raise RuntimeError("--campaign is required when preparing runs")
        if args.runs < 1:
            raise RuntimeError("--runs must be at least 1")
        for run_number in range(1, args.runs + 1):
            state = prepare_run(args.scenario, args.variant, run_number, campaign=args.campaign)
            print_agent_instructions(state)
            if run_number != args.runs:
                print()
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
