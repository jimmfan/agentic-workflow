"""Normalize Codex exec event streams and persisted rollout JSONL."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
from typing import Any

from ..models import (
    AgentToolCall,
    CompactionEvent,
    NormalizedTrace,
    ToolInvocation,
    UsageObservation,
)


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


# Multi-agent tool names registered by Codex (V1 under the `multi_agent_v1`
# namespace, V2 unnamespaced); see codex-rs/core/src/tools/handlers.
_AGENT_TOOL_NAMES = {
    "close_agent",
    "followup_task",
    "interrupt_agent",
    "list_agents",
    "resume_agent",
    "send_input",
    "send_message",
    "spawn_agent",
    "wait_agent",
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


def _exec_agent_call(
    item: dict[str, Any], *, sequence: int, line_number: int
) -> AgentToolCall | None:
    if item.get("type") != "collab_tool_call":
        return None
    receivers = item.get("receiver_thread_ids")
    states = item.get("agents_states")
    statuses: list[str] = []
    if isinstance(states, dict):
        for state in states.values():
            if isinstance(state, dict) and isinstance(state.get("status"), str):
                statuses.append(state["status"])
    return AgentToolCall(
        sequence=sequence,
        line_number=line_number,
        source="exec_collab_item",
        tool=str(item.get("tool") or "collab_tool_call"),
        call_id=str(item["id"]) if item.get("id") is not None else None,
        status=str(item["status"]) if item.get("status") is not None else None,
        sender_thread_id=item.get("sender_thread_id")
        if isinstance(item.get("sender_thread_id"), str)
        else None,
        receiver_thread_ids=tuple(
            str(receiver) for receiver in receivers if isinstance(receiver, str)
        )
        if isinstance(receivers, list)
        else (),
        agent_statuses=tuple(sorted(statuses)),
        prompt_bytes=_byte_length(item.get("prompt")),
    )


def _rollout_agent_call(
    payload: dict[str, Any], *, sequence: int, line_number: int
) -> AgentToolCall | None:
    name = payload.get("name")
    if payload.get("type") != "function_call" or name not in _AGENT_TOOL_NAMES:
        return None
    arguments: Any = None
    parsed = False
    raw_arguments = payload.get("arguments")
    if isinstance(raw_arguments, str):
        try:
            arguments = json.loads(raw_arguments)
            parsed = isinstance(arguments, dict)
        except json.JSONDecodeError:
            parsed = False
    if not parsed:
        arguments = {}
    prompt = arguments.get("message")
    if prompt is None and arguments.get("items") is not None:
        prompt = arguments.get("items")
    fork_turns = arguments.get("fork_turns")
    fork_context = arguments.get("fork_context")
    model = arguments.get("model")
    effort = arguments.get("reasoning_effort")
    namespace = payload.get("namespace")
    return AgentToolCall(
        sequence=sequence,
        line_number=line_number,
        source="rollout_function_call",
        tool=str(name),
        call_id=str(payload["call_id"]) if payload.get("call_id") is not None else None,
        namespace=namespace if isinstance(namespace, str) else None,
        prompt_bytes=_byte_length(prompt),
        arguments_parsed=parsed,
        model=model if isinstance(model, str) and model else None,
        reasoning_effort=effort if isinstance(effort, str) and effort else None,
        fork_turns=fork_turns if isinstance(fork_turns, str) else None,
        fork_context=fork_context if isinstance(fork_context, bool) else None,
        timeout_ms=_nonnegative_int(arguments.get("timeout_ms")),
    )


def _output_text(output: Any) -> str | None:
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        parts = [
            part["text"]
            for part in output
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        ]
        return "".join(parts) if parts else None
    return None


def _timed_out(output: Any) -> bool | None:
    text = _output_text(output)
    if text is None:
        return None
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(value, dict) and isinstance(value.get("timed_out"), bool):
        return value["timed_out"]
    return None


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
    agent_calls: dict[str, AgentToolCall] = {}
    agent_order: list[str] = []
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
                    agent_call = _exec_agent_call(
                        item, sequence=sequence, line_number=line_number
                    )
                    if agent_call is not None:
                        key = f"exec:{agent_call.call_id or f'line-{line_number}'}"
                        if key not in agent_calls:
                            agent_order.append(key)
                        else:
                            agent_call = replace(
                                agent_call,
                                sequence=agent_calls[key].sequence,
                                line_number=agent_calls[key].line_number,
                            )
                        agent_calls[key] = agent_call
                    if (
                        top_type == "item.completed"
                        and item.get("type") == "agent_message"
                        and isinstance(item.get("text"), str)
                    ):
                        messages.append(item["text"])

            payload = event.get("payload")
            payload_type = payload.get("type") if isinstance(payload, dict) else None
            if top_type == "response_item" and isinstance(payload, dict):
                rollout_call = _rollout_agent_call(
                    payload, sequence=sequence, line_number=line_number
                )
                if rollout_call is not None:
                    key = f"rollout:{rollout_call.call_id or f'line-{line_number}'}"
                    if key not in agent_calls:
                        agent_order.append(key)
                    agent_calls[key] = rollout_call
                elif payload_type == "function_call_output":
                    key = f"rollout:{payload.get('call_id')}"
                    existing = agent_calls.get(key)
                    if existing is not None and existing.tool == "wait_agent":
                        agent_calls[key] = replace(
                            existing, timed_out=_timed_out(payload.get("output"))
                        )
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
        tool_observations_complete=saw_exec and not saw_rollout,
        compactions=compactions,
        agent_tool_calls=[agent_calls[key] for key in agent_order],
        agent_messages=messages,
        parse_warnings=warnings,
    )
