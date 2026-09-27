# Workflow responsibility boundaries

## Objective

Keep consequential questions and follow-up work concerning Agent Workflow's routing, workflow, specialist, artifact, and durable-state responsibility boundaries understandable and resumable as the framework evolves.

## Scope

Responsibility selection, method composition, handoffs, artifact and persistence ownership, and the authority and evidence boundaries that affect them.
The initial task authorizes a source-grounded audit and this effort state, with no framework, architecture-documentation, test, evaluator, or runtime changes and no live evaluation.
On 2026-09-27 jimmfan authorized the routing-audit changes on branch `codex/routing-audit-improvements` (`VERSION` 0.37.0), including pushing that branch; opening a PR was not requested.

Resume when an authorized request materially affects a represented boundary, question, or evidence claim.
Inspect changed sources and reconcile only affected coordination within that request's scope; this map is not self-updating and its existence does not select Wayfinder or require an audit of unrelated work.
The [architecture overview](../../docs/architecture.md) maintains lasting system shape; canonical instructions maintain behavior.
This effort does not maintain a second routing specification, skill catalog, evaluation campaign, or general architecture backlog.

## Ready work

No further framework change is ready.
The Debugging handoff below shipped in [PR #59](https://github.com/jimmfan/agentic-workflow/pull/59) with release 0.36.0.
The routing-audit changes below are on the pushed branch `codex/routing-audit-improvements` and await a PR and review.

## Current state

The inspected root policy, routing, state contract, distributed skill instructions, and accepted ADRs establish the ownership relationships summarized below.
The initial audit (2026-09-17) found no contradictory ownership assignment.

**Debugging-to-build transition (source analysis, 2026-09-27).**
The sources show a coverage gap for authorized fixes that aren't trivial, not a contradiction:

- [Debugging's fix guidance](../../.agents/skills/workflow-debugging/SKILL.md#fix-and-verify) sent every authorized fix directly to Verification and, before the 2026-09-27 change, had never named an Implementation handoff; its "do not duplicate Code Review already performed by `implement`" clause originated as a reference to an upstream `implement` run.
- [Detailed routing](../../.agent-workflow/routing.md#decide-and-compose) routes a ready implementation scope through Implementation and `implement` and keeps trivial low-risk edits Direct, but names only the reverse transition ("new causal uncertainty returns to Debugging").
- [Verification](../../.agents/skills/workflow-verification/SKILL.md) assesses existing TDD and Code Review evidence and adds only uncovered checks; it does not supply a closing review when none ran.
- [ADR-0027](../../architecture-decisions/0027-use-direct-first-progressive-routing.md) treats route sequences as entry-conditioned default transitions, and detailed routing loads only when needed, so Debugging's explicit step is the instruction most likely in context at the fix.

On the Debugging path, closing review of an authorized fix that isn't trivial therefore depends on the agent re-classifying the fix as an implementation scope without an instruction that says to.
The [existing investigation](../../evals/remaining-audit-behavior/REPORT.md#h2--debuggings-transition-may-omit-meaningful-closing-review) observed exactly that omission, but its attribution remains inconclusive; source analysis cannot establish present agent behavior or that the recommended change would alter it.

**Resolution (approved 2026-09-27, delivered in PR #59).**
Debugging's fix guidance now has a conditional handoff.
A trivial low-risk causal fix keeps the current path: apply it and invoke Verification.
A fix that isn't trivial hands the smallest causal fix to Implementation as one ready scope, with the diagnosed cause, regression seam, and original symptom or honest proxy as acceptance; Implementation then owns `implement` (TDD and closing Code Review) and Verification.
This reuses routing's existing trivial/meaningful boundary and adds no new pipeline, record, or test.
Rejected alternatives:

- **No change:** relies on a routing re-evaluation that no instruction on the Debugging path triggers, that Debugging's explicit Verification step likely preempts, and that the investigation did not observe.
- **Routing-only transition row:** routing may not be loaded at the fix, and the investigated subject read routing and still went Debugging → Verification.
- **Debugging invokes `code-review` itself:** bypasses `implement`'s pre-edit baseline and TDD and creates a parallel build path, contrary to `implement` owning closing review.
- **Verification requires a missing review:** moves review into the acceptance layer for every Verification use.

The package gate passed on the applied change; its closing Code Review ran inline in the implementing session rather than through independent reviewers.
Revisit if a clean rerun of the investigation shows agents already reach Implementation from Debugging, or shows the handoff adds ceremony to fixes that are actually trivial.

**Routing-audit changes (authorized by jimmfan 2026-09-27, branch `codex/routing-audit-improvements`).**
[Detailed routing](../../.agent-workflow/routing.md#decide-and-compose) prefers a curated skill over an overlapping host skill unless the user names the other one, and [route reporting](../../.agent-workflow/routing.md#report-the-executed-route) adds a `<skill>-incomplete` outcome for a skill that started but did not finish; Code Review treats a failed reviewer as an incomplete axis.
The root policy keeps all its Wayfinder signals and now states that explicit use or opt-out overrides them and that a hard signal overrides the isolated-question default.
jimmfan chose this on 2026-09-27 over removing two hard signals, because the recorded incidents are mostly missed coordination and the [cited research](../context-efficiency/map.md#current-state) identifies ambiguous decision points and uncorrected early decisions as common failures.
A proposed limit on re-entering the same workflow was dropped the same day because no such loop has been observed.
No live run has checked whether agents follow these rules.

The [campaign effort](../remaining-behavior-evidence/map.md) and its linked protocol/report retain execution prerequisites, observations, and follow-up details; do not mirror their campaign state here.

## Areas and relationships

- **Selection and composition:** the [root policy](../../agent_workflow/install/AGENTS.md.template) owns first-pass routing, Direct defaults, Wayfinder selection, and the rules for authorization and project decision authority.
  [Detailed routing](../../.agent-workflow/routing.md) owns composition, transitions, relevant resumption, and selected-skill availability; specialists supply their methods rather than an alternative router.
- **Coordination and representation:** [Wayfinder](../../.agents/skills/wayfinder/SKILL.md) owns effort orientation, question navigation, method selection within the effort, and consequential handoffs.
  Its [state contract](../../.agent-workflow/contracts/effort-state.md) owns recognition, map authoring, selective records, reconciliation, preservation, pruning safeguards, and ending; the [records contract](../../.agent-workflow/contracts/effort-records.md) owns U/E/F/D formats, identifiers, and single-record pruning.
  The [Wayfinder Effort entry point](../../.agents/skills/wayfinder-effort/SKILL.md) establishes or updates effort state without product implementation.
- **Investigation and choices:** [Debugging](../../.agents/skills/workflow-debugging/SKILL.md) establishes causes; [Research](../../.agents/skills/research/SKILL.md) supplies primary-source evidence; [Discovery](../../.agents/skills/workflow-discovery/SKILL.md) analyzes bounded choices; [Grilling](../../.agents/skills/grilling/SKILL.md) sequences interdependent human choices; [Prototype](../../.agents/skills/prototype/SKILL.md) answers questions through throwaway interactive exploration.
  Their results inform authorized next work without granting project decision authority, production adoption, or execution authorization.
- **Model and design boundaries:** [Domain Modeling](../../.agents/skills/domain-modeling/SKILL.md) maintains the project's domain/context model, while [Codebase Design](../../.agents/skills/codebase-design/SKILL.md) supplies module-interface and test-seam vocabulary.
  Neither owns all project structure or Wayfinder's effort view; [canonical framework terminology](../../.agent-workflow/terminology.md) separately maintains Agent Workflow meanings under [ADR-0029](../../architecture-decisions/0029-distribute-canonical-framework-terminology.md).
- **Build and acceptance:** [Implementation](../../.agents/skills/workflow-implementation/SKILL.md) consumes one ready authorized scope, invokes [implement](../../.agents/skills/implement/SKILL.md), then [Verification](../../.agents/skills/workflow-verification/SKILL.md), and reconciles consequential outcomes into the selected effort state when authorized.
  `implement` owns the build loop, agreed-seam [TDD](../../.agents/skills/tdd/SKILL.md) where possible, and closing [Code Review](../../.agents/skills/code-review/SKILL.md); Code Review independently assesses Standards and Spec.
  Verification adds uncovered acceptance and integration evidence, reuses existing checks, and owns the completion gate rather than repeating the build or review.
- **Lasting results:** [to-spec](../../.agents/skills/to-spec/SKILL.md) synthesizes accepted scope; [to-tickets](../../.agents/skills/to-tickets/SKILL.md) produces dependency-aware work slices.
  Authorized durable specifications, tickets, research results, reviews, and architecture decisions remain in their designated maintaining artifacts; chat-only drafts remain session-local.
  Wayfinder links those results and does not mirror ticket readiness or specialist procedures, as required by [ADR-0028](../../architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md).
- **Evidence and preservation:** [test ownership](../../tests/README.md) distinguishes actual filesystem/Git observations from structural guards and synthetic evaluator controls.
  The removed [specialist reconciliation tests](https://github.com/jimmfan/agentic-workflow/blob/92d3304473b0fbebdcb6ab08b41bbad1d9710a50/tests/test_specialist_reconciliation.py) remain historical evidence only; their substring checks did not prove instruction meaning, agent ordering or execution.
  [ADR-0010](../../architecture-decisions/0010-separate-framework-output-from-project-owned-state.md) keeps effort state project-owned and outside lifecycle traversal and mutation; safe effort state changes remain governed by the state contract.

## Dependencies

Merging the routing-audit branch needs a PR, which jimmfan has not yet requested.
Any effectiveness claim for the handoff needs actual execution evidence under the [existing protocol](../../evals/remaining-audit-behavior/README.md); the map must not claim it.
Reusing campaign observations requires retaining their original scope and limitations.

## Blockers

Merging `codex/routing-audit-improvements` waits only on a PR and review.
Live evaluation remains blocked by the campaign's unresolved execution-isolation limitations; consult its current maintaining artifacts before proposing a live continuation.

## Key references

- [Architecture and ownership](../../docs/architecture.md) — lasting system overview and applicable ADRs.
- [Detailed routing](../../.agent-workflow/routing.md) — current selection overlaps and transitions.
- [Effort state contract](../../.agent-workflow/contracts/effort-state.md) — map and supporting-state mechanics.
- [Coverage and evidence limits](../../tests/README.md#wayfinder-coverage-and-evidence-limits) — what existing controls do and do not establish.
- [Remaining behavior evidence effort](../remaining-behavior-evidence/map.md) — existing campaign continuation and its maintaining report.
