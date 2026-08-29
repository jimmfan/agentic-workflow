from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from _behavior_test_support import behavior


class WayfinderBehaviorTests(unittest.TestCase):
    def test_wayfinder_assessment_can_end_without_durable_state(self) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "wayfinder-assessment-needs-no-state"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            stdout = (
                "No durable Wayfinder state is needed.\n\n"
                "[route: router → wayfinder → assessed-no-state]"
            )
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=before,
                stdout=stdout,
                stderr="",
                returncode=0,
                report={
                    "status": "success",
                    "summary": "No durable Wayfinder state is needed.",
                },
                verification=(),
                route_components=behavior.route_components(stdout),
            )

            failures = [
                result.detail
                for result in behavior.evaluate(evidence)
                if not result.passed
            ]
            self.assertEqual(failures, [])
            self.assertFalse((workspace / ".agent-wayfinder").exists())

            manufactured = workspace / ".agent-wayfinder/greeting/map.md"
            manufactured.parent.mkdir(parents=True)
            manufactured.write_text("# Manufactured planning state\n", encoding="utf-8")
            changed = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=behavior.snapshot(workspace),
                stdout=stdout,
                stderr="",
                returncode=0,
                report={
                    "status": "success",
                    "summary": "No durable Wayfinder state is needed.",
                },
                verification=(),
                route_components=behavior.route_components(stdout),
            )
            failed = {item.name for item in behavior.evaluate(changed) if not item.passed}
            self.assertIn("expect:repository_unchanged", failed)
            self.assertIn("must-not:unnecessary_planning_artifacts", failed)

    def test_required_live_safety_boundaries_remain_enabled(self) -> None:
        live_ids = {
            scenario.id for scenario in behavior.load_scenarios() if scenario.live
        }

        self.assertTrue(
            {
                "simple-bounded-task",
                "blocked-project",
                "wayfinder-read-only-stale-state",
                "wayfinder-accepted-residual-uncertainty",
                "wayfinder-state-cannot-grant-authority",
                "wayfinder-assessment-needs-no-state",
            }
            <= live_ids
        )

    def test_accepted_residual_relationship_assertions_distinguish_the_boundary(
        self,
    ) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        accepted = scenarios["wayfinder-accepted-residual-uncertainty"]
        accepted_relationships = [
            item
            for item in accepted.assertions
            if item.kind in {"glob_any_matches", "glob_none_matches"}
            and item.path.as_posix() == ".agent-wayfinder/*/map.md"
        ]
        self.assertEqual(len(accepted_relationships), 4)
        self.assertTrue(
            any(
                item.kind == "glob_any_matches"
                and item.path.as_posix()
                == ".agent-wayfinder/*/unknowns/U1-*.md"
                for item in accepted.assertions
            )
        )

        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(accepted, Path(temporary))
            map_path = next((workspace / ".agent-wayfinder").glob("*/map.md"))
            evidence_args = {
                "scenario": accepted,
                "workspace": workspace,
                "before": {},
                "stdout": "",
                "stderr": "",
                "returncode": 0,
                "report": {},
                "verification": (),
                "route_components": (),
            }

            def relationships_pass(text: str) -> bool:
                map_path.write_text(text + "\n", encoding="utf-8")
                evidence = behavior.RunEvidence(
                    after=behavior.snapshot(workspace),
                    **evidence_args,
                )
                return all(
                    behavior.evaluate_assertion(evidence, assertion).passed
                    for assertion in accepted_relationships
                )

            for correct in (
                (
                    "The bounded pilot may proceed and is ready for handoff. "
                    "Production sizing remains blocked."
                ),
                (
                    "The pilot is not blocked and is ready. Production is not ready "
                    "and remains blocked."
                ),
                "The pilot is approved to proceed. Production remains blocked.",
            ):
                with self.subTest(correct=correct):
                    self.assertTrue(relationships_pass(correct))

            for incorrect in (
                "The bounded pilot remains blocked. Production sizing is ready.",
                (
                    "Ready frontier: the pilot remains blocked. Production sizing "
                    "remains blocked."
                ),
                (
                    "The pilot may proceed. Blocked work includes logging; production "
                    "is ready."
                ),
                "The pilot may proceed. Production is not ready.",
            ):
                with self.subTest(incorrect=incorrect):
                    self.assertFalse(relationships_pass(incorrect))

    def test_answered_authority_scenario_requires_reconciliation_and_pruning(
        self,
    ) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        answered = scenarios["wayfinder-answered-unknown-authority-choice"]
        assertion_paths = {
            (assertion.kind, assertion.path.as_posix(), assertion.value)
            for assertion in answered.assertions
        }

        self.assertTrue(answered.live)
        self.assertIn(
            (
                "path_not_exists",
                ".agent-wayfinder/rollout-choice/unknowns/U1-rollout-strategy.md",
                None,
            ),
            assertion_paths,
        )
        self.assertIn(
            (
                "path_contains",
                ".agent-wayfinder/rollout-choice/decisions.md",
                "Option B",
            ),
            assertion_paths,
        )
        self.assertIn(
            (
                "path_contains",
                ".agent-wayfinder/rollout-choice/decisions.md",
                "responsible project owner",
            ),
            assertion_paths,
        )
        self.assertIn(
            (
                "path_contains",
                ".agent-wayfinder/rollout-choice/map.md",
                "ready",
            ),
            assertion_paths,
        )
        self.assertIn(
            ".agent-wayfinder/rollout-choice/unrelated-notes.md",
            {path.as_posix() for path in answered.preserve_paths},
        )
        self.assertNotIn(
            ".agent-wayfinder/rollout-choice/unknowns",
            {assertion.path.as_posix() for assertion in answered.assertions},
        )

        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(answered, Path(temporary))
            decisions = workspace / ".agent-wayfinder/rollout-choice/decisions.md"
            decisions.write_text(
                decisions.read_text(encoding="utf-8")
                + "\n## D8 — Rollout strategy\n\n"
                "- Authority: responsible project owner\n\nUse Option B.\n",
                encoding="utf-8",
            )
            evidence = behavior.RunEvidence(
                scenario=answered,
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
            failed_values = {
                assertion.value
                for assertion in answered.assertions
                if not behavior.evaluate_assertion(evidence, assertion).passed
            }
            self.assertIn("## D8", failed_values)
            self.assertIn("Option A", failed_values)

    def test_blocked_settlement_keeps_current_coordination_and_mapless_data(self) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "wayfinder-blocked-settlement"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            stdout = "Blocked on provider checksum.\n\n[route: router → wayfinder]"
            report = {
                "status": "blocked",
                "summary": "The effort remains current and resumable.",
                "blockers": ["provider checksum is not published"],
                "state_used": [
                    item.as_posix() for item in scenario.state_must_include
                ],
            }
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=before,
                stdout=stdout,
                stderr="",
                returncode=0,
                report=report,
                verification=(),
                route_components=behavior.route_components(stdout),
            )
            self.assertTrue(all(item.passed for item in behavior.evaluate(evidence)))

            (workspace / ".agent-wayfinder/blocked-provider-direction/map.md").unlink()
            (workspace / ".agent-wayfinder/blocked-provider-direction/unknowns/"
             "U1-provider-checksum.md").unlink()
            ended = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=behavior.snapshot(workspace),
                stdout=stdout,
                stderr="",
                returncode=0,
                report=report,
                verification=(),
                route_components=behavior.route_components(stdout),
            )
            failed = {item.name for item in behavior.evaluate(ended) if not item.passed}
            self.assertIn("expect:blocked_cleanly", failed)
            self.assertIn(
                "assert:.agent-wayfinder/blocked-provider-direction/map.md:exists",
                failed,
            )

    def test_conflicting_observations_and_questions_are_detected_independently(
        self,
    ) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "wayfinder-selective-unknown-promotion"
        )
        for label, keep_evidence, keep_unknown in (
            ("neither", False, False),
            ("evidence-only", True, False),
            ("unknown-only", False, True),
            ("both", True, True),
        ):
            with self.subTest(case=label), tempfile.TemporaryDirectory() as temporary:
                workspace = Path(temporary)
                effort = workspace / ".agent-wayfinder/conflict"
                effort.mkdir(parents=True)
                (effort / "map.md").write_text("# Conflict\n", encoding="utf-8")
                if keep_evidence:
                    evidence_path = effort / "evidence/E1-observation.md"
                    evidence_path.parent.mkdir()
                    evidence_path.write_text("# E1: Observation\n", encoding="utf-8")
                if keep_unknown:
                    unknown_path = effort / "unknowns/U1-current-question.md"
                    unknown_path.parent.mkdir()
                    unknown_path.write_text("# U1: Current question?\n", encoding="utf-8")
                run = behavior.RunEvidence(
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
                self.assertEqual(
                    behavior.wayfinder_record_changed(run, "evidence", "E"),
                    keep_evidence,
                )
                self.assertEqual(
                    behavior.wayfinder_record_changed(run, "unknowns", "U"),
                    keep_unknown,
                )

    def test_cross_system_fact_boundary_requires_evidence_without_local_fact_or_decision(
        self,
    ) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "wayfinder-cross-system-fact-boundary"
        )
        self.assertTrue(scenario.blind_grading)
        required = {
            (item.kind, item.path.as_posix(), item.value, item.count)
            for item in scenario.assertions
        }
        self.assertIn(
            ("glob_count", ".agent-wayfinder/*/evidence/E*.md", None, 1), required
        )
        self.assertIn(
            ("glob_count", ".agent-wayfinder/*/unknowns/U*.md", None, 1), required
        )
        self.assertIn(
            ("glob_count", ".agent-wayfinder/*/facts.md", None, 0), required
        )
        self.assertIn(
            ("glob_count", ".agent-wayfinder/*/decisions.md", None, 0), required
        )

    def test_progressive_state_contract_rejects_loading_an_unrelated_child(
        self,
    ) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "existing-wayfinder-state"
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
        progressive = next(
            result for result in results if result.name == "state-loading:progressive"
        )
        self.assertFalse(progressive.passed)
        self.assertIn("U1-name-telemetry-metric.md", progressive.detail)



    def test_presence_defines_current_records_and_conflicts_prune_unsupported_facts(
        self,
    ) -> None:
        for fixture_name, effort_name in (
            ("wayfinder-fact-conflict", "deployment-mode"),
            ("wayfinder-reference-settlement", "release-direction"),
        ):
            with self.subTest(fixture=fixture_name):
                effort = (
                    behavior.FIXTURE_ROOT
                    / fixture_name
                    / ".agent-wayfinder"
                    / effort_name
                )
                self.assertTrue((effort / "facts.md").is_file())
                self.assertTrue((effort / "decisions.md").is_file())
        unrelated = (
            behavior.FIXTURE_ROOT
            / "wayfinder-unrelated/.agent-wayfinder/database-migration"
        )
        self.assertTrue((unrelated / "decisions.md").is_file())
        self.assertIn(
            "## D1 — Preserve rollback",
            (unrelated / "decisions.md").read_text(encoding="utf-8"),
        )

        scenarios = {item.id: item for item in behavior.load_scenarios()}
        conflict = scenarios["wayfinder-fact-conflict"]
        required = {
            (item.kind, item.path.as_posix(), item.value)
            for item in conflict.assertions
        }
        self.assertIn(
            (
                "path_not_exists",
                ".agent-wayfinder/deployment-mode/facts.md",
                None,
            ),
            required,
        )
        for record in (
            ".agent-wayfinder/deployment-mode/evidence/E2-*.md",
            ".agent-wayfinder/deployment-mode/unknowns/U1-*.md",
        ):
            self.assertTrue(
                any(item.path.as_posix() == record for item in conflict.assertions)
            )
        self.assertIn(
            (
                "path_contains",
                ".agent-wayfinder/deployment-mode/decisions.md",
                "authority review",
            ),
            required,
        )
        self.assertIn(
            (
                "path_contains",
                ".agent-wayfinder/deployment-mode/decisions.md",
                "platform architecture policy",
            ),
            required,
        )
        self.assertIn(
            (
                "path_contains",
                ".agent-wayfinder/deployment-mode/decisions.md",
                "Use the dedicated capacity policy",
            ),
            required,
        )

        blocked = (
            behavior.FIXTURE_ROOT
            / "wayfinder-settlement/.agent-wayfinder/blocked-provider-direction"
        )
        self.assertTrue((blocked / "map.md").is_file())
        self.assertTrue((blocked / "unknowns/U1-provider-checksum.md").is_file())


if __name__ == "__main__":
    unittest.main()
