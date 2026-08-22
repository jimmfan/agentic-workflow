"""Best-effort repository and framework-context attribution."""

from __future__ import annotations

from collections import Counter, defaultdict
import re
from typing import Any

from ..models import NormalizedTrace, Thresholds, ToolInvocation


_PATH = re.compile(
    r"(?<![A-Za-z0-9_])(?:/[^\s'\";|&<>]+|(?:\.{1,2}/)?(?:[A-Za-z0-9_.@+-]+/)+[A-Za-z0-9_.@+-]+|[A-Za-z0-9_.-]+\.(?:jsonl?|md|txt|toml|ya?ml|py|tsv|csv|log))"
)
_SEARCH = re.compile(r"(?:^|[\s;/'\"])(?:rg|grep|find|fd)(?:\s|$)")
_READ = re.compile(r"(?:^|[\s;/'\"])(?:cat|sed|head|tail|less|jq|awk|perl|python3?)(?:\s|$)")
_BOUND = re.compile(r"(?:--max-count(?:=|\s)|(?:^|\s)-m\s*\d|(?:^|[|;]\s*)head\b|(?:^|[|;]\s*)tail\b)")
_EXECUTABLES = {
    "/bin/bash",
    "/bin/sh",
    "/bin/zsh",
    "/usr/bin/awk",
    "/usr/bin/env",
    "/usr/bin/perl",
    "/usr/bin/python3",
    "/usr/bin/sed",
}
_ABSOLUTE_ROOTS = (
    "/Users/",
    "/etc/",
    "/home/",
    "/mnt/",
    "/opt/",
    "/private/",
    "/tmp/",
    "/var/",
    "/workspace/",
)


def _clip(value: str | None, limit: int = 400) -> str | None:
    if value is None or len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def _clean_path(value: str) -> str:
    return value.rstrip(".,:)]}")


def _paths(command: str | None) -> list[str]:
    if not command:
        return []
    result: list[str] = []
    for match in _PATH.finditer(command):
        path = _clean_path(match.group(0))
        if path in _EXECUTABLES or path.startswith("/dev/"):
            continue
        if "/bin/" in path and "." not in path.rsplit("/", 1)[-1]:
            continue
        if path.startswith("/") and not path.startswith(_ABSOLUTE_ROOTS):
            continue
        if path not in result:
            result.append(path)
    return result


def _is_search(command: str | None) -> bool:
    return bool(command and _SEARCH.search(command))


def _is_read(command: str | None) -> bool:
    return bool(command and (_READ.search(command) or _is_search(command)))


