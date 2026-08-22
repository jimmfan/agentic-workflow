from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from evals import wayfinder_fresh_agent_continuation_v2 as fresh_v2


class CampaignContractTests(unittest.TestCase):
    def test_campaign_is_matched_four_repetition_bc_replication(self) -> None:
        campaign = fresh_v2.campaign()

        self.assertEqual(tuple(campaign["conditions"]), fresh_v2.CONDITIONS)
        self.assertEqual(campaign["candidate_git_sha"], fresh_v2.CANDIDATE_SHA)
        self.assertEqual(campaign["repetitions"], 4)
        self.assertEqual(campaign["prompts"]["B"], campaign["prompts"]["C"])
        self.assertTrue(campaign["prompts"]["B"]["1"].startswith("$wayfinder "))
        self.assertTrue(campaign["prompts"]["B"]["2"].startswith("$wayfinder "))
        self.assertEqual(len(campaign["execution_order"]), 16)
        self.assertEqual(
            [item[0] for item in campaign["execution_order"] if item.endswith(":1")],
            ["B", "C", "C", "B", "C", "B", "B", "C"],
        )

    def test_prepared_pair_comes_from_frozen_candidate_and_only_treatment_differs(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            states = fresh_v2.prepare_pair(Path(temporary), repetition=1)

            self.assertNotEqual(states["B"]["workspace"], states["C"]["workspace"])
            self.assertEqual(
                states["B"]["workflow_installation"]["candidate_git_sha"],
                fresh_v2.CANDIDATE_SHA,
            )
            self.assertEqual(
                states["C"]["workflow_installation"]["candidate_git_sha"],
                fresh_v2.CANDIDATE_SHA,
            )
            self.assertEqual(
                states["B"]["workflow_installation"]["files_changed_from_candidate"],
                sorted(fresh_v2.TREATMENT_PATHS),
            )
            self.assertEqual(
                states["B"]["workflow_installation"]["bc_differences"],
                sorted(fresh_v2.TREATMENT_PATHS),
            )

    def test_freeze_inventory_covers_runner_treatment_fixture_and_rubric(self) -> None:
        inventory = fresh_v2.critical_digests()
        for path in (
            "evals/wayfinder_fresh_agent_continuation_v2.py",
            "evals/campaigns/wayfinder-fresh-agent-continuation-v2.json",
            "evals/scenarios/wayfinder-fresh-agent-continuation-v1/matched-old-wayfinder.patch",
            "evals/scenarios/wayfinder-fresh-agent-continuation-v2/semantic-review-rubric.json",
            "evals/scenarios/resume/fixture/inputs/transient-platform-facts.md",
            "evals/scenarios/resume/phase-2-mutation/docs/decisions/D1-runner-architecture.md",
            "evals/arc_wayfinder_v2.py",
            "evals/run.py",
        ):
            self.assertIn(path, inventory)

    def test_v1_artifacts_remain_unchanged(self) -> None:
        self.assertTrue(
            fresh_v2.paths_unchanged_since(
                fresh_v2.V1_BASE_SHA, fresh_v2.V1_IMMUTABLE_PATHS
            )
        )

    def test_candidate_cache_rejects_any_inventory_change(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            run_root = Path(temporary)
            candidate = fresh_v2.materialize_candidate_source(run_root)
            fingerprint = fresh_v2.candidate_tree_fingerprint(candidate)
            self.assertEqual(
                fresh_v2.verify_candidate_source(run_root, fingerprint), candidate
            )

            (candidate / "unexpected.txt").write_text("drift\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "inventory changed"):
                fresh_v2.verify_candidate_source(run_root, fingerprint)


class TraceParserTests(unittest.TestCase):
    def test_file_change_stops_prewrite_read_collection(self) -> None:
        events = [
            {"type": "thread.started", "thread_id": "thread-v2-parser"},
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "sed -n '1,80p' docs/before.md",
                    "aggregated_output": "before",
                    "exit_code": 0,
                },
            },
            {
                "type": "item.started",
                "item": {
                    "type": "file_change",
                    "changes": [{"path": "terraform/runners.tf", "kind": "update"}],
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "type": "file_change",
                    "changes": [{"path": "terraform/runners.tf", "kind": "update"}],
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "cat docs/after.md",
                    "aggregated_output": "after",
                    "exit_code": 0,
                },
            },
        ]
        stdout = "\n".join(json.dumps(event) for event in events)

        summary = fresh_v2.event_execution_summary(stdout, 1.25)

        self.assertTrue(summary["continuation_cost"]["file_change_event_observed"])
        self.assertEqual(
            summary["continuation_cost"]["files_read_before_first_observed_write"],
            ["docs/before.md"],
        )
        self.assertEqual(
            summary["continuation_cost"]["file_read_count_before_first_observed_write"],
            1,
        )


class ShellEnvironmentTests(unittest.TestCase):
    def test_shell_environment_is_explicit_functional_and_secret_free(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            agent_home = Path(temporary) / "agent-home"
            policy = fresh_v2.shell_environment_policy(agent_home)

        self.assertEqual(policy["inherit"], "none")
        self.assertEqual(
            set(policy["set"]),
            {
                "GIT_PAGER",
                "HOME",
                "LANG",
                "LC_ALL",
                "NO_COLOR",
                "PAGER",
                "PATH",
                "SHELL",
                "TERM",
                "TMPDIR",
            },
        )
        self.assertEqual(policy["set"]["PATH"], fresh_v2.MINIMAL_TOOL_PATH)
        self.assertNotIn("AWS_PROFILE", policy["set"])
        self.assertNotIn("CODEX_HOME", policy["set"])

    def test_process_environment_contains_only_runtime_essentials(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            codex_home = Path(temporary) / "codex-home"
            environment = fresh_v2.codex_process_environment(codex_home)

        self.assertEqual(
            set(environment),
            {"CODEX_HOME", "HOME", "LANG", "LC_ALL", "NO_COLOR", "PATH", "TERM", "TMPDIR"},
        )
        self.assertEqual(environment["CODEX_HOME"], str(codex_home))
        self.assertEqual(environment["HOME"], str(codex_home))
        self.assertEqual(environment["PATH"], fresh_v2.MINIMAL_TOOL_PATH)

    def test_codex_command_applies_frozen_runtime_and_explicit_shell_policy(self) -> None:
        command = fresh_v2.codex_phase_command(
            Path("/opt/codex"),
            Path("/private/tmp/workspace"),
            Path("/private/tmp/agent-home"),
        )
        joined = "\n".join(command)

        self.assertIn("gpt-5.6-terra", command)
        self.assertIn('model_reasoning_effort="medium"', command)
        self.assertIn('approval_policy="never"', command)
        self.assertIn('shell_environment_policy.inherit="none"', command)
        self.assertIn("shell_environment_policy.set=", joined)
        self.assertIn("allow_login_shell=false", command)
        self.assertIn("sandbox_workspace_write.network_access=false", command)
        self.assertNotIn("AWS_", joined)

    def test_direct_script_entrypoint_can_render_environment(self) -> None:
        result = subprocess.run(
            [sys.executable, str(Path(fresh_v2.__file__)), "--show-environment"],
            cwd=fresh_v2.SOURCE_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        rendered = json.loads(result.stdout)
        self.assertEqual(rendered, fresh_v2.normalized_environment_record())


class SemanticReviewTests(unittest.TestCase):
    def test_every_frozen_dimension_is_required_before_summary(self) -> None:
        result = {
            "run_id": "fresh-agent-v2-b-1-test",
            "condition": "B",
            "repetition": 1,
        }
        dimensions = {
            name: {
                "classification": "not_applicable",
                "evidence": [],
                "rationale": "No applicable evidence in this deterministic fixture.",
            }
            for name in fresh_v2.semantic_rubric()["dimensions"]
        }
        review = {
            "schema_version": 1,
            "campaign_id": fresh_v2.CAMPAIGN_ID,
            **result,
            "reviewed_at": "2026-08-22T00:00:00+00:00",
            "dimensions": dimensions,
        }
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            results_root = Path(temporary)
            path = results_root / "runs" / result["run_id"] / "semantic-review.json"
            fresh_v2.write_json(path, review)
            with mock.patch.object(fresh_v2, "RESULTS_ROOT", results_root):
                self.assertEqual(fresh_v2.semantic_review_for(result), review)
                del review["dimensions"][next(iter(dimensions))]
                fresh_v2.write_json(path, review)
                with self.assertRaisesRegex(RuntimeError, "dimension coverage mismatch"):
                    fresh_v2.semantic_review_for(result)


if __name__ == "__main__":
    unittest.main()
