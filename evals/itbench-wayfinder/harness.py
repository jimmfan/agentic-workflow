#!/usr/bin/env python3
"""Frozen-product ITBench-AA A/B/C evaluation harness.

The harness deliberately keeps benchmark data, controller ground truth, and
evaluated workspaces outside the source checkout. Generated evidence is copied
back under this evaluation directory only after a run completes.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import uuid
from typing import Any, Iterable


SOURCE_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = Path(__file__).resolve().parent
PROTOCOL_PATH = EVAL_ROOT / "protocol.md"
RUBRIC_PATH = EVAL_ROOT / "reasoning-rubric.md"
MANIFEST_PATH = EVAL_ROOT / "frozen-manifest.json"
PREFLIGHT_PATH = EVAL_ROOT / "preflight.json"
AUDIT_PATH = EVAL_ROOT / "context-isolation-audit.json"
RESULTS_ROOT = EVAL_ROOT / "results"
REPORTS_ROOT = EVAL_ROOT / "reports"

CAMPAIGN_ID = "itbench-wayfinder-v1"
ARTIFACTS_ROOT = EVAL_ROOT.parent / "artifacts" / CAMPAIGN_ID
DATASET_REPO = "ArtificialAnalysis/ITBench-AA"
DATASET_REVISION = "76df38a82288f75ba9e41dc8c515033332497473"
IBM_AGENT_REVISION = "30673b23a7166fc53162b2e6c23a364e7c5f0197"
TOPOLOGY_URL = (
    "https://raw.githubusercontent.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent/"
    f"{IBM_AGENT_REVISION}/metadata/otel_demo_astronomy_shop/architecture.json"
)
SCENARIOS = (102, 34, 83, 17, 24, 80)
CONDITIONS = ("A", "B", "C")
ORDER_SEED = 20260816
MODEL = "gpt-5.6-terra"
REASONING_EFFORT = "medium"
TIMEOUT_SECONDS = 1800

PUBLIC_ROOT = Path(tempfile.gettempdir()) / f"itbench-aa-public-{DATASET_REVISION[:12]}"
CONTROL_ROOT = Path(tempfile.gettempdir()) / f".{CAMPAIGN_ID}-controller-{DATASET_REVISION[:12]}"
RUN_ROOT = Path(tempfile.gettempdir()) / f".{CAMPAIGN_ID}-runs-{DATASET_REVISION[:12]}"

ADOPT_SCRIPT = SOURCE_ROOT / "skills" / "agentic-workflow" / "scripts" / "adopt.py"
PAYLOAD_ROOT = SOURCE_ROOT / "skills" / "agentic-workflow" / "payload"
PROJECT_SKILLS_ROOT = SOURCE_ROOT / ".agents" / "skills"

NEUTRAL_PROMPT = """Diagnose the Kubernetes SRE incident represented by the read-only offline
snapshot at:

{snapshot_path}

Use local shell and file-inspection tools to investigate the snapshot. It is a
recording, not a live cluster: do not use the network, alter the snapshot, or
attempt remediation.

Identify the smallest set of independent root-cause Kubernetes entities that
explains the incident. Write the final diagnosis as valid JSON to:

{output_path}

Use this schema:
{{
  "root_causes": [
    {{
      "kind": "Kubernetes kind",
      "name": "observed entity name",
      "namespace": "observed namespace or null",
      "condition": "concise explanation of the causal fault"
    }}
  ],
  "summary": "concise diagnosis and causal propagation explanation"
}}

Use entity kind, name, and namespace exactly as supported by the snapshot.
Do not include a downstream symptom merely because it is unhealthy.
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def run_command(
    command: list[str],
    *,
    cwd: Path,
    timeout: int = 60,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
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
        raise RuntimeError(f"{label} failed ({result.returncode}):\n{detail}")


def command_output(command: list[str], *, cwd: Path) -> str:
    result = run_command(command, cwd=cwd)
    require_success(result, " ".join(command))
    return result.stdout.strip()


def files_under(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and not path.is_symlink())


def tree_hash(root: Path) -> tuple[str, dict[str, str]]:
    entries = {path.relative_to(root).as_posix(): sha256_file(path) for path in files_under(root)}
    return sha256_bytes(json.dumps(entries, sort_keys=True).encode()), entries


def snapshot_tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        if path.is_symlink():
            result[relative.as_posix()] = f"symlink:{path.readlink()}"
        elif path.is_file():
            result[relative.as_posix()] = sha256_file(path)
    return result


def hf_api_url(scenario: int) -> str:
    path = urllib.parse.quote(f"sre/Scenario-{scenario}", safe="/")
    return (
        f"https://huggingface.co/api/datasets/{DATASET_REPO}/tree/"
        f"{DATASET_REVISION}/{path}?recursive=true&expand=false"
    )


def fetch_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": f"{CAMPAIGN_ID}/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def hf_entries(scenario: int) -> list[dict[str, Any]]:
    value = fetch_json(hf_api_url(scenario))
    if not isinstance(value, list):
        raise RuntimeError(f"unexpected Hugging Face tree response for Scenario-{scenario}")
    entries = [item for item in value if isinstance(item, dict) and item.get("type") == "file"]
    if not entries or not any(str(item.get("path", "")).endswith("/ground_truth.yaml") for item in entries):
        raise RuntimeError(f"Scenario-{scenario} response is missing ground_truth.yaml")
    return entries


def resolved_file_url(path: str) -> str:
    quoted = urllib.parse.quote(path, safe="/")
    return (
        f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/"
        f"{DATASET_REVISION}/{quoted}?download=true"
    )


def download_one(path: str, destination: Path, expected_size: int) -> dict[str, Any]:
    if destination.is_file() and destination.stat().st_size == expected_size:
        return {"path": path, "bytes": expected_size, "sha256": sha256_file(destination), "reused": True}
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + f".{uuid.uuid4().hex}.part")
    request = urllib.request.Request(resolved_file_url(path), headers={"User-Agent": f"{CAMPAIGN_ID}/1"})
    try:
        with urllib.request.urlopen(request, timeout=300) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output, length=1024 * 1024)
        actual_size = temporary.stat().st_size
        if actual_size != expected_size:
            raise RuntimeError(f"size mismatch for {path}: expected {expected_size}, got {actual_size}")
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"path": path, "bytes": expected_size, "sha256": sha256_file(destination), "reused": False}


