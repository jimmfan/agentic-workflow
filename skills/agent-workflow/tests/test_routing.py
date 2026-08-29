from __future__ import annotations

from pathlib import Path
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
PRE_THIN_AMBIGUOUS_ROUTE_WORDS = 2169
PRE_THIN_DIRECT_ROOT_WORDS = 682
GLOBAL_RECONCILIATION_RULE_WORDS = 94
GLOBAL_RECONCILIATION_RULE_PROFILE = (700, GLOBAL_RECONCILIATION_RULE_WORDS)
PRE_DECOMPOSITION_CONTEXT = {
    "direct": (3362, 466),
    "standalone-discovery": (7642, 1050),
    "wayfinder-decision": (54264, 7683),
    "wayfinder-causal": (71751, 10118),
    "wayfinder-research": (68316, 9636),
    "wayfinder-implementation": (52822, 7462),
    "multi-front": (79626, 11294),
}


def instruction_profile(paths: list[Path]) -> tuple[int, int]:
    bodies = [path.read_text(encoding="utf-8") for path in paths]
    return sum(len(body.encode("utf-8")) for body in bodies), sum(
        len(body.split()) for body in bodies
    )


class RoutingContractTests(unittest.TestCase):
    def test_explicit_compatible_skill_selection_still_takes_precedence(self) -> None:
        routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text().split()
        )

        self.assertIn(
            "Explicit compatible skill request | Named skill | Honor unless authorization, "
            "safety, or compatibility blocks it",
            routing,
        )

    def test_route_marker_is_required_without_becoming_runtime_telemetry(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        normalized_root = " ".join(root_policy.split())
        self.assertIn(
            "End each user-facing final response with exactly one truthful",
            normalized_root,
        )
        self.assertIn(
            "Never reroute or work merely to produce the marker", normalized_root
        )

    def test_authority_blocks_only_dependent_work_and_preserves_read_scope(
        self,
    ) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        normalized_root = " ".join(root_policy.split())
        state_contract = (
            PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md"
        ).read_text()
        normalized_state_contract = " ".join(state_contract.split())

        self.assertIn(
            "MUST NOT cross a consequential decision boundary without required "
            "evidence, approval, or authority",
            normalized_root,
        )
        self.assertIn(
            "Explicit responsible-authority acceptance leaves the recorded uncertainty "
            "unresolved and unblocks only its named boundary",
            normalized_root,
        )
        self.assertNotIn("U#", normalized_root)
        self.assertIn("independent work may continue", normalized_root)
        self.assertIn("why authority is required", normalized_root)
        self.assertIn(
            "Exact external read-only targets permit only that read",
            normalized_root,
        )
        self.assertIn(
            "can record authority; it cannot create it", normalized_state_contract
        )

    def test_specialist_selection_has_material_boundaries(self) -> None:
        self._assert_optional_specialist_boundaries()

    def _assert_optional_specialist_boundaries(self) -> None:
        routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text().split()
        )
        required_boundaries = (
            "Discovery owns bounded consequential choice",
            "reorganizing the domain would materially improve",
            (
                "Interdependent human/project-owned decisions materially shape downstream choices "
                "| Direct or `grilling`"
            ),
            "factual unknowns and one straightforward clarification use the minimum sufficient method",
            (
                "Throwaway implementation would answer a design or behavior question "
                "| Direct or `prototype`"
            ),
            "Ordinary production implementation stays Direct or with its dominant workflow",
            (
                "Module interface, seam, depth, locality, or testability needs explicit design "
                "| Direct or `codebase-design`"
            ),
            (
                "when its vocabulary materially improves the design; ordinary edits and refactors "
                "stay Direct or with their dominant workflow"
            ),
        )
        for boundary in required_boundaries:
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, routing)

    def test_missing_wayfinder_contract_fails_closed_without_substitute_state(
        self,
    ) -> None:
        runtime = " ".join(
            (PACKAGE_ROOT / "runtime-projections/wayfinder.md").read_text().split()
        )
        self.assertIn("If the state contract is unavailable", runtime)
        self.assertIn("do not invent substitute persistence", runtime)

    def test_wayfinder_route_loads_the_state_contract_before_the_map(
        self,
    ) -> None:
        root_policy = " ".join(
            (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text().split()
        )
        self.assertIn(
            "read `.agent-workflow/contracts/wayfinder-state.md` before the map",
            root_policy.casefold(),
        )

    def test_thin_router_is_direct_first_and_progressively_loaded(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        routing = (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text()
        normalized_root = " ".join(root_policy.split())
        normalized_routing = " ".join(routing.split())

        self.assertIn("Direct is default", normalized_root)
        self.assertIn("skill selects a workflow", normalized_root)
        self.assertIn(
            "encountering the topic alone never forces a specialist", normalized_root
        )
        self.assertIn(
            "one obvious specialist inside an already selected Wayfinder effort",
            normalized_root,
        )
        self.assertIn("Read `.agent-workflow/routing.md` only when", normalized_root)
        self.assertIn(
            "Three or more meaningful items require assessment, never selection by count alone",
            normalized_root,
        )
        self.assertIn(
            "After reconnaissance, assess durable coordination", normalized_root
        )
        self.assertIn("MUST select or resume Wayfinder", normalized_root)
        self.assertIn("any hard signal or at least two soft signals", normalized_root)
        self.assertIn("Read-only work changes no state", normalized_root)
        self.assertNotIn("\n* ", root_policy)
        self.assertNotIn(
            "If it is unclear whether the work is clearly bounded", normalized_root
        )
        self.assertNotIn("For a named skill, a resume", normalized_root)
        self.assertIn("avoid routing loops", normalized_routing.lower())
        self.assertIn("trivial low-risk edits stay direct", normalized_routing.lower())
        self.assertIn("no safe authorized fallback exists", normalized_routing)
        self.assertIn("report the host-native activity", normalized_routing)
        self.assertIn("selection did not become equivalent execution", normalized_root)
        self.assertIn(
            "selection did not become equivalent execution", normalized_routing
        )
        self.assertIn("omit the unavailable provider", normalized_routing)

        self._assert_context_reduction_budgets()
        self._assert_directional_context_profiles()

    def _assert_context_reduction_budgets(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        root_words = len(root_policy.split())

        self.assertLessEqual(
            root_words,
            PRE_THIN_AMBIGUOUS_ROUTE_WORDS // 5 + GLOBAL_RECONCILIATION_RULE_WORDS,
            "routing context excluding the required global reconciliation rule must be at least 80% smaller when the old ambiguity gate loaded root plus router",
        )
        self.assertLessEqual(
            root_words,
            PRE_THIN_DIRECT_ROOT_WORDS * 65 // 100
            + GLOBAL_RECONCILIATION_RULE_WORDS,
            "the always-loaded root excluding the required global reconciliation rule must be at least 35% smaller for confidently Direct work",
        )

        selected_skills = [
            PACKAGE_ROOT / "payload/skills/workflow-debugging/SKILL.md",
            PACKAGE_ROOT / "payload/skills/workflow-discovery/SKILL.md",
            PACKAGE_ROOT / "payload/skills/workflow-implementation/SKILL.md",
            PACKAGE_ROOT / "payload/skills/workflow-verification/SKILL.md",
            REPOSITORY_ROOT / ".agents/skills/domain-modeling/SKILL.md",
            REPOSITORY_ROOT / ".agents/skills/implement/SKILL.md",
            REPOSITORY_ROOT / ".agents/skills/research/SKILL.md",
            REPOSITORY_ROOT / ".agents/skills/tdd/SKILL.md",
            REPOSITORY_ROOT / ".agents/skills/to-spec/SKILL.md",
            REPOSITORY_ROOT / ".agents/skills/to-tickets/SKILL.md",
        ]
        for skill in selected_skills:
            with self.subTest(skill=skill.parent.name):
                skill_words = len(skill.read_text().split())
                old_context = PRE_THIN_AMBIGUOUS_ROUTE_WORDS + skill_words
                new_context = root_words + skill_words
                self.assertLessEqual(
                    new_context,
                    old_context / 2,
                    "ordinary selected-workflow context must be at least 50% smaller",
                )

    def _assert_directional_context_profiles(
        self,
    ) -> None:
        root = PACKAGE_ROOT / "payload/root/AGENTS.md.template"
        runtime = PACKAGE_ROOT / "runtime-projections/wayfinder.md"
        state = PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md"
        discovery = PACKAGE_ROOT / "payload/skills/workflow-discovery/SKILL.md"
        debugging = PACKAGE_ROOT / "payload/skills/workflow-debugging/SKILL.md"
        implementation = (
            PACKAGE_ROOT / "payload/skills/workflow-implementation/SKILL.md"
        )
        verification = PACKAGE_ROOT / "payload/skills/workflow-verification/SKILL.md"
        research = REPOSITORY_ROOT / ".agents/skills/research/SKILL.md"
        prototype = REPOSITORY_ROOT / ".agents/skills/prototype/SKILL.md"
        domain_modeling = REPOSITORY_ROOT / ".agents/skills/domain-modeling/SKILL.md"
        implement = REPOSITORY_ROOT / ".agents/skills/implement/SKILL.md"

        profiles = {
            "direct": [root],
            "standalone-discovery": [root, discovery],
            "wayfinder-decision": [root, runtime, state],
            "wayfinder-decision-with-discovery": [root, runtime, state, discovery],
            "wayfinder-causal": [root, runtime, state, debugging],
            "wayfinder-research": [root, runtime, state, research],
            "wayfinder-implementation": [
                root,
                runtime,
                state,
                implementation,
                implement,
                verification,
            ],
            "multi-front": [
                root,
                runtime,
                state,
                discovery,
                debugging,
                research,
                prototype,
                domain_modeling,
                implementation,
                verification,
            ],
        }
        measured = {
            name: instruction_profile(paths) for name, paths in profiles.items()
        }

        direct_limit = tuple(
            baseline + reconciliation
            for baseline, reconciliation in zip(
                PRE_DECOMPOSITION_CONTEXT["direct"],
                GLOBAL_RECONCILIATION_RULE_PROFILE,
                strict=True,
            )
        )
        self.assertLessEqual(measured["direct"], direct_limit)
        self.assertLess(
            measured["standalone-discovery"],
            PRE_DECOMPOSITION_CONTEXT["standalone-discovery"],
        )
        self.assertLess(
            measured["wayfinder-decision"],
            PRE_DECOMPOSITION_CONTEXT["wayfinder-decision"],
        )
        self.assertLess(
            measured["wayfinder-decision-with-discovery"],
            PRE_DECOMPOSITION_CONTEXT["wayfinder-decision"],
        )
        for name in (
            "wayfinder-causal",
            "wayfinder-research",
            "wayfinder-implementation",
            "multi-front",
        ):
            with self.subTest(profile=name):
                self.assertLess(measured[name], PRE_DECOMPOSITION_CONTEXT[name])

        self.assertEqual(
            measured["wayfinder-decision-with-discovery"][0]
            - measured["wayfinder-decision"][0],
            discovery.stat().st_size,
        )


if __name__ == "__main__":
    unittest.main()
