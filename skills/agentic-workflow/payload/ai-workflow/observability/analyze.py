#!/usr/bin/env python3
"""Summarize metadata-only VS Code/Copilot agent telemetry without storing it."""

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


SCHEMA_VERSION = 1
ANALYZER_VERSION = "1.0.0"
MINIMUM_PYTHON = (3, 11)
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
TAG_KEY = re.compile(r"[a-z][a-z0-9_.-]{0,63}")
TOKEN_KEYS = {
    "input": ("gen_ai.usage.input_tokens",),
    "output": ("gen_ai.usage.output_tokens",),
    "cache_read_input": ("gen_ai.usage.cache_read.input_tokens",),
    "cache_creation_input": ("gen_ai.usage.cache_creation.input_tokens",),
    "reasoning_output": (
        "gen_ai.usage.reasoning.output_tokens",
        "gen_ai.usage.reasoning_tokens",
    ),
}
OPERATION_KEYS = (
    "gen_ai.operation.name",
    "github.copilot.operation.name",
    "copilot_chat.operation.name",
)
SKILL_KEYS = (
    "github.copilot.tool.parameters.skill_name",
    "github.copilot.skill.name",
)
CONTENT_FRAGMENTS = (
    "input.messages",
    "output.messages",
    "prompt",
    "completion",
    "system.instructions",
    "system_instructions",
    "tool.arguments",
    "tool.call.arguments",
    "tool.definitions",
    "tool.result",
    "tool.parameters",
    "user_request",
    "prompt_context",
)
PATH_FRAGMENTS = (
    "repository.url",
    "repository.path",
    "repo.url",
    "repo.path",
    "vcs.repository",
    "workspace.path",
    "working_directory",
    "cwd",
    "github.copilot.skill.path",
)


class AnalyzerError(RuntimeError):
    """An input could not be interpreted safely."""


