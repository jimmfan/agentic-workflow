from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest

from evals import wayfinder_fresh_agent_continuation as fresh


class CampaignContractTests(unittest.TestCase):
    def test_campaign_is_frozen_three_condition_two_phase_smoke(self) -> None:
        campaign = fresh.campaign()
        self.assertEqual(tuple(campaign["conditions"]), fresh.CONDITIONS)
        self.assertEqual(campaign["repetitions"], 1)
        self.assertTrue(campaign["stop_after_smoke"])
        self.assertTrue(campaign["prohibited_overall_score"])
        self.assertEqual(len(campaign["execution_order"]), 6)
        self.assertEqual(campaign["prompts"]["B"], campaign["prompts"]["C"])
        self.assertTrue(campaign["prompts"]["B"]["1"].startswith("$wayfinder "))
        self.assertTrue(campaign["prompts"]["B"]["2"].startswith("$wayfinder "))
        self.assertNotIn("wayfinder", campaign["prompts"]["A"]["1"].lower())

    def test_freeze_inventory_covers_fixture_treatment_and_runner(self) -> None:
        inventory = fresh.critical_digests()
        for path in (
            "evals/wayfinder_fresh_agent_continuation.py",
            "evals/campaigns/wayfinder-fresh-agent-continuation-v1.json",
            "evals/scenarios/wayfinder-fresh-agent-continuation-v1/matched-old-wayfinder.patch",
            "evals/scenarios/resume/fixture/inputs/transient-platform-facts.md",
            "evals/scenarios/resume/phase-2-mutation/docs/decisions/D1-runner-architecture.md",
            "skills/agent-workflow/runtime-projections/wayfinder.md",
            "skills/agent-workflow/payload/agent-workflow/contracts/wayfinder-state.md",
        ):
            self.assertIn(path, inventory)


class PreparationAndGradingTests(unittest.TestCase):
    def test_control_and_candidate_differ_only_on_exact_treatment_surfaces(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            states = fresh.prepare_trio(Path(temporary))
            self.assertFalse((Path(states["A"]["workspace"]) / ".agent-workflow").exists())
            b = states["B"]["workflow_installation"]
            c = states["C"]["workflow_installation"]
            self.assertEqual(b["files_changed_from_candidate"], sorted(fresh.TREATMENT_PATHS))
            self.assertTrue(not any(b["treatment_markers_present"].values()))
            self.assertTrue(all(c["treatment_markers_present"].values()))
            differences = sorted(
                path
                for path in b["installed_file_sha256"].keys() | c["installed_file_sha256"].keys()
                if b["installed_file_sha256"].get(path) != c["installed_file_sha256"].get(path)
            )
            self.assertEqual(differences, sorted(fresh.TREATMENT_PATHS))

    def test_state_metrics_separates_current_facts_from_procedural_lines(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            workspace = Path(temporary)
            note = workspace / "HANDOFF.md"
            note.write_text(
                f"Approved parameter: `{fresh.resume.AMI_PARAMETER}`.\n"
                "I read the input, then I ran a check.\n",
                encoding="utf-8",
            )
            metrics = fresh.state_metrics(workspace, ["HANDOFF.md"])
            self.assertEqual(metrics["exact_fact_occurrences"], 1)
            self.assertEqual(metrics["procedural_history_line_count"], 1)

    def test_resume_mutation_removes_fact_source_but_keeps_durable_note(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            workspace = Path(temporary) / "repo"
            shutil.copytree(fresh.FIXTURE_ROOT, workspace)
            note = workspace / "HANDOFF.md"
            note.write_text(fresh.resume.AMI_PARAMETER + "\n", encoding="utf-8")
            fresh.infra.init_git_repository(workspace)
            fresh.resume.mutate_resume_phase_2(workspace)
            self.assertFalse((workspace / "inputs" / "transient-platform-facts.md").exists())
            self.assertIn(fresh.resume.AMI_PARAMETER, note.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
