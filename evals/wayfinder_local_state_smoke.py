#!/usr/bin/env python3
"""Frozen A/B/C smoke for the Wayfinder local-state integration."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any, Iterable

from evals import arc_wayfinder_v2 as base


EVAL_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = EVAL_ROOT.parent
CAMPAIGN_ID = "wayfinder-local-state-smoke-v1"
CAMPAIGN_PATH = EVAL_ROOT / "campaigns" / f"{CAMPAIGN_ID}.json"
PROTOCOL_PATH = EVAL_ROOT / "wayfinder-local-state-smoke" / "protocol.md"
RUBRIC_PATH = EVAL_ROOT / "wayfinder-local-state-smoke" / "rubric.md"
SCENARIO_ROOT = EVAL_ROOT / "scenarios" / "arc-wayfinder-e2e-v2"
RESULTS_ROOT = EVAL_ROOT / "results" / CAMPAIGN_ID
ARTIFACTS_ROOT = EVAL_ROOT / "artifacts" / CAMPAIGN_ID
FREEZE_PATH = RESULTS_ROOT / "frozen-evaluator.json"
ISOLATION_AUDIT_PATH = RESULTS_ROOT / "context-isolation-audit.json"
RUN_ROOT = Path(tempfile.gettempdir()) / CAMPAIGN_ID
PACKAGE_ROOT = SOURCE_ROOT / "skills" / "agentic-workflow"


def configure_base() -> None:
    base.CAMPAIGN_ID = CAMPAIGN_ID
    base.CAMPAIGN_PATH = CAMPAIGN_PATH
    base.SCENARIO_ROOT = SCENARIO_ROOT
    base.FIXTURE_ROOT = SCENARIO_ROOT / "fixture"
    base.PHASE_2_MUTATION_ROOT = SCENARIO_ROOT / "phase-2-mutation"
    base.PHASE_3_MUTATION_ROOT = SCENARIO_ROOT / "phase-3-mutation"
    base.RESULTS_ROOT = RESULTS_ROOT
    base.ARTIFACTS_ROOT = ARTIFACTS_ROOT
    base.FREEZE_PATH = FREEZE_PATH
    base.ISOLATION_AUDIT_PATH = ISOLATION_AUDIT_PATH
    base.RUN_ROOT = RUN_ROOT


configure_base()


# The reusable v2 harness predates campaign wrappers, so its function defaults
# retain the old campaign paths. Bind the reusable operations to this campaign
# explicitly while still honoring caller-supplied temporary roots in tests and
# the isolation audit.
_load_state = base.load_state
_save_state = base.save_state
_result_run_root = base.result_run_root
_prepare_run = base.prepare_run
_prepare_trio = base.prepare_trio
_run_codex_phase = base.run_codex_phase
_record_phase = base.record_phase
_trio_path = base.trio_path
_save_trio = base.save_trio
_load_trio = base.load_trio
_run_trio_automatic = base.run_trio_automatic
_completed_results = base.completed_results


def load_state(run_id: str, run_root: Path = RUN_ROOT) -> dict[str, Any]:
    return _load_state(run_id, run_root)


def save_state(state: dict[str, Any], run_root: Path = RUN_ROOT) -> None:
    _save_state(state, run_root)


def result_run_root(run_id: str, results_root: Path = RESULTS_ROOT) -> Path:
    return _result_run_root(run_id, results_root)


def prepare_run(
    condition: str,
    *,
    run_number: int = 1,
    run_root: Path = RUN_ROOT,
    require_frozen: bool = True,
) -> dict[str, Any]:
    return _prepare_run(
        condition,
        run_number=run_number,
        run_root=run_root,
        require_frozen=require_frozen,
    )


def prepare_trio(
    *, run_root: Path = RUN_ROOT, require_frozen: bool = True
) -> dict[str, dict[str, Any]]:
    return _prepare_trio(run_root=run_root, require_frozen=require_frozen)


def run_codex_phase(
    state: dict[str, Any],
    *,
    codex_executable: str = "codex",
    timeout: int = 1800,
    run_root: Path = RUN_ROOT,
    results_root: Path = RESULTS_ROOT,
) -> dict[str, Any]:
    return _run_codex_phase(
        state,
        codex_executable=codex_executable,
        timeout=timeout,
        run_root=run_root,
        results_root=results_root,
    )


def record_phase(
    run_id: str,
    execution: dict[str, Any],
    *,
    run_root: Path = RUN_ROOT,
    results_root: Path = RESULTS_ROOT,
) -> tuple[str, Path]:
    return _record_phase(
        run_id,
        execution,
        run_root=run_root,
        results_root=results_root,
    )


def trio_path(run_root: Path = RUN_ROOT) -> Path:
    return _trio_path(run_root)


def save_trio(states: dict[str, dict[str, Any]], run_root: Path = RUN_ROOT) -> Path:
    return _save_trio(states, run_root)


def load_trio(run_root: Path = RUN_ROOT) -> dict[str, Any]:
    return _load_trio(run_root)


def run_trio_automatic(
    *,
    run_root: Path = RUN_ROOT,
    results_root: Path = RESULTS_ROOT,
    codex_executable: str = "codex",
    timeout: int = 1800,
) -> list[Path]:
    return _run_trio_automatic(
        run_root=run_root,
        results_root=results_root,
        codex_executable=codex_executable,
        timeout=timeout,
    )


def completed_results(results_root: Path = RESULTS_ROOT) -> list[dict[str, Any]]:
    return _completed_results(results_root)


base.load_state = load_state
base.save_state = save_state
base.result_run_root = result_run_root
base.prepare_run = prepare_run
base.prepare_trio = prepare_trio
base.run_codex_phase = run_codex_phase
base.record_phase = record_phase
base.trio_path = trio_path
base.save_trio = save_trio
base.load_trio = load_trio
base.run_trio_automatic = run_trio_automatic
base.completed_results = completed_results


def critical_paths() -> list[Path]:
    paths = [
        Path(__file__).resolve(),
        Path(base.__file__).resolve(),
        CAMPAIGN_PATH,
        PROTOCOL_PATH,
        RUBRIC_PATH,
        PACKAGE_ROOT / "VERSION",
        PACKAGE_ROOT / "scripts" / "adopt.py",
        PACKAGE_ROOT / "scripts" / "lifecycle.py",
        PACKAGE_ROOT / "scripts" / "providers.py",
        SOURCE_ROOT / ".agents" / "skills" / "wayfinder" / "SKILL.md",
        SOURCE_ROOT / ".agents" / "skills" / "wayfinder" / "agents" / "openai.yaml",
    ]
    paths.extend(path for path in sorted((PACKAGE_ROOT / "payload").rglob("*")) if path.is_file())
    paths.extend(path for path in sorted(SCENARIO_ROOT.rglob("*")) if path.is_file())
    return sorted(set(path.resolve() for path in paths))


def critical_digests() -> dict[str, str]:
    return {
        path.relative_to(SOURCE_ROOT).as_posix(): base.file_digest(path)
        for path in critical_paths()
    }


base.critical_paths = critical_paths
base.critical_digests = critical_digests


_base_event_execution_summary = base.event_execution_summary


def event_execution_summary(stdout: str, elapsed_seconds: float) -> dict[str, Any]:
    summary = _base_event_execution_summary(stdout, elapsed_seconds)
    messages = "\n".join(base.agent_messages(stdout))
    route_markers = re.findall(r"\[route:[^\]]+\]", messages, re.I)
    summary["route_markers"] = route_markers
    summary["specialized_workflow_observed"] = bool(
        re.search(r"router\s*→\s*(?:debugging|implement|verification)", messages, re.I)
    )
    return summary


base.event_execution_summary = event_execution_summary


def wayfinder_treatment_observation(
    condition: str,
    workspace: Path,
    changed: Iterable[str],
    execution: dict[str, Any],
) -> dict[str, Any]:
    all_paths = sorted(base.snapshot(workspace))
    state_files = [path for path in all_paths if path.startswith(".wayfinder/")]
    changed_state_files = sorted(
        path for path in changed if path.startswith(".wayfinder/")
    )
    alternate_paths = [
        path
        for path in all_paths
        if path.startswith(".scratch/")
        or path in {".wayfinder/active.md", ".agent-workflow/state/active.md"}
    ]
    observation = dict(execution.get("wayfinder_observation") or {})
    state_read = bool(state_files) and bool(observation.get("wayfinder_state_read"))
    phase = int(execution.get("phase", 0))
    explicit_prompt = condition == "C" and phase in {1, 3}
    definitive = bool(changed_state_files or state_read)
    return {
        "condition": condition,
        "phase": phase,
        "prompt_explicitly_invoked_wayfinder": explicit_prompt,
        "wayfinder_skill_read": observation.get("wayfinder_skill_read"),
        "wayfinder_state_present": bool(state_files),
        "wayfinder_state_files": state_files,
        "wayfinder_state_created_or_modified_this_phase": changed_state_files,
        "wayfinder_state_read": state_read,
        "route_to_wayfinder_self_reported": observation.get("route_to_wayfinder_self_reported"),
        "automatic_wayfinder_exercised": condition == "B" and definitive,
        "explicit_wayfinder_exercised": condition == "C" and explicit_prompt and definitive,
        "vanilla_treatment_contamination": condition == "A" and definitive,
        "alternate_local_state_paths": alternate_paths,
        "specialized_workflow_observed": execution.get("specialized_workflow_observed"),
        "route_markers": execution.get("route_markers", []),
        "instrumentation_note": (
            "State creation/read is definitive. Route self-report and skill reads are supporting evidence only."
        ),
    }


base.treatment_crossover = wayfinder_treatment_observation
_base_finalize_result = base.finalize_result


def finalize_result(
    state: dict[str, Any],
    *,
    results_root: Path = RESULTS_ROOT,
    run_root: Path = RUN_ROOT,
) -> Path:
    path = _base_finalize_result(state, results_root=results_root, run_root=run_root)
    result = base.read_json(path)
    phases = [result[f"phase_{number}"] for number in range(1, 5)]
    observations = [phase.get("treatment_crossover", {}) for phase in phases]
    workspace = Path(state["workspace"])
    all_paths = sorted(base.snapshot(workspace))
    state_files = [path for path in all_paths if path.startswith(".wayfinder/")]
    maps = [path for path in state_files if path.endswith("/map.md")]
    unknowns = [path for path in state_files if "/unknowns/U" in path]
    decisions = [path for path in state_files if "/decisions/D" in path]
    tickets = [path for path in state_files if "/tickets/T" in path]
    condition = str(result["condition"])
    automatic = condition == "B" and bool(
        observations[0].get("automatic_wayfinder_exercised")
    )
    explicit = condition == "C" and bool(
        observations[0].get("explicit_wayfinder_exercised")
    )
    resume = condition in {"B", "C"} and any(
        observation.get("wayfinder_state_read") for observation in observations[1:]
    )
    reconciliation = condition in {"B", "C"} and bool(
        observations[2].get("wayfinder_state_created_or_modified_this_phase")
    )
    alternate = sorted(
        {
            path
            for observation in observations
            for path in observation.get("alternate_local_state_paths", [])
        }
    )
    result.pop("treatment_crossover", None)
    result["wayfinder_treatment"] = {
        "automatic_selection_exercised": automatic,
        "explicit_selection_exercised": explicit,
        "fresh_process_resume_exercised": resume,
        "phase_3_reconciliation_exercised": reconciliation,
        "vanilla_treatment_contamination": any(
            observation.get("vanilla_treatment_contamination") for observation in observations
        ),
        "canonical_state_files": state_files,
        "map_files": maps,
        "unknown_files": unknowns,
        "decision_files": decisions,
        "ticket_files": tickets,
        "alternate_local_state_paths": alternate,
        "by_phase": {str(index): value for index, value in enumerate(observations, start=1)},
        "mechanism_gate_passed": (
            not state_files and not alternate
            if condition == "A"
            else bool(maps) and not alternate and resume and reconciliation and (automatic or explicit)
        ),
    }
    executions = list(state.get("executions", []))
    result["cost"] = {
        key: sum(
            value
            for item in executions
            if isinstance((value := item.get(key)), (int, float))
        )
        for key in (
            "elapsed_seconds",
            "tool_action_count",
            "input_tokens",
            "cached_input_tokens",
            "output_tokens",
            "reasoning_tokens",
        )
    }
    result["cost"]["phase_count"] = len(executions)
    base.write_json(path, result)
    return path


base.finalize_result = finalize_result


def nested(value: dict[str, Any], dotted: str) -> Any:
    current: Any = value
    for part in dotted.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def comparison_text(results_root: Path = RESULTS_ROOT) -> str:
    results = {str(item["condition"]): item for item in base.completed_results(results_root)}
    if set(results) != set(base.CONDITIONS):
        return "The A/B/C smoke is not complete.\n"
    lines = [
        "# Wayfinder local-state smoke v1 comparison",
        "",
        "No overall score is computed. Vanilla receives full credit for equivalent behavior.",
        "",
        "| Evidence | A vanilla | B automatic | C explicit |",
        "| --- | --- | --- | --- |",
    ]
    rows = (
        ("Phase 1 exact fact preserved", "phase_1.state_quality.exact_fact_preserved"),
        ("Phase 1 mapping-only respected", "phase_1.mapping_only_respected"),
        ("Phase 2 exact fact consumed", "phase_2.continuity.exact_fact_trusted_or_consumed"),
        ("Phase 2 safe SSM progress", "phase_2.safe_progress.ssm"),
        ("Phase 3 mapping-only respected", "phase_3.mapping_only_respected"),
        ("Phase 4 production slice complete", "phase_4.production_readiness_slice_complete"),
        ("Mechanism gate passed", "wayfinder_treatment.mechanism_gate_passed"),
    )
    for label, dotted in rows:
        values = [str(nested(results[condition], dotted)) for condition in base.CONDITIONS]
        lines.append(f"| {label} | {' | '.join(values)} |")
    lines.extend(["", "## Cost", "", "| Condition | Seconds | Tool actions | Input tokens | Output tokens |"])
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for condition in base.CONDITIONS:
        cost = dict(results[condition].get("cost", {}))
        sums = [
            cost.get(key, 0)
            for key in ("elapsed_seconds", "tool_action_count", "input_tokens", "output_tokens")
        ]
        lines.append(f"| {condition} | {sums[0]:.1f} | {int(sums[1])} | {int(sums[2])} | {int(sums[3])} |")
    lines.append("")
    return "\n".join(lines)


base.comparison_text = comparison_text


def self_check() -> int:
    manifest = base.campaign()
    if manifest["prompts"]["A"] != manifest["prompts"]["B"]:
        raise RuntimeError("A and B prompts must be byte-identical")
    if any("$wayfinder" in prompt for prompt in manifest["prompts"]["B"].values()):
        raise RuntimeError("automatic condition B must not name Wayfinder")
    if [phase for phase, prompt in manifest["prompts"]["C"].items() if "$wayfinder" in prompt] != ["1", "3"]:
        raise RuntimeError("explicit condition C must invoke Wayfinder only in phases 1 and 3")
    skill = (SOURCE_ROOT / ".agents/skills/wayfinder/SKILL.md").read_text(encoding="utf-8")
    if skill.count("agentic-workflow:wayfinder-local-state-v1:begin") != 1:
        raise RuntimeError("the product under test lacks exactly one local-state adapter")
    with tempfile.TemporaryDirectory(prefix="wayfinder-smoke-self-check-") as temporary:
        workspace = Path(temporary) / "repo"
        shutil.copytree(base.FIXTURE_ROOT, workspace)
        validation = base.run_fixture_validation(workspace)
        if not validation["passed"]:
            raise RuntimeError("fixture validation is not initially green")
    print(f"OK: {CAMPAIGN_ID} deterministic self-check passed ({len(critical_paths())} frozen files).")
    return 0


def phase_one_gate() -> int:
    trio = base.load_trio()
    failures: list[str] = []
    for condition in base.CONDITIONS:
        state = base.load_state(str(trio["runs"][condition]))
        phase_one = state.get("phase_results", {}).get("1", {})
        exercised = bool(phase_one.get("wayfinder", {}).get("exercised"))
        if condition == "A" and exercised:
            failures.append("A was contaminated by Wayfinder state")
        if condition in {"B", "C"} and not exercised:
            failures.append(f"{condition} did not create Wayfinder state in phase 1")
        workspace = Path(state["workspace"])
        alternate = [
            path
            for path in base.snapshot(workspace)
            if path.startswith(".scratch/") or path.endswith("/active.md")
        ]
        if alternate:
            failures.append(f"{condition} created alternate state: {', '.join(alternate)}")
    if failures:
        print("STOP: phase-1 mechanism gate failed: " + "; ".join(failures), file=sys.stderr)
        return 1
    print("OK: phase-1 mechanism gate passed; B automatic and C explicit local state were exercised.")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments == ["--self-check"]:
        return self_check()
    if arguments == ["--gate-phase-one"]:
        return phase_one_gate()
    return base.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
