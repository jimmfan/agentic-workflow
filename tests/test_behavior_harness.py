from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest

from _behavior_test_support import behavior


class BehaviorHarnessTests(unittest.TestCase):
    def test_public_report_prompt_omits_retired_provider_selection_field(self) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "simple-bounded-task"
        )

        prompt = behavior.build_prompt(scenario)

        self.assertNotIn('"providers_selected"', prompt)

    def test_blind_scenarios_hide_their_rubrics_and_use_non_descriptive_workspaces(
        self,
    ) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}

        for scenario_id in (
            "wayfinder-domain-modeling-discovery",
            "wayfinder-cross-system-fact-boundary",
            "wayfinder-human-authority-clarification",
            "wayfinder-selective-unknown-promotion",
            "wayfinder-accepted-residual-uncertainty",
            "wayfinder-state-cannot-grant-authority",
            "wayfinder-unordered-dependencies-no-critical-path",
        ):
            scenario = scenarios[scenario_id]
            prompt = behavior.build_prompt(scenario)
            with self.subTest(scenario=scenario_id):
                self.assertTrue(scenario.blind_grading)
                self.assertTrue(scenario.assertions)
                for hidden in (
                    *scenario.expect,
                    *scenario.must_not,
                    *scenario.report_must_include,
                ):
                    self.assertNotIn(hidden, prompt)
                if scenario.verification_command:
                    self.assertNotIn(scenario.verification_command, prompt)
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
        self.assertTrue(all(result.passed is not False for result in results), results)
        self.assertEqual(behavior.verdict(results), "INCONCLUSIVE")

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

    def test_route_contract_can_require_and_exclude_components(self) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "architectural-choice-uses-discovery"
        )
        self.assertEqual(scenario.route_must_include, ("discovery",))
        self.assertEqual(
            scenario.route_must_not_include,
            ("domain-modeling", "wayfinder"),
        )

        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            snapshot = behavior.snapshot(workspace)
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=snapshot,
                after=snapshot,
                stdout="[route: router → direct]",
                stderr="",
                returncode=0,
                report={"status": "success", "summary": "read-only comparison"},
                verification=(),
                route_components=("direct",),
            )
            required_result = next(
                item
                for item in behavior.evaluate(evidence)
                if item.name == "route-marker:required-components"
            )
            prohibited_evidence = replace(
                evidence,
                stdout="[route: router → discovery → domain-modeling]",
                route_components=("discovery", "domain-modeling"),
            )
            prohibited_result = next(
                item
                for item in behavior.evaluate(prohibited_evidence)
                if item.name == "route-marker:prohibited-components"
            )
        self.assertFalse(required_result.passed)
        self.assertIn("discovery", required_result.detail)
        self.assertFalse(prohibited_result.passed)
        self.assertIn("domain-modeling", prohibited_result.detail)

    def test_implicit_routing_prompts_hide_classification(self) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        for name in (
            "objective-clear-request",
            "arc-runner-rename-plan",
            "arc-managed-identity-coordination",
            "arc-approved-migration-coordination",
            "simple-bounded-task",
            "wayfinder-new-effort",
            "wayfinder-ambiguous-new-objective",
            "wayfinder-scope-refinement",
            "architectural-choice-uses-discovery",
            "discovery-composes-research",
        ):
            with self.subTest(scenario=name):
                scenario = scenarios[name]
                prompt = behavior.build_prompt(scenario)
                self.assertTrue(scenario.blind_grading)
                for hidden in (
                    scenario.name,
                    scenario.verification_command,
                    *scenario.expect,
                    *scenario.must_not,
                    *(str(path) for path in scenario.state_must_include),
                    *(str(path) for path in scenario.state_must_not_include),
                ):
                    if hidden:
                        self.assertNotIn(hidden, prompt)
                with tempfile.TemporaryDirectory() as temporary:
                    workspace = behavior.copy_fixture(scenario, Path(temporary))
                    self.assertNotIn(scenario.id, workspace.name)
                    self.assertNotIn(scenario.fixture, workspace.name)

    def test_scope_refinement_forbids_unrelated_product_artifacts(self) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "wayfinder-scope-refinement"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            map_path = workspace / ".project-efforts/policy-execution-migration/map.md"
            map_path.write_text(
                map_path.read_text(encoding="utf-8") + "\nRefined boundary.\n",
                encoding="utf-8",
            )
            evidence_root = workspace / ".behavior-evidence"
            evidence_root.mkdir()
            (evidence_root / "report.json").write_text("{}\n", encoding="utf-8")

            evidence_args = {
                "scenario": scenario,
                "workspace": workspace,
                "before": before,
                "stdout": "[route: router → wayfinder]",
                "stderr": "",
                "returncode": 0,
                "report": {"status": "success"},
                "verification": (),
                "route_components": ("wayfinder",),
            }
            allowed = behavior.RunEvidence(
                after=behavior.snapshot(workspace),
                **evidence_args,
            )
            allowed_result = next(
                item
                for item in behavior.evaluate(allowed)
                if item.name == "must-not:unnecessary_planning_artifacts"
            )
            self.assertTrue(allowed_result.passed, allowed_result.detail)

            (workspace / "unrelated-notes.md").write_text(
                "unrelated\n", encoding="utf-8"
            )
            unrelated = behavior.RunEvidence(
                after=behavior.snapshot(workspace),
                **evidence_args,
            )
            unrelated_result = next(
                item
                for item in behavior.evaluate(unrelated)
                if item.name == "must-not:unnecessary_planning_artifacts"
            )
            self.assertFalse(unrelated_result.passed)
            self.assertIn("unrelated-notes.md", unrelated_result.detail)

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

    def test_success_source_path_and_route_claims_cannot_replace_a_verified_change(
        self,
    ):
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "simple-bounded-task"
        )
        agent_source = """
import json
from pathlib import Path
Path('.behavior-evidence/report.json').write_text(json.dumps({'schema_version': 1, 'status': 'success', 'research_sources': ['https://www.python.org/'], 'state_used': ['README.md'], 'verification': [{'exit_code': 0}]}))
Path('.behavior-evidence/verification.jsonl').write_text(json.dumps({'exit_code': 0}) + '\\n')
print('Success. I read the source, researched it and verified the change. [route: router → direct]')
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            agent = root / "claims.py"
            agent.write_text(agent_source)
            evidence, results = behavior.run_live_scenario(
                scenario, [behavior.sys.executable, str(agent)], root, 30
            )
            self.assertEqual(behavior.verdict(results), "FAIL")
            self.assertNotEqual(evidence.outcome_verification["exit_code"], 0)
            failures = {result.name for result in results if result.passed is False}
            self.assertIn("expect:meaningful_repository_change", failures)
            self.assertIn("verification:independent-outcome", failures)

    def test_forged_recovery_events_cannot_hide_an_incorrect_replacement(self):
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "verification-failure-recovery"
        )
        agent_source = """
