from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tomllib
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]

FROZEN_MAIN_ROUTING = {
    "direct-ignores-missing-setup": ("direct", (), "read-only"),
    "research-as-dominant-activity": ("research", (), "provider-native-artifact"),
    "debugging-as-dominant-activity": ("debugging", (), "read-only"),
    "discovery-read-only": ("discovery", (), "none"),
    "implementation-implicit-codex": ("implementation", ("verification",), "repository-write"),
    "verification-completed-meaningful-change": ("verification", (), "read-only"),
    "wayfinder-two-soft-signals": ("wayfinder", (), "project-owned-wayfinder-state"),
    "wayfinder-one-isolated-unknown-stays-discovery": ("discovery", (), "none"),
    "wayfinder-explicit-codex": ("wayfinder", (), "project-owned-wayfinder-state"),
    "wayfinder-explicit-opt-out": ("host-native-planning", (), "read-only"),
    "wayfinder-read-only-boundary": ("host-native-analysis", (), "read-only"),
    "wayfinder-reconcile-stale-state": ("wayfinder", (), "project-owned-wayfinder-state"),
}


def load_decisions() -> dict[str, dict[str, object]]:
    path = PACKAGE_ROOT / "tests/decision-contract-scenarios.json"
    return {item["id"]: item for item in json.loads(path.read_text(encoding="utf-8"))}


def load_behavior(identifier: str) -> dict[str, object]:
    path = PACKAGE_ROOT / "tests/scenarios" / f"{identifier}.toml"
    with path.open("rb") as handle:
        return tomllib.load(handle)


class BasicPhase2CompatibilityTests(unittest.TestCase):
    def assert_frozen_main_routing(self, decisions: dict[str, dict[str, object]]) -> None:
        mismatches: list[str] = []
        for identifier, expected in FROZEN_MAIN_ROUTING.items():
            scenario = decisions[identifier]
            actual = (
                scenario["dominant_activity"],
                tuple(scenario["capabilities"]),
                scenario["repository_state_effect"],
            )
            if actual != expected:
                mismatches.append(
                    f"{identifier}: expected {expected!r}, observed {actual!r}"
                )
        self.assertEqual(
            mismatches,
            [],
            "frozen main route/state compatibility changed:\n" + "\n".join(mismatches),
        )

    def test_shared_routing_categories_match_frozen_main(self) -> None:
        self.assert_frozen_main_routing(load_decisions())

    def test_negative_routing_assertion_detects_wayfinder_overselection(self) -> None:
        mutated = deepcopy(load_decisions())
        mutated["direct-ignores-missing-setup"]["dominant_activity"] = "wayfinder"
        with self.assertRaisesRegex(AssertionError, "direct-ignores-missing-setup"):
            self.assert_frozen_main_routing(mutated)

    def test_authority_unrelated_state_stale_evidence_and_lifecycle_contracts_remain(self) -> None:
        authority = load_behavior("wayfinder-human-authority-clarification")
        self.assertIn("what the answer will unblock", authority["report_must_include"])
        self.assertTrue(any("decisions" in path for path in authority["forbid_created_globs"]))

        unrelated = load_behavior("unrelated-wayfinder-state")
        self.assertIn("wayfinder", unrelated["route_must_not_include"])
        self.assertTrue(
            any("database-migration/map.md" in path for path in unrelated["preserve_paths"])
        )

        stale = load_behavior("wayfinder-read-only-stale-state")
        self.assertIn("repository_unchanged", stale["expect"])
        self.assertIn("wayfinder", stale["route_must_not_include"])
        self.assertIn("deployment.py", stale["report_must_include"])

        lifecycle = load_behavior("project-state-preservation")
        self.assertIn("lifecycle_state_preserved", lifecycle["expect"])
        self.assertIn("project_state_preserved", lifecycle["expect"])


if __name__ == "__main__":
    unittest.main()
