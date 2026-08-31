<!-- agent-workflow:managed-begin -->
# Mandatory — no exceptions

- MUST route every request. Direct is default; clear intent or an applicable
  skill selects a workflow.
- Use cues when the method materially helps; encountering the topic alone never
  forces a specialist:
  - unexplained causal failure → consider Debugging
  - consequential choice needing alternative analysis → consider Discovery
  - substantive sourced external uncertainty → consider Research
  - ready substantial change → Implementation
  - completed meaningful change → Verification
  - durable coordination across session continuations, agent handoffs,
    responsible participants, or interacting state → assess Wayfinder using the
    criteria below
- For one obvious specialist inside an already selected Wayfinder effort, load
  only what it needs.
  Read `.agent-workflow/routing.md` only when artifact responsibility is unclear or selected-skill
  fallback, invocation instruction, agent handoff, or durable resumption
  materially matters.
- Do not treat a consequential project choice as committed until required
  evidence is sufficient and either accepted project policy determines the
  choice for that boundary or the person, role, or valid delegate with project
  decision authority commits it. Technical judgment already delegated by the
  user or accepted project policy remains valid. Dependent work stops while a
  required project choice remains uncommitted; independent work may continue.
- Perform writes, commands, publication, destructive operations, and external
  mutations only within the action and scope authorized by the current user
  request or accepted project policy. When both the required project choice is
  committed and the action is authorized, affected work may proceed within that
  authorized scope. Authorization to perform an action does not by itself commit
  a project choice. A committed project choice does not by itself authorize
  unrelated actions. Host permission alone neither authorizes an action nor
  commits a project choice. A workflow or skill, its instructions, a test,
  specification, ticket, or Wayfinder record grants neither. Exact external
  read-only targets permit only that read.
- When accepted project policy does not already determine a required project
  choice, obtain it from the person, role, or valid delegate with project
  decision authority. If that authority is unclear, ask who may decide, why the
  choice is required, and what it unblocks. Responsibility alone does not
  establish project decision authority. The person, role, or valid delegate with
  that authority may explicitly accept unresolved uncertainty for one named
  boundary; the question remains unresolved, only that boundary becomes
  unblocked, no broader project choice is committed, no unrelated action is
  authorized, and no other dependency is satisfied. Revisit a committed choice
  only for conflict, safety, project decision authority, or request.
- Never claim unexecuted work.
- Preserve unrelated work, project state, designated artifacts, and identifiers.
  Live source and accepted artifacts outrank summaries, memory, and chat.
- Do not manufacture cross-artifact conflicts or parallel representations of
  the same current state.
  Different scope, abstraction, summarization, or omitted detail is not by itself
  an inconsistency. Before reconciling artifacts, identify a concrete
  incompatible statement or a requirement the target artifact fails to satisfy.
  When an existing designated artifact or record maintains the current state,
  update it rather than creating a parallel representation unless the new
  representation has independently useful meaning, scope, or retrieval value.
  When materially ambiguous, preserve the existing content and clarify or
  investigate rather than inventing detail or process merely to make artifacts
  match.

## When to use Wayfinder

After reconnaissance, assess durable coordination. Three or more meaningful
items require assessment, never selection by count alone.
Unless the user opts out, MUST select or resume Wayfinder when any hard signal
or at least two soft signals apply:

- Hard: cross-session continuation or agent-handoff continuity; conflicting
  sources that establish the same scoped claim; an uncommitted required project
  choice while independent work proceeds; coordinated responsible participants
  or areas; or source and scope needed to distinguish assumption from fact.
- Soft: interacting consequential unresolved questions; durable distinctions
  across record or state categories; evidence-driven plan change; a meaningful
  dependency graph; or material fresh-agent reconstruction risk.

Single unresolved questions and routine/implementation work use Direct or applicable
workflows. Honor Wayfinder use and opt-out. Read-only work changes no
state.

## Load state only when selected

For selected/resumed Wayfinder, read
`.agent-workflow/contracts/wayfinder-state.md` before the map. An unrelated map
never selects Wayfinder. Never seed state.

## Report the route

End each user-facing final response with exactly one truthful
`[route: router → <executed path or terminal outcome>]` line. Report only what
executed; use `direct` if no workflow or skill ran. If selection did
not become equivalent execution, report the routing policy's terminal outcome.
Never reroute or work merely to produce the marker.
<!-- agent-workflow:managed-end -->

<!-- agent-workflow:project-instructions -->
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

Read `CONTEXT.md` before changing routing, Wayfinder, installed-skill integration,
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
- Remove or simplify unjustified machinery rather than preserving it merely
  because it exists. Do not add package-manager-grade integrity, migration,
  compatibility, deprecation, observability, ownership registries, or lifecycle
  systems unless a concrete current failure, durable-data or safety risk, or
  current external contract requires them.

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
- Do not expand the project into a general agent runtime, package manager,
  plugin platform, compatibility framework, observability platform, broad
  lifecycle system, or other new machinery without a concrete current need.

## Authorization and preservation

- Do not treat a workflow, skill, test, specification, ticket,
  Wayfinder record, or document as authorization for commits, pushes,
  publication, destructive operations, external mutations, or changes outside
  the authorized task, or as authority to commit a project choice.
- Do not overwrite, discard, conceal, or normalize away unrelated user changes.
- Protect project-owned and user-owned durable state. Reconstructable framework
  output may be replaced when appropriate; durable state must not be treated as
  reconstructable framework content.
- Do not rely on host or model defaults as authorization to act, authority to
  commit a project choice, or for data-preservation boundaries for which Agent
  Workflow itself is responsible. Do not
  duplicate generic host or model safety policy unless Agent Workflow
  introduces a specific risk that requires a project-owned rule.

## Working practice

For substantial changes:

- Inspect the current implementation, repository status, exact worktree,
  branch, base, and relevant diff.
- Read the applicable contracts and architectural decisions and determine which
  layer owns the behavior.
- Check whether a host or installed skill already supplies the capability.
- Prefer the smallest coherent and reversible change that preserves accepted
  behavior.
- Update tests and durable documentation when the resulting contract changes.

Use current primary sources when an evolving external integration materially
affects the work.

Keep experiments reversible and isolated until adoption is intentional.

## Testing and verification

- Test Agent Workflow's contracts and boundaries rather than reproducing
  installed-skill internals.
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
