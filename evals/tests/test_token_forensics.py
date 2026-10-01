from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from evals.token_forensics import Thresholds, analyze_trace, parse_codex_trace
from evals.token_forensics.models import (
    NormalizedTrace,
    ToolInvocation,
    UsageObservation,
)
from evals.token_forensics.report import human_text, json_text


FIXTURES = Path(__file__).parent / "fixtures" / "token_forensics"


class CodexParserTests(unittest.TestCase):
    def analyze_events(self, events):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "trace.jsonl"
            path.write_text("".join(json.dumps(event) + "\n" for event in events))
            return analyze_trace(parse_codex_trace(path))

    def test_unparsed_rollout_tools_are_unavailable_including_mixed_traces(self):
        rollout = [
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "call_id": "call-1",
                    "name": "exec_command",
                    "arguments": '{"cmd":"pwd"}',
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call_output",
                    "call_id": "call-1",
                    "output": "/project\n",
                },
            },
        ]
        exec_events = [
            {
                "type": "item.completed",
                "item": {
                    "id": "exec-1",
                    "type": "command_execution",
                    "command": "pwd",
                    "status": "completed",
                    "exit_code": 0,
                    "aggregated_output": "abc",
                },
            },
        ]
        for mixed in (False, True):
            with self.subTest(mixed=mixed):
                summary = self.analyze_events((exec_events if mixed else []) + rollout)
                tools = summary["measured"]["tools"]
                for field in ("calls", "output_bytes", "combined_output_bytes"):
                    self.assertIsNone(tools[field], field)
                self.assertFalse(tools["observations_complete"])
                self.assertEqual(tools["observed_calls"], 1 if mixed else 0)
                self.assertEqual(tools["observed_output_bytes"], 3 if mixed else 0)
                report = human_text(summary)
                self.assertRegex(report, r"Tool calls\s+unknown / unavailable")
                self.assertRegex(report, r"Total output\s+unknown / unavailable")
                self.assertRegex(report, r"Failed calls\s+unknown / unavailable")

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

    def test_missing_turn_usage_keeps_known_subtotal_separate_from_total(self):
        known = {
            "type": "turn.completed",
            "usage": {
                "input_tokens": 100,
                "cached_input_tokens": 20,
                "output_tokens": 10,
            },
        }
        for missing in (
            {"type": "turn.completed"},
            {"type": "turn.completed", "usage": {}},
        ):
            for missing_first in (False, True):
                with self.subTest(missing=missing, missing_first=missing_first):
                    events = [missing, known] if missing_first else [known, missing]
                    summary = self.analyze_events(events)
                    tokens = summary["measured"]["tokens"]
                    self.assertIsNone(tokens["input"])
                    self.assertIsNone(tokens["output"])
                    self.assertEqual(tokens["known_subtotals"]["input"], 100)
                    self.assertEqual(tokens["known_subtotals"]["output"], 10)
                    self.assertIsNone(summary["derived"]["tokens"]["uncached_input"])
                    self.assertIsNone(
                        summary["derived"]["tokens"]["cached_input_ratio"]
                    )
                    self.assertRegex(
                        human_text(summary), r"Input\s+unknown / unavailable"
                    )
                    self.assertRegex(human_text(summary), r"Known input subtotal\s+100")

    def test_missing_usage_between_known_turns_does_not_understate_trajectory(self):
        summary = self.analyze_events(
            [
                {"type": "turn.completed", "usage": {"input_tokens": 100}},
                {"type": "turn.completed"},
                {"type": "turn.completed", "usage": {"input_tokens": 50}},
            ]
        )
        self.assertIsNone(summary["measured"]["tokens"]["input"])
        self.assertEqual(summary["measured"]["tokens"]["known_subtotals"]["input"], 150)
        trajectory = summary["derived"]["tokens"]["token_trajectory"]
        self.assertIsNone(trajectory[-1]["input_tokens"])

    def test_missing_one_counter_keeps_other_complete_totals(self):
        summary = self.analyze_events(
            [
                {
                    "type": "turn.completed",
                    "usage": {"input_tokens": 100, "output_tokens": 10},
                },
                {"type": "turn.completed", "usage": {"input_tokens": 50}},
            ]
        )
        tokens = summary["measured"]["tokens"]
        self.assertEqual(tokens["input"], 150)
        self.assertIsNone(tokens["output"])
        self.assertEqual(tokens["known_subtotals"]["output"], 10)
        self.assertEqual(tokens["completed_turns_without_usage"], 0)

    def test_measured_zero_remains_distinct_from_unavailable(self):
        summary = self.analyze_events(
            [
                {"type": "turn.started"},
                {
                    "type": "turn.completed",
                    "usage": {
                        "input_tokens": 0,
                        "cached_input_tokens": 0,
                        "output_tokens": 0,
                    },
                },
            ]
        )
        self.assertEqual(summary["measured"]["tokens"]["input"], 0)
        self.assertEqual(summary["measured"]["tokens"]["output"], 0)
        self.assertEqual(summary["measured"]["tools"]["calls"], 0)
        self.assertEqual(summary["measured"]["tools"]["output_bytes"], 0)
        self.assertTrue(summary["measured"]["tools"]["observations_complete"])
        unknown = self.analyze_events([{"type": "unknown"}])
        self.assertIsNone(unknown["measured"]["tools"]["calls"])
        self.assertIsNone(unknown["measured"]["tools"]["output_bytes"])

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
    def test_matching_skill_read_and_route_claim_do_not_establish_execution(self):
        trace = NormalizedTrace(
            source_path=Path("claims.jsonl"),
            source_format="codex-exec-jsonl",
            source_bytes=1,
            agent_messages=["[route: router → research]"],
            tool_invocations=[
                ToolInvocation(
                    "read",
                    1,
                    "command_execution",
                    "command_execution",
                    "cat .agents/skills/research/SKILL.md",
                    "completed",
                    0,
                )
            ],
        )
        summary = analyze_trace(trace)
        self.assertEqual(
            summary["heuristic"]["framework"]["skills_materially_invoked"], ["research"]
        )
        report = human_text(summary)
        self.assertIn("Skills with matching read and route claims: research", report)
        self.assertNotIn("Skills materially invoked:", report)
        self.assertIn("cannot establish method execution", report)

    def test_only_supported_wayfinder_paths_become_current_state(
        self,
    ) -> None:
        current_paths = (
            ".project-efforts/current-effort/map.md",
            ".project-efforts/current-effort/facts.md",
            ".project-efforts/current-effort/decisions.md",
            ".project-efforts/current-effort/unknowns.md",
            ".project-efforts/current-effort/evidence/E2-test-output.md",
        )
        unrecognized_paths = (
            ".project-efforts/current-effort/unknowns/U3-open-question.md",
            ".project-efforts/unrecognized-project-data/note.txt",
            ".project-efforts/current-effort/notes/free-form.md",
            ".project-efforts/current-effort/unknowns/question.md",
            ".project-efforts/current-effort/evidence/output.txt",
            ".project-efforts/current-effort/unknowns/U0-invalid.md",
            ".project-efforts/current-effort/evidence/E-invalid.md",
            ".project-efforts/current-effort/private-memory.md",
        )
        paths = current_paths + unrecognized_paths
        trace = NormalizedTrace(
            source_path=Path("project-data-trace.jsonl"),
            source_format="codex-exec-jsonl",
            source_bytes=1,
            tool_invocations=[
                ToolInvocation(
                    f"tool-{index}",
                    index,
                    "command_execution",
                    "command_execution",
                    f"sed -n '1,40p' {path}",
                    "completed",
                    0,
                    combined_output_bytes=10,
                    changed_paths=(("modified", path),),
                )
                for index, path in enumerate(paths, start=1)
            ],
        )

        summary = analyze_trace(trace)
        repository = summary["heuristic"]["repository"]
        framework = summary["heuristic"]["framework"]

        self.assertEqual(framework["wayfinder_files_read"], sorted(current_paths))
        self.assertEqual(framework["wayfinder_files_written"], sorted(current_paths))
        self.assertNotIn("other_durable_state_read", framework)
        self.assertNotIn("other_durable_state_written", framework)
        self.assertTrue(set(paths) <= set(repository["paths_observed"]))

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
            json.loads(json_text(summary))["schema_version"], "token-forensics/v3"
        )
        report = human_text(summary, label="Fixture")
        self.assertIn("Fixture", report)
        self.assertIn("TOKENS", report)
        self.assertIn("FRAMEWORK ACTIVITY (HEURISTIC)", report)

    def test_cli_output_can_be_written_from_small_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            json_path = root / "summary.json"
            text_path = root / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "evals.token_forensics",
                    str(FIXTURES / "codex-exec.jsonl"),
                    "--json-out",
                    str(json_path),
                    "--text-out",
                    str(text_path),
                ],
                cwd=Path(__file__).resolve().parents[2],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(
                json.loads(json_path.read_text())["schema_version"],
                "token-forensics/v3",
            )
            self.assertIn("TOKENS", text_path.read_text())


