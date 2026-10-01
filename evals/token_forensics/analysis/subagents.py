"""Summarize multi-agent tool calls without inferring unrecorded settings."""

from __future__ import annotations

from collections import Counter
from statistics import median
from typing import Any

from ..models import AgentToolCall, NormalizedTrace

# Codex multi-agent defaults at openai/codex 60947e2 (2026-09-30):
# V2 `spawn_agent` treats a missing `fork_turns` as "all" (full parent history);
# V1 (`multi_agent_v1` namespace) treats a missing `fork_context` as false.
_V1_NAMESPACE = "multi_agent_v1"


def _fork_mode(call: AgentToolCall) -> str:
    if call.source != "rollout_function_call":
        return "unavailable"
    if call.arguments_parsed is False:
        return "unavailable"
    if call.fork_context is not None:
        return "full_history" if call.fork_context else "none"
    if call.fork_turns is not None:
        value = call.fork_turns.strip().casefold()
        if value == "none":
            return "none"
        if value in {"", "all"}:
            return "full_history"
        if value.isdigit() and int(value) > 0:
            return "last_n_turns"
        return "invalid"
    if call.namespace == _V1_NAMESPACE:
        return "none"
    return "full_history_default"


def _is_spawn(call: AgentToolCall) -> bool:
    return call.tool == "spawn_agent"


def _is_wait(call: AgentToolCall) -> bool:
    # The exec stream reports V1 `wait_agent`, V2 `wait_agent`, and
    # `resume_agent` all as `wait`.
    return call.tool in {"wait", "wait_agent"}


def _explicit_count(calls: list[AgentToolCall], field: str) -> int | None:
    if not calls:
        return 0
    observable = [
        call
        for call in calls
        if call.source == "rollout_function_call" and call.arguments_parsed
    ]
    if not observable or len(observable) != len(calls):
        return None
    return sum(1 for call in observable if getattr(call, field) is not None)


def analyze_subagents(
    trace: NormalizedTrace,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    calls = trace.agent_tool_calls
    sources = sorted({call.source for call in calls})
    spawns = [call for call in calls if _is_spawn(call)]
    waits = [call for call in calls if _is_wait(call)]
    other = Counter(
        call.tool for call in calls if not _is_spawn(call) and not _is_wait(call)
    )

    prompt_sizes = [call.prompt_bytes for call in spawns]
    known_prompts = [size for size in prompt_sizes if size is not None]
    fork_modes = Counter(_fork_mode(call) for call in spawns)

    nested: int | None = None
    exec_spawns = [call for call in spawns if call.source == "exec_collab_item"]
    if exec_spawns and trace.thread_id is not None:
        nested = sum(
            1
            for call in exec_spawns
            if call.sender_thread_id is not None
            and call.sender_thread_id != trace.thread_id
        )

    rollout_waits = [call for call in waits if call.source == "rollout_function_call"]
    timed_out: int | None = None
    if waits and len(rollout_waits) == len(waits):
        known = [call.timed_out for call in rollout_waits]
        if all(value is not None for value in known):
            timed_out = sum(1 for value in known if value)
    requested = [call.timeout_ms for call in rollout_waits]
    requested_known = [value for value in requested if value is not None]
    requested_summary: dict[str, Any] | None = None
    if rollout_waits and len(rollout_waits) == len(waits):
        requested_summary = {
            "unset": sum(1 for value in requested if value is None),
            "min": min(requested_known) if requested_known else None,
            "median": median(requested_known) if requested_known else None,
            "max": max(requested_known) if requested_known else None,
        }

    summary = {
        "observed_calls": len(calls),
        "sources": sources,
        "spawns": {
            "count": len(spawns),
            "prompt_bytes_total": sum(known_prompts)
            if len(known_prompts) == len(spawns)
            else None,
            "prompt_bytes_max": max(known_prompts) if known_prompts else None,
            "explicit_model": _explicit_count(spawns, "model"),
            "explicit_reasoning_effort": _explicit_count(spawns, "reasoning_effort"),
            "fork_modes": dict(sorted(fork_modes.items())),
            "spawned_by_other_threads": nested,
        },
        "waits": {
            "count": len(waits),
            "timed_out": timed_out,
            "requested_timeout_ms": requested_summary,
        },
        "other_agent_tools": dict(sorted(other.items())),
        "calls": [
            {
                "line": call.line_number,
                "source": call.source,
                "tool": call.tool,
                "namespace": call.namespace,
                "prompt_bytes": call.prompt_bytes,
                "model": call.model,
                "reasoning_effort": call.reasoning_effort,
                "fork_mode": _fork_mode(call) if _is_spawn(call) else None,
                "timeout_ms": call.timeout_ms,
                "timed_out": call.timed_out,
                "sender_thread_id": call.sender_thread_id,
                "receiver_thread_ids": list(call.receiver_thread_ids),
            }
            for call in calls
        ],
    }

    warnings: list[dict[str, str]] = []
    full_history = fork_modes.get("full_history", 0) + fork_modes.get(
        "full_history_default", 0
    )
    if full_history:
        warnings.append(
            {
                "code": "full_history_spawn",
                "category": "measured",
                "message": f"{full_history} of {len(spawns)} spawn(s) forked the parent's full history, explicitly or by the V2 default.",
            }
        )
    missing_model = summary["spawns"]["explicit_model"]
    if missing_model is not None and missing_model < len(spawns):
        warnings.append(
            {
                "code": "spawn_without_model",
                "category": "measured",
                "message": f"{len(spawns) - missing_model} of {len(spawns)} spawn(s) did not set a model explicitly.",
            }
        )
    if timed_out:
        warnings.append(
            {
                "code": "wait_timeouts",
                "category": "measured",
                "message": f"{timed_out} of {len(waits)} wait call(s) timed out.",
            }
        )
    if nested:
        warnings.append(
            {
                "code": "nested_spawn",
                "category": "measured",
                "message": f"{nested} spawn(s) were issued by a thread other than the traced root thread.",
            }
        )
    return summary, warnings


__all__ = ["analyze_subagents"]
