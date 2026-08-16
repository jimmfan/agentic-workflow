#!/usr/bin/env python3
"""Aggregate the frozen ITBench Wayfinder campaign without changing its graders."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import statistics
from typing import Any


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
OUTPUT = ROOT / "reports" / "results-summary.json"
CONDITIONS = ("A", "B", "C")
SCENARIOS = (102, 34, 83, 17, 24, 80)


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def observation_value(value: Any) -> Any:
    if not isinstance(value, dict):
        return None
    for key in ("assessment", "value", "rating", "status"):
        if key in value:
            return value[key]
    return None


def normalized_wayfinder_key(key: str) -> str:
    if "duplicated" in key:
        return "duplicated_debugging_process_overhead"
    if "dependency_representation" in key:
        return "dependency_representation"
    if "meaningful_unknowns" in key:
        return "meaningful_unknowns"
    return key


def load_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((RESULTS / "runs").glob("*/execution.json")):
        execution = read(path)
        run_id = str(execution["run_id"])
        native = read(RESULTS / "grades" / run_id / "native.json")
        reasoning_artifact = read(RESULTS / "grades" / run_id / "reasoning.json")
        if reasoning_artifact.get("validation_errors"):
            raise RuntimeError(f"invalid reasoning grade: {run_id}")
        usage = execution.get("summary", {}).get("usage", {})
        rows.append({
            "run_id": run_id,
            "scenario": execution["scenario"],
            "condition": execution["condition"],
            "repetition": execution["repetition"],
            "exit_status": execution["exit_status"],
            "diagnosis_valid_json_object": execution["diagnosis_valid_json_object"],
            "elapsed_seconds": execution["elapsed_seconds"],
            "input_tokens": usage.get("input_tokens", 0),
            "cached_input_tokens": usage.get("cached_input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "tool_actions": execution.get("summary", {}).get("tool_action_count", 0),
            "capabilities": execution.get("capabilities", {}),
            "native_score": native["native_score"],
            "native_success": native["success"],
            "native_missing_root_group_ids": native["missing_root_group_ids"],
            "native_predictions": native["predictions"],
            "reasoning_dimensions": reasoning_artifact["grade"]["dimensions"],
            "wayfinder_observations": reasoning_artifact["grade"].get("wayfinder"),
            "domain_modeling_observations": reasoning_artifact["grade"].get("domain_modeling"),
            "reasoning_grader_elapsed_seconds": reasoning_artifact["elapsed_seconds"],
            "reasoning_grader_ground_truth_supplied": reasoning_artifact.get(
                "ground_truth_supplied_to_reasoning_grader"
            ),
        })
    return rows


def numeric_summary(values: list[float | int]) -> dict[str, Any]:
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "minimum": min(values),
        "maximum": max(values),
        "sum": sum(values),
    }


def condition_summary(rows: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    selected = [row for row in rows if row["condition"] == condition]
    capability_names = ("wayfinder", "domain-modeling", "debugging", "research", "discovery", "verification")
    return {
        "runs": len(selected),
        "normal_exits": sum(row["exit_status"] == 0 for row in selected),
        "valid_diagnoses": sum(row["diagnosis_valid_json_object"] for row in selected),
        "native_mean": statistics.mean(row["native_score"] for row in selected),
        "native_successes": sum(row["native_success"] for row in selected),
        "elapsed_seconds": numeric_summary([row["elapsed_seconds"] for row in selected]),
        "input_tokens": numeric_summary([row["input_tokens"] for row in selected]),
        "cached_input_tokens": numeric_summary([row["cached_input_tokens"] for row in selected]),
        "output_tokens": numeric_summary([row["output_tokens"] for row in selected]),
        "tool_actions": numeric_summary([row["tool_actions"] for row in selected]),
        "capability_invocations": {
            name: sum(bool(row["capabilities"].get(name, {}).get("invoked")) for row in selected)
            for name in capability_names
        },
        "route_marker_runs": sum(bool(row["capabilities"].get("route_markers")) for row in selected),
    }


def native_pairwise(rows: list[dict[str, Any]], left: str, right: str) -> dict[str, Any]:
    differences: list[float] = []
    for scenario in SCENARIOS:
        for repetition in (1, 2, 3):
            left_score = next(
                row["native_score"] for row in rows
                if row["scenario"] == scenario and row["repetition"] == repetition and row["condition"] == left
            )
            right_score = next(
                row["native_score"] for row in rows
                if row["scenario"] == scenario and row["repetition"] == repetition and row["condition"] == right
            )
            differences.append(right_score - left_score)
    return {
        "contrast": f"{right}-{left}",
        "mean_difference": statistics.mean(differences),
        "right_wins": sum(value > 0 for value in differences),
        "ties": sum(value == 0 for value in differences),
        "right_losses": sum(value < 0 for value in differences),
    }


def reasoning_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    dimensions = list(rows[0]["reasoning_dimensions"])
    result: dict[str, Any] = {}
    for dimension in dimensions:
        by_condition: dict[str, Any] = {}
        for condition in CONDITIONS:
            values = [
                row["reasoning_dimensions"][dimension]["score"]
                for row in rows
                if row["condition"] == condition
                and row["reasoning_dimensions"][dimension]["score"] is not None
            ]
            by_condition[condition] = {
                "non_null_n": len(values),
                "mean": statistics.mean(values) if values else None,
                "distribution": {str(score): values.count(score) for score in (0, 1, 2)},
            }
        result[dimension] = {
            "conditions": by_condition,
            "mean_differences": {
                "B-A": (
                    by_condition["B"]["mean"] - by_condition["A"]["mean"]
                    if by_condition["B"]["mean"] is not None and by_condition["A"]["mean"] is not None else None
                ),
                "C-B": (
                    by_condition["C"]["mean"] - by_condition["B"]["mean"]
                    if by_condition["C"]["mean"] is not None and by_condition["B"]["mean"] is not None else None
                ),
                "C-A": (
                    by_condition["C"]["mean"] - by_condition["A"]["mean"]
                    if by_condition["C"]["mean"] is not None and by_condition["A"]["mean"] is not None else None
                ),
            },
        }
    return result


def wayfinder_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, Counter[Any]] = {}
    for row in rows:
        observations = row["wayfinder_observations"]
        if not isinstance(observations, dict):
            continue
        for key, value in observations.items():
            normalized = normalized_wayfinder_key(key)
            counts.setdefault(normalized, Counter())[observation_value(value)] += 1
    return {key: dict(value) for key, value in sorted(counts.items())}


def main() -> int:
    rows = load_rows()
    if len(rows) != 54:
        raise RuntimeError(f"expected 54 runs, found {len(rows)}")
    value = {
        "campaign_id": "itbench-wayfinder-v1",
        "run_counts": {
            "total": len(rows),
            "normal_exits": sum(row["exit_status"] == 0 for row in rows),
            "valid_diagnoses": sum(row["diagnosis_valid_json_object"] for row in rows),
            "native_successes": sum(row["native_success"] for row in rows),
            "valid_reasoning_grades": len(rows),
        },
        "total_diagnostic_elapsed_seconds": sum(row["elapsed_seconds"] for row in rows),
        "summed_reasoning_grader_elapsed_seconds": sum(row["reasoning_grader_elapsed_seconds"] for row in rows),
        "conditions": {condition: condition_summary(rows, condition) for condition in CONDITIONS},
        "native_pairwise": {
            "A_vs_B": native_pairwise(rows, "A", "B"),
            "B_vs_C": native_pairwise(rows, "B", "C"),
            "A_vs_C": native_pairwise(rows, "A", "C"),
        },
        "native_by_scenario": {
            str(scenario): {
                condition: [
                    row["native_score"] for row in rows
                    if row["scenario"] == scenario and row["condition"] == condition
                ]
                for condition in CONDITIONS
            }
            for scenario in SCENARIOS
        },
        "reasoning_dimensions": reasoning_summary(rows),
        "wayfinder_observation_counts": wayfinder_summary(rows),
        "domain_modeling_observed_runs": sum(
            row["domain_modeling_observations"] is not None for row in rows
        ),
        "reasoning_grader_ground_truth_supplied_runs": sum(
            row["reasoning_grader_ground_truth_supplied"] is True for row in rows
        ),
        "per_run": rows,
    }
    write(OUTPUT, value)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
