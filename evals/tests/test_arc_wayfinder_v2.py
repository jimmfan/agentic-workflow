from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from evals import arc_wayfinder_v2 as arc


def append(path: Path, text: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


class CampaignContractTests(unittest.TestCase):
    def test_campaign_is_three_condition_four_phase_without_overall_score(self) -> None:
        campaign = arc.campaign()
        self.assertEqual(tuple(campaign["conditions"]), arc.CONDITIONS)
        self.assertTrue(campaign["prohibited_overall_score"])
        self.assertTrue(campaign["stop_after_smoke"])
        self.assertEqual(len(campaign["execution_order"]), 12)
        for condition in arc.CONDITIONS:
            self.assertEqual(set(campaign["prompts"][condition]), {"1", "2", "3", "4"})
        self.assertEqual(campaign["prompts"]["A"]["1"], campaign["prompts"]["B"]["1"])
        self.assertEqual(campaign["prompts"]["A"]["3"], campaign["prompts"]["B"]["3"])
        self.assertEqual(campaign["prompts"]["A"]["2"], campaign["prompts"]["B"]["2"])
        self.assertEqual(campaign["prompts"]["B"]["2"], campaign["prompts"]["C"]["2"])
        self.assertEqual(campaign["prompts"]["A"]["4"], campaign["prompts"]["C"]["4"])
        self.assertNotIn("wayfinder", campaign["prompts"]["B"]["1"].lower())
        self.assertTrue(campaign["prompts"]["C"]["1"].startswith("$wayfinder "))
        self.assertTrue(campaign["prompts"]["C"]["3"].startswith("$wayfinder "))

    def test_fixture_and_phase_3_make_bounded_slice_unambiguous(self) -> None:
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
        for value in (
            "m7i.large",
            "minimum size: 2",
            "desired size: 2",
            "maximum size: 6",
            "ec2.amazonaws.com",
            "AmazonEKSWorkerNodePolicy",
            "does **not** block this bounded slice",
            "Do not run `terraform init`",
        ):
            self.assertIn(value, phase_3)
        self.assertIn(arc.AMI_PARAMETER, phase_3)

    def test_critical_digest_inventory_is_v2_only(self) -> None:
        inventory = arc.critical_digests()
        self.assertIn("evals/arc_wayfinder_v2.py", inventory)
        self.assertIn("evals/campaigns/arc-wayfinder-e2e-v2.json", inventory)
        self.assertIn(
            "evals/scenarios/arc-wayfinder-e2e-v2/fixture/docs/platform-facts.md",
            inventory,
        )
        self.assertNotIn("evals/arc_wayfinder.py", inventory)


class PreparationAndMutationTests(unittest.TestCase):
    def test_A_is_vanilla_and_B_C_installations_are_identical(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            states = arc.prepare_trio(
                run_root=Path(temporary),
                require_frozen=False,
            )
            a_workspace = Path(states["A"]["workspace"])
            self.assertFalse((a_workspace / ".agent-workflow").exists())
            self.assertFalse((a_workspace / ".agents").exists())
            self.assertIsNone(states["A"]["workflow_installation"])
            for condition in ("B", "C"):
                workspace = Path(states[condition]["workspace"])
                self.assertTrue((workspace / ".agent-workflow" / "routing.md").is_file())
                self.assertTrue((workspace / ".agents" / "skills" / "wayfinder" / "SKILL.md").is_file())
                self.assertTrue(all(arc.verify_automatic_workspace(states[condition])["checks"].values()))
            self.assertEqual(
                states["B"]["workflow_installation"]["installed_artifact_sha256"],
                states["C"]["workflow_installation"]["installed_artifact_sha256"],
            )

    def test_phase_mutations_preserve_agent_state_and_delete_only_original_source(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            state = arc.prepare_run("A", run_root=Path(temporary), require_frozen=False)
            workspace = Path(state["workspace"])
            note = workspace / "handoff.md"
            note.write_text(f"Approved SSM path: {arc.AMI_PARAMETER}\n", encoding="utf-8")
            arc.apply_phase_2_mutation(workspace)
            self.assertFalse((workspace / "docs" / "platform-facts.md").exists())
            self.assertIn(arc.AMI_PARAMETER, note.read_text(encoding="utf-8"))
            arc.apply_phase_3_mutation(workspace)
            readiness = workspace / "docs" / "implementation-readiness.md"
            self.assertTrue(readiness.is_file())
            self.assertIn("does **not** block", readiness.read_text(encoding="utf-8"))


class CorrectedGraderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.workspace = Path(self.temporary.name) / "repo"
        shutil.copytree(arc.FIXTURE_ROOT, self.workspace)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_phase_1_preserves_ambiguous_semantics_instead_of_false_positive(self) -> None:
        before = arc.snapshot(self.workspace)
        note = self.workspace / "ordinary-handoff.md"
        note.write_text(
            f"""# Continuation

Known: externally managed EKS, private networking, permissions boundary, and `{arc.AMI_PARAMETER}`.
The m6i recommendation is stale and not approved. m7i is under consideration, not approved.
The exact instance family is unresolved.
Shared versus dedicated compute remains unresolved.
Karpenter versus managed node groups remains unresolved.
Legacy security group ownership is unknown; do not import, delete, modify, or assume it.
The next actionable work can proceed with the SSM AMI lookup and IAM permissions-boundary slice.
""",
            encoding="utf-8",
        )
        grade = arc.grade_phase_1(self.workspace, before, "A")
        self.assertTrue(grade["state_quality"]["exact_fact_preserved"])
        self.assertTrue(grade["mapping_only_respected"])
        semantic = grade["state_quality"]["semantic_observations"]
        self.assertEqual(semantic["m6i_stale"]["classification"], "explicit_affirmative")
        self.assertIn(semantic["instance_family"]["classification"], {"unresolved", "ambiguous"})
        self.assertEqual(semantic["karpenter_vs_managed"]["classification"], "unresolved")
        self.assertTrue(semantic["m6i_stale"]["evidence"])
        self.assertEqual(semantic["m6i_stale"]["evidence"][0]["path"], "ordinary-handoff.md")
        self.assertIsInstance(semantic["m6i_stale"]["evidence"][0]["line"], int)

    def test_phase_2_reports_ssm_and_iam_progress_independently(self) -> None:
        before = arc.snapshot(self.workspace)
        append(
            self.workspace / "terraform" / "runners.tf",
            f'''\ndata "aws_ssm_parameter" "runner_ami" {{\n  name = "{arc.AMI_PARAMETER}"\n}}\n''',
        )
        execution = {"observed_exact_fact_in_tool_output": True}
        grade = arc.grade_phase_2(self.workspace, before, execution)
        self.assertTrue(grade["safe_progress"]["ssm"])
        self.assertFalse(grade["safe_progress"]["iam_permissions_boundary"])
        self.assertTrue(grade["continuity"]["exact_fact_located_or_read"])
        self.assertTrue(grade["continuity"]["exact_fact_trusted_or_consumed"])

    def test_phase_3_records_exact_blocker_evidence_without_forcing_boolean(self) -> None:
        state = self.workspace / ".agent-workflow-state/wayfinder/arc/tickets/T1.md"
        state.parent.mkdir(parents=True)
        state.write_text(
            "# T1\n\n- Status: ready\n- Blocked by: none\n\nLegacy ownership remains unresolved and non-blocking.\n",
            encoding="utf-8",
        )
        evidence = arc.wayfinder_blocker_evidence(self.workspace)
        self.assertEqual(evidence["all_blocked_by_lines"][0]["path"], ".agent-workflow-state/wayfinder/arc/tickets/T1.md")
        self.assertTrue(evidence["legacy_explicitly_non_blocking"])
        self.assertTrue(evidence["manual_interpretation_required"])

    def test_phase_4_checks_every_required_component_independently(self) -> None:
        before = arc.snapshot(self.workspace)
        (self.workspace / "terraform" / "runners.tf").write_text(
            f'''data "aws_ssm_parameter" "runner_ami" {{
  name = "{arc.AMI_PARAMETER}"
}}

resource "aws_launch_template" "runner" {{
  image_id = data.aws_ssm_parameter.runner_ami.value
}}

resource "aws_eks_node_group" "runner" {{
  cluster_name   = data.aws_eks_cluster.existing.name
  node_role_arn  = aws_iam_role.runner.arn
  subnet_ids     = var.private_subnet_ids
  instance_types = ["m7i.large"]
  capacity_type  = "ON_DEMAND"
  launch_template {{
    id = aws_launch_template.runner.id
  }}
  scaling_config {{
    min_size     = 2
    desired_size = 2
    max_size     = 6
  }}
  labels = {{ workload = "arc-runner" }}
  taint {{
    key    = "dedicated"
    value  = "arc-runner"
    effect = "NO_SCHEDULE"
  }}
  depends_on = [aws_iam_role_policy_attachment.worker]
}}
''',
            encoding="utf-8",
        )
        (self.workspace / "terraform" / "iam.tf").write_text(
            '''resource "aws_iam_role" "runner" {
  permissions_boundary = var.permissions_boundary_arn
  assume_role_policy = jsonencode({ Statement = [{ Principal = { Service = "ec2.amazonaws.com" } }] })
}

resource "aws_iam_role_policy_attachment" "worker" {
  role       = aws_iam_role.runner.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}
resource "aws_iam_role_policy_attachment" "ecr" {
  role       = aws_iam_role.runner.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly"
}
resource "aws_iam_role_policy_attachment" "cni" {
  role       = aws_iam_role.runner.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}
''',
            encoding="utf-8",
        )
        terraform = shutil.which("terraform")
        if terraform:
            subprocess.run(
                [terraform, "fmt", "-recursive", "terraform"],
                cwd=self.workspace,
                check=True,
                capture_output=True,
                text=True,
            )
        grade = arc.grade_phase_4(self.workspace, before)
        self.assertTrue(all(grade["execution_quality"].values()))
        self.assertTrue(grade["production_readiness_slice_complete"])
        self.assertTrue(grade["continuity"]["exact_fact_correctly_implemented"])

    def test_event_parser_captures_usage_ids_validation_and_fact_reads(self) -> None:
        stdout = "\n".join(
            [
                json.dumps({"type": "thread.started", "thread_id": "fresh-123"}),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {
                            "type": "command_execution",
                            "command": "python3 -m unittest discover -s tests -v",
                            "aggregated_output": f"handoff says {arc.AMI_PARAMETER}",
                            "exit_code": 0,
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "turn.completed",
                        "usage": {
                            "input_tokens": 120,
                            "cached_input_tokens": 80,
                            "output_tokens": 30,
                            "reasoning_output_tokens": 12,
                        },
                    }
                ),
            ]
        )
        summary = arc.event_execution_summary(stdout, 1.25)
        self.assertEqual(summary["execution_id"], "fresh-123")
        self.assertEqual(summary["cached_input_tokens"], 80)
        self.assertEqual(summary["reasoning_tokens"], 12)
        self.assertTrue(summary["observed_exact_fact_in_tool_output"])
        self.assertEqual(summary["validation_events"][0]["exit_code"], 0)

    def test_treatment_crossover_is_primitive_and_condition_specific(self) -> None:
        state = self.workspace / ".agent-workflow-state/wayfinder/arc/map.md"
        state.parent.mkdir(parents=True)
        state.write_text("# ARC\n", encoding="utf-8")
        execution = {
            "phase": 1,
            "wayfinder_observation": {
                "explicit_invocation_observed": False,
                "wayfinder_skill_read": True,
                "wayfinder_state_read": True,
                "route_to_wayfinder_self_reported": False,
                "instrumentation_note": "test",
            },
        }
        result = arc.treatment_crossover(
            "B",
            self.workspace,
            [".agent-workflow-state/wayfinder/arc/map.md"],
            execution,
        )
        self.assertTrue(result["treatment_crossover_observed"])
        self.assertTrue(result["wayfinder_state_created_or_modified_this_phase"])

    def test_minimal_agent_environment_has_no_cloud_or_controller_variables(self) -> None:
        environment = arc.sanitized_agent_environment(Path("/private/tmp/isolated-codex-home"))
        self.assertEqual(environment["CODEX_HOME"], "/private/tmp/isolated-codex-home")
        self.assertNotIn("AWS_PROFILE", environment)
        self.assertNotIn("CODEX_THREAD_ID", environment)

    def test_controller_probe_requires_an_explicit_null_excerpt(self) -> None:
        self.assertTrue(
            arc.controller_conversation_not_reported(
                json.dumps({"controller_conversation_excerpt": None})
            )
        )
        self.assertFalse(
            arc.controller_conversation_not_reported(
                json.dumps({"controller_conversation_visible": True})
            )
        )
        self.assertFalse(
            arc.controller_conversation_not_reported(
                json.dumps({"controller_conversation_excerpt": "corrected ARC Wayfinder"})
            )
        )


if __name__ == "__main__":
    unittest.main()
