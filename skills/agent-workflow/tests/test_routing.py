from __future__ import annotations

from pathlib import Path
import re
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]

EXPECTED_PROJECT_LANGUAGE = {
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
    def test_source_project_language_policy_uses_an_undistributed_glossary(
        self,
    ) -> None:
        context_path = REPOSITORY_ROOT / "CONTEXT.md"
        source_policy = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        distributed_policy = (
            PACKAGE_ROOT / "payload/root/AGENTS.md.template"
        ).read_text(encoding="utf-8")

        self.assertTrue(context_path.is_file())
        context = context_path.read_text(encoding="utf-8")
        self.assertEqual(
            set(re.findall(r"^\*\*([^*]+)\*\*:", context, re.MULTILINE)),
            EXPECTED_PROJECT_LANGUAGE,
        )
        entries = {
            name: " ".join(definition.split())
            for name, definition in re.findall(
                r"^\*\*([^*]+)\*\*:\n(.*?)(?=\n\n\*\*|\Z)",
                context,
                re.MULTILINE | re.DOTALL,
            )
        }
        expected_fragments = {
            "Objective": (
                "result a Wayfinder effort is intended to achieve",
            ),
            "Consequential": (
                "handling it differently",
                "effort's objective",
                "scope",
                "required authority",
                "lasting result",
                "dependencies",
                "which work may proceed",
            ),
            "Blocker": (
                "condition that currently prevents particular work",
                "unsatisfied dependency",
                "unresolved consequential uncertainty",
                "missing required authority",
                "can be a blocker",
                "scoped to",
                "not a separate Wayfinder record type",
            ),
            "Ready work": (
                "work to which no blocker currently applies",
            ),
            "Dependency": (
                "particular work requires",
                "action",
                "artifact",
                "decision",
                "person",
                "system",
                "external result",
                "other input",
            ),
            "Pruning": (
                "removes a recognized Wayfinder record from current coordination",
                "File or ledger-section removal carries out pruning",
                "ending an effort is separate",
            ),
            "U# (unresolved question record)": (
                "durable record",
                "consequential question",
                "remains unanswered",
                "record is not itself a blocker",
            ),
            "F# (fact record)": (
                "durable record",
                "scoped descriptive conclusion",
                "sufficiently supported",
                "revisable as evidence changes",
            ),
            "Project decision authority": (
                "person, role, or valid delegate",
                "choice the project treats as binding",
                "defined decision boundary",
                "does not restrict technical judgment already delegated",
            ),
            "Reconciliation": (
                "updating affected current coordination state",
                "current truth",
                "choices committed by project decision authority",
                "designated artifacts that maintain lasting results",
            ),
            "Framework-owned": (
                "content or a delimited region",
                "install, update, and remove lifecycle",
                "separate from durability and reconstructability",
            ),
            "Project-owned": (
                "meaning and preservation belong to the consuming project",
                "reference or interpret a recognized form",
                "without gaining lifecycle ownership",
            ),
            "Durable": (
                "retained across sessions or workflow transitions",
                "separate from lifecycle ownership and reconstructability",
            ),
            "Reconstructable": (
                "current declared source or package content",
                "without losing unique project information",
            ),
        }
        for term, fragments in expected_fragments.items():
            with self.subTest(term=term):
                for fragment in fragments:
                    self.assertIn(fragment.casefold(), entries[term].casefold())
        consequential = entries["Consequential"].casefold()
        self.assertNotIn("blocker", consequential)
        self.assertNotIn("ready work", consequential)
        self.assertNotIn("CONTEXT.md", distributed_policy)
        self.assertNotIn("## Project language", distributed_policy)
        self.assertFalse(any(PACKAGE_ROOT.glob("payload/**/CONTEXT.md")))
        self.assertNotIn(
            "CONTEXT.md",
            (
                PACKAGE_ROOT / "payload/distribution/manifest.json"
            ).read_text(encoding="utf-8"),
        )

        project_instructions = source_policy.split(
            "<!-- agent-workflow:project-instructions -->", 1
        )[1]
        normalized = " ".join(project_instructions.split())
        for requirement in (
            "## Project language",
            "Read `CONTEXT.md` before changing routing, Wayfinder, provider integration, "
            "ownership, or framework-lifecycle concepts",
            "determine the actual concept from current source, behavior, tests, and accepted decisions",
            "identify the bounded technical or domain context that owns it",
            "primary standards, official technical documentation, strong engineering evidence, "
            "and peer-reviewed evidence when available",
            "compare alternatives by exact semantics and applicability",
            "prefer established or literal language only when its semantic precision earns its cognitive cost",
            "state evidence strength and uncertainty honestly",
            "Update `CONTEXT.md` only after the terminology decision is accepted",
            "Keep behavior, architecture, authority, and terminology in their respective owning layers",
            "Do not force one term across genuinely different bounded contexts",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)

    def test_explicit_compatible_skill_selection_still_takes_precedence(self) -> None:
        routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text().split()
        )

        self.assertIn(
            "Explicit compatible skill request | Named skill | Honor unless action authorization, "
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
            "evidence, action authorization, or project decision authority",
            normalized_root,
        )
        self.assertIn(
            "Explicit acceptance by project decision authority leaves the recorded "
            "unresolved question unresolved and unblocks only its named boundary",
            normalized_root,
        )
        self.assertNotIn("U#", normalized_root)
        self.assertIn("independent work may continue", normalized_root)
        self.assertIn("why that authority is required", normalized_root)
        self.assertIn(
            "Exact external read-only targets permit only that read",
            normalized_root,
        )
        self.assertIn(
            "can record authority; it cannot create it", normalized_state_contract
        )
        for distinction in (
            "Evidence cannot commit a project choice",
            "Action authorization does not establish project decision authority",
            "Host permission does not authorize an action or commit a project choice",
            "technical judgment already delegated by user direction or accepted project policy",
            "project artifact that records it",
        ):
            with self.subTest(distinction=distinction):
                self.assertIn(distinction, normalized_state_contract)
        self.assertNotIn(
            "project artifact, accepted policy, or valid delegate that establishes "
            "project decision authority",
            normalized_state_contract,
        )

        documented_routing = " ".join(
            (REPOSITORY_ROOT / "docs/routing.md")
            .read_text(encoding="utf-8")
            .split()
        )
        self.assertIn(
            "actions authorized by user direction or accepted project policy",
            documented_routing,
        )
        for workflow in ("workflow-implementation", "workflow-verification"):
            with self.subTest(workflow=workflow):
                workflow_text = " ".join(
                    (
                        PACKAGE_ROOT / f"payload/skills/{workflow}/SKILL.md"
                    ).read_text(encoding="utf-8").split()
                )
                self.assertIn(
                    "limitation to be explicitly accepted by project decision authority "
                    "for the named completion boundary",
                    workflow_text,
                )

    def test_route_selection_execution_and_provider_statuses_remain_distinct(
        self,
    ) -> None:
        routing = (
            PACKAGE_ROOT / "payload/agent-workflow/routing.md"
        ).read_text(encoding="utf-8")

        sections = {
            heading: " ".join(
                routing.split(heading, 1)[1].split("\n## ", 1)[0].split()
            )
            for heading in (
                "## Decide and compose",
                "## Resolve providers",
                "## Preserve responsibilities and transitions",
                "## Report the executed route",
            )
        }
        for fragment in (
            "Choose Direct or one primary workflow",
            "supporting capabilities that materially help",
        ):
            self.assertIn(fragment, sections["## Decide and compose"])
        for fragment in (
            "Route selection chooses Direct or a workflow",
            "provider resolution identifies the configured provider operation",
            "skill invocation calls or activates the selected skill",
            "material execution means the selected method actually ran",
            "completion and verification require evidence beyond the route marker",
            "host support",
            "invocation policy",
            "configuration readiness",
            "installed provider-projection status",
            "host-native fallback",
        ):
            self.assertIn(fragment, sections["## Resolve providers"])
        self.assertIn(
            "The specialist creates no Agent Workflow durable coordination state",
            sections["## Preserve responsibilities and transitions"],
        )
        reporting = sections["## Report the executed route"]
        self.assertIn("<skill>-handoff", reporting)
        self.assertIn("required provider still needs explicit user invocation", reporting)

    def test_specialist_selection_has_material_boundaries(self) -> None:
        self._assert_optional_specialist_boundaries()

    def _assert_optional_specialist_boundaries(self) -> None:
        routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text().split()
        )
        required_boundaries = (
            "Discovery is the method for bounded consequential choice",
            "reorganizing the domain would materially improve",
            (
                "Interdependent human/project-owned decisions materially shape downstream choices "
                "| Direct or `grilling`"
            ),
            "factual questions and one straightforward clarification use the minimum sufficient method",
            (
                "Throwaway implementation would answer a design or behavior question "
                "| Direct or `prototype`"
            ),
            "Ordinary production implementation stays Direct or with its primary workflow",
            (
                "Module interface, seam, depth, locality, or testability needs explicit design "
                "| Direct or `codebase-design`"
            ),
            (
                "when its vocabulary materially improves the design; ordinary edits and refactors "
                "stay Direct or with their primary workflow"
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
        self.assertIn("no safe fallback with action authorization exists", normalized_routing)
        self.assertIn("report the host-native activity", normalized_routing)
        self.assertIn("selection did not become equivalent execution", normalized_root)
        self.assertIn(
            "selection did not become equivalent execution", normalized_routing
        )
        self.assertIn("omit the unavailable provider", normalized_routing)
        self.assertIn(
            "Direct work, one obvious workflow, and one obvious specialist inside "
            "Wayfinder do not load it",
            normalized_routing,
        )
        self.assertIn(
            "A supporting capability does not become the primary workflow or create "
            "Agent Workflow durable coordination state",
            normalized_routing,
        )
        self.assertIn(
            "After selecting Wayfinder, read `contracts/wayfinder-state.md`, then the map",
            normalized_routing,
        )


if __name__ == "__main__":
    unittest.main()
