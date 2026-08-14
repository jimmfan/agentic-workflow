from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
from typing import List, Optional


PACKAGE = Path(__file__).resolve().parent.parent
ANALYZER_PATH = PACKAGE / "payload/ai-workflow/observability/analyze.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("agentic_workflow_observability", ANALYZER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load analyzer from {ANALYZER_PATH}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


ANALYZER = load_analyzer()


def attribute(key: str, value: object) -> dict:
    if isinstance(value, bool):
        encoded = {"boolValue": value}
    elif isinstance(value, int):
        encoded = {"intValue": str(value)}
    else:
        encoded = {"stringValue": str(value)}
    return {"key": key, "value": encoded}


def span(
    name: str,
    span_id: str,
    parent_id: str,
    start: int,
    end: int,
    attributes: List[dict],
    *,
    events: Optional[List[dict]] = None,
    status: Optional[dict] = None,
) -> dict:
    return {
        "traceId": "trace-one",
        "spanId": span_id,
        "parentSpanId": parent_id,
        "name": name,
        "startTimeUnixNano": str(start),
        "endTimeUnixNano": str(end),
        "attributes": attributes,
        "events": events or [],
        "status": status or {"code": 1},
    }


def otlp(spans: List[dict]) -> dict:
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        attribute("service.name", "github-copilot"),
                        attribute("service.version", "1.0.73"),
                        attribute("vcs.repository.url", "https://secret.invalid/private/repo"),
                    ]
                },
                "scopeSpans": [{"spans": spans}],
            }
        ]
    }


