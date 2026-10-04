"""Deterministic controls for frozen ARC transitions and neutral inputs."""

import copy
import hashlib
import sys
import subprocess
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from evals.campaign import core, codex, arc_launch
from evals.campaign.schema import load_spec, validate_scenario

ROOT = Path(__file__).resolve().parents[2]
ARC = ROOT / "evals/arc-state-complexity-v2"


class ArcControls(unittest.TestCase):
    def test_recovered_six_fresh_phases_and_complete_alarm_contract(self):
        spec, scenarios = load_spec(ARC / "campaign.json")
        turns = scenarios[0][0]["turns"]
        self.assertEqual(len(turns), 6)
        self.assertEqual(len({t["session"] for t in turns}), 6)
        self.assertEqual(spec["limits"]["max_turns"], 12)
        self.assertEqual(turns[1]["before_turn"]["delete"], ["docs/platform-facts.md"])
        self.assertIn(
            "docs/decisions/D1-runner-compute-architecture.md",
            turns[2]["before_turn"]["create"],
        )
        self.assertIn(
            "docs/decisions/D2-runner-instance-size.md",
            turns[4]["before_turn"]["create"],
        )
        contract = (ARC / "fixture/docs/observability-requirements.md").read_text()
        for field in (
            "FailedRunnerJobs",
            "ARC/Runner",
            "ClusterName",
            "Sum",
            "60",
            "GreaterThanOrEqualToThreshold",
            "Count",
            "notBreaching",
            "datapoints",
            "OK",
            "insufficient-data",
        ):
            self.assertIn(field, contract)
        self.assertNotIn("$wayfinder", json.dumps(turns))
        self.assertEqual(scenarios[0][0]["applicability"], "common-outcome")

    def test_transition_deletes_exact_source_and_keeps_subject_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "consumer"
            workspace.mkdir()
            (workspace / "docs").mkdir()
            (workspace / "docs/fact.md").write_text("source")
            (workspace / "HANDOFF.md").write_text("durable exact fact")
            raw = root / "evidence"
            raw.mkdir()
            result = core.apply_transition(
                workspace,
                raw,
                {"delete": ["docs/fact.md"], "create": {"docs/D1.md": "approved"}},
            )
            self.assertNotIn("docs/fact.md", result["files"])
            self.assertEqual(result["files"]["HANDOFF.md"], "durable exact fact")
            self.assertEqual(
                json.loads((raw / "before-transition.json").read_text())["files"][
                    "docs/fact.md"
                ],
                "source",
            )
            self.assertEqual(result["files"]["docs/D1.md"], "approved")

    def test_collision_is_rejected_before_any_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/fact.md").write_text("fact")
            (root / "docs/D1.md").write_text("subject")
            with self.assertRaisesRegex(ValueError, "overwrite"):
                core.apply_transition(
                    root,
                    root,
                    {
                        "delete": ["docs/fact.md"],
                        "create": {"docs/D1.md": "replacement"},
                    },
                )
            self.assertEqual((root / "docs/fact.md").read_text(), "fact")
            self.assertEqual((root / "docs/D1.md").read_text(), "subject")

    def test_transition_rejects_escape_and_framework_paths(self):
        scenario = json.loads((ARC / "scenario.json").read_text())
        for path in ("../outside", "docs/../../outside", ".agents/skills/rubric.md"):
            candidate = copy.deepcopy(scenario)
            candidate["turns"][0]["before_turn"] = {"create": {path: "x"}}
            with self.assertRaises(ValueError):
                validate_scenario(candidate)

    def test_six_phase_lifecycle_preserves_controller_evidence_and_freshness(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = Path(tmp)
            spec = json.loads((ARC / "campaign.json").read_text())
            spec["conditions"] = [{"id": "vanilla", "ref": "vanilla", "overlays": []}]
            spec["host"] = {
                "kind": "manual",
                "model": "unavailable",
                "reasoning_effort": "unavailable",
            }
            spec["scenarios"] = [str(ARC / "scenario.json")]
            core.dump(root / "spec.json", spec)
            campaign = root / "campaign"
            core.freeze_campaign(root / "spec.json", campaign)
            for index in range(1, 7):
                request = core.begin_turn(campaign, "run-0001")
                self.assertIsNone(request["session_id"])
                workspace = Path(request["workspace"])
                if index == 1:
                    baseline = subprocess.check_output(
                        ["git", "log", "-1", "--format=%an %ae %s"],
                        cwd=workspace,
                        text=True,
                    )
                    self.assertNotIn("Campaign", baseline)
                    self.assertNotIn("evaluation", baseline)
                    self.assertIn("Initial project state", baseline)
                if index >= 2:
                    self.assertFalse((workspace / "docs/platform-facts.md").exists())
                if index >= 3:
                    self.assertTrue(
                        (
                            workspace
                            / "docs/decisions/D1-runner-compute-architecture.md"
                        ).exists()
                    )
                if index >= 5:
                    self.assertTrue(
                        (
                            workspace / "docs/decisions/D2-runner-instance-size.md"
                        ).exists()
                    )
                core.finish_turn(
                    campaign,
                    "run-0001",
                    {
                        "schema": 1,
                        "execution_status": "completed",
                        "session_id": f"fake-phase-{index}",
                        "response": "Synthetic transport test; no subject implementation or model run.",
                    },
                )
            report = core.report_campaign(campaign)
            self.assertEqual(report["expected_turns"], 6)
            self.assertIn("none", core.render_report(report))
            packet = core.grading_packet(campaign)
            self.assertEqual(len(packet["items"]), 6)
            evidence = campaign / "runs/run-0001/002/transition.json"
            evidence.write_text("{}")
            with self.assertRaisesRegex(ValueError, "transition"):
                core.grading_packet(campaign)

    def test_unittest_module_observation_does_not_reward_echo(self):
        self.assertTrue(
            core._command_executes(
                "python3 -m unittest discover -s tests -v", "unittest"
            )
        )
        self.assertFalse(core._command_executes("echo python3 -m unittest", "unittest"))
        self.assertFalse(core._command_executes("python3 -c 'print(42)'", "unittest"))

    def test_alarm_calibration_requires_real_implementation_in_both_note_layouts(self):
        corpus = json.loads((ARC / "calibration.json").read_text())
        cases = {case["id"]: case for case in corpus["cases"]}
        self.assertIn("notes/state.json", cases["control-1"]["evidence"]["files"])
        self.assertIn("HANDOFF.md", cases["control-2"]["evidence"]["files"])
        for case in cases.values():
            hcl = case["evidence"]["files"]["terraform/observability.tf"]
            self.assertIn('resource "aws_cloudwatch_metric_alarm"', hcl)
            self.assertIn("ClusterName = var.cluster_name", hcl)
            self.assertIn("insufficient_data_actions = []", hcl)
            self.assertIn("arn:aws:sns:us-east-1:123456789012:arc-runner-alerts", hcl)
            request = case["evidence"]["request"]
            self.assertNotIn("The destination ARN has not arrived", request)
            self.assertIn(
                "approval at the start of this request satisfies that condition",
                request,
            )
        good = cases["control-1"]["evidence"]["files"]["terraform/observability.tf"]
        self.assertEqual(
            good, cases["control-2"]["evidence"]["files"]["terraform/observability.tf"]
        )
        wrong = cases["control-3"]["evidence"]["files"]["terraform/observability.tf"]
        self.assertEqual(
            wrong,
            good.replace(
                'metric_name         = "FailedRunnerJobs"',
                'metric_name         = "RunnerErrors"',
            ),
        )
        expected = {
            check["id"]: check["verdict"] for check in cases["control-3"]["expected"]
        }
        self.assertEqual(expected["alarm-contract"], "FAIL")
        criterion = next(c for c in corpus["rubric"] if c["id"] == "alarm-contract")
        self.assertIn("state note declaring implementation", criterion["requirement"])

    def test_phase_two_format_obligation_is_supplied_in_initial_fixture(self):
        readme = (ARC / "fixture/README.md").read_text()
        self.assertIn(
            "After implementation changes, run `terraform fmt -check terraform`", readme
        )
        self.assertIn("If Terraform is unavailable, disclose that limitation", readme)
        scenario = json.loads((ARC / "scenario.json").read_text())
        self.assertEqual(scenario["fixture"], "fixture")
        self.assertTrue(
            any(
                "terraform fmt -check" in c.get("requirement", "")
                for c in scenario["turns"][1]["checks"]
            )
        )

    def test_full_budget_preparation_has_no_stale_wallclock_cutoff(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = Path(tmp)
            binary = root / "synthetic-binary"
            binary.write_bytes(b"synthetic native identity; never executed")
            campaign = root / "project"
            manifest = arc_launch.prepare(campaign, binary)
            self.assertNotIn("launch_before_utc", manifest["spec"]["limits"])
            self.assertEqual(
                manifest["spec"]["limits"],
                {"max_turns": 12, "turn_seconds": 300, "campaign_seconds": 3900},
            )
            self.assertTrue(manifest["spec"]["host"]["settings"]["fast_mode"])
            core.dump(
                campaign / "native-preflight-result.json",
                {"passed": True, "manifest_sha256": core.fingerprint(manifest)},
            )
            with patch.object(
                arc_launch, "run_supervised", return_value={"verdict": "INCONCLUSIVE"}
            ) as runner:
                arc_launch.run_once(campaign)
                runner.assert_called_once_with(campaign, manifest)
                with self.assertRaises(FileExistsError):
                    arc_launch.run_once(campaign)
                self.assertEqual(runner.call_count, 1)

    def test_outer_timeout_is_bounded_keyless_and_cleans_owned_copies(self):
        from unittest.mock import Mock

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "spec": {"limits": {"campaign_seconds": 3900}},
                "schedule": [],
                "scenarios": {},
            }
            process = Mock(returncode=-9)
            process.poll.return_value = None
            process.wait.side_effect = [
                subprocess.TimeoutExpired("synthetic controller", 3900),
                -9,
            ]
            with (
                patch.object(
                    arc_launch.subprocess, "Popen", return_value=process
                ) as popen,
                patch.object(arc_launch, "stop_owned_processes") as stop,
                patch.object(
                    arc_launch, "cleanup_owned_credentials", return_value=[]
                ) as cleanup,
                patch.dict("os.environ", {"OPENAI_API_KEY": "synthetic canary"}),
            ):
                result = arc_launch.run_supervised(root, manifest)
            self.assertEqual(result["execution_status"], "timeout")
            self.assertNotIn("OPENAI_API_KEY", popen.call_args.kwargs["env"])
            self.assertEqual(process.wait.call_args_list[0].kwargs["timeout"], 3900)
            stop.assert_called_once_with(process)
            cleanup.assert_called_once_with(root, manifest)
            self.assertTrue((root / "controller-run/launch-result.json").exists())

    def test_supervisor_stops_only_owned_descendant_groups(self):
        from unittest.mock import Mock

        with (
            patch.object(
                arc_launch.subprocess,
                "check_output",
                return_value=b"100 1\n200 100\n300 200\n999 1\n",
            ),
            patch.object(arc_launch.os, "kill") as kill,
            patch.object(arc_launch.os, "killpg") as killpg,
        ):
            arc_launch.stop_owned_processes(Mock(pid=100))
            self.assertEqual(
                {call.args[0] for call in killpg.call_args_list}, {100, 200, 300}
            )
            self.assertNotIn(999, {call.args[0] for call in kill.call_args_list})

    def test_cleanup_removes_only_owned_synthetic_credential_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "schedule": [{"id": "run-0001", "scenario": "arc"}],
                "scenarios": {
                    "arc": {"turns": [{"session": "owned"}, {"session": "unowned"}]}
                },
            }
            for session in ("owned", "unowned"):
                home = root / "sessions/run-0001" / session
                (home / "codex-home").mkdir(parents=True)
                (home / "codex-home/auth.json").write_text("synthetic test canary")
            core.dump(
                root / "sessions/run-0001/owned/.campaign-owned.json",
                {"schema": 1, "workspace": str(root / "workspaces/run-0001")},
            )
            cleaned = arc_launch.cleanup_owned_credentials(root, manifest)
            self.assertEqual(cleaned, ["sessions/run-0001/owned/codex-home/auth.json"])
            self.assertTrue(
                (root / "sessions/run-0001/unowned/codex-home/auth.json").exists()
            )

    def test_launch_rejects_native_binary_drift_before_authentication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binary = root / "synthetic-binary"
            binary.write_bytes(b"original")
            core.dump(
                root / "preparation.json",
                {
                    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                    "python": str(Path(sys.executable).resolve(strict=True)),
                },
            )
            manifest = {"spec": {"host": {"settings": {"binary": str(binary)}}}}
            arc_launch.verify_launch_identity(root, manifest)
            binary.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "binary changed"):
                arc_launch.verify_launch_identity(root, manifest)

    def test_cutoff_blocks_new_attempt_without_consuming_budget(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as tmp:
            root = Path(tmp)
            spec = json.loads((ARC / "campaign.json").read_text())
            spec["conditions"] = [{"id": "vanilla", "ref": "vanilla"}]
            spec["scenarios"] = [str(ARC / "scenario.json")]
            spec["limits"]["launch_before_utc"] = "2000-01-01T00:00:00+00:00"
            core.dump(root / "spec.json", spec)
            campaign = root / "campaign"
            core.freeze_campaign(root / "spec.json", campaign)
            with self.assertRaisesRegex(ValueError, "window ended"):
                core.begin_turn(campaign, "run-0001")
            self.assertEqual(
                core.read_json(campaign / "state.json")["launched_turns"], 0
            )

    def test_native_subscription_fast_overrides_and_keyless_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "consumer"
            home = root / "session"
            artifact = root / "raw"
            for p in (workspace, home, artifact):
                p.mkdir()
            with patch.dict("os.environ", {"OPENAI_API_KEY": "synthetic-canary"}):
                config, env = codex._settings(
                    {
                        "model": "gpt-6.1-sol",
                        "reasoning_effort": "medium",
                        "settings": {
                            "subscription_only": True,
                            "fast_mode": True,
                            "allow_subagents": False,
                        },
                    },
                    workspace,
                    home,
                    artifact,
                    Path("/usr/bin/true"),
                )
            self.assertIn('forced_login_method="chatgpt"', config)
            self.assertIn('cli_auth_credentials_store="file"', config)
            self.assertIn('service_tier="fast"', config)
            self.assertIn("features.fast_mode=true", config)
            self.assertNotIn("OPENAI_API_KEY", env)
            self.assertIn("agents.enabled=false", config)


if __name__ == "__main__":
    unittest.main()
