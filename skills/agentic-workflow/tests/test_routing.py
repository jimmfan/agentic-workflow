from __future__ import annotations

import json
from pathlib import Path
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]


class RoutingContractTests(unittest.TestCase):
    def test_decision_catalog_covers_core_routes_and_authorization(self) -> None:
        scenarios = json.loads((PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text())
        dominant = {item["dominant_activity"] for item in scenarios}
        results = {item["route_result"] for item in scenarios}
        effects = {item["repository_state_effect"] for item in scenarios}
        self.assertTrue({"direct", "debugging", "discovery", "research"} <= dominant)
        self.assertTrue({"direct", "local", "host-native-fallback", "blocked"} <= results)
        self.assertTrue({"read-only", "none", "repository-write"} <= effects)

    def test_every_scenario_keeps_selection_execution_and_effect_explicit(self) -> None:
        scenarios = json.loads((PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text())
        required = {
            "id",
            "prompt",
            "dominant_activity",
            "capabilities",
            "provider_invocations",
            "route_result",
            "executed",
            "repository_state_effect",
            "expected_behavior",
        }
        for scenario in scenarios:
            with self.subTest(scenario=scenario["id"]):
                self.assertTrue(required <= set(scenario))
                for provider in scenario["provider_invocations"]:
                    self.assertTrue({"name", "policy", "invocation", "executed"} <= set(provider))

    def test_route_marker_is_required_without_becoming_runtime_telemetry(self) -> None:
        routing = (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text()
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        self.assertIn("Every user-facing final response MUST end with exactly one", root_policy)
        self.assertIn("Every user-facing final response must end with exactly one", routing)
        self.assertIn("[route: router → debugging → wayfinder]", routing)
        self.assertIn("[route: router → research-handoff]", routing)
        self.assertIn("unexecuted selection do not count as execution", routing)
        self.assertIn("Do not reroute, load skills, execute workflows", routing)
        self.assertNotIn("runtime/capabilities.json", routing)
        self.assertNotIn(".agent-workflow/runtime", routing)

    def test_project_adr_namespace_defaults_without_overriding_existing_convention(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        contract = (
            PACKAGE_ROOT / "payload/agent-workflow/contracts/durable-state.md"
        ).read_text()
        normalized_policy = " ".join(root_policy.split())
        normalized_contract = " ".join(contract.split())
        self.assertIn("Use `docs/decisions/` as the default", normalized_policy)
        self.assertIn(
            "project instructions name another canonical location", normalized_policy
        )
        self.assertIn("do not create a parallel ADR namespace", normalized_contract)
        self.assertIn("Do not promote every workflow choice", normalized_contract)
        self.assertIn("link the workflow record", normalized_contract)
        self.assertIn("maintained set of current decisions", normalized_contract)
        self.assertIn("recoverable version-control history", normalized_contract)

    def test_adr_index_separates_current_records_from_superseded_history(self) -> None:
        index = (REPOSITORY_ROOT / "docs/decisions/README.md").read_text()
        current, superseded = index.split("## Superseded tombstones", 1)
        for identifier in ("ADR-0002", "ADR-0003", "ADR-0005", "ADR-0009"):
            self.assertNotIn(identifier, current)
            self.assertIn(identifier, superseded)
        governance = (
            REPOSITORY_ROOT
            / "docs/decisions/0021-maintain-compact-current-decision-context.md"
        ).read_text()
        self.assertIn("- Status: accepted", governance)
        self.assertIn("Treat a choice the user explicitly resolves as settled", governance)
        self.assertIn("maintained set of current decisions", governance)

    def test_selected_provider_that_cannot_load_is_not_claimed_as_executed(self) -> None:
        scenarios = json.loads((PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text())
        scenario = next(item for item in scenarios if item["id"] == "selected-provider-cannot-execute")
        provider = scenario["provider_invocations"][0]
        self.assertEqual(scenario["host"], "github-copilot")
        self.assertEqual(scenario["route_result"], "host-native-fallback")
        self.assertFalse(provider["executed"])
        self.assertIn("omit Wayfinder from the executed route marker", scenario["expected_behavior"])

    def test_implementation_and_review_do_not_require_tracker_configuration(self) -> None:
        declaration = json.loads(
            (PACKAGE_ROOT / "payload/agent-workflow/providers.json").read_text()
        )
        skills = {item["name"]: item for item in declaration["provider"]["skills"]}
        self.assertEqual(skills["implement"]["requires_configuration"], [])
        self.assertEqual(skills["code-review"]["requires_configuration"], [])
        self.assertIn("issue-tracker", skills["to-spec"]["requires_configuration"])
        self.assertIn("issue-tracker", skills["to-tickets"]["requires_configuration"])

    def test_wayfinder_completion_reconciliation_is_scoped_and_read_only_safe(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        contract = (
            PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md"
        ).read_text()
        self.assertIn("Authorized mutating work is complete only after", root_policy)
        self.assertIn("do not inspect unrelated\n  efforts", root_policy)
        self.assertIn("Do not globally scan Wayfinder state", contract)
        self.assertIn("Canonical artifacts keep ownership of their content", contract)
        self.assertIn("never performs\nreconciliation writes", contract)
        self.assertIn("No\nhook, background process, global index", contract)

    def test_resolved_preferences_and_wayfinder_smells_are_explicit(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        contract = (PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md").read_text()
        normalized_root = " ".join(root_policy.split())
        normalized_contract = " ".join(contract.split())
        self.assertIn("choice the user explicitly resolves as settled", normalized_root)
        self.assertIn("not a reason to renumber an existing item", normalized_contract)
        self.assertIn("large external planning document", normalized_contract)
        self.assertIn("zero children", normalized_contract)

    def test_wayfinder_catalog_covers_implicit_dynamic_explicit_and_read_only_boundaries(self) -> None:
        scenarios = json.loads((PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text())
        by_id = {item["id"]: item for item in scenarios}
        self.assertTrue(
            {
                "wayfinder-implicit-codex",
                "wayfinder-mid-task-escalation",
                "wayfinder-one-isolated-unknown-stays-discovery",
                "wayfinder-explicit-codex",
                "wayfinder-with-debugging-evidence",
                "wayfinder-reconcile-stale-state",
                "wayfinder-read-only-boundary",
                "wayfinder-explicit-opt-out",
                "wayfinder-with-research",
            }
            <= set(by_id)
        )
        for scenario_id in ("wayfinder-implicit-codex", "wayfinder-mid-task-escalation"):
            provider = by_id[scenario_id]["provider_invocations"][0]
            self.assertEqual(provider["policy"], "implicit")
            self.assertEqual(provider["invocation"], "implicit")
            self.assertTrue(provider["executed"])
        self.assertEqual(by_id["wayfinder-with-research"]["provider_invocations"][0]["invocation"], "explicit")
        self.assertEqual(by_id["wayfinder-explicit-codex"]["provider_invocations"][0]["invocation"], "explicit")
        self.assertEqual(by_id["wayfinder-one-isolated-unknown-stays-discovery"]["dominant_activity"], "discovery")
        self.assertEqual(by_id["wayfinder-one-isolated-unknown-stays-discovery"]["provider_invocations"], [])
        self.assertEqual(by_id["wayfinder-with-debugging-evidence"]["capabilities"], ["debugging"])
        self.assertEqual(
            by_id["wayfinder-reconcile-stale-state"]["repository_state_effect"],
            "project-owned-wayfinder-state",
        )
        self.assertEqual(by_id["wayfinder-read-only-boundary"]["repository_state_effect"], "read-only")
        self.assertEqual(by_id["wayfinder-explicit-opt-out"]["provider_invocations"], [])


if __name__ == "__main__":
    unittest.main()
