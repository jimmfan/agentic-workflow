from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from token_forensics import Thresholds, analyze_trace, parse_codex_trace
from token_forensics.models import NormalizedTrace, ToolInvocation, UsageObservation
from token_forensics.report import human_text, json_text


FIXTURES = Path(__file__).parent / "fixtures" / "token_forensics"


class CodexParserTests(unittest.TestCase):
    def test_exec_usage_is_summed_per_turn_without_counting_item_updates(self) -> None:
        trace = parse_codex_trace(FIXTURES / "codex-exec.jsonl")
        summary = analyze_trace(trace)

        self.assertEqual(trace.source_format, "codex-exec-jsonl")
        self.assertEqual(summary["measured"]["tokens"]["input"], 250)
        self.assertEqual(summary["measured"]["tokens"]["cached_input"], 200)
        self.assertEqual(summary["derived"]["tokens"]["uncached_input"], 50)
        self.assertEqual(summary["derived"]["tokens"]["cached_input_ratio"], 0.8)
        self.assertEqual(summary["measured"]["tokens"]["output"], 30)
        self.assertEqual(summary["measured"]["trajectory"]["codex_turns_completed"], 2)
        self.assertEqual(summary["measured"]["tools"]["calls"], 3)

    def test_rollout_cumulative_snapshots_are_not_summed_or_repeated(self) -> None:
        trace = parse_codex_trace(FIXTURES / "codex-rollout.jsonl")
        summary = analyze_trace(trace)

        self.assertEqual(trace.source_format, "codex-rollout-jsonl")
        self.assertEqual(summary["measured"]["tokens"]["raw_usage_observations"], 3)
        self.assertEqual(summary["measured"]["tokens"]["usage_observations"], 2)
        self.assertEqual(summary["measured"]["tokens"]["input"], 250)
        self.assertEqual(summary["measured"]["tokens"]["cached_input"], 200)
        self.assertEqual(summary["measured"]["tokens"]["output"], 30)
        self.assertEqual(summary["derived"]["tokens"]["uncached_input"], 50)
        self.assertEqual(summary["measured"]["trajectory"]["context_compactions"], 1)

    def test_stdout_stderr_and_combined_output_are_not_double_counted(self) -> None:
        summary = analyze_trace(parse_codex_trace(FIXTURES / "codex-exec.jsonl"))
        tools = summary["measured"]["tools"]

        self.assertEqual(tools["output_bytes"], 15)
        self.assertIsNone(tools["stdout_bytes"])
        self.assertIsNone(tools["stderr_bytes"])
        self.assertEqual(tools["combined_output_bytes"], 7)
        self.assertEqual(len(tools["failed_calls"]), 1)

    def test_incomplete_older_trace_degrades_to_unknown(self) -> None:
        summary = analyze_trace(parse_codex_trace(FIXTURES / "codex-incomplete.jsonl"))

        self.assertIsNone(summary["measured"]["tokens"]["input"])
        self.assertEqual(summary["measured"]["tools"]["calls"], 1)
        self.assertTrue(
            any(item["code"] == "parse_warning" for item in summary["warnings"])
        )
        self.assertIn("unknown / unavailable", human_text(summary))


class GenericAnalysisTests(unittest.TestCase):
    def test_analysis_accepts_normalized_trace_without_benchmark_code(self) -> None:
        trace = NormalizedTrace(
            source_path=Path("ordinary-codex.jsonl"),
            source_format="codex-exec-jsonl",
            source_bytes=10,
            codex_turns_started=1,
            codex_turns_completed=1,
            usage_observations=[
                UsageObservation(
                    1,
                    1,
                    "per_turn",
                    input_tokens=20,
                    cached_input_tokens=5,
                    output_tokens=2,
                )
            ],
            tool_invocations=[
                ToolInvocation(
                    "tool-1",
                    2,
                    "command_execution",
                    "command_execution",
                    "rg -n error .",
                    "completed",
                    0,
                    combined_output_bytes=20,
                )
            ],
        )

        summary = analyze_trace(trace, Thresholds(large_tool_output_bytes=10))

        self.assertEqual(summary["measured"]["tokens"]["input"], 20)
        self.assertTrue(
            any(item["code"] == "large_tool_output" for item in summary["warnings"])
        )
        self.assertNotIn("itbench", json_text(summary).casefold())

    def test_repeated_reads_commands_failures_and_large_output_warning(self) -> None:
        trace = NormalizedTrace(
            source_path=Path("fixture.jsonl"),
            source_format="codex-exec-jsonl",
            source_bytes=1,
            tool_invocations=[
                ToolInvocation(
                    f"tool-{index}",
                    index,
                    "command_execution",
                    "command_execution",
                    "sed -n '1,80p' evidence.json",
                    "failed",
                    1,
                    combined_output_bytes=20,
                )
                for index in range(1, 4)
            ],
        )
        thresholds = Thresholds(
            large_tool_output_bytes=10,
            repeated_command_count=3,
            repeated_failed_command_count=2,
            repeated_resource_count=3,
        )

        summary = analyze_trace(trace, thresholds)
        codes = {item["code"] for item in summary["warnings"]}

        self.assertIn("large_tool_output", codes)
        self.assertIn("repeated_command", codes)
        self.assertIn("repeated_failed_command", codes)
        self.assertIn("repeated_resource_observation", codes)
        self.assertEqual(
            summary["heuristic"]["repository"]["repeated_reads"][0]["observations"], 3
        )

    def test_reports_are_valid_and_concise(self) -> None:
        summary = analyze_trace(parse_codex_trace(FIXTURES / "codex-exec.jsonl"))

        self.assertEqual(
            json.loads(json_text(summary))["schema_version"], "token-forensics/v1"
        )
        report = human_text(summary, label="Fixture")
        self.assertIn("Fixture", report)
        self.assertIn("TOKENS", report)
        self.assertIn("FRAMEWORK ACTIVITY (HEURISTIC)", report)

    def test_cli_output_can_be_written_from_small_fixture(self) -> None:
        from token_forensics.cli import main

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            json_path = root / "summary.json"
            text_path = root / "summary.md"
            exit_code = main(
                [
                    str(FIXTURES / "codex-exec.jsonl"),
                    "--json-out",
                    str(json_path),
                    "--text-out",
                    str(text_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                json.loads(json_path.read_text())["schema_version"],
                "token-forensics/v1",
            )
            self.assertIn("TOKENS", text_path.read_text())


if __name__ == "__main__":
    unittest.main()
