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

    def test_decision_catalog_covers_core_routes_and_authorization(self) -> None:
        scenarios = json.loads(
            (PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text()
        )
        dominant = {item["dominant_activity"] for item in scenarios}
        results = {item["route_result"] for item in scenarios}
        effects = {item["repository_state_effect"] for item in scenarios}
        self.assertTrue({"direct", "debugging", "discovery", "research"} <= dominant)
        self.assertTrue(
            {"direct", "local", "host-native-fallback", "user-only-handoff"} <= results
        )
        self.assertTrue({"read-only", "none", "repository-write"} <= effects)

    def test_every_scenario_keeps_selection_execution_and_effect_explicit(self) -> None:
        scenarios = json.loads(
            (PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text()
        )
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
                    self.assertTrue(
                        {"name", "policy", "invocation", "executed"} <= set(provider)
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

    def test_focused_vscode_experiment_is_not_product_behavior(self) -> None:
        removed_repository_paths = (
            ".agent-workflow/hooks/inject_route_marker_reminder.py",
            ".agent-workflow/hooks/protect_wayfinder_state.py",
            ".github/agents/wayfinder.agent.md",
            ".github/copilot-instructions.md",
            ".github/hooks/agent-workflow-route-marker.json",
        )
        removed_package_paths = (
            "payload/agent-workflow/hooks/inject_route_marker_reminder.py",
            "payload/agent-workflow/hooks/protect_wayfinder_state.py",
            "payload/agents/vscode-wayfinder.agent.md",
            "payload/hooks/vscode-route-marker.json",
            "payload/root/vscode-copilot-instructions.md.template",
        )

        for relative in removed_repository_paths:
            self.assertFalse((REPOSITORY_ROOT / relative).exists(), relative)
        for relative in removed_package_paths:
            self.assertFalse((PACKAGE_ROOT / relative).exists(), relative)

        state_contract = (
            PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md"
        ).read_text()
        self.assertIn(".wayfinder-mutation-lock/", state_contract)
        self.assertIn("atomically creating", state_contract)

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

    def test_adr_index_contains_only_current_decisions_and_git_history_note(
        self,
    ) -> None:
        index = (REPOSITORY_ROOT / "architecture-decisions/README.md").read_text()
        decision_root = REPOSITORY_ROOT / "architecture-decisions"
        current_files = {
            path.name for path in decision_root.glob("*.md") if path.name != "README.md"
        }
        expected_files = {
            "0010-separate-framework-output-from-project-owned-state.md",
            "0011-use-map-first-wayfinder-state.md",
            "0025-preserve-authority-at-consequential-boundaries.md",
            "0027-use-direct-first-progressive-routing.md",
            "0028-use-wayfinder-as-sole-durable-coordinator.md",
        }
        self.assertEqual(current_files, expected_files)
        for identifier in ("ADR-0010", "ADR-0011", "ADR-0025", "ADR-0027", "ADR-0028"):
            self.assertIn(identifier, index)
        self.assertIn("previous complete set remains available in Git", index)
        self.assertIn("fb51c4a", index)
        self.assertNotIn("Superseded tombstones", index)

        source_policy = (REPOSITORY_ROOT / "AGENTS.md").read_text()
        self.assertIn("Keep `architecture-decisions/` small", source_policy)
        self.assertIn("Git preserves historical evolution", source_policy)
        root_template = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        self.assertNotIn("Keep `architecture-decisions/` small", root_template)

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

    def test_selected_provider_that_cannot_load_is_not_claimed_as_executed(
        self,
    ) -> None:
        scenarios = json.loads(
            (PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text()
        )
        scenario = next(
            item
            for item in scenarios
            if item["id"] == "selected-provider-cannot-execute"
        )
        provider = scenario["provider_invocations"][0]
        self.assertEqual(scenario["host"], "github-copilot")
        self.assertEqual(scenario["route_result"], "host-native-fallback")
        self.assertFalse(provider["executed"])
        self.assertIn(
            "omit Wayfinder from the executed route marker",
            scenario["expected_behavior"],
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

    def test_domain_modeling_selection_covers_standalone_discovery_and_wayfinder_boundaries(
        self,
    ) -> None:
        scenarios = {
            item["id"]: item
            for item in json.loads(
                (PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text()
            )
        }

        standalone = scenarios["domain-modeling-standalone"]
        self.assertEqual(standalone["dominant_activity"], "domain-modeling")
        self.assertEqual(standalone["capabilities"], [])
        self.assertTrue(standalone["provider_invocations"][0]["executed"])

        discovery = scenarios["discovery-with-coherent-domain"]
        self.assertEqual(discovery["dominant_activity"], "discovery")
        self.assertEqual(discovery["capabilities"], [])

        composed = scenarios["discovery-with-domain-modeling"]
        self.assertEqual(composed["dominant_activity"], "discovery")
        self.assertEqual(composed["capabilities"], ["domain-modeling"])
        self.assertIn("materially affects", composed["expected_behavior"])

        routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text().split()
        )
        self.assertIn("Discovery owns bounded consequential choice", routing)
        self.assertIn("reorganizing the domain would materially improve", routing)

    def test_grilling_resolves_interdependent_human_decisions_not_simple_unknowns(
        self,
    ) -> None:
        routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text().split()
        )

        self.assertIn(
            "Interdependent human/project-owned decisions materially shape downstream choices "
            "| Direct or `grilling`",
            routing,
        )
        self.assertIn(
            "factual unknowns and one straightforward clarification use the minimum sufficient method",
            routing,
        )

    def test_prototype_answers_design_questions_not_ordinary_implementation(
        self,
    ) -> None:
        routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text().split()
        )

        self.assertIn(
            "Throwaway implementation would answer a design or behavior question "
            "| Direct or `prototype`",
            routing,
        )
        self.assertIn(
            "Ordinary production implementation stays Direct or with its dominant workflow",
            routing,
        )

    def test_codebase_design_materially_improves_module_design_not_every_refactor(
        self,
    ) -> None:
        routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text().split()
        )

        self.assertIn(
            "Module interface, seam, depth, locality, or testability needs explicit design "
            "| Direct or `codebase-design`",
            routing,
        )
        self.assertIn(
            "when its vocabulary materially improves the design; ordinary edits and refactors "
            "stay Direct or with their dominant workflow",
            routing,
        )

    def test_missing_wayfinder_contract_fails_closed_without_substitute_state(
        self,
    ) -> None:
        scenarios = {
            item["id"]: item
            for item in json.loads(
                (PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text()
            )
        }
        missing = scenarios["wayfinder-missing-state-contract"]
        self.assertFalse(missing["executed"])
        self.assertEqual(missing["repository_state_effect"], "none")
        self.assertIn("no substitute persistence", missing["expected_behavior"])

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

    def test_wayfinder_catalog_covers_implicit_dynamic_explicit_and_read_only_boundaries(
        self,
    ) -> None:
        scenarios = json.loads(
            (PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text()
        )
        by_id = {item["id"]: item for item in scenarios}
        self.assertTrue(
            {
                "wayfinder-implicit-codex",
                "wayfinder-mid-task-escalation",
                "wayfinder-one-isolated-unknown-stays-discovery",
                "wayfinder-explicit-codex",
                "wayfinder-with-debugging-evidence",
                "wayfinder-direct-decision-resolution",
                "wayfinder-with-discovery",
                "wayfinder-ready-implementation-handoff",
                "wayfinder-resumes-interrupted-specialist",
                "wayfinder-reconcile-stale-state",
                "wayfinder-read-only-boundary",
                "wayfinder-explicit-opt-out",
                "wayfinder-with-research",
                "wayfinder-with-prototype",
            }
            <= set(by_id)
        )
        for scenario_id in (
            "wayfinder-implicit-codex",
            "wayfinder-mid-task-escalation",
        ):
            provider = by_id[scenario_id]["provider_invocations"][0]
            self.assertEqual(provider["policy"], "implicit")
            self.assertEqual(provider["invocation"], "implicit")
            self.assertTrue(provider["executed"])
        self.assertEqual(
            by_id["wayfinder-with-research"]["provider_invocations"][0]["invocation"],
            "explicit",
        )
        self.assertEqual(
            by_id["wayfinder-explicit-codex"]["provider_invocations"][0]["invocation"],
            "explicit",
        )
        self.assertEqual(
            by_id["wayfinder-one-isolated-unknown-stays-discovery"][
                "dominant_activity"
            ],
            "discovery",
        )
        self.assertEqual(
            by_id["wayfinder-one-isolated-unknown-stays-discovery"][
                "provider_invocations"
            ],
            [],
        )
        self.assertEqual(
            by_id["wayfinder-with-debugging-evidence"]["capabilities"], ["debugging"]
        )
        self.assertEqual(
            by_id["wayfinder-direct-decision-resolution"]["capabilities"], []
        )
        self.assertEqual(
            by_id["wayfinder-with-discovery"]["capabilities"], ["discovery"]
        )
        self.assertEqual(
            by_id["wayfinder-ready-implementation-handoff"]["capabilities"],
            ["verification"],
        )
        self.assertEqual(
            by_id["wayfinder-resumes-interrupted-specialist"]["capabilities"],
            ["debugging"],
        )
        self.assertEqual(
            by_id["wayfinder-with-prototype"]["capabilities"], ["prototype"]
        )
        for scenario_id in (
            "wayfinder-with-research",
            "wayfinder-with-prototype",
            "wayfinder-with-debugging-evidence",
            "wayfinder-with-discovery",
            "wayfinder-resumes-interrupted-specialist",
        ):
            self.assertIn("reconcile", by_id[scenario_id]["expected_behavior"].lower())
        self.assertEqual(
            by_id["wayfinder-reconcile-stale-state"]["repository_state_effect"],
            "project-owned-wayfinder-state",
        )
        self.assertEqual(
            by_id["wayfinder-read-only-boundary"]["repository_state_effect"],
            "read-only",
        )
        self.assertEqual(
            by_id["wayfinder-explicit-opt-out"]["provider_invocations"], []
        )

    def test_catalog_covers_routing_seams_that_previously_relied_on_prose(self) -> None:
        scenarios = json.loads(
            (PACKAGE_ROOT / "tests/decision-contract-scenarios.json").read_text()
        )
        by_id = {item["id"]: item for item in scenarios}

        trivial_edit = by_id["trivial-local-edit-stays-direct"]
        self.assertEqual(trivial_edit["dominant_activity"], "direct")
        self.assertEqual(trivial_edit["provider_invocations"], [])
        self.assertEqual(trivial_edit["repository_state_effect"], "repository-write")

        setup_handoff = by_id["setup-user-only-copilot"]
        self.assertEqual(setup_handoff["route_result"], "user-only-handoff")
        self.assertFalse(setup_handoff["executed"])

        fallback = by_id["selected-provider-cannot-execute"]
        self.assertEqual(fallback["route_result"], "host-native-fallback")
        self.assertTrue(fallback["executed"])
        self.assertEqual(fallback["expected_marker"], "[route: router → direct]")
        self.assertIn("actual host-native activity", fallback["expected_behavior"])

        three_items = by_id["three-trivial-items-stay-direct"]
        self.assertEqual(three_items["dominant_activity"], "direct")
        self.assertEqual(three_items["provider_invocations"], [])

        soft_signals = by_id["wayfinder-two-soft-signals"]
        self.assertEqual(soft_signals["dominant_activity"], "wayfinder")
        self.assertTrue(soft_signals["provider_invocations"][0]["executed"])

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

    def test_thin_router_and_sole_coordinator_decisions_are_current(self) -> None:
        decision = (
            REPOSITORY_ROOT
            / "architecture-decisions/0027-use-direct-first-progressive-routing.md"
        ).read_text()
        index = (REPOSITORY_ROOT / "architecture-decisions/README.md").read_text()
        self.assertIn("- Status: accepted", decision)
        self.assertIn("Begin with the simplest reasonable route", decision)
        self.assertIn("Routing is not frozen at the first prompt", decision)
        self.assertIn("progressively load deeper", decision)
        self.assertNotIn("model-based grading", decision.lower())
        self.assertIn("ADR-0027", index)
        coordinator = (
            REPOSITORY_ROOT
            / "architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md"
        ).read_text()
        self.assertIn("- Status: accepted", coordinator)
        self.assertIn("sole framework-owned durable coordination", coordinator)
        self.assertIn("ADR-0028", index)


if __name__ == "__main__":
    unittest.main()
