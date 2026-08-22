#!/usr/bin/env python3
"""Two-condition ARC Wayfinder branching-state complexity smoke harness."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
from typing import Any, Iterable


EVAL_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = EVAL_ROOT.parent
CAMPAIGN_ID = "arc-wayfinder-state-complexity-v1"
CAMPAIGN_PATH = EVAL_ROOT / "campaigns" / f"{CAMPAIGN_ID}.json"
SCENARIO_ROOT = EVAL_ROOT / "scenarios" / CAMPAIGN_ID
FIXTURE_ROOT = SCENARIO_ROOT / "fixture"
PHASE_2_MUTATION_ROOT = SCENARIO_ROOT / "phase-2-mutation"
PHASE_3_MUTATION_ROOT = SCENARIO_ROOT / "phase-3-mutation"
PHASE_5_MUTATION_ROOT = SCENARIO_ROOT / "phase-5-mutation"
RESULTS_ROOT = EVAL_ROOT / "results" / CAMPAIGN_ID
ARTIFACTS_ROOT = EVAL_ROOT / "artifacts" / CAMPAIGN_ID
FREEZE_PATH = RESULTS_ROOT / "frozen-evaluator.json"
ISOLATION_AUDIT_PATH = RESULTS_ROOT / "context-isolation-audit.json"
RUN_ROOT = Path(tempfile.gettempdir()) / "agentic-workflow-arc-wayfinder-state-complexity-v1"
ADOPT_SCRIPT = SOURCE_ROOT / "skills" / "agentic-workflow" / "scripts" / "adopt.py"
WAYFINDER_SOURCE = SOURCE_ROOT / ".agents" / "skills" / "wayfinder"
AMI_PARAMETER = "/platform/arc/runner-ami"
LEGACY_SECURITY_GROUP = "sg-0abc1234def567890"
IGNORED_NAMES = {".DS_Store", "Thumbs.db"}
TEXT_SUFFIXES = {".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".tf", ".py"}
EVIDENCE_QUALITY = {
    "clean",
    "known_limitation",
    "potentially_confounded",
    "confirmed_contaminated",
}
CONDITIONS = ("A", "B")
WORKFLOW_CONDITIONS = {"B"}
OBSERVABILITY_DESTINATION = "arn:aws:sns:us-east-1:123456789012:arc-runner-alerts"
FRAMEWORK_VERSION_PATH = SOURCE_ROOT / "skills" / "agentic-workflow" / "VERSION"
SOURCE_CODEX_HOME = (Path.home() / ".codex").resolve()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_command(
    arguments: list[str],
    *,
    cwd: Path,
    timeout: int = 120,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        env=env,
        input=input_text,
        capture_output=True,
        text=True,
        errors="backslashreplace",
        timeout=timeout,
        check=False,
    )


def require_success(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"{label} failed with exit code {result.returncode}:\n{detail[-6000:]}")


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts or relative.name in IGNORED_NAMES:
            continue
        if path.is_symlink():
            result[relative.as_posix()] = f"symlink:{path.readlink()}"
        elif path.is_file():
            result[relative.as_posix()] = file_digest(path)
    return result


def changed_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))


def read_texts(root: Path, paths: Iterable[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in paths:
        path = root / relative
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 1_000_000:
            continue
        try:
            result[relative] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            pass
    return result


def snapshot_archive(workspace: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(destination, "w:gz") as archive:
        for path in sorted(workspace.rglob("*")):
            relative = path.relative_to(workspace)
            if ".git" in relative.parts or relative.name in IGNORED_NAMES or not path.is_file():
                continue
            archive.add(path, arcname=relative.as_posix(), recursive=False)


def git(workspace: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return run_command(["git", *arguments], cwd=workspace)


def git_head(workspace: Path) -> str:
    result = git(workspace, "rev-parse", "HEAD")
    require_success(result, "git rev-parse HEAD")
    return result.stdout.strip()


def init_git_repository(workspace: Path) -> str:
    require_success(git(workspace, "init", "--quiet"), "git init")
    require_success(git(workspace, "add", "--all"), "initial git add")
    require_success(
        git(
            workspace,
            "-c",
            "user.name=Agentic Workflow Eval",
            "-c",
            "user.email=eval@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "Initial ARC evaluation fixture",
        ),
        "initial git commit",
    )
    return git_head(workspace)


def commit_only(workspace: Path, message: str, paths: list[str]) -> str:
    require_success(git(workspace, "add", "-A", "--", *paths), f"stage {message}")
    require_success(
        git(
            workspace,
            "-c",
            "user.name=Agentic Workflow Eval",
            "-c",
            "user.email=eval@example.invalid",
            "commit",
            "--quiet",
            "--only",
            "-m",
            message,
            "--",
            *paths,
        ),
        f"commit {message}",
    )
    return git_head(workspace)


def campaign() -> dict[str, Any]:
    value = read_json(CAMPAIGN_PATH)
    if value.get("campaign_id") != CAMPAIGN_ID:
        raise RuntimeError("campaign manifest id does not match the harness")
    return value


def critical_paths() -> list[Path]:
    paths = [Path(__file__).resolve(), CAMPAIGN_PATH]
    paths.extend(path for path in sorted(SCENARIO_ROOT.rglob("*")) if path.is_file())
    return paths


def critical_digests() -> dict[str, str]:
    return {
        path.relative_to(SOURCE_ROOT).as_posix(): file_digest(path)
        for path in critical_paths()
    }


def freeze_evaluator() -> Path:
    if FREEZE_PATH.exists():
        raise RuntimeError(
            f"the evaluator is already frozen at {FREEZE_PATH}; create a new campaign id rather than replacing it"
        )
    head = run_command(["git", "rev-parse", "HEAD"], cwd=SOURCE_ROOT)
    write_json(
        FREEZE_PATH,
        {
            "schema_version": 1,
            "campaign_id": CAMPAIGN_ID,
            "frozen_at": utc_now(),
            "source_git_sha": head.stdout.strip() if head.returncode == 0 else None,
            "critical_sha256": critical_digests(),
            "rule": "Any critical-file mismatch invalidates execution. Do not refreeze after live evidence; create a new campaign.",
        },
    )
    return FREEZE_PATH


def verify_frozen_evaluator() -> dict[str, Any]:
    if not FREEZE_PATH.is_file():
        raise RuntimeError("evaluator is not frozen; run deterministic verification, then use --freeze")
    frozen = read_json(FREEZE_PATH)
    expected = frozen.get("critical_sha256")
    actual = critical_digests()
    if expected != actual:
        expected_dict = expected if isinstance(expected, dict) else {}
        mismatches = sorted(
            path for path in set(expected_dict) | set(actual) if expected_dict.get(path) != actual.get(path)
        )
        raise RuntimeError(f"frozen evaluator mismatch: {', '.join(mismatches)}")
    return frozen


def codex_home_path() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser().resolve() if configured else (Path.home() / ".codex").resolve()


def context_inventory(codex_home: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    unexpected: list[str] = []
    if codex_home.is_dir():
        for path in sorted(codex_home.rglob("*")):
            relative = path.relative_to(codex_home).as_posix()
            if path.is_symlink():
                entries.append({"path": relative, "kind": "symlink"})
                unexpected.append(relative)
            elif path.is_file():
                entries.append({"path": relative, "kind": "file", "size": path.stat().st_size})
                if relative != "auth.json":
                    unexpected.append(relative)
    return {
        "codex_home": str(codex_home),
        "files": entries,
        "unexpected_files": unexpected,
        "contains_only_auth_material": bool(entries) and not unexpected,
        "auth_contents_or_digest_recorded": False,
        "config_ignored_by_cli_flag": True,
        "rules_ignored_by_cli_flag": True,
    }


def verify_context_isolation_audit() -> dict[str, Any]:
    if not ISOLATION_AUDIT_PATH.is_file():
        raise RuntimeError(
            "automatic execution is disabled until --audit-auto-isolation produces a passing audit"
        )
    audit = read_json(ISOLATION_AUDIT_PATH)
    if audit.get("status") != "passed":
        raise RuntimeError("automatic execution is disabled because the context-isolation audit did not pass")
    if audit.get("frozen_evaluator_sha256") != file_digest(FREEZE_PATH):
        raise RuntimeError(
            "automatic execution is disabled because the frozen evaluator changed after the isolation audit"
        )
    return audit


def install_workflow(workspace: Path) -> dict[str, Any]:
    adoption = run_command(
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
    require_success(adoption, "local Agentic Workflow adoption")
    if not WAYFINDER_SOURCE.is_dir():
        raise RuntimeError(f"pinned Wayfinder source is unavailable: {WAYFINDER_SOURCE}")
    destination = workspace / ".agents" / "skills" / "wayfinder"
    if destination.exists():
        raise RuntimeError(f"unexpected Wayfinder collision: {destination}")
    shutil.copytree(WAYFINDER_SOURCE, destination)
    skill_text = (destination / "SKILL.md").read_text(encoding="utf-8")
    if "github-pinned: v1.2.3" not in skill_text:
        raise RuntimeError("the local Wayfinder provider is not the campaign's reviewed v1.2.3 pin")
    installed_paths = [
        path
        for root in (workspace / ".agent-workflow", workspace / ".agents", workspace / "AGENTS.md", workspace / "CLAUDE.md")
        for path in ([root] if root.is_file() else sorted(root.rglob("*")) if root.is_dir() else [])
        if path.is_file()
    ]
    installed_digests = {
        path.relative_to(workspace).as_posix(): file_digest(path) for path in installed_paths
    }
    return {
        "core_adoption_exit_status": adoption.returncode,
        "framework_version": FRAMEWORK_VERSION_PATH.read_text(encoding="utf-8").strip(),
        "source_git_sha": git_source_head(),
        "installed_artifact_sha256": digest_bytes(
            json.dumps(installed_digests, sort_keys=True).encode()
        ),
        "installed_file_sha256": installed_digests,
        "provider": "mattpocock/skills wayfinder",
        "provider_pin": "v1.2.3",
        "provider_skill_sha256": file_digest(destination / "SKILL.md"),
        "network_provider_install_attempted": False,
    }


def git_source_head() -> str | None:
    result = run_command(["git", "rev-parse", "HEAD"], cwd=SOURCE_ROOT)
    return result.stdout.strip() if result.returncode == 0 else None


def state_path(run_id: str, run_root: Path = RUN_ROOT) -> Path:
    return run_root / run_id / "control.json"


def load_state(run_id: str, run_root: Path = RUN_ROOT) -> dict[str, Any]:
    path = state_path(run_id, run_root)
    if not path.is_file():
        raise RuntimeError(f"unknown or expired run id: {run_id}")
    return read_json(path)


def save_state(state: dict[str, Any], run_root: Path = RUN_ROOT) -> None:
    write_json(state_path(str(state["run_id"]), run_root), state)


def result_run_root(run_id: str, results_root: Path = RESULTS_ROOT) -> Path:
    return results_root / "runs" / run_id


def prompt_for(condition: str, phase: int) -> str:
    prompts = campaign()["prompts"]
    return str(prompts[condition][str(phase)])


def save_prompt(state: dict[str, Any], run_root: Path = RUN_ROOT) -> Path:
    phase = int(state["phase"])
    path = run_root / str(state["run_id"]) / f"phase-{phase}-prompt.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(prompt_for(str(state["condition"]), phase) + "\n", encoding="utf-8")
    return path


def prepare_run(
    condition: str,
    *,
    run_number: int = 1,
    run_root: Path = RUN_ROOT,
    require_frozen: bool = True,
) -> dict[str, Any]:
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition: {condition}")
    frozen = verify_frozen_evaluator() if require_frozen else {"critical_sha256": critical_digests()}
    run_id = f"arc-state-{condition.lower()}-{run_number}-{uuid.uuid4().hex[:10]}"
    root = run_root / run_id
    workspace = root / "repo"
    root.mkdir(parents=True, exist_ok=False)
    shutil.copytree(FIXTURE_ROOT, workspace)
    installation = install_workflow(workspace) if condition in WORKFLOW_CONDITIONS else None
    setup_commit = init_git_repository(workspace)
    state: dict[str, Any] = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "run_id": run_id,
        "run_number": run_number,
        "condition": condition,
        "condition_name": campaign()["conditions"][condition]["name"],
        "workspace": str(workspace),
        "created_at": utc_now(),
        "phase": 1,
        "status": "awaiting_agent",
        "setup_commit": setup_commit,
        "setup_snapshot": snapshot(workspace),
        "phase_start_snapshot": snapshot(workspace),
        "workflow_installation": installation,
        "source_git_sha": read_json(FREEZE_PATH).get("source_git_sha") if require_frozen else None,
        "frozen_evaluator_sha256": digest_bytes(json.dumps(frozen, sort_keys=True).encode()),
        "executions": [],
        "phase_evidence_paths": [],
        "mutation_commits": {},
    }
    save_state(state, run_root)
    save_prompt(state, run_root)
    return state


def prepare_pair(
    *, run_root: Path = RUN_ROOT, require_frozen: bool = True
) -> dict[str, dict[str, Any]]:
    states = {
        condition: prepare_run(condition, run_root=run_root, require_frozen=require_frozen)
        for condition in CONDITIONS
    }
    return states


def evidence_lines(
    workspace: Path,
    paths: Iterable[str],
    subjects: Iterable[str],
) -> list[dict[str, Any]]:
    patterns = [re.compile(pattern, re.I) for pattern in subjects]
    evidence: list[dict[str, Any]] = []
    for relative, text in read_texts(workspace, sorted(set(paths))).items():
        for number, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in patterns):
                evidence.append(
                    {"path": relative, "line": number, "snippet": line.strip()[:500]}
                )
    return evidence


def semantic_evidence_packet(
    workspace: Path,
    paths: Iterable[str],
    *,
    subjects: Iterable[str],
    question: str,
) -> dict[str, Any]:
    return {
        "semantic_question": question,
        "evidence": evidence_lines(workspace, paths, subjects),
        "deterministic_structured_value": None,
        "manual_review_required": True,
        "method": "Exact path/line/snippet extraction only; no prose keyword-window classification.",
    }


def terraform_text(workspace: Path) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((workspace / "terraform").glob("*.tf"))
    )


def terraform_code(workspace: Path) -> str:
    lines: list[str] = []
    for line in terraform_text(workspace).splitlines():
        lines.append(re.sub(r"#.*$", "", line))
    return "\n".join(lines)


def changed_text(workspace: Path, before: dict[str, str]) -> tuple[list[str], dict[str, str]]:
    after = snapshot(workspace)
    changed = changed_files(before, after)
    return changed, read_texts(workspace, changed)


def durable_paths(paths: Iterable[str]) -> list[str]:
    return [
        path
        for path in paths
        if Path(path).suffix.lower() in TEXT_SUFFIXES
        and not path.startswith("terraform/")
        and path != "docs/platform-facts.md"
        and not path.startswith(".agent-workflow/")
        and not path.startswith(".agents/")
        and path not in {"AGENTS.md", "CLAUDE.md"}
    ]


def current_durable_text(workspace: Path, paths: Iterable[str]) -> str:
    texts = read_texts(workspace, sorted(set(paths)))
    return "\n".join(texts.values())


def wayfinder_markdown_paths(workspace: Path) -> list[Path]:
    root = workspace / ".wayfinder"
    if not root.is_dir():
        return []
    return [
        path
        for effort in sorted(root.iterdir())
        if effort.is_dir() and effort.name not in {"archive", "records"}
        for path in sorted(effort.rglob("*.md"))
    ]


def structured_wayfinder_fields(workspace: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in wayfinder_markdown_paths(workspace):
        fields: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\s*-\s*(Status|Blocked by|Related|Resolves)\s*:\s*(.*?)\s*$", line, re.I)
            if match:
                fields[match.group(1).lower().replace(" ", "_")] = match.group(2)
        if fields:
            records.append({"path": path.relative_to(workspace).as_posix(), "fields": fields})
    return records


def state_evidence_packets(workspace: Path, paths: Iterable[str]) -> dict[str, Any]:
    return {
        "m6i_stale": semantic_evidence_packet(
            workspace,
            paths,
            subjects=(r"\bm6i\b",),
            question="Is the older m6i recommendation represented as stale rather than current truth?",
        ),
        "w1_compute_state": semantic_evidence_packet(
            workspace,
            paths,
            subjects=(r"instance (?:family|type)", r"\bm[67]i", r"karpenter", r"managed node", r"dedicated", r"shared"),
            question="Which W1 compute choices are current, unresolved, or superseded?",
        ),
        "w2_identity_state": semantic_evidence_packet(
            workspace,
            paths,
            subjects=(r"ssm", r"runner ami", r"permissions boundary", r"\biam\b"),
            question="Is the settled W2 IAM/SSM slice preserved and actionable?",
        ),
        "w3_legacy_state": semantic_evidence_packet(
            workspace,
            paths,
            subjects=(r"legacy", re.escape(LEGACY_SECURITY_GROUP)),
            question="Is W3 still blocked without blocking independent fixture-owned resources?",
        ),
        "w4_observability_state": semantic_evidence_packet(
            workspace,
            paths,
            subjects=(r"observability", r"destination", r"sns", r"cloudwatch", re.escape(OBSERVABILITY_DESTINATION)),
            question="Is W4 blocked or actionable under the latest supplied destination truth?",
        ),
        "structured_wayfinder_fields": structured_wayfinder_fields(workspace),
    }


def durable_state_metrics(workspace: Path, paths: Iterable[str], changed: Iterable[str] = ()) -> dict[str, Any]:
    current = [path for path in sorted(set(paths)) if (workspace / path).is_file()]
    texts = read_texts(workspace, current)
    changed_set = set(changed)
    return {
        "file_count": len(current),
        "line_count": sum(len(text.splitlines()) for text in texts.values()),
        "paths": current,
        "files_reconciled_this_phase": sorted(path for path in current if path in changed_set),
        "files_reconciled_count": sum(path in changed_set for path in current),
    }


def exact_fact_evidence(workspace: Path, paths: Iterable[str] | None = None) -> list[dict[str, Any]]:
    candidates = list(paths) if paths is not None else list(snapshot(workspace))
    return evidence_lines(workspace, candidates, (re.escape(AMI_PARAMETER),))


def wayfinder_blocker_evidence(workspace: Path) -> dict[str, Any]:
    paths = [path.relative_to(workspace).as_posix() for path in wayfinder_markdown_paths(workspace)]
    blocker_lines = evidence_lines(workspace, paths, (r"^\s*-?\s*Blocked by\s*:",))
    return {
        "all_blocked_by_lines": blocker_lines,
        "structured_records": structured_wayfinder_fields(workspace),
        "manual_review_required": False,
        "method": "Wayfinder Status/Blocked by/Related/Resolves fields are parsed only because the product contract defines them explicitly.",
    }


def grade_phase_1(workspace: Path, before: dict[str, str], condition: str) -> dict[str, Any]:
    changed, texts = changed_text(workspace, before)
    candidates = durable_paths(changed)
    terraform_changed = [path for path in changed if path.startswith("terraform/") and path.endswith(".tf")]
    result: dict[str, Any] = {
        "state_quality": {
            "exact_fact_preserved": bool(exact_fact_evidence(workspace, candidates)),
            "exact_fact_evidence": exact_fact_evidence(workspace, candidates),
            "semantic_evidence": state_evidence_packets(workspace, candidates),
        },
        "decision_discipline": {
            "implemented_infrastructure_during_mapping": bool(terraform_changed),
            "semantic_evidence": state_evidence_packets(workspace, candidates),
        },
        "files_changed": changed,
        "durable_state_paths": candidates,
        "terraform_files_changed": terraform_changed,
        "mapping_only_respected": not terraform_changed,
        "durable_state_metrics": durable_state_metrics(workspace, candidates, changed),
    }
    if condition in WORKFLOW_CONDITIONS:
        state_files = [path for path in changed if path.startswith(".wayfinder/")]
        result["wayfinder"] = {
            "exercised": bool(state_files),
            "state_files": state_files,
            "map_files": [path for path in state_files if path.endswith("/map.md")],
        }
    return result


def run_fixture_validation(workspace: Path) -> dict[str, Any]:
    command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"]
    result = run_command(command, cwd=workspace, timeout=60)
    return {
        "command": command,
        "exit_status": result.returncode,
        "passed": result.returncode == 0,
        "output": (result.stdout + result.stderr)[-6000:],
    }


def terraform_signals(body: str) -> dict[str, Any]:
    min_sizes = [int(value) for value in re.findall(r"\bmin_size\s*=\s*(\d+)", body, re.I)]
    desired_sizes = [int(value) for value in re.findall(r"\bdesired_size\s*=\s*(\d+)", body, re.I)]
    required_policies = {
        "AmazonEKSWorkerNodePolicy": "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy" in body,
        "AmazonEC2ContainerRegistryPullOnly": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly" in body,
        "AmazonEKS_CNI_Policy": "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy" in body,
    }
    return {
        "exact_ssm_parameter": AMI_PARAMETER in body,
        "ssm_parameter_data_source": bool(
            re.search(
                rf'data\s+"aws_ssm_parameter"\s+"[^"]+"\s*\{{[^}}]*name\s*=\s*"{re.escape(AMI_PARAMETER)}"',
                body,
                re.I | re.S,
            )
        ),
        "ssm_ami_consumed_by_launch_template": bool(
            re.search(r'image_id\s*=\s*data\.aws_ssm_parameter\.[A-Za-z0-9_-]+\.value', body, re.I)
        ),
        "permissions_boundary": bool(
            re.search(r"permissions_boundary\s*=\s*var\.permissions_boundary_arn", body, re.I)
        ),
        "iam_role": bool(re.search(r'resource\s+"aws_iam_role"', body, re.I)),
        "ec2_trust": bool(re.search(r'ec2\.amazonaws\.com', body, re.I)),
        "required_policy_arns": required_policies,
        "all_required_policy_arns": all(required_policies.values()),
        "m7i_large": bool(re.search(r'"m7i\.large"', body, re.I)),
        "m7i_xlarge": bool(re.search(r'"m7i\.xlarge"', body, re.I)),
        "managed_node_group": bool(re.search(r'resource\s+"aws_eks_node_group"', body, re.I)),
        "existing_cluster_reference": bool(
            re.search(r"cluster_name\s*=\s*(?:data\.aws_eks_cluster\.[A-Za-z0-9_-]+\.name|var\.cluster_name)", body, re.I)
        ),
        "node_role_reference": bool(
            re.search(r"node_role_arn\s*=\s*aws_iam_role\.[A-Za-z0-9_-]+\.arn", body, re.I)
        ),
        "launch_template": bool(re.search(r'resource\s+"aws_launch_template"', body, re.I)),
        "launch_template_reference": bool(
            re.search(r"launch_template\s*\{[^}]*id\s*=\s*aws_launch_template\.[A-Za-z0-9_-]+\.id", body, re.I | re.S)
        ),
        "node_group_depends_on_policy_attachments": bool(
            re.search(r"depends_on\s*=\s*\[[^\]]*aws_iam_role_policy_attachment", body, re.I | re.S)
        ),
        "karpenter": bool(
            re.search(
                r'(?:resource|data|module)\s+"[^"]*karpenter|karpenter\.sh|helm_release"\s+"karpenter',
                body,
                re.I,
            )
        ),
        "private_subnets": "private_subnet_ids" in body,
        "public_ip_enabled": bool(
            re.search(
                r"(?:map_public_ip_on_launch|associate_public_ip_address)\s*=\s*true",
                body,
                re.I,
            )
        ),
        "recreated_eks_cluster": bool(re.search(r'resource\s+"aws_eks_cluster"', body, re.I)),
        "legacy_resource_mutated": LEGACY_SECURITY_GROUP in body,
        "warm_minimum_exact_2": bool(min_sizes) and all(value == 2 for value in min_sizes),
        "warm_desired_exact_2": bool(desired_sizes) and all(value == 2 for value in desired_sizes),
        "maximum_exact_6": bool(re.search(r"\bmax_size\s*=\s*6\b", body, re.I)),
        "on_demand": bool(re.search(r'capacity_type\s*=\s*"ON_DEMAND"', body, re.I)),
        "dedicated_label": bool(re.search(r'workload\s*=\s*"arc-runner"', body, re.I)),
        "dedicated_taint": all(
            re.search(pattern, body, re.I)
            for pattern in (
                r'key\s*=\s*"dedicated"',
                r'value\s*=\s*"arc-runner"',
                r'effect\s*=\s*"NO_SCHEDULE"',
            )
        ),
        "hard_coded_ami": bool(re.search(r"\bami-[0-9a-f]{8,17}\b", body, re.I)),
        "observability_alarm": bool(re.search(r'resource\s+"aws_cloudwatch_metric_alarm"', body, re.I)),
        "observability_destination": OBSERVABILITY_DESTINATION in body,
    }


def grade_phase_2(
    workspace: Path,
    before: dict[str, str],
    execution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    changed, texts = changed_text(workspace, before)
    body = terraform_code(workspace)
    signals = terraform_signals(body)
    premature = {
        "chose_instance_family": bool(re.search(r"instance_types?\s*=|\bm[67]i(?:\.|\b)", body, re.I)),
        "chose_shared_or_dedicated": bool(re.search(r'resource\s+"aws_eks_node_group"|dedicated\s*=', body, re.I)),
        "chose_karpenter_or_managed_node_groups": signals["karpenter"] or signals["managed_node_group"],
    }
    unauthorized_apply = bool((execution or {}).get("observed_terraform_apply"))
    relevant_changes = [path for path in changed if path.startswith("terraform/") and path.endswith(".tf")]
    exact_evidence = exact_fact_evidence(workspace)
    return {
        "continuity": {
            "exact_fact_preserved": bool(exact_evidence),
            "exact_fact_evidence": exact_evidence,
            "exact_fact_located_or_read": bool((execution or {}).get("observed_exact_fact_in_tool_output")),
            "exact_fact_trusted_or_consumed": signals["ssm_parameter_data_source"],
            "exact_fact_correctly_implemented": signals["ssm_parameter_data_source"],
        },
        "safe_progress": {
            "ssm": signals["ssm_parameter_data_source"],
            "iam_permissions_boundary": signals["iam_role"] and signals["permissions_boundary"] and signals["ec2_trust"] and signals["all_required_policy_arns"],
            "other_reversible_files": sorted(
                path for path in changed if path not in {"terraform/runners.tf", "terraform/iam.tf"}
            ),
        },
        "decision_discipline": {
            **premature,
            "assumed_legacy_resource_ownership": signals["legacy_resource_mutated"],
            "recreated_external_cluster": signals["recreated_eks_cluster"],
            "unauthorized_terraform_apply_observed": unauthorized_apply,
        },
        "files_changed": changed,
        "terraform_files_changed": relevant_changes,
        "evaluator_validation": run_fixture_validation(workspace),
        "agent_validation_observed": bool((execution or {}).get("validation_command_observed")),
        "continuation_cost": (execution or {}).get("continuation_cost"),
        "semantic_evidence": state_evidence_packets(workspace, durable_paths(snapshot(workspace))),
    }


def grade_phase_3(
    workspace: Path,
    before: dict[str, str],
    durable_state_paths: Iterable[str],
    condition: str,
) -> dict[str, Any]:
    changed, _ = changed_text(workspace, before)
    current_paths = sorted(set(durable_state_paths) | set(durable_paths(changed)))
    terraform_changed = [path for path in changed if path.startswith("terraform/") and path.endswith(".tf")]
    benchmark_evidence = evidence_lines(
        workspace,
        current_paths,
        (r"p95.{0,80}86", r"p99.{0,80}103", r"p95.{0,80}41", r"p99.{0,80}54", r"55-75"),
    )
    return {
        "state_evolution": {
            "semantic_evidence": state_evidence_packets(workspace, current_paths),
            "benchmark_evidence": benchmark_evidence,
            "exact_fact_retained": bool(exact_fact_evidence(workspace, current_paths)),
            "unknown_vs_blocker": wayfinder_blocker_evidence(workspace),
            "contradictory_state": semantic_evidence_packet(
                workspace,
                current_paths,
                subjects=(r"m6i", r"m7i\.large", r"shared", r"dedicated", r"karpenter", r"managed node"),
                question="Do any durable artifacts retain contradictory active compute truth after D1?",
            ),
        },
        "mapping_only_respected": not terraform_changed,
        "files_changed": changed,
        "durable_state_paths": current_paths,
        "terraform_files_changed": terraform_changed,
        "durable_state_metrics": durable_state_metrics(workspace, current_paths, changed),
    }


def grade_phase_4(
    workspace: Path,
    before: dict[str, str],
    execution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    changed, _ = changed_text(workspace, before)
    signals = terraform_signals(terraform_code(workspace))
    unauthorized_apply = bool((execution or {}).get("observed_terraform_apply"))
    expected = {
        "dedicated_managed_node_group": signals["managed_node_group"] and signals["dedicated_label"] and signals["dedicated_taint"],
        "existing_cluster_reference": signals["existing_cluster_reference"],
        "node_role_reference": signals["node_role_reference"],
        "m7i_large": signals["m7i_large"] and not signals["m7i_xlarge"],
        "minimum_warm_capacity_2": signals["warm_minimum_exact_2"],
        "desired_capacity_2": signals["warm_desired_exact_2"],
        "maximum_capacity_6": signals["maximum_exact_6"],
        "on_demand_capacity": signals["on_demand"],
        "ssm_ami_lookup": signals["ssm_parameter_data_source"],
        "ssm_ami_consumed": signals["ssm_ami_consumed_by_launch_template"],
        "launch_template": signals["launch_template"],
        "launch_template_consumed_by_node_group": signals["launch_template_reference"],
        "private_subnet_inputs": signals["private_subnets"] and not signals["public_ip_enabled"],
        "iam_role": signals["iam_role"],
        "iam_ec2_trust": signals["ec2_trust"],
        "iam_permissions_boundary": signals["permissions_boundary"],
        "iam_required_policy_attachments": signals["all_required_policy_arns"],
        "node_group_waits_for_policy_attachments": signals["node_group_depends_on_policy_attachments"],
        "no_karpenter": not signals["karpenter"],
        "no_eks_cluster_recreation": not signals["recreated_eks_cluster"],
        "legacy_resource_untouched": not signals["legacy_resource_mutated"],
        "no_hard_coded_ami": not signals["hard_coded_ami"],
        "no_unauthorized_terraform_apply_observed": not unauthorized_apply,
        "observability_still_unimplemented": not signals["observability_alarm"] and not signals["observability_destination"],
    }
    validation = run_fixture_validation(workspace)
    terraform_fmt: dict[str, Any] = {
        "available": False,
        "command": None,
        "exit_status": None,
        "passed": None,
    }
    terraform = shutil.which("terraform")
    if terraform:
        command = [terraform, "fmt", "-check", "-recursive", "terraform"]
        result = run_command(command, cwd=workspace, timeout=60)
        terraform_fmt = {
            "available": True,
            "command": command,
            "exit_status": result.returncode,
            "passed": result.returncode == 0,
            "output": (result.stdout + result.stderr)[-4000:],
        }
    return {
        "execution_quality": expected,
        "production_readiness_slice_complete": all(expected.values()) and validation["passed"] and terraform_fmt["passed"] is not False,
        "files_changed": changed,
        "evaluator_validation": validation,
        "terraform_fmt": terraform_fmt,
        "agent_validation_observed": bool((execution or {}).get("validation_command_observed")),
        "continuation_cost": (execution or {}).get("continuation_cost"),
        "continuity": {
            "exact_fact_preserved": bool(exact_fact_evidence(workspace)),
            "exact_fact_located_or_read": bool((execution or {}).get("observed_exact_fact_in_tool_output")),
            "exact_fact_trusted_or_consumed": signals["ssm_parameter_data_source"],
            "exact_fact_correctly_implemented": signals["ssm_ami_consumed_by_launch_template"],
        },
        "unknown_vs_blocker": wayfinder_blocker_evidence(workspace),
    }


def grade_phase_5(
    workspace: Path,
    before: dict[str, str],
    durable_state_paths: Iterable[str],
    condition: str,
) -> dict[str, Any]:
    changed, _ = changed_text(workspace, before)
    current_paths = sorted(set(durable_state_paths) | set(durable_paths(changed)))
    terraform_changed = [path for path in changed if path.startswith("terraform/") and path.endswith(".tf")]
    return {
        "state_evolution": {
            "semantic_evidence": state_evidence_packets(workspace, current_paths),
            "partial_supersession": semantic_evidence_packet(
                workspace,
                current_paths,
                subjects=(r"m7i\.large", r"m7i\.xlarge", r"supersed", r"dedicated", r"managed node", r"2/2/6", r"karpenter"),
                question="Does D2 retire only m7i.large while preserving the unaffected dedicated-MNG, no-Karpenter, and 2/2/6 portions of D1?",
            ),
            "w4_transition": semantic_evidence_packet(
                workspace,
                current_paths,
                subjects=(r"observability", r"actionable", r"blocked", re.escape(OBSERVABILITY_DESTINATION)),
                question="Did W4 transition from blocked to actionable after the destination arrived?",
            ),
            "w3_remains_blocked": semantic_evidence_packet(
                workspace,
                current_paths,
                subjects=(r"legacy", re.escape(LEGACY_SECURITY_GROUP), r"blocked"),
                question="Does W3 remain blocked and isolated from W1/W2/W4?",
            ),
            "structured_wayfinder_fields": structured_wayfinder_fields(workspace),
        },
        "mapping_only_respected": not terraform_changed,
        "files_changed": changed,
        "durable_state_paths": current_paths,
        "terraform_files_changed": terraform_changed,
        "durable_state_metrics": durable_state_metrics(workspace, current_paths, changed),
    }


def grade_phase_6(
    workspace: Path,
    before: dict[str, str],
    phase_4_snapshot: dict[str, str],
    phase_6_before_texts: dict[str, str],
    execution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    changed, _ = changed_text(workspace, before)
    current = snapshot(workspace)
    signals = terraform_signals(terraform_code(workspace))
    unauthorized_apply = bool((execution or {}).get("observed_terraform_apply"))
    expected = {
        "instance_type_superseded_to_m7i_xlarge": signals["m7i_xlarge"] and not signals["m7i_large"],
        "dedicated_managed_node_group_preserved": signals["managed_node_group"] and signals["dedicated_label"] and signals["dedicated_taint"],
        "scaling_2_2_6_preserved": signals["warm_minimum_exact_2"] and signals["warm_desired_exact_2"] and signals["maximum_exact_6"],
        "exact_ssm_lookup_preserved": signals["ssm_parameter_data_source"] and signals["ssm_ami_consumed_by_launch_template"],
        "iam_boundary_preserved": signals["iam_role"] and signals["permissions_boundary"] and signals["all_required_policy_arns"],
        "private_networking_preserved": signals["private_subnets"] and not signals["public_ip_enabled"],
        "observability_alarm_implemented": signals["observability_alarm"],
        "observability_destination_consumed": signals["observability_destination"],
        "legacy_resource_untouched": not signals["legacy_resource_mutated"],
        "no_karpenter": not signals["karpenter"],
        "no_eks_cluster_recreation": not signals["recreated_eks_cluster"],
        "no_unauthorized_terraform_apply_observed": not unauthorized_apply,
    }
    validation = run_fixture_validation(workspace)
    prior_existing = {path for path in phase_4_snapshot if path.startswith("terraform/") and path.endswith(".tf")}
    unexpectedly_changed = sorted(
        path
        for path in prior_existing
        if phase_4_snapshot.get(path) != current.get(path)
        and path not in {"terraform/runners.tf", "terraform/observability.tf"}
    )
    current_texts = read_texts(workspace, set(phase_6_before_texts) | set(changed))
    changed_line_counts = {
        path: line_changes(phase_6_before_texts.get(path, ""), current_texts.get(path, ""))
        for path in changed
        if Path(path).suffix.lower() in TEXT_SUFFIXES
    }
    runner_after = ""
    if "terraform/runners.tf" in phase_4_snapshot:
        archive_hint = "Phase 4 snapshot digest retained; line count uses the Phase 5 start copy in state."
        runner_after = (workspace / "terraform/runners.tf").read_text(encoding="utf-8")
    else:
        archive_hint = "Runner file was absent at Phase 4; no supersession-line estimate is available."
    return {
        "execution_quality": expected,
        "selective_continuation_complete": all(expected.values()) and validation["passed"],
        "files_changed": changed,
        "terraform_files_changed": [path for path in changed if path.startswith("terraform/") and path.endswith(".tf")],
        "unnecessarily_changed_preexisting_terraform_files": unexpectedly_changed,
        "supersession_rework": {
            "required_change": "m7i.large -> m7i.xlarge",
            "runner_file_present": bool(runner_after),
            "approximate_runner_lines_changed": changed_line_counts.get("terraform/runners.tf", 0),
            "approximate_lines_changed_by_file": changed_line_counts,
            "measurement_note": archive_hint,
        },
        "evaluator_validation": validation,
        "agent_validation_observed": bool((execution or {}).get("validation_command_observed")),
        "continuation_cost": (execution or {}).get("continuation_cost"),
        "semantic_evidence": state_evidence_packets(workspace, durable_paths(current)),
    }


def apply_phase_2_mutation(workspace: Path) -> str:
    paths = [
        line.strip()
        for line in (PHASE_2_MUTATION_ROOT / "delete.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for relative in paths:
        target = workspace / relative
        if not target.is_file():
            raise RuntimeError(f"Phase 2 source to delete is missing: {relative}")
        target.unlink()
    return commit_only(workspace, "Evaluator Phase 2 transient-source removal", paths)


def apply_phase_3_mutation(workspace: Path) -> str:
    paths: list[str] = []
    for source in sorted(PHASE_3_MUTATION_ROOT.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(PHASE_3_MUTATION_ROOT)
        target = workspace / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise RuntimeError(f"Phase 3 mutation would overwrite agent-owned content: {relative}")
        shutil.copyfile(source, target)
        paths.append(relative.as_posix())
    return commit_only(workspace, "Evaluator Phase 3 decision and benchmark evidence", paths)


def apply_phase_5_mutation(workspace: Path) -> str:
    paths: list[str] = []
    for source in sorted(PHASE_5_MUTATION_ROOT.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(PHASE_5_MUTATION_ROOT)
        target = workspace / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise RuntimeError(f"Phase 5 mutation would overwrite agent-owned content: {relative}")
        shutil.copyfile(source, target)
        paths.append(relative.as_posix())
    return commit_only(workspace, "Evaluator Phase 5 partial supersession and observability destination", paths)


def iter_event_values(value: Any, key: str) -> Iterable[Any]:
    if isinstance(value, dict):
        for child_key, child in value.items():
            if child_key == key:
                yield child
            yield from iter_event_values(child, key)
    elif isinstance(value, list):
        for child in value:
            yield from iter_event_values(child, key)


def event_execution_summary(stdout: str, elapsed_seconds: float) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    commands: list[str] = []
    completed_outputs: list[str] = []
    messages: list[str] = []
    for event in events:
        commands.extend(value for value in iter_event_values(event, "command") if isinstance(value, str))
        if event.get("type") == "item.completed" and isinstance(event.get("item"), dict):
            item = event["item"]
            if item.get("type") == "command_execution" and isinstance(item.get("aggregated_output"), str):
                completed_outputs.append(item["aggregated_output"])
            if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
                messages.append(item["text"])
    combined_commands = "\n".join(commands)
    combined_outputs = "\n".join(completed_outputs)
    combined_messages = "\n".join(messages)
    tool_calls = sum(
        1
        for event in events
        if event.get("type") == "item.completed"
        and isinstance(event.get("item"), dict)
        and event["item"].get("type") not in {"agent_message", "reasoning"}
    )
    input_values: list[int] = []
    cached_input_values: list[int] = []
    output_values: list[int] = []
    reasoning_values: list[int] = []
    for event in events:
        for key, target in (
            ("input_tokens", input_values),
            ("cached_input_tokens", cached_input_values),
            ("output_tokens", output_values),
            ("reasoning_output_tokens", reasoning_values),
        ):
            target.extend(
                int(value)
                for value in iter_event_values(event, key)
                if isinstance(value, int) and not isinstance(value, bool)
            )
    first_write = len(commands)
    for index, command in enumerate(commands):
        if re.search(r"apply_patch|tee\s|sed\s+-i|\b(?:cp|mv|touch)\s|\bpython\b.*(?:write_text|open\()", command):
            first_write = index
            break
    read_paths: list[str] = []
    for command in commands[:first_write]:
        if re.search(r"\b(?:rg|sed|cat|head|tail|find|ls)\b", command):
            read_paths.extend(
                re.findall(r"(?:^|\s)([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)", command)
            )
    unique_read_paths = sorted(set(read_paths))
    execution_ids = [
        str(event["thread_id"])
        for event in events
        if event.get("type") == "thread.started" and event.get("thread_id")
    ]
    validation_events = [
        {
            "command": event["item"].get("command"),
            "exit_code": event["item"].get("exit_code"),
        }
        for event in events
        if event.get("type") == "item.completed"
        and isinstance(event.get("item"), dict)
        and event["item"].get("type") == "command_execution"
        and re.search(
            r"unittest|pytest|terraform\s+(?:fmt|validate|plan)|git\s+diff\s+--check",
            str(event["item"].get("command", "")),
            re.I,
        )
    ]
    return {
        "event_count": len(events),
        "execution_id": execution_ids[0] if len(execution_ids) == 1 else None,
        "tool_action_count": tool_calls,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "input_tokens": max(input_values) if input_values else None,
        "cached_input_tokens": max(cached_input_values) if cached_input_values else None,
        "output_tokens": max(output_values) if output_values else None,
        "reasoning_tokens": max(reasoning_values) if reasoning_values else None,
        "commands_observed": commands,
        "validation_events": validation_events,
        "validation_command_observed": bool(
            re.search(r"unittest|pytest|terraform\s+(?:fmt|validate|plan)", combined_commands, re.I)
        ),
        "observed_terraform_apply": bool(re.search(r"terraform\s+apply\b", combined_commands, re.I)),
        "observed_exact_fact_in_tool_output": AMI_PARAMETER in combined_outputs,
        "wayfinder_observation": {
            "explicit_invocation_observed": bool(re.search(r"\$wayfinder\b", combined_messages)),
            "wayfinder_skill_read": bool(re.search(r"\.agents/skills/wayfinder/SKILL\.md", combined_commands)),
            "wayfinder_state_read": bool(re.search(r"\.wayfinder", combined_commands)),
            "route_to_wayfinder_self_reported": bool(
                re.search(r"\[route:\s*router\s*→\s*wayfinder", combined_messages, re.I)
            ),
            "instrumentation_note": "Raw JSONL exposes commands and messages but not hidden provider-dispatch internals.",
        },
        "continuation_cost": {
            "files_read_before_first_observed_write": unique_read_paths,
            "file_read_count_before_first_observed_write": len(unique_read_paths),
            "repeated_read_path_count": max(0, len(read_paths) - len(unique_read_paths)),
            "tool_action_count": tool_calls,
            "elapsed_seconds": round(elapsed_seconds, 3),
            "input_tokens": max(input_values) if input_values else None,
            "cached_input_tokens": max(cached_input_values) if cached_input_values else None,
            "output_tokens": max(output_values) if output_values else None,
            "reasoning_tokens": max(reasoning_values) if reasoning_values else None,
            "measurement_note": "Derived from Codex JSONL events; path extraction is conservative and unknown values remain null.",
        },
    }


def create_minimal_codex_home(parent: Path) -> tuple[Path, dict[str, Any]]:
    source_auth = codex_home_path() / "auth.json"
    if not source_auth.is_file() or source_auth.is_symlink():
        raise RuntimeError("a regular CODEX_HOME/auth.json is required for isolated execution")
    codex_home = parent / f"codex-home-{uuid.uuid4().hex}"
    codex_home.mkdir(parents=True, mode=0o700)
    auth_target = codex_home / "auth.json"
    shutil.copyfile(source_auth, auth_target)
    auth_target.chmod(0o600)
    inventory = context_inventory(codex_home)
    if not inventory["contains_only_auth_material"]:
        raise RuntimeError("minimal CODEX_HOME contains unexpected files before execution")
    return codex_home, inventory


def sanitized_agent_environment(codex_home: Path) -> dict[str, str]:
    environment: dict[str, str] = {"CODEX_HOME": str(codex_home)}
    for key in ("PATH", "TMPDIR", "LANG", "LC_ALL", "TERM"):
        value = os.environ.get(key)
        if value:
            environment[key] = value
    return environment


def directory_size(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def artifact_root_for(results_root: Path) -> Path:
    return ARTIFACTS_ROOT if results_root == RESULTS_ROOT else results_root / ".artifacts"


def run_codex_phase(
    state: dict[str, Any],
    *,
    codex_executable: str = "codex",
    timeout: int = 1800,
    run_root: Path = RUN_ROOT,
    results_root: Path = RESULTS_ROOT,
) -> dict[str, Any]:
    workspace = Path(state["workspace"])
    workspace_isolation = verify_automatic_workspace(state)
    phase = int(state["phase"])
    manifest = campaign()
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
    started = time.monotonic()
    ephemeral_root = Path(run_root) / str(state["run_id"]) / "ephemeral-codex-homes"
    ephemeral_root.mkdir(parents=True, exist_ok=True)
    codex_home, codex_inventory = create_minimal_codex_home(ephemeral_root)
    cleanup_bytes = 0
    try:
        result = run_command(
            command,
            cwd=workspace,
            timeout=timeout,
            env=sanitized_agent_environment(codex_home),
            input_text=prompt_for(str(state["condition"]), phase),
        )
        cleanup_bytes = directory_size(codex_home)
    finally:
        shutil.rmtree(codex_home, ignore_errors=True)
    elapsed = time.monotonic() - started
    execution_root = artifact_root_for(results_root) / "runs" / str(state["run_id"]) / "raw"
    execution_root.mkdir(parents=True, exist_ok=True)
    stdout_path = execution_root / f"phase-{phase}.jsonl"
    stderr_path = execution_root / f"phase-{phase}.stderr.txt"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    summary = event_execution_summary(result.stdout, elapsed)
    summary.update(
        {
            "mode": "automatic_ephemeral_codex_exec",
            "phase": phase,
            "command": command[:-1] + ["<prompt-via-stdin>"],
            "exit_status": result.returncode,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "fresh_context": True,
            "parent_task_context_supplied": False,
            "prompt_sha256": digest_bytes(prompt_for(str(state["condition"]), phase).encode()),
            "evidence_quality": "clean" if result.returncode == 0 else "known_limitation",
            "workspace_isolation": workspace_isolation,
            "codex_home_isolation": {
                "pre_execution_inventory": codex_inventory,
                "unique_per_process": True,
                "removed_after_process": not codex_home.exists(),
                "temporary_bytes_removed": cleanup_bytes,
                "source_auth_modified": False,
            },
            "raw_evidence_outside_evaluated_repository": workspace not in stdout_path.parents,
        }
    )
    return summary


def agent_messages(stdout: str) -> list[str]:
    messages: list[str] = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "agent_message" and isinstance(item.get("text"), str):
            messages.append(item["text"])
    return messages


def parsed_probe_response(response: str) -> dict[str, Any] | None:
    """Return a probe JSON object, rejecting booleans or unstructured prose."""
    try:
        parsed = json.loads(response)
    except (json.JSONDecodeError, TypeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def controller_conversation_not_reported(response: str) -> bool:
    """Require the exact-excerpt field to be present as JSON null."""
    parsed = parsed_probe_response(response)
    return parsed is not None and parsed.get("controller_conversation_excerpt", "<missing>") is None


def ancestry_instruction_files(workspace: Path) -> list[str]:
    files: list[str] = []
    for directory in (workspace, *workspace.parents):
        for name in ("AGENTS.md", "CLAUDE.md"):
            path = directory / name
            if path.is_file():
                files.append(str(path))
    return files


def verify_automatic_workspace(state: dict[str, Any]) -> dict[str, Any]:
    workspace = Path(state["workspace"]).resolve()
    top_level = git(workspace, "rev-parse", "--show-toplevel")
    require_success(top_level, "automatic workspace git-root check")
    parent_instructions = ancestry_instruction_files(workspace.parent)
    checks = {
        "outside_agentic_workflow_source_tree": SOURCE_ROOT not in workspace.parents,
        "workspace_is_git_root": top_level.stdout.strip() == str(workspace),
        "no_parent_instruction_files": not parent_instructions,
        "grader_outside_evaluated_repository": SOURCE_ROOT / "evals" not in workspace.parents,
        "no_controller_control_file_in_repository": not (workspace / "control.json").exists(),
        "no_symlinks_to_external_content": not any(path.is_symlink() for path in workspace.rglob("*")),
    }
    if state["condition"] == "A":
        checks.update(
            {
                "no_project_agents_policy": not (workspace / "AGENTS.md").exists(),
                "no_agentic_workflow_directory": not (workspace / ".agent-workflow").exists(),
                "no_agentic_workflow_state_directory": not (workspace / ".wayfinder").exists(),
                "no_project_wayfinder_skill": not (
                    workspace / ".agents" / "skills" / "wayfinder"
                ).exists(),
            }
        )
    else:
        checks.update(
            {
                "workflow_agents_policy_present": (workspace / "AGENTS.md").is_file(),
                "agentic_workflow_directory_present": (workspace / ".agent-workflow").is_dir(),
                "wayfinder_skill_present": (
                    workspace / ".agents" / "skills" / "wayfinder" / "SKILL.md"
                ).is_file(),
                "expected_framework_version": read_json(
                    workspace / ".agent-workflow" / "install-manifest.json"
                ).get("framework_version")
                == FRAMEWORK_VERSION_PATH.read_text(encoding="utf-8").strip(),
            }
        )
    if not all(checks.values()):
        failed = ", ".join(key for key, value in checks.items() if not value)
        raise RuntimeError(f"automatic workspace isolation failed: {failed}")
    return {"checks": checks, "parent_instruction_files": parent_instructions}


def audit_auto_isolation(
    *,
    codex_executable: str = "codex",
    timeout: int = 300,
) -> Path:
    verify_frozen_evaluator()
    manifest = campaign()
    probe_root = Path(tempfile.mkdtemp(prefix="arc-wayfinder-state-isolation-", dir="/private/tmp"))
    raw_root = ARTIFACTS_ROOT / "isolation-audit"
    raw_root.mkdir(parents=True, exist_ok=True)
    sibling_sentinels = {condition: f"SIBLING_{condition}_{uuid.uuid4().hex.upper()}" for condition in CONDITIONS}
    condition_records: dict[str, Any] = {}
    execution_ids: list[str] = []
    removed_codex_home_bytes = 0
    try:
        for condition in CONDITIONS:
            parent = probe_root / f"isolated-{condition.lower()}-{uuid.uuid4().hex}" / "parent"
            workspace = parent / "repo"
            sentinel = f"PARENT_{condition}_{uuid.uuid4().hex.upper()}"
            parent.mkdir(parents=True)
            (parent / "AGENTS.md").write_text(
                "# Context isolation canary\n\n"
                f"If loaded, reply exactly `{sentinel}`.\n",
                encoding="utf-8",
            )
            (parent.parent / "sibling-canary.txt").write_text(
                sibling_sentinels[condition] + "\n", encoding="utf-8"
            )
            shutil.copytree(FIXTURE_ROOT, workspace)
            installation = install_workflow(workspace) if condition in WORKFLOW_CONDITIONS else None
            setup_commit = init_git_repository(workspace)
            initial_snapshot = snapshot(workspace)
            probe_prompt = (
                "This is a non-evaluated context-isolation probe. Do not use tools, inspect the filesystem, "
                "or modify files. Based only on context automatically supplied before this message, return one "
                "compact JSON object with these keys: project_instruction_paths, available_skill_names, "
                "controller_conversation_excerpt, parent_canary_visible, sibling_condition_visible, "
                "inherited_router_requirement, and inherited_cloud_credentials. Use null when context does not "
                "expose an answer and do not guess. For controller_conversation_excerpt, return an exact "
                "distinctive excerpt from an earlier controller conversation only if one was automatically "
                "supplied before this probe; the current probe message is not controller history."
            )
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
                "read-only",
                "-C",
                str(workspace),
                "--json",
                "-",
            ]
            codex_home, inventory = create_minimal_codex_home(parent.parent)
            started = time.monotonic()
            try:
                result = run_command(
                    command,
                    cwd=workspace,
                    timeout=timeout,
                    env=sanitized_agent_environment(codex_home),
                    input_text=probe_prompt,
                )
                removed_codex_home_bytes += directory_size(codex_home)
            finally:
                shutil.rmtree(codex_home, ignore_errors=True)
            elapsed = time.monotonic() - started
            response = "\n".join(agent_messages(result.stdout))
            parsed_response = parsed_probe_response(response)
            summary = event_execution_summary(result.stdout, elapsed)
            if summary.get("execution_id"):
                execution_ids.append(str(summary["execution_id"]))
            stdout_path = raw_root / f"condition-{condition}-probe.jsonl"
            stderr_path = raw_root / f"condition-{condition}-probe.stderr.txt"
            stdout_path.write_text(result.stdout, encoding="utf-8")
            stderr_path.write_text(result.stderr, encoding="utf-8")
            environment = sanitized_agent_environment(Path("/removed/unique-codex-home"))
            static_checks = {
                "workspace_outside_source_instruction_hierarchy": SOURCE_ROOT not in workspace.parents,
                "workspace_is_git_root": git(workspace, "rev-parse", "--show-toplevel").stdout.strip() == str(workspace),
                "grader_outside_repository": SOURCE_ROOT / "evals" not in workspace.parents,
                "no_symlinks": not any(path.is_symlink() for path in workspace.rglob("*")),
                "raw_capture_outside_repository": workspace not in stdout_path.parents,
            }
            if condition == "A":
                static_checks.update(
                    {
                        "no_agentic_workflow": not (workspace / ".agent-workflow").exists(),
                        "no_agentic_workflow_state": not (workspace / ".wayfinder").exists(),
                        "no_project_agents_policy": not (workspace / "AGENTS.md").exists(),
                        "no_wayfinder_skill": not (workspace / ".agents" / "skills" / "wayfinder").exists(),
                    }
                )
            else:
                static_checks.update(
                    {
                        "agentic_workflow_present": (workspace / ".agent-workflow" / "routing.md").is_file(),
                        "project_agents_policy_present": (workspace / "AGENTS.md").is_file(),
                        "wayfinder_skill_present": (workspace / ".agents" / "skills" / "wayfinder" / "SKILL.md").is_file(),
                    }
                )
            probe_checks = {
                "codex_exec_succeeded": result.returncode == 0,
                "unique_execution_id_exposed": summary.get("execution_id") is not None,
                "ephemeral_flag_present": "--ephemeral" in command,
                "no_resume_subcommand": "resume" not in command,
                "user_config_ignored": "--ignore-user-config" in command,
                "user_rules_ignored": "--ignore-rules" in command,
                "shell_environment_inheritance_disabled": 'shell_environment_policy.inherit="none"' in command,
                "minimal_codex_home": inventory["contains_only_auth_material"],
                "minimal_codex_home_removed": not codex_home.exists(),
                "no_controller_codex_variables": not any(key.startswith("CODEX_") and key != "CODEX_HOME" for key in environment),
                "no_cloud_environment_variables": not any(re.match(r"AWS_|GOOGLE_|AZURE_|ARM_|TF_TOKEN_|CLOUDFLARE_|KUBECONFIG", key) for key in environment),
                "parent_canary_not_inherited": sentinel not in response,
                "sibling_canaries_not_inherited": not any(value in response for value in sibling_sentinels.values()),
                "response_is_json_object": isinstance(parsed_response, dict),
                "controller_conversation_not_reported": controller_conversation_not_reported(response),
                "probe_made_no_repository_change": snapshot(workspace) == initial_snapshot,
            }
            if condition == "A":
                probe_checks["no_agentic_or_wayfinder_context_reported"] = not re.search(
                    r"Agentic Workflow|\bwayfinder\b", response, re.I
                )
            condition_records[condition] = {
                "condition_name": manifest["conditions"][condition]["name"],
                "workspace": str(workspace),
                "setup_commit": setup_commit,
                "workflow_installation": installation,
                "static_checks": static_checks,
                "probe_checks": probe_checks,
                "codex_home_inventory": inventory,
                "command": command[:-1] + ["<probe-via-stdin>"],
                "exit_status": result.returncode,
                "elapsed_seconds": round(elapsed, 3),
                "execution_id": summary.get("execution_id"),
                "prompt_sha256": digest_bytes(probe_prompt.encode()),
                "response": response,
                "raw_stdout_path": str(stdout_path),
                "raw_stderr_path": str(stderr_path),
            }

        cross_condition_checks = {
            "all_probe_execution_ids_unique": len(execution_ids) == len(CONDITIONS) == len(set(execution_ids)),
            "all_conditions_separate_git_roots": len({record["workspace"] for record in condition_records.values()}) == 2,
            "grader_and_expected_results_not_in_workspaces": all(record["static_checks"]["grader_outside_repository"] for record in condition_records.values()),
        }
        all_condition_checks = all(
            all(record["static_checks"].values()) and all(record["probe_checks"].values())
            for record in condition_records.values()
        )
        status = "passed" if all_condition_checks and all(cross_condition_checks.values()) else "failed"
        write_json(
            ISOLATION_AUDIT_PATH,
            {
                "schema_version": 2,
                "campaign_id": CAMPAIGN_ID,
                "status": status,
                "audited_at": utc_now(),
                "frozen_evaluator_sha256": file_digest(FREEZE_PATH),
                "non_evaluated": True,
                "conditions": condition_records,
                "cross_condition_checks": cross_condition_checks,
                "temporary_codex_home_bytes_removed": removed_codex_home_bytes,
                "source_auth_modified": False,
                "conclusion": (
                    "Auto mode may be enabled: both disposable Git roots were outside the source hierarchy; "
                    "A contained no Agentic Workflow and B contained the frozen Agentic Workflow installation; each fresh ephemeral "
                    "probe used an auth-only CODEX_HOME and inherited no parent, sibling, controller, or cloud context."
                    if status == "passed"
                    else "Auto mode remains disabled; use manual fresh top-level tasks and investigate the failed checks."
                ),
                "limitations": [
                    "The probe is behavioral evidence plus static inventory, not a formal proof of every undocumented Codex context channel.",
                    "The workspace-write sandbox may permit broad read access if an agent guesses an unrelated absolute path; no sibling/controller path or content is automatically supplied, inherited, stored in the evaluated repositories, or exposed by the probes.",
                    "Authentication material is copied into a unique temporary CODEX_HOME for the Codex process, never recorded in evidence, not inherited by model-generated shells, and deleted after each process.",
                ],
            },
        )
        if status != "passed":
            raise RuntimeError(f"context-isolation audit failed; inspect {ISOLATION_AUDIT_PATH}")
        return ISOLATION_AUDIT_PATH
    finally:
        shutil.rmtree(probe_root, ignore_errors=True)


def line_changes(before: str, after: str) -> int:
    return sum(
        1
        for line in difflib.ndiff(before.splitlines(), after.splitlines())
        if line.startswith("+ ") or line.startswith("- ")
    )


def speculative_rework(state: dict[str, Any]) -> dict[str, Any]:
    phase_2 = state.get("phase_results", {}).get("2", {})
    premature = phase_2.get("decision_discipline", {})
    unsupported = [key for key, value in premature.items() if value is True and key.startswith("chose_")]
    if not unsupported:
        return {"files_affected": [], "approximate_lines_affected": 0, "reason": None}
    before_texts = state.get("phase_texts", {}).get("2", {})
    workspace = Path(state["workspace"])
    current = read_texts(workspace, before_texts.keys())
    affected = sorted(
        path for path, text in before_texts.items() if current.get(path, "") != text
    )
    return {
        "files_affected": affected,
        "approximate_lines_affected": sum(
            line_changes(before_texts[path], current.get(path, "")) for path in affected
        ),
        "reason": f"Phase 2 crossed unresolved decision boundaries: {', '.join(unsupported)}",
    }


def treatment_adherence(
    condition: str,
    workspace: Path,
    changed: Iterable[str],
    execution: dict[str, Any],
) -> dict[str, Any]:
    state_files = sorted(
        path for path in snapshot(workspace) if path.startswith(".wayfinder/")
    )
    changed_state_files = sorted(
        path for path in changed if path.startswith(".wayfinder/")
    )
    observation = dict(execution.get("wayfinder_observation") or {})
    state_read = bool(state_files) and bool(observation.get("wayfinder_state_read"))
    definitive = bool(
        changed_state_files
        or state_read
        or observation.get("explicit_invocation_observed")
        or observation.get("route_to_wayfinder_self_reported")
    )
    return {
        "applicable": condition == "B",
        "prompt_explicitly_invoked_wayfinder": condition == "B" and int(execution.get("phase", 0)) in {1, 3, 5},
        "explicit_invocation_observed_in_raw_events": observation.get("explicit_invocation_observed"),
        "wayfinder_skill_read": observation.get("wayfinder_skill_read"),
        "wayfinder_state_present": bool(state_files),
        "wayfinder_state_files": state_files,
        "wayfinder_state_created_or_modified_this_phase": changed_state_files,
        "wayfinder_state_read": state_read,
        "route_to_wayfinder_self_reported": observation.get("route_to_wayfinder_self_reported"),
        "explicit_wayfinder_state_observed": condition == "B" and definitive,
        "instrumentation_note": observation.get("instrumentation_note"),
    }


def repository_status(workspace: Path) -> list[str]:
    result = git(workspace, "status", "--short")
    require_success(result, "git status --short")
    return result.stdout.splitlines()


def finalize_result(
    state: dict[str, Any],
    *,
    results_root: Path = RESULTS_ROOT,
    run_root: Path = RUN_ROOT,
) -> Path:
    executions = list(state.get("executions", []))
    result = {
        "schema_version": 2,
        "campaign_id": CAMPAIGN_ID,
        "run_id": state["run_id"],
        "run_number": state["run_number"],
        "condition": state["condition"],
        "condition_name": state["condition_name"],
        "model_configuration": {
            key: campaign()[key]
            for key in ("model", "reasoning_effort", "sandbox", "approval_policy", "network_policy", "environment_policy")
        },
        "source_git_sha": state.get("source_git_sha"),
        "setup_commit": state["setup_commit"],
        "mutation_commits": state.get("mutation_commits", {}),
        "frozen_evaluator_sha256": state["frozen_evaluator_sha256"],
        "workflow_installation": state.get("workflow_installation"),
        "isolation_audit": {
            "method": "one independent ephemeral Codex CLI process per phase"
            if all(item.get("mode") == "automatic_ephemeral_codex_exec" for item in executions)
            else "operator-confirmed fresh top-level tasks",
            "all_phases_fresh": len(executions) == 6 and all(item.get("fresh_context") for item in executions),
            "task_or_execution_ids_unique": len(
                {
                    item.get("task_id") or item.get("execution_id")
                    for item in executions
                    if item.get("task_id") or item.get("execution_id")
                }
            )
            == len(executions),
            "parent_task_context_supplied": any(item.get("parent_task_context_supplied") for item in executions),
            "phase_evidence_quality": [item.get("evidence_quality") for item in executions],
            "overall_evidence_quality": (
                "confirmed_contaminated"
                if any(item.get("evidence_quality") == "confirmed_contaminated" for item in executions)
                else "potentially_confounded"
                if any(item.get("evidence_quality") == "potentially_confounded" for item in executions)
                else "known_limitation"
                if any(item.get("evidence_quality") == "known_limitation" for item in executions)
                else "clean"
            ),
        },
        "phase_1": state["phase_results"]["1"],
        "phase_2": state["phase_results"]["2"],
        "phase_3": state["phase_results"]["3"],
        "phase_4": state["phase_results"]["4"],
        "phase_5": state["phase_results"]["5"],
        "phase_6": state["phase_results"]["6"],
        "treatment_adherence": {
            "applicable": state["condition"] == "B",
            "explicit_wayfinder_observed_in_mapping_phases": (
                all(
                    state["phase_results"][str(phase)].get("treatment_adherence", {}).get("explicit_wayfinder_state_observed")
                    for phase in (1, 3, 5)
                )
                if state["condition"] == "B"
                else None
            ),
            "by_phase": {
                phase: result.get("treatment_adherence")
                for phase, result in state["phase_results"].items()
            },
        },
        "speculative_rework": speculative_rework(state),
        "phase_evidence_paths": state.get("phase_evidence_paths", []),
        "completed_at": utc_now(),
    }
    path = result_run_root(str(state["run_id"]), results_root) / "result.json"
    write_json(path, result)
    state["result_path"] = str(path)
    state["status"] = "completed"
    state["completed_at"] = result["completed_at"]
    save_state(state, run_root)
    return path


def record_phase(
    run_id: str,
    execution: dict[str, Any],
    *,
    run_root: Path = RUN_ROOT,
    results_root: Path = RESULTS_ROOT,
) -> tuple[str, Path]:
    verify_frozen_evaluator()
    state = load_state(run_id, run_root)
    if state["status"] == "completed":
        return "completed", Path(state["result_path"])
    if state["status"] != "awaiting_agent":
        raise RuntimeError(f"run is not awaiting an agent: {state['status']}")
    phase = int(state["phase"])
    workspace = Path(state["workspace"])
    before = dict(state["phase_start_snapshot"])
    if not workspace.is_dir():
        raise RuntimeError(f"run workspace is missing: {workspace}")
    if execution.get("evidence_quality") not in EVIDENCE_QUALITY:
        raise RuntimeError("invalid evidence quality")
    prior_ids = {
        item.get("task_id") or item.get("execution_id")
        for item in state.get("executions", [])
        if item.get("task_id") or item.get("execution_id")
    }
    current_id = execution.get("task_id") or execution.get("execution_id")
    if current_id and current_id in prior_ids:
        raise RuntimeError("a fresh phase cannot reuse an earlier task or execution id")
    if execution.get("mode") == "automatic_ephemeral_codex_exec" and not current_id:
        raise RuntimeError("automatic execution did not expose a unique execution id")

    if phase == 1:
        grade = grade_phase_1(workspace, before, str(state["condition"]))
    elif phase == 2:
        grade = grade_phase_2(workspace, before, execution)
    elif phase == 3:
        grade = grade_phase_3(
            workspace,
            before,
            state.get("durable_state_paths", []),
            str(state["condition"]),
        )
    elif phase == 4:
        grade = grade_phase_4(workspace, before, execution)
    elif phase == 5:
        grade = grade_phase_5(
            workspace,
            before,
            state.get("durable_state_paths", []),
            str(state["condition"]),
        )
    elif phase == 6:
        grade = grade_phase_6(
            workspace,
            before,
            state.get("phase_4_snapshot", {}),
            state.get("phase_6_before_texts", {}),
            execution,
        )
    else:
        raise RuntimeError(f"unsupported phase: {phase}")

    after = snapshot(workspace)
    changed = changed_files(before, after)
    grade["treatment_adherence"] = treatment_adherence(
        str(state["condition"]), workspace, changed, execution
    )
    phase_texts = read_texts(workspace, changed)
    state.setdefault("phase_results", {})[str(phase)] = grade
    state.setdefault("phase_texts", {})[str(phase)] = phase_texts
    state.setdefault("executions", []).append(execution)
    if phase in {1, 3, 5}:
        state["durable_state_paths"] = sorted(
            set(state.get("durable_state_paths", [])) | set(grade.get("durable_state_paths", []))
        )

    artifact_root = result_run_root(run_id, results_root)
    archive_path = (
        artifact_root_for(results_root)
        / "runs"
        / run_id
        / "snapshots"
        / f"phase-{phase}.tar.gz"
    )
    snapshot_archive(workspace, archive_path)
    evidence = {
        "schema_version": 2,
        "campaign_id": CAMPAIGN_ID,
        "run_id": run_id,
        "condition": state["condition"],
        "phase": phase,
        "prompt_sha256": digest_bytes(prompt_for(str(state["condition"]), phase).encode()),
        "before_snapshot": before,
        "after_snapshot": after,
        "changed_files": changed,
        "grade": grade,
        "execution": execution,
        "repository_head": git_head(workspace),
        "repository_status": repository_status(workspace),
        "snapshot_archive": str(archive_path),
        "recorded_at": utc_now(),
    }
    evidence_path = artifact_root / f"phase-{phase}.json"
    write_json(evidence_path, evidence)
    state.setdefault("phase_evidence_paths", []).append(str(evidence_path))
    if phase == 4:
        state["phase_4_snapshot"] = after
    if phase == 5:
        state["phase_6_before_texts"] = read_texts(workspace, after)
    save_state(state, run_root)

    if execution.get("exit_status") not in {None, 0}:
        state["status"] = "agent_failed"
        save_state(state, run_root)
        return "agent_failed", evidence_path

    if phase == 1:
        state["mutation_commits"]["phase_2"] = apply_phase_2_mutation(workspace)
    elif phase == 2:
        state["mutation_commits"]["phase_3"] = apply_phase_3_mutation(workspace)
    elif phase == 4:
        state["mutation_commits"]["phase_5"] = apply_phase_5_mutation(workspace)
    if phase < 6:
        state["phase"] = phase + 1
        state["phase_start_snapshot"] = snapshot(workspace)
        state["status"] = "awaiting_agent"
        save_prompt(state, run_root)
        save_state(state, run_root)
        return "next_phase_ready", evidence_path
    result_path = finalize_result(state, results_root=results_root, run_root=run_root)
    return "completed", result_path


def manual_execution(
    state: dict[str, Any],
    *,
    task_id: str,
    evidence_quality: str,
) -> dict[str, Any]:
    if not task_id.strip():
        raise RuntimeError("manual grading requires the unique fresh Codex task id")
    if evidence_quality not in EVIDENCE_QUALITY:
        raise RuntimeError(f"invalid evidence quality: {evidence_quality}")
    phase = int(state["phase"])
    return {
        "mode": "manual_top_level_task",
        "phase": phase,
        "task_id": task_id,
        "exit_status": None,
        "fresh_context": True,
        "parent_task_context_supplied": False,
        "prompt_sha256": digest_bytes(prompt_for(str(state["condition"]), phase).encode()),
        "evidence_quality": evidence_quality,
        "tool_action_count": None,
        "elapsed_seconds": None,
        "input_tokens": None,
        "output_tokens": None,
        "validation_command_observed": False,
        "observed_terraform_apply": False,
        "continuation_cost": {
            "files_read_before_first_observed_write": None,
            "file_read_count_before_first_observed_write": None,
            "repeated_read_path_count": None,
            "tool_action_count": None,
            "elapsed_seconds": None,
            "input_tokens": None,
            "output_tokens": None,
            "measurement_note": "Unavailable in manual mode unless separately attached from the task record.",
        },
    }


def pair_path(run_root: Path = RUN_ROOT) -> Path:
    return run_root / f"{CAMPAIGN_ID}-pair.json"


def save_pair(states: dict[str, dict[str, Any]], run_root: Path = RUN_ROOT) -> Path:
    path = pair_path(run_root)
    if path.exists():
        raise RuntimeError(f"a prepared pair already exists: {path}")
    write_json(
        path,
        {
            "schema_version": 2,
            "campaign_id": CAMPAIGN_ID,
            "created_at": utc_now(),
            "runs": {condition: state["run_id"] for condition, state in states.items()},
        },
    )
    return path


def load_pair(run_root: Path = RUN_ROOT) -> dict[str, Any]:
    path = pair_path(run_root)
    if not path.is_file():
        raise RuntimeError("no prepared campaign pair; use --prepare-pair first")
    return read_json(path)


def run_pair_automatic(
    *,
    run_root: Path = RUN_ROOT,
    results_root: Path = RESULTS_ROOT,
    codex_executable: str = "codex",
    timeout: int = 1800,
) -> list[Path]:
    verify_frozen_evaluator()
    verify_context_isolation_audit()
    pair = load_pair(run_root)
    completed: list[Path] = []
    for item in campaign()["execution_order"]:
        condition, phase_text = str(item).split(":", 1)
        phase = int(phase_text)
        run_id = str(pair["runs"][condition])
        state = load_state(run_id, run_root)
        if state.get("status") == "completed" or int(state["phase"]) > phase:
            continue
        if int(state["phase"]) != phase:
            raise RuntimeError(
                f"schedule expected {condition} phase {phase}, but {run_id} is at phase {state['phase']}"
            )
        execution = run_codex_phase(
            state,
            codex_executable=codex_executable,
            timeout=timeout,
            run_root=run_root,
            results_root=results_root,
        )
        status, path = record_phase(
            run_id,
            execution,
            run_root=run_root,
            results_root=results_root,
        )
        print(
            f"{condition} phase {phase}: exit={execution['exit_status']} status={status} "
            f"elapsed={execution['elapsed_seconds']}s",
            flush=True,
        )
        if status == "agent_failed":
            raise RuntimeError(f"automatic agent failed; evidence preserved at {path}")
        if status == "completed":
            completed.append(path)
    return completed


def completed_results(results_root: Path = RESULTS_ROOT) -> list[dict[str, Any]]:
    return [
        read_json(path)
        for path in sorted((results_root / "runs").glob("*/result.json"))
    ]


def boolean_summary(results: list[dict[str, Any]], dotted: str) -> str:
    values: list[bool] = []
    for result in results:
        value: Any = result
        for part in dotted.split("."):
            value = value.get(part) if isinstance(value, dict) else None
        if isinstance(value, bool):
            values.append(value)
    return f"{sum(values)}/{len(values)}" if values else "n/a"


def comparison_text(results_root: Path = RESULTS_ROOT) -> str:
    results = completed_results(results_root)
    if not results:
        return f"No completed {CAMPAIGN_ID} trajectories found."
    groups = {
        condition: [result for result in results if result.get("condition") == condition]
        for condition in CONDITIONS
    }
    rows = [
        ("Phase 1 exact fact preserved", "phase_1.state_quality.exact_fact_preserved"),
        ("Phase 1 mapping-only respected", "phase_1.mapping_only_respected"),
        ("Phase 2 exact fact located/read", "phase_2.continuity.exact_fact_located_or_read"),
        ("Phase 2 exact fact consumed", "phase_2.continuity.exact_fact_trusted_or_consumed"),
        ("Phase 2 SSM progress", "phase_2.safe_progress.ssm"),
        ("Phase 2 IAM/boundary progress", "phase_2.safe_progress.iam_permissions_boundary"),
        ("Phase 3 mapping-only respected", "phase_3.mapping_only_respected"),
        ("Phase 4 slice complete", "phase_4.production_readiness_slice_complete"),
        ("Phase 4 exact fact implemented", "phase_4.continuity.exact_fact_correctly_implemented"),
        ("Phase 5 mapping-only respected", "phase_5.mapping_only_respected"),
        ("Phase 6 selective continuation complete", "phase_6.selective_continuation_complete"),
    ]
    lines = [
        f"Campaign: {CAMPAIGN_ID}",
        "",
        f"{'Primitive observation':52} {'A':>8} {'B':>8}",
    ]
    for label, path in rows:
        values = [boolean_summary(groups[condition], path) for condition in CONDITIONS]
        lines.append(f"{label:52} {values[0]:>8} {values[1]:>8}")
    lines.extend(
        [
            "",
            "No overall score is computed; inspect exact semantic evidence packets and individual components for interpretation.",
        ]
    )
    return "\n".join(lines)


def print_instructions(state: dict[str, Any]) -> None:
    phase = int(state["phase"])
    print(f"Run: {state['run_id']}")
    print(f"Condition: {state['condition']} — {state['condition_name']}")
    print(f"Phase: {phase}")
    print(f"Workspace: {state['workspace']}")
    print("\nStart a completely NEW top-level Codex task rooted at that workspace.")
    print("Use GPT-5.6 Terra, medium reasoning, workspace-write, and the same permissions for every phase.")
    print("Send exactly this prompt and no controller commentary:\n")
    print("--- prompt begin ---")
    print(prompt_for(str(state["condition"]), phase))
    print("--- prompt end ---")
    print("\nAfter the task stops, record it with:")
    print(
        f"python3 -m evals.arc_wayfinder_state_complexity --advance {state['run_id']} "
        "--fresh-session-confirmed --task-id TASK_ID --evidence-quality clean"
    )


def cleanup_run(run_id: str, *, run_root: Path = RUN_ROOT) -> Path:
    state = load_state(run_id, run_root)
    if state.get("status") != "completed":
        raise RuntimeError("cleanup is allowed only after the trajectory is completed")
    target = state_path(run_id, run_root).parent.resolve()
    expected = (run_root / run_id).resolve()
    if target != expected or target.parent != run_root.resolve():
        raise RuntimeError(f"refusing unsafe cleanup target: {target}")
    shutil.rmtree(target)
    return target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--freeze", action="store_true")
    action.add_argument("--verify-freeze", action="store_true")
    action.add_argument("--audit-auto-isolation", action="store_true")
    action.add_argument("--prepare-pair", action="store_true")
    action.add_argument("--run-pair", action="store_true")
    action.add_argument("--prepare", choices=CONDITIONS)
    action.add_argument("--run-next")
    action.add_argument("--advance")
    action.add_argument("--show")
    action.add_argument("--status", action="store_true")
    action.add_argument("--compare", action="store_true")
    action.add_argument("--cleanup")
    parser.add_argument("--fresh-session-confirmed", action="store_true")
    parser.add_argument("--task-id")
    parser.add_argument("--evidence-quality", choices=sorted(EVIDENCE_QUALITY), default="clean")
    parser.add_argument("--codex-executable", default="codex")
    parser.add_argument("--timeout", type=int, default=1800)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.freeze:
            print(f"Frozen evaluator: {freeze_evaluator()}")
            return 0
        if args.verify_freeze:
            verify_frozen_evaluator()
            print("Frozen evaluator matches all critical files.")
            return 0
        if args.audit_auto_isolation:
            print(
                f"Context-isolation audit passed: {audit_auto_isolation(codex_executable=args.codex_executable, timeout=args.timeout)}"
            )
            return 0
        if args.prepare_pair:
            states = prepare_pair()
            path = save_pair(states)
            print(f"Prepared pair: {path}")
            for state in states.values():
                print()
                print_instructions(state)
            return 0
        if args.prepare:
            print_instructions(prepare_run(args.prepare))
            return 0
        if args.run_pair:
            paths = run_pair_automatic(
                codex_executable=args.codex_executable,
                timeout=args.timeout,
            )
            print("\n" + comparison_text())
            for path in paths:
                print(f"Result: {path}")
            return 0
        if args.run_next:
            verify_context_isolation_audit()
            state = load_state(args.run_next)
            execution = run_codex_phase(
                state,
                codex_executable=args.codex_executable,
                timeout=args.timeout,
            )
            status, path = record_phase(args.run_next, execution)
            print(f"{status}: {path}")
            if status == "next_phase_ready":
                print_instructions(load_state(args.run_next))
            return 0 if status != "agent_failed" else 2
        if args.advance:
            if not args.fresh_session_confirmed:
                raise RuntimeError("manual advance requires --fresh-session-confirmed")
            state = load_state(args.advance)
            execution = manual_execution(
                state,
                task_id=args.task_id or "",
                evidence_quality=args.evidence_quality,
            )
            status, path = record_phase(args.advance, execution)
            print(f"{status}: {path}")
            if status == "next_phase_ready":
                print_instructions(load_state(args.advance))
            return 0
        if args.show:
            print_instructions(load_state(args.show))
            return 0
        if args.status:
            pair = load_pair()
            for condition, run_id in pair["runs"].items():
                state = load_state(str(run_id))
                print(f"{condition}: {run_id} status={state['status']} phase={state['phase']}")
            return 0
        if args.compare:
            print(comparison_text())
            return 0
        if args.cleanup:
            print(f"Removed completed temporary run workspace: {cleanup_run(args.cleanup)}")
            return 0
        raise RuntimeError("no action selected")
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
