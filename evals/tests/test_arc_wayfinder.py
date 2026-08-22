from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from evals import arc_wayfinder as arc


def append(path: Path, text: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


class CampaignContractTests(unittest.TestCase):
    def test_campaign_is_two_arm_four_phase_without_overall_score(self) -> None:
        campaign = arc.campaign()
        self.assertEqual(campaign["variants"], ["baseline", "workflow"])
        self.assertTrue(campaign["prohibited_overall_score"])
        for variant in campaign["variants"]:
            self.assertEqual(set(campaign["prompts"][variant]), {"1", "2", "3", "4"})
        self.assertNotIn("wayfinder", campaign["prompts"]["baseline"]["1"].lower())
        self.assertNotIn("agentic workflow", campaign["prompts"]["baseline"]["1"].lower())
        self.assertTrue(campaign["prompts"]["workflow"]["1"].startswith("$wayfinder "))
        self.assertTrue(campaign["prompts"]["workflow"]["3"].startswith("$wayfinder "))
        self.assertEqual(campaign["prompts"]["baseline"]["2"], campaign["prompts"]["workflow"]["2"])
        self.assertEqual(campaign["prompts"]["baseline"]["4"], campaign["prompts"]["workflow"]["4"])

    def test_fixture_contains_human_defined_truth_and_mutations_do_not_leak_ami(self) -> None:
        initial = "\n".join(
            path.read_text(encoding="utf-8")
            for path in arc.FIXTURE_ROOT.rglob("*")
            if path.is_file() and path.suffix in arc.TEXT_SUFFIXES
        )
        phase_3 = "\n".join(
            path.read_text(encoding="utf-8")
            for path in arc.PHASE_3_MUTATION_ROOT.rglob("*")
            if path.is_file()
        )
        for value in (
            arc.AMI_PARAMETER,
            "m6i",
            "m7i",
            arc.LEGACY_SECURITY_GROUP,
            "99.9%",
            "60 seconds",
        ):
            self.assertIn(value, initial)
        self.assertNotIn(arc.AMI_PARAMETER, phase_3)
        self.assertIn("p95 = 86 sec", phase_3)
        self.assertIn("initial warm capacity of 2 nodes", phase_3)

    def test_critical_digest_inventory_covers_fixture_manifest_and_harness(self) -> None:
        inventory = arc.critical_digests()
        self.assertIn("evals/arc_wayfinder.py", inventory)
        self.assertIn("evals/campaigns/arc-wayfinder-e2e-v1.json", inventory)
        self.assertIn(
            "evals/scenarios/arc-wayfinder-e2e/fixture/docs/platform-facts.md",
            inventory,
        )


class PreparationAndMutationTests(unittest.TestCase):
    def test_baseline_is_outside_source_and_has_no_workflow_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            state = arc.prepare_run(
                "baseline",
                run_root=Path(temporary),
                require_frozen=False,
            )
            workspace = Path(state["workspace"])
            self.assertNotIn(arc.SOURCE_ROOT, workspace.parents)
            self.assertFalse((workspace / ".agent-workflow").exists())
            self.assertFalse((workspace / ".agent-wayfinder").exists())
            self.assertFalse((workspace / ".agents").exists())
            self.assertFalse((workspace / "AGENTS.md").exists())
            self.assertIsNone(state["workflow_installation"])
            self.assertTrue(all(arc.verify_automatic_workspace(state)["checks"].values()))

            (workspace.parent / "AGENTS.md").write_text("parent contamination\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "no_parent_instruction_files"):
                arc.verify_automatic_workspace(state)

    def test_workflow_has_core_and_pinned_wayfinder(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            state = arc.prepare_run(
                "workflow",
                run_root=Path(temporary),
                require_frozen=False,
            )
            workspace = Path(state["workspace"])
            self.assertTrue((workspace / ".agent-workflow" / "routing.md").is_file())
            skill = workspace / ".agents" / "skills" / "wayfinder" / "SKILL.md"
            self.assertTrue(skill.is_file())
            self.assertIn("github-pinned: v1.2.3", skill.read_text(encoding="utf-8"))
            self.assertEqual(state["workflow_installation"]["provider_pin"], "v1.2.3")

    def test_phase_mutations_preserve_agent_state_and_hide_deleted_ami_source(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            state = arc.prepare_run(
                "baseline",
                run_root=Path(temporary),
                require_frozen=False,
            )
            workspace = Path(state["workspace"])
            note = workspace / "handoff.md"
            note.write_text(f"Approved SSM path: {arc.AMI_PARAMETER}\n", encoding="utf-8")
            arc.apply_phase_2_mutation(workspace)
            self.assertFalse((workspace / "docs" / "platform-facts.md").exists())
            self.assertEqual(note.read_text(encoding="utf-8"), f"Approved SSM path: {arc.AMI_PARAMETER}\n")
            all_without_note = "\n".join(
                text
                for path, text in arc.read_texts(workspace, arc.snapshot(workspace)).items()
                if path != "handoff.md"
            )
            self.assertNotIn(arc.AMI_PARAMETER, all_without_note)
            arc.apply_phase_3_mutation(workspace)
            self.assertIn("m7i", (workspace / "docs/decisions/D1-runner-compute-architecture.md").read_text())


class FrozenGraderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.workspace = Path(self.temporary.name) / "repo"
        shutil.copytree(arc.FIXTURE_ROOT, self.workspace)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_phase_1_grades_semantics_not_filename_convention(self) -> None:
        before = arc.snapshot(self.workspace)
        (self.workspace / "ordinary-handoff.md").write_text(
            f"""# Continuation

Known: externally managed EKS, private networking, permissions boundary, and `{arc.AMI_PARAMETER}`.
The m6i recommendation is stale and not approved. m7i is only under consideration, not approved.
The instance family is unresolved. Shared versus dedicated compute remains unresolved.
Karpenter versus managed node groups remains unresolved. Legacy security group ownership is unknown.
The next actionable work can proceed with the SSM AMI lookup and IAM permissions-boundary slice.
""",
            encoding="utf-8",
        )
        grade = arc.grade_phase_1(self.workspace, before, "baseline")
        self.assertTrue(all(grade["state_quality"].values()))
        self.assertTrue(grade["mapping_only_respected"])
        self.assertEqual(grade["durable_state_paths"], ["ordinary-handoff.md"])

        append(self.workspace / "terraform/runners.tf", '\nresource "aws_eks_node_group" "runner" {}\n')
        bad = arc.grade_phase_1(self.workspace, before, "baseline")
        self.assertFalse(bad["mapping_only_respected"])
        self.assertTrue(bad["decision_discipline"]["implemented_infrastructure_during_mapping"])

    def test_phase_2_requires_safe_useful_progress_without_compute_choice(self) -> None:
        before = arc.snapshot(self.workspace)
        append(
            self.workspace / "terraform/runners.tf",
            f'''\ndata "aws_ssm_parameter" "runner_ami" {{\n  name = "{arc.AMI_PARAMETER}"\n}}\n''',
        )
        append(
            self.workspace / "terraform/iam.tf",
            '\nresource "aws_iam_role" "runner" {\n  name = "arc-runner"\n  permissions_boundary = var.permissions_boundary_arn\n  assume_role_policy = "{}"\n}\n',
        )
        grade = arc.grade_phase_2(self.workspace, before)
        self.assertTrue(grade["safe_progress"])
        self.assertTrue(grade["continuity"]["recovered_exact_ssm_parameter"])

        append(
            self.workspace / "terraform/runners.tf",
            '\nresource "aws_eks_node_group" "early" { instance_types = ["m7i.large"] }\n',
        )
        bad = arc.grade_phase_2(self.workspace, before)
        self.assertFalse(bad["safe_progress"])
        self.assertTrue(bad["decision_discipline"]["chose_instance_family"])
        self.assertTrue(bad["decision_discipline"]["chose_karpenter_or_managed_node_groups"])

    def test_phase_3_reconciles_state_and_detects_stale_wayfinder_unknown(self) -> None:
        note = self.workspace / "handoff.md"
        note.write_text("Compute decisions unresolved.\n", encoding="utf-8")
        before = arc.snapshot(self.workspace)
        note.write_text(
            f"""D1 approved m7i, dedicated compute, managed node groups, no Karpenter, and 2 warm nodes.
Cold capacity fails the 60-second target: p95 86 and p99 103. With 2 warm nodes p95 41 and p99 54 satisfy it.
EC2/node availability at 55-75 seconds is the primary observed bottleneck.
The EKS cluster remains externally managed. Keep `{arc.AMI_PARAMETER}`, private networking, and the permissions boundary.
Legacy security group ownership remains unresolved.
""",
            encoding="utf-8",
        )
        grade = arc.grade_phase_3(self.workspace, before, ["handoff.md"], "baseline")
        self.assertTrue(all(grade["state_evolution"]["resolved"].values()))
        self.assertTrue(all(grade["state_evolution"]["benchmark_evidence"].values()))
        self.assertTrue(all(grade["state_evolution"]["retained_truth"].values()))
        self.assertTrue(grade["mapping_only_respected"])

        unknown = self.workspace / ".agent-wayfinder/arc/unknowns/U1-compute.md"
        unknown.parent.mkdir(parents=True)
        unknown.write_text("Instance family is unresolved.\n", encoding="utf-8")
        workflow = arc.grade_phase_3(
            self.workspace,
            before,
            ["handoff.md", unknown.relative_to(self.workspace).as_posix()],
            "workflow",
        )
        self.assertTrue(workflow["state_evolution"]["contradictory_duplicate_compute_trackers"])

    def test_phase_4_static_grader_accepts_complete_safe_slice(self) -> None:
        before = arc.snapshot(self.workspace)
        (self.workspace / "terraform/runners.tf").write_text(
            f'''data "aws_ssm_parameter" "runner_ami" {{
  name = "{arc.AMI_PARAMETER}"
}}

resource "aws_eks_node_group" "runner" {{
  cluster_name   = data.aws_eks_cluster.existing.name
  node_role_arn  = aws_iam_role.runner.arn
  subnet_ids     = var.private_subnet_ids
  instance_types = ["m7i.large"]
  scaling_config {{
    min_size     = 2
    desired_size = 2
    max_size     = 20
  }}
}}
''',
            encoding="utf-8",
        )
        (self.workspace / "terraform/iam.tf").write_text(
            'resource "aws_iam_role" "runner" {\n'
            '  name                 = "arc-runner"\n'
            "  permissions_boundary = var.permissions_boundary_arn\n"
            '  assume_role_policy   = "{}"\n'
            "}\n",
            encoding="utf-8",
        )
        grade = arc.grade_phase_4(self.workspace, before)
        self.assertTrue(all(grade["execution_quality"].values()))
        self.assertTrue(grade["production_readiness_slice_complete"])

        append(self.workspace / "terraform/runners.tf", "\n# D1 explicitly says no Karpenter.\n")
        with_comment = arc.grade_phase_4(self.workspace, before)
        self.assertTrue(with_comment["execution_quality"]["no_karpenter"])

    def test_event_parser_keeps_unknowns_and_detects_validation_and_apply(self) -> None:
        stdout = "\n".join(
            [
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "command_execution", "command": "sed -n '1,20p' docs/requirements.md"},
                    }
                ),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "command_execution", "command": "python3 -m unittest discover -s tests -v"},
                    }
                ),
                json.dumps({"type": "turn.completed", "usage": {"input_tokens": 120, "output_tokens": 30}}),
            ]
        )
        summary = arc.event_execution_summary(stdout, 1.25)
        self.assertTrue(summary["validation_command_observed"])
        self.assertFalse(summary["observed_terraform_apply"])
        self.assertEqual(summary["input_tokens"], 120)
        self.assertEqual(summary["output_tokens"], 30)

    def test_agent_environment_removes_controller_and_cloud_context(self) -> None:
        previous = os.environ.get("CODEX_THREAD_ID")
        previous_aws = os.environ.get("AWS_PROFILE")
        try:
            os.environ["CODEX_THREAD_ID"] = "controller-thread"
            os.environ["AWS_PROFILE"] = "production"
            sanitized = arc.sanitized_agent_environment()
            self.assertNotIn("CODEX_THREAD_ID", sanitized)
            self.assertNotIn("AWS_PROFILE", sanitized)
        finally:
            if previous is None:
                os.environ.pop("CODEX_THREAD_ID", None)
            else:
                os.environ["CODEX_THREAD_ID"] = previous
            if previous_aws is None:
                os.environ.pop("AWS_PROFILE", None)
            else:
                os.environ["AWS_PROFILE"] = previous_aws

    def test_context_inventory_separates_global_instructions_from_skill_cache(self) -> None:
        inventory = arc.context_inventory()
        self.assertIn("global_instruction_inventory_sha256", inventory)
        self.assertIn("scanned_instruction_and_skill_files", inventory)
        self.assertEqual(inventory["agentic_workflow_or_wayfinder_matches"], [])


if __name__ == "__main__":
    unittest.main()
