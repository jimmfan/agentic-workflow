# Focused Wayfinder VS Code projection

- Status: current

## Destination

Test whether a thin native VS Code projection can focus Wayfinder on durable
project understanding and coordination while preserving the portable runtime,
state schema, routing behavior, provider boundaries, and human authority.

## Territory

- Portable Wayfinder semantics — the owned runtime projection and local state
  contract remain canonical.
- VS Code projection — a small host wrapper selects the canonical runtime and
  exposes only the capabilities needed for repository navigation and legitimate
  state reconciliation.
- Durable-state protection — one narrow `PreToolUse` guard rejects explicit
  `apply_patch` deletion of an effort map while allowing child retirement.
- Evaluation — focused behavioral scenarios cover resume, reconciliation,
  progressive architecture loading, authority, missing knowledge, readiness,
  and the guard without embedding expected answers in live prompts.

The host projection and guard depend on current VS Code tool and hook contracts;
the scenarios and deterministic package checks then verify the distributable
artifacts without claiming a live editor run.

## Current state

- The user supplied the accepted Phase 1 scope and explicit non-goals.
- Relevant accepted ADRs already establish portable projection ownership,
  sole Wayfinder durable-state ownership, progressive territory, canonical
  evidence precedence, and human/project authority boundaries.
- Primary-source VS Code customization research is complete at
  `docs/vscode-focused-wayfinder-research.md`.
- [ADR-0030](../../../architecture-decisions/0030-use-thin-focused-vscode-wayfinder-projection.md)
  accepts the thin host projection and records the forced tradeoff: `execute`
  is needed for the canonical atomic effort lock, but VS Code cannot restrict
  that shell capability to lock operations.
- The distributable and installed custom agent, hook configuration, and guard
  are synchronized. The Phase 0 SessionStart route-marker reminder remains
  unchanged.
- Six neutral, blind live scenarios cover clean resume, authoritative stale
  reconciliation, progressive context loading, authority, missing knowledge,
  and the implementation-ready boundary.
- Closing Standards and Spec review findings were reconciled. The documented
  package gate passes 138 tests, fixture lifecycle checks preserve all 44
  scenarios, installation status is healthy, and `git diff --check` passes.

## Blockers and dependencies

- No live VS Code baseline-versus-focused run was performed, so the Phase 1
  behavioral hypothesis remains inconclusive.
- Progressive repository loading is currently supported only by the agent's
  public `state_used` report. A live host adapter with tool telemetry is needed
  to prove that unreported files were not opened.
- No human- or project-authority decision is currently blocked.

## Next work

Run the same six scenario IDs through matched general-agent and focused-agent
VS Code adapters with the model, permissions, fixture revision, and evaluator
held fixed. Compare pass/fail outcomes and reported/read context before deciding
whether the focused projection improves durable project understanding.

## Notes

- Preserve successful Phase 0 route-report enforcement.
- Do not change the Wayfinder state schema or duplicate runtime semantics into
  the VS Code wrapper.
- Do not add Phase 2 agents, protocols, handoffs, memory, reputation, generic
  host abstractions, semantic-router rewrites, or additional hook machinery.

## Out of scope

Any Phase 2 architecture; Codex or Claude projections; broader security or
authorization enforcement; and live-editor success claims not actually run.