class ObservabilityAnalyzerTests(unittest.TestCase):
    def test_analyzer_requires_supported_python(self) -> None:
        self.assertEqual(ANALYZER.MINIMUM_PYTHON, (3, 11))
        with mock.patch.object(ANALYZER.sys, "version_info", (3, 10, 14)):
            with self.assertRaisesRegex(ANALYZER.AnalyzerError, "Python 3.11 or newer is required"):
                ANALYZER.require_supported_python()

    def write_json(self, root: Path, name: str, value: object) -> Path:
        path = root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_otlp_uses_leaf_chat_tokens_and_observes_both_skill_encodings(self) -> None:
        skill_event = {
            "name": "github.copilot.skill.invoked",
            "timeUnixNano": "7000000",
            "attributes": [
                attribute("github.copilot.skill.name", "workflow-verification"),
                attribute("github.copilot.skill.path", "/secret/skill/path"),
            ],
        }
        spans = [
            span(
                "invoke_agent",
                "root",
                "",
                1_000_000,
                12_000_000,
                [
                    attribute("gen_ai.usage.input_tokens", 999),
                    attribute("gen_ai.usage.output_tokens", 888),
                ],
            ),
            span(
                "chat",
                "chat-1",
                "root",
                2_000_000,
                4_000_000,
                [
                    attribute("gen_ai.request.model", "auto"),
                    attribute("gen_ai.response.model", "gpt-5.6"),
                    attribute("gen_ai.usage.input_tokens", 100),
                    attribute("gen_ai.usage.output_tokens", 20),
                    attribute("gen_ai.usage.cache_read.input_tokens", 40),
                    attribute("gen_ai.usage.reasoning.output_tokens", 5),
                    attribute("gen_ai.input.messages", "TOP SECRET PROMPT"),
                ],
            ),
            span(
                "execute_tool",
                "tool-1",
                "root",
                4_000_000,
                5_000_000,
                [attribute("github.copilot.tool.parameters.skill_name", "workflow-implementation")],
            ),
            span("invoke_agent", "nested", "tool-1", 5_000_000, 10_000_000, []),
            span(
                "chat",
                "chat-2",
                "nested",
                6_000_000,
                8_000_000,
                [
                    attribute("gen_ai.response.model", "gpt-5.6"),
                    attribute("gen_ai.usage.input_tokens", 50),
                    attribute("gen_ai.usage.output_tokens", 10),
                    attribute("gen_ai.usage.cache_creation.input_tokens", 5),
                ],
            ),
            span(
                "execute_tool",
                "tool-2",
                "nested",
                7_000_000,
                9_000_000,
                [attribute("github.copilot.tool.parameters.skill_name", "workflow-verification")],
                events=[skill_event],
            ),
        ]
        with tempfile.TemporaryDirectory(prefix="agentic-workflow-observability-") as temporary:
            path = self.write_json(Path(temporary), "trace.json", otlp(spans))
            report = ANALYZER.analyze([path], {"variant": "observed-skills"})

        self.assertEqual(len(report["runs"]), 1)
        run = report["runs"][0]
        self.assertEqual(run["skills"], ["workflow-implementation", "workflow-verification"])
        self.assertEqual(run["requested_models"], ["auto"])
        self.assertEqual(run["response_models"], ["gpt-5.6"])
        self.assertEqual(run["llm_calls"], 2)
        self.assertEqual(run["subagent_invocations"], 1)
        self.assertEqual(run["tokens"]["input"], 150)
        self.assertEqual(run["tokens"]["output"], 30)
        self.assertEqual(run["tokens"]["cache_read_input"], 40)
        self.assertEqual(run["tokens"]["cache_creation_input"], 5)
        self.assertEqual(run["tokens"]["reasoning_output"], 5)
        self.assertEqual(run["token_accounting"], "chat-spans")
        self.assertGreater(report["privacy"]["content_fields_discarded"], 0)
        self.assertGreater(report["privacy"]["repository_fields_discarded"], 0)
        serialized = json.dumps(report)
        self.assertNotIn("TOP SECRET PROMPT", serialized)
        self.assertNotIn("secret.invalid", serialized)
        self.assertNotIn("/secret/skill/path", serialized)

    def test_outer_invocation_tokens_are_a_labeled_fallback(self) -> None:
        spans = [
            span(
                "invoke_agent",
                "root",
                "",
                1_000_000,
                4_000_000,
                [
                    attribute("gen_ai.usage.input_tokens", 10),
                    attribute("gen_ai.usage.output_tokens", 5),
                ],
            ),
            span("chat", "chat", "root", 2_000_000, 3_000_000, []),
        ]
        with tempfile.TemporaryDirectory(prefix="agentic-workflow-observability-") as temporary:
            path = self.write_json(Path(temporary), "fallback.json", otlp(spans))
            report = ANALYZER.analyze([path], {})
        run = report["runs"][0]
        self.assertEqual(run["token_accounting"], "outer-invoke-fallback")
        self.assertEqual(run["tokens"]["input"], 10)
        self.assertEqual(report["capabilities"]["token_usage"], "available")
        self.assertIn("fallback", " ".join(report["warnings"]))

    def test_unix_lf_jsonl_paths_are_redacted_and_incomplete_tail_is_safe(self) -> None:
        root = {
            "name": "invoke_agent",
            "_spanContext": {"traceId": "raw-trace", "spanId": "raw-root"},
            "startTime": [1, 0],
            "duration": [1, 0],
            "attributes": {"workspace.path": "/Users/alice/project"},
            "resource": {"_rawAttributes": [["service.name", "copilot-chat"]]},
            "events": [],
            "status": {"code": 1},
        }
        tool = {
            "name": "execute_tool",
            "_spanContext": {"traceId": "raw-trace", "spanId": "raw-tool"},
            "parentSpanContext": {"spanId": "raw-root"},
            "startTime": [1, 100],
            "endTime": [1, 200],
            "attributes": {
                "github.copilot.tool.parameters.skill_name": "research",
                "cwd": "/home/alice/project",
            },
            "events": [],
            "status": {"code": 1},
        }
        with tempfile.TemporaryDirectory(prefix="agentic-workflow-observability-") as temporary:
            path = Path(temporary) / "live.jsonl"
            path.write_bytes(
                (json.dumps(root) + "\n" + json.dumps(tool) + "\n{\"partial\"").encode("utf-8")
            )
            report = ANALYZER.analyze([path], {})
        self.assertTrue(report["provenance"][0]["incomplete_tail_ignored"])
        self.assertEqual(report["provenance"][0]["format"], "copilot-jsonl")
        self.assertEqual(report["runs"][0]["skills"], ["research"])
        self.assertEqual(report["runs"][0]["duration_ms"], 1000)
        self.assertEqual(report["runs"][0]["services"], ["copilot-chat"])
        serialized = json.dumps(report)
        self.assertNotIn("/Users/alice", serialized)
        self.assertNotIn("/home/alice", serialized)

    def test_windows_crlf_bom_and_missing_optional_capabilities_degrade(self) -> None:
        root = {
            "name": "invoke_agent",
            "_spanContext": {"traceId": "windows-trace", "spanId": "root"},
            "startTime": [1, 0],
            "duration": [2, 0],
            "attributes": {"workspace.path": r"C:\Users\Alice\project"},
            "events": [],
            "status": {"code": 1},
        }
        chat = {
            "name": "chat",
            "_spanContext": {"traceId": "windows-trace", "spanId": "chat"},
            "parentSpanContext": {"spanId": "root"},
            "startTime": [1, 100],
            "duration": [1, 0],
            "attributes": {
                "gen_ai.usage.input_tokens": 12,
                "gen_ai.usage.output_tokens": 3,
            },
            "events": [],
            "status": {"code": 1},
        }
        tool = {
            "name": "execute_tool",
            "_spanContext": {"traceId": "windows-trace", "spanId": "tool"},
            "parentSpanContext": {"spanId": "root"},
            "startTime": [2, 0],
            "duration": [0, 100],
            "attributes": {
                "github.copilot.skill.path": r"C:\Users\Alice\.copilot\skills\research"
            },
            "events": [],
            "status": {"code": 1},
        }
        payload = "\ufeff" + "\r\n".join(json.dumps(item) for item in (root, chat, tool)) + "\r\n"
        with tempfile.TemporaryDirectory(prefix="agentic-workflow-observability-") as temporary:
            path = Path(temporary) / r"C:\Users\Alice\copilot.jsonl"
            path.write_bytes(payload.encode("utf-8"))
            report = ANALYZER.analyze([path], {})

        self.assertEqual(report["capabilities"]["token_usage"], "available")
        self.assertEqual(report["capabilities"]["skill_attribution"], "unavailable")
        self.assertEqual(report["capabilities"]["model_metadata"], "unavailable")
        self.assertEqual(report["runs"][0]["tokens"]["input"], 12)
        self.assertEqual(report["runs"][0]["tool_calls"], 1)
        self.assertEqual(report["runs"][0]["skills"], [])
        self.assertIn("skill attribution is unavailable", " ".join(report["warnings"]))
        self.assertNotIn("Alice", json.dumps(report))

    def test_duplicate_spans_are_not_double_counted(self) -> None:
        chat = span(
            "chat",
            "chat",
            "root",
            2_000_000,
            3_000_000,
            [attribute("gen_ai.usage.input_tokens", 25), attribute("gen_ai.usage.output_tokens", 4)],
        )
        trace = otlp([span("invoke_agent", "root", "", 1_000_000, 4_000_000, []), chat])
        with tempfile.TemporaryDirectory(prefix="agentic-workflow-observability-") as temporary:
            root = Path(temporary)
            first = self.write_json(root, "first.json", trace)
            second = self.write_json(root, "second.json", trace)
            report = ANALYZER.analyze([first, second], {})
        self.assertEqual(report["runs"][0]["tokens"]["input"], 25)
        self.assertIn("deduplicated 2", " ".join(report["warnings"]))

    def test_agent_debug_export_is_labeled_lower_fidelity(self) -> None:
        trace = otlp([span("chat", "chat", "", 1_000_000, 2_000_000, [])])
        trace["copilotChat"] = {"title": "sensitive title", "exporterVersion": ""}
        with tempfile.TemporaryDirectory(prefix="agentic-workflow-observability-") as temporary:
            path = self.write_json(Path(temporary), "debug.json", trace)
            report = ANALYZER.analyze([path], {})
        self.assertEqual(report["runs"][0]["fidelity"], "debug-converted")
        self.assertGreater(report["privacy"]["content_fields_discarded"], 0)
        self.assertNotIn("sensitive title", json.dumps(report))

    def test_separate_debug_exports_do_not_collide_on_synthetic_span_ids(self) -> None:
        trace = otlp([span("chat", "synthetic", "", 1_000_000, 2_000_000, [])])
        trace["copilotChat"] = {"title": "sensitive title", "exporterVersion": ""}
        with tempfile.TemporaryDirectory(prefix="agentic-workflow-observability-") as temporary:
            root = Path(temporary)
            first = self.write_json(root, "debug-1.json", trace)
            second = self.write_json(root, "debug-2.json", trace)
            report = ANALYZER.analyze([first, second], {})
        self.assertEqual(len(report["runs"]), 2)
        self.assertEqual(len({run["run_id"] for run in report["runs"]}), 2)

    def test_unknown_shape_fails_visibly(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agentic-workflow-observability-") as temporary:
            path = self.write_json(Path(temporary), "unknown.json", {"newExporterShape": []})
            with self.assertRaises(ANALYZER.AnalyzerError):
                ANALYZER.analyze([path], {})

    def test_read_error_does_not_echo_sensitive_input_path(self) -> None:
        path = Path("/private/sensitive-customer/missing-trace.json")
        with self.assertRaises(ANALYZER.AnalyzerError) as caught:
            ANALYZER.analyze([path], {})
        self.assertNotIn("sensitive-customer", str(caught.exception))
        self.assertIn("input 1", str(caught.exception))

    def test_json_output_is_deterministic_and_does_not_emit_input_path(self) -> None:
        trace = otlp([span("invoke_agent", "root", "", 1_000_000, 2_000_000, [])])
        with tempfile.TemporaryDirectory(prefix="agentic-workflow-observability-secret-") as temporary:
            path = self.write_json(Path(temporary), "private-name.json", trace)
            first = io.StringIO()
            second = io.StringIO()
            with mock.patch("sys.stdout", first):
                self.assertEqual(ANALYZER.main(["--format", "json", "--tag", "experiment=route-a", str(path)]), 0)
            with mock.patch("sys.stdout", second):
                self.assertEqual(ANALYZER.main(["--format", "json", "--tag", "experiment=route-a", str(path)]), 0)
        self.assertEqual(first.getvalue(), second.getvalue())
        self.assertNotIn("private-name", first.getvalue())
        self.assertNotIn("observability-secret", first.getvalue())
        report = json.loads(first.getvalue())
        self.assertIsNone(report["runs"][0]["tokens"]["input"])
        self.assertIsNone(report["groups"][0]["median_tokens"]["input"])

    def test_invalid_experiment_tag_is_rejected(self) -> None:
        with self.assertRaises(ANALYZER.AnalyzerError):
            ANALYZER._parse_tags(["Bad Key=value"])


if __name__ == "__main__":
    unittest.main()
