from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
# Frozen at a7deffc: 682 root words plus 1,487 detailed-router words.
PRE_THIN_AMBIGUOUS_ROUTE_WORDS = 2169
PRE_THIN_DIRECT_ROOT_WORDS = 682
PRE_DECOMPOSITION_CONTEXT = {
    "direct": (3362, 466),
    "standalone-discovery": (7642, 1050),
    "wayfinder-decision": (54264, 7683),
    "wayfinder-causal": (71751, 10118),
    "wayfinder-research": (68316, 9636),
    "wayfinder-implementation": (52822, 7462),
    "multi-front": (79626, 11294),
}
ROUTING_TABLE_COVERAGE_EXCEPTIONS: dict[str, str] = {}


def instruction_profile(paths: list[Path]) -> tuple[int, int]:
    bodies = [path.read_text(encoding="utf-8") for path in paths]
    return sum(len(body.encode("utf-8")) for body in bodies), sum(
        len(body.split()) for body in bodies
    )


class RoutingContractTests(unittest.TestCase):
    def test_every_normally_model_invokable_skill_has_a_routing_selection_cue(
        self,
    ) -> None:
        declaration = json.loads(
            (PACKAGE_ROOT / "payload/agent-workflow/providers.json").read_text()
        )
        provider_skills = {
            item["name"]
            for item in declaration["provider"]["skills"]
            if "implicit" in item["invocation"].values()
        }
        framework_skills = set()
        for path in (PACKAGE_ROOT / "payload/skills").glob("*/SKILL.md"):
            match = re.search(r"^name: (\S+)$", path.read_text(), re.MULTILINE)
            self.assertIsNotNone(match, path)
            framework_skills.add(match.group(1))
        normally_invokable = provider_skills | framework_skills

        routing = (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text()
        table = routing.split("| Signal | Selection | Boundary |", 1)[1].split(
            "Normal intent may select", 1
        )[0]
        selection_cells = [
            line.split("|")[2]
            for line in table.splitlines()
            if line.startswith("|") and not line.startswith("|---")
        ]
        normalized_selections = [
            re.sub(r"[^a-z0-9]+", " ", cell.lower()).strip() for cell in selection_cells
        ]
        missing = set()
        for name in normally_invokable:
            selection_label = re.sub(
                r"[^a-z0-9]+", " ", name.removeprefix("workflow-").lower()
            ).strip()
            cue = re.compile(rf"(?:^| ){re.escape(selection_label)}(?:$| )")
            if not any(cue.search(selection) for selection in normalized_selections):
                missing.add(name)

        self.assertTrue(
            all(reason.strip() for reason in ROUTING_TABLE_COVERAGE_EXCEPTIONS.values())
        )
        self.assertTrue(set(ROUTING_TABLE_COVERAGE_EXCEPTIONS) <= missing)
        self.assertEqual(missing - set(ROUTING_TABLE_COVERAGE_EXCEPTIONS), set())

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
        routing = (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text()
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        normalized_root = " ".join(root_policy.split())
        normalized_routing = " ".join(routing.split())
        self.assertIn(
            "End each user-facing final response with exactly one truthful",
            normalized_root,
        )
        self.assertIn(
            "Never reroute or work merely to produce the marker", normalized_root
        )
        self.assertIn(
            "Every user-facing final response ends with exactly one", normalized_routing
        )
        self.assertIn("[route: router → implement → verification]", normalized_routing)
        self.assertIn("<skill>-handoff", normalized_routing)
        self.assertIn(
            "unexecuted selections do not count as execution", normalized_routing
        )
        self.assertIn("Never reroute, load skills, execute work", normalized_routing)
        self.assertNotIn("runtime/capabilities.json", routing)
        self.assertNotIn(".agent-workflow/runtime", routing)

    def test_project_adr_namespace_defaults_without_overriding_existing_convention(
        self,
    ) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        contract = (
            PACKAGE_ROOT / "payload/agent-workflow/contracts/durable-state.md"
        ).read_text()
        normalized_policy = " ".join(root_policy.split())
        normalized_contract = " ".join(contract.split())
        self.assertNotIn("architecture-decision/", normalized_policy)
        self.assertNotIn("architecture-decision/", normalized_contract)
        self.assertIn(
            "Use `architecture-decisions/` as the default", normalized_contract
        )
        self.assertIn("Preserve an existing project convention", normalized_contract)
        self.assertIn("instead of creating a parallel namespace", normalized_contract)
        self.assertIn("Do not promote every workflow choice", normalized_contract)
        self.assertIn("A current Wayfinder D# may link that ADR", normalized_contract)
        self.assertIn("maintained consequential decisions", normalized_contract)
        self.assertIn(
            "follow the project's existing convention for superseded or historical decisions",
            normalized_contract,
        )
        self.assertNotIn("pre-1.0 decision history", normalized_contract)
        self.assertNotIn("without requiring tombstone files", normalized_contract)
        self.assertNotIn(
            "Consolidate or remove obsolete pre-1.0 decisions", root_policy
        )

    def test_decision_context_goal_blocks_only_dependent_work(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        normalized_root = " ".join(root_policy.split())
        decision = (
            REPOSITORY_ROOT
            / "architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md"
        ).read_text()
        normalized_decision = " ".join(decision.split())
        map_decision = (
            REPOSITORY_ROOT
            / "architecture-decisions/0011-use-map-first-wayfinder-state.md"
        ).read_text()
        normalized_map_decision = " ".join(map_decision.split())
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
        for required in (
            "consequential decision boundary",
            "required evidence, approval, or authority remains unresolved",
            "Independent work may continue",
            "explicitly accept residual uncertainty for one named boundary",
            "does not answer the underlying unknown",
            "do not expand authority",
        ):
            self.assertIn(required, normalized_decision)
        for required in (
            "low-resolution semantic territory",
            "current navigation rather than permanent identities",
            "current state converges and shrinks",
            "material dependencies are answered or explicitly dispositioned",
            "owns scoped reconciliation",
            "one coherent operational model",
        ):
            self.assertIn(required, normalized_map_decision)
        self.assertIn(
            "The resolution method determines what evidence or authority is sufficient",
            normalized_state_contract,
        )
        self.assertIn(
            "Durable Wayfinder state can record authority", normalized_state_contract
        )
        self.assertIn(
            "A semantic area is settled when no consequential uncertainty remains",
            normalized_state_contract,
        )

    def test_implementation_and_review_do_not_require_tracker_configuration(
        self,
    ) -> None:
        declaration = json.loads(
            (PACKAGE_ROOT / "payload/agent-workflow/providers.json").read_text()
        )
        skills = {item["name"]: item for item in declaration["provider"]["skills"]}
        self.assertEqual(skills["implement"]["requires_configuration"], [])
        self.assertEqual(skills["code-review"]["requires_configuration"], [])
        self.assertIn("issue-tracker", skills["to-spec"]["requires_configuration"])
        self.assertIn("issue-tracker", skills["to-tickets"]["requires_configuration"])

    def test_specialist_workflows_are_stateless_and_keep_their_methods(self) -> None:
        discovery = (
            PACKAGE_ROOT / "payload/skills/workflow-discovery/SKILL.md"
        ).read_text()
        debugging = (
            PACKAGE_ROOT / "payload/skills/workflow-debugging/SKILL.md"
        ).read_text()
        implementation = (
            PACKAGE_ROOT / "payload/skills/workflow-implementation/SKILL.md"
        ).read_text()
        durable = (
            PACKAGE_ROOT / "payload/agent-workflow/contracts/durable-state.md"
        ).read_text()

        discovery = " ".join(discovery.split())
        debugging = " ".join(debugging.split())
        implementation = " ".join(implementation.split())
        durable = " ".join(durable.split())

        self.assertIn("without creating DEC", discovery)
        self.assertIn("Compare viable alternatives", discovery)
        self.assertIn("without creating a DBG", debugging)
        self.assertIn("Form 3–5 ranked, falsifiable hypotheses", debugging)
        self.assertIn("Create no IMP or replacement record", implementation)
        self.assertIn("Invoke `workflow-verification` once", implementation)
        self.assertIn("not a current framework re-entry point", durable)

    def test_optional_specialists_have_material_selection_boundaries(self) -> None:
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

    def test_wayfinder_completion_reconciliation_is_scoped_and_read_only_safe(
        self,
    ) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        contract = (
            PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md"
        ).read_text()
        normalized_contract = " ".join(contract.split())
        normalized_root = " ".join(root_policy.split())
        self.assertIn("wayfinder-state.md` before the map", normalized_root)
        self.assertIn("only before current project-state writes", normalized_root)
        self.assertIn("An unrelated map never selects Wayfinder", normalized_root)
        self.assertIn("Do not globally scan for related efforts", normalized_contract)
        self.assertIn("do not copy canonical artifact bodies", normalized_contract)
        self.assertIn(
            "Read-only work reports the exact stale claim", normalized_contract
        )
        self.assertIn("No hook, daemon, synchronization service", normalized_contract)

    def test_resolved_preferences_and_wayfinder_smells_are_explicit(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        contract = (
            PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md"
        ).read_text()
        normalized_root = " ".join(root_policy.split())
        normalized_contract = " ".join(contract.split())
        self.assertIn("Reopen a settled choice only", normalized_root)
        self.assertIn("Never renumber an existing current record", normalized_contract)
        self.assertIn("`map.md` owns the current state", normalized_contract)
        self.assertIn("`map.md` alone is a complete and valid", normalized_contract)
        self.assertIn(
            "Do not turn every source read or test run into an E#", normalized_contract
        )

    def test_wayfinder_efforts_have_stable_names_and_progressive_resume_rules(
        self,
    ) -> None:
        contract = (
            PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md"
        ).read_text()
        normalized = " ".join(contract.split())
        for required in (
            "## Effort naming, selection, and stable paths",
            "The H1 heading in `map.md` is the durable human-readable effort name",
            "directory slug is only its stable storage key",
            "List effort directory names",
            "smallest plausible candidate set",
            "If multiple efforts remain plausible",
            "create a third synonymous effort",
            "A branch, ticket, file, command, temporary task description, or chat title",
            "lowercase, filesystem-safe, hyphen-separated",
            "Immediately before creating the directory",
            "shortest stable meaningful disambiguator",
            "Once created, the effort directory path is stable",
            "Established awkward or legacy slugs remain valid",
            "bringing previously out-of-scope work inside the boundary",
        ):
            self.assertIn(required, normalized)
        self.assertNotIn("## Identity", contract)
        self.assertNotIn("├── identity", contract)
        self.assertNotIn("identity/unknowns", contract)

    def test_external_read_scope_is_always_loaded_policy(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        normalized_root = " ".join(root_policy.split())

        self.assertIn("Exact external read-only targets", normalized_root)

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

    def test_thin_router_meets_context_reduction_budgets(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        root_words = len(root_policy.split())

        self.assertLessEqual(
            root_words,
            PRE_THIN_AMBIGUOUS_ROUTE_WORDS // 5,
            "routing context must be at least 80% smaller when the old ambiguity gate loaded root plus router",
        )
        self.assertLessEqual(
            root_words,
            PRE_THIN_DIRECT_ROOT_WORDS * 65 // 100,
            "the always-loaded root must be at least 35% smaller for confidently Direct work",
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

    def test_specialist_backed_wayfinder_reduces_directional_context_profiles(
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

        self.assertLessEqual(measured["direct"], PRE_DECOMPOSITION_CONTEXT["direct"])
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
