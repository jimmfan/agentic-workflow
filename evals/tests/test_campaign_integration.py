"""Exercise real command transport and interrupted checkpoints with synthetic actors.

These are harness controls, not behavioral model evidence. No model, credentials,
network operation, or real project effort is involved.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest
from unittest.mock import patch

from evals.campaign import core
from evals.campaign.revisions import snapshot_files


FAKE_ADAPTER = r"""
import json
from pathlib import Path
import sys

request = json.load(sys.stdin)
raw = Path(request["artifact_dir"])
# A native adapter owns this directory; transport must not pre-populate it.
assert raw.is_dir() and not list(raw.iterdir()), "raw evidence collided with transport"
assert request["settings"]["allow_live"] is True
(raw / "received.json").write_text(json.dumps(request))
mode = request["settings"].get("fake_mode", "complete")
session = request["session_id"] or "synthetic-" + Path(request["session_home"]).name
if mode == "wrong-resume" and request["session_id"]:
    session = "synthetic-unrelated"
trace = raw / "native.jsonl"
trace.write_text(json.dumps({"type": "thread.started", "thread_id": session}) + "\n")
if mode == "malformed":
    print('{"schema":1')
    raise SystemExit(2)
if mode == "blocked":
    response = {"schema": 1, "execution_status": "infrastructure-blocked",
        "session_id": request["session_id"], "response": "",
        "error": "Synthetic sandbox cannot deny controller canary",
        "observations": {"same_session": None}, "traces": [str(trace)]}
    print(json.dumps(response))
    raise SystemExit(2)
(Path(request["workspace"]) / "note.txt").write_text("after\n")
with trace.open("a") as output:
    output.write(json.dumps({"type":"turn.completed","usage":{"input_tokens":9,"output_tokens":2}}) + "\n")
response = {"schema": 1, "execution_status": "completed", "session_id": session,
    "response": "Synthetic adapter updated note.txt.", "error": None,
    "observations": {"same_session": request["session_id"] is not None}, "traces": [str(trace)]}
