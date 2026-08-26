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
  - durable coordination across sessions, handoffs, owners, or interacting
    state → assess Wayfinder using the criteria below
- For one obvious specialist inside an already selected Wayfinder effort, load
  only what it needs.
  Read `.agent-workflow/routing.md` only when ownership is unclear or provider
  fallback, handoff, or durable re-entry materially matters.
- Workflows never expand authority. Exact external read-only targets permit only
  that read.
- MUST NOT cross a consequential decision boundary without required evidence,
  approval, or authority. Explicit responsible-authority acceptance leaves the
  recorded uncertainty unresolved and unblocks only its named boundary;
  independent work may continue.
- Never decide for human or project authority. Ask the concrete question and
  why authority is required, and what its answer unblocks. Reopen a settled
  choice only for conflict, safety, authority, or request.
- Never claim unexecuted work.
- Preserve unrelated work, project state, canonical artifacts, and identifiers.
  Live source and accepted artifacts outrank summaries, memory, and chat.

## When to use Wayfinder

After reconnaissance, assess durable coordination. Three or more meaningful
items require assessment, never selection by count alone.
Unless the user opts out, MUST select or resume Wayfinder when any hard signal
or at least two soft signals apply:

- Hard: cross-session or handoff continuity; conflicting authoritative sources;
  an authority-owned blocker while other work proceeds; coordinated owners or
  areas; or provenance needed to distinguish assumption from fact.
- Soft: interacting consequential unknowns; durable distinctions across state
  categories; evidence-driven plan change; a meaningful dependency graph; or
  material fresh-agent reconstruction risk.

Single unknowns and routine/implementation work use Direct or applicable
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
  provider integration, safe framework delivery, authorization boundaries,
  durable coordination the framework genuinely owns, and integration
  verification.
- Prefer existing host or provider capabilities and canonical artifacts over
  parallel Agent Workflow representations or lightly rewritten upstream
  functionality.
- Do not expand the project into a general agent runtime, package manager,
  plugin platform, compatibility framework, observability platform, broad
  lifecycle system, or other new machinery without a concrete current need.

## Authorization and preservation

- Do not treat a workflow, provider, skill, test, or document as authorization
  for commits, pushes, publication, destructive operations, external mutations,
  or changes outside the authorized task.
- Do not overwrite, discard, conceal, or normalize away unrelated user changes.
- Protect project-owned and user-owned durable state. Reconstructable framework
  output may be replaced when appropriate; durable state must not be treated as
  disposable framework content.

## Working practice

For substantial changes:

- Inspect the current implementation, repository status, exact worktree,
  branch, base, and relevant diff.
- Read the applicable contracts and architectural decisions and determine which
  layer owns the behavior.
- Check whether a host or provider already supplies the capability.
- Prefer the smallest coherent and reversible change that preserves accepted
  behavior.
- Update tests and durable documentation when the resulting contract changes.

Use current primary sources when an evolving external integration materially
affects the work.

Keep experiments reversible and isolated until adoption is intentional.

## Testing and verification

- Test Agent Workflow's contracts and boundaries rather than reproducing
  provider internals.
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
