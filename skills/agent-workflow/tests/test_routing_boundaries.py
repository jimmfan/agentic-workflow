from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from _behavior_test_support import behavior


class RoutingBoundaryTests(unittest.TestCase):
    def scenario(self, identifier: str) -> behavior.Scenario:
        return next(item for item in behavior.load_scenarios() if item.id == identifier)

    def failures(self, evidence: behavior.RunEvidence) -> list[str]:
        return [item.name for item in behavior.evaluate(evidence) if not item.passed]

    def test_response_patterns_are_validated_and_hidden_from_the_agent(self) -> None:
        scenario = self.scenario("arc-runner-rename-plan")
        source = scenario.source.read_text()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / scenario.source.name
            path.write_text(
                source.replace("response_must_match = [", 'response_must_match = ["[",')
            )
            with self.assertRaisesRegex(behavior.BehaviorError, "response_must_match"):
                behavior.load_scenario(path)
        prompt = behavior.build_prompt(
            replace(scenario, response_must_match=("HIDDEN-RESPONSE-ORACLE",))
        )
        self.assertNotIn("HIDDEN-RESPONSE-ORACLE", prompt)

    def test_migration_route_marker_needs_one_map_and_preserved_configuration(
        self,
    ) -> None:
        for identifier in (
            "arc-managed-identity-coordination",
            "arc-approved-migration-coordination",
        ):
            with (
                self.subTest(scenario=identifier),
                tempfile.TemporaryDirectory() as temporary,
            ):
                scenario = self.scenario(identifier)
                workspace = behavior.copy_fixture(scenario, Path(temporary))
                before = behavior.snapshot(workspace)
                evidence = behavior.RunEvidence(
                    scenario=scenario,
                    workspace=workspace,
                    before=before,
                    after=before,
                    stdout="[route: router → wayfinder]",
                    stderr="",
                    returncode=0,
                    report={"status": "success"},
                    verification=(),
                    route_components=("wayfinder",),
                )
                count_check = "assert:.agent-wayfinder/*/map.md:glob-count"
                self.assertIn(count_check, self.failures(evidence))
                for effort in ("first", "second"):
                    path = workspace / f".agent-wayfinder/{effort}/map.md"
                    path.parent.mkdir(parents=True)
                    path.write_text("# Migration\n")
                (workspace / "part-03-arc-runners/values.yaml").write_text(
                    "# deployed migration\n"
                )
                failures = self.failures(
                    replace(evidence, after=behavior.snapshot(workspace))
                )
                self.assertIn(count_check, failures)
                self.assertIn("expect:project_state_preserved", failures)

    def check_migration_maps(
        self, identifier: str, cases: dict[str, tuple[str, bool]]
    ) -> None:
        scenario = self.scenario(identifier)
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            map_path = workspace / ".agent-wayfinder/arc-migration/map.md"
            map_path.parent.mkdir(parents=True)
            for label, (content, expected) in cases.items():
                with self.subTest(case=label):
                    map_path.write_text(content)
                    evidence = behavior.RunEvidence(
                        scenario=scenario,
                        workspace=workspace,
                        before=before,
                        after=behavior.snapshot(workspace),
                        stdout="[route: router → wayfinder]",
                        stderr="",
                        returncode=0,
                        report={"status": "success"},
                        verification=(),
                        route_components=("wayfinder",),
                    )
                    failures = self.failures(evidence)
                    self.assertEqual(not failures, expected, failures)

    def test_unresolved_migration_accepts_map_only_but_rejects_false_readiness(
        self,
    ) -> None:
        content = (
            "# ARC managed identity migration\n"
            "Objective: migrate part-03-arc-runners to managed identity without downtime.\n"
            "Scope: ARC runner configuration and workload permissions; no live changes.\n"
            "Areas: runner jobs depend on identity permissions; Security approval gates rollout.\n"
            "Rollout ordering is unresolved. Rollback boundaries remain undecided.\n"
            "Security approval is pending for workload permissions.\n"
            "Ready work: inventory runner jobs and their permission references.\n"
        )
        self.check_migration_maps(
            "arc-managed-identity-coordination",
            {
                "map-only": (content, True),
                "empty-map": ("# ARC migration\n", False),
                "lost-rollout": (
                    content.replace("Rollout ordering is unresolved.", ""),
                    False,
                ),
                "lost-rollback": (
                    content.replace("Rollback boundaries remain undecided.", ""),
                    False,
                ),
                "invented-security-approval": (
                    content.replace(
                        "Security approval is pending", "Security approval is complete"
                    ),
                    False,
                ),
                "contradictory-readiness": (
                    "Inventory work is blocked until Security approves.\n" + content,
                    False,
                ),
            },
        )

    def test_known_migration_accepts_map_only_and_security_question_but_not_reopened_choices(
        self,
    ) -> None:
        content = (
            "# ARC managed identity migration\n"
            "Objective: migrate part-03-arc-runners to managed identity without downtime.\n"
            "Scope: runner configuration and workload permissions; no live changes.\n"
            "Areas: runner jobs depend on identity permissions; Security approval gates rollout.\n"
            "The approved migration in docs/migration.md settles identity, rollout, and rollback.\n"
            "Security approval is pending next week for workload permissions.\n"
            "Ready work: inventory runner jobs and their permission references.\n"
        )
        identifier = "arc-approved-migration-coordination"
        self.check_migration_maps(
            identifier,
            {
                "map-only": (content, True),
                "contradicted-current-state": (
                    "Identity mechanism is unresolved.\n" + content,
                    False,
                ),
                "contradicted-rollout": (
                    "Rollout ordering remains undecided.\n" + content,
                    False,
                ),
                "lost-source": (
                    content.replace("docs/migration.md", "some plan"),
                    False,
                ),
            },
        )
        scenario = self.scenario(identifier)
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            effort = workspace / ".agent-wayfinder/arc-migration"
            effort.mkdir(parents=True)
            (effort / "map.md").write_text(content)
            unknown = effort / "unknowns/U1-review.md"
            unknown.parent.mkdir()
            for question, expected in (
                (
                    "# U1: What identity permissions must Security approve?\n"
                    "The identity mechanism, rollout, and rollback remain settled.\n",
                    True,
                ),
                (
                    "# U1: What permissions must Security approve for workload identity?\n",
                    True,
                ),
                (
                    "# U1: What Security approval is needed before rollout?\n",
                    True,
                ),
                (
                    "# U1: When will Security approve workload permissions?\nThe approved identity mechanism and rollout are in docs/migration.md.\n",
                    True,
                ),
                ("# U1: Which identity mechanism should we choose?\n", False),
                ("# U1: What rollout ordering should we use?\n", False),
                ("# U1: Which rollback approach should we choose?\n", False),
            ):
                with self.subTest(question=question):
                    unknown.write_text(question)
                    evidence = behavior.RunEvidence(
                        scenario=scenario,
                        workspace=workspace,
                        before=before,
                        after=behavior.snapshot(workspace),
                        stdout="[route: router → wayfinder]",
                        stderr="",
                        returncode=0,
                        report={"status": "success"},
                        verification=(),
                        route_components=("wayfinder",),
                    )
                    self.assertEqual(
                        not self.failures(evidence), expected, self.failures(evidence)
                    )

    def test_clear_objective_accepts_completion_on_other_minimum_routes(self) -> None:
        scenario = self.scenario("objective-clear-request")
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            (workspace / "app.py").write_text(
                'def greeting():\n    return "hello, world!"\n'
            )
            completed = subprocess.run(
                [sys.executable, "verify.py"], cwd=workspace, capture_output=True
            )
            self.assertEqual(completed.returncode, 0)
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=behavior.snapshot(workspace),
                stdout="Updated greeting and verified it.\n[route: router → implement → verification]",
                stderr="",
                returncode=0,
                report={"status": "success"},
                verification=behavior.load_verification(
                    workspace / behavior.VERIFICATION_LOG
                ),
                route_components=("implement", "verification"),
            )
            self.assertEqual(self.failures(evidence), [])
            self.assertIn(
                "expect:verification_performed",
                self.failures(replace(evidence, verification=())),
            )
            self.assertIn(
                "route-marker:prohibited-components",
                self.failures(
                    replace(
                        evidence,
                        stdout="[route: router → wayfinder → implement]",
                        route_components=("wayfinder", "implement"),
                    )
                ),
            )

    def test_bounded_plan_requires_a_plan_and_allows_project_plan_artifacts(
        self,
    ) -> None:
        scenario = self.scenario("arc-runner-rename-plan")
        response = (
            "1. Rename runnerScaleSetName in part-03-arc-runners/values.yaml "
            "from arc-runner-set to arc-runner-set-local.\n"
            "2. Update the matching runs-on reference in README.md.\n"
            "3. Run python part-03-arc-runners/verify.py to check the local configuration.\n"
            "[route: router → direct]"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=before,
                stdout=response,
                stderr="",
                returncode=0,
                report={"status": "success"},
                verification=(),
                route_components=("direct",),
            )
            self.assertEqual(self.failures(evidence), [])
            for missing in (
                "values.yaml",
                "README.md",
                "verify.py",
                "arc-runner-set-local",
            ):
                with self.subTest(missing=missing):
                    self.assertTrue(
                        self.failures(
                            replace(
                                evidence, stdout=response.replace(missing, "omitted")
                            )
                        )
                    )
            multiline = (
                "1. In part-03-arc-runners/values.yaml:\n"
                "   Change runnerScaleSetName from arc-runner-set to arc-runner-set-local.\n\n"
                "2. In README.md:\n"
                "   Update the documented runs-on reference.\n\n"
                "3. For verification:\n"
                "   Run python part-03-arc-runners/verify.py.\n"
                "[route: router → direct]"
            )
            self.assertEqual(self.failures(replace(evidence, stdout=multiline)), [])
            self.assertEqual(
                self.failures(
                    replace(
                        evidence,
                        stdout=response.replace("→ direct", "→ to-spec"),
                        route_components=("to-spec",),
                    )
                ),
                [],
            )
            self.assertTrue(
                self.failures(replace(evidence, stdout="[route: router → direct]"))
            )
            (workspace / "docs").mkdir()
            (workspace / "docs/plan.md").write_text(response)
            self.assertEqual(
                self.failures(replace(evidence, after=behavior.snapshot(workspace))), []
            )
            (workspace / ".agent-wayfinder/rename").mkdir(parents=True)
            (workspace / ".agent-wayfinder/rename/map.md").write_text(response)
            self.assertTrue(
                self.failures(replace(evidence, after=behavior.snapshot(workspace)))
            )


if __name__ == "__main__":
    unittest.main()