def _looks_like_file(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return "." in name and not name.startswith(".") or name in {"AGENTS.md", "CLAUDE.md", "SKILL.md"}


def _skill_name(path: str) -> str | None:
    parts = path.split("/")
    for index, part in enumerate(parts):
        if part == "skills" and index + 1 < len(parts):
            return parts[index + 1]
    return None


def _route_markers(messages: list[str]) -> list[str]:
    markers: list[str] = []
    for message in messages:
        for marker in re.findall(r"\[route:\s*[^\]]+\]", message, flags=re.I):
            if marker not in markers:
                markers.append(marker)
    return markers


def _framework_kind(path: str) -> str | None:
    normalized = path.replace("\\", "/")
    if any(marker in normalized for marker in (
        ".agent-wayfinder/project-profile.md",
        ".agent-wayfinder/records/",
        ".agent-wayfinder/archive/",
    )):
        return "durable_workflow_state"
    if ".agent-wayfinder/" in normalized:
        return "wayfinder_state"
    if "/.agents/skills/" in normalized or normalized.startswith(".agents/skills/"):
        return "skill"
    if "/.codex/skills/" in normalized or normalized.startswith(".codex/skills/"):
        return "skill"
    if ".agent-workflow/" in normalized or normalized.endswith(("AGENTS.md", "CLAUDE.md")):
        return "framework_instruction"
    return None


def _tool_record(tool: ToolInvocation) -> dict[str, Any]:
    return {
        "invocation_id": tool.invocation_id,
        "command": _clip(tool.command),
        "output_bytes": tool.output_bytes,
    }


def analyze_context(
    trace: NormalizedTrace, thresholds: Thresholds
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    observations: dict[str, list[ToolInvocation]] = defaultdict(list)
    broad_searches: list[dict[str, Any]] = []
    unbounded_searches: list[dict[str, Any]] = []

    for tool in trace.tool_invocations:
        paths = _paths(tool.command)
        if _is_read(tool.command):
            for path in paths:
                observations[path].append(tool)
        if _is_search(tool.command):
            file_targets = [path for path in paths if _looks_like_file(path)]
            if not file_targets or "--files" in (tool.command or ""):
                broad_searches.append(_tool_record(tool))
            if not _BOUND.search(tool.command or "") and tool.output_bytes >= thresholds.large_tool_output_bytes:
                unbounded_searches.append(_tool_record(tool))

    changed: list[tuple[str, str, ToolInvocation]] = []
    for tool in trace.tool_invocations:
        for kind, path in tool.changed_paths:
            changed.append((kind, path, tool))

    repeated_reads = [
        {
            "path": path,
            "observations": len(tools),
            "associated_tool_output_bytes": sum(tool.output_bytes for tool in tools),
        }
        for path, tools in observations.items()
        if len(tools) > 1
    ]
    repeated_reads.sort(key=lambda item: (-item["observations"], item["path"]))
    large_reads = [
        {
            "path": path,
            "associated_tool_output_bytes": max(tool.output_bytes for tool in tools),
            "note": "tool output is associated with this command, not attributed exactly to this file",
        }
        for path, tools in observations.items()
        if any(tool.output_bytes >= thresholds.large_tool_output_bytes for tool in tools)
    ]
    large_reads.sort(key=lambda item: item["associated_tool_output_bytes"], reverse=True)

    framework_paths: dict[str, set[str]] = defaultdict(set)
    framework_tools: dict[str, set[str]] = defaultdict(set)
    tool_by_id = {tool.invocation_id: tool for tool in trace.tool_invocations}
    for path, tools in observations.items():
        kind = _framework_kind(path)
        if kind is None:
            continue
        framework_paths[kind].add(path)
        framework_tools[kind].update(tool.invocation_id for tool in tools)
    framework_writes: dict[str, set[str]] = defaultdict(set)
    for _kind, path, _tool in changed:
        category = _framework_kind(path)
        if category is not None:
            framework_writes[category].add(path)

    def output_bytes_for(category: str) -> int:
        return sum(tool_by_id[identifier].output_bytes for identifier in framework_tools[category])

    skill_names = sorted(
        {name for path in framework_paths["skill"] if (name := _skill_name(path)) is not None}
    )
    markers = _route_markers(trace.agent_messages)
    marker_text = " ".join(markers).casefold()
    invoked = []
    for name in skill_names:
        short = name.removeprefix("workflow-")
        if re.search(rf"\b{re.escape(short.casefold())}\b", marker_text):
            invoked.append(name)

    repository = {
        "unique_paths_observed": len(observations),
        "paths_observed": sorted(observations),
        "repeated_reads": repeated_reads,
        "large_reads": large_reads[:20],
        "broad_searches": broad_searches,
        "likely_unbounded_searches": unbounded_searches,
        "file_detection_note": "best-effort inference from command text; not a complete filesystem access trace",
    }
    skill_files = sorted(path for path in framework_paths["skill"] if _looks_like_file(path))
    framework = {
        "instruction_files_observed": sorted(framework_paths["framework_instruction"]),
        "instruction_output_bytes_observed": output_bytes_for("framework_instruction"),
        "skill_files_observed": skill_files,
        "skill_names_observed": skill_names,
        "skill_output_bytes_observed": output_bytes_for("skill"),
        "skills_materially_invoked": invoked,
        "route_markers": markers,
        "wayfinder_files_read": sorted(framework_paths["wayfinder_state"]),
        "wayfinder_files_written": sorted(framework_writes["wayfinder_state"]),
        "wayfinder_output_bytes_observed": output_bytes_for("wayfinder_state"),
        "other_durable_state_read": sorted(framework_paths["durable_workflow_state"]),
        "other_durable_state_written": sorted(framework_writes["durable_workflow_state"]),
        "byte_note": "bytes are tool-output bytes associated with commands that name these paths, not token counts or exact per-file bytes",
    }

    pressure: list[dict[str, Any]] = []
    ordered = sorted(trace.tool_invocations, key=lambda item: item.sequence)
    for tool in ordered:
        if tool.output_bytes < thresholds.large_tool_output_bytes:
            continue
        later_calls = sum(other.sequence > tool.sequence for other in ordered)
        pressure.append(
            {
                "kind": "large_tool_output_with_later_activity",
                "invocation_id": tool.invocation_id,
                "output_bytes": tool.output_bytes,
                "later_tool_calls": later_calls,
                "command": _clip(tool.command),
                "interpretation": "plausible sustained-context contributor; exact token attribution is unavailable",
            }
        )

    heuristic = {
        "repository": repository,
        "framework": framework,
        "potential_context_pressure": pressure,
    }

    warnings: list[dict[str, Any]] = []
    if any(item["observations"] >= thresholds.repeated_resource_count for item in repeated_reads):
        warnings.append(
            {
                "code": "repeated_resource_observation",
                "category": "heuristic",
                "message": "The same resource path was observed repeatedly.",
            }
        )
    if unbounded_searches:
        warnings.append(
            {
                "code": "large_unbounded_search",
                "category": "heuristic",
                "message": "A broad search emitted a large result without an observable output bound.",
            }
        )
    framework_tool_ids = framework_tools["framework_instruction"] | framework_tools["skill"]
    framework_bytes = sum(tool_by_id[identifier].output_bytes for identifier in framework_tool_ids)
    if framework_bytes >= thresholds.large_framework_output_bytes:
        warnings.append(
            {
                "code": "large_framework_loading",
                "category": "heuristic",
                "message": f"Framework/skill reads were associated with {framework_bytes} output bytes.",
            }
        )
    return repository, heuristic, warnings
