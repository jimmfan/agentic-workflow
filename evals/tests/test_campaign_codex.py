"""Native adapter contract tests; fake CLI and runner never call a model."""

from pathlib import Path
import json
import os
import shlex
import tempfile
import unittest
from unittest import mock

from evals.campaign import codex


class CodexAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="campaign-native-tests-")
        self.root = Path(self.temp.name)
        self.workspace = self.root / "consumer"
        self.workspace.mkdir()
        self.binary = self.root / "codex"
        self.binary.write_text("synthetic executable")
        self.auth = self.root / "auth.json"
        self.auth.write_text('{"synthetic":"credential"}')
        self.request = {
            "schema": 1,
            "workspace": str(self.workspace),
            "artifact_dir": str(self.root / "evidence"),
            "session_home": str(self.root / "session"),
            "session_id": None,
            "prompt": "Implement the requested behavior.",
            "model": "synthetic-model",
            "reasoning_effort": "high",
            "timeout_seconds": 30,
            "settings": {
                "binary": str(self.binary),
                "auth_file": str(self.auth),
                "allow_live": True,
            },
        }
        self.sid = "00000000-1111-2222-3333-444444444444"

    def tearDown(self):
        self.temp.cleanup()

    def events(self, sid=None):
        return [
            {"type": "thread.started", "thread_id": sid or self.sid},
            {"type": "turn.started"},
            {
                "type": "item.completed",
                "item": {"type": "agent_message", "text": "Done."},
            },
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 150000, "output_tokens": 42},
            },
        ]

    def fake_runner(self, command, *, raw, **kwargs):
        self.command = command
        self.env = kwargs["env"]
        self.assertEqual(Path(self.env["HOME"]), self.root / "session/user-home")
        self.assertEqual(Path(self.env["CODEX_HOME"]), self.root / "session/codex-home")
        self.assertEqual(kwargs["prompt"], self.request["prompt"])
        self.assertTrue((self.root / "session/codex-home/auth.json").is_file())
        (raw / "codex.jsonl").write_text(
            "\n".join(json.dumps(event) for event in self.events()) + "\n"
        )
        (raw / "stderr.txt").write_text("")
        return "completed", 0, 0.1

    def invoke(self, **patches):
        defaults = {
            "_inspect_cli": mock.Mock(return_value="codex-cli fake"),
            "_preflight": mock.Mock(return_value={"returncode": 0}),
            "bounded_process": self.fake_runner,
        }
        defaults.update(patches)
        with mock.patch.multiple(codex, **defaults):
            return codex.run(self.request)

    def test_fresh_and_exact_native_resume(self):
        first = self.invoke()
        self.assertEqual(first["execution_status"], "completed")
        self.assertEqual(first["session_id"], self.sid)
        self.assertFalse(first["observations"]["same_session"])
        self.assertIsNone(first["observations"]["active_context_tokens"])
        self.assertIsNone(first["observations"]["compaction_events"])
        self.assertIsNone(first["observations"]["model"])
        self.assertNotIn("--ephemeral", self.command)
        self.assertNotIn("--last", self.command)
        self.assertIn('model="synthetic-model"', self.command)
        self.assertIn('model_reasoning_effort="high"', self.command)
        self.assertIn('approval_policy="never"', self.command)
        self.assertIn("agents.enabled=true", self.command)
        self.assertIn("agents.max_concurrent_threads_per_session=2", self.command)
        self.assertIn("--ignore-user-config", self.command)
        self.assertIn("--ignore-rules", self.command)
        self.assertNotIn("--sandbox", self.command)
        self.assertFalse((self.root / "session/codex-home/auth.json").exists())
        self.request.update(session_id=self.sid, artifact_dir=str(self.root / "second"))
        second = self.invoke()
        self.assertEqual(second["execution_status"], "completed")
        self.assertTrue(second["observations"]["same_session"])
        self.assertEqual(self.command[-3:], ["resume", self.sid, "-"])

    def test_cli_capability_check_rejects_unsupported_binary(self):
        env = {"HOME": str(self.root)}
        responses = [mock.Mock(stdout="codex-cli old"), mock.Mock(stdout="exec --json")]
        with mock.patch.object(
            codex.subprocess, "run", side_effect=responses
        ) as process:
            with self.assertRaisesRegex(ValueError, "Unsupported Codex"):
                codex._inspect_cli(self.binary, env)
        self.assertEqual(process.call_count, 2)
        self.assertEqual(process.call_args_list[0].args[0][-1], "--version")

    def test_observed_model_mismatch_is_infrastructure_blocked(self):
        mismatch = (
            {
                "model": "different",
                "reasoning_effort": "high",
                "compaction_events": None,
                "active_context_tokens": None,
            },
            [],
        )
        result = self.invoke(_rollout_observations=mock.Mock(return_value=mismatch))
        self.assertEqual(result["execution_status"], "infrastructure-blocked")
        self.assertIn("Observed model", result["error"])
        self.assertFalse((self.root / "session/codex-home/auth.json").exists())

    def test_subagents_are_explicit_restricted_host_ablation(self):
        self.request["settings"]["allow_subagents"] = False
        result = self.invoke()
        self.assertEqual(result["execution_status"], "completed")
        self.assertIn("agents.enabled=false", self.command)
        record = json.loads((self.root / "evidence/invocation.json").read_text())
        self.assertFalse(record["host_capabilities"]["subagents_enabled_requested"])
        self.assertIsNone(record["host_capabilities"]["subagent_model_calls_observed"])
        self.assertEqual(
            record["host_capabilities"]["sandbox_probe_scope"], "parent command only"
        )
        self.request.update(session_id=self.sid, artifact_dir=str(self.root / "second"))
        self.request["settings"]["allow_subagents"] = True
        self.assertIn("changed", self.invoke()["error"])

    def test_subagent_flag_rejects_string_truthiness(self):
        self.request["settings"]["allow_subagents"] = "false"
        self.assertIn("boolean", codex.run(self.request)["error"])

    def test_requires_opt_in_and_rejects_unknown_settings(self):
        self.request["settings"].pop("allow_live")
        self.assertIn("allow_live", codex.run(self.request)["error"])
        self.request["settings"]["sandbox"] = "danger-full-access"
        self.assertIn("Unsupported", codex.run(self.request)["error"])

    def test_preflight_never_reads_auth_or_launches_model(self):
        self.request["settings"] = {
            "binary": str(self.binary),
            "preflight_only": True,
            "auth_file": "/missing/auth.json",
        }
        runner = mock.Mock(side_effect=AssertionError("model must not run"))
        result = self.invoke(bounded_process=runner)
        self.assertEqual(result["execution_status"], "completed")
        runner.assert_not_called()
        self.assertFalse((self.root / "session/codex-home/auth.json").exists())

    def test_setup_consumes_the_same_turn_time_budget(self):
        runner = mock.Mock(side_effect=AssertionError("No time remains for a model"))
        with mock.patch.object(codex.time, "monotonic", side_effect=[0, 31]):
            result = self.invoke(bounded_process=runner)
        self.assertEqual(result["execution_status"], "infrastructure-blocked")
        self.assertIn("time budget", result["error"])
        runner.assert_not_called()
        self.assertFalse((self.root / "session/codex-home/auth.json").exists())

    def test_failed_isolation_precedes_credentials_and_model(self):
        runner = mock.Mock()
        preflight = mock.Mock(side_effect=ValueError("denied-path-readable"))
        result = self.invoke(_preflight=preflight, bounded_process=runner)
        self.assertEqual(result["execution_status"], "infrastructure-blocked")
        self.assertIn("denied-path-readable", result["error"])
        runner.assert_not_called()
        self.assertFalse((self.root / "session/codex-home/auth.json").exists())

    def test_model_effort_and_cli_cannot_change_on_resume(self):
        self.invoke()
        self.request.update(
            session_id=self.sid, model="another", artifact_dir=str(self.root / "second")
        )
        result = self.invoke()
        self.assertIn("changed", result["error"])

    def test_unknown_session_is_not_replaced_with_last(self):
        self.request["session_id"] = self.sid
        result = self.invoke()
        self.assertIn("does not match", result["error"])

    def test_fresh_session_cannot_reuse_existing_home(self):
        self.invoke()
        self.request["artifact_dir"] = str(self.root / "second")
        self.assertIn("does not match", self.invoke()["error"])

    def test_timeout_cleans_credential_and_keeps_evidence(self):
        def timeout(*args, raw, **kwargs):
            (raw / "codex.jsonl").write_text("")
            (raw / "stderr.txt").write_text("Timeout")
            return "timeout", -9, 30

        result = self.invoke(bounded_process=timeout)
        self.assertEqual(result["execution_status"], "timeout")
        self.assertFalse((self.root / "session/codex-home/auth.json").exists())
        self.assertTrue((self.root / "evidence/invocation.json").exists())

    def test_runner_exception_cleans_credential(self):
        result = self.invoke(
            bounded_process=mock.Mock(side_effect=OSError("cannot start"))
        )
        self.assertEqual(result["execution_status"], "infrastructure-blocked")
        self.assertFalse((self.root / "session/codex-home/auth.json").exists())

    def test_no_ambient_credentials_passed_to_child(self):
        with mock.patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "sentinel",
                "GH_TOKEN": "sentinel",
                "SECRET": "sentinel",
            },
        ):
            self.invoke()
        self.assertNotIn("OPENAI_API_KEY", self.env)
        self.assertNotIn("GH_TOKEN", self.env)
        self.assertNotIn("SECRET", self.env)

    def test_incomplete_failed_and_wrong_session_traces(self):
        path = self.root / "trace.jsonl"
        cases = [
            self.events()[:-1],
            self.events() + [{"type": "turn.started"}],
            self.events() + [{"type": "turn.failed"}],
            self.events() + [{"type": "error", "message": "quota"}],
            [{"type": "turn.completed"}],
            self.events("wrong-id"),
        ]
        for events in cases:
            with self.subTest(events=events):
                path.write_text("\n".join(map(json.dumps, events)))
                with self.assertRaises(ValueError):
                    codex.parse_execution(path, self.sid)
        path.write_text('{"type":"thread.started"')
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            codex.parse_execution(path)

    def test_rollout_observations_are_per_turn_not_cumulative_usage(self):
        home = self.root / "session"
        session_dir = home / "codex-home/sessions/2026"
        session_dir.mkdir(parents=True)
        rollout = session_dir / "rollout.jsonl"
        header = [
            {"type": "session_meta", "payload": {"id": self.sid}},
            {"type": "compacted", "payload": {}},
            {"type": "turn_context", "payload": {"model": "old", "effort": "low"}},
        ]
        rollout.write_text("\n".join(map(json.dumps, header)) + "\n")
        offset = rollout.stat().st_size
        current = [
            {
                "type": "turn_context",
                "payload": {"model": "observed-model", "effort": "high"},
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"input_tokens": 99999}},
                },
            },
            {"type": "compacted", "payload": {}},
        ]
        with rollout.open("a") as file:
            file.write("\n".join(map(json.dumps, current)) + "\n")
        artifact = self.root / "evidence"
        artifact.mkdir()
        observed, traces = codex._rollout_observations(
            home, artifact, self.sid, {str(rollout): offset}
        )
        self.assertEqual(observed["compaction_events"], 1)
        self.assertEqual(observed["model"], "observed-model")
        self.assertEqual(observed["reasoning_effort"], "high")
        self.assertIsNone(observed["active_context_tokens"])
        self.assertEqual(len(traces), 1)

    def test_preflight_commands_deny_canaries_and_clean_probe(self):
        home, artifact = self.root / "session", self.root / "evidence"
        home.mkdir()
        artifact.mkdir()
        config, env = codex._settings(
            self.request, self.workspace, home, artifact, self.binary
        )

        def sandbox(command, raw, **kwargs):
            self.assertEqual(command[1], "sandbox")
            self.assertIn("-P", command)
            self.assertIn("denied-path-readable", command[-1])
            self.assertIn("credential-canary", command[-1])
            self.assertTrue((artifact / "controller-canary.txt").exists())
            self.assertFalse((home / "codex-home/auth.json").exists())
            (raw / "codex.jsonl").write_text("denied-path-readable")
            (raw / "stderr.txt").write_text("")
            return "infrastructure-blocked", 11, 0.1

        with mock.patch.object(codex, "bounded_process", side_effect=sandbox):
            with self.assertRaisesRegex(ValueError, "no credentials"):
                codex._preflight(
                    self.binary, config, self.workspace, home, artifact, env
                )
        self.assertFalse(list(self.workspace.glob(".campaign-probe-*")))
        self.assertFalse((artifact / "controller-canary.txt").exists())
        self.assertTrue((artifact / "preflight.json").is_file())

    def test_preflight_child_uses_controller_resolved_interpreter(self):
        home, artifact = self.root / "session", self.root / "evidence"
        home.mkdir()
        artifact.mkdir()
        interpreter = self.root / "runtime with spaces" / "bin" / "python"
        interpreter.parent.mkdir(parents=True)
        interpreter.write_text("synthetic interpreter; never executed")
        alias = self.root / "python alias"
        alias.symlink_to(interpreter)
        expected = str(interpreter.resolve())
        child_alias = self.root / "unresolved child alias"

        def sandbox(command, raw, **kwargs):
            self.assertEqual(kwargs["limits"], {"seconds": 30, "output_bytes": 200_000})
            tokens = shlex.split(command[-1])
            self.assertEqual(tokens[-3:-1], ["python", "-c"])
            with (
                mock.patch.object(codex.sys, "executable", str(child_alias)),
                mock.patch.object(Path, "resolve", return_value=child_alias) as resolve,
                mock.patch.object(codex.subprocess, "run") as child,
            ):
                exec(tokens[-1], {})
            child.assert_called_once_with([expected, "-c", "pass"], check=True)
            resolve.assert_not_called()
            (raw / "codex.jsonl").write_text("")
            (raw / "stderr.txt").write_text("")
            return "completed", 0, 0.1

        with mock.patch.object(codex.sys, "executable", str(alias)):
            config, env = codex._settings(
                self.request, self.workspace, home, artifact, self.binary
            )
            with mock.patch.object(codex, "bounded_process", side_effect=sandbox):
                result = codex._preflight(
                    self.binary, config, self.workspace, home, artifact, env
                )
        self.assertEqual(result["returncode"], 0)

    def test_preflight_unresolved_controller_interpreter_stops_before_launch(self):
        home, artifact = self.root / "session", self.root / "evidence"
        home.mkdir()
        artifact.mkdir()
        config, env = codex._settings(
            self.request, self.workspace, home, artifact, self.binary
        )
        with (
            mock.patch.object(codex.sys, "executable", str(self.root / "missing")),
            mock.patch.object(codex, "bounded_process") as runner,
        ):
            with self.assertRaises(FileNotFoundError):
                codex._preflight(
                    self.binary, config, self.workspace, home, artifact, env
                )
        runner.assert_not_called()
        self.assertFalse(list(self.workspace.glob(".campaign-probe-*")))
        self.assertFalse((artifact / "controller-canary.txt").exists())

    def test_preserves_existing_lock_and_artifacts(self):
        self.invoke()
        artifact = self.root / "evidence"
        original = (artifact / "invocation.json").read_bytes()
        self.assertIn("must be empty", self.invoke()["error"])
        self.assertEqual((artifact / "invocation.json").read_bytes(), original)
        self.request.update(artifact_dir=str(self.root / "second"), session_id=self.sid)
        lock = self.root / "session/.campaign-lock"
        lock.mkdir()
        self.assertEqual(self.invoke()["execution_status"], "infrastructure-blocked")
        self.assertTrue(lock.exists())

    def test_rejects_ancestor_instructions_or_consumer_config(self):
        (self.root / "AGENTS.md").write_text("Controller instructions")
        self.assertIn("ancestor", self.invoke()["error"])
        (self.root / "AGENTS.md").unlink()
        (self.workspace / ".codex").mkdir()
        (self.workspace / ".codex/config.toml").write_text(
            'sandbox_mode="danger-full-access"'
        )
        self.assertIn("override", self.invoke()["error"])

    def test_rejects_non_disjoint_and_nonempty_unowned_home(self):
        self.request["session_home"] = str(self.workspace / "session")
        self.assertIn("disjoint", self.invoke()["error"])
        self.request["session_home"] = str(self.root / "session")
        home = self.root / "session"
        home.mkdir()
        (home / "real-file").write_text("Do not touch")
        self.assertIn("unowned", self.invoke()["error"])
        self.assertEqual((home / "real-file").read_text(), "Do not touch")


if __name__ == "__main__":
    unittest.main()