def _rollout_call(call_id, name, arguments, namespace=None):
    payload = {
        "type": "function_call",
        "call_id": call_id,
        "name": name,
        "arguments": arguments if isinstance(arguments, str) else json.dumps(arguments),
    }
    if namespace is not None:
        payload["namespace"] = namespace
    return {"type": "response_item", "payload": payload}


def _rollout_output(call_id, output):
    return {
        "type": "response_item",
        "payload": {
            "type": "function_call_output",
            "call_id": call_id,
            "output": output,
        },
    }


class SubagentAnalysisTests(unittest.TestCase):
    """Event shapes follow openai/codex 60947e2 exec_events.rs and multi_agents_v2."""

    def analyze_events(self, events):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "trace.jsonl"
            path.write_text("".join(json.dumps(event) + "\n" for event in events))
            return analyze_trace(parse_codex_trace(path))

    def test_exec_collab_items_report_counts_and_leave_settings_unavailable(self):
        spawn = {
            "id": "item-1",
            "type": "collab_tool_call",
            "tool": "spawn_agent",
            "sender_thread_id": "root",
            "receiver_thread_ids": ["child-1"],
            "prompt": "Review the diff.",
            "agents_states": {},
            "status": "in_progress",
        }
        summary = self.analyze_events(
            [
                {"type": "thread.started", "thread_id": "root"},
                {"type": "item.started", "item": spawn},
                {"type": "item.completed", "item": {**spawn, "status": "completed"}},
                {
                    "type": "item.completed",
                    "item": {
                        **spawn,
                        "id": "item-2",
                        "sender_thread_id": "child-1",
                        "receiver_thread_ids": ["child-2"],
                        "status": "completed",
                    },
                },
                {
                    "type": "item.completed",
                    "item": {
                        "id": "item-3",
                        "type": "collab_tool_call",
                        "tool": "wait",
                        "sender_thread_id": "root",
                        "receiver_thread_ids": ["child-1"],
                        "prompt": None,
                        "agents_states": {
                            "child-1": {"status": "running", "message": None}
                        },
                        "status": "completed",
                    },
                },
            ]
        )
        subagents = summary["measured"]["subagents"]
        self.assertEqual(subagents["observed_calls"], 3)
        self.assertEqual(subagents["spawns"]["count"], 2)
        self.assertEqual(subagents["spawns"]["prompt_bytes_total"], 32)
        self.assertEqual(subagents["spawns"]["spawned_by_other_threads"], 1)
        self.assertIsNone(subagents["spawns"]["explicit_model"])
        self.assertEqual(subagents["spawns"]["fork_modes"], {"unavailable": 2})
        self.assertEqual(subagents["waits"]["count"], 1)
        self.assertIsNone(subagents["waits"]["timed_out"])
        self.assertIsNone(subagents["waits"]["requested_timeout_ms"])
        codes = {item["code"] for item in summary["warnings"]}
        self.assertIn("nested_spawn", codes)
        self.assertNotIn("full_history_spawn", codes)
        self.assertTrue(
            any(
                "collab_tool_call items omit" in item
                for item in summary["source"]["limitations"]
            )
        )

    def test_rollout_v2_arguments_expose_fork_model_and_wait_outcomes(self):
        summary = self.analyze_events(
            [
                {"type": "session_meta", "payload": {"id": "rollout"}},
                _rollout_call(
                    "c1", "spawn_agent", {"message": "abcd", "task_name": "review"}
                ),
                _rollout_call(
                    "c2",
                    "spawn_agent",
                    {
                        "message": "ab",
                        "task_name": "spec",
                        "model": "gpt-mini",
                        "reasoning_effort": "medium",
                        "fork_turns": "none",
                    },
                ),
                _rollout_call(
                    "c3",
                    "spawn_agent",
                    {"message": "x", "task_name": "t", "fork_turns": "3"},
                ),
                _rollout_call("w1", "wait_agent", {"timeout_ms": 10000}),
                _rollout_output(
                    "w1", json.dumps({"message": "Wait timed out.", "timed_out": True})
                ),
                _rollout_call("w2", "wait_agent", {}),
                _rollout_output(
                    "w2",
                    [
                        {
                            "type": "input_text",
                            "text": json.dumps(
                                {"message": "Wait completed.", "timed_out": False}
                            ),
                        }
                    ],
                ),
                _rollout_call(
                    "f1", "followup_task", {"target": "review", "message": "fix it"}
                ),
            ]
        )
        subagents = summary["measured"]["subagents"]
        spawns = subagents["spawns"]
        self.assertEqual(spawns["count"], 3)
        self.assertEqual(spawns["prompt_bytes_total"], 7)
        self.assertEqual(spawns["prompt_bytes_max"], 4)
        self.assertEqual(spawns["explicit_model"], 1)
        self.assertEqual(spawns["explicit_reasoning_effort"], 1)
        self.assertEqual(
            spawns["fork_modes"],
            {"full_history_default": 1, "last_n_turns": 1, "none": 1},
        )
        self.assertIsNone(spawns["spawned_by_other_threads"])
        waits = subagents["waits"]
        self.assertEqual(waits["count"], 2)
        self.assertEqual(waits["timed_out"], 1)
        self.assertEqual(
            waits["requested_timeout_ms"],
            {"unset": 1, "min": 10000, "median": 10000, "max": 10000},
        )
        self.assertEqual(subagents["other_agent_tools"], {"followup_task": 1})
        codes = {item["code"] for item in summary["warnings"]}
        self.assertTrue(
            {"full_history_spawn", "spawn_without_model", "wait_timeouts"} <= codes
        )

        report = human_text(summary)
        self.assertIn("SUBAGENTS", report)
        self.assertIn("full_history_default 1", report)

    def test_v1_namespace_defaults_to_no_fork_and_bad_arguments_stay_unavailable(self):
        summary = self.analyze_events(
            [
                _rollout_call(
                    "a", "spawn_agent", {"message": "m"}, namespace="multi_agent_v1"
                ),
                _rollout_call(
                    "b",
                    "spawn_agent",
                    {"message": "m", "fork_context": True},
                    namespace="multi_agent_v1",
                ),
                _rollout_call("c", "spawn_agent", "{not json"),
            ]
        )
        spawns = summary["measured"]["subagents"]["spawns"]
        self.assertEqual(
            spawns["fork_modes"], {"full_history": 1, "none": 1, "unavailable": 1}
        )
        self.assertIsNone(spawns["explicit_model"])
        self.assertIsNone(spawns["prompt_bytes_total"])

    def test_traces_without_agent_tools_report_zero_and_omit_the_text_section(self):
        summary = analyze_trace(parse_codex_trace(FIXTURES / "codex-exec.jsonl"))
        subagents = summary["measured"]["subagents"]
        self.assertEqual(subagents["observed_calls"], 0)
        self.assertEqual(subagents["spawns"]["explicit_model"], 0)
        self.assertNotIn("SUBAGENTS", human_text(summary))


if __name__ == "__main__":
    unittest.main()
