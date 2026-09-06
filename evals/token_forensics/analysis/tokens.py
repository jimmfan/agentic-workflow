"""Token accounting over normalized observations."""

from __future__ import annotations

from typing import Any

from ..models import NormalizedTrace, UsageObservation


_TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


def _same_counters(left: UsageObservation, right: UsageObservation) -> bool:
    return all(getattr(left, field) == getattr(right, field) for field in _TOKEN_FIELDS)


def _deduplicate_snapshots(
    observations: list[UsageObservation],
) -> list[UsageObservation]:
    result: list[UsageObservation] = []
    for observation in observations:
        if result and _same_counters(result[-1], observation):
            continue
        result.append(observation)
    return result


def _sum_complete(observations: list[UsageObservation], field: str) -> int | None:
    if not observations or any(getattr(item, field) is None for item in observations):
        return None
    return sum(int(getattr(item, field)) for item in observations)


def _cumulative_value(
    observations: list[UsageObservation], field: str, warnings: list[dict[str, Any]]
) -> int | None:
    values = [getattr(item, field) for item in observations]
    if not values or any(value is None for value in values):
        return None
    numeric = [int(value) for value in values]
    if any(current < previous for previous, current in zip(numeric, numeric[1:])):
        warnings.append(
            {
                "code": "non_monotonic_cumulative_tokens",
                "category": "measured",
                "message": f"Cumulative {field} decreased; a safe run total is unavailable.",
            }
        )
        return None
    return numeric[-1]


def _point(
    observation: UsageObservation, cumulative: dict[str, int | None]
) -> dict[str, Any]:
    return {
        "observation": observation.sequence,
        "line": observation.line_number,
        "input_tokens": cumulative["input_tokens"],
        "cached_input_tokens": cumulative["cached_input_tokens"],
        "output_tokens": cumulative["output_tokens"],
    }


def analyze_tokens(
    trace: NormalizedTrace,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    warnings: list[dict[str, Any]] = []
    per_turn = [
        item for item in trace.usage_observations if item.semantics == "per_turn"
    ]
    cumulative = _deduplicate_snapshots(
        [
            item
            for item in trace.usage_observations
            if item.semantics == "cumulative_snapshot"
        ]
    )

    if per_turn and cumulative:
        warnings.append(
            {
                "code": "mixed_usage_semantics",
                "category": "measured",
                "message": "Trace mixes per-turn and cumulative usage; totals are unavailable to avoid double-counting.",
            }
        )
        selected: list[UsageObservation] = []
        accounting = "mixed-unavailable"
        totals = {field: None for field in _TOKEN_FIELDS}
    elif cumulative:
        selected = cumulative
        accounting = (
            "final monotonic cumulative snapshot; repeated snapshots deduplicated"
        )
        totals = {
            field: _cumulative_value(selected, field, warnings)
            for field in _TOKEN_FIELDS
        }
    else:
        selected = per_turn
        accounting = "sum of per-turn usage observations"
        totals = {field: _sum_complete(selected, field) for field in _TOKEN_FIELDS}

    measured = {
        "input": totals["input_tokens"],
        "cached_input": totals["cached_input_tokens"],
        "cache_write_input": totals["cache_write_input_tokens"],
        "output": totals["output_tokens"],
        "reasoning_output": totals["reasoning_output_tokens"],
        "accounting": accounting,
        "usage_observations": len(selected),
        "raw_usage_observations": len(trace.usage_observations),
    }

    input_tokens = totals["input_tokens"]
    cached_tokens = totals["cached_input_tokens"]
    if (
        input_tokens is not None
        and cached_tokens is not None
        and cached_tokens <= input_tokens
    ):
        uncached = input_tokens - cached_tokens
        cached_ratio = cached_tokens / input_tokens if input_tokens else None
    else:
        uncached = None
        cached_ratio = None
        if input_tokens is not None and cached_tokens is not None:
            warnings.append(
                {
                    "code": "cached_input_exceeds_input",
                    "category": "measured",
                    "message": "Cached input exceeds total input; uncached input and ratio are unavailable.",
                }
            )

    trajectory: list[dict[str, Any]] = []
    running = {field: 0 for field in _TOKEN_FIELDS}
    for observation in selected:
        if observation.semantics == "per_turn":
            for field in _TOKEN_FIELDS:
                value = getattr(observation, field)
                if running[field] is not None and value is not None:
                    running[field] = int(running[field]) + value
                else:
                    running[field] = None
            trajectory.append(_point(observation, running))
        else:
            current = {field: getattr(observation, field) for field in _TOKEN_FIELDS}
            trajectory.append(_point(observation, current))

    increases: list[dict[str, Any]] = []
    for previous, current in zip(trajectory, trajectory[1:]):
        before = previous["input_tokens"]
        after = current["input_tokens"]
        if before is None or after is None or after < before:
            continue
        increases.append(
            {
                "from_observation": previous["observation"],
                "to_observation": current["observation"],
                "input_increase": after - before,
                "cached_input_increase": (
                    current["cached_input_tokens"] - previous["cached_input_tokens"]
                    if current["cached_input_tokens"] is not None
                    and previous["cached_input_tokens"] is not None
                    and current["cached_input_tokens"]
                    >= previous["cached_input_tokens"]
                    else None
                ),
            }
        )
    increases.sort(key=lambda item: item["input_increase"], reverse=True)

    derived = {
        "uncached_input": uncached,
        "cached_input_ratio": cached_ratio,
        "token_trajectory": trajectory,
        "largest_input_increases": increases[:10],
    }
    return measured, derived, warnings
