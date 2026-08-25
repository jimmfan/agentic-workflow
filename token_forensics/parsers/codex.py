"""Normalize Codex exec event streams and persisted rollout JSONL."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from ..models import CompactionEvent, NormalizedTrace, ToolInvocation, UsageObservation


_EXEC_EVENT_TYPES = {
    "thread.started",
    "turn.started",
    "turn.completed",
    "turn.failed",
    "item.started",
    "item.updated",
    "item.completed",
    "error",
}
_TOOL_ITEM_TYPES = {
    "collab_tool_call",
    "command_execution",
    "file_change",
    "mcp_tool_call",
    "plan_update",
    "web_search",
}


def _nonnegative_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _byte_length(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    try:
        rendered = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return None
    return len(rendered.encode("utf-8"))


def _usage(
    value: Any,
    *,
    sequence: int,
    line_number: int,
    semantics: str,
    model_context_window: Any = None,
) -> UsageObservation | None:
    if not isinstance(value, dict):
        return None
    return UsageObservation(
        sequence=sequence,
        line_number=line_number,
        semantics=semantics,  # type: ignore[arg-type]
        input_tokens=_nonnegative_int(value.get("input_tokens")),
        cached_input_tokens=_nonnegative_int(value.get("cached_input_tokens")),
        cache_write_input_tokens=_nonnegative_int(
            value.get("cache_write_input_tokens")
        ),
        output_tokens=_nonnegative_int(value.get("output_tokens")),
        reasoning_output_tokens=_nonnegative_int(value.get("reasoning_output_tokens")),
        model_context_window=_nonnegative_int(model_context_window),
    )


def _changed_paths(item: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    changes = item.get("changes")
    if not isinstance(changes, list):
        return ()
    result: list[tuple[str, str]] = []
    for change in changes:
        if not isinstance(change, dict) or not isinstance(change.get("path"), str):
            continue
        result.append((str(change.get("kind") or "change"), change["path"]))
    return tuple(result)


def _tool_invocation(item: dict[str, Any], *, sequence: int) -> ToolInvocation | None:
    item_type = item.get("type")
    if not isinstance(item_type, str) or item_type not in _TOOL_ITEM_TYPES:
        return None
    identifier = item.get("id")
    invocation_id = str(identifier) if identifier is not None else f"line-{sequence}"

    command: str | None = None
    name = item_type
    if isinstance(item.get("command"), str):
        command = item["command"]
    elif item_type == "mcp_tool_call":
        server = item.get("server") or item.get("server_name")
        tool = item.get("tool") or item.get("tool_name")
        name = ".".join(str(part) for part in (server, tool) if part) or item_type
        command = name
    elif item_type == "web_search" and isinstance(item.get("query"), str):
        name = "web_search"
        command = item["query"]
    elif item_type == "collab_tool_call":
        name = str(item.get("tool") or item.get("name") or item_type)
        command = name

    stdout_bytes = _byte_length(item.get("stdout"))
    stderr_bytes = _byte_length(item.get("stderr"))
    combined_output_bytes: int | None = None
    if stdout_bytes is None and stderr_bytes is None:
        for key in ("aggregated_output", "result", "output", "error"):
            if key in item and item.get(key) is not None:
                combined_output_bytes = _byte_length(item.get(key))
                break

    status = str(item["status"]) if item.get("status") is not None else None
    exit_code = item.get("exit_code")
    if isinstance(exit_code, bool) or not isinstance(exit_code, int):
        exit_code = None
    return ToolInvocation(
        invocation_id=invocation_id,
        sequence=sequence,
        tool_type=item_type,
        name=name,
        command=command,
        status=status,
        exit_code=exit_code,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        combined_output_bytes=combined_output_bytes,
        duration_ms=_number(item.get("duration_ms")),
        changed_paths=_changed_paths(item),
    )


def _event_type(event: dict[str, Any]) -> str:
    top_level = event.get("type")
    payload = event.get("payload")
    if top_level == "event_msg" and isinstance(payload, dict):
        return f"event_msg/{payload.get('type', '<missing>')}"
    return str(top_level or "<missing>")


def parse_codex_trace(path: str | Path) -> NormalizedTrace:
    """Parse Codex JSONL without retaining raw tool output strings in memory."""

    source = Path(path)
    event_counts: Counter[str] = Counter()
    usage_observations: list[UsageObservation] = []
    compactions: list[CompactionEvent] = []
    messages: list[str] = []
    warnings: list[str] = []
    tool_items: dict[str, ToolInvocation] = {}
    tool_order: list[str] = []
    saw_exec = False
    saw_rollout = False
    thread_id: str | None = None
    turns_started = 0
    turns_completed = 0
    sequence = 0

    with source.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                continue
            sequence += 1
            try:
                event = json.loads(raw_line)
            except json.JSONDecodeError as error:
                warnings.append(f"line {line_number}: invalid JSON ({error.msg})")
                continue
            if not isinstance(event, dict):
                warnings.append(f"line {line_number}: expected a JSON object")
                continue

            event_counts[_event_type(event)] += 1
            top_type = event.get("type")
            if top_type in _EXEC_EVENT_TYPES:
                saw_exec = True
            if top_type in {
                "event_msg",
                "response_item",
                "turn_context",
                "session_meta",
                "compacted",
            }:
                saw_rollout = True

            if top_type == "thread.started" and isinstance(event.get("thread_id"), str):
                thread_id = event["thread_id"]
            elif top_type == "turn.started":
                turns_started += 1
            elif top_type == "turn.completed":
                turns_completed += 1
                observation = _usage(
                    event.get("usage"),
                    sequence=turns_completed,
                    line_number=line_number,
                    semantics="per_turn",
                )
                if observation is None:
                    warnings.append(
                        f"line {line_number}: turn.completed has no usable usage object"
                    )
                else:
                    usage_observations.append(observation)

            if top_type in {"item.started", "item.updated", "item.completed"}:
                item = event.get("item")
                if isinstance(item, dict):
                    invocation = _tool_invocation(item, sequence=sequence)
                    if invocation is not None:
                        if invocation.invocation_id not in tool_items:
                            tool_order.append(invocation.invocation_id)
                        tool_items[invocation.invocation_id] = invocation
                    if (
                        top_type == "item.completed"
                        and item.get("type") == "agent_message"
                        and isinstance(item.get("text"), str)
                    ):
                        messages.append(item["text"])

            payload = event.get("payload")
            payload_type = payload.get("type") if isinstance(payload, dict) else None
            if top_type == "event_msg" and payload_type == "token_count":
                info = payload.get("info")
                if isinstance(info, dict):
                    observation = _usage(
                        info.get("total_token_usage"),
                        sequence=len(usage_observations) + 1,
                        line_number=line_number,
                        semantics="cumulative_snapshot",
                        model_context_window=info.get("model_context_window"),
                    )
                    if observation is not None:
                        usage_observations.append(observation)
            if top_type == "event_msg" and payload_type in {
                "task_started",
                "turn_started",
            }:
                turns_started += 1
            if top_type == "event_msg" and payload_type in {
                "task_complete",
                "turn_complete",
            }:
                turns_completed += 1

            compact_type: str | None = None
            if isinstance(top_type, str) and "compact" in top_type.casefold():
                compact_type = top_type
            elif isinstance(payload_type, str) and "compact" in payload_type.casefold():
                compact_type = f"event_msg/{payload_type}"
            if compact_type is not None:
                compactions.append(CompactionEvent(sequence, line_number, compact_type))

    if saw_exec and saw_rollout:
        source_format = "codex-mixed-jsonl"
    elif saw_rollout:
        source_format = "codex-rollout-jsonl"
    elif saw_exec:
        source_format = "codex-exec-jsonl"
    else:
        source_format = "codex-jsonl-unknown"
        warnings.append("no recognized Codex exec or rollout events were found")

    return NormalizedTrace(
        source_path=source,
        source_format=source_format,
        source_bytes=source.stat().st_size,
        thread_id=thread_id,
        event_type_counts=dict(sorted(event_counts.items())),
        codex_turns_started=turns_started,
        codex_turns_completed=turns_completed,
        usage_observations=usage_observations,
        tool_invocations=[tool_items[identifier] for identifier in tool_order],
        compactions=compactions,
        agent_messages=messages,
        parse_warnings=warnings,
    )
