from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPOSITORY_ROOT / "agent_workflow"

EXPECTED_FRAMEWORK_LANGUAGE = {
    "Wayfinder effort",
    "Map",
    "Objective",
    "Scope",
    "Consequential",
    "Current coordination state",
    "Ready work",
    "Dependency",
    "Blocker",
    "U# (unresolved question record)",
    "F# (fact record)",
    "Project decision authority",
    "Reconciliation",
    "Pruning",
    "Framework-owned",
    "Project-owned",
    "Durable",
    "Reconstructable",
}


class RoutingContractTests(unittest.TestCase):
    """Check literal routing interfaces; behavior is exercised by fixture outcomes."""

    def test_framework_terminology_has_the_canonical_term_inventory(self) -> None:
        terminology = (REPOSITORY_ROOT / ".agent-workflow/terminology.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            set(re.findall(r"^\*\*([^*]+)\*\*:", terminology, re.MULTILINE)),
            EXPECTED_FRAMEWORK_LANGUAGE,
        )

    def test_framework_terminology_is_distributed_at_its_canonical_path(self) -> None:
        relative = ".agent-workflow/terminology.md"
        self.assertTrue((REPOSITORY_ROOT / relative).is_file())
        manifest = json.loads(
            (PACKAGE_ROOT / "install/manifest.json").read_text(encoding="utf-8")
        )
        self.assertIn(
            {"source": relative, "target": relative},
            manifest["framework_owned"],
        )

    def test_runtime_and_source_policy_reference_canonical_terminology(self) -> None:
        relative = ".agent-workflow/terminology.md"
        distributed_policy = (PACKAGE_ROOT / "install/AGENTS.md.template").read_text(
            encoding="utf-8"
        )
        source_policy = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        project_instructions = source_policy.split(
            "<!-- agent-workflow:managed-end -->", 1
        )[1]
        self.assertIn(relative, distributed_policy)
        self.assertIn(relative, project_instructions)

    def test_route_reporting_documents_machine_interface(self) -> None:
        root_policy = (PACKAGE_ROOT / "install/AGENTS.md.template").read_text(
            encoding="utf-8"
        )
        routing = (REPOSITORY_ROOT / ".agent-workflow/routing.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("[route: router →", root_policy)
        for token in (
            "workflow-discovery",
            "workflow-debugging",
            "workflow-implementation",
            "workflow-verification",
            "discovery",
            "debugging",
            "implement",
            "verification",
            "direct",
            "<skill>-handoff",
            "<skill>-unavailable",
            "<skill>-blocked",
            "->",
        ):
            with self.subTest(token=token):
                self.assertIn(token, routing)

    def test_routing_and_wayfinder_reference_their_runtime_sources(self) -> None:
        root_policy = (PACKAGE_ROOT / "install/AGENTS.md.template").read_text(
            encoding="utf-8"
        )
        self.assertIn(".agent-workflow/routing.md", root_policy)
        routing = (REPOSITORY_ROOT / ".agent-workflow/routing.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("contracts/wayfinder-state.md", routing)
        contract = REPOSITORY_ROOT / ".agent-workflow/contracts/wayfinder-state.md"
        self.assertTrue(contract.is_file())
        wayfinder = (REPOSITORY_ROOT / ".agents/skills/wayfinder/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(".agent-workflow/contracts/wayfinder-state.md", wayfinder)
        self.assertIn("map.md", wayfinder)

    def test_domain_modeling_references_its_project_context_interfaces(self) -> None:
        domain = (
            REPOSITORY_ROOT / ".agents/skills/domain-modeling/SKILL.md"
        ).read_text(encoding="utf-8")
        for filename in ("CONTEXT.md", "CONTEXT-MAP.md", "CONTEXT-FORMAT.md"):
            with self.subTest(filename=filename):
                self.assertIn(filename, domain)


if __name__ == "__main__":
    unittest.main()