print(json.dumps(response))
print("Synthetic transport diagnostic", file=sys.stderr)
raise SystemExit(2 if mode == "false-completion" else 0)
"""


class CampaignIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="campaign-integration-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.campaign = self.root / "campaign"
        fixture = self.root / "fixture"
        fixture.mkdir()
        (fixture / "note.txt").write_text("before\n")
        self.adapter = self.root / "fake_adapter.py"
        self.adapter.write_text(textwrap.dedent(FAKE_ADAPTER))
        self.scenario = {
            "schema": 1,
            "id": "notes",
            "title": "Synthetic notes",
            "question": "Does the runner retain evidence?",
            "fixture": "fixture",
            "applicability": "common-outcome",
            "turns": [self.turn("T1")],
        }
        self.spec = {
            "schema": 1,
            "name": "transport-controls",
            "question": "Does transport preserve outcomes?",
            "scenarios": ["scenario.json"],
            "conditions": [{"id": "candidate", "ref": "main"}],
            "repetitions": 1,
            "seed": 7,
            "limits": {"max_turns": 10, "turn_seconds": 5, "campaign_seconds": 120},
            "host": {
                "kind": "command",
                "command": [sys.executable, str(self.adapter)],
                "model": "synthetic",
                "reasoning_effort": "synthetic",
                "settings": {},
            },
        }

    def turn(self, name, session="writer"):
        return {
            "id": name,
            "session": session,
            "request": "Update note.txt to after.",
            "allowed_writes": ["note.txt"],
            "checks": [
                {
                    "id": "note",
                    "kind": "file_equals",
                    "path": "note.txt",
                    "value": "after\n",
                }
            ],
        }

    def freeze(self):
        core.dump(self.root / "scenario.json", self.scenario)
        core.dump(self.root / "spec.json", self.spec)

        def prepare(repo, ref, destination, **kwargs):
            destination.mkdir()
            (destination / "AGENTS.md").write_text("Synthetic framework\n")
            return {
                "ref": ref,
                "commit": "a" * 40,
                "version": "0.0.0",
                "layout": "test",
                "files": snapshot_files(destination),
                "warnings": [],
                "overlays": [],
            }

        with patch.object(core, "prepare_revision", side_effect=prepare):
            return core.freeze_campaign(self.root / "spec.json", self.campaign)

    def state(self):
        return json.loads((self.campaign / "state.json").read_text())

    def directory(self, index=1):
        return self.campaign / "runs/run-0001" / f"{index:03d}"

    def response(self, index=1):
        return json.loads((self.directory(index) / "response.json").read_text())

    def test_real_command_transport_retains_output_and_separates_raw(self):
        self.freeze()
        report = core.run_campaign(self.campaign, allow_live=True)
        self.assertEqual(report["rows"][0]["verdict"], "PASS")
        directory = self.directory()
        transported = json.loads(
            (directory / "adapter-process/codex.jsonl").read_text()
        )
        self.assertEqual(transported, self.response())
        self.assertEqual(
            (directory / "adapter-process/stderr.txt").read_text().strip(),
            "Synthetic transport diagnostic",
        )
        self.assertTrue((directory / "raw/native.jsonl").is_file())
        self.assertFalse((directory / "raw/codex.jsonl").exists())
        received = json.loads((directory / "raw/received.json").read_text())
        self.assertEqual(received["prompt"], self.scenario["turns"][0]["request"])
        self.assertNotIn("checks", received)
        self.assertNotIn("requirement", received)
        self.assertEqual(received["model"], "synthetic")
        self.assertEqual(self.state()["launched_turns"], 1)

    def test_exact_resume_and_fresh_reader_identity_through_real_transport(self):
        self.scenario["turns"].extend([self.turn("T2"), self.turn("T3", "reader")])
        self.freeze()
        report = core.run_campaign(self.campaign, allow_live=True)
        self.assertEqual(
            [row["execution_status"] for row in report["rows"]], ["completed"] * 3
        )
        requests = [
            json.loads((self.directory(i) / "raw/received.json").read_text())
            for i in range(1, 4)
        ]
        self.assertIsNone(requests[0]["session_id"])
        self.assertEqual(requests[1]["session_id"], "synthetic-writer")
        self.assertEqual(requests[1]["session_home"], requests[0]["session_home"])
        self.assertIsNone(requests[2]["session_id"])
        self.assertNotEqual(requests[2]["session_home"], requests[0]["session_home"])
        self.assertEqual(
            self.state()["runs"]["run-0001"]["sessions"],
            {"writer": "synthetic-writer", "reader": "synthetic-reader"},
        )
        checkpoints = [
            json.loads((self.directory(i) / "checkpoint.json").read_text())
            for i in range(1, 4)
        ]
        self.assertEqual(
            [c["continuation"] for c in checkpoints], ["fresh", "resumed", "fresh"]
        )

    def test_adapter_exit_two_preserves_block_reason_and_evidence(self):
        self.spec["host"]["settings"]["fake_mode"] = "blocked"
        self.scenario["turns"].append(self.turn("T2"))
        self.freeze()
        report = core.run_campaign(self.campaign, allow_live=True)
        response = self.response()
        self.assertEqual(response["execution_status"], "infrastructure-blocked")
        self.assertEqual(
            response["error"], "Synthetic sandbox cannot deny controller canary"
        )
        self.assertEqual(response["observations"], {"same_session": None})
        self.assertEqual(len(response["traces"]), 1)
        self.assertTrue(Path(response["traces"][0]).is_file())
        self.assertEqual(report["rows"][0]["verdict"], "INCONCLUSIVE")
        self.assertEqual(report["rows"][1]["execution_status"], "unexecuted")
        self.assertEqual(self.state()["runs"]["run-0001"]["status"], "stopped")
        with patch.object(
            core, "bounded_process", side_effect=AssertionError("must not retry")
        ):
            core.run_campaign(self.campaign, allow_live=True)
        self.assertEqual(self.state()["launched_turns"], 1)

    def test_failing_exit_cannot_claim_completed(self):
        self.spec["host"]["settings"]["fake_mode"] = "false-completion"
        self.freeze()
        core.run_campaign(self.campaign, allow_live=True)
        self.assertEqual(self.response()["execution_status"], "error")
        self.assertIn("failing exit code", self.response()["error"])
        self.assertEqual(self.state()["runs"]["run-0001"]["status"], "stopped")

    def test_malformed_adapter_json_is_recorded_as_error(self):
        self.spec["host"]["settings"]["fake_mode"] = "malformed"
        self.freeze()
        core.run_campaign(self.campaign, allow_live=True)
        self.assertEqual(self.response()["execution_status"], "error")
        self.assertTrue(
            (self.directory() / "adapter-process/codex.jsonl")
            .read_text()
            .startswith('{"schema":1')
        )
        self.assertIsNone(self.state()["runs"]["run-0001"]["pending"])

    def test_mismatched_resume_is_stopped_without_third_turn(self):
        self.spec["host"]["settings"]["fake_mode"] = "wrong-resume"
        self.scenario["turns"].extend([self.turn("T2"), self.turn("T3")])
        self.freeze()
        report = core.run_campaign(self.campaign, allow_live=True)
        self.assertEqual(self.response(2)["execution_status"], "error")
        self.assertIn("session identity", self.response(2)["error"])
        self.assertEqual(report["rows"][2]["execution_status"], "unexecuted")
        self.assertEqual(self.state()["launched_turns"], 2)

    def test_unknown_run_selector_rejects_without_execution(self):
        self.freeze()
        with patch.object(
            core, "bounded_process", side_effect=AssertionError("must not execute")
        ):
            with self.assertRaisesRegex(ValueError, "Unknown run"):
                core.run_campaign(self.campaign, allow_live=True, run_id="run-9999")
        self.assertEqual(self.state()["launched_turns"], 0)

    def test_live_execution_needs_explicit_flag(self):
        self.freeze()
        with patch.object(
            core, "bounded_process", side_effect=AssertionError("must not execute")
        ):
            with self.assertRaisesRegex(ValueError, "allow-live"):
                core.run_campaign(self.campaign)
        self.assertEqual(self.state()["launched_turns"], 0)

    def test_recover_pending_subject_records_failure_without_retry(self):
        self.scenario["turns"].append(self.turn("T2"))
        self.freeze()
        request = core.begin_turn(self.campaign, "run-0001")
        (Path(request["workspace"]) / "note.txt").write_text("partial\n")
        with patch.object(
            core, "bounded_process", side_effect=AssertionError("must not execute")
        ):
            recovered = core.recover_turn(
                self.campaign, "run-0001", "Synthetic worker stopped before response"
            )
            report = core.run_campaign(self.campaign, allow_live=True)
        self.assertEqual(recovered["execution_status"], "error")
        self.assertEqual(
            self.response()["error"], "Synthetic worker stopped before response"
        )
        state = self.state()
        self.assertEqual(state["launched_turns"], 1)
        self.assertEqual(state["runs"]["run-0001"]["next"], 1)
        self.assertIsNone(state["runs"]["run-0001"]["pending"])
        self.assertEqual(state["runs"]["run-0001"]["status"], "stopped")
        self.assertEqual(report["rows"][1]["execution_status"], "unexecuted")
        with self.assertRaisesRegex(ValueError, "complete or stopped"):
            core.begin_turn(self.campaign, "run-0001")

    def test_recover_committed_checkpoint_does_not_duplicate_turn(self):
        self.scenario["turns"].append(self.turn("T2"))
        self.freeze()
        request = core.begin_turn(self.campaign, "run-0001")
        (Path(request["workspace"]) / "note.txt").write_text("after\n")
        actual_dump = core.dump

        def interrupted_state_write(path, data):
            if path == self.campaign / "state.json":
                raise OSError("Synthetic interruption after checkpoint")
            return actual_dump(path, data)

        response = {
            "schema": 1,
            "execution_status": "completed",
            "session_id": "synthetic-writer",
            "response": "Synthetic completed response",
            "traces": [],
        }
        with patch.object(core, "dump", side_effect=interrupted_state_write):
            with self.assertRaisesRegex(OSError, "after checkpoint"):
                core.finish_turn(self.campaign, "run-0001", response)
        checkpoint_path = self.directory() / "checkpoint.json"
        saved = checkpoint_path.read_bytes()
        self.assertIsNotNone(self.state()["runs"]["run-0001"]["pending"])
        with patch.object(
            core, "bounded_process", side_effect=AssertionError("must not execute")
        ):
            recovered = core.recover_turn(
                self.campaign, "run-0001", "Checkpoint saved; state write interrupted"
            )
        self.assertEqual(recovered["next"], 1)
        self.assertEqual(recovered["status"], "ready")
        self.assertEqual(recovered["sessions"], {"writer": "synthetic-writer"})
        self.assertEqual(self.state()["launched_turns"], 1)
        self.assertEqual(checkpoint_path.read_bytes(), saved)
        reconciled = (self.campaign / "state.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "No interrupted attempt"):
            core.recover_turn(self.campaign, "run-0001", "Repeat recovery")
        self.assertEqual((self.campaign / "state.json").read_bytes(), reconciled)
        next_request = core.begin_turn(self.campaign, "run-0001")
        self.assertEqual(next_request["session_id"], "synthetic-writer")
        self.assertEqual(self.state()["launched_turns"], 2)
        self.assertEqual(checkpoint_path.read_bytes(), saved)

    def test_recovery_stops_capture_failure_without_deleting_partial_evidence(self):
        self.scenario["turns"].append(self.turn("T2"))
        self.freeze()
        request = core.begin_turn(self.campaign, "run-0001")
        note = Path(request["workspace"]) / "note.txt"
        note.write_text("partial effect must remain\n")
        before_evidence = (self.directory() / "before.zip").read_bytes()
        raw = Path(request["artifact_dir"]) / "partial.log"
        raw.write_text("Synthetic interrupted worker trace\n")
        with patch.object(
            core, "_capture", side_effect=OSError("Synthetic storage read failure")
        ):
            with patch.object(
                core, "bounded_process", side_effect=AssertionError("must not execute")
            ):
                recovered = core.recover_turn(
                    self.campaign, "run-0001", "Worker stopped; capture unavailable"
                )
        self.assertEqual(recovered["status"], "stopped")
        self.assertIsNone(recovered["pending"])
        failure = recovered["failed_attempt"]
        self.assertEqual(failure["index"], 0)
        self.assertEqual(failure["execution_status"], "error")
        self.assertIn("storage read failure", failure["error"])
        self.assertEqual(note.read_text(), "partial effect must remain\n")
        self.assertEqual(raw.read_text(), "Synthetic interrupted worker trace\n")
        self.assertEqual(
            (self.directory() / "before.zip").read_bytes(), before_evidence
        )
        self.assertFalse((self.directory() / "checkpoint.json").exists())
        with patch.object(
            core, "bounded_process", side_effect=AssertionError("must not retry")
        ):
            report = core.run_campaign(self.campaign, allow_live=True)
        self.assertEqual(report["rows"][0]["execution_status"], "error")
        self.assertEqual(report["rows"][0]["verdict"], "INCONCLUSIVE")
        self.assertEqual(report["rows"][1]["execution_status"], "unexecuted")
        self.assertEqual(report["totals"]["candidate"]["execution_failures"], 1)
        self.assertEqual(report["totals"]["candidate"]["unexecuted"], 1)
        self.assertEqual(self.state()["launched_turns"], 1)

    def test_recovery_rejects_tampered_checkpoint(self):
        self.freeze()
        request = core.begin_turn(self.campaign, "run-0001")
        (Path(request["workspace"]) / "note.txt").write_text("after\n")
        pending_state = self.state()
        core.finish_turn(
            self.campaign,
            "run-0001",
            {
                "schema": 1,
                "execution_status": "completed",
                "session_id": "synthetic-writer",
                "response": "Synthetic completed response",
            },
        )
        core.dump(self.campaign / "state.json", pending_state)
        checkpoint_path = self.directory() / "checkpoint.json"
        checkpoint = json.loads(checkpoint_path.read_text())
        checkpoint["turn_id"] = "invented-turn"
        core.dump(checkpoint_path, checkpoint)
        with self.assertRaisesRegex(ValueError, "identity"):
            core.recover_turn(self.campaign, "run-0001", "Synthetic interruption")
        self.assertIsNotNone(self.state()["runs"]["run-0001"]["pending"])


if __name__ == "__main__":
    unittest.main()
