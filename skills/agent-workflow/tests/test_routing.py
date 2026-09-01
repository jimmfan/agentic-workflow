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
        project_decision_authority = entries["Project decision authority"]
        for required in (
            "The person, role, or valid delegate whose choice the project treats as binding",
            "within a defined decision boundary",
            "Accepted project policy may determine the choice for that boundary directly",
            "or establish who holds that authority",
            "does not restrict technical judgment already delegated by the user or policy",
        ):
            self.assertIn(required, project_decision_authority)
        self.assertNotIn("settle", project_decision_authority.casefold())
        self.assertEqual(
            entries["Reconciliation"],
            "Updating affected current coordination state so it agrees with current "
            "truth, project choices determined by accepted project policy or committed by "
            "project decision authority, and the designated artifacts that maintain "
            "lasting results.",
        )
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
            "<!-- agent-workflow:managed-end -->", 1
        )[1]
        normalized = " ".join(project_instructions.split())
        for requirement in (
            "## Project language",
            "Read `CONTEXT.md` before changing routing, Wayfinder, direct skill distribution, "
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

    def test_explicit_available_skill_selection_still_takes_precedence(self) -> None:
        routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text().split()
        )

        self.assertIn(
            "Explicit skill request | Named skill | Honor when available unless action "
            "authorization or safety blocks execution; otherwise apply the unavailable-skill rule",
            routing,
        )

    def test_route_marker_is_required_without_becoming_runtime_telemetry(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        normalized_root = " ".join(root_policy.split())
        detailed_routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md")
            .read_text(encoding="utf-8")
            .split()
        )
        self.assertIn(
            "End each user-facing final response with exactly one truthful",
            normalized_root,
        )
        self.assertIn("Report only what executed", normalized_root)
        self.assertIn("use `direct` if no workflow or skill ran", normalized_root)
        self.assertIn(
            "selection did not become equivalent execution", normalized_root
        )
        self.assertIn(
            "Never reroute or work merely to produce the marker", normalized_root
        )
        for compact_label in (
            "`workflow-discovery`",
            "`workflow-debugging`",
            "`workflow-implementation`",
            "`workflow-verification`",
            "`discovery`",
            "`debugging`",
            "`implement`",
            "`verification`",
        ):
            with self.subTest(compact_label=compact_label):
                self.assertIn(compact_label, detailed_routing)
        for terminal_suffix in (
            "`<skill>-handoff`",
            "`<skill>-unavailable`",
            "`<skill>-blocked`",
        ):
            with self.subTest(terminal_suffix=terminal_suffix):
                self.assertIn(terminal_suffix, detailed_routing)
        self.assertIn(
            "listing only workflows and composed capabilities that executed, in "
            "effective-use order",
            detailed_routing,
        )
        self.assertIn("The ASCII `->` separator is valid", detailed_routing)

    def test_root_preserves_source_precedence_and_cross_artifact_boundaries(
        self,
    ) -> None:
        root_policy = " ".join(
            (PACKAGE_ROOT / "payload/root/AGENTS.md.template")
            .read_text(encoding="utf-8")
            .split()
        )

        for boundary in (
            "Preserve unrelated work, project-owned state, designated artifacts, and "
            "identifiers",
            "Live source and accepted artifacts outrank summaries, memory, and chat",
            "Do not manufacture cross-artifact conflicts or parallel representations of "
            "the same current state",
            "Differences in scope, abstraction, summarization, or omitted detail are not "
            "by themselves conflicts",
            "Reconcile only a concrete incompatible statement or an unmet requirement",
            "Update the artifact or record that maintains current state instead of creating "
            "a competing representation unless the new representation has independently "
            "useful meaning, scope, or retrieval value",
            "When materially ambiguous, preserve the existing content and clarify or "
            "investigate rather than inventing detail or process merely to make artifacts agree",
        ):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, root_policy)

    def test_project_choice_and_action_boundaries_are_independent(
        self,
    ) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        normalized_root = " ".join(root_policy.split())
        state_contract = (
            PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md"
        ).read_text()
        normalized_state_contract = " ".join(state_contract.split())

        boundary_requirements = {
            "project-choice commitment gate": (
                "required evidence is sufficient",
                "accepted project policy determines the choice for its boundary",
                "person, role, or valid delegate with project decision authority commits it",
            ),
            "delegated technical judgment": (
                "Evidence-backed technical judgment already delegated by the user or "
                "accepted project policy remains valid",
            ),
            "authority source": (
                "Responsibility alone does not establish project decision authority",
                "from the person, role, or valid delegate with that authority",
                "identify the concrete question",
                "who may decide",
                "why the choice is required",
                "what it unblocks",
            ),
            "blocked and independent work": (
                "Dependent work stops while a required project choice remains uncommitted; "
                "independent work may continue",
            ),
            "authorized action scope": (
                "Perform writes, commands, publication, destructive operations, and external "
                "mutations only when the current user request or accepted project policy "
                "authorizes that action and scope",
                "An exact external read-only target authorizes only that read",
            ),
            "independent gates": (
                "Action authorization does not commit a project choice",
                "A committed project choice does not authorize an unrelated action",
                "Host permission supplies neither",
                "Workflows, skills and their instructions, tests, specifications, "
                "tickets, and Wayfinder records supply neither",
            ),
            "both gates satisfied": (
                "When both the required project choice is committed and the action is "
                "authorized, affected work may proceed only within the authorized scope",
            ),
            "accepted unresolved uncertainty": (
                "explicitly accept unresolved uncertainty for one named boundary",
                "The question remains unresolved",
                "only that boundary becomes unblocked",
                "no broader project choice is committed",
                "no unrelated action is authorized",
                "no other dependency is satisfied",
            ),
        }
        for case, requirements in boundary_requirements.items():
            for requirement in requirements:
                with self.subTest(case=case, requirement=requirement):
                    self.assertIn(requirement, normalized_root)
        self.assertIn(
            "Revisit a committed choice only for conflict, safety, project decision "
            "authority, or request",
            normalized_root,
        )
        self.assertNotIn(
            "Revisit a committed choice only for conflict, safety, authority, or request",
            normalized_root,
        )
        revisit_rule = re.search(
            r"Revisit a committed choice only for [^.]+\.", normalized_root
        )
        self.assertIsNotNone(revisit_rule)
        self.assertNotIn("evidence", revisit_rule.group().casefold())
        self.assertNotIn("U#", normalized_root)
        self.assertIn(
            "can record authority; it cannot create it", normalized_state_contract
        )
        for distinction in (
            "Accepted project policy may determine the choice for a boundary directly",
            "person, role, or valid delegate with project decision authority may commit it",
            "Authorization to perform an action does not commit a project choice",
            "A committed project choice does not authorize an unrelated action",
            "Host permission supplies neither action authorization nor a committed project choice",
            "technical judgment already delegated by the user or accepted project policy",
            "Responsibility alone does not establish project decision authority",
            "clarify who may decide",
            "project artifact that records it",
        ):
            with self.subTest(distinction=distinction):
                self.assertIn(distinction, normalized_state_contract)
        documented_routing = " ".join(
            (REPOSITORY_ROOT / "docs/routing.md")
            .read_text(encoding="utf-8")
            .split()
        )
        self.assertIn(
            "actions authorized by the current user request or accepted project policy",
            documented_routing,
        )
        self.assertIn(
            "D# contains a current consequential choice determined directly by accepted "
            "project policy or committed by the person, role, or valid delegate with "
            "project decision authority",
            documented_routing,
        )
        self.assertNotIn(
            "D# contains a choice committed by project decision authority",
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
                    "accepted project policy determines that a limitation is acceptable "
                    "for the named completion boundary",
                    workflow_text,
                )
                self.assertIn(
                    "person, role, or valid delegate with project decision authority "
                    "explicitly accepts it",
                    workflow_text,
                )

        authority_adr = (
            REPOSITORY_ROOT
            / "architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md"
        ).read_text(encoding="utf-8")
        adr_decision = " ".join(
            authority_adr.split("## Decision", 1)[1]
            .split("## Consequences", 1)[0]
            .split()
        )
        for required in (
            "required evidence is sufficient",
            "accepted project policy determines the choice for that boundary",
            "person, role, or valid delegate with project decision authority commits it",
            "Dependent work stops while a required project choice remains uncommitted; "
            "independent work may continue",
            "actions authorized by the current user request or accepted project policy",
            "Authorization to perform an action does not commit a project choice",
            "A committed project choice does not authorize an unrelated action",
            "Host permission supplies neither",
            "A workflow or skill, its instructions, a test, specification, ticket, or "
            "Wayfinder record grants neither",
        ):
            with self.subTest(adr_boundary=required):
                self.assertIn(required, adr_decision)

        direct_choice_boundary = (
            "Dependent work stops while a required project choice remains uncommitted; "
            "independent work may continue"
        )
        for name, path in (
            ("managed root source", PACKAGE_ROOT / "payload/root/AGENTS.md.template"),
            ("readme", REPOSITORY_ROOT / "README.md"),
            (
                "authority decision",
                REPOSITORY_ROOT
                / "architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md",
            ),
        ):
            text = " ".join(path.read_text(encoding="utf-8").split())
            with self.subTest(direct_choice_boundary=name):
                self.assertIn(direct_choice_boundary, text)
                self.assertNotIn("unresolved project-choice boundary", text)

    def test_route_selection_loading_execution_and_completion_remain_distinct(
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
                "## Use selected skills",
                "## Preserve responsibilities and transitions",
                "## Report the executed route",
            )
        }
        for fragment in (
            "Choose Direct or one primary workflow",
            "supporting capabilities that materially help",
        ):
            self.assertIn(fragment, sections["## Decide and compose"])
        selected_skills = sections["## Use selected skills"]
        for fragment in (
            "exposed in the current session",
            "Read the selected skill's instructions",
            "Selecting a skill is not execution",
            "Route selection",
            "material execution",
            "completion and verification",
            "cannot run without explicit user invocation",
            "available capabilities can satisfy the request",
            "Never claim an unavailable skill ran",
        ):
            self.assertIn(fragment, selected_skills)
        for obsolete_abstraction in (
            "behavior-bearing",
            "user-only operation",
            "skill resolution",
            "installed availability",
            "skill prerequisites",
            "registry",
        ):
            self.assertNotIn(obsolete_abstraction, selected_skills)
        self.assertIn(
            "The specialist creates no Agent Workflow durable coordination state",
            sections["## Preserve responsibilities and transitions"],
        )
        reporting = sections["## Report the executed route"]
        self.assertIn("<skill>-handoff", reporting)
        self.assertIn("explicit user invocation remains required", reporting)

    def test_specialist_selection_has_material_boundaries(self) -> None:
        self._assert_optional_specialist_boundaries()

    def test_implementation_scope_carriers_are_precise_and_consistent(self) -> None:
        carrier = (
            "the current authorized request, selected Wayfinder map, current "
            "decision record, accepted specification, or approved durable ticket "
            "or ticket set"
        )

        detailed_routing = " ".join(
            (
                PACKAGE_ROOT / "payload/agent-workflow/routing.md"
            ).read_text(encoding="utf-8").split()
        )
        implementation = " ".join(
            (
                PACKAGE_ROOT / "payload/skills/workflow-implementation/SKILL.md"
            ).read_text(encoding="utf-8").split()
        )
        verification = " ".join(
            (
                PACKAGE_ROOT / "payload/skills/workflow-verification/SKILL.md"
            ).read_text(encoding="utf-8").split()
        )

        # Routing owns the detailed cross-workflow carrier contract.
        self.assertEqual(detailed_routing.count(carrier), 3)

        # Implementation enumerates the accepted carriers once at its input boundary.
        self.assertEqual(implementation.count(carrier), 1)

        for required in (
            "Resume from the accepted scope and verification evidence",
            "artifact references, dependencies, and ready work in Wayfinder",
            "plus any references to artifacts or records that maintain the scope",
            (
                "Invoke `workflow-verification` once with the accepted scope and "
                "its acceptance criteria"
            ),
            (
                "Remaining durable next work must be maintained in the selected "
                "Wayfinder map, accepted specification, or approved durable ticket "
                "or ticket set"
            ),
        ):
            self.assertIn(required, implementation)

        for required in (
            (
                "Selected skills supply their methods, terminology, and evidence. "
                "Wayfinder is Agent Workflow's sole durable coordinator and stores "
                "only consequential state and references."
            ),
            (
                "Specifications, tickets, research, maps, and reviews remain in the "
                "artifacts or records designated to maintain their results; external "
                "identifiers remain unchanged."
            ),
        ):
            self.assertIn(required, detailed_routing)

        # Verification consumes the already-established accepted scope rather than
        # redefining the complete carrier taxonomy.
        self.assertNotIn(carrier, verification)
        self.assertIn(
            "the accepted scope Implementation actually consumed",
            verification,
        )
        self.assertIn(
            "the accepted scope referenced by Implementation is the one actually consumed",
            verification,
        )
        self.assertIn(
            "integration boundaries, and expected artifacts",
            verification,
        )
        self.assertIn(
            "expected artifacts, and workflow completion",
            verification,
        )
        self.assertNotIn(
            "applicable compatibility behavior",
            verification,
        )

    def _assert_optional_specialist_boundaries(self) -> None:
        routing = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text().split()
        )
        required_boundaries = (
            "Discovery is the method for bounded consequential choice",
            "reorganizing the domain would materially improve",
            (
                "Interdependent choices requiring human input or project decision authority "
                "materially shape downstream work "
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
            (PACKAGE_ROOT / "payload/skills/wayfinder/SKILL.md").read_text().split()
        )
        self.assertIn("If the state contract is unavailable", runtime)
        self.assertIn("do not invent substitute persistence", runtime)

    def test_wayfinder_post_selection_loading_is_owned_by_skill_and_contract(
        self,
    ) -> None:
        root_policy = (
            PACKAGE_ROOT / "payload/root/AGENTS.md.template"
        ).read_text(encoding="utf-8")
        wayfinder_skill = " ".join(
            (PACKAGE_ROOT / "payload/skills/wayfinder/SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )
        state_contract = " ".join(
            (PACKAGE_ROOT / "payload/agent-workflow/contracts/wayfinder-state.md")
            .read_text(encoding="utf-8")
            .split()
        )
        normalized_root = " ".join(root_policy.split())

        self.assertNotIn("## Load state only when selected", root_policy)
        self.assertNotIn("Never seed state", root_policy)
        self.assertNotIn("read the state contract before effort state", normalized_root)
        self.assertIn(
            "When selecting or resuming Wayfinder, read the state contract before effort state",
            wayfinder_skill,
        )
        self.assertIn(
            "When resuming a Wayfinder effort, read `map.md` first among its effort files",
            wayfinder_skill,
        )
        self.assertIn("Load this state contract before effort state", state_contract)
        self.assertIn(
            "When resuming a Wayfinder effort, read `map.md` first",
            state_contract,
        )
        self.assertIn("Existing state is never a routing signal", state_contract)
        self.assertIn(
            "Selection may conclude that no consequential continuity earns persistence; "
            "in that case create no effort, map, or supporting record",
            wayfinder_skill,
        )

    def test_thin_router_is_direct_first_and_progressively_loaded(self) -> None:
        root_policy = (PACKAGE_ROOT / "payload/root/AGENTS.md.template").read_text()
        routing = (PACKAGE_ROOT / "payload/agent-workflow/routing.md").read_text()
        readme = (REPOSITORY_ROOT / "README.md").read_text()
        normalized_root = " ".join(root_policy.split())
        normalized_routing = " ".join(routing.split())
        normalized_readme = " ".join(readme.split())

        self.assertTrue(root_policy.startswith("# Agent Workflow\n"))
        self.assertNotIn("# Mandatory — no exceptions", root_policy)
        self.assertIn("MUST route every request", normalized_root)
        self.assertIn("Direct is default", normalized_root)
        self.assertIn(
            "first-pass selection from the current user intent and skill descriptions "
            "exposed in the session",
            normalized_root,
        )
        self.assertIn(
            "Topic overlap or skill availability alone does not select a specialist",
            normalized_root,
        )
        self.assertIn("Choose Direct or one primary workflow", normalized_root)
        self.assertIn(
            "supporting capabilities that materially help", normalized_root
        )
        self.assertIn("Re-evaluate the route when evidence changes", normalized_root)
        for removed_cue in (
            "unexplained causal failure",
            "consequential choice needing alternative analysis",
            "substantive sourced external uncertainty",
            "ready substantial change",
            "completed meaningful change",
        ):
            with self.subTest(removed_cue=removed_cue):
                self.assertNotIn(removed_cue, normalized_root)
        self.assertNotIn(
            "one obvious specialist inside an already selected Wayfinder effort",
            normalized_root,
        )
        self.assertIn(
            (
                "Read `.agent-workflow/routing.md` only when detailed composition, "
                "selected-skill availability or invocation, artifact or record "
                "responsibility, handoff, or durable resumption guidance materially matters"
            ),
            normalized_root,
        )
        self.assertIn(
            (
                "artifact or record responsibility is unclear or selected-skill "
                "availability, an exact invocation instruction, agent handoff, or "
                "durable resumption materially matters"
            ),
            normalized_routing,
        )
        self.assertIn(
            (
                "artifact or record responsibility or workflow composition is "
                "unclear, or selected-skill availability, an exact invocation "
                "instruction, agent handoff, or durable resumption materially matters"
            ),
            normalized_readme,
        )
        self.assertIn(
            "Assess durable coordination after any needed reconnaissance; item count alone "
            "never selects Wayfinder",
            normalized_root,
        )
        self.assertNotIn("Three or more meaningful items", normalized_root)
        self.assertIn("MUST select or resume Wayfinder", normalized_root)
        self.assertIn("any hard signal or at least two soft signals", normalized_root)
        self.assertIn(
            "Hard: cross-session continuation or agent-handoff continuity; conflicting "
            "sources that establish the same scoped claim; an uncommitted required project "
            "choice while independent work proceeds; coordinated responsible participants "
            "or areas; or source and scope needed to distinguish assumption from fact",
            normalized_root,
        )
        self.assertIn(
            "Soft: interacting consequential unresolved questions; durable distinctions "
            "across record or state categories; evidence-driven plan change; a meaningful "
            "dependency graph; or material fresh-agent reconstruction risk",
            normalized_root,
        )
        self.assertIn(
            "One isolated unresolved question and routine work use Direct or an "
            "applicable workflow",
            normalized_root,
        )
        self.assertIn("Honor explicit Wayfinder use and opt-out", normalized_root)
        self.assertIn("Read-only work changes no state", normalized_root)
        self.assertIn(
            "Existing state, including an unrelated map, never selects Wayfinder",
            normalized_root,
        )
        self.assertNotIn("\n* ", root_policy)
        self.assertNotIn(
            "If it is unclear whether the work is clearly bounded", normalized_root
        )
        self.assertNotIn("For a named skill, a resume", normalized_root)
        self.assertIn("avoid routing loops", normalized_routing.lower())
        self.assertIn("trivial low-risk edits stay direct", normalized_routing.lower())
        self.assertIn(
            "available capabilities can satisfy the request", normalized_routing
        )
        self.assertIn(
            "unavailable or cannot run without explicit user invocation",
            normalized_routing,
        )
        self.assertIn("After a successful Direct fallback", normalized_routing)
        self.assertIn("selection did not become equivalent execution", normalized_root)
        self.assertIn(
            "selection did not become equivalent execution", normalized_routing
        )
        self.assertIn("omit the skill that could not run", normalized_routing)
        self.assertNotIn("one obvious specialist inside Wayfinder", normalized_routing)
        self.assertIn(
            "A supporting skill creates no Agent Workflow durable coordination state",
            normalized_routing,
        )

        documented_routing = " ".join(
            (REPOSITORY_ROOT / "docs/routing.md")
            .read_text(encoding="utf-8")
            .split()
        )
        self.assertIn(
            "Assess durable coordination after any needed reconnaissance; item count "
            "alone never selects Wayfinder",
            documented_routing,
        )
        self.assertNotIn("Three or more meaningful items", documented_routing)

    def test_detailed_router_defers_global_policy_to_the_root(self) -> None:
        routing = (
            PACKAGE_ROOT / "payload/agent-workflow/routing.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(routing.split())

        self.assertIn(
            "Root rules for action authorization, project decision authority, "
            "preservation, and reporting remain binding",
            normalized,
        )
        for root_owned_restatement in (
            "Execute only actions authorized by the current user request",
            "Do not treat a consequential project choice as committed until",
            "Choose skills from the descriptions exposed in the current session",
            "Direct work remains subject to the current request's or accepted project "
            "policy's action authorization",
            "counts trigger assessment, never selection",
            "Explicit Wayfinder use and opt-out control the route",
        ):
            with self.subTest(root_owned_restatement=root_owned_restatement):
                self.assertNotIn(root_owned_restatement, normalized)

        for route_specific_behavior in (
            "This table resolves overlaps",
            "Resume only relevant work",
            "After selecting Wayfinder, read `contracts/wayfinder-state.md`, then the map",
            "Avoid routing loops",
            "If a selected skill is unavailable",
            "stop with `<skill>-blocked`",
            "Use compact labels",
            "Use a terminal suffix only when selection did not become equivalent execution",
        ):
            with self.subTest(route_specific_behavior=route_specific_behavior):
                self.assertIn(route_specific_behavior, normalized)


if __name__ == "__main__":
    unittest.main()
