"""Synthetic rollout observations; these controls make no model calls."""

import json
from pathlib import Path
import tempfile
import unittest

from evals.native_execution import NativeExecutionMonitor


class NativeExecutionMonitorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home, self.project = self.root / "home", self.root / "project"
        self.project.mkdir()
        (self.home / "sessions").mkdir(parents=True)
        self.trace = self.home / "sessions/parent.jsonl"

    def emit(self, kind, output, path=None):
        with (path or self.trace).open("a") as stream:
            stream.write(
                json.dumps(
                    {
                        "type": "response_item",
                        "payload": {"type": kind, "output": output},
                    }
                )
                + "\n"
            )

    def test_only_observed_outputs_disclosing_canaries_fail(self):
        monitor = NativeExecutionMonitor(
            self.home, self.project, canaries=("hidden-value",)
        )
        self.emit("message", "hidden-value")
        self.emit("custom_tool_call", "hidden-value")
        self.emit("custom_tool_call_output", "cat: canary.txt: Operation not permitted")
        self.assertIsNone(monitor())
        self.emit("custom_tool_call_output", "hidden-value")
        self.assertEqual(monitor(), "isolation-failure")

    def test_child_tool_failure_stops_but_expected_denials_and_git_cache_warnings_do_not(
        self,
    ):
        monitor = NativeExecutionMonitor(self.home, self.project)
        self.emit(
            "custom_tool_call_output",
            "patch rejected: writing is blocked by read-only sandbox",
        )
        self.emit(
            "custom_tool_call_output",
            "git: error: couldn't create cache file (errno=Operation not permitted)",
        )
        self.assertIsNone(monitor())
        child = self.home / "sessions/child.jsonl"
        self.emit(
            "custom_tool_call_output",
            "xcrun: error: invalid active developer path",
            child,
        )
        self.assertEqual(monitor(), "infrastructure-blocked")
        self.assertEqual(monitor.failure["trace"], "sessions/child.jsonl")

    def test_observed_runtime_startup_denials_stop_execution(self):
        for output in (
            "Operation not permitted - /Library/Ruby/Gems/2.6.0/specifications/default (Errno::EPERM)",
            "dyld[4885]: Library not loaded: /System/Library/Perl/5.34/CORE/libperl.dylib (blocked by sandbox)",
        ):
            with self.subTest(output=output):
                self.trace.unlink(missing_ok=True)
                monitor = NativeExecutionMonitor(self.home, self.project)
                self.emit("custom_tool_call_output", output)
                self.assertEqual(monitor(), "infrastructure-blocked")

    def test_partial_rollout_record_is_retried_on_next_poll(self):
        monitor = NativeExecutionMonitor(self.home, self.project)
        self.trace.write_text('{"type":"event_msg",')
        self.assertIsNone(monitor())
        with self.trace.open("a") as stream:
            stream.write('"payload":{"type":"error","message":"quota failure"}}\n')
        self.assertEqual(monitor(), "infrastructure-blocked")

    def test_cli_failure_is_observed_without_rollout_error(self):
        events = self.root / "codex.jsonl"
        events.write_text(
            '{"type":"turn.failed","error":{"message":"quota exceeded"}}\n'
        )
        monitor = NativeExecutionMonitor(self.home, self.project, events=events)
        self.assertEqual(monitor(), "infrastructure-blocked")
        self.assertEqual(monitor.failure["trace"], "codex.jsonl")

    def test_read_only_file_changes_stop_execution(self):
        monitor = NativeExecutionMonitor(self.home, self.project, read_only=True)
        (self.project / "unexpected.txt").write_text("changed")
        self.assertEqual(monitor(), "isolation-failure")

    def test_read_only_git_metadata_changes_stop_execution(self):
        git = self.project / ".git"
        git.mkdir()
        (git / "index").write_bytes(b"original")
        monitor = NativeExecutionMonitor(self.home, self.project, read_only=True)
        (git / "index").write_bytes(b"changed")
        self.assertEqual(monitor(), "isolation-failure")
