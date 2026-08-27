from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest

TEST_ROOT = Path(__file__).resolve().parent


def load_behavior():
    path = TEST_ROOT / "behavior.py"
    spec = importlib.util.spec_from_file_location("agent_workflow_behavior", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


behavior = load_behavior()


class BehaviorContractTests(unittest.TestCase):
    def test_implementation_reentry_uses_current_map_and_preserves_unknown_content(
        self,
    ) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        scenario = scenarios["existing-actionable-work"]
        preserved = {path.as_posix() for path in scenario.preserve_paths}
        state_used = {path.as_posix() for path in scenario.state_must_include}
        state_not_used = {
            path.as_posix() for path in scenario.state_must_not_include
        }
        unknown_note = ".agent-wayfinder/unrecognized-project-data/note.txt"

        self.assertIn(unknown_note, preserved)
        self.assertIn(unknown_note, state_not_used)
        self.assertNotIn(unknown_note, state_used)
        self.assertIn(".agent-wayfinder/discount-bounds/map.md", state_used)
        self.assertIn("docs/decisions/0001-discount-bounds.md", state_used)

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
            }
            <= live_ids
        )

    def test_blind_scenarios_hide_their_rubrics_and_use_opaque_workspaces(
        self,
    ) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}

        blind_judgments = {
            "wayfinder-domain-modeling-discovery": (
                "preferred specialist",
                "zero-downtime platform cutover",
            ),
            "wayfinder-domain-modeling-reorganizes-territory": (
                "Domain Modeling",
                "Policy intake",
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

    def test_accepted_residual_relationship_assertions_distinguish_the_boundary(
        self,
    ) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        accepted = scenarios["wayfinder-accepted-residual-uncertainty"]
        accepted_relationships = [
            item
            for item in accepted.assertions
            if item.kind in {"glob_any_matches", "glob_none_matches"}
        ]
        self.assertEqual(len(accepted_relationships), 4)

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

    def test_answered_authority_scenario_requires_reconciliation_and_retirement(
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

    def test_scenarios_reject_unknown_behavior_vocabulary(self) -> None:
        source = (behavior.SCENARIO_ROOT / "simple-bounded-task.toml").read_text(
            encoding="utf-8"
        )
        invalid = source.replace(
            '"task_completed"', '"implementation_route_exactly"', 1
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "simple-bounded-task.toml"
            path.write_text(invalid, encoding="utf-8")
            with self.assertRaisesRegex(behavior.BehaviorError, "unknown expectations"):
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
            if item.id == "meaningful-implementation"
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
                "genuine-unresolved-decision",
                None,
                "expect:uncertainty_recorded_or_blocked",
                False,
            ),
            (
                "map-change-is-not-recorded-uncertainty",
                "genuine-unresolved-decision",
                ".agent-wayfinder/persistence/map.md",
                "expect:uncertainty_recorded_or_blocked",
                False,
            ),
            (
                "current-unknown-is-recorded-uncertainty",
                "genuine-unresolved-decision",
                (
                    ".agent-wayfinder/persistence/map.md",
                    ".agent-wayfinder/persistence/unknowns/U1-backend.md",
                ),
                "expect:uncertainty_recorded_or_blocked",
                True,
            ),
            (
                "current-unknown-uses-recognized-state",
                "genuine-unresolved-decision",
                (
                    ".agent-wayfinder/persistence/map.md",
                    ".agent-wayfinder/persistence/unknowns/U1-backend.md",
                ),
                "contract:recognized-wayfinder-mutations",
                True,
            ),
            (
                "orphan-unknown-is-rejected",
                "genuine-unresolved-decision",
                ".agent-wayfinder/persistence/unknowns/U1-backend.md",
                "contract:recognized-wayfinder-mutations",
                False,
            ),
            (
                "unrecognized-wayfinder-write-is-rejected",
                "genuine-unresolved-decision",
                (
                    ".agent-wayfinder/persistence/map.md",
                    ".agent-wayfinder/persistence/notes/choice.md",
                ),
                "contract:recognized-wayfinder-mutations",
                False,
            ),
            (
                "bare-unknown-is-not-recorded-uncertainty",
                "genuine-unresolved-decision",
                ".agent-wayfinder/persistence/unknowns/U1.md",
                "expect:uncertainty_recorded_or_blocked",
                False,
            ),
            (
                "empty-slug-is-not-recorded-uncertainty",
                "genuine-unresolved-decision",
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
                "genuine-unresolved-decision",
                None,
                "must-not:silent_decision_invention",
                True,
            ),
            (
                "created-wayfinder-decision-ledger-is-invention",
                "genuine-unresolved-decision",
                ".agent-wayfinder/persistence/decisions.md",
                "must-not:silent_decision_invention",
                False,
            ),
            (
                "created-project-decision-is-invention",
                "genuine-unresolved-decision",
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

    def test_default_wayfinder_fixtures_use_ledgers_and_exact_section_anchors(
        self,
    ) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        existing = scenarios["existing-wayfinder-state"]
        decision_path = behavior.PurePosixPath(
            ".agent-wayfinder/response-serialization/decisions.md"
        )
        self.assertIn(decision_path, existing.state_must_include)

        fixture = behavior.FIXTURE_ROOT / existing.fixture
        decisions = (fixture / decision_path.as_posix()).read_text(encoding="utf-8")
        mapping = (
            fixture / ".agent-wayfinder/response-serialization/map.md"
        ).read_text(encoding="utf-8")
        self.assertTrue(decisions.startswith("# Decisions\n\n"))
        self.assertIn("## D1 — Use compact sorted JSON", decisions)
        self.assertIn(
            "decisions.md#d1--use-compact-sorted-json",
            mapping,
        )

        expected_output_paths = {
            "wayfinder-contract-smoke": behavior.PurePosixPath(
                ".agent-wayfinder/runtime-rollout/facts.md"
            ),
            "wayfinder-new-effort": behavior.PurePosixPath(
                ".agent-wayfinder/platform-migration/decisions.md"
            ),
        }
        for scenario_id, output_path in expected_output_paths.items():
            with self.subTest(scenario=scenario_id):
                assertions = scenarios[scenario_id].assertions
                self.assertTrue(
                    any(
                        item.path == output_path and item.kind == "path_exists"
                        for item in assertions
                    )
                )
                self.assertTrue(
                    any(
                        item.path.name == "map.md"
                        and item.kind == "path_contains"
                        and item.value is not None
                        and f"{output_path.name}#" in item.value
                        for item in assertions
                    )
                )

    def test_negative_knowledge_contracts_cover_root_ledgers(self) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        prohibited_ledgers = {
            "genuine-unresolved-decision": (
                ".agent-wayfinder/persistence/decisions.md",
            ),
            "wayfinder-contract-smoke": (
                ".agent-wayfinder/runtime-rollout/decisions.md",
            ),
            "wayfinder-domain-modeling-discovery": (
                ".agent-wayfinder/zero-downtime-platform-cutover/decisions.md",
            ),
            "wayfinder-domain-modeling-reorganizes-territory": (
                ".agent-wayfinder/policy-execution-migration/facts.md",
                ".agent-wayfinder/policy-execution-migration/decisions.md",
            ),
            "wayfinder-human-authority-clarification": (
                ".agent-wayfinder/persistence-authority/decisions.md",
            ),
            "wayfinder-selective-unknown-promotion": (
                ".agent-wayfinder/arc-platform-delivery/decisions.md",
            ),
            "wayfinder-state-cannot-grant-authority": (
                ".agent-wayfinder/api-authentication/decisions.md",
            ),
        }
        for scenario_id, ledgers in prohibited_ledgers.items():
            for ledger in ledgers:
                with self.subTest(scenario=scenario_id, ledger=ledger):
                    self.assertTrue(
                        behavior.path_matches_any(
                            ledger,
                            scenarios[scenario_id].forbid_created_globs,
                        ),
                        ledger,
                    )

    def test_current_fixtures_use_fact_and_decision_ledgers(
        self,
    ) -> None:
        for fixture_name, effort_name in (
            ("wayfinder-fact-conflict", "deployment-mode"),
            ("wayfinder-reference-settlement", "provider-state"),
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
            unknowns = workspace / ".agent-wayfinder/arc/unknowns"
            unknowns.mkdir(parents=True)
            (unknowns / "U7-review.md").write_text(
                "# U7: Has the ADR completed full-team review?\n",
                encoding="utf-8",
            )
            (unknowns / "U9-firewall.md").write_text(
                "# U9: Which destinations have firewall approval?\n",
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
            pattern = behavior.PurePosixPath(".agent-wayfinder/arc/unknowns/U*.md")
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


if __name__ == "__main__":
    unittest.main()
