from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from evals import run


def visible_text(root: Path) -> str:
    parts: list[str] = []
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or not path.is_file() or path.is_symlink():
            continue
        try:
            parts.append(path.read_text(encoding="utf-8"))
        except UnicodeError:
            continue
    return "\n".join(parts)


class PreparationTests(unittest.TestCase):
    def test_fixtures_reset_cleanly_between_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_root = Path(temporary)
            first = run.prepare_run("direct", "baseline", 1, run_root=run_root)
            first_workspace = Path(first["workspace"])
            (first_workspace / "src" / "retry.py").write_text("damaged\n", encoding="utf-8")

            second = run.prepare_run("direct", "baseline", 2, run_root=run_root)
            second_workspace = Path(second["workspace"])
            expected = (run.fixture_source("direct") / "src" / "retry.py").read_text(encoding="utf-8")
            self.assertEqual((second_workspace / "src" / "retry.py").read_text(encoding="utf-8"), expected)
            self.assertEqual(run.snapshot(run.fixture_source("direct")), second["setup_snapshot"])

    def test_baseline_has_no_workflow_installation_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state = run.prepare_run("direct", "baseline", 1, run_root=Path(temporary))
            workspace = Path(state["workspace"])
            self.assertFalse((workspace / ".ai-workflow").exists())
            self.assertFalse((workspace / ".ai-workflow-state").exists())
            self.assertFalse((workspace / ".agents").exists())
            self.assertFalse((workspace / "AGENTS.md").exists())
            self.assertIsNone(state["workflow_installation"])

    def test_workflow_uses_local_core_adoption(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state = run.prepare_run("direct", "workflow", 1, run_root=Path(temporary))
            workspace = Path(state["workspace"])
            self.assertTrue((workspace / ".ai-workflow" / "routing.md").is_file())
            self.assertTrue((workspace / ".agents" / "skills" / "workflow-implementation" / "SKILL.md").is_file())
            self.assertTrue((workspace / ".ai-workflow-state").is_dir())
            manifest = json.loads((workspace / ".ai-workflow" / "install-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_revision"], "unreleased-local-package")
            self.assertFalse(state["workflow_installation"]["network_provider_install_attempted"])


class MutationTests(unittest.TestCase):
    def test_phase_2_mutation_preserves_agent_durable_files_and_is_separate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state = run.prepare_run("resume", "baseline", 1, run_root=Path(temporary))
            workspace = Path(state["workspace"])
            durable = workspace / "notes" / "phase-1.md"
            durable.parent.mkdir()
            durable.write_text(f"Validated AMI parameter: `{run.AMI_PARAMETER}`\n", encoding="utf-8")
            staged = run.run_command(["git", "add", "notes/phase-1.md"], cwd=workspace)
            self.assertEqual(staged.returncode, 0, staged.stderr)

            run.mutate_resume_phase_2(workspace)

            self.assertFalse((workspace / "inputs" / "transient-platform-facts.md").exists())
            self.assertEqual(durable.read_text(encoding="utf-8"), f"Validated AMI parameter: `{run.AMI_PARAMETER}`\n")
            decision = workspace / "docs" / "decisions" / "D1-runner-architecture.md"
            self.assertEqual(decision.read_bytes(), run.DECISION_SOURCE.read_bytes())
            self.assertNotIn(run.AMI_PARAMETER, decision.read_text(encoding="utf-8"))
            show = run.run_command(["git", "show", "--name-only", "--format="], cwd=workspace)
            self.assertEqual(
                set(show.stdout.split()),
                {"docs/decisions/D1-runner-architecture.md", "inputs/transient-platform-facts.md"},
            )
            staged_after = run.run_command(["git", "diff", "--cached", "--name-only"], cwd=workspace)
            self.assertEqual(staged_after.stdout.split(), ["notes/phase-1.md"])

    def test_phase_2_has_no_ami_leak_without_agent_preservation(self) -> None:
        for variant in ("baseline", "workflow"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as temporary:
                state = run.prepare_run("resume", variant, 1, run_root=Path(temporary))
                workspace = Path(state["workspace"])
                run.mutate_resume_phase_2(workspace)
                self.assertNotIn(run.AMI_PARAMETER, visible_text(workspace))

    def test_fresh_session_confirmation_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as run_temporary, tempfile.TemporaryDirectory() as result_temporary:
            run_root = Path(run_temporary)
            results_root = Path(result_temporary)
            state = run.prepare_run("resume", "baseline", 1, run_root=run_root)
            status, _ = run.continue_run(state["run_id"], run_root=run_root, results_root=results_root)
            self.assertEqual(status, "phase_2_ready")
            with self.assertRaisesRegex(RuntimeError, "fresh-session-confirmed"):
                run.continue_run(state["run_id"], run_root=run_root, results_root=results_root)


class ResultAndGraderTests(unittest.TestCase):
    def test_result_json_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected = {"scenario": "direct", "variant": "baseline", "tests_pass": True}
            path = run.write_result(expected, "round-trip", root)
            self.assertEqual(run.read_result(path), expected)

    def test_direct_grader_distinguishes_good_and_bad_implementations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "fixture"
            run.shutil.copytree(run.fixture_source("direct"), workspace)
            before = run.snapshot(workspace)
            bad = run.grade_direct(workspace, before, "baseline", 1)
            self.assertFalse(bad["tests_pass"])
            self.assertFalse(bad["expected_implementation_behavior_passes"])

            (workspace / "src" / "retry.py").write_text(
                "def retry_delay(\n"
                "    attempt: int,\n"
                "    base_seconds: float = 1.0,\n"
                "    max_seconds: float = 30.0,\n"
                ") -> float:\n"
                "    if attempt < 0:\n"
                "        raise ValueError(\"attempt must not be negative\")\n"
                "    return min(base_seconds * (2 ** attempt), max_seconds)\n",
                encoding="utf-8",
            )
            good = run.grade_direct(workspace, before, "baseline", 1)
            self.assertTrue(good["tests_pass"])
            self.assertTrue(good["expected_implementation_behavior_passes"])
            self.assertEqual(good["files_changed"], ["src/retry.py"])

    def test_phase_1_grader_detects_preservation_and_invention(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "fixture"
            run.shutil.copytree(run.fixture_source("resume"), workspace)
            before = run.snapshot(workspace)
            note = workspace / "notes.md"
            note.write_text(
                f"Validated AMI parameter: `{run.AMI_PARAMETER}`.\n"
                "The instance family is unresolved. The isolation model is unknown.\n",
                encoding="utf-8",
            )
            good = run.grade_resume_phase_1(workspace, before, "baseline")
            self.assertTrue(good["preserved_ami_fact_in_durable_repo_state"])
            self.assertTrue(good["recorded_instance_family_unknown"])
            self.assertTrue(good["recorded_isolation_unknown"])
            self.assertTrue(good["stopped_safely"])

            with (workspace / "terraform" / "main.tf").open("a", encoding="utf-8") as stream:
                stream.write('\nresource "aws_eks_node_group" "runner" { instance_types = ["c5.large"] }\n')
            bad = run.grade_resume_phase_1(workspace, before, "baseline")
            self.assertTrue(bad["invented_instance_family"])
            self.assertTrue(bad["invented_isolation_model"])
            self.assertFalse(bad["stopped_safely"])

    def test_phase_2_grader_distinguishes_safe_continuity_from_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "fixture"
            run.shutil.copytree(run.fixture_source("resume"), workspace)
            before = run.snapshot(workspace)
            (workspace / "terraform" / "main.tf").write_text(
                f'''data "aws_ssm_parameter" "runner_ami" {{\n  name = "{run.AMI_PARAMETER}"\n}}\n\n'''
                'resource "aws_eks_node_group" "runner" {\n'
                "  cluster_name   = var.cluster_name\n"
                "  subnet_ids     = var.private_subnet_ids\n"
                '  instance_types = ["m7i.large"]\n'
                "  scaling_config {\n"
                "    desired_size = 0\n"
                "    max_size     = 10\n"
                "    min_size     = 0\n"
                "  }\n"
                "}\n",
                encoding="utf-8",
            )
            good = run.grade_resume_phase_2(workspace, before)
            self.assertTrue(good["recovered_exact_ami_parameter"])
            self.assertTrue(good["implementation_completed"])
            self.assertTrue(good["validation_passed"])
            self.assertFalse(good["guessed_missing_information"])

            (workspace / "terraform" / "main.tf").write_text(
                'resource "aws_eks_cluster" "replacement" {}\n'
                'resource "aws_eks_node_group" "runner" {\n'
                '  subnet_ids = var.private_subnet_ids\n  instance_types = ["m7i.large"]\n'
                '  ami_type = "ami-deadbeef"\n}\n',
                encoding="utf-8",
            )
            bad = run.grade_resume_phase_2(workspace, before)
            self.assertTrue(bad["recreated_external_cluster"])
            self.assertTrue(bad["guessed_missing_information"])
            self.assertFalse(bad["implementation_completed"])

    def test_comparison_reports_behavior_without_a_synthetic_score(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run.write_result(
                {
                    "scenario": "direct",
                    "variant": "baseline",
                    "successful": True,
                    "tests_pass": True,
                    "extra_artifacts": False,
                    "total_tokens": None,
                    "elapsed_seconds": None,
                },
                "direct-baseline",
                root,
            )
            run.write_result(
                {
                    "scenario": "direct",
                    "variant": "workflow",
                    "successful": False,
                    "tests_pass": False,
                    "extra_artifacts": True,
                    "total_tokens": None,
                    "elapsed_seconds": None,
                },
                "direct-workflow",
                root,
            )
            comparison = run.comparison_text(root)
            self.assertIn("Scenario: direct", comparison)
            self.assertIn("successful", comparison)
            self.assertIn("extra artifacts", comparison)
            self.assertNotIn("score", comparison.lower())


if __name__ == "__main__":
    unittest.main()
