# Workflow responsibility boundaries

## Objective

Keep consequential questions and follow-up work concerning Agent Workflow's routing, workflow, specialist, artifact, and durable-state responsibility boundaries understandable and resumable as the framework evolves.

## Scope

Responsibility selection, method composition, handoffs, artifact and persistence ownership, and the authority and evidence boundaries that affect them.
The initial task authorized a source-grounded audit and this effort state, with no framework, architecture-documentation, test, evaluator, or runtime changes and no live evaluation.
jimmfan later authorized the framework changes delivered in [PR #59](https://github.com/jimmfan/agentic-workflow/pull/59) (0.36.0) and [PR #60](https://github.com/jimmfan/agentic-workflow/pull/60) (0.37.0), both on 2026-09-27.
On 2026-09-29 jimmfan authorized committing and pushing the selection-focused skill descriptions in 0.38.0 to a branch.

Resume when an authorized request materially affects a represented boundary, question, or evidence claim.
Inspect changed sources and reconcile only affected coordination within that request's scope; this map is not self-updating and its existence does not select Wayfinder or require an audit of unrelated work.
The [architecture overview](../../docs/architecture.md) maintains lasting system shape; canonical instructions maintain behavior.
This effort does not maintain a second routing specification, skill catalog, evaluation campaign, or general architecture backlog.

## Ready work

No framework change is ready.
Checking whether agents follow the boundaries below needs live evidence, which is blocked as described under Blockers.

## Current state

The initial audit (2026-09-17) found no contradictory ownership assignment in the root policy, routing, state contract, distributed skill instructions, and accepted ADRs.

**Debugging-to-build handoff (approved 2026-09-27, shipped in PR #59).**
Before the change, closing review of an authorized fix that isn't trivial depended on the agent re-classifying the fix as an implementation scope with no instruction telling it to, and the [existing investigation](../../evals/remaining-audit-behavior/REPORT.md#h2--debuggings-transition-may-omit-meaningful-closing-review) observed that omission with inconclusive attribution.
[Debugging's fix guidance](../../.agents/skills/workflow-debugging/SKILL.md#fix-and-verify) now keeps a trivial low-risk causal fix on the direct path to Verification and hands any other fix to Implementation as one ready scope, with the diagnosed cause, regression seam, and original symptom or honest proxy as acceptance.
It reuses routing's existing trivial/meaningful boundary and adds no pipeline, record, or test.
Rejected alternatives:

- **No change:** relies on a routing re-evaluation that nothing on the Debugging path triggers, that Debugging's explicit Verification step likely preempts, and that the investigation did not observe.
- **Routing-only transition row:** routing may not be loaded at the fix, and the investigated subject read routing and still went Debugging → Verification.
- **Debugging invokes `code-review` itself:** bypasses `implement`'s pre-edit baseline and TDD and creates a parallel build path, contrary to `implement` owning closing review.
- **Verification requires a missing review:** moves review into the acceptance layer for every Verification use.

That change's closing Code Review ran inline rather than through independent reviewers.
Revisit if a clean rerun of the investigation shows agents already reach Implementation from Debugging, or shows the handoff adds ceremony to fixes that are actually trivial.

**Routing audit (shipped in PR #60).**
A curated skill is preferred over an overlapping host skill unless the user names the other one; since 0.40.0 the [root policy](../../agent_workflow/install/AGENTS.md.template) carries that rule instead of detailed routing.
[Route reporting](../../.agent-workflow/routing.md#report-the-executed-route) has a `<skill>-incomplete` outcome for a skill that started but did not finish.
Code Review treats a failed reviewer as an incomplete axis.
The root policy keeps all its Wayfinder signals and states that explicit use or opt-out overrides them and that a hard signal overrides the isolated-question default.
jimmfan chose this on 2026-09-27 over removing two hard signals, because the recorded incidents are mostly missed coordination and the [cited research](../context-efficiency/map.md#current-state) identifies ambiguous decision points and uncorrected early decisions as common failures.
A proposed limit on re-entering the same workflow was dropped the same day because no such loop has been observed.

**Selection descriptions (0.38.0).**
The `implement`, `workflow-implementation`, `workflow-discovery`, and `wayfinder-effort` descriptions now say when to use each skill and name the nearest alternative, leaving ownership detail to the skill bodies.
Routing states that the `implement` route label covers the Implementation integration, an `implement` run on its own, or both.

**Route-conflict fixes (0.40.0).**
After a 2026-10-01 review of selection and handoff rules that pointed nowhere or loaded too late, jimmfan approved moving curated-skill precedence into the root policy so it applies at first-pass selection.
After an independent audit, jimmfan also chose on 2026-10-01 to keep `wayfinder-effort` the easy prompt for creating, resuming, or refreshing an effort without product changes, while carrying out ready work stays with `wayfinder`.
On hosts that start sub-agents only on request, `implement` now asks before editing so one answer covers its whole scope, and a declined Code Review is reported as blocked.
Git history for 0.40.0 maintains the full change list.

On 2026-10-01 jimmfan also closed the review's finding that no step owned refactoring: [TDD](../../.agents/skills/tdd/SKILL.md#rules-of-the-loop) may refactor the code a cycle touched once tests pass, and [`implement`](../../.agents/skills/implement/SKILL.md) fixes plain defects that [Code Review](../../.agents/skills/code-review/SKILL.md) now reports and applies justified judgement calls in the code its scope changed, while Code Review stays read-only.
Checking this live needs two contrasting cases: a warranted local cleanup the agent should make, and a tempting broader rewrite it should defer.

No live run has checked whether agents follow any of these changes.
The [campaign effort](../remaining-behavior-evidence/map.md) and its linked protocol and report keep execution prerequisites, observations, and follow-up details; do not mirror their campaign state here.

## Areas and relationships

- **Selection and composition:** the [root policy](../../agent_workflow/install/AGENTS.md.template) owns first-pass routing, curated-skill precedence, Direct defaults, Wayfinder selection, and the rules for authorization and project decision authority.
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

Any effectiveness claim for these boundaries needs actual execution evidence under the [existing protocol](../../evals/remaining-audit-behavior/README.md); the map must not claim it.
Reusing campaign observations requires retaining their original scope and limitations.

## Blockers

Live evaluation remains blocked by the campaign's unresolved execution-isolation limitations; consult its current maintaining artifacts before proposing a live continuation.

## Key references

- [Architecture and ownership](../../docs/architecture.md) — lasting system overview and applicable ADRs.
- [Detailed routing](../../.agent-workflow/routing.md) — current selection overlaps and transitions.
- [Effort state contract](../../.agent-workflow/contracts/effort-state.md) — map and supporting-state mechanics.
- [Coverage and evidence limits](../../tests/README.md#wayfinder-coverage-and-evidence-limits) — what existing controls do and do not establish.
- [Remaining behavior evidence effort](../remaining-behavior-evidence/map.md) — existing campaign continuation and its maintaining report.
