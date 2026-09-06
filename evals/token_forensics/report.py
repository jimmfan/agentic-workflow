"""Machine-readable and concise human-readable forensic reports."""

from __future__ import annotations

import json
from typing import Any


def json_text(summary: dict[str, Any]) -> str:
    return json.dumps(summary, indent=2, sort_keys=True) + "\n"


def _count(value: Any) -> str:
    return "unknown / unavailable" if value is None else f"{value:,}"


def _bytes(value: Any) -> str:
    if value is None:
        return "unknown / unavailable"
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if amount < 1024 or unit == "GiB":
            return f"{amount:.0f} {unit}" if unit == "B" else f"{amount:.2f} {unit}"
        amount /= 1024
    return f"{amount:.2f} GiB"


def _percent(value: Any) -> str:
    return "unknown / unavailable" if value is None else f"{value * 100:.1f}%"


def _line(label: str, value: str, width: int = 26) -> str:
    return f"{label:<{width}} {value}"


def human_text(summary: dict[str, Any], *, label: str | None = None) -> str:
    source = summary["source"]
    measured = summary["measured"]
    derived = summary["derived"]
    heuristic = summary["heuristic"]
    tokens = measured["tokens"]
    token_derived = derived["tokens"]
    tools = measured["tools"]
    trajectory = measured["trajectory"]
    repository = heuristic["repository"]
    framework = heuristic["framework"]

    lines = [label or source["path"], "", "TOKENS"]
    lines.extend(
        [
            _line("Input", _count(tokens["input"])),
            _line("Cached input", _count(tokens["cached_input"])),
            _line("Uncached input", _count(token_derived["uncached_input"])),
            _line("Output", _count(tokens["output"])),
            _line("Reasoning output", _count(tokens["reasoning_output"])),
            _line("Cached ratio", _percent(token_derived["cached_input_ratio"])),
            _line("Accounting", tokens["accounting"]),
        ]
    )

    lines.extend(["", "TRAJECTORY"])
    lines.extend(
        [
            _line("Codex turns", _count(trajectory["codex_turns_completed"])),
            _line("Internal model calls", _count(trajectory["internal_model_calls"])),
            _line("Usage observations", _count(tokens["usage_observations"])),
            _line("Context compactions", _count(trajectory["context_compactions"])),
        ]
    )

    lines.extend(["", "TOOL OUTPUT"])
    lines.extend(
        [
            _line("Tool calls", _count(tools["calls"])),
            _line("Total output", _bytes(tools["output_bytes"])),
            _line("Stdout", _bytes(tools["stdout_bytes"])),
            _line("Stderr", _bytes(tools["stderr_bytes"])),
            _line("Failed calls", _count(len(tools["failed_calls"]))),
        ]
    )
    if tools["largest_outputs"]:
        lines.extend(["", "Largest outputs"])
        for index, item in enumerate(tools["largest_outputs"][:5], start=1):
            command = (item.get("command") or item["tool_type"]).replace("\n", " ")
            lines.append(f"{index}. {_bytes(item['output_bytes']):>10}  {command}")

    lines.extend(["", "REPOSITORY / CONTEXT (HEURISTIC)"])
    lines.extend(
        [
            _line("Unique paths observed", _count(repository["unique_paths_observed"])),
            _line("Repeated reads", _count(len(repository["repeated_reads"]))),
            _line("Broad searches", _count(len(repository["broad_searches"]))),
            _line(
                "Likely unbounded searches",
                _count(len(repository["likely_unbounded_searches"])),
            ),
        ]
    )
    if heuristic["potential_context_pressure"]:
        lines.extend(["", "Potential context pressure"])
        for item in heuristic["potential_context_pressure"][:8]:
            lines.append(
                f"- {_bytes(item['output_bytes'])} output before {item['later_tool_calls']} later tool call(s): "
                f"{(item.get('command') or item['invocation_id']).replace(chr(10), ' ')}"
            )

    lines.extend(["", "FRAMEWORK ACTIVITY (HEURISTIC)"])
    lines.extend(
        [
            _line(
                "Instruction files",
                _count(len(framework["instruction_files_observed"])),
            ),
            _line("Skill files", _count(len(framework["skill_files_observed"]))),
            _line(
                "Skill output observed",
                _bytes(framework["skill_output_bytes_observed"]),
            ),
            _line(
                "Wayfinder files read", _count(len(framework["wayfinder_files_read"]))
            ),
            _line(
                "Wayfinder files written",
                _count(len(framework["wayfinder_files_written"])),
            ),
        ]
    )
    if framework["skill_names_observed"]:
        lines.append(
            "- Skill files observed: " + ", ".join(framework["skill_names_observed"])
        )
    if framework["skills_materially_invoked"]:
        lines.append(
            "- Skills materially invoked: "
            + ", ".join(framework["skills_materially_invoked"])
        )
    if framework["route_markers"]:
        lines.append("- Route markers: " + ", ".join(framework["route_markers"]))

    if summary["warnings"]:
        lines.extend(["", "WARNINGS"])
        for warning in summary["warnings"]:
            lines.append(f"- [{warning['category']}] {warning['message']}")

    lines.extend(["", "LIMITATIONS"])
    for limitation in source["limitations"]:
        lines.append(f"- {limitation}")
    return "\n".join(lines) + "\n"
