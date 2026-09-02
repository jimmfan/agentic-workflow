<!-- agent-workflow:managed-begin -->
# Agent Workflow

- MUST route every request. Direct is default. Make first-pass selection from
  the current user intent and skill descriptions exposed in the session. Topic
  overlap or skill availability alone does not select a specialist.
- When evidence is insufficient to select or re-evaluate the route, perform only
  the smallest read-only reconnaissance within the scope delegated by the current
  user request or accepted project policy.
- Choose Direct or one primary workflow; add only supporting capabilities that
  materially help. Re-evaluate the route when evidence changes.
- Read `.agent-workflow/routing.md` only when detailed composition,
  selected-skill availability or invocation, artifact or record responsibility,
  handoff, or durable resumption guidance materially matters.
- Treat a consequential project choice as committed only when required evidence
  is sufficient and either accepted project policy determines the choice for
  its boundary or the person, role, or valid delegate with project decision
  authority commits it. Evidence-backed technical judgment already delegated by
  the user or accepted project policy remains valid. Responsibility alone does
  not establish project decision authority. Dependent work stops while a
  required project choice remains uncommitted; independent work may continue.
  If accepted project policy does not determine a required choice, obtain it
  from the person, role, or valid delegate with that authority. If authority is
  unclear, identify the concrete question, who may decide, why the choice is
  required, and what it unblocks.
  Revisit a committed choice only for conflict, safety, project decision
  authority, or request.
- Perform writes, commands, publication, destructive operations, and external
  mutations only when the current user request or accepted project policy
  authorizes that action and scope. An exact external read-only target authorizes
  only that read. When both the required project choice is committed and the
  action is authorized, affected work may proceed only within the authorized scope.
  Action authorization does not commit a project choice. A committed project
  choice does not authorize an unrelated action. Host permission supplies
  neither. Workflows, skills and their instructions, tests, specifications,
  tickets, and Wayfinder records supply neither.
- The person, role, or valid delegate with project decision authority may
  explicitly accept unresolved uncertainty for one named boundary. The question
  remains unresolved; only that boundary becomes unblocked, no broader project
  choice is committed, no unrelated action is authorized, and no other
  dependency is satisfied.
- Never claim unexecuted work.
- Preserve unrelated work, project-owned state, designated artifacts, and
  identifiers.
  Live source and accepted artifacts outrank summaries, memory, and chat.
- Do not manufacture cross-artifact conflicts or parallel representations of
  the same current state. Differences in scope, abstraction, summarization, or
  omitted detail are not by themselves conflicts. Reconcile only a concrete
  incompatible statement or an unmet requirement. Update the artifact or record
  that maintains current state instead of creating a competing representation
  unless the new representation has independently useful meaning, scope, or
  retrieval value. When materially ambiguous, preserve the existing content and
  clarify or investigate rather than inventing detail or process merely to make
  artifacts agree.

## When to use Wayfinder

Assess durable coordination after any needed reconnaissance.
Unless the user opts out, MUST select or resume Wayfinder when any hard signal
or at least two soft signals apply:

- Hard: the current work continues a relevant Wayfinder effort, is intended to
  continue across sessions or agents, establishes or materially changes a plan
  that later work is expected to execute or depend on, or establishes
  consequential context needed by later work before the effort's objective is
  achieved; conflicting sources that establish the same scoped claim; an
  uncommitted required project choice while independent work proceeds;
  coordinated responsible participants or areas; or source and scope needed to
  distinguish assumption from fact.
- Soft: interacting consequential unresolved questions; durable distinctions
  across record or state categories; evidence-driven plan change; a meaningful
  dependency graph; or material fresh-agent reconstruction risk.

A material update to an existing durable planning artifact for unfinished work
may indicate continuation of an existing Wayfinder effort. Use detailed routing
for the bounded read-only check needed to determine whether one relevant effort
clearly matches.

One isolated unresolved question and routine work use Direct or an applicable
workflow. Honor explicit Wayfinder use and opt-out. Read-only work changes no
state. Existing Wayfinder state alone never selects Wayfinder. A bounded read-only
check may establish that the current work clearly continues a relevant effort;
unrelated efforts never change the route.

## Report the route

End each user-facing final response with exactly one truthful
`[route: router → <executed path or terminal outcome>]` line. Report only what
executed; use `direct` if no workflow or skill ran. If selection did
not become equivalent execution, report the routing policy's terminal outcome.
Never reroute or work merely to produce the marker.
<!-- agent-workflow:managed-end -->
## External action notifications

When progress is blocked on an action the user must take outside the agent
session—such as trusting a workspace, approving a permission, authenticating,
or clicking a UI control—say so immediately. State that the blocked step cannot
continue, name the exact app, window, and control, give the single exact action
required and what it unblocks, and ask the user to confirm when complete.
Explicitly say when the action has taken effect or is no longer needed.

# Agent Workflow source repository