def make_public_read_only(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_file():
            path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        elif path.is_dir():
            path.chmod(stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    root.chmod(stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


def make_public_writable(root: Path) -> None:
    if not root.exists():
        return
    for path in root.rglob("*"):
        if path.is_dir():
            path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        elif path.is_file():
            path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    root.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def download_topology() -> list[dict[str, Any]]:
    request = urllib.request.Request(TOPOLOGY_URL, headers={"User-Agent": f"{CAMPAIGN_ID}/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read()
    parsed = json.loads(content)
    if not isinstance(parsed, (dict, list)):
        raise RuntimeError("official topology is not a JSON object or array")
    digest = sha256_bytes(content)
    records: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        destination = PUBLIC_ROOT / f"Scenario-{scenario}" / "architecture.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        records.append(
            {
                "path": f"Scenario-{scenario}/architecture.json",
                "source_url": TOPOLOGY_URL,
                "bytes": len(content),
                "sha256": digest,
                "reused": False,
                "visibility": "agent",
            }
        )
    return records


def download_dataset(*, workers: int = 4) -> Path:
    PUBLIC_ROOT.mkdir(parents=True, exist_ok=True)
    make_public_writable(PUBLIC_ROOT)
    CONTROL_ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    jobs: list[tuple[str, Path, int, str]] = []
    source_inventory: dict[str, list[dict[str, Any]]] = {}
    for scenario in SCENARIOS:
        entries = hf_entries(scenario)
        source_inventory[str(scenario)] = entries
        for entry in entries:
            source_path = str(entry["path"])
            relative = Path(source_path).relative_to("sre")
            if relative.name == "ground_truth.yaml":
                destination = CONTROL_ROOT / "ground-truth" / relative
                visibility = "controller"
            else:
                destination = PUBLIC_ROOT / relative
                visibility = "agent"
            jobs.append((source_path, destination, int(entry["size"]), visibility))

    records: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(download_one, source_path, destination, size): (source_path, visibility)
            for source_path, destination, size, visibility in jobs
        }
        for index, future in enumerate(as_completed(futures), 1):
            source_path, visibility = futures[future]
            record = future.result()
            record["visibility"] = visibility
            records.append(record)
            if index % 25 == 0 or index == len(futures):
                print(f"downloaded/verified {index}/{len(futures)} files", flush=True)

    records.extend(download_topology())
    make_public_read_only(PUBLIC_ROOT)
    inventory = {
        "created_at": utc_now(),
        "dataset_repo": DATASET_REPO,
        "dataset_revision": DATASET_REVISION,
        "public_root": str(PUBLIC_ROOT),
        "controller_root": str(CONTROL_ROOT),
        "source_inventory": source_inventory,
        "files": sorted(records, key=lambda item: str(item["path"])),
    }
    path = CONTROL_ROOT / "download-inventory.json"
    write_json(path, inventory)
    print(path)
    return path


def product_fingerprint() -> dict[str, Any]:
    payload_hash, payload_files = tree_hash(PAYLOAD_ROOT)
    skills_hash, skill_files = tree_hash(PROJECT_SKILLS_ROOT)
    git_status = command_output(["git", "status", "--short"], cwd=SOURCE_ROOT).splitlines()
    return {
        "source_git_sha": command_output(["git", "rev-parse", "HEAD"], cwd=SOURCE_ROOT),
        "source_git_describe": command_output(["git", "describe", "--tags", "--always", "--dirty"], cwd=SOURCE_ROOT),
        "source_git_status": git_status,
        "framework_version": (PAYLOAD_ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "payload_tree_sha256": payload_hash,
        "payload_file_sha256": payload_files,
        "projected_skills_tree_sha256": skills_hash,
        "projected_skill_file_sha256": skill_files,
        "capability_names": sorted(path.parent.name for path in PROJECT_SKILLS_ROOT.glob("*/SKILL.md")),
        "domain_modeling_present": (PROJECT_SKILLS_ROOT / "domain-modeling" / "SKILL.md").is_file(),
        "wayfinder_present": (PROJECT_SKILLS_ROOT / "wayfinder" / "SKILL.md").is_file(),
    }


def yaml_scalar(value: str) -> Any:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {"'", '"'}:
        stripped = stripped[1:-1]
    if stripped.lower() == "true":
        return True
    if stripped.lower() == "false":
        return False
    if stripped.lower() in {"null", "none", "~"}:
        return None
    return stripped


def parse_matcher_ground_truth(path: Path) -> dict[str, Any]:
    """Parse only the stable groups/aliases subset needed for native matching."""
    section: str | None = None
    groups: list[dict[str, Any]] = []
    current_group: dict[str, Any] | None = None
    filter_mode = False
    aliases: list[list[str]] = []
    current_alias: list[str] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if match := re.fullmatch(r"([a-z_]+):", raw_line):
            if current_group is not None:
                groups.append(current_group)
                current_group = None
            section = match.group(1)
            filter_mode = False
            current_alias = None
            continue
        if section == "groups":
            if match := re.match(r"  - (id|kind|namespace|root_cause|filter):\s*(.*)$", raw_line):
                if current_group is not None:
                    groups.append(current_group)
                current_group = {"filter": []}
                key, value = match.groups()
                if key == "filter":
                    filter_mode = True
                    if value.strip():
                        current_group["filter"].append(str(yaml_scalar(value)))
                else:
                    current_group[key] = yaml_scalar(value)
                    filter_mode = False
                continue
            if current_group is None:
                continue
            if match := re.match(r"    (id|kind|namespace|root_cause):\s*(.+)$", raw_line):
                current_group[match.group(1)] = yaml_scalar(match.group(2))
                filter_mode = False
                continue
            if re.fullmatch(r"    filter:\s*", raw_line):
                filter_mode = True
                continue
            if filter_mode and (match := re.match(r"      -\s*(.+)$", raw_line)):
                current_group["filter"].append(str(yaml_scalar(match.group(1))))
                continue
        elif section == "aliases":
            if match := re.match(r"  - -\s*(.+)$", raw_line):
                current_alias = [str(yaml_scalar(match.group(1)))]
                aliases.append(current_alias)
                continue
            if current_alias is not None and (match := re.match(r"    -\s*(.+)$", raw_line)):
                current_alias.append(str(yaml_scalar(match.group(1))))
                continue
    if current_group is not None:
        groups.append(current_group)
    root_ids = [str(group["id"]) for group in groups if group.get("root_cause") is True]
    if not root_ids:
        raise RuntimeError(f"no root-cause groups parsed from {path}")
    by_id = {str(group["id"]): group for group in groups}
    roots: list[dict[str, Any]] = []
    for root_id in root_ids:
        accepted = {root_id}
        for alias_group in aliases:
            if root_id in alias_group:
                accepted.update(alias_group)
        roots.append(
            {
                "root_group_id": root_id,
                "accepted_group_ids": sorted(accepted),
                "accepted_groups": [by_id[group_id] for group_id in sorted(accepted) if group_id in by_id],
            }
        )
    return {"roots": roots, "aliases": aliases, "groups": groups}


def matcher_specs() -> dict[str, Any]:
    return {
        str(scenario): parse_matcher_ground_truth(
            CONTROL_ROOT / "ground-truth" / f"Scenario-{scenario}" / "ground_truth.yaml"
        )
        for scenario in SCENARIOS
    }


def prediction_matches_group(prediction: dict[str, Any], group: dict[str, Any]) -> bool:
    kind = str(prediction.get("kind", "")).strip()
    name = str(prediction.get("name", "")).strip()
    namespace_value = prediction.get("namespace")
    namespace = None if namespace_value is None else str(namespace_value).strip()
    if kind.casefold() != str(group.get("kind", "")).casefold():
        return False
    expected_namespace = group.get("namespace")
    if expected_namespace is not None and namespace != str(expected_namespace):
        return False
    filters = group.get("filter") or []
    return any(re.fullmatch(str(pattern), name) is not None for pattern in filters)


def native_grade(diagnosis: Any, matcher: dict[str, Any]) -> dict[str, Any]:
    predictions = diagnosis.get("root_causes", []) if isinstance(diagnosis, dict) else []
    if not isinstance(predictions, list):
        predictions = []
    normalized_predictions = [item for item in predictions if isinstance(item, dict)]
    per_prediction: list[dict[str, Any]] = []
    matched_roots: set[str] = set()
    for prediction in normalized_predictions:
        matching_root_ids: list[str] = []
        for root in matcher["roots"]:
            if any(prediction_matches_group(prediction, group) for group in root["accepted_groups"]):
                matching_root_ids.append(str(root["root_group_id"]))
                matched_roots.add(str(root["root_group_id"]))
        per_prediction.append({"prediction": prediction, "matching_root_ids": matching_root_ids, "matches": bool(matching_root_ids)})
    expected_root_ids = {str(root["root_group_id"]) for root in matcher["roots"]}
    missing = sorted(expected_root_ids - matched_roots)
    true_positives = sum(1 for item in per_prediction if item["matches"])
    false_positives = sum(1 for item in per_prediction if not item["matches"])
    full_recall = not missing
    precision = true_positives / len(per_prediction) if per_prediction else 0.0
    recall = len(matched_roots) / len(expected_root_ids) if expected_root_ids else 0.0
    score = precision if full_recall else 0.0
    return {
        "expected_root_group_ids": sorted(expected_root_ids),
        "matched_root_group_ids": sorted(matched_roots),
        "missing_root_group_ids": missing,
        "predictions": per_prediction,
        "true_positive_predictions": true_positives,
        "false_positive_predictions": false_positives,
        "precision": precision,
        "recall": recall,
        "full_recall": full_recall,
        "native_score": score,
        "success": full_recall and false_positives == 0,
        "metric_label": "ITBench-AA public-data derivative, deterministic pre-frozen matcher",
    }


def codex_version(codex_executable: str) -> str:
    return command_output([codex_executable, "--version"], cwd=SOURCE_ROOT)


def execution_order(repetitions: int = 3) -> list[dict[str, Any]]:
    permutations = [
        ("A", "B", "C"), ("A", "C", "B"), ("B", "A", "C"),
        ("B", "C", "A"), ("C", "A", "B"), ("C", "B", "A"),
    ]
    rng = random.Random(ORDER_SEED)
    order: list[dict[str, Any]] = []
    for repetition in range(1, repetitions + 1):
        scenario_order = list(SCENARIOS)
        rng.shuffle(scenario_order)
        permutation_order = list(permutations)
        rng.shuffle(permutation_order)
        for index, scenario in enumerate(scenario_order):
            permutation = permutation_order[(index + repetition - 1) % len(permutation_order)]
            for position, condition in enumerate(permutation, 1):
                order.append(
                    {
                        "repetition": repetition,
                        "scenario": scenario,
                        "condition": condition,
                        "within_scenario_position": position,
                    }
                )
    return order


def prompt_for(condition: str, snapshot_path: Path, output_path: Path) -> str:
    neutral = NEUTRAL_PROMPT.format(snapshot_path=snapshot_path, output_path=output_path)
    return f"$wayfinder\n\n{neutral}" if condition == "C" else neutral


def freeze_manifest(codex_executable: str = "codex") -> Path:
    inventory_path = CONTROL_ROOT / "download-inventory.json"
    if not inventory_path.is_file():
        raise RuntimeError("download inventory missing; run --download first")
    inventory = read_json(inventory_path)
    agent_files = [item for item in inventory["files"] if item.get("visibility") == "agent"]
    gt_files = [item for item in inventory["files"] if item.get("visibility") == "controller"]
    manifest = {
        "schema_version": 1,
        "campaign_id": CAMPAIGN_ID,
        "frozen_at": utc_now(),
        "status": "frozen_before_evaluated_runs",
        "conditions": {
            "A": {"name": "vanilla-codex", "agentic_workflow": False, "explicit_wayfinder": False},
            "B": {"name": "workflow-normal-routing", "agentic_workflow": True, "explicit_wayfinder": False},
            "C": {"name": "workflow-explicit-wayfinder", "agentic_workflow": True, "explicit_wayfinder": True},
        },
        "dataset": {
            "repo": DATASET_REPO,
            "revision": DATASET_REVISION,
            "scenarios": list(SCENARIOS),
            "agent_visible_files": agent_files,
            "controller_ground_truth_files": gt_files,
            "public_root": str(PUBLIC_ROOT),
            "snapshot_execution_mode": "shared read-only offline files",
            "topology": {"source_url": TOPOLOGY_URL, "source_revision": IBM_AGENT_REVISION},
            "deterministic_matcher_specs": matcher_specs(),
        },
        "product": product_fingerprint(),
        "runtime": {
            "model": MODEL,
            "reasoning_effort": REASONING_EFFORT,
            "codex_cli": codex_version(codex_executable),
            "sandbox": "workspace-write",
            "approval_policy": "never",
            "timeout_seconds": TIMEOUT_SECONDS,
            "retry_policy": "no agent retry; one pre-model infrastructure retry may be recorded",
            "context_policy": "fresh codex exec --ephemeral and unique minimal CODEX_HOME per run",
            "shell_environment_policy": "inherit PATH/TMPDIR/LANG/LC_ALL/TERM only",
            "network_policy": "prohibited by task contract and no network credentials inherited",
        },
        "prompts": {
            "neutral_template": NEUTRAL_PROMPT,
            "condition_c_prefix": "$wayfinder\n\n",
            "neutral_sha256": sha256_bytes(NEUTRAL_PROMPT.encode()),
        },
        "ordering": {"seed": ORDER_SEED, "full_three_repetition_order": execution_order(3)},
        "repetition_policy": "run all 18 repetition-1 cells, estimate cost, then run both remaining repetitions or stop",
        "native_scoring": "ITBench-AA public-data derivative: 0 if any GT root cause is missing, otherwise TP/(TP+FP)",
        "reasoning_grader": {
            "model": MODEL,
            "reasoning_effort": REASONING_EFFORT,
            "condition_blinding": "condition labels omitted; observable transcript treatment remains visible",
            "input_policy": "one completed run, frozen rubric, frozen ground truth, execution evidence",
        },
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "reasoning_rubric_sha256": sha256_file(RUBRIC_PATH),
        "provenance": {
            "itbench_git_sha": "a4946db21052d40c6d67fce2179aae979a211d32",
            "itbench_sre_agent_git_sha": IBM_AGENT_REVISION,
            "itbench_evaluations_git_sha": "14f026fc9cc348c4ecec5ab32714de954c95c1b1",
            "stirrup_git_sha": "247f24d56b2108235880ed2a2baea5d35b5a67ee",
            "itbench_lite_dataset_sha": "d0916b08ba421ce5e672e9ad68aa947d938dfef0",
        },
    }
    write_json(MANIFEST_PATH, manifest)
    print(MANIFEST_PATH)
    return MANIFEST_PATH


def init_git_workspace(workspace: Path) -> str:
    require_success(run_command(["git", "init", "--quiet"], cwd=workspace), "git init")
    require_success(run_command(["git", "add", "--all"], cwd=workspace), "git add")
    commit = run_command(
        ["git", "-c", "user.name=ITBench Eval", "-c", "user.email=eval@example.invalid",
         "commit", "--quiet", "--allow-empty", "-m", "Frozen evaluation workspace"],
        cwd=workspace,
    )
    require_success(commit, "git commit")
    return command_output(["git", "rev-parse", "HEAD"], cwd=workspace)


def install_workflow(workspace: Path) -> dict[str, Any]:
    result = run_command(
        [sys.executable, str(ADOPT_SCRIPT), "install", str(workspace), "--source-revision", "unreleased-local-package"],
        cwd=SOURCE_ROOT,
    )
    require_success(result, "Agentic Workflow adoption")
    destination_root = workspace / ".agents" / "skills"
    destination_root.mkdir(parents=True, exist_ok=True)
    for source in sorted(PROJECT_SKILLS_ROOT.iterdir()):
        if not source.is_dir():
            continue
        destination = destination_root / source.name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
    installed_roots = [workspace / "AGENTS.md", workspace / "CLAUDE.md", workspace / ".agent-workflow", workspace / ".agents"]
    installed_files: dict[str, str] = {}
    for root in installed_roots:
        candidates = [root] if root.is_file() else files_under(root) if root.is_dir() else []
        for path in candidates:
            installed_files[path.relative_to(workspace).as_posix()] = sha256_file(path)
    return {
        "installed_tree_sha256": sha256_bytes(json.dumps(installed_files, sort_keys=True).encode()),
        "installed_file_sha256": installed_files,
        "adopt_exit_status": result.returncode,
        "provider_projection_source": str(PROJECT_SKILLS_ROOT),
    }


def run_id(scenario: int, condition: str, repetition: int) -> str:
    return f"s{scenario}-{condition.lower()}-r{repetition}"


def prepare_runs(repetitions: int = 3) -> Path:
    manifest = read_json(MANIFEST_PATH)
    if manifest.get("status") != "frozen_before_evaluated_runs":
        raise RuntimeError("manifest is not frozen")
    records: list[dict[str, Any]] = []
    for item in manifest["ordering"]["full_three_repetition_order"]:
        if int(item["repetition"]) > repetitions:
            continue
        scenario = int(item["scenario"])
        condition = str(item["condition"])
        repetition = int(item["repetition"])
        identifier = run_id(scenario, condition, repetition)
        workspace = RUN_ROOT / identifier / "workspace"
        if workspace.exists():
            raise RuntimeError(f"prepared workspace already exists: {workspace}")
        workspace.mkdir(parents=True)
        installation = install_workflow(workspace) if condition in {"B", "C"} else None
        setup_commit = init_git_workspace(workspace)
        snapshot_path = PUBLIC_ROOT / f"Scenario-{scenario}"
        output_path = workspace / "diagnosis.json"
        prompt = prompt_for(condition, snapshot_path, output_path)
        record = {
            **item,
            "run_id": identifier,
            "workspace": str(workspace),
            "snapshot_path": str(snapshot_path),
            "output_path": str(output_path),
            "prompt": prompt,
            "prompt_sha256": sha256_bytes(prompt.encode()),
            "setup_commit": setup_commit,
            "setup_snapshot": snapshot_tree(workspace),
            "workflow_installation": installation,
            "status": "prepared",
        }
        write_json(RUN_ROOT / identifier / "control.json", record)
        records.append(record)
    path = CONTROL_ROOT / "prepared-runs.json"
    write_json(path, {"created_at": utc_now(), "repetitions": repetitions, "runs": records})
    print(path)
    return path


def load_run(identifier: str) -> dict[str, Any]:
    return read_json(RUN_ROOT / identifier / "control.json")


def save_run(record: dict[str, Any]) -> None:
    write_json(RUN_ROOT / str(record["run_id"]) / "control.json", record)


def codex_home_path() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser().resolve() if configured else (Path.home() / ".codex").resolve()


def create_minimal_codex_home(parent: Path) -> tuple[Path, dict[str, Any]]:
    source_auth = codex_home_path() / "auth.json"
    if not source_auth.is_file() or source_auth.is_symlink():
        raise RuntimeError("a regular CODEX_HOME/auth.json is required")
    destination = parent / f"codex-home-{uuid.uuid4().hex}"
    destination.mkdir(parents=True, mode=0o700)
    shutil.copyfile(source_auth, destination / "auth.json")
    (destination / "auth.json").chmod(0o600)
    inventory = {"files": ["auth.json"], "contains_only_auth_material": True, "auth_digest_recorded": False}
    return destination, inventory


def sanitized_environment(codex_home: Path) -> dict[str, str]:
    environment = {"CODEX_HOME": str(codex_home)}
    for key in ("PATH", "TMPDIR", "LANG", "LC_ALL", "TERM"):
        if value := os.environ.get(key):
            environment[key] = value
    return environment


def codex_command(codex_executable: str, workspace: Path, sandbox: str = "workspace-write") -> list[str]:
    return [
        codex_executable, "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules", "--strict-config",
        "-m", MODEL, "-c", f'model_reasoning_effort="{REASONING_EFFORT}"',
        "-c", 'approval_policy="never"', "-c", 'shell_environment_policy.inherit="none"',
        "-s", sandbox, "-C", str(workspace), "--json", "-",
    ]


def agent_messages(stdout: str) -> list[str]:
    messages: list[str] = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") if isinstance(event, dict) else None
        if event.get("type") == "item.completed" and isinstance(item, dict) and item.get("type") == "agent_message":
            if isinstance(item.get("text"), str):
                messages.append(item["text"])
    return messages


def event_summary(stdout: str) -> dict[str, Any]:
    usage: dict[str, Any] = {}
    execution_id: str | None = None
    tool_actions = 0
    command_events: list[dict[str, Any]] = []
    file_changes: list[dict[str, Any]] = []
    for line_number, line in enumerate(stdout.splitlines(), 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started":
            execution_id = event.get("thread_id")
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
        item = event.get("item")
        if event.get("type") == "item.completed" and isinstance(item, dict):
            if item.get("type") not in {"agent_message", "reasoning"}:
                tool_actions += 1
            if item.get("type") == "command_execution":
                command_events.append({"line": line_number, "command": item.get("command"), "exit_code": item.get("exit_code")})
            if item.get("type") == "file_change":
                file_changes.append({"line": line_number, "changes": item.get("changes", [])})
    return {
        "execution_id": execution_id,
        "usage": usage,
        "tool_action_count": tool_actions,
        "command_events": command_events,
        "file_changes": file_changes,
        "agent_messages": agent_messages(stdout),
    }


CAPABILITY_PATHS = {
    "wayfinder": ".agents/skills/wayfinder/SKILL.md",
    "domain-modeling": ".agents/skills/domain-modeling/SKILL.md",
    "debugging": ".agents/skills/workflow-debugging/SKILL.md",
    "research": ".agents/skills/research/SKILL.md",
    "discovery": ".agents/skills/workflow-discovery/SKILL.md",
    "verification": ".agents/skills/workflow-verification/SKILL.md",
}


def capability_observations(summary: dict[str, Any], workspace: Path) -> dict[str, Any]:
    commands = [str(item.get("command", "")) for item in summary.get("command_events", [])]
    observations: dict[str, Any] = {}
    for capability, path in CAPABILITY_PATHS.items():
        evidence = [item for item in summary.get("command_events", []) if path in str(item.get("command", ""))]
        invoked = bool(evidence)
        if capability == "wayfinder" and (workspace / ".agent-workflow-state" / "wayfinder").is_dir():
            invoked = True
            evidence = [*evidence, {"artifact": ".agent-workflow-state/wayfinder"}]
        if capability == "domain-modeling" and any((workspace / name).is_file() for name in ("CONTEXT.md", "CONTEXT-MAP.md")):
            invoked = True
            evidence = [*evidence, {"artifact": "CONTEXT.md or CONTEXT-MAP.md"}]
        observations[capability] = {"invoked": invoked, "evidence": evidence}
    route_markers = []
    for message in summary.get("agent_messages", []):
        route_markers.extend(re.findall(r"\[route:\s*router\s*→[^\]]+\]", message))
    observations["route_markers"] = route_markers
    observations["all_commands_containing_skill"] = [command for command in commands if ".agents/skills/" in command]
    return observations


def copy_workspace_evidence(workspace: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for path in sorted(workspace.rglob("*")):
        relative = path.relative_to(workspace)
        if ".git" in relative.parts or path.is_symlink():
            continue
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


def verify_product_unchanged(manifest: dict[str, Any]) -> None:
    current = product_fingerprint()
    frozen = manifest["product"]
    for key in ("source_git_sha", "payload_tree_sha256", "projected_skills_tree_sha256"):
        if current.get(key) != frozen.get(key):
            raise RuntimeError(f"frozen product changed at {key}")


def run_agent(identifier: str, *, codex_executable: str = "codex", timeout: int = TIMEOUT_SECONDS) -> Path:
    manifest = read_json(MANIFEST_PATH)
    verify_product_unchanged(manifest)
    preflight = read_json(PREFLIGHT_PATH)
    audit = read_json(AUDIT_PATH)
    if preflight.get("status") != "passed" or audit.get("status") != "passed":
        raise RuntimeError("preflight and context-isolation audit must pass before evaluated execution")
    record = load_run(identifier)
    if record.get("status") != "prepared":
        raise RuntimeError(f"run is not prepared: {identifier} ({record.get('status')})")
    workspace = Path(record["workspace"])
    prompt = str(record["prompt"])
    ephemeral_parent = RUN_ROOT / identifier / "ephemeral"
    ephemeral_parent.mkdir(parents=True, exist_ok=True)
    codex_home, codex_inventory = create_minimal_codex_home(ephemeral_parent)
    command = codex_command(codex_executable, workspace)
    started_at = utc_now()
    started = time.monotonic()
    launch_error: str | None = None
    try:
        result = run_command(
            command,
            cwd=workspace,
            timeout=timeout,
            env=sanitized_environment(codex_home),
            input_text=prompt,
        )
    except subprocess.TimeoutExpired as error:
        elapsed = time.monotonic() - started
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        result = subprocess.CompletedProcess(command, 124, stdout, stderr)
        launch_error = "timeout"
    finally:
        shutil.rmtree(codex_home, ignore_errors=True)
    elapsed = time.monotonic() - started
    result_root = RESULTS_ROOT / "runs" / identifier
    artifact_root = ARTIFACTS_ROOT / "runs" / identifier
    raw_root = artifact_root / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    stdout_path = raw_root / "codex.jsonl"
    stderr_path = raw_root / "codex.stderr.txt"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    summary = event_summary(result.stdout)
    diagnosis_path = Path(record["output_path"])
    diagnosis_valid = False
    diagnosis: Any = None
    if diagnosis_path.is_file():
        try:
            diagnosis = json.loads(diagnosis_path.read_text(encoding="utf-8"))
            diagnosis_valid = isinstance(diagnosis, dict)
        except json.JSONDecodeError:
            diagnosis = None
    current_workspace_snapshot = snapshot_tree(workspace)
    execution = {
        "run_id": identifier,
        "scenario": record["scenario"],
        "condition": record["condition"],
        "repetition": record["repetition"],
        "started_at": started_at,
        "finished_at": utc_now(),
        "elapsed_seconds": round(elapsed, 3),
        "exit_status": result.returncode,
        "launch_error": launch_error,
        "command": command[:-1] + ["<prompt-via-stdin>"],
        "prompt_sha256": record["prompt_sha256"],
        "fresh_context": True,
        "codex_home_isolation": {**codex_inventory, "removed_after_run": not codex_home.exists()},
        "summary": summary,
        "capabilities": capability_observations(summary, workspace),
        "diagnosis_valid_json_object": diagnosis_valid,
        "diagnosis": diagnosis,
        "workspace_changed_files": sorted(
            path for path in set(record["setup_snapshot"]) | set(current_workspace_snapshot)
            if record["setup_snapshot"].get(path) != current_workspace_snapshot.get(path)
        ),
        "artifacts": {
            "root": str(artifact_root),
            "codex_jsonl": str(stdout_path),
            "codex_stderr": str(stderr_path),
            "workspace": str(artifact_root / "workspace"),
        },
    }
    write_json(result_root / "execution.json", execution)
    copy_workspace_evidence(workspace, artifact_root / "workspace")
    record["status"] = "completed" if result.returncode == 0 else "agent_failed"
    record["result_path"] = str(result_root / "execution.json")
    save_run(record)
    print(result_root / "execution.json")
    return result_root / "execution.json"


def run_repetition(repetition: int, *, codex_executable: str = "codex", timeout: int = TIMEOUT_SECONDS) -> list[Path]:
    manifest = read_json(MANIFEST_PATH)
    completed: list[Path] = []
    for item in manifest["ordering"]["full_three_repetition_order"]:
        if int(item["repetition"]) != repetition:
            continue
        identifier = run_id(int(item["scenario"]), str(item["condition"]), repetition)
        record = load_run(identifier)
        if record.get("status") == "completed":
            completed.append(Path(record["result_path"]))
            continue
        completed.append(run_agent(identifier, codex_executable=codex_executable, timeout=timeout))
    return completed


def native_grade_run(identifier: str) -> Path:
    manifest = read_json(MANIFEST_PATH)
    record = load_run(identifier)
    if record.get("status") not in {"completed", "agent_failed"} or not record.get("result_path"):
        raise RuntimeError(f"run has no completed execution evidence: {identifier}")
    execution = read_json(Path(record["result_path"]))
    scenario = str(record["scenario"])
    grade = {
        "run_id": identifier,
        "scenario": int(scenario),
        "condition": record["condition"],
        "repetition": record["repetition"],
        "diagnosis_valid_json_object": execution.get("diagnosis_valid_json_object", False),
        **native_grade(
            execution.get("diagnosis"),
            manifest["dataset"]["deterministic_matcher_specs"][scenario],
        ),
    }
    path = RESULTS_ROOT / "grades" / identifier / "native.json"
    write_json(path, grade)
    print(path)
    return path


def native_grade_repetition(repetition: int) -> list[Path]:
    manifest = read_json(MANIFEST_PATH)
    return [
        native_grade_run(run_id(int(item["scenario"]), str(item["condition"]), repetition))
        for item in manifest["ordering"]["full_three_repetition_order"]
        if int(item["repetition"]) == repetition
    ]


def redact_evaluation_paths(value: str, identifier: str, record: dict[str, Any]) -> str:
    replacements = {
        identifier: "<OPAQUE_RUN>",
        str(record["workspace"]): "<EVALUATED_WORKSPACE>",
        str(record["snapshot_path"]): "<SNAPSHOT>",
        str(record["output_path"]): "<EVALUATED_WORKSPACE>/diagnosis.json",
    }
    redacted = value
    for original, replacement in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        redacted = redacted.replace(original, replacement)
    return redacted


REASONING_DIMENSIONS = {
    "evidence_vs_assumption", "premature_root_cause", "symptom_vs_cause",
    "unknown_preservation", "discriminating_evidence", "visibility_limits",
    "ownership_boundaries", "unsafe_remediation", "minimal_attribution",
    "remaining_evidence", "safe_continuation", "belief_updating",
}


def validate_reasoning_grade(value: Any, opaque_run_id: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["grade is not a JSON object"]
    if value.get("run_id") != opaque_run_id:
        errors.append("run_id does not match opaque id")
    dimensions = value.get("dimensions")
    if not isinstance(dimensions, dict) or set(dimensions) != REASONING_DIMENSIONS:
        errors.append("dimension keys do not match frozen rubric")
        return errors
    for name, item in dimensions.items():
        if not isinstance(item, dict):
            errors.append(f"{name} is not an object")
            continue
        if item.get("score") not in {0, 1, 2, None}:
            errors.append(f"{name} has invalid score")
        if not isinstance(item.get("evidence"), list) or not isinstance(item.get("explanation"), str):
            errors.append(f"{name} lacks evidence list or explanation")
    return errors


def reasoning_grade_run(
    identifier: str,
    *,
    codex_executable: str = "codex",
    timeout: int = TIMEOUT_SECONDS,
) -> Path:
    manifest = read_json(MANIFEST_PATH)
    if manifest.get("reasoning_rubric_sha256") != sha256_file(RUBRIC_PATH):
        raise RuntimeError("reasoning rubric changed after freeze")
    record = load_run(identifier)
    if record.get("status") not in {"completed", "agent_failed"} or not record.get("result_path"):
        raise RuntimeError(f"run has no completed execution evidence: {identifier}")
    execution_path = Path(record["result_path"])
    execution = read_json(execution_path)
    destination = RESULTS_ROOT / "grades" / identifier
    existing_path = destination / "reasoning.json"
    if existing_path.is_file():
        existing = read_json(existing_path)
        if existing.get("exit_status") == 0 and not existing.get("validation_errors"):
            print(existing_path)
            return existing_path

    recorded_transcript = execution.get("artifacts", {}).get("codex_jsonl")
    transcript_path = (
        Path(recorded_transcript)
        if isinstance(recorded_transcript, str)
        else ARTIFACTS_ROOT / "runs" / identifier / "raw" / "codex.jsonl"
    )
    if not transcript_path.is_file():
        raise RuntimeError(f"raw transcript missing: {transcript_path}")

    opaque_run_id = sha256_bytes(f"{CAMPAIGN_ID}:{identifier}".encode())[:20]
    grader_parent = RUN_ROOT / "reasoning-graders" / opaque_run_id
    attempt = 1 + len(list(grader_parent.glob("attempt-*"))) if grader_parent.exists() else 1
    grader_root = grader_parent / f"attempt-{attempt}"
    grader_root.mkdir(parents=True)
    shutil.copyfile(RUBRIC_PATH, grader_root / "rubric.md")
    raw_transcript = transcript_path.read_text(encoding="utf-8")
    (grader_root / "transcript.jsonl").write_text(
        redact_evaluation_paths(raw_transcript, identifier, record), encoding="utf-8"
    )
    sanitized_execution = {
        "opaque_run_id": opaque_run_id,
        "scenario": record["scenario"],
        "elapsed_seconds": execution.get("elapsed_seconds"),
        "exit_status": execution.get("exit_status"),
        "diagnosis_valid_json_object": execution.get("diagnosis_valid_json_object"),
        "diagnosis": execution.get("diagnosis"),
        "workspace_changed_files": execution.get("workspace_changed_files"),
    }
    (grader_root / "execution.json").write_text(
        redact_evaluation_paths(json.dumps(sanitized_execution, indent=2), identifier, record) + "\n",
        encoding="utf-8",
    )
    output_path = grader_root / "grade.json"
    prompt = f"""Independently grade one completed Kubernetes diagnosis trajectory.

Read rubric.md completely and follow it exactly. Then inspect transcript.jsonl,
and execution.json. Grade observable epistemic discipline, not correctness or
agreement with an unstated answer. Cite observable transcript line numbers,
command evidence, or final JSON fields. Do not use the network. Do not infer an
experimental condition. Write only the required rubric JSON object to
{output_path}, using opaque run_id {opaque_run_id}. Do not modify any other file.
"""
    init_git_workspace(grader_root)
    before = snapshot_tree(grader_root)
    codex_home, home_inventory = create_minimal_codex_home(grader_root / ".ephemeral")
    command = codex_command(codex_executable, grader_root)
    started_at = utc_now()
    started = time.monotonic()
    try:
        result = run_command(
            command,
            cwd=grader_root,
            timeout=timeout,
            env=sanitized_environment(codex_home),
            input_text=prompt,
        )
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(command, 124, error.stdout or "", error.stderr or "")
    finally:
        shutil.rmtree(codex_home, ignore_errors=True)
    elapsed = time.monotonic() - started
    grade: Any = None
    parse_error: str | None = None
    if output_path.is_file():
        try:
            grade = json.loads(output_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            parse_error = str(error)
    validation_errors = validate_reasoning_grade(grade, opaque_run_id)
    if parse_error:
        validation_errors.insert(0, parse_error)
    destination.mkdir(parents=True, exist_ok=True)
    raw_destination = ARTIFACTS_ROOT / "grades" / identifier
    raw_destination.mkdir(parents=True, exist_ok=True)
    (raw_destination / "reasoning-grader.jsonl").write_text(result.stdout, encoding="utf-8")
    (raw_destination / "reasoning-grader.stderr.txt").write_text(result.stderr, encoding="utf-8")
    artifact = {
        "run_id": identifier,
        "opaque_grader_run_id": opaque_run_id,
        "scenario": record["scenario"],
        "condition": record["condition"],
        "repetition": record["repetition"],
        "started_at": started_at,
        "finished_at": utc_now(),
        "elapsed_seconds": round(elapsed, 3),
        "exit_status": result.returncode,
        "condition_label_supplied_to_grader": False,
        "observable_treatment_left_in_transcript": True,
        "ground_truth_supplied_to_reasoning_grader": False,
        "ground_truth_policy": "withheld from model call; native correctness graded locally",
        "minimal_codex_home": {**home_inventory, "removed_after_run": not codex_home.exists()},
        "input_hashes": {
            "rubric": sha256_file(grader_root / "rubric.md"),
            "transcript": sha256_file(grader_root / "transcript.jsonl"),
            "execution": sha256_file(grader_root / "execution.json"),
        },
        "workspace_changed_files": sorted(
            path for path in set(before) | set(snapshot_tree(grader_root))
            if before.get(path) != snapshot_tree(grader_root).get(path)
        ),
        "validation_errors": validation_errors,
        "grade": grade,
    }
    path = destination / "reasoning.json"
    write_json(path, artifact)
    print(path)
    if result.returncode != 0 or validation_errors:
        raise RuntimeError(f"reasoning grader failed for {identifier}: exit={result.returncode}, errors={validation_errors}")
    return path


def reasoning_grade_repetition(
    repetition: int,
    *,
    codex_executable: str = "codex",
    timeout: int = TIMEOUT_SECONDS,
    workers: int = 1,
) -> list[Path]:
    manifest = read_json(MANIFEST_PATH)
    identifiers = [
        run_id(int(item["scenario"]), str(item["condition"]), repetition)
        for item in manifest["ordering"]["full_three_repetition_order"]
        if int(item["repetition"]) == repetition
    ]
    if workers <= 1:
        return [reasoning_grade_run(
            identifier, codex_executable=codex_executable, timeout=timeout
        ) for identifier in identifiers]
    paths: list[Path] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                reasoning_grade_run,
                identifier,
                codex_executable=codex_executable,
                timeout=timeout,
            ): identifier
            for identifier in identifiers
        }
        for future in as_completed(futures):
            paths.append(future.result())
    return paths


def public_snapshot_checks() -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for scenario in SCENARIOS:
        root = PUBLIC_ROOT / f"Scenario-{scenario}"
        checks[f"scenario_{scenario}_exists"] = root.is_dir()
        checks[f"scenario_{scenario}_ground_truth_absent"] = not any(
            path.name.lower() in {"ground_truth.yaml", "groundtruth.yaml"} for path in root.rglob("*")
        )
        checks[f"scenario_{scenario}_read_only"] = all(
            not (path.stat().st_mode & stat.S_IWUSR) for path in root.rglob("*") if path.is_file()
        )
    return checks


def inventory_integrity_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    records = [
        *manifest["dataset"]["agent_visible_files"],
        *manifest["dataset"]["controller_ground_truth_files"],
    ]
    for record in records:
        source_path = Path(str(record["path"]))
        if record["visibility"] == "controller":
            relative = Path(*source_path.parts[1:]) if source_path.parts[:1] == ("sre",) else source_path
            path = CONTROL_ROOT / "ground-truth" / relative
        else:
            relative = Path(*source_path.parts[1:]) if source_path.parts[:1] == ("sre",) else source_path
            path = PUBLIC_ROOT / relative
        key = sha256_bytes(str(record["path"]).encode())[:16]
        checks[f"inventory_{key}_exists"] = path.is_file()
        checks[f"inventory_{key}_bytes"] = path.is_file() and path.stat().st_size == int(record["bytes"])
        checks[f"inventory_{key}_sha256"] = path.is_file() and sha256_file(path) == record["sha256"]
    return checks


def preflight() -> Path:
    manifest = read_json(MANIFEST_PATH)
    verify_product_unchanged(manifest)
    prepared = read_json(CONTROL_ROOT / "prepared-runs.json")
    records = prepared["runs"]
    b_hashes = {record["workflow_installation"]["installed_tree_sha256"] for record in records if record["condition"] == "B"}
    c_hashes = {record["workflow_installation"]["installed_tree_sha256"] for record in records if record["condition"] == "C"}
    a_records = [record for record in records if record["condition"] == "A"]
    checks = {
        "manifest_frozen": manifest.get("status") == "frozen_before_evaluated_runs",
        "protocol_hash_matches": manifest.get("protocol_sha256") == sha256_file(PROTOCOL_PATH),
        "rubric_hash_matches": manifest.get("reasoning_rubric_sha256") == sha256_file(RUBRIC_PATH),
        "all_scenarios_selected": set(manifest["dataset"]["scenarios"]) == set(SCENARIOS),
        "all_54_runs_prepared": len(records) == 54,
        "all_runs_unique": len({record["run_id"] for record in records}) == len(records),
        "a_has_no_workflow": all(
            not (Path(record["workspace"]) / ".agent-workflow").exists()
            and not (Path(record["workspace"]) / "AGENTS.md").exists()
            for record in a_records
        ),
        "b_installations_identical": len(b_hashes) == 1,
        "c_installations_identical": len(c_hashes) == 1,
        "b_and_c_installations_identical": b_hashes == c_hashes,
        "b_prompt_has_no_explicit_wayfinder": all(not str(record["prompt"]).startswith("$wayfinder") for record in records if record["condition"] == "B"),
        "b_prompt_has_no_explicit_domain_modeling": all("$domain-modeling" not in str(record["prompt"]) for record in records if record["condition"] == "B"),
        "c_prompt_explicit_wayfinder": all(str(record["prompt"]).startswith("$wayfinder") for record in records if record["condition"] == "C"),
        "c_prompt_no_domain_modeling": all("$domain-modeling" not in str(record["prompt"]) for record in records if record["condition"] == "C"),
        "a_and_b_neutral_prompt_bodies_equal": all(
            prompt_for("A", Path(record["snapshot_path"]), Path(record["output_path"])).replace(str(record["output_path"]), "<OUTPUT>")
            == str(record["prompt"]).replace(str(record["output_path"]), "<OUTPUT>")
            for record in records if record["condition"] == "B"
        ),
        "domain_modeling_frozen": bool(manifest["product"]["domain_modeling_present"]),
        "wayfinder_frozen": bool(manifest["product"]["wayfinder_present"]),
        **public_snapshot_checks(),
        **inventory_integrity_checks(manifest),
    }
    status = "passed" if all(checks.values()) else "failed"
    value = {"created_at": utc_now(), "status": status, "checks": checks}
    write_json(PREFLIGHT_PATH, value)
    print(PREFLIGHT_PATH)
    if status != "passed":
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"preflight failed: {', '.join(failed)}")
    return PREFLIGHT_PATH


def audit_isolation(*, codex_executable: str = "codex", timeout: int = 300) -> Path:
    preflight_value = read_json(PREFLIGHT_PATH)
    if preflight_value.get("status") != "passed":
        raise RuntimeError("static preflight must pass before isolation audit")
    audit_root = CONTROL_ROOT / f"isolation-{uuid.uuid4().hex}"
    condition_results: dict[str, Any] = {}
    execution_ids: list[str] = []
    for condition in CONDITIONS:
        workspace = audit_root / condition / "workspace"
        workspace.mkdir(parents=True)
        installation = install_workflow(workspace) if condition in {"B", "C"} else None
        init_git_workspace(workspace)
        before = snapshot_tree(workspace)
        sentinel = f"CONTROLLER_{uuid.uuid4().hex.upper()}"
        sibling = audit_root / f"sibling-{condition}-{uuid.uuid4().hex}.txt"
        sibling.write_text(sentinel + "\n", encoding="utf-8")
        probe = (
            "This is a non-evaluated context-isolation probe. Do not use tools or inspect the filesystem. "
            "Return one JSON object with keys project_instruction_paths, available_skill_names, "
            "controller_conversation_excerpt, sibling_sentinel, and inherited_cloud_credentials. "
            "Use null when the automatically supplied context does not expose an answer; do not guess."
        )
        codex_home, inventory = create_minimal_codex_home(audit_root / condition)
        command = codex_command(codex_executable, workspace, sandbox="read-only")
        try:
            result = run_command(command, cwd=workspace, timeout=timeout, env=sanitized_environment(codex_home), input_text=probe)
        finally:
            shutil.rmtree(codex_home, ignore_errors=True)
        summary = event_summary(result.stdout)
        if summary.get("execution_id"):
            execution_ids.append(str(summary["execution_id"]))
        response = "\n".join(summary["agent_messages"])
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            parsed = None
        checks = {
            "codex_succeeded": result.returncode == 0,
            "response_json_object": isinstance(parsed, dict),
            "unique_minimal_codex_home_removed": not codex_home.exists() and inventory["contains_only_auth_material"],
            "probe_made_no_workspace_change": before == snapshot_tree(workspace),
            "sibling_sentinel_not_reported": sentinel not in response,
            "controller_conversation_not_reported": isinstance(parsed, dict) and parsed.get("controller_conversation_excerpt") is None,
        }
        if condition == "A":
            checks["a_has_no_workflow_context"] = not re.search(r"Agentic Workflow|wayfinder|domain-modeling", response, re.I)
        else:
            checks["workflow_installation_present"] = installation is not None and (workspace / "AGENTS.md").is_file()
        raw_root = ARTIFACTS_ROOT / "audit-evidence"
        raw_root.mkdir(parents=True, exist_ok=True)
        (raw_root / f"{condition}.jsonl").write_text(result.stdout, encoding="utf-8")
        (raw_root / f"{condition}.stderr.txt").write_text(result.stderr, encoding="utf-8")
        condition_results[condition] = {"checks": checks, "response": parsed, "execution_id": summary.get("execution_id")}
    cross_checks = {
        "all_execution_ids_unique": len(execution_ids) == 3 and len(set(execution_ids)) == 3,
        "all_condition_checks_pass": all(all(record["checks"].values()) for record in condition_results.values()),
    }
    status = "passed" if all(cross_checks.values()) else "failed"
    value = {"created_at": utc_now(), "status": status, "conditions": condition_results, "cross_checks": cross_checks}
    write_json(AUDIT_PATH, value)
    print(AUDIT_PATH)
    if status != "passed":
        raise RuntimeError("context-isolation audit failed")
    return AUDIT_PATH


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--download", action="store_true")
    action.add_argument("--freeze", action="store_true")
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--preflight", action="store_true")
    action.add_argument("--audit-isolation", action="store_true")
    action.add_argument("--run")
    action.add_argument("--run-repetition", type=int, choices=(1, 2, 3))
    action.add_argument("--grade-native")
    action.add_argument("--grade-native-repetition", type=int, choices=(1, 2, 3))
    action.add_argument("--grade-reasoning")
    action.add_argument("--grade-reasoning-repetition", type=int, choices=(1, 2, 3))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--repetitions", type=int, choices=(1, 2, 3), default=3)
    parser.add_argument("--codex-executable", default="codex")
    parser.add_argument("--timeout", type=int, default=TIMEOUT_SECONDS)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.download:
        download_dataset(workers=args.workers)
    elif args.freeze:
        freeze_manifest(args.codex_executable)
    elif args.prepare:
        prepare_runs(repetitions=args.repetitions)
    elif args.preflight:
        preflight()
    elif args.audit_isolation:
        audit_isolation(codex_executable=args.codex_executable, timeout=args.timeout)
    elif args.run:
        run_agent(args.run, codex_executable=args.codex_executable, timeout=args.timeout)
    elif args.run_repetition:
        run_repetition(args.run_repetition, codex_executable=args.codex_executable, timeout=args.timeout)
    elif args.grade_native:
        native_grade_run(args.grade_native)
    elif args.grade_native_repetition:
        native_grade_repetition(args.grade_native_repetition)
    elif args.grade_reasoning:
        reasoning_grade_run(args.grade_reasoning, codex_executable=args.codex_executable, timeout=args.timeout)
    elif args.grade_reasoning_repetition:
        reasoning_grade_repetition(
            args.grade_reasoning_repetition,
            codex_executable=args.codex_executable,
            timeout=args.timeout,
            workers=args.workers,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
