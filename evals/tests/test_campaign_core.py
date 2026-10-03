"""Public campaign lifecycle controls; synthetic responses are not live evidence."""

from __future__ import annotations

import json
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from evals.campaign import core
from evals.campaign.__main__ import main
from evals.campaign.schema import load_spec, validate_scenario
from evals.campaign.revisions import snapshot_files


class CampaignControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="campaign-controls-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = self.root / "fixture"
        self.fixture.mkdir()
        (self.fixture / "note.txt").write_text("before\n")
        self.scenario = {
            "schema": 1,
            "id": "notes",
            "title": "Notes",
            "question": "Does meaning survive?",
            "fixture": "fixture",
            "applicability": "common-outcome",
            "turns": [
                {
                    "id": "T1",
                    "session": "writer",
                    "request": "Change note.txt to after.",
                    "allowed_writes": ["note.txt"],
                    "checks": [
                        {
                            "id": "note",
                            "kind": "file_equals",
                            "path": "note.txt",
                            "value": "after\n",
                        },
                        {
                            "id": "meaning",
                            "kind": "semantic",
                            "requirement": "Saved note says after",
                            "evidence_scope": "saved",
                        },
                    ],
                }
            ],
        }
        self.spec = {
            "schema": 1,
            "name": "controls",
            "question": "Does evidence constrain verdicts?",
            "scenarios": ["scenario.json"],
            "conditions": [{"id": "candidate", "ref": "main"}],
            "repetitions": 1,
            "seed": 2,
            "limits": {"max_turns": 20, "turn_seconds": 5, "campaign_seconds": 120},
            "host": {
                "kind": "manual",
                "model": "unavailable",
                "reasoning_effort": "unavailable",
            },
        }
        self.campaign = self.root / "campaign"

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

    def finish(self, run="run-0001", session="subject-one", status="completed"):
        request = core.begin_turn(self.campaign, run)
        (Path(request["workspace"]) / "note.txt").write_text("after\n")
        return core.finish_turn(
            self.campaign,
            run,
            {
                "schema": 1,
                "execution_status": status,
                "session_id": session,
                "response": "Updated the note.",
                "traces": [],
            },
        )

    def review(self):
        packet = core.grading_packet(self.campaign)
        return {
            "packet_sha256": core.fingerprint(packet),
            "reviewer": "independent-control",
            "items": [
                {
                    "id": "run-0001/T1",
                    "checks": {
                        "meaning": {
                            "verdict": "PASS",
                            "rationale": "Saved artifact contains the requested text.",
                            "evidence": [{"path": "note.txt", "quote": "after"}],
                        }
                    },
                }
            ],
        }

    def test_complete_cycle_requires_semantic_review(self):
        self.freeze()
        self.assertEqual(
            core.report_campaign(self.campaign)["totals"]["candidate"]["unexecuted"], 1
        )
        self.finish()
        self.assertEqual(
            core.report_campaign(self.campaign)["rows"][0]["verdict"], "INCONCLUSIVE"
        )
        report = core.apply_review(self.campaign, self.review())
        self.assertEqual(report["rows"][0]["verdict"], "PASS")

    def test_bad_write_is_failure_even_after_timeout_and_favorable_review(self):
        self.freeze()
        request = core.begin_turn(self.campaign, "run-0001")
        (Path(request["workspace"]) / "unrelated.txt").write_text("unauthorized")
        core.finish_turn(
            self.campaign,
            "run-0001",
            {
                "schema": 1,
                "execution_status": "timeout",
                "session_id": None,
                "response": "",
            },
        )
        report = core.report_campaign(self.campaign)
        self.assertEqual(report["rows"][0]["verdict"], "FAIL")
        self.assertEqual(report["totals"]["candidate"]["execution_failures"], 1)

    def test_missing_semantic_review_never_passes(self):
        self.freeze()
        self.finish()
        review = self.review()
        review["items"] = []
        self.assertEqual(
            core.apply_review(self.campaign, review)["rows"][0]["verdict"],
            "INCONCLUSIVE",
        )

    def test_stale_review_and_fabricated_citations_rejected(self):
        self.freeze()
        self.finish()
        review = self.review()
        review["packet_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "does not match"):
            core.apply_review(self.campaign, review)
        review = self.review()
        review["items"][0]["checks"]["meaning"]["evidence"][0]["quote"] = "invented"
        with self.assertRaisesRegex(ValueError, "citation"):
            core.apply_review(self.campaign, review)

    def test_saved_claim_cannot_pass_from_response_only(self):
        self.freeze()
        self.finish()
        review = self.review()
        review["items"][0]["checks"]["meaning"]["evidence"] = [
            {"path": "@response", "quote": "Updated"}
        ]
        with self.assertRaisesRegex(ValueError, "saved project artifact"):
            core.apply_review(self.campaign, review)

    def test_stored_review_is_revalidated(self):
        self.freeze()
        self.finish()
        review = self.review()
        core.apply_review(self.campaign, review)
        review["items"][0]["checks"]["meaning"]["evidence"] = []
        core.dump(self.campaign / "reviews" / f"{review['packet_sha256']}.json", review)
        with self.assertRaisesRegex(ValueError, "evidence"):
            core.report_campaign(self.campaign)

    def test_checkpoint_verdict_and_identity_cannot_be_overridden(self):
        self.freeze()
        self.finish()
        path = self.campaign / "runs/run-0001/001/checkpoint.json"
        checkpoint = json.loads(path.read_text())
        checkpoint["checks"][0]["verdict"] = "FAIL"
        core.dump(path, checkpoint)
        with self.assertRaisesRegex(ValueError, "judgments differ"):
            core.report_campaign(self.campaign)
        checkpoint["run_id"] = "run-9999"
        core.dump(path, checkpoint)
        with self.assertRaisesRegex(ValueError, "identity"):
            core.report_campaign(self.campaign)

    def test_freeze_detects_input_and_tooling_drift(self):
        self.freeze()
        (self.campaign / "inputs/notes/fixture/note.txt").write_text("changed")
        with self.assertRaisesRegex(ValueError, "drift"):
            core.begin_turn(self.campaign, "run-0001")

    def test_pending_turn_cannot_be_silently_retried(self):
        self.freeze()
        core.begin_turn(self.campaign, "run-0001")
        with self.assertRaisesRegex(ValueError, "already pending"):
            core.begin_turn(self.campaign, "run-0001")

    def test_pending_inputs_are_bound_at_launch(self):
        self.freeze()
        core.begin_turn(self.campaign, "run-0001")
        path = self.campaign / "runs/run-0001/001/request.json"
        request = json.loads(path.read_text())
        request["prompt"] = "Different test"
        core.dump(path, request)
        with self.assertRaisesRegex(ValueError, "Pending attempt inputs changed"):
            core.finish_turn(
                self.campaign,
                "run-0001",
                {
                    "schema": 1,
                    "execution_status": "completed",
                    "session_id": "one",
                    "response": "Done",
                },
            )

    def test_independent_runs_cannot_reuse_a_session(self):
        self.spec["repetitions"] = 2
        self.freeze()
        self.finish(session="same")
        result = self.finish(run="run-0002", session="same")
        self.assertEqual(result["execution_status"], "error")

    def test_fresh_reader_cannot_reuse_writer_session(self):
        self.scenario["turns"].append(
            {**self.scenario["turns"][0], "id": "T2", "session": "reader"}
        )
        self.freeze()
        self.finish(session="same")
        result = self.finish(session="same")
        self.assertEqual(result["execution_status"], "error")

    def test_resumed_writer_keeps_exact_session(self):
        self.scenario["turns"].append({**self.scenario["turns"][0], "id": "T2"})
        self.freeze()
        self.finish(session="same")
        request = core.begin_turn(self.campaign, "run-0001")
        self.assertEqual(request["session_id"], "same")
        result = core.finish_turn(
            self.campaign,
            "run-0001",
            {
                "schema": 1,
                "execution_status": "completed",
                "session_id": "different",
                "response": "Done",
            },
        )
        self.assertEqual(result["execution_status"], "error")

    def test_between_turn_mutation_rejected(self):
        self.scenario["turns"].append({**self.scenario["turns"][0], "id": "T2"})
        self.freeze()
        self.finish()
        (self.campaign / "workspaces/run-0001/note.txt").write_text(
            "controller coaching"
        )
        with self.assertRaisesRegex(ValueError, "between recorded turns"):
            core.begin_turn(self.campaign, "run-0001")

    def test_new_campaign_required_and_source_policy_not_inherited(self):
        self.freeze()
        with self.assertRaisesRegex(ValueError, "existing run"):
            core.freeze_campaign(self.root / "spec.json", self.campaign)
        with self.assertRaisesRegex(ValueError, "ancestor policy"):
            core.freeze_campaign(
                self.root / "spec.json", core.ROOT / "evals/artifacts/unsafe"
            )

    def test_schema_rejects_scope_typos_and_oversized_schedule(self):
        self.scenario["turns"][0]["checks"][1]["evidence_scope"] = "saveed"
        with self.assertRaisesRegex(ValueError, "evidence_scope"):
            validate_scenario(self.scenario)
        self.scenario["turns"][0]["checks"][1]["evidence_scope"] = "saved"
        self.spec["limits"]["max_turns"] = 1
        self.spec["repetitions"] = 2
        core.dump(self.root / "scenario.json", self.scenario)
        core.dump(self.root / "spec.json", self.spec)
        with self.assertRaisesRegex(ValueError, "exceeding"):
            load_spec(self.root / "spec.json")

    def test_consumer_has_local_git_baseline_without_remote(self):
        self.freeze()
        request = core.begin_turn(self.campaign, "run-0001")
        workspace = request["workspace"]
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=workspace,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertEqual(len(head), 40)
        self.assertEqual(
            subprocess.run(
                ["git", "remote"],
                cwd=workspace,
                capture_output=True,
                text=True,
                check=True,
            ).stdout,
            "",
        )
        self.assertEqual(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=workspace,
                capture_output=True,
                text=True,
                check=True,
            ).stdout,
            "",
        )

    def test_public_command_output_is_retained_without_reasoning_events(self):
        self.scenario["turns"][0]["checks"] = [
            {
                "id": "inspection",
                "kind": "command_observed",
                "argv_contains": "inspect.py",
            }
        ]
        self.freeze()
        request = core.begin_turn(self.campaign, "run-0001")
        trace = Path(request["artifact_dir"]) / "codex.jsonl"
        events = [
            {"type": "thread.started", "thread_id": "subject-one"},
            {
                "type": "item.completed",
                "item": {
                    "id": "cmd1",
                    "type": "command_execution",
                    "command": "python inspect.py",
                    "exit_code": 0,
                    "status": "completed",
                    "aggregated_output": "Observed 94 cm",
                },
            },
            {
                "type": "item.completed",
                "item": {"type": "reasoning", "text": "not public command evidence"},
            },
        ]
        trace.write_text("\n".join(json.dumps(event) for event in events))
        core.finish_turn(
            self.campaign,
            "run-0001",
            {
                "schema": 1,
                "execution_status": "completed",
                "session_id": "subject-one",
                "response": "Inspected.",
                "traces": [str(trace)],
            },
        )
        packet = core.grading_packet(self.campaign)
        observations = packet["items"][0]["evidence"]["@observations"]
        self.assertIn("Observed 94 cm", observations)
        self.assertNotIn("not public command evidence", observations)
        self.assertEqual(core.report_campaign(self.campaign)["verdict"], "PASS")

    def test_report_outputs_are_distinct_and_preserve_existing_files(self):
        self.freeze()
        destination = self.root / "result.json"
        markdown = destination.with_suffix(".md")
        markdown.write_text("Existing user document\n")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(
                main(["report", str(self.campaign), "--out", str(destination)]), 2
            )
            self.assertEqual(
                main(
                    ["report", str(self.campaign), "--out", str(self.root / "wrong.md")]
                ),
                2,
            )
        self.assertFalse(destination.exists())
        self.assertFalse((self.root / "wrong.md").exists())
        self.assertEqual(markdown.read_text(), "Existing user document\n")
        fresh = self.root / "fresh.json"
        self.assertEqual(main(["report", str(self.campaign), "--out", str(fresh)]), 2)
        self.assertEqual(json.loads(fresh.read_text())["verdict"], "INCONCLUSIVE")
        self.assertTrue(fresh.with_suffix(".md").read_text().startswith("# controls"))

    def test_report_exit_codes_and_applicability(self):
        self.scenario["applicability"] = "current-contract"
        self.scenario["turns"][0]["checks"] = self.scenario["turns"][0]["checks"][:1]
        self.freeze()
        self.finish()
        report = core.report_campaign(self.campaign)
        self.assertEqual(
            report["by_applicability"]["current-contract"]["candidate"]["PASS"], 1
        )
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["report", str(self.campaign)]), 0)

    def test_atomic_output_preserves_existing_temporary_sibling(self):
        destination = self.root / "report.json"
        sibling = self.root / "report.json.tmp"
        sibling.write_text("unrelated user data")
        core.dump(destination, {"done": True})
        self.assertEqual(sibling.read_text(), "unrelated user data")
        target = self.root / "valuable.txt"
        target.write_text("preserve me")
        sibling.unlink()
        sibling.symlink_to(target)
        core.dump(destination, {"done": False})
        self.assertEqual(target.read_text(), "preserve me")

    def test_recovery_preserves_actual_response_saved_before_checkpoint(self):
        self.freeze()
        request = core.begin_turn(self.campaign, "run-0001")
        (Path(request["workspace"]) / "note.txt").write_text("after\n")
        response = {
            "schema": 1,
            "execution_status": "completed",
            "session_id": "actual-session",
            "response": "Actual retained answer",
            "traces": [],
        }
        original_dump = core.dump

        def interrupt_checkpoint(path, value):
            if path.name == "checkpoint.json":
                raise OSError("Simulated interruption after response save")
            original_dump(path, value)

        with patch.object(core, "dump", side_effect=interrupt_checkpoint):
            with self.assertRaises(OSError):
                core.finish_turn(self.campaign, "run-0001", response)
        recovered = core.recover_turn(
            self.campaign, "run-0001", "Coordinator interrupted"
        )
        self.assertEqual(recovered["execution_status"], "completed")
        self.assertEqual(
            json.loads((self.campaign / "runs/run-0001/001/response.json").read_text()),
            response,
        )
        self.assertEqual(
            json.loads((self.campaign / "state.json").read_text())["launched_turns"], 1
        )


if __name__ == "__main__":
    unittest.main()
