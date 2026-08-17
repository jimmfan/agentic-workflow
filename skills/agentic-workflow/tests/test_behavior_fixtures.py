from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


TEST_ROOT = Path(__file__).resolve().parent


def load_behavior():
    path = TEST_ROOT / "behavior.py"
    spec = importlib.util.spec_from_file_location("agentic_workflow_behavior_fixtures", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


behavior = load_behavior()


class BehaviorFixtureTests(unittest.TestCase):
    def test_every_fixture_survives_full_lifecycle_sequence(self) -> None:
        for scenario in behavior.load_scenarios():
            with self.subTest(scenario=scenario.id):
                passed, detail = behavior.exercise_fixture_lifecycle(scenario)
                self.assertTrue(passed, detail)

    def test_fixture_copy_is_disposable_and_resettable(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "simple-bounded-task"
        )
        source = behavior.snapshot(behavior.FIXTURE_ROOT / scenario.fixture)
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            workspace_one = behavior.copy_fixture(scenario, Path(first))
            (workspace_one / "app.py").write_text("changed disposable bytes\n", encoding="utf-8")
            workspace_two = behavior.copy_fixture(scenario, Path(second))
            self.assertEqual(behavior.snapshot(workspace_two), source)
        self.assertEqual(behavior.snapshot(behavior.FIXTURE_ROOT / scenario.fixture), source)

    def test_wayfinder_state_is_not_seeded_by_install(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "wayfinder-new-effort"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            install = behavior.run_adopt("install", workspace)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            state_root = workspace / ".ai-workflow-state"
            self.assertTrue(state_root.is_dir())
            self.assertFalse((state_root / "wayfinder").exists())
            self.assertFalse((state_root / "active.md").exists())
            self.assertFalse((workspace / ".scratch").exists())

    def test_state_preservation_oracle_detects_destructive_change(self) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "project-state-preservation"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            install = behavior.run_adopt("install", workspace)
            self.assertEqual(install.returncode, 0, install.stderr)
            before = behavior.snapshot(workspace)
            target = workspace / ".ai-workflow-state/custom/owner-note.txt"
            target.write_text("destructive replacement\n", encoding="utf-8")
            (workspace / "AGENTS.md").write_text("unauthorized policy replacement\n", encoding="utf-8")
            after = behavior.snapshot(workspace)
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=after,
                stdout="",
                stderr="",
                returncode=0,
                report={"status": "success"},
                verification=(),
                route_components=(),
            )
            results = behavior.evaluate(evidence)
            repository_changes = behavior.repository_changes(evidence)
        failed = {result.name for result in results if not result.passed}
        self.assertIn("AGENTS.md", repository_changes)
        self.assertIn("expect:project_state_preserved", failed)
        self.assertIn("must-not:overwrite_project_owned_state", failed)

    def test_implementation_fixture_verifiers_begin_red(self) -> None:
        fixture_names = {
            "simple-project",
            "external-fact",
            "wayfinder-existing",
            "actionable-work",
            "implementation-project",
            "verification-failure",
            "wayfinder-unrelated",
        }
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            scenarios = {scenario.fixture: scenario for scenario in behavior.load_scenarios()}
            for name in sorted(fixture_names):
                with self.subTest(fixture=name):
                    workspace = behavior.copy_fixture(scenarios[name], temporary_root)
                    result = subprocess.run(
                        [behavior.sys.executable, "verify.py"],
                        cwd=workspace,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
