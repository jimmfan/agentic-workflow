"""Structural handoff guards and fixture links; no model compliance is claimed.

These checks keep trigger, timing, and authority clauses together in their owning
instruction layer. They do not execute reconciliation or prove agent ordering.
"""

from pathlib import Path
import tempfile
import unittest

from test_wayfinder_state import broken_fixture_links

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def skill(name: str) -> str:
    return read(f".agents/skills/{name}/SKILL.md")


class SpecialistReconciliationTests(unittest.TestCase):
    def assert_clause(self, text: str, *parts: str) -> None:
        """Require related safeguards in one paragraph, allowing other wording."""
        paragraphs = [" ".join(p.split()) for p in text.split("\n\n")]
        self.assertTrue(
            any(all(part in paragraph for part in parts) for paragraph in paragraphs),
            f"Missing a single instruction paragraph covering {parts!r}",
        )

    def test_debugging_reconciliation_requires_action_authorization(self):
        self.assert_clause(
            skill("workflow-debugging"),
            "Inside Wayfinder",
            "reconcile state only within current action authorization",
            "only for consequential evidence",
            "selected map remains the durable coordination summary",
        )
        self.assert_clause(
            read("agent_workflow/install/AGENTS.md.template"),
            "current user request or accepted project policy authorizes",
            "Workflows, skills and their instructions",
            "Wayfinder records supply neither",
        )

    def test_debugging_reconciles_authorized_evidence_without_another_request(self):
        self.assert_clause(
            skill("workflow-debugging"),
            "Within that authorized scope",
            "user-provided or tool-observed evidence",
            "materially supports or changes",
            "reconcile",
            "through its contract",
            "before further work relies",
            "before final response or handoff",
            "Once those state writes are authorized",
            "do not wait for a separate persistence request",
        )
        self.assert_clause(
            read(".agent-workflow/contracts/wayfinder-state.md"),
            "consequential evidence supplied by a user",
            "observed from an external system",
            "materially supports a diagnosis or implementation choice",
            "future agent cannot reliably reconstruct",
            "source, scope, observation, and limitations",
            "durable project sources",
            "before dependent work relies",
            "before final response or handoff",
            "use a separate E# when its source, method, limitations, or reuse value",
        )

    def test_composed_specialist_handoff_belongs_to_wayfinder(self):
        self.assert_clause(
            skill("wayfinder"),
            "Each specialist retains its method",
            "no separate Agent Workflow durable coordination state",
            "composed specialist",
            "consequential result affecting the selected effort",
            "recording is authorized",
            "through the state contract",
            "before dependent work relies",
            "before final response or handoff",
        )

    def test_standalone_specialists_keep_their_result_owners(self):
        routing = read(".agent-workflow/routing.md")
        self.assert_clause(
            routing,
            "Using a skill for specialist work",
            "does not create separate Agent Workflow durable coordination state",
        )
        owners = {
            "workflow-discovery": "Standalone Discovery returns its result",
            "research": "Return evidence to the caller",
            "prototype": "Report the question, observed result, and limitations",
            "domain-modeling": "Update CONTEXT.md inline",
            "grilling": "State the shared understanding",
        }
        for name, boundary in owners.items():
            with self.subTest(specialist=name):
                self.assertIn(boundary, skill(name))
                self.assertNotIn(".project-efforts/", skill(name))
        self.assert_clause(
            skill("wayfinder"),
            "meaningful review-round boundaries",
            "when recording is authorized",
            "Interpret review answers before recording",
        )

    def test_post_verification_handoff_belongs_to_outer_implementation(self):
        integration = skill("workflow-implementation").split("## Verify the result", 1)[
            1
        ]
        self.assert_clause(
            integration,
            "came from or remains part of a selected Wayfinder effort",
            "recording is authorized",
            "reconcile consequential Verification results",
            "completion, blockers, dependencies, verification boundaries",
            "remaining ready work",
            ".agent-workflow/contracts/wayfinder-state.md",
            "before claiming completion or handing off remaining work",
        )
        for name in ("workflow-verification", "implement", "tdd", "code-review"):
            with self.subTest(method=name):
                self.assertNotIn(
                    ".agent-workflow/contracts/wayfinder-state.md", skill(name)
                )
                self.assertNotIn(".project-efforts/", skill(name))
        self.assert_clause(
            integration,
            "scope is finished",
            "required `workflow-verification` completion gate is satisfied",
        )
        self.assert_clause(
            skill("workflow-verification"),
            "every required acceptance criterion to pass",
            "unless accepted project policy",
            "named completion boundary",
            "person, role, or valid delegate with project decision authority",
            "explicitly accepts it",
        )
        self.assertIn(
            "cannot commit a project choice", skill("workflow-implementation")
        )

    def test_read_only_and_contract_loading_boundaries_remain_explicit(self):
        self.assertIn(
            "Read-only work changes no state",
            read("agent_workflow/install/AGENTS.md.template"),
        )
        self.assert_clause(
            read(".agent-workflow/contracts/wayfinder-state.md"),
            "Read-only work may report stale or conflicting state",
            "does not change it",
        )
        self.assert_clause(
            skill("workflow-debugging"),
            "diagnosis-only work",
            "without editing or implying fix approval",
        )
        self.assert_clause(
            skill("wayfinder"),
            "Once Wayfinder is selected",
            ".agent-workflow/contracts/wayfinder-state.md",
            "before inspecting or changing effort state",
        )

    def test_sufficient_state_needs_no_redundant_record_or_rewrite(self):
        contract = read(".agent-workflow/contracts/wayfinder-state.md")
        self.assert_clause(
            contract,
            "Keep a separate record only when",
            "independently useful",
            "beyond the map",
            "applies to all four record types",
            "the map may remain the entire result",
            "Do not create records from ceremony",
        )
        self.assertIn(
            "do not create or retain an E# merely as a transition step", contract
        )
        self.assertIn("normalize unchanged files", contract)
        self.assertIn(
            "Reconcile only a concrete incompatible statement or an unmet requirement",
            read("agent_workflow/install/AGENTS.md.template"),
        )

    def test_fixture_preflight_rejects_a_wrong_relative_depth(self):
        # Adapt the historical incident's ../../../ vs ../../ failure using the
        # existing fixture checker, without importing its evaluator or artifacts.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "docs/build-context.md"
            source.parent.mkdir()
            source.write_text("# Build context\n")
            map_path = root / ".project-efforts/build/map.md"
            map_path.parent.mkdir(parents=True)
            for target, expected in (
                ("../../docs/build-context.md", []),
                ("../../../docs/build-context.md", ["../../../docs/build-context.md"]),
            ):
                with self.subTest(target=target):
                    map_path.write_text(f"# Build\n[Context]({target})\n")
                    self.assertEqual(broken_fixture_links([map_path]), expected)
            map_path.write_text("# Build\n[Context](../../docs/build-context.md)\n")
            source.unlink()
            self.assertEqual(
                broken_fixture_links([map_path]), ["../../docs/build-context.md"]
            )


if __name__ == "__main__":
    unittest.main()
