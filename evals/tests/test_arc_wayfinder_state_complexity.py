from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from evals import arc_wayfinder_state_complexity as arc


def write_complete_w1_w2(workspace: Path, instance_type: str = "m7i.large") -> None:
    (workspace / "terraform" / "iam.tf").write_text(
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
    (workspace / "terraform" / "runners.tf").write_text(
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
  instance_types = ["{instance_type}"]
  capacity_type  = "ON_DEMAND"
  launch_template {{ id = aws_launch_template.runner.id }}
  scaling_config {{
    min_size = 2
    desired_size = 2
    max_size = 6
  }}
  labels = {{ workload = "arc-runner" }}
  taint {{
    key = "dedicated"
    value = "arc-runner"
    effect = "NO_SCHEDULE"
  }}
  depends_on = [aws_iam_role_policy_attachment.worker, aws_iam_role_policy_attachment.ecr, aws_iam_role_policy_attachment.cni]
}}
''',
        encoding="utf-8",
    )


def format_terraform(workspace: Path) -> None:
    terraform = shutil.which("terraform")
    if terraform:
        subprocess.run(
            [terraform, "fmt", "-recursive", "terraform"],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
        )


class CampaignContractTests(unittest.TestCase):
    def test_campaign_is_two_condition_six_phase_smoke(self) -> None:
        campaign = arc.campaign()
        self.assertEqual(tuple(campaign["conditions"]), ("A", "B"))
        self.assertEqual(len(campaign["execution_order"]), 12)
        self.assertTrue(campaign["prohibited_overall_score"])
        self.assertTrue(campaign["stop_after_smoke"])
        for condition in arc.CONDITIONS:
            self.assertEqual(set(campaign["prompts"][condition]), {"1", "2", "3", "4", "5", "6"})
        for phase in (2, 4, 6):
            self.assertEqual(campaign["prompts"]["A"][str(phase)], campaign["prompts"]["B"][str(phase)])
        for phase in (1, 3, 5):
            self.assertTrue(campaign["prompts"]["B"][str(phase)].startswith("$wayfinder "))
            self.assertNotIn("wayfinder", campaign["prompts"]["A"][str(phase)].lower())

    def test_fixture_and_mutations_encode_branching_truth(self) -> None:
        initial_files = [path for path in arc.FIXTURE_ROOT.rglob("*") if path.is_file()]
        initial = "\n".join(path.read_text(encoding="utf-8") for path in initial_files)
        self.assertEqual(sum(arc.AMI_PARAMETER in path.read_text(encoding="utf-8") for path in initial_files), 1)
        for value in ("m6i", "m7i", arc.LEGACY_SECURITY_GROUP, "99.9%", "60 seconds", "observability"):
            self.assertIn(value, initial)
        phase_3 = "\n".join(path.read_text(encoding="utf-8") for path in arc.PHASE_3_MUTATION_ROOT.rglob("*") if path.is_file())
        for value in ("m7i.large", "minimum size: 2", "desired size: 2", "maximum size: 6", "does **not** block"):
            self.assertIn(value, phase_3)
        self.assertNotIn(arc.AMI_PARAMETER, phase_3)
        phase_5 = "\n".join(path.read_text(encoding="utf-8") for path in arc.PHASE_5_MUTATION_ROOT.rglob("*") if path.is_file())
        for value in ("m7i.xlarge", "supersedes only", arc.OBSERVABILITY_DESTINATION, "W3"):
            self.assertIn(value, phase_5)

    def test_critical_inventory_is_campaign_local(self) -> None:
        inventory = arc.critical_digests()
        self.assertIn("evals/arc_wayfinder_state_complexity.py", inventory)
        self.assertIn("evals/campaigns/arc-wayfinder-state-complexity-v1.json", inventory)
        self.assertNotIn("evals/arc_wayfinder_v2.py", inventory)


class PreparationAndMutationTests(unittest.TestCase):
    def test_pair_has_vanilla_A_and_installed_B(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            states = arc.prepare_pair(run_root=Path(temporary), require_frozen=False)
            a = Path(states["A"]["workspace"])
            b = Path(states["B"]["workspace"])
            self.assertFalse((a / ".agent-workflow").exists())
            self.assertIsNone(states["A"]["workflow_installation"])
            self.assertTrue((b / ".agent-workflow" / "routing.md").is_file())
            self.assertTrue((b / ".agents" / "skills" / "wayfinder" / "SKILL.md").is_file())
            self.assertTrue(all(arc.verify_automatic_workspace(states["B"])["checks"].values()))

    def test_mutations_preserve_agent_state_and_do_not_overwrite(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            state = arc.prepare_run("A", run_root=Path(temporary), require_frozen=False)
            workspace = Path(state["workspace"])
            note = workspace / "handoff.md"
            note.write_text(f"Settled: {arc.AMI_PARAMETER}\n", encoding="utf-8")
            arc.apply_phase_2_mutation(workspace)
            self.assertFalse((workspace / "docs" / "platform-facts.md").exists())
            self.assertIn(arc.AMI_PARAMETER, note.read_text(encoding="utf-8"))
            arc.apply_phase_3_mutation(workspace)
            self.assertTrue((workspace / "docs" / "decisions" / "D1-runner-compute-architecture.md").is_file())
            arc.apply_phase_5_mutation(workspace)
            self.assertTrue((workspace / "docs" / "decisions" / "D2-runner-instance-size.md").is_file())


class EvidenceAndGraderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.workspace = Path(self.temporary.name) / "repo"
        shutil.copytree(arc.FIXTURE_ROOT, self.workspace)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_arbitrary_prose_is_manual_evidence_not_classification(self) -> None:
        note = self.workspace / "handoff.md"
        note.write_text("m6i is stale. W3 legacy cleanup is blocked. W2 is actionable.\n", encoding="utf-8")
        packet = arc.state_evidence_packets(self.workspace, ["handoff.md"])
        self.assertTrue(packet["m6i_stale"]["manual_review_required"])
        self.assertNotIn("classification", packet["m6i_stale"])
        self.assertEqual(packet["m6i_stale"]["evidence"][0]["path"], "handoff.md")

    def test_wayfinder_contract_fields_are_structured(self) -> None:
        path = self.workspace / ".agent-wayfinder/arc/tickets/T1.md"
        path.parent.mkdir(parents=True)
        path.write_text("# T1\n\n- Status: ready\n- Blocked by: none\n- Related: D1, U3\n", encoding="utf-8")
        fields = arc.structured_wayfinder_fields(self.workspace)
        self.assertEqual(fields[0]["fields"]["status"], "ready")
        self.assertEqual(fields[0]["fields"]["blocked_by"], "none")

    def test_phase_2_grades_exact_fact_and_complete_safe_w2(self) -> None:
        before = arc.snapshot(self.workspace)
        write_complete_w1_w2(self.workspace)
        (self.workspace / "terraform" / "runners.tf").write_text(
            f'data "aws_ssm_parameter" "runner_ami" {{\n  name = "{arc.AMI_PARAMETER}"\n}}\n',
            encoding="utf-8",
        )
        grade = arc.grade_phase_2(self.workspace, before, {"observed_exact_fact_in_tool_output": True})
        self.assertTrue(grade["continuity"]["exact_fact_located_or_read"])
        self.assertTrue(grade["continuity"]["exact_fact_trusted_or_consumed"])
        self.assertTrue(grade["safe_progress"]["iam_permissions_boundary"])
        self.assertFalse(any(grade["decision_discipline"][key] for key in ("chose_instance_family", "chose_shared_or_dedicated", "chose_karpenter_or_managed_node_groups")))

    def test_phase_4_checks_parallel_w1_w2_and_keeps_w4_unimplemented(self) -> None:
        before = arc.snapshot(self.workspace)
        write_complete_w1_w2(self.workspace)
        format_terraform(self.workspace)
        grade = arc.grade_phase_4(self.workspace, before)
        self.assertTrue(all(grade["execution_quality"].values()))
        self.assertTrue(grade["production_readiness_slice_complete"])

    def test_phase_6_requires_selective_supersession_and_w4(self) -> None:
        write_complete_w1_w2(self.workspace, "m7i.large")
        phase_4 = arc.snapshot(self.workspace)
        before = arc.snapshot(self.workspace)
        before_texts = arc.read_texts(self.workspace, before)
        write_complete_w1_w2(self.workspace, "m7i.xlarge")
        (self.workspace / "terraform" / "observability.tf").write_text(
            f'''resource "aws_cloudwatch_metric_alarm" "failed_runner_jobs" {{
  alarm_name = "arc-failed-runner-jobs"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods = 1
  metric_name = "FailedRunnerJobs"
  namespace = "ARC"
  period = 60
  statistic = "Sum"
  threshold = 0
  alarm_actions = ["{arc.OBSERVABILITY_DESTINATION}"]
}}
''',
            encoding="utf-8",
        )
        grade = arc.grade_phase_6(self.workspace, before, phase_4, before_texts)
        self.assertTrue(all(grade["execution_quality"].values()))
        self.assertTrue(grade["selective_continuation_complete"])
        self.assertEqual(grade["unnecessarily_changed_preexisting_terraform_files"], [])

    def test_event_parser_captures_fresh_id_usage_validation_and_fact(self) -> None:
        stdout = "\n".join([
            json.dumps({"type": "thread.started", "thread_id": "fresh-123"}),
            json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": "python3 -m unittest discover -s tests -v", "aggregated_output": arc.AMI_PARAMETER, "exit_code": 0}}),
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 120, "cached_input_tokens": 80, "output_tokens": 30, "reasoning_output_tokens": 12}}),
        ])
        summary = arc.event_execution_summary(stdout, 1.25)
        self.assertEqual(summary["execution_id"], "fresh-123")
        self.assertTrue(summary["observed_exact_fact_in_tool_output"])
        self.assertEqual(summary["reasoning_tokens"], 12)

    def test_minimal_environment_and_probe_contract(self) -> None:
        environment = arc.sanitized_agent_environment(Path("/private/tmp/isolated-codex-home"))
        self.assertEqual(environment["CODEX_HOME"], "/private/tmp/isolated-codex-home")
        self.assertNotIn("AWS_PROFILE", environment)
        self.assertTrue(arc.controller_conversation_not_reported(json.dumps({"controller_conversation_excerpt": None})))
        self.assertFalse(arc.controller_conversation_not_reported(json.dumps({"controller_conversation_excerpt": "controller"})))


if __name__ == "__main__":
    unittest.main()
