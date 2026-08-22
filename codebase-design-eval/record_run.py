#!/usr/bin/env python3
"""Normalize one synthetic review output and retain only compact run metrics."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--events", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--repetition", required=True, type=int)
    parser.add_argument("--elapsed-seconds", required=True, type=int)
    parser.add_argument("--run-kind", default="controlled_live_synthetic")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_text = args.output.read_text(encoding="utf-8")
    workspaces = {str(args.workspace), str(args.workspace.resolve())}
    for workspace in sorted(workspaces, key=len, reverse=True):
        output_text = output_text.replace(
            f"{workspace}/codebase-design-eval/",
            "../../",
        ).replace(
            f"{workspace}/.agents/",
            "../../../.agents/",
        ).replace(
            f"{workspace}/",
            "../../../",
        )
    args.output.write_text(output_text, encoding="utf-8")

    usage: dict[str, int] | None = None
    tool_count = 0
    failed_tool_count = 0
    for line in args.events.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
        item = event.get("item")
        if (
            event.get("type") == "item.completed"
            and isinstance(item, dict)
            and item.get("type") == "command_execution"
        ):
            tool_count += 1
            if item.get("status") != "completed" or item.get("exit_code") != 0:
                failed_tool_count += 1

    metrics = {
        "scenario": args.scenario.upper(),
        "condition": args.condition,
        "repetition": args.repetition,
        "run_kind": args.run_kind,
        "status": "completed",
        "model": "gpt-5.4",
        "reasoning_effort": "high",
        "session": "ephemeral",
        "sandbox": "read-only",
        "elapsed_seconds": args.elapsed_seconds,
        "usage": usage,
        "tool_count": tool_count,
        "failed_tool_count": failed_tool_count,
        "output_sha256": sha256(output_text.encode("utf-8")).hexdigest(),
        "evidence_path": args.output.resolve().relative_to(
            Path(__file__).resolve().parent.parent
        ).as_posix(),
    }
    metrics_path = args.output.with_suffix(".json")
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    args.events.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