These source-repository instructions apply specifically to agents modifying the
Agent Workflow source repository.

## Project language

Read `CONTEXT.md` before changing routing, Wayfinder, direct skill distribution,
ownership, or framework-lifecycle concepts in a way that uses or changes
canonical project language.

Before introducing, renaming, or materially redefining a canonical term,
determine the actual concept from current source, behavior, tests, and accepted
decisions; identify the bounded technical or domain context that owns it;
research established terminology using applicable primary standards, official
technical documentation, strong engineering evidence, and peer-reviewed
evidence when available; compare alternatives by exact semantics and
applicability; prefer established or literal language only when its semantic
precision earns its cognitive cost; and state evidence strength and uncertainty
honestly.

Update `CONTEXT.md` only after the terminology decision is accepted. Keep
behavior, architecture, authority, and terminology in their respective owning
layers. Do not force one term across genuinely different bounded contexts.

## Pre-1.0 engineering priority

- Agent Workflow is pre-1.0. Prioritize protecting project-owned and user-owned
  durable data, preserving authorization and safe-delivery boundaries, and
  making core routing behavior reliable.
- Outside those boundaries, prefer simple, replaceable designs over speculative
  robustness or machinery for hypothetical future needs.

## Scope

- Do not copy source-repository maintenance instructions into consuming
  projects.
- Do not modify downstream consuming projects unless the task explicitly
  includes a migration, adoption test, or disposable compatibility test
  involving them.

## Architectural decisions

- Accepted, non-superseded records under `architecture-decisions/` govern the
  boundaries they address. Do not silently bypass or reinterpret them. For
  substantial changes, read the applicable decisions rather than the entire
  decision history.
- If an ADR and current repository behavior appear inconsistent, investigate
  the discrepancy. If new evidence changes an accepted decision, update the ADR
  and affected contracts, implementation, documentation, and tests explicitly.
- Keep ADRs for architecturally significant choices that can reasonably be
  reconsidered independently and whose rationale would otherwise be lost.
  Before adding one, check whether an existing ADR already owns the boundary.
  Put current system shape in `docs/architecture.md` and exact required behavior
  in contracts, source, and tests.
- Do not use ADRs merely to record experiments, bug fixes, dependency or version
  updates, numeric limits, path cleanup, benchmark results, or routine
  implementation mechanics. During explicit ADR maintenance, consolidate or
  remove obsolete pre-1.0 records rather than keeping them as a changelog; Git
  preserves historical evolution.

## Architecture boundary

- Agent Workflow is a thin orchestration layer. Keep it centered on routing,
  direct skill distribution, safe framework delivery, authorization boundaries,
  durable coordination Agent Workflow defines, and integration
  verification.
- Prefer existing host or curated skill capabilities and accepted artifacts that
  maintain lasting results over parallel Agent Workflow representations or
  lightly rewritten upstream functionality.
- Remove or simplify machinery that lacks a current justification. Do not add
  package-manager-grade integrity, compatibility, migration, deprecation,
  observability, ownership registries, or lifecycle systems, and do not expand
  Agent Workflow into a general agent runtime, package manager, plugin platform,
  or compatibility framework, unless a concrete current need, durable-data or
  safety requirement, or current external contract requires it.

## Project data preservation

- Do not overwrite, discard, conceal, or normalize away unrelated user changes.
- Protect project-owned and user-owned durable state. Reconstructable framework
  output may be replaced when appropriate; durable state must not be treated as
  reconstructable framework content.
- Define Agent Workflow's own data-preservation boundaries instead of relying on
  host or model defaults. Do not duplicate generic host or model safety policy
  unless Agent Workflow introduces a specific risk that requires a project-owned
  rule.

## Working practice

For substantial changes:

- Inspect the current implementation, repository status, exact worktree,
  branch, base, and relevant diff.
- Read the applicable contracts and architectural decisions and determine which
  layer owns the behavior.
- Check whether an existing host capability or skill exposed in the current
  session already provides the needed behavior.
- Prefer the smallest coherent and reversible change that preserves accepted
  behavior.
- Update tests and durable documentation when the resulting contract changes.

Use current primary sources when an evolving external integration materially
affects the work.

Keep experiments reversible and isolated until adoption is intentional.

## Testing and verification

- Test Agent Workflow's contracts and boundaries rather than reproducing
  distributed-skill internals.
- Prefer deterministic tests for normal development. Keep live-agent evaluation
  opt-in, benchmark-specific, scheduled, or release-gated.
- Follow `docs/verification.md` and the applicable evaluation documentation for
  required checks and execution procedures.
- Report verification truthfully. If a relevant test, platform, integration,
  workflow, or external behavior was not actually exercised, say so. Separate
  product behavior from harness, evaluator, fixture, authentication, quota,
  timeout, permission, host, and other infrastructure failures.
- Do not regenerate or modify derived metadata merely to make an unexplained
  difference disappear.