def configure_console() -> None:
    """Keep terminal output writable when the active encoding is restrictive."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except (AttributeError, OSError, ValueError):
                pass


def require_supported_python() -> None:
    if sys.version_info < MINIMUM_PYTHON:
        found = ".".join(str(part) for part in sys.version_info[:3])
        raise AnalyzerError(f"Python 3.11 or newer is required; found Python {found}")


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: str
    operation: str
    start_ms: Optional[float]
    end_ms: Optional[float]
    tokens: Dict[str, Optional[int]]
    request_model: Optional[str]
    response_model: Optional[str]
    skill: Optional[str]
    skill_events: List[Tuple[float, str]]
    error: bool
    source_index: int
    source_format: str
    service_name: Optional[str]
    service_version: Optional[str]
    content_fields: int
    path_fields: int


def _first(values: Mapping[str, Any], keys: Sequence[str]) -> Any:
    return next((values[key] for key in keys if key in values), None)


def _value(raw: Any) -> Any:
    if not isinstance(raw, Mapping):
        return raw
    for key in ("stringValue", "intValue", "doubleValue", "boolValue"):
        if key in raw:
            return raw[key]
    return None


def _attributes(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, Mapping):
        return {str(key): _value(value) for key, value in raw.items()}
    result: Dict[str, Any] = {}
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, Mapping) and isinstance(item.get("key"), str):
                result[item["key"]] = _value(item.get("value"))
    return result


def _resource_attributes(resource: Mapping[str, Any]) -> Dict[str, Any]:
    direct = _attributes(resource.get("attributes", {}))
    if direct:
        return direct
    result: Dict[str, Any] = {}
    raw_pairs = resource.get("_rawAttributes", [])
    if isinstance(raw_pairs, list):
        for item in raw_pairs:
            if isinstance(item, list) and len(item) == 2 and isinstance(item[0], str):
                result[item[0]] = _value(item[1])
    return result


def _safe_identifier(value: Any) -> Optional[str]:
    candidate = value.strip() if isinstance(value, str) else ""
    return candidate if IDENTIFIER.fullmatch(candidate) else None


def _safe_model(value: Any) -> Optional[str]:
    candidate = value.strip() if isinstance(value, str) else ""
    if not candidate or len(candidate) > 128 or any(ord(char) < 32 for char in candidate):
        return None
    return candidate


def _integer(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if number >= 0 else None


def _milliseconds(value: Any, nanoseconds: bool = False) -> Optional[float]:
    if isinstance(value, list) and len(value) == 2:
        try:
            return float(value[0]) * 1000 + float(value[1]) / 1_000_000
        except (TypeError, ValueError, OverflowError):
            return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number / 1_000_000 if nanoseconds else number


def _privacy_counts(attributes: Mapping[str, Any]) -> Tuple[int, int]:
    content = sum(
        key not in SKILL_KEYS and any(part in key.lower() for part in CONTENT_FRAGMENTS)
        for key in attributes
    )
    paths = sum(any(part in key.lower() for part in PATH_FRAGMENTS) for key in attributes)
    return content, paths


def _parent_id(raw: Mapping[str, Any]) -> str:
    if isinstance(raw.get("parentSpanId"), str):
        return raw["parentSpanId"]
    parent = raw.get("parentSpanContext", {})
    return parent.get("spanId", "") if isinstance(parent, Mapping) else ""


def _normalize_span(
    raw: Mapping[str, Any], resource: Mapping[str, Any], source_index: int, source_format: str
) -> Optional[Span]:
    context = raw.get("_spanContext", raw.get("spanContext", {}))
    context = context if isinstance(context, Mapping) else {}
    trace_id = raw.get("traceId", context.get("traceId"))
    span_id = raw.get("spanId", context.get("spanId"))
    name = raw.get("name")
    if not all(isinstance(value, str) for value in (trace_id, span_id, name)):
        return None

    attributes = _attributes(raw.get("attributes", {}))
    resource_attributes = _resource_attributes(resource)
    content_fields, path_fields = _privacy_counts(attributes)
    resource_content, resource_paths = _privacy_counts(resource_attributes)
    skill_events: List[Tuple[float, str]] = []
    events = raw.get("events", [])
    if isinstance(events, list):
        for event in events:
            if not isinstance(event, Mapping):
                continue
            event_attributes = _attributes(event.get("attributes", {}))
            event_content, event_paths = _privacy_counts(event_attributes)
            content_fields += event_content
            path_fields += event_paths
            if event.get("name") == "github.copilot.skill.invoked":
                skill = _safe_identifier(event_attributes.get("github.copilot.skill.name"))
                if skill:
                    event_time = _milliseconds(event.get("timeUnixNano"), True)
                    if event_time is None:
                        event_time = _milliseconds(event.get("time"))
                    skill_events.append((event_time or 0, skill))

    start_ms = _milliseconds(raw.get("startTimeUnixNano"), True)
    end_ms = _milliseconds(raw.get("endTimeUnixNano"), True)
    if start_ms is None:
        start_ms = _milliseconds(raw.get("startTime"))
    if end_ms is None:
        end_ms = _milliseconds(raw.get("endTime"))
    duration_ms = _milliseconds(raw.get("duration"))
    if end_ms is None and start_ms is not None and duration_ms is not None:
        end_ms = start_ms + duration_ms

    status = raw.get("status", {})
    status_code = status.get("code") if isinstance(status, Mapping) else None
    operation = _first(attributes, OPERATION_KEYS) or name
    operation = operation.strip().lower().replace(" ", "_") if isinstance(operation, str) else name
    return Span(
        trace_id=trace_id,
        span_id=span_id,
        parent_id=_parent_id(raw),
        operation=operation,
        start_ms=start_ms,
        end_ms=end_ms,
        tokens={label: _integer(_first(attributes, keys)) for label, keys in TOKEN_KEYS.items()},
        request_model=_safe_model(attributes.get("gen_ai.request.model")),
        response_model=_safe_model(
            attributes.get("gen_ai.response.model", attributes.get("github.copilot.model"))
        ),
        skill=_safe_identifier(_first(attributes, SKILL_KEYS)),
        skill_events=skill_events,
        error=status_code in (2, "2", "ERROR", "STATUS_CODE_ERROR") or "error.type" in attributes,
        source_index=source_index,
        source_format=source_format,
        service_name=_safe_identifier(resource_attributes.get("service.name")),
        service_version=_safe_model(resource_attributes.get("service.version")),
        content_fields=content_fields + resource_content,
        path_fields=path_fields + resource_paths,
    )


def _extract_otlp(
    raw: Mapping[str, Any], source_index: int, source_format: str
) -> List[Span]:
    result: List[Span] = []
    resource_spans = raw.get("resourceSpans", [])
    if not isinstance(resource_spans, list):
        return result
    for resource_span in resource_spans:
        if not isinstance(resource_span, Mapping):
            continue
        resource = resource_span.get("resource", {})
        resource = resource if isinstance(resource, Mapping) else {}
        scope_spans = resource_span.get("scopeSpans", [])
        if not isinstance(scope_spans, list):
            continue
        for scope in scope_spans:
            spans = scope.get("spans", []) if isinstance(scope, Mapping) else []
            if not isinstance(spans, list):
                continue
            for raw_span in spans:
                if isinstance(raw_span, Mapping):
                    span = _normalize_span(raw_span, resource, source_index, source_format)
                    if span:
                        result.append(span)
    return result


def _extract_record(raw: Any, source_index: int, source_format: str) -> Tuple[List[Span], int, int]:
    if not isinstance(raw, Mapping):
        return [], 0, 1
    if "resourceSpans" in raw:
        return _extract_otlp(raw, source_index, source_format), 0, 0
    resource = raw.get("resource", {})
    resource = resource if isinstance(resource, Mapping) else {}
    span = _normalize_span(raw, resource, source_index, source_format)
    if span:
        return [span], 0, 0
    ignored_keys = {
        "resourceMetrics",
        "resourceLogs",
        "scopeMetrics",
        "scopeLogs",
        "dataPoints",
        "descriptor",
        "aggregationTemporality",
    }
    if ignored_keys.intersection(raw) or ("body" in raw and "hrTime" in raw):
        return [], 1, 0
    return [], 0, 1


def _format_of(record: Any, json_lines: bool) -> str:
    if isinstance(record, Mapping) and "copilotChat" in record:
        return "agent-debug-json"
    if isinstance(record, Mapping) and "resourceSpans" in record:
        return "otlp-jsonl" if json_lines else "otlp-json"
    return "copilot-jsonl"


def _load_source(path: Path, source_index: int) -> Tuple[List[Span], Dict[str, Any]]:
    try:
        text = path.read_bytes().decode("utf-8-sig")
    except OSError as exc:
        raise AnalyzerError(
            f"cannot read input {source_index + 1}: {exc.strerror or exc.__class__.__name__}"
        ) from exc
    except UnicodeDecodeError as exc:
        raise AnalyzerError(f"input {source_index + 1} is not UTF-8 JSON: {exc.reason}") from exc

    json_lines = False
    incomplete_tail = False
    try:
        records = [json.loads(text)]
    except json.JSONDecodeError:
        json_lines = True
        records = []
        lines = text.splitlines(keepends=True)
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line.strip()))
            except json.JSONDecodeError as exc:
                if number == len(lines) and not line.endswith(("\n", "\r")):
                    incomplete_tail = True
                    continue
                raise AnalyzerError(
                    f"invalid JSONL record in input {source_index + 1}, line {number}: {exc.msg}"
                ) from exc

    source_format = _format_of(records[0] if records else {}, json_lines)
    spans: List[Span] = []
    ignored = 0
    unknown = 0
    for record in records:
        found, ignored_count, unknown_count = _extract_record(record, source_index, source_format)
        spans.extend(found)
        ignored += ignored_count
        unknown += unknown_count
    if not spans and not ignored:
        raise AnalyzerError(
            f"input {source_index + 1} contains no supported spans; its export shape may be unsupported"
        )
    if source_format == "agent-debug-json":
        for span in spans:
            span.content_fields += 1
    identity = "|".join(
        [
            source_format,
            *(f"{span.trace_id}:{span.span_id}" for span in sorted(spans, key=lambda item: (item.trace_id, item.span_id))),
            f"ignored={ignored}",
            f"unknown={unknown}",
        ]
    )
    return spans, {
        "input_id": hashlib.sha256(identity.encode()).hexdigest()[:16],
        "format": source_format,
        "records": len(records),
        "spans": len(spans),
        "ignored_signal_records": ignored,
        "unknown_records": unknown,
        "incomplete_tail_ignored": incomplete_tail,
    }


def _ordered(spans: Iterable[Span]) -> List[Span]:
    return sorted(
        spans,
        key=lambda span: (
            span.start_ms is None,
            span.start_ms if span.start_ms is not None else 0,
            span.span_id,
        ),
    )


def _descendants(root: Span, spans: Sequence[Span]) -> List[Span]:
    children: Dict[str, List[Span]] = {}
    for span in spans:
        children.setdefault(span.parent_id, []).append(span)
    result: List[Span] = []
    pending = [root]
    seen = set()
    while pending:
        current = pending.pop()
        if current.span_id in seen:
            continue
        seen.add(current.span_id)
        result.append(current)
        pending.extend(children.get(current.span_id, []))
    return _ordered(result)


def _run_sets(spans: Sequence[Span]) -> List[Tuple[Optional[Span], List[Span]]]:
    traces: Dict[str, List[Span]] = {}
    for span in spans:
        traces.setdefault(span.trace_id, []).append(span)
    result: List[Tuple[Optional[Span], List[Span]]] = []
    for trace_id in sorted(traces):
        trace_spans = traces[trace_id]
        debug_sources = sorted(
            {span.source_index for span in trace_spans if span.source_format == "agent-debug-json"}
        )
        for source_index in debug_sources:
            result.append(
                (None, _ordered(span for span in trace_spans if span.source_index == source_index))
            )
        trace_spans = [span for span in trace_spans if span.source_index not in debug_sources]
        if not trace_spans:
            continue
        by_id = {span.span_id: span for span in trace_spans}

        def has_invoke_ancestor(span: Span) -> bool:
            parent_id = span.parent_id
            seen = set()
            while parent_id in by_id and parent_id not in seen:
                seen.add(parent_id)
                parent = by_id[parent_id]
                if parent.operation == "invoke_agent":
                    return True
                parent_id = parent.parent_id
            return False

        roots = [
            span
            for span in trace_spans
            if span.operation == "invoke_agent" and not has_invoke_ancestor(span)
        ]
        assigned = set()
        for root in _ordered(roots):
            members = _descendants(root, trace_spans)
            result.append((root, members))
            assigned.update(span.span_id for span in members)
        remainder = [span for span in trace_spans if span.span_id not in assigned]
        if remainder:
            possible_roots = [span for span in remainder if span.parent_id not in by_id]
            result.append((_ordered(possible_roots)[0] if possible_roots else None, _ordered(remainder)))
    return result


def _sum_tokens(spans: Sequence[Span]) -> Dict[str, Optional[int]]:
    result: Dict[str, Optional[int]] = {}
    for label in TOKEN_KEYS:
        values = [span.tokens[label] for span in spans if span.tokens[label] is not None]
        result[label] = sum(values) if values else None
    return result


def _duration(root: Optional[Span], spans: Sequence[Span]) -> Optional[float]:
    if root and root.start_ms is not None and root.end_ms is not None:
        return max(0, root.end_ms - root.start_ms)
    starts = [span.start_ms for span in spans if span.start_ms is not None]
    ends = [span.end_ms for span in spans if span.end_ms is not None]
    return max(0, max(ends) - min(starts)) if starts and ends else None


def _unique(values: Iterable[Optional[str]]) -> List[str]:
    result: List[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _summarize_run(
    root: Optional[Span], spans: Sequence[Span], input_ids: Sequence[str]
) -> Dict[str, Any]:
    chats = [span for span in spans if span.operation == "chat"]
    tokenized = [
        span for span in chats if span.tokens["input"] is not None or span.tokens["output"] is not None
    ]
    if tokenized:
        accounting, token_spans = "chat-spans", tokenized
    elif root and any(root.tokens[label] is not None for label in TOKEN_KEYS):
        accounting, token_spans = "outer-invoke-fallback", [root]
    else:
        accounting, token_spans = "unavailable", []

    skill_signals: List[Tuple[float, str, str]] = []
    for span in spans:
        if span.skill:
            skill_signals.append((span.start_ms or 0, span.span_id, span.skill))
        skipped_duplicate = False
        for index, (event_time, event_skill) in enumerate(span.skill_events):
            if event_skill == span.skill and not skipped_duplicate:
                skipped_duplicate = True
                continue
            skill_signals.append((event_time, f"{span.span_id}:{index}", event_skill))
    skills = [signal[2] for signal in sorted(skill_signals)]
    source_positions = sorted({span.source_index for span in spans})
    source_ids = sorted({input_ids[position] for position in source_positions})
    seed = "|".join(
        [
            spans[0].trace_id,
            root.span_id if root else spans[0].span_id,
            *(str(position) for position in source_positions),
            *source_ids,
        ]
    )
    duration = _duration(root, spans)
    return {
        "run_id": hashlib.sha256(seed.encode()).hexdigest()[:16],
        "source_ids": source_ids,
        "source_formats": sorted({span.source_format for span in spans}),
        "fidelity": "debug-converted" if any(
            span.source_format == "agent-debug-json" for span in spans
        ) else ("preview-raw" if any(span.source_format == "copilot-jsonl" for span in spans) else "otlp"),
        "services": _unique(span.service_name for span in spans),
        "service_versions": _unique(span.service_version for span in spans),
        "requested_models": _unique(span.request_model for span in spans),
        "response_models": _unique(span.response_model for span in spans),
        "skills": skills,
        "skill_observation": "observed" if skills else "none-observed",
        "llm_calls": len(chats),
        "tokenized_llm_calls": len(tokenized),
        "tool_calls": sum(span.operation == "execute_tool" for span in spans),
        "subagent_invocations": sum(span.operation == "invoke_agent" for span in spans)
        - (1 if root and root.operation == "invoke_agent" else 0),
        "duration_ms": round(duration, 3) if duration is not None else None,
        "error_spans": sum(span.error for span in spans),
        "token_accounting": accounting,
        "tokens": _sum_tokens(token_spans),
    }


def _median(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    value = float(statistics.median(values))
    return int(value) if value.is_integer() else round(value, 3)


def _groups(runs: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, ...], List[Mapping[str, Any]]] = {}
    for run in runs:
        grouped.setdefault(tuple(run["skills"]), []).append(run)
    result: List[Dict[str, Any]] = []
    for skills in sorted(grouped, key=lambda item: (not item, item)):
        members = grouped[skills]
        result.append(
            {
                "skills": list(skills),
                "skill_observation": "observed" if skills else "none-observed",
                "runs": len(members),
                "median_llm_calls": _median([run["llm_calls"] for run in members]),
                "median_tool_calls": _median([run["tool_calls"] for run in members]),
                "median_duration_ms": _median(
                    [run["duration_ms"] for run in members if run["duration_ms"] is not None]
                ),
                "median_tokens": {
                    label: _median(
                        [run["tokens"][label] for run in members if run["tokens"][label] is not None]
                    )
                    for label in TOKEN_KEYS
                },
                "runs_with_errors": sum(bool(run["error_spans"]) for run in members),
            }
        )
    return result


def _capabilities(spans: Sequence[Span]) -> Dict[str, str]:
    chats = [span for span in spans if span.operation == "chat"]
    tokenized = [
        span for span in chats if span.tokens["input"] is not None or span.tokens["output"] is not None
    ]
    token_status = "unavailable"
    if tokenized:
        token_status = "available" if len(tokenized) == len(chats) else "partial"
    elif any(any(span.tokens[label] is not None for label in TOKEN_KEYS) for span in spans):
        token_status = "available"
    return {
        "token_usage": token_status,
        "skill_attribution": "available" if any(
            span.skill or span.skill_events for span in spans
        ) else "unavailable",
        "model_metadata": "available" if any(
            span.request_model or span.response_model for span in spans
        ) else "unavailable",
    }


def analyze(paths: Sequence[Path], tags: Mapping[str, str]) -> Dict[str, Any]:
    spans: List[Span] = []
    provenance: List[Dict[str, Any]] = []
    for source_index, path in enumerate(paths):
        source_spans, source_provenance = _load_source(path, source_index)
        spans.extend(source_spans)
        provenance.append(source_provenance)

    deduplicated: Dict[Tuple[Any, ...], Span] = {}
    for span in spans:
        key = (span.trace_id, span.span_id)
        if span.source_format == "agent-debug-json":
            key = (span.source_format, span.source_index, span.trace_id, span.span_id)
        deduplicated.setdefault(key, span)
    duplicate_count = len(spans) - len(deduplicated)
    normalized = list(deduplicated.values())
    input_ids = [item["input_id"] for item in provenance]
    runs = [_summarize_run(root, members, input_ids) for root, members in _run_sets(normalized)]
    runs.sort(key=lambda run: run["run_id"])
    capabilities = _capabilities(normalized)

    warnings: List[str] = []
    if duplicate_count:
        warnings.append(f"deduplicated {duplicate_count} repeated span(s) by trace ID and span ID")
    if any(item["incomplete_tail_ignored"] for item in provenance):
        warnings.append("ignored an incomplete final JSONL record; use a closed snapshot for reproducibility")
    if any(item["unknown_records"] for item in provenance):
        warnings.append("ignored records with an unknown non-span shape; exporter compatibility may have drifted")
    if any(item["ignored_signal_records"] for item in provenance):
        warnings.append("ignored metric/log records; this analyzer intentionally summarizes spans only")
    if capabilities["skill_attribution"] == "unavailable":
        warnings.append("skill attribution is unavailable in these inputs; other observed metrics remain valid")
    if any(span.content_fields for span in normalized):
        warnings.append("discarded content-bearing fields; no content values are emitted")
    if any(span.path_fields for span in normalized):
        warnings.append("discarded repository/workspace path metadata; no path values are emitted")
    if any(run["token_accounting"] == "outer-invoke-fallback" for run in runs):
        warnings.append("some token totals use a labeled outer invoke_agent fallback")
    if any(run["token_accounting"] == "unavailable" for run in runs):
        warnings.append("token usage is unavailable for some runs; missing values are null, not zero")
    if any(run["llm_calls"] > run["tokenized_llm_calls"] for run in runs):
        warnings.append("some chat spans lack token attributes; reported chat-span totals are partial")
    if any(run["fidelity"] == "debug-converted" for run in runs):
        warnings.append("Agent Debug export parentage and token detail may be incomplete")

    return {
        "schema_version": SCHEMA_VERSION,
        "analyzer_version": ANALYZER_VERSION,
        "tags": dict(sorted(tags.items())),
        "capabilities": capabilities,
        "privacy": {
            "content_values_emitted": False,
            "repository_values_emitted": False,
            "content_fields_discarded": sum(span.content_fields for span in normalized),
            "repository_fields_discarded": sum(span.path_fields for span in normalized),
        },
        "provenance": provenance,
        "runs": runs,
        "groups": _groups(runs),
        "warnings": warnings,
    }


def _tokens_text(tokens: Mapping[str, Any]) -> str:
    return (
        f"in={tokens['input']}, out={tokens['output']}, cache-read={tokens['cache_read_input']}, "
        f"cache-create={tokens['cache_creation_input']}, reasoning={tokens['reasoning_output']}"
    )


def render_text(report: Mapping[str, Any]) -> str:
    lines = [
        "Agentic Workflow observability report",
        f"Inputs: {len(report['provenance'])}; runs: {len(report['runs'])}",
        "Capabilities: " + ", ".join(
            f"{key}={value}" for key, value in report["capabilities"].items()
        ),
    ]
    if report["tags"]:
        lines.append("Tags: " + ", ".join(f"{key}={value}" for key, value in report["tags"].items()))
    privacy = report["privacy"]
    lines.append(
        "Privacy: emitted no content or repository values; discarded "
        f"{privacy['content_fields_discarded']} content and "
        f"{privacy['repository_fields_discarded']} path field(s)"
    )
    lines.append("Groups:")
    for group in report["groups"]:
        path = " -> ".join(group["skills"]) if group["skills"] else "(no skill event observed)"
        lines.append(
            f"  {path}: runs={group['runs']}, median LLM={group['median_llm_calls']}, "
            f"tools={group['median_tool_calls']}, {_tokens_text(group['median_tokens'])}, "
            f"errors={group['runs_with_errors']} run(s)"
        )
    if not report["groups"]:
        lines.append("  (no runs)")
    lines.append("Runs:")
    for run in report["runs"]:
        path = " -> ".join(run["skills"]) if run["skills"] else "(no skill event observed)"
        requested = ",".join(run["requested_models"]) or "unknown"
        response = ",".join(run["response_models"]) or "unknown"
        lines.append(
            f"  {run['run_id']}: {path}; requested={requested}; response={response}; "
            f"LLM={run['llm_calls']}; tools={run['tool_calls']}; {_tokens_text(run['tokens'])}; "
            f"accounting={run['token_accounting']}; errors={run['error_spans']}"
        )
    if not report["runs"]:
        lines.append("  (no runs)")
    if report["warnings"]:
        lines.append("Warnings:")
        lines.extend(f"  - {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _parse_tags(values: Sequence[str]) -> Dict[str, str]:
    tags: Dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            raise AnalyzerError(f"tag must have KEY=VALUE form: {raw!r}")
        key, value = raw.split("=", 1)
        value = value.strip()
        if not TAG_KEY.fullmatch(key):
            raise AnalyzerError(f"invalid tag key: {key!r}")
        if not value or len(value) > 128 or any(ord(char) < 32 for char in value):
            raise AnalyzerError(f"invalid tag value for {key!r}")
        tags[key] = value
    return tags


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize VS Code/Copilot OTLP or JSONL metadata without storing it."
    )
    parser.add_argument("inputs", nargs="+", type=Path, metavar="INPUT")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--tag", action="append", default=[], metavar="KEY=VALUE")
    return parser.parse_args(argv)


def main(argv: Iterable[str] = ()) -> int:
    require_supported_python()
    configure_console()
    args = parse_args(list(argv))
    report = analyze(args.inputs, _parse_tags(args.tag))
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        sys.stdout.write(render_text(report))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except AnalyzerError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
