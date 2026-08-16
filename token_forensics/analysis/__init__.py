"""Compose generic forensic analyses over a normalized trace."""

from __future__ import annotations

from typing import Any

from ..models import NormalizedTrace, Thresholds
from .context import analyze_context
from .tokens import analyze_tokens
from .tools import analyze_tools


def _limitations(trace: NormalizedTrace) -> list[str]:
    limitations = [
        "Tool-output bytes are bytes in trace payloads, not token counts.",
        "Individual tool outputs cannot be assigned exact later input-token costs from these events.",
        "Repository reads and framework activity are inferred from commands and file-change events, not a complete filesystem audit.",
    ]
    if trace.source_format == "codex-exec-jsonl":
        limitations.extend(
            [
                "turn.completed usage is per Codex turn and aggregates internal model calls; internal model-call count is unavailable.",
                "command_execution exposes aggregated_output, so tool stdout and stderr cannot be separated.",
                "context compaction is not exposed by this exec event stream unless an explicit compaction event appears.",
            ]
        )
    if trace.source_format == "codex-rollout-jsonl":
        limitations.append(
            "Rollout token_count events are cumulative snapshots and may be repeated; only monotonic distinct snapshots are used."
        )
    return limitations


def analyze_trace(trace: NormalizedTrace, thresholds: Thresholds | None = None) -> dict[str, Any]:
    configured = thresholds or Thresholds()
    measured_tokens, derived_tokens, token_warnings = analyze_tokens(trace)
    measured_tools, derived_tools, tool_warnings = analyze_tools(trace, configured)
    _repository, heuristic, context_warnings = analyze_context(trace, configured)

    compaction_observable = trace.source_format in {"codex-rollout-jsonl", "codex-mixed-jsonl"}
    context_compactions: int | None
    if trace.compactions:
        context_compactions = len(trace.compactions)
    elif compaction_observable:
        context_compactions = 0
    else:
        context_compactions = None

    trajectory = {
        "codex_turns_started": trace.codex_turns_started,
        "codex_turns_completed": trace.codex_turns_completed,
        "internal_model_calls": None,
        "context_compactions": context_compactions,
        "compaction_observability": "rollout-events" if compaction_observable else "unavailable",
        "compaction_events": [
            {"line": item.line_number, "event_type": item.event_type} for item in trace.compactions
        ],
    }
    warnings = token_warnings + tool_warnings + context_warnings
    if trace.codex_turns_completed >= configured.long_codex_turn_count:
        warnings.append(
            {
                "code": "long_trajectory",
                "category": "measured",
                "message": f"Trace contains {trace.codex_turns_completed} completed Codex turns.",
            }
        )
    if trace.compactions:
        warnings.append(
            {
                "code": "context_compaction",
                "category": "measured",
                "message": f"Trace contains {len(trace.compactions)} explicit context compaction event(s).",
            }
        )
    for warning in trace.parse_warnings:
        warnings.append({"code": "parse_warning", "category": "measured", "message": warning})

    return {
        "schema_version": "token-forensics/v1",
        "source": {
            "format": trace.source_format,
            "path": str(trace.source_path),
            "bytes": trace.source_bytes,
            "thread_id": trace.thread_id,
            "event_type_counts": trace.event_type_counts,
            "limitations": _limitations(trace),
        },
        "measured": {
            "tokens": measured_tokens,
            "trajectory": trajectory,
            "tools": measured_tools,
        },
        "derived": {
            "tokens": derived_tokens,
            "tools": derived_tools,
        },
        "heuristic": heuristic,
        "warnings": warnings,
    }


__all__ = ["analyze_trace"]
