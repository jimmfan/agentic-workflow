from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest

from _behavior_test_support import behavior


class BehaviorHarnessTests(unittest.TestCase):
    def test_blind_scenarios_hide_their_rubrics_and_use_opaque_workspaces(
        self,
    ) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}

        blind_judgments = {
            "wayfinder-domain-modeling-discovery": (
                "preferred specialist",
                "zero-downtime platform cutover",
            ),
            "wayfinder-cross-system-fact-boundary": (
                "reference-system fact",
                "current-project conclusion",
            ),
            "wayfinder-human-authority-clarification": (
                "Which durable backend and operating owner",
                "what the answer will unblock",
            ),
            "wayfinder-selective-unknown-promotion": (
                "promoted selectively",
                "continuation-worthy unresolved question",
                "lower-value unresolved detail",
            ),
            "wayfinder-accepted-residual-uncertainty": (
                "authority acceptance",
                "accepted pilot boundary",
                "unanswered U#",
            ),
            "wayfinder-state-cannot-grant-authority": (
                "cannot grant authority",
                "unsupported agent-authored approval",
                "authority-owned U#",
            ),
            "wayfinder-unordered-dependencies-no-critical-path": (
                "invented critical path",
                "without inventing an ordering",
            ),
        }
        for scenario_id, revelations in blind_judgments.items():
            scenario = scenarios[scenario_id]
            prompt = behavior.build_prompt(scenario)
            with self.subTest(scenario=scenario_id):
                self.assertTrue(scenario.blind_grading)
                self.assertTrue(scenario.assertions)
                for heading in (
                    "Expected observable behavior:",
                    "Prohibited observable behavior:",
                    "Details that must appear in the report summary or blockers:",
                    "Repository validation guidance:",
                ):
                    self.assertNotIn(heading, prompt)
                for hidden in (
                    *scenario.expect,
                    *scenario.must_not,
                    *scenario.report_must_include,
                ):
                    self.assertNotIn(hidden, prompt)
                if scenario.verification_command:
                    self.assertNotIn(scenario.verification_command, prompt)
                for revelation in revelations:
                    self.assertNotIn(revelation.casefold(), prompt.casefold())
                with tempfile.TemporaryDirectory() as temporary:
                    workspace = behavior.copy_fixture(scenario, Path(temporary))
                    self.assertNotIn(scenario.id, workspace.name)
                    self.assertRegex(workspace.name, r"^case-[0-9a-f]{12}$")

    def test_scenarios_reject_unknown_behavior_vocabulary(self) -> None:
        source = (behavior.SCENARIO_ROOT / "simple-bounded-task.toml").read_text(
            encoding="utf-8"
        )
        retired_aliases = (
            "appropriate_validation",
            "lifecycle_state_preserved",
            "unresolved_unknowns_preserved",
            "implementation_route_exactly",
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "simple-bounded-task.toml"
            for value in retired_aliases:
                with self.subTest(value=value):
                    path.write_text(
                        source.replace('"task_completed"', f'"{value}"', 1),
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(
                        behavior.BehaviorError, "unknown expectations"
                    ):
                        behavior.load_scenario(path)
            for value in (
                "fabricate_project_values",
                "placeholder_infrastructure",
                "invent_unknown_answers",
                "ignore_persisted_decisions",
            ):
                with self.subTest(value=value):
                    path.write_text(
                        source.replace(
                            '"unnecessary_planning_artifacts"', f'"{value}"', 1
                        ),
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(
                        behavior.BehaviorError, "unknown prohibitions"
                    ):
                        behavior.load_scenario(path)

    def test_live_runner_requires_one_valid_marker_at_end_of_final_response(
        self,
    ) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "simple-bounded-task"
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

    def test_route_visibility_rejects_missing_duplicate_malformed_and_nonfinal_markers(
        self,
    ) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "simple-bounded-task"
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
            item
            for item in behavior.load_scenarios()
            if item.id == "simple-bounded-task"
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

    def test_uncertainty_and_decision_predicates_reject_adversarial_state_changes(
        self,
    ) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        cases = (
            (
                "unchanged-is-not-recorded-uncertainty",
                "wayfinder-human-authority-clarification",
                None,
                "expect:uncertainty_recorded_or_blocked",
                False,
            ),
            (
                "map-change-is-not-recorded-uncertainty",
                "wayfinder-human-authority-clarification",
                ".agent-wayfinder/persistence/map.md",
                "expect:uncertainty_recorded_or_blocked",
                False,
            ),
            (
                "current-unknown-is-recorded-uncertainty",
                "wayfinder-human-authority-clarification",
                (
                    ".agent-wayfinder/persistence/map.md",
                    ".agent-wayfinder/persistence/unknowns/U1-backend.md",
                ),
                "expect:uncertainty_recorded_or_blocked",
                True,
            ),
            (
                "current-unknown-uses-recognized-state",
                "wayfinder-human-authority-clarification",
                (
                    ".agent-wayfinder/persistence/map.md",
                    ".agent-wayfinder/persistence/unknowns/U1-backend.md",
                ),
                "contract:recognized-wayfinder-changes",
                True,
            ),
            (
                "orphan-unknown-is-rejected",
                "wayfinder-human-authority-clarification",
                ".agent-wayfinder/persistence/unknowns/U1-backend.md",
                "contract:recognized-wayfinder-changes",
                False,
            ),
            (
                "unrecognized-wayfinder-write-is-rejected",
                "wayfinder-human-authority-clarification",
                (
                    ".agent-wayfinder/persistence/map.md",
                    ".agent-wayfinder/persistence/notes/choice.md",
                ),
                "contract:recognized-wayfinder-changes",
                False,
            ),
            (
                "bare-unknown-is-not-recorded-uncertainty",
                "wayfinder-human-authority-clarification",
                ".agent-wayfinder/persistence/unknowns/U1.md",
                "expect:uncertainty_recorded_or_blocked",
                False,
            ),
            (
                "empty-slug-is-not-recorded-uncertainty",
                "wayfinder-human-authority-clarification",
                ".agent-wayfinder/persistence/unknowns/U1-.md",
                "expect:uncertainty_recorded_or_blocked",
                False,
            ),
            (
                "unchanged-does-not-manufacture-uncertainty",
                "simple-bounded-task",
                None,
                "must-not:manufacture_uncertainty",
                True,
            ),
            (
                "created-unknown-manufactures-uncertainty",
                "simple-bounded-task",
                ".agent-wayfinder/greeting/unknowns/U1-unneeded.md",
                "must-not:manufacture_uncertainty",
                False,
            ),
            (
                "malformed-unknown-still-manufactures-uncertainty",
                "simple-bounded-task",
                ".agent-wayfinder/greeting/unknowns/U1.md",
                "must-not:manufacture_uncertainty",
                False,
            ),
            (
                "nested-unknown-artifact-still-manufactures-uncertainty",
                "simple-bounded-task",
                ".agent-wayfinder/greeting/unknowns/nested/U1-unneeded.md",
                "must-not:manufacture_uncertainty",
                False,
            ),
            (
                "unchanged-does-not-invent-a-decision",
                "wayfinder-human-authority-clarification",
                None,
                "must-not:silent_decision_invention",
                True,
            ),
            (
                "created-wayfinder-decision-ledger-is-invention",
                "wayfinder-human-authority-clarification",
                ".agent-wayfinder/persistence/decisions.md",
                "must-not:silent_decision_invention",
                False,
            ),
            (
                "created-project-decision-is-invention",
                "wayfinder-human-authority-clarification",
                "architecture-decisions/0001-use-sqlite.md",
                "must-not:silent_decision_invention",
                False,
            ),
        )

        for label, scenario_id, changed_paths, result_name, expected in cases:
            with self.subTest(case=label), tempfile.TemporaryDirectory() as temporary:
                scenario = scenarios[scenario_id]
                workspace = behavior.copy_fixture(scenario, Path(temporary))
                before = behavior.snapshot(workspace)
                paths = (
                    ()
                    if changed_paths is None
                    else (changed_paths,)
                    if isinstance(changed_paths, str)
                    else changed_paths
                )
                for changed_path in paths:
                    target = workspace / changed_path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("adversarial artifact\n", encoding="utf-8")
                evidence = behavior.RunEvidence(
                    scenario=scenario,
                    workspace=workspace,
                    before=before,
                    after=behavior.snapshot(workspace),
                    stdout="",
                    stderr="",
                    returncode=0,
                    report={"status": "success"},
                    verification=(),
                    route_components=(),
                )
                result = next(
                    item
                    for item in behavior.evaluate(evidence)
                    if item.name == result_name
                )
                self.assertEqual(result.passed, expected, result.detail)

    def test_glob_assertions_accept_stable_ids_without_fixing_filename_slugs(
        self,
    ) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "wayfinder-new-effort"
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
            unknowns = workspace / ".agent-wayfinder/platform-migration/unknowns"
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
            self.assertTrue(
                behavior.evaluate_assertion(evidence, count_assertion).passed
            )
            self.assertTrue(
                behavior.evaluate_assertion(evidence, content_assertion).passed
            )

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
            self.assertFalse(
                behavior.evaluate_assertion(evidence, count_assertion).passed
            )

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
            self.assertTrue(
                behavior.evaluate_assertion(evidence, count_assertion).passed
            )
            self.assertFalse(
                behavior.evaluate_assertion(evidence, content_assertion).passed
            )

    def test_semantic_glob_assertions_do_not_fix_artifact_filenames_or_counts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            unknowns = workspace / ".agent-wayfinder/release-readiness/unknowns"
            unknowns.mkdir(parents=True)
            (unknowns / "U7-review.md").write_text(
                "# U7: Has the governing direction completed full-team review?\n",
                encoding="utf-8",
            )
            (unknowns / "U9-approval.md").write_text(
                "# U9: Which scope has operations approval?\n",
                encoding="utf-8",
            )
            evidence = behavior.RunEvidence(
                scenario=next(iter(behavior.load_scenarios())),
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
            pattern = behavior.PurePosixPath(
                ".agent-wayfinder/release-readiness/unknowns/U*.md"
            )
            any_review = behavior.Assertion(
                kind="glob_any_contains",
                path=pattern,
                value="full-team review",
            )
            none_cost = behavior.Assertion(
                kind="glob_none_contains",
                path=pattern,
                value="precise cost model",
            )
            self.assertTrue(behavior.evaluate_assertion(evidence, any_review).passed)
            self.assertTrue(behavior.evaluate_assertion(evidence, none_cost).passed)

            empty_pattern = behavior.PurePosixPath("missing/U*.md")
            no_matches = behavior.Assertion(
                kind="glob_none_contains",
                path=empty_pattern,
                value="anything",
            )
            any_missing = behavior.Assertion(
                kind="glob_any_contains",
                path=empty_pattern,
                value="anything",
            )
            self.assertTrue(behavior.evaluate_assertion(evidence, no_matches).passed)
            self.assertFalse(behavior.evaluate_assertion(evidence, any_missing).passed)

            (unknowns / "U11-cost.md").write_text(
                "# U11: What is the precise cost model?\n",
                encoding="utf-8",
            )
            evidence_with_incidental = behavior.RunEvidence(
                scenario=evidence.scenario,
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
            self.assertFalse(
                behavior.evaluate_assertion(evidence_with_incidental, none_cost).passed
            )

    def test_fixture_copy_is_disposable_and_resettable(self) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "simple-bounded-task"
        )
        source = behavior.snapshot(behavior.FIXTURE_ROOT / scenario.fixture)
        with (
            tempfile.TemporaryDirectory() as first,
            tempfile.TemporaryDirectory() as second,
        ):
            workspace_one = behavior.copy_fixture(scenario, Path(first))
            (workspace_one / "app.py").write_text(
                "changed disposable bytes\n", encoding="utf-8"
            )
            workspace_two = behavior.copy_fixture(scenario, Path(second))
            self.assertEqual(behavior.snapshot(workspace_two), source)
        self.assertEqual(
            behavior.snapshot(behavior.FIXTURE_ROOT / scenario.fixture), source
        )

    def test_state_preservation_oracle_detects_destructive_change(self) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "existing-wayfinder-state"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            install = behavior.run_adopt("install", workspace)
            self.assertEqual(install.returncode, 0, install.stderr)
            before = behavior.snapshot(workspace)
            target = (
                workspace
                / ".agent-wayfinder/response-serialization/unknowns/"
                "U1-name-telemetry-metric.md"
            )
            target.write_text("destructive replacement\n", encoding="utf-8")
            (workspace / "AGENTS.md").write_text(
                "unauthorized policy replacement\n", encoding="utf-8"
            )
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
            "verification-failure",
            "wayfinder-fact-conflict",
            "wayfinder-contract-smoke",
            "wayfinder-unrelated",
        }
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            scenarios = {
                scenario.fixture: scenario for scenario in behavior.load_scenarios()
            }
            for name in sorted(fixture_names):
                with self.subTest(fixture=name):
                    workspace = behavior.copy_fixture(scenarios[name], temporary_root)
                    result = subprocess.run(
                        [behavior.sys.executable, "verify.py"],
                        cwd=workspace,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(
                        result.returncode, 1, result.stdout + result.stderr
                    )
                    verification_path = (
                        workspace / ".behavior-evidence/verification.jsonl"
                    )
                    self.assertTrue(
                        verification_path.is_file(),
                        f"{name} verifier did not emit observable evidence",
                    )
                    events = [
                        json.loads(line)
                        for line in verification_path.read_text(
                            encoding="utf-8"
                        ).splitlines()
                        if line.strip()
                    ]
                    self.assertEqual(
                        events,
                        [{"command": "python verify.py", "exit_code": 1}],
                    )


if __name__ == "__main__":
    unittest.main()
