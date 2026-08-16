"""Command-line interface for local trace analysis."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .analysis import analyze_trace
from .models import Thresholds
from .parsers.codex import parse_codex_trace
from .report import human_text, json_text


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        prog="python3 -m token_forensics",
        description="Analyze a Codex JSONL trace without running Codex.",
    )
    value.add_argument("trace", type=Path, help="Codex exec or rollout JSONL file")
    value.add_argument("--label", help="human-report title")
    value.add_argument("--json-out", type=Path, help="write compact machine-readable summary")
    value.add_argument("--text-out", type=Path, help="write concise human-readable summary")
    value.add_argument(
        "--large-tool-output-bytes",
        type=int,
        default=Thresholds.large_tool_output_bytes,
        help="warning threshold for one tool result",
    )
    value.add_argument(
        "--large-total-output-bytes",
        type=int,
        default=Thresholds.large_total_tool_output_bytes,
        help="warning threshold for cumulative tool output",
    )
    return value


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    thresholds = Thresholds(
        large_tool_output_bytes=arguments.large_tool_output_bytes,
        large_total_tool_output_bytes=arguments.large_total_output_bytes,
    )
    summary = analyze_trace(parse_codex_trace(arguments.trace), thresholds)
    machine = json_text(summary)
    human = human_text(summary, label=arguments.label)
    if arguments.json_out:
        _write(arguments.json_out, machine)
    if arguments.text_out:
        _write(arguments.text_out, human)
    if not arguments.json_out and not arguments.text_out:
        sys.stdout.write(human)
    return 0
