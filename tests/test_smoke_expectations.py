"""Focused fixture-grader controls, not live Wayfinder compliance evidence.

These candidates distinguish required source/evidence relationships from
incidental Markdown layout. Critical-path examples exercise only the narrow
declaration forms checked by that scenario, not arbitrary prose semantics.
"""

from pathlib import Path
import tempfile
import unittest

from _behavior_test_support import behavior
from _test_support import run_script


class SmokeExpectationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.destination = Path(self.temporary.name)

    def scenario(self, identifier):
        return next(s for s in behavior.load_scenarios() if s.id == identifier)

    def assertion_failures(self, scenario, workspace):
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
            result
            for assertion in scenario.assertions
            if not (result := behavior.evaluate_assertion(evidence, assertion)).passed
        ]

    def test_unordered_work_accepts_truthful_critical_path_limitations(self):
        scenario = self.scenario("wayfinder-unordered-dependencies-no-critical-path")
        workspace = behavior.copy_fixture(scenario, self.destination)
        mapping = workspace / ".project-efforts/sdk-onboarding/map.md"
        mapping.parent.mkdir(parents=True)
        for statement in (
            "No critical path can be inferred.",
            "A critical path cannot be inferred from this unordered work.",
            "The critical path is not established.",
            "Critical path: unknown because no execution order is recorded.",
        ):
            with self.subTest(statement=statement):
                mapping.write_text(
                    "# SDK onboarding\n\nThe guidance items are independent.\n"
                    + statement
                    + "\n"
                )
                self.assertEqual(self.assertion_failures(scenario, workspace), [])

    def test_unordered_work_rejects_representative_invented_critical_paths(self):
        scenario = self.scenario("wayfinder-unordered-dependencies-no-critical-path")
        workspace = behavior.copy_fixture(scenario, self.destination)
        mapping = workspace / ".project-efforts/sdk-onboarding/map.md"
        mapping.parent.mkdir(parents=True)
        for declaration in (
            "Critical path: terminology → installation example → troubleshooting.",
            "The critical path is terminology, then installation, then troubleshooting.",
            "No critical path is documented.\nThe critical path runs through installation.",
        ):
            with self.subTest(declaration=declaration):
                mapping.write_text(
                    "# SDK onboarding\n\nThe guidance items are independent.\n"
                    + declaration
                    + "\n"
                )
                self.assertTrue(self.assertion_failures(scenario, workspace))

    def completed_contract_fixture(self):
        scenario = self.scenario("wayfinder-contract-smoke")
        workspace = behavior.copy_fixture(scenario, self.destination)
        effort = workspace / ".project-efforts/runtime-rollout"
        (effort / "evidence").mkdir()
        evidence = effort / "evidence/E1-policy.md"
        evidence.write_text(
            "# E1 — Runtime policy\n\n"
            "Source: release-policy.txt\n"
            "Scope: current runtime rollout policy.\n\n"
            "## Observation\nminimum_supported=3.11\n\n"
            "Limitations: Policy declaration, not a live runtime check.\n"
        )
        facts = effort / "facts.md"
        facts.write_text(
            "## F1 — Python 3.11 is the minimum supported runtime\n\n"
            "The current runtime rollout policy sets this minimum.\n"
            "Derived from: E1\n"
        )
        mapping = effort / "map.md"
        mapping.write_text(
            "# Runtime rollout\n\n"
            "[Minimum runtime](facts.md#f1--python-311-is-the-minimum-supported-runtime)\n\n"
            "## Ready work\nTicket 01 is ready.\n"
            "[Approved tickets](../../docs/agents/runtime-rollout/issues/01.md)\n"
        )
        tickets = workspace / "docs/agents/runtime-rollout/issues"
        tickets.mkdir(parents=True)
        for number, blockers in ((1, "None"), (2, "01"), (3, "01, 02")):
            (tickets / f"{number:02}.md").write_text(
                f"# {number:02} — Approved slice\n\n**Blocked by:** {blockers}\n"
            )
        return scenario, workspace, evidence, facts, mapping

    def test_contract_accepts_required_records_without_incidental_layout(self):
        scenario, workspace, evidence, facts, mapping = (
            self.completed_contract_fixture()
        )
        for layout in ("plain", "bulleted", "linked-and-bold"):
            with self.subTest(layout=layout):
                if layout == "bulleted":
                    evidence.write_text(
                        evidence.read_text().replace("Source:", "- Source:")
                    )
                    facts.write_text("# Facts\n\n" + facts.read_text())
                    mapping.write_text(
                        mapping.read_text().replace("## Ready work", "## Next work")
                    )
                elif layout == "linked-and-bold":
                    evidence.write_text(
                        evidence.read_text().replace(
                            "- Source: release-policy.txt",
                            "**Source:** [Policy](../../../release-policy.txt)",
                        )
                    )
                    facts.write_text(
                        facts.read_text().replace(
                            "Derived from: E1",
                            "Derived from: [E1](evidence/E1-policy.md)",
                        )
                    )
                result = run_script(workspace / "verify.py", cwd=workspace)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(self.assertion_failures(scenario, workspace), [])

    def test_contract_rejects_missing_evidence_relationships_and_required_fields(self):
        scenario, workspace, evidence, facts, mapping = (
            self.completed_contract_fixture()
        )
        baseline = run_script(workspace / "verify.py", cwd=workspace)
        self.assertEqual(baseline.returncode, 0, baseline.stdout)
        self.assertEqual(self.assertion_failures(scenario, workspace), [])
        for path, before, after in (
            (evidence, "Source: release-policy.txt", "Source: unrelated.txt"),
            (evidence, "Scope: current runtime rollout policy.\n", ""),
            (evidence, "## Observation\n", ""),
            (evidence, "minimum_supported=3.11", "minimum_supported=3.10"),
            (
                evidence,
                "Limitations: Policy declaration, not a live runtime check.\n",
                "",
            ),
            (facts, "Derived from: E1", "Derived from: E2"),
            (
                mapping,
                "facts.md#f1--python-311-is-the-minimum-supported-runtime",
                "facts.md#f2",
            ),
        ):
            with self.subTest(removed=before):
                original = path.read_text()
                path.write_text(original.replace(before, after))
                result = run_script(workspace / "verify.py", cwd=workspace)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertTrue(self.assertion_failures(scenario, workspace))
                path.write_text(original)

    def test_contract_keeps_ticket_dependency_and_duplicate_state_protections(self):
        _, workspace, _, _, _ = self.completed_contract_fixture()
        baseline = run_script(workspace / "verify.py", cwd=workspace)
        self.assertEqual(baseline.returncode, 0, baseline.stdout)
        third = workspace / "docs/agents/runtime-rollout/issues/03.md"
        original = third.read_text()
        third.write_text(original.replace("01, 02", "01"))
        self.assertNotEqual(
            run_script(workspace / "verify.py", cwd=workspace).returncode, 0
        )
        third.write_text(original)
        extra = workspace / ".project-efforts/runtime-rollout/unknowns.md"
        extra.write_text("## U1 — Already approved rollout?\n")
        self.assertNotEqual(
            run_script(workspace / "verify.py", cwd=workspace).returncode, 0
        )


if __name__ == "__main__":
    unittest.main()
