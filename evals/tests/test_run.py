from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from evals import run


HISTORICAL_RESULT_SHA256 = {
    "2026-08-15-initial-spike/direct-baseline-1-b27e6dbd54.json": "15c2434185979d85266a8c1a35b42365bc282ac04e01894bf2071835af25d543",
    "2026-08-15-initial-spike/direct-workflow-1-583922fcb9.json": "2dcb239da8b9d21bd7bc9a01fd8905a22586a6c6fba6b719c71d89a585a23fc5",
    "2026-08-15-initial-spike/resume-baseline-1-3e01672ee1.json": "d6e325daf3097bf9e83204972e57188907fe41d4392d82e6bc56d547a60b0617",
    "2026-08-15-initial-spike/resume-workflow-1-a7da21356d.json": "de8f7518d5d4e40622fb0dce91e4dee8befa3b5258cd3b6ed19fef1ab3ab5d15",
    "2026-08-15-three-paired-trials/direct-baseline-1-17940cccb0.json": "b60dd118c7013f47f0d77e94d08a455137b4f302eebb9da077a59736386cb6fe",
    "2026-08-15-three-paired-trials/direct-baseline-2-fd6c336414.json": "b7c6fdb675c39dd0f74938ec7a0debdf1a6aa01f5bacd8c74ef7d6d467443e22",
    "2026-08-15-three-paired-trials/direct-baseline-3-16c2aa5c13.json": "4fef3bb5d60e1dd38c6c70f12c8d8976c4f2daccebe701e9e4c1ead932492e58",
    "2026-08-15-three-paired-trials/direct-workflow-1-7c9f767d29.json": "ba1673c4103748d0fc57e968d312a8aee98ebbdb8503191627afeff7333043db",
    "2026-08-15-three-paired-trials/direct-workflow-2-a82addaf44.json": "3920390ebf77a738528b3eb09e53916b33d9a589b2fa478ee9957fec21c67824",
    "2026-08-15-three-paired-trials/direct-workflow-3-dff9d64823.json": "9bf76e8f3e043b14f383bb9f05d2806830fccfa92af6a6c6b23d0e40073b89b2",
    "2026-08-15-three-paired-trials/resume-baseline-1-686c2905f1.json": "9859676f0ed340716e7e60578fff23fec3c8dda147bcac4806b2935fe78c0ce1",
    "2026-08-15-three-paired-trials/resume-baseline-2-9da14bff94.json": "438b07cf39fb684ba34a9fc715e63684f88b77cbb2f179349b4f2e4ea153bd04",
    "2026-08-15-three-paired-trials/resume-baseline-3-55ca646e53.json": "c5cc47595a29ff2d0420617785088d9c9f88bb4a8b94b4b85b28ace93c30f153",
    "2026-08-15-three-paired-trials/resume-workflow-1-7f02e472ee.json": "238368ea000896f41ba1b5afe3330e46a93eca0e129fffa6874a234e9a23bde9",
    "2026-08-15-three-paired-trials/resume-workflow-2-434f756aed.json": "051c206a270a6762fd33af7fda92e73c2db8142895701ff666cb6a2cfae1f549",
    "2026-08-15-three-paired-trials/resume-workflow-3-1a01a370a5.json": "ab61a7d82df25e5d5d151b8db0ac0ad06abb27fe24e63f19c1fc7300aa1116f9",
}


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
            self.assertFalse((workspace / ".agent-workflow").exists())
            self.assertFalse((workspace / ".agent-wayfinder").exists())
            self.assertFalse((workspace / ".agents").exists())
            self.assertFalse((workspace / "AGENTS.md").exists())
            self.assertIsNone(state["workflow_installation"])

    def test_workflow_uses_local_core_adoption(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state = run.prepare_run("direct", "workflow", 1, run_root=Path(temporary))
            workspace = Path(state["workspace"])
            self.assertTrue((workspace / ".agent-workflow" / "routing.md").is_file())
            self.assertTrue((workspace / ".agents" / "skills" / "workflow-verification" / "SKILL.md").is_file())
            self.assertFalse((workspace / ".agents" / "skills" / "workflow-implementation").exists())
            self.assertTrue((workspace / ".agent-wayfinder").is_dir())
            manifest = json.loads((workspace / ".agent-workflow" / "install-manifest.json").read_text(encoding="utf-8"))
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
    def test_historical_result_contents_are_unchanged(self) -> None:
        for relative, expected_digest in HISTORICAL_RESULT_SHA256.items():
            with self.subTest(result=relative):
                self.assertEqual(run.file_digest(run.RESULTS_ROOT / relative), expected_digest)

    def test_result_json_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected = {"scenario": "direct", "variant": "baseline", "tests_pass": True}
            path = run.write_result(expected, "round-trip", root, "campaign-a")
            self.assertEqual(path, root / "campaign-a" / "round-trip.json")
            self.assertEqual(run.read_result(path), expected)

    def test_continuation_writes_into_the_prepared_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as run_temporary, tempfile.TemporaryDirectory() as result_temporary:
            run_root = Path(run_temporary)
            results_root = Path(result_temporary)
            state = run.prepare_run(
                "direct",
                "baseline",
                1,
                campaign="campaign-a",
                run_root=run_root,
            )
            status, path = run.continue_run(
                state["run_id"],
                run_root=run_root,
                results_root=results_root,
            )
            self.assertEqual(status, "completed")
            self.assertEqual(path, results_root / "campaign-a" / f"{state['run_id']}.json")
            self.assertEqual(run.read_result(path)["campaign"], "campaign-a")

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
            overflow_prone = run.grade_direct(workspace, before, "baseline", 1)
            self.assertFalse(overflow_prone["tests_pass"])
            self.assertFalse(overflow_prone["huge_attempt_semantic_test_passed"])
            self.assertFalse(overflow_prone["successful"])

            run.shutil.rmtree(workspace)
            run.shutil.copytree(run.fixture_source("direct"), workspace)
            before = run.snapshot(workspace)
            (workspace / "src" / "retry.py").write_text(
                "def retry_delay(\n"
                "    attempt: int,\n"
                "    base_seconds: float = 1.0,\n"
                "    max_seconds: float = 30.0,\n"
                ") -> float:\n"
                "    if attempt < 0:\n"
                "        raise ValueError(\"attempt must not be negative\")\n"
                "    try:\n"
                "        delay = base_seconds * (2 ** attempt)\n"
                "    except OverflowError:\n"
                "        return max_seconds\n"
                "    return min(delay, max_seconds)\n",
                encoding="utf-8",
            )
            good = run.grade_direct(workspace, before, "baseline", 1)
            self.assertTrue(good["tests_pass"])
            self.assertTrue(good["expected_implementation_behavior_passes"])
            self.assertTrue(good["huge_attempt_semantic_test_passed"])
            self.assertTrue(good["successful"])
            self.assertEqual(good["files_changed"], ["src/retry.py"])

    def test_os_metadata_does_not_contaminate_direct_artifact_grading(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "fixture"
            run.shutil.copytree(run.fixture_source("direct"), workspace)
            before = run.snapshot(workspace)
            (workspace / ".DS_Store").write_bytes(b"finder metadata")
            (workspace / "nested").mkdir()
            (workspace / "nested" / "Thumbs.db").write_bytes(b"windows metadata")

            self.assertEqual(run.snapshot(workspace), before)

            result = run.grade_direct(workspace, before, "baseline", 1)
            self.assertNotIn(".DS_Store", result["files_changed"])
            self.assertNotIn("nested/Thumbs.db", result["files_changed"])
            self.assertFalse(result["extra_artifacts"])

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

    def test_comparison_is_limited_to_one_campaign_without_a_synthetic_score(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run.write_result(
                {
                    "scenario": "direct",
                    "variant": "baseline",
                    "successful": True,
                    "tests_pass": True,
                    "huge_attempt_semantic_test_passed": True,
                    "extra_artifacts": False,
                    "total_tokens": None,
                    "elapsed_seconds": None,
                },
                "direct-baseline",
                root,
                "campaign-a",
            )
            run.write_result(
                {
                    "scenario": "direct",
                    "variant": "workflow",
                    "successful": False,
                    "tests_pass": False,
                    "huge_attempt_semantic_test_passed": False,
                    "extra_artifacts": True,
                    "total_tokens": None,
                    "elapsed_seconds": None,
                },
                "direct-workflow",
                root,
                "campaign-b",
            )
            comparison = run.comparison_text(root, "campaign-a")
            self.assertIn("Scenario: direct", comparison)
            self.assertIn("successful", comparison)
            self.assertIn("huge attempt semantic test passed", comparison)
            self.assertIn("extra artifacts", comparison)
            self.assertIn("1/1", comparison)
            self.assertIn("n/a", comparison)
            self.assertNotIn("score", comparison.lower())

            with self.assertRaisesRegex(ValueError, "requires one campaign"):
                run.comparison_text(root)


if __name__ == "__main__":
    unittest.main()
