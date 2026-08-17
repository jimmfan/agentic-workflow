from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest


TEST_ROOT = Path(__file__).resolve().parent


def load_behavior():
    path = TEST_ROOT / "behavior.py"
    spec = importlib.util.spec_from_file_location("agentic_workflow_behavior", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


behavior = load_behavior()


class BehaviorContractTests(unittest.TestCase):
    def test_catalog_has_thirteen_contracts_and_seven_live_smokes(self) -> None:
        scenarios = behavior.load_scenarios()
        self.assertEqual(len(scenarios), 13)
        self.assertEqual(sum(scenario.live for scenario in scenarios), 7)
        self.assertEqual(
            {scenario.id for scenario in scenarios},
            {
                "simple-bounded-task",
                "external-factual-uncertainty",
                "genuine-unresolved-decision",
                "existing-wayfinder-state",
                "existing-actionable-work",
                "meaningful-implementation",
                "verification-failure-recovery",
                "blocked-project",
                "project-state-preservation",
                "wayfinder-read-only-stale-state",
                "wayfinder-reconciliation-conflict",
                "wayfinder-new-effort",
                "unrelated-wayfinder-state",
            },
        )
        read_only = next(
            scenario for scenario in scenarios if scenario.id == "wayfinder-read-only-stale-state"
        )
        self.assertIn("unresolved", read_only.report_must_include)

    def test_scenarios_reject_unknown_behavior_vocabulary(self) -> None:
        source = (behavior.SCENARIO_ROOT / "simple-bounded-task.toml").read_text(encoding="utf-8")
        invalid = source.replace('"task_completed"', '"implementation_route_exactly"', 1)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "simple-bounded-task.toml"
            path.write_text(invalid, encoding="utf-8")
            with self.assertRaisesRegex(behavior.BehaviorError, "unknown expectations"):
                behavior.load_scenario(path)

    def test_fixtures_remain_small_and_human_readable(self) -> None:
        for fixture in behavior.FIXTURE_ROOT.iterdir():
            if not fixture.is_dir():
                continue
            files = [path for path in fixture.rglob("*") if path.is_file()]
            with self.subTest(fixture=fixture.name):
                self.assertLessEqual(len(files), 8)
                self.assertTrue(all(path.stat().st_size < 12_000 for path in files))

    def test_live_runner_requires_one_valid_marker_at_end_of_final_response(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "simple-bounded-task"
        )
        agent_source = textwrap.dedent(
            """
            import json
            from pathlib import Path
            import subprocess
            import sys

            Path("app.py").write_text(
                'def greeting() -> str:\\n    return "hello, world!"\\n',
                encoding="utf-8",
            )
            check = subprocess.run(
                [sys.executable, "verify.py"],
                capture_output=True,
                text=True,
            )
            report = {
                "schema_version": 1,
                "status": "success" if check.returncode == 0 else "failed",
                "summary": "updated and checked greeting",
                "verification": [{"command": "python verify.py", "exit_code": check.returncode}],
                "research_sources": [],
                "state_used": [],
                "blockers": [],
            }
            Path(".behavior-evidence/report.json").write_text(json.dumps(report), encoding="utf-8")
            print("Implemented and verified.\\n\\n[route: router → direct]")
            raise SystemExit(check.returncode)
            """
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            agent = root / "fake_agent.py"
            agent.write_text(agent_source, encoding="utf-8")
            evidence, results = behavior.run_live_scenario(
                scenario,
                [behavior.sys.executable, str(agent)],
                root,
                30,
            )
        self.assertEqual(evidence.route_components, ("direct",))
        self.assertTrue(all(result.passed for result in results), results)

    def test_route_visibility_rejects_missing_duplicate_malformed_and_nonfinal_markers(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "simple-bounded-task"
        )
        cases = {
            "missing": "done",
            "duplicate": "[route: router → direct]\n[route: router → direct]",
            "malformed": "[route: direct]",
            "nonfinal": "[route: router → direct]\nmore text",
        }
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            snapshot = behavior.snapshot(workspace)
            for label, stdout in cases.items():
                with self.subTest(label=label):
                    evidence = behavior.RunEvidence(
                        scenario=scenario,
                        workspace=workspace,
                        before=snapshot,
                        after=snapshot,
                        stdout=stdout,
                        stderr="[route: router → direct]",
                        returncode=0,
                        report={"route_marker": "[route: router → direct]"},
                        verification=(),
                        route_components=behavior.route_components(stdout),
                    )
                    result = next(
                        item
                        for item in behavior.evaluate(evidence)
                        if item.name == "route-marker:exactly-one-valid-final"
                    )
                    self.assertFalse(result.passed)

    def test_success_report_without_failure_recovery_fails_the_contract(self) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "verification-failure-recovery"
        )
        agent_source = textwrap.dedent(
            """
            import json
            from pathlib import Path

            Path(".behavior-evidence/verification.jsonl").write_text(
                json.dumps({"command": "python verify.py", "exit_code": 0}) + "\\n",
                encoding="utf-8",
            )
            report = {
                "schema_version": 1,
                "status": "success",
                "summary": "claimed success without observing the initial failure",
                "verification": [],
                "research_sources": [],
                "state_used": [],
                "blockers": [],
            }
            Path(".behavior-evidence/report.json").write_text(json.dumps(report), encoding="utf-8")
            """
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            agent = root / "fake_agent.py"
            agent.write_text(agent_source, encoding="utf-8")
            _evidence, results = behavior.run_live_scenario(
                scenario,
                [behavior.sys.executable, str(agent)],
                root,
                30,
            )
        failed_names = {result.name for result in results if not result.passed}
        self.assertIn("expect:verification_failure_recovered", failed_names)
        self.assertIn("expect:meaningful_repository_change", failed_names)

    def test_self_report_does_not_replace_observed_verification(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "meaningful-implementation"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=before,
                stdout="",
                stderr="",
                returncode=0,
                report={
                    "status": "success",
                    "verification": [{"command": "python verify.py", "exit_code": 0}],
                },
                verification=(),
                route_components=(),
            )
            results = behavior.evaluate(evidence)
        failed_names = {result.name for result in results if not result.passed}
        self.assertIn("expect:verification_performed", failed_names)

    def test_progressive_state_contract_rejects_loading_an_unrelated_child(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "existing-wayfinder-state"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            report = {
                "status": "success",
                "state_used": [
                    *(item.as_posix() for item in scenario.state_must_include),
                    *(item.as_posix() for item in scenario.state_must_not_include),
                ],
            }
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=before,
                stdout="",
                stderr="",
                returncode=0,
                report=report,
                verification=(),
                route_components=(),
            )
            results = behavior.evaluate(evidence)
        progressive = next(result for result in results if result.name == "state-loading:progressive")
        self.assertFalse(progressive.passed)
        self.assertIn("U1-name-telemetry-metric.md", progressive.detail)

    def test_wayfinder_new_effort_is_demand_driven_and_allows_implicit_provider_execution(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "wayfinder-new-effort"
        )
        request = scenario.request.lower()
        self.assertNotIn("$wayfinder", request)
        self.assertNotIn("/wayfinder", request)
        self.assertNotIn("create a wayfinder map", request)
        self.assertNotIn("claim_unexecuted_provider", scenario.must_not)
        self.assertIn("unresolved ordering", request)
        self.assertIn("while part of the plan is blocked", request)

    def test_glob_assertions_accept_stable_ids_without_fixing_filename_slugs(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "wayfinder-new-effort"
        )
        count_assertion = next(
            item
            for item in scenario.assertions
            if item.kind == "glob_count" and "unknowns/U" in item.path.as_posix()
        )
        content_assertion = next(
            item
            for item in scenario.assertions
            if item.kind == "glob_contains" and "unknowns/U" in item.path.as_posix()
        )
        self.assertTrue(content_assertion.path.name.startswith("U1-"))
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            unknowns = workspace / ".ai-workflow-state/wayfinder/platform-migration/unknowns"
            unknowns.mkdir(parents=True)
            stable_unknown = unknowns / "U1-any-clear-slug-is-valid.md"
            stable_unknown.write_text(
                "# U1: Determine the safe migration order\n",
                encoding="utf-8",
            )
            after_one = behavior.snapshot(workspace)
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before={},
                after=after_one,
                stdout="",
                stderr="",
                returncode=0,
                report={},
                verification=(),
                route_components=(),
            )
            self.assertTrue(behavior.evaluate_assertion(evidence, count_assertion).passed)
            self.assertTrue(behavior.evaluate_assertion(evidence, content_assertion).passed)

            (unknowns / "U2-unjustified-extra.md").write_text(
                "# U2: Unjustified extra unknown\n",
                encoding="utf-8",
            )
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before={},
                after=behavior.snapshot(workspace),
                stdout="",
                stderr="",
                returncode=0,
                report={},
                verification=(),
                route_components=(),
            )
            self.assertFalse(behavior.evaluate_assertion(evidence, count_assertion).passed)

            stable_unknown.unlink()
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before={},
                after=behavior.snapshot(workspace),
                stdout="",
                stderr="",
                returncode=0,
                report={},
                verification=(),
                route_components=(),
            )
            self.assertTrue(behavior.evaluate_assertion(evidence, count_assertion).passed)
            self.assertFalse(behavior.evaluate_assertion(evidence, content_assertion).passed)


if __name__ == "__main__":
    unittest.main()
