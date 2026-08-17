# ADR-0016: Reconcile relevant Wayfinder state at completion

- Status: accepted
- Date: 2026-08-16
- Amends: ADR-0011 and ADR-0013; preserved by ADR-0020

## Context

The evaluation program exposed a real continuity failure: completed ARC v2
work updated some linked Wayfinder children while its map and frontier still
described that work as future. The canonical evaluation evidence remained
intact, but the stale coordination state made the next executable work
ambiguous. Requiring users to remember a second reconciliation request leaves
the framework's durable-continuity boundary unreliable.

## Decision

When authorized mutating work materially changes a relevant existing Wayfinder
effort, the agent performing that work owns scoped reconciliation of the
affected map and U/D/T state before claiming completion. Relevance comes from
the request and progressively loaded work context; agents do not scan unrelated
efforts. Read-only work reports stale state and never repairs it.

Code, accepted ADRs, documentation, tests, and evaluation results remain
authoritative for their domains. Wayfinder stores only the coordination effect
and concise pointers to those artifacts. Detailed mechanics live in the
Wayfinder state contract; root policy carries only the compact completion and
read-only invariant.

## Consequences

Users need not separately request continuity maintenance for work they already
authorized. Completion may touch a small set of relevant project-owned state
files, but it does not broaden the work to unrelated efforts or make Wayfinder
a second source of product truth. A conflict that prevents truthful
reconciliation blocks the affected completion claim rather than being hidden.

## Alternatives considered

- Require an explicit reconciliation request: rejected because that is the
  observed source of stale continuity state.
- Scan or normalize every Wayfinder effort after mutations: rejected because it
  expands scope, increases cost, and risks unrelated project-owned data.
- Add hooks, background reconciliation, a global index, or synchronization
  machinery: rejected because existing evidence supports a completion
  ownership rule, not new infrastructure.
- Copy canonical artifacts into Wayfinder: rejected because duplicate truth
  creates a larger drift surface.
- Repair stale state during read-only work: rejected because reporting work
  does not authorize repository mutation.
