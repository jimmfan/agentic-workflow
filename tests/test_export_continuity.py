"""Evaluator controls; synthetic answers are not live behavior evidence."""

from dataclasses import replace
from pathlib import Path
import shutil
import tempfile
import unittest

from _behavior_test_support import behavior

MAP = ".project-efforts/photo-export/map.md"
BACKUP = "config/export-fallback.json"
SOURCE = "snapshots/export-r3.json"


class ExportContinuityTests(unittest.TestCase):
    def scenario(self, case="primary"):
        return behavior.load_scenario(
            behavior.SCENARIO_ROOT / f"photo-export-{case}.toml"
        )

    def evidence(self, workspace, before, case="primary"):
        return behavior.RunEvidence(
            scenario=self.scenario(case),
            workspace=workspace,
            before=before,
            after=behavior.snapshot(workspace),
            stdout="[route: router → direct]",
            stderr="",
            returncode=0,
            report={"status": "success", "state_used": [MAP]},
            verification=(),
            route_components=("direct",),
        )

    def failures(self, evidence):
        return [
            check.name for check in behavior.evaluate(evidence) if check.passed is False
        ]

    def preserve_copy(self, workspace):
        target = workspace / BACKUP
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(workspace / SOURCE, target)

    def reconcile(self, workspace):
        path = workspace / MAP
        path.write_text(
            path.read_text().replace(
                "a preserved export configuration has not been selected.",
                "version export-r3 is preserved locally in "
                "[export-fallback](../../config/export-fallback.json).\n"
                "Source: snapshots/export-r3.json (catalog reference export-r3).\n"
                "The user reports that the source works; the preserved copy has not been tested by exporting an image.\n"
                "This local fallback is neither committed nor published.",
            )
        )

    def test_primary_requires_exact_copy_and_saved_connection(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = behavior.copy_fixture(self.scenario(), Path(temp))
            before = behavior.snapshot(workspace)
            self.assertTrue(self.failures(self.evidence(workspace, before)))
            self.preserve_copy(workspace)
            self.assertTrue(self.failures(self.evidence(workspace, before)))
            self.reconcile(workspace)
            evidence = self.evidence(workspace, before)
            self.assertEqual(self.failures(evidence), [])
            # Real reads, status semantics and fresh-reader recovery still need adjudication.
            self.assertEqual(
                behavior.verdict(behavior.evaluate(evidence)), "INCONCLUSIVE"
            )
            for route in ("direct", "wayfinder"):
                self.assertEqual(
                    self.failures(
                        replace(
                            evidence,
                            stdout=f"[route: router → {route}]",
                            route_components=(route,),
                        )
                    ),
                    [],
                )
            (workspace / BACKUP).write_bytes(
                (workspace / "snapshots/export-r4.json").read_bytes()
            )
            self.assertIn(
                f"assert:{BACKUP}:sha256",
                self.failures(self.evidence(workspace, before)),
            )
            self.preserve_copy(workspace)
            with (workspace / BACKUP).open("ab") as output:
                output.write(b"\n")
            self.assertIn(
                f"assert:{BACKUP}:sha256",
                self.failures(self.evidence(workspace, before)),
            )

    def test_duplicate_effort_and_changed_source_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = behavior.copy_fixture(self.scenario(), Path(temp))
            before = behavior.snapshot(workspace)
            self.preserve_copy(workspace)
            self.reconcile(workspace)
            duplicate = workspace / ".project-efforts/export-copy/map.md"
            duplicate.parent.mkdir()
            duplicate.write_text("# Duplicate\n")
            self.assertIn(
                "must-not:unnecessary_planning_artifacts",
                self.failures(self.evidence(workspace, before)),
            )
            (workspace / SOURCE).write_text("overwritten")
            self.assertIn(
                "expect:project_state_preserved",
                self.failures(self.evidence(workspace, before)),
            )

    def test_controls_preserve_coordination_state(self):
        for case in ("ambiguous", "read-only", "unrelated"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                workspace = behavior.copy_fixture(self.scenario(case), Path(temp))
                before = behavior.snapshot(workspace)
                if case == "unrelated":
                    self.preserve_copy(workspace)
                evidence = self.evidence(workspace, before, case)
                self.assertEqual(self.failures(evidence), [])
                self.reconcile(workspace)
                self.assertIn(
                    "expect:project_state_preserved",
                    self.failures(self.evidence(workspace, before, case)),
                )

    def test_read_only_rejects_other_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = behavior.copy_fixture(self.scenario("read-only"), Path(temp))
            before = behavior.snapshot(workspace)
            self.preserve_copy(workspace)
            self.assertIn(
                "expect:repository_unchanged",
                self.failures(self.evidence(workspace, before, "read-only")),
            )

    def test_hash_rejects_symlink_and_symlink_ancestor(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = behavior.copy_fixture(self.scenario(), Path(temp))
            before = behavior.snapshot(workspace)
            (workspace / "config").mkdir()
            target = workspace / BACKUP
            target.symlink_to(workspace / SOURCE)
            self.assertIn(
                f"assert:{BACKUP}:path_sha256",
                self.failures(self.evidence(workspace, before)),
            )
            target.unlink()
            (workspace / "config").rmdir()
            (workspace / "config").symlink_to(
                workspace / "snapshots", target_is_directory=True
            )
            shutil.copyfile(workspace / SOURCE, target)
            self.assertIn(
                f"assert:{BACKUP}:sha256",
                self.failures(self.evidence(workspace, before)),
            )

    def test_hash_validation(self):
        for value in ("wrong", "A" * 64, "../snapshots/file", ""):
            with self.subTest(value=value), self.assertRaises(behavior.BehaviorError):
                behavior.load_assertions(
                    [{"kind": "path_sha256", "path": BACKUP, "value": value}], "test"
                )

    def test_read_only_rejects_test_report_and_preserves_request_text(self):
        scenario = replace(
            self.scenario("read-only"),
            request="Explain this. Before finishing, write nothing. Preserve this sentence.",
        )
        self.assertIn(scenario.request, behavior.build_prompt(scenario))
        with tempfile.TemporaryDirectory() as temp:
            workspace = behavior.copy_fixture(scenario, Path(temp))
            evidence_dir = workspace / ".behavior-evidence"
            evidence_dir.mkdir()
            (evidence_dir / "prompt.md").write_text(behavior.build_prompt(scenario))
            before = behavior.snapshot(workspace)
            self.assertEqual(
                self.failures(self.evidence(workspace, before, "read-only")), []
            )
            (evidence_dir / "report.json").write_text('{"status": "success"}')
            self.assertIn(
                "expect:repository_unchanged",
                self.failures(self.evidence(workspace, before, "read-only")),
            )

    def test_prompts_are_blind_and_read_only_does_not_request_report(self):
        for case in ("primary", "ambiguous", "read-only", "unrelated"):
            scenario = self.scenario(case)
            prompt = behavior.build_prompt(scenario)
            for hidden in (
                scenario.name,
                "path_sha256",
                "state_must_include",
                "Expected observable behavior",
            ):
                self.assertNotIn(hidden, prompt)
            if case == "primary":
                for cue in (
                    "Wayfinder",
                    "map.md",
                    "effort tracking",
                    "existing_state_reused",
                ):
                    self.assertNotIn(cue, prompt)
            if case == "read-only":
                self.assertNotIn("Before finishing, write", prompt)
                self.assertNotIn(".behavior-evidence/report.json", prompt)
            else:
                self.assertIn("Before finishing, write", prompt)


if __name__ == "__main__":
    unittest.main()