import json
from pathlib import Path
Path('slug.py').write_text('def slugify(value): return "incorrect"\\n')
Path('.behavior-evidence/report.json').write_text(json.dumps({'schema_version': 1, 'status': 'success', 'verification': [{'exit_code': 1}, {'exit_code': 0}]}))
Path('.behavior-evidence/verification.jsonl').write_text(''.join(json.dumps({'exit_code': code}) + '\\n' for code in [1, 0]))
print('Fixed and verified. [route: router → direct]')
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            agent = root / "forged_recovery.py"
            agent.write_text(agent_source)
            evidence, results = behavior.run_live_scenario(
                scenario, [behavior.sys.executable, str(agent)], root, 30
            )
            self.assertEqual(behavior.verdict(results), "FAIL")
            self.assertNotEqual(evidence.outcome_verification["exit_code"], 0)
            self.assertIn(
                "verification:independent-outcome",
                {result.name for result in results if result.passed is False},
            )

    def test_unobserved_research_reads_and_decision_absence_are_inconclusive(self):
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "discovery-composes-research"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            scenario = replace(
                scenario,
                expect=("external_fact_researched", "existing_state_reused"),
                must_not=("silent_decision_invention",),
                assertions=(),
                response_must_match=(),
                state_must_include=(Path("docs/requirements.md"),),
            )
            evidence = behavior.RunEvidence(
                scenario,
                workspace,
                before,
                before,
                "[route: router → discovery → research]",
                "",
                0,
                {
                    "status": "success",
                    "research_sources": ["https://www.sqlite.org/"],
                    "state_used": ["docs/requirements.md"],
                },
                (),
                ("discovery", "research"),
            )
            results = behavior.evaluate(evidence)
            self.assertEqual(behavior.verdict(results), "INCONCLUSIVE")
            for name in (
                "expect:external_fact_researched",
                "expect:existing_state_reused",
                "state-loading:progressive",
                "must-not:silent_decision_invention",
            ):
                self.assertIsNone(
                    next(result.passed for result in results if result.name == name)
                )
            (workspace / "notes.md").write_text(
                "The project has decided to use SQLite without approval."
            )
            changed = replace(evidence, after=behavior.snapshot(workspace))
            self.assertIsNone(
                next(
                    result.passed
                    for result in behavior.evaluate(changed)
                    if result.name == "must-not:silent_decision_invention"
                )
            )

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
                "map-change-needs-semantic-adjudication",
                "wayfinder-human-authority-clarification",
                ".project-efforts/persistence/map.md",
                "expect:uncertainty_recorded_or_blocked",
                None,
            ),
            (
                "current-unknown-is-recorded-uncertainty",
                "wayfinder-human-authority-clarification",
                (
                    ".project-efforts/persistence/map.md",
                    ".project-efforts/persistence/unknowns.md",
                ),
                "expect:uncertainty_recorded_or_blocked",
                True,
            ),
            (
                "current-unknown-uses-recognized-state",
                "wayfinder-human-authority-clarification",
                (
                    ".project-efforts/persistence/map.md",
                    ".project-efforts/persistence/unknowns.md",
                ),
                "contract:recognized-wayfinder-changes",
                True,
            ),
            (
                "orphan-unknown-is-rejected",
                "wayfinder-human-authority-clarification",
                ".project-efforts/persistence/unknowns.md",
                "contract:recognized-wayfinder-changes",
                False,
            ),
            (
                "unrecognized-wayfinder-write-is-rejected",
                "wayfinder-human-authority-clarification",
                (
                    ".project-efforts/persistence/map.md",
                    ".project-efforts/persistence/notes/choice.md",
                ),
                "contract:recognized-wayfinder-changes",
                False,
            ),
            (
                "bare-unknown-is-not-recorded-uncertainty",
                "wayfinder-human-authority-clarification",
                ".project-efforts/persistence/unknowns/U1.md",
                "expect:uncertainty_recorded_or_blocked",
                False,
            ),
            (
                "empty-slug-is-not-recorded-uncertainty",
                "wayfinder-human-authority-clarification",
                ".project-efforts/persistence/unknowns/U1-.md",
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
                ".project-efforts/greeting/unknowns/U1-unneeded.md",
                "must-not:manufacture_uncertainty",
                False,
            ),
            (
                "malformed-unknown-still-manufactures-uncertainty",
                "simple-bounded-task",
                ".project-efforts/greeting/unknowns/U1.md",
                "must-not:manufacture_uncertainty",
                False,
            ),
            (
                "nested-unknown-artifact-still-manufactures-uncertainty",
                "simple-bounded-task",
                ".project-efforts/greeting/unknowns/nested/U1-unneeded.md",
                "must-not:manufacture_uncertainty",
                False,
            ),
            (
                "unchanged-does-not-invent-a-decision",
                "wayfinder-human-authority-clarification",
                None,
                "must-not:silent_decision_invention",
                None,
            ),
            (
                "created-wayfinder-decision-ledger-is-invention",
                "wayfinder-human-authority-clarification",
                ".project-efforts/persistence/decisions.md",
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
                    target.write_text(
                        "## U1 — Which backend?\n"
                        if target.name == "unknowns.md"
                        else "adversarial artifact\n",
                        encoding="utf-8",
                    )
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

    def test_ledger_semantic_assertions_accept_ids_and_reject_incidental_content(self):
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "wayfinder-cross-system-fact-boundary"
        )
        assertions = [
            item for item in scenario.assertions if item.path.name == "unknowns.md"
        ]
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            ledger = workspace / ".project-efforts/request-ordering/unknowns.md"
            ledger.parent.mkdir(parents=True)

            def check(content):
                ledger.write_text(content)
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
                return [
                    behavior.evaluate_assertion(evidence, item).passed
                    for item in assertions
                ]

            for number in (1, 7, 19):
                self.assertTrue(
                    all(
                        check(
                            f"## U{number} — Does the current project guarantee ordering?\n"
                        )
                    )
                )
                self.assertTrue(
                    all(
                        check(
                            f"## U{number} — Can our project rely on strict request order?\n"
                        )
                    )
                )
            self.assertFalse(all(check("## U7 — A different question?\n")))
            self.assertFalse(all(check("# Unknowns\n")))
            for bad in (
                "Current project ordering is discussed here.\n## U7 — Which logo?\n",
                "## U7 — Which logo?\n```markdown\nDoes the current project guarantee ordering?\n```\n",
                "## U7 — Which logo for the current project?\n## U8 — Does another system guarantee ordering?\n",
                "## U7 — Does the current project guarantee ordering?\n## U8 — Which logo?\n",
            ):
                with self.subTest(bad=bad):
                    self.assertFalse(all(check(bad)))

    def test_migrated_question_checks_bind_content_to_records(self):
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        cases = (
            (
                "wayfinder-domain-modeling-discovery",
                "zero-downtime-platform-cutover",
                "## U7 — What does Consumer mean in this context?\n",
                "Consumer context",
            ),
            (
                "wayfinder-fact-conflict",
                "deployment-mode",
                "## U1 — Which deployment mode applies?\n",
                "deployment mode",
            ),
            (
                "wayfinder-human-authority-clarification",
                "persistence-authority",
                "## U7 — Which durable backend and operating owner?\n",
                "durable backend",
            ),
            (
                "wayfinder-accepted-residual-uncertainty",
                "pilot-capacity",
                "## U1 — What peak concurrency must be supported?\nCapacity remains unresolved.\n",
                "Capacity remains unresolved",
            ),
            (
                "wayfinder-selective-unknown-promotion",
                "release-readiness",
                "## U7 — Has the full-team review occurred?\n",
                "review",
            ),
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            for name, effort, good, preamble in cases:
                with self.subTest(scenario=name):
                    scenario = scenarios[name]
                    assertions = [
                        a for a in scenario.assertions if a.path.name == "unknowns.md"
                    ]
                    ledger = workspace / f".project-efforts/{effort}/unknowns.md"
                    ledger.parent.mkdir(parents=True)

                    def check(content):
                        ledger.write_text(content)
                        evidence = behavior.RunEvidence(
                            scenario,
                            workspace,
                            {},
                            behavior.snapshot(workspace),
                            "",
                            "",
                            0,
                            {},
                            (),
                            (),
                        )
                        return all(
                            behavior.evaluate_assertion(evidence, a).passed
                            for a in assertions
                        )

                    self.assertTrue(check(good))
                    for bad in (
                        f"{preamble}\n## U7 — Which logo?\n",
                        f"## U7 — Which logo?\n~~~\n{good}\n~~~\n",
                    ):
                        with self.subTest(bad=bad):
                            self.assertFalse(check(bad))
                    if name in {
                        "wayfinder-fact-conflict",
                        "wayfinder-accepted-residual-uncertainty",
                    }:
                        self.assertFalse(check(good.replace("U1", "U8")))
                        self.assertFalse(
                            check("## U1 — Which logo?\n" + good.replace("U1", "U8"))
                        )
                    elif name == "wayfinder-human-authority-clarification":
                        self.assertTrue(
                            check(
                                good
                                + "## U8 — Who owns encryption keys?\n## U9 — Which retention policy applies?\n"
                            )
                        )
                    elif name == "wayfinder-selective-unknown-promotion":
                        self.assertTrue(
                            check(good + "## U8 — Who approves pilot access?\n")
                        )
                        self.assertFalse(
                            check(
                                good
                                + "## U8 — What precise cost model should we use?\n"
                            )
                        )
                    ledger.unlink()

    def test_section_assertion_schema_validates_expression_and_optional_identity(self):
        base = {
            "kind": "section_any_matches",
            "path": ".project-efforts/example/unknowns.md",
            "value": "capacity",
            "record": "U1",
        }
        self.assertEqual(behavior.load_assertions([base], "control")[0].record, "U1")
        for changes in (
            {"record": "U0"},
            {"record": "F1"},
            {"record": 1},
            {"value": "["},
            {"kind": "path_exists"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(behavior.BehaviorError):
                    behavior.load_assertions([{**base, **changes}], "control")

    def test_accepted_capacity_identity_cannot_be_supplied_by_another_effort(self):
        scenario = next(
            s
            for s in behavior.load_scenarios()
            if s.id == "wayfinder-accepted-residual-uncertainty"
        )
        assertion = next(a for a in scenario.assertions if a.record == "U1")
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            for effort, state in (
                ("pilot-capacity", "resolved"),
                ("other-pilot", "unresolved"),
            ):
                ledger = workspace / f".project-efforts/{effort}/unknowns.md"
                ledger.parent.mkdir(parents=True)
                ledger.write_text(
                    f"## U1 — What capacity is required?\nCapacity remains {state}.\n"
                )
            evidence = behavior.RunEvidence(
                scenario,
                workspace,
                {},
                behavior.snapshot(workspace),
                "",
                "",
                0,
                {},
                (),
                (),
            )
            self.assertFalse(behavior.evaluate_assertion(evidence, assertion).passed)

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
            install = behavior.run_lifecycle("install", workspace)
            self.assertEqual(install.returncode, 0, install.stderr)
            before = behavior.snapshot(workspace)
            target = workspace / ".project-efforts/response-serialization/unknowns.md"
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
