from __future__ import annotations

import json
from pathlib import Path
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


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

    def test_route_marker_is_optional_metadata_not_runtime_telemetry(self) -> None:
        routing = (PACKAGE_ROOT / "payload/ai-workflow/routing.md").read_text()
        self.assertIn("marker is optional instruction-level diagnostics", routing)
        self.assertNotIn("runtime/capabilities.json", routing)
        self.assertNotIn(".ai-workflow/runtime", routing)

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
