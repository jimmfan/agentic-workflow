"""Check authored grading constraints against observable fixture outcomes.

These controls exercise the grader, not live skill execution or prose equivalence.
"""

from pathlib import Path
import shutil
import tempfile
import unittest

from _behavior_test_support import behavior


class ScenarioConstraintTests(unittest.TestCase):
    def scenario(self, identifier):
        return behavior.load_scenario(behavior.SCENARIO_ROOT / f"{identifier}.toml")

    def checks(self, scenario, workspace, before):
        return {
            check.name: check.passed
            for check in behavior.evaluate(
                behavior.RunEvidence(
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
            )
        }

    def test_authored_path_constraints_have_an_active_check(self):
        for scenario in behavior.load_scenarios():
            with self.subTest(scenario=scenario.id):
                if scenario.preserve_paths:
                    self.assertTrue(
                        "project_state_preserved" in scenario.expect
                        or {
                            "overwrite_project_owned_state",
                            "repeat_resolved_discovery",
                        }
                        & set(scenario.must_not),
                        "preserve_paths has no active preservation check",
                    )
                if scenario.forbid_created_globs:
                    self.assertTrue(
                        {
                            "unnecessary_planning_artifacts",
                            "full_discovery_for_lookup",
                            "repeat_resolved_discovery",
                        }
                        & set(scenario.must_not),
                        "forbid_created_globs has no active forbidden-path check",
                    )

    def test_preservation_accepts_unchanged_sources_and_rejects_source_edits(self):
        for identifier, protected in (
            ("audit-integration", "orders.py"),
            ("audit-spec", "design.md"),
            ("audit-trivial-fix", "check.py"),
            ("verification-failure-recovery", "README.md"),
        ):
            with (
                self.subTest(scenario=identifier),
                tempfile.TemporaryDirectory() as temp,
            ):
                scenario = self.scenario(identifier)
                workspace = Path(temp) / "consumer"
                shutil.copytree(behavior.FIXTURE_ROOT / scenario.fixture, workspace)
                before = behavior.snapshot(workspace)
                self.assertIs(
                    self.checks(scenario, workspace, before).get(
                        "expect:project_state_preserved"
                    ),
                    True,
                )
                target = workspace / protected
                target.write_text(target.read_text() + "\nUnauthorized change.\n")
                self.assertIs(
                    self.checks(scenario, workspace, before).get(
                        "expect:project_state_preserved"
                    ),
                    False,
                )

    def test_forbidden_tickets_do_not_prohibit_an_authorized_map(self):
        scenario = self.scenario("wayfinder-map-authoring")
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "consumer"
            shutil.copytree(behavior.FIXTURE_ROOT / scenario.fixture, workspace)
            before = behavior.snapshot(workspace)
            mapping = workspace / ".project-efforts/consumer-handoff/map.md"
            mapping.parent.mkdir(parents=True)
            mapping.write_text("# Consumer handoff\n")
            name = "must-not:unnecessary_planning_artifacts"
            self.assertIs(self.checks(scenario, workspace, before).get(name), True)
            ticket = workspace / "tickets/01-unauthorized.md"
            ticket.parent.mkdir()
            ticket.write_text("Unauthorized implementation ticket.\n")
            self.assertIs(self.checks(scenario, workspace, before).get(name), False)

    def test_relevant_resumption_and_read_only_review_allow_wayfinder(self):
        for identifier in (
            "existing-wayfinder-state",
            "wayfinder-read-only-stale-state",
        ):
            with (
                self.subTest(scenario=identifier),
                tempfile.TemporaryDirectory() as temp,
            ):
                scenario = self.scenario(identifier)
                workspace = Path(temp) / "consumer"
                shutil.copytree(behavior.FIXTURE_ROOT / scenario.fixture, workspace)
                before = behavior.snapshot(workspace)
                self.assertIs(
                    self.checks(scenario, workspace, before)[
                        "route-marker:prohibited-components"
                    ],
                    True,
                )
                if identifier == "wayfinder-read-only-stale-state":
                    (workspace / "deployment.py").write_text("Unauthorized repair.\n")
                    self.assertIs(
                        self.checks(scenario, workspace, before)[
                            "expect:repository_unchanged"
                        ],
                        False,
                    )

    def test_requested_title_change_preserves_other_efforts(self):
        scenario = self.scenario("wayfinder-resume-synonymous-wording")
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "consumer"
            shutil.copytree(behavior.FIXTURE_ROOT / scenario.fixture, workspace)
            before = behavior.snapshot(workspace)
            target = workspace / ".project-efforts/wayfinder-runtime-projection/map.md"
            target.write_text(
                target.read_text().replace(
                    "# Wayfinder runtime projection",
                    "# First-party Wayfinder runtime",
                    1,
                )
            )
            self.assertIs(
                self.checks(scenario, workspace, before)[
                    "expect:project_state_preserved"
                ],
                True,
            )
            scope_check = (
                "assert:.project-efforts/wayfinder-runtime-projection/map.md:contains"
            )
            self.assertIs(self.checks(scenario, workspace, before)[scope_check], True)
            target.write_text(
                target.read_text().replace(
                    "Current-knowledge settlement and safe-retirement rules.", ""
                )
            )
            self.assertIs(self.checks(scenario, workspace, before)[scope_check], False)
            other = workspace / ".project-efforts/provider-runtime/map.md"
            other.write_text("# Overwritten unrelated effort\n")
            self.assertIs(
                self.checks(scenario, workspace, before)[
                    "expect:project_state_preserved"
                ],
                False,
            )


if __name__ == "__main__":
    unittest.main()
