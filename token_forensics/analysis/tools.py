"""Tool-call and tool-output analysis over normalized traces."""

from __future__ import annotations

from collections import Counter, defaultdict
from difflib import SequenceMatcher
import hashlib
import re
from typing import Any

from ..models import NormalizedTrace, Thresholds, ToolInvocation


_ABSOLUTE_PATH = re.compile(r"/(?:[^\s'\";|&<>]+/)*[^\s'\";|&<>]+")
_NUMBER = re.compile(r"\b\d+\b")


def _clip(value: str | None, limit: int = 500) -> str | None:
    if value is None or len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def _exact_key(command: str) -> str:
    return " ".join(command.split())


def _shape(command: str) -> str:
    value = _ABSOLUTE_PATH.sub("<path>", _exact_key(command))
    value = _NUMBER.sub("<n>", value)
    return value[:1000]


def _command_record(
    tool: ToolInvocation, *, count: int | None = None
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "tool_type": tool.tool_type,
        "command": _clip(tool.command),
        "command_sha256": hashlib.sha256(
            (tool.command or tool.name).encode()
        ).hexdigest(),
    }
    if count is not None:
        value["count"] = count
    return value


def _is_failed(tool: ToolInvocation) -> bool:
    return tool.exit_code not in {None, 0} or (tool.status or "").casefold() in {
        "failed",
        "error",
    }


def _repeated_exact(tools: list[ToolInvocation]) -> list[dict[str, Any]]:
    grouped: dict[str, list[ToolInvocation]] = defaultdict(list)
    for tool in tools:
        if tool.command:
            grouped[_exact_key(tool.command)].append(tool)
    result = []
    for group in grouped.values():
        if len(group) > 1:
            result.append(_command_record(group[0], count=len(group)))
    return sorted(result, key=lambda item: item["count"], reverse=True)


def _near_identical(tools: list[ToolInvocation]) -> list[dict[str, Any]]:
    candidates = [tool for tool in tools if tool.command]
    used: set[int] = set()
    groups: list[list[ToolInvocation]] = []
    for index, tool in enumerate(candidates):
        if index in used:
            continue
        exact = _exact_key(tool.command or "")
        shape = _shape(tool.command or "")
        group = [tool]
        for other_index in range(index + 1, len(candidates)):
            if other_index in used:
                continue
            other = candidates[other_index]
            if _exact_key(other.command or "") == exact:
                continue
            other_shape = _shape(other.command or "")
            if (
                shape == other_shape
                or SequenceMatcher(None, shape, other_shape).ratio() >= 0.94
            ):
                group.append(other)
                used.add(other_index)
        if len(group) > 1:
            used.add(index)
            groups.append(group)
    return [
        {
            "count": len(group),
            "commands": [_clip(tool.command, 300) for tool in group[:5]],
        }
        for group in sorted(groups, key=len, reverse=True)
    ]


def analyze_tools(
    trace: NormalizedTrace, thresholds: Thresholds
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    tools = trace.tool_invocations
    failures = [tool for tool in tools if _is_failed(tool)]
    largest = sorted(tools, key=lambda item: item.output_bytes, reverse=True)[:10]

    stdout_observable = bool(tools) and all(
        tool.stdout_bytes is not None for tool in tools
    )
    stderr_observable = bool(tools) and all(
        tool.stderr_bytes is not None for tool in tools
    )
    measured = {
        "calls": len(tools),
        "type_counts": dict(sorted(Counter(tool.tool_type for tool in tools).items())),
        "output_bytes": sum(tool.output_bytes for tool in tools),
        "stdout_bytes": sum(tool.stdout_bytes or 0 for tool in tools)
        if stdout_observable
        else None,
        "stderr_bytes": sum(tool.stderr_bytes or 0 for tool in tools)
        if stderr_observable
        else None,
        "combined_output_bytes": sum(tool.combined_output_bytes or 0 for tool in tools),
        "output_channel_note": (
            "stdout and stderr reported separately"
            if stdout_observable and stderr_observable
            else "Codex command_execution reports combined aggregated_output; stdout/stderr split unavailable"
        ),
        "largest_outputs": [
            {
                "invocation_id": tool.invocation_id,
                "tool_type": tool.tool_type,
                "command": _clip(tool.command),
                "output_bytes": tool.output_bytes,
                "stdout_bytes": tool.stdout_bytes,
                "stderr_bytes": tool.stderr_bytes,
                "combined_output_bytes": tool.combined_output_bytes,
            }
            for tool in largest
            if tool.output_bytes
        ],
        "failed_calls": [
            {
                "invocation_id": tool.invocation_id,
                "tool_type": tool.tool_type,
                "command": _clip(tool.command),
                "status": tool.status,
                "exit_code": tool.exit_code,
                "output_bytes": tool.output_bytes,
            }
            for tool in failures
        ],
        "duration_ms": {
            "available_calls": sum(tool.duration_ms is not None for tool in tools),
            "total": (
                sum(tool.duration_ms or 0 for tool in tools)
                if tools and all(tool.duration_ms is not None for tool in tools)
                else None
            ),
        },
    }

    exact = _repeated_exact(tools)
    near = _near_identical(tools)
    failed_exact = _repeated_exact(failures)
    failed_near = _near_identical(failures)
    derived = {
        "repeated_commands": exact,
        "near_identical_commands": near,
        "repeated_failed_commands": failed_exact,
        "near_identical_failed_commands": failed_near,
    }

    warnings: list[dict[str, Any]] = []
    for tool in tools:
        if tool.output_bytes >= thresholds.large_tool_output_bytes:
            warnings.append(
                {
                    "code": "large_tool_output",
                    "category": "measured",
                    "message": f"Tool output was {tool.output_bytes} bytes.",
                    "invocation_id": tool.invocation_id,
                    "command": _clip(tool.command, 240),
                }
            )
    if measured["output_bytes"] >= thresholds.large_total_tool_output_bytes:
        warnings.append(
            {
                "code": "large_cumulative_tool_output",
                "category": "measured",
                "message": f"Cumulative tool output was {measured['output_bytes']} bytes.",
            }
        )
    if len(tools) >= thresholds.high_tool_call_count:
        warnings.append(
            {
                "code": "high_tool_call_count",
                "category": "measured",
                "message": f"Trace contains {len(tools)} tool calls.",
            }
        )
    if any(item["count"] >= thresholds.repeated_command_count for item in exact):
        warnings.append(
            {
                "code": "repeated_command",
                "category": "derived",
                "message": "An identical command was repeated at least "
                f"{thresholds.repeated_command_count} times.",
            }
        )
    if any(
        item["count"] >= thresholds.repeated_failed_command_count
        for item in failed_exact
    ):
        warnings.append(
            {
                "code": "repeated_failed_command",
                "category": "derived",
                "message": "A failed command was repeated.",
            }
        )
    return measured, derived, warnings
