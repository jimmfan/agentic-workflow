# Workflow responsibility boundaries

## Objective

Keep consequential questions and follow-up work concerning Agent Workflow's routing, workflow, specialist, artifact, and durable-state responsibility boundaries understandable and resumable as the framework evolves.

## Scope

Responsibility selection, method composition, handoffs, artifact and persistence ownership, and the authority and evidence boundaries that affect them.
The initial task authorizes a source-grounded audit and this effort state, with no framework, architecture-documentation, test, evaluator, or runtime changes and no live evaluation.

Resume when an authorized request materially affects a represented boundary, question, or evidence claim.
Inspect changed sources and reconcile only affected coordination within that request's scope; this map is not self-updating and its existence does not select Wayfinder or require an audit of unrelated work.
The [architecture overview](../../docs/architecture.md) maintains lasting system shape; canonical instructions maintain behavior.
This effort does not maintain a second routing specification, skill catalog, evaluation campaign, or general architecture backlog.

## Ready work

The initial source audit is complete; no further framework change or live evaluation is authorized by that task.
Proposed follow-up is to resolve the meaningful Debugging-to-build transition question below, reusing the existing campaign's evidence and obtaining an authorized scope before changing instructions or running evaluations.
The proposal is not an implementation-ready assignment.

## Current state

The inspected root policy, routing, state contract, distributed skill instructions, and accepted ADRs establish the ownership relationships summarized below.
This audit did not establish a new contradictory ownership assignment or justify a framework correction.
One consequential transition remains worth investigating:

**When does an authorized meaningful repair leave Debugging for Implementation, and how is closing review ensured?**
[Debugging's fix guidance](../../.agents/skills/workflow-debugging/SKILL.md#fix-and-verify) says to apply the smallest causal fix and invoke Verification, while [detailed routing](../../.agent-workflow/routing.md#decide-and-compose) routes a ready implementation scope through Implementation and `implement`, with a Direct exception for trivial edits.
The explicit Debugging guidance does not name that handoff.
Whether general routing re-evaluation sufficiently resolves this transition is an interpretation to investigate, not an established contract defect or a requirement that every fix invoke `implement`.

The [existing meaningful-fix investigation](../../evals/remaining-audit-behavior/REPORT.md#h2--debuggings-transition-may-omit-meaningful-closing-review) already records a correct repair without observed independent closing review.
Its infrastructure and reviewer-capability limitations leave attribution inconclusive; this audit did not rerun it or establish present-day agent behavior.
The [campaign effort](../remaining-behavior-evidence/map.md) and its linked protocol/report retain execution prerequisites, observations, and follow-up details; do not mirror their campaign state here.

## Areas and relationships

- **Selection and composition:** the [root policy](../../agent_workflow/install/AGENTS.md.template) owns first-pass routing, Direct defaults, Wayfinder selection, and the rules for authorization and project decision authority.
  [Detailed routing](../../.agent-workflow/routing.md) owns composition, transitions, relevant resumption, and selected-skill availability; specialists supply their methods rather than an alternative router.
- **Coordination and representation:** [Wayfinder](../../.agents/skills/wayfinder/SKILL.md) owns effort orientation, question navigation, method selection within the effort, and consequential handoffs.
  Its [state contract](../../.agent-workflow/contracts/wayfinder-state.md) owns recognition, map authoring, selective records, reconciliation, preservation, pruning, and ending.
  The [Wayfinder Effort entry point](../../.agents/skills/wayfinder-effort/SKILL.md) establishes or updates effort state without product implementation.
- **Investigation and choices:** [Debugging](../../.agents/skills/workflow-debugging/SKILL.md) establishes causes; [Research](../../.agents/skills/research/SKILL.md) supplies primary-source evidence; [Discovery](../../.agents/skills/workflow-discovery/SKILL.md) analyzes bounded choices; [Grilling](../../.agents/skills/grilling/SKILL.md) sequences interdependent human choices; [Prototype](../../.agents/skills/prototype/SKILL.md) answers questions through throwaway interactive exploration.
  Their results inform authorized next work without granting project decision authority, production adoption, or execution authorization.
- **Model and design boundaries:** [Domain Modeling](../../.agents/skills/domain-modeling/SKILL.md) maintains the project's domain/context model, while [Codebase Design](../../.agents/skills/codebase-design/SKILL.md) supplies module-interface and test-seam vocabulary.
  Neither owns all project structure or Wayfinder's effort view; [canonical framework terminology](../../.agent-workflow/terminology.md) separately maintains Agent Workflow meanings under [ADR-0029](../../architecture-decisions/0029-distribute-canonical-framework-terminology.md).
- **Build and acceptance:** [Implementation](../../.agents/skills/workflow-implementation/SKILL.md) consumes one ready authorized scope, invokes [implement](../../.agents/skills/implement/SKILL.md), then [Verification](../../.agents/skills/workflow-verification/SKILL.md), and reconciles consequential outcomes into selected Wayfinder state when authorized.
  `implement` owns the build loop, agreed-seam [TDD](../../.agents/skills/tdd/SKILL.md) where possible, and closing [Code Review](../../.agents/skills/code-review/SKILL.md); Code Review independently assesses Standards and Spec.
  Verification adds uncovered acceptance and integration evidence, reuses existing checks, and owns the completion gate rather than repeating the build or review.
- **Lasting results:** [to-spec](../../.agents/skills/to-spec/SKILL.md) synthesizes accepted scope; [to-tickets](../../.agents/skills/to-tickets/SKILL.md) produces dependency-aware work slices.
  Authorized durable specifications, tickets, research results, reviews, and architecture decisions remain in their designated maintaining artifacts; chat-only drafts remain session-local.
  Wayfinder links those results and does not mirror ticket readiness or specialist procedures, as required by [ADR-0028](../../architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md).
- **Evidence and preservation:** [test ownership](../../tests/README.md) distinguishes actual filesystem/Git observations from structural guards and synthetic evaluator controls.
  [Specialist reconciliation tests](../../tests/test_specialist_reconciliation.py) guard owning-layer instructions but do not prove agent ordering or execution.
  [ADR-0010](../../architecture-decisions/0010-separate-framework-output-from-project-owned-state.md) keeps effort state project-owned and outside lifecycle traversal and mutation; safe Wayfinder state changes remain governed by the state contract.

## Dependencies

Any proposed transition clarification needs a bounded authorized scope, current source comparison, and evidence sufficient for the claimed change.
Reusing campaign observations requires retaining their original scope and limitations; new behavioral claims require actual execution evidence under the [existing protocol](../../evals/remaining-audit-behavior/README.md).
The protocol's isolation and reviewer-capability prerequisites apply to its live work, not to independent source analysis or this map's completion.

## Blockers

No unresolved source or authority question prevents completing this initial audit and effort state.
Framework changes and live evaluations remain outside its authorization.
The existing campaign documents unresolved execution-isolation limitations; consult its current maintaining artifacts before proposing a live continuation rather than assuming that environment is now usable.
That limitation does not establish a framework defect or block independent documentation analysis.

## Key references

- [Architecture and ownership](../../docs/architecture.md) — lasting system overview and applicable ADRs.
- [Detailed routing](../../.agent-workflow/routing.md) — current selection overlaps and transitions.
- [Wayfinder state contract](../../.agent-workflow/contracts/wayfinder-state.md) — map and supporting-state mechanics.
- [Coverage and evidence limits](../../tests/README.md#wayfinder-coverage-and-evidence-limits) — what existing controls do and do not establish.
- [Remaining behavior evidence effort](../remaining-behavior-evidence/map.md) — existing campaign continuation and its maintaining report.
