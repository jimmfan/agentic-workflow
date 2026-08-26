# ADR-0025: Preserve authority at consequential boundaries

- Status: accepted
- Date: 2026-08-18

## Context

An agent can avoid recording an explicit decision yet still smuggle an
assumption into a specification, ticket, or implementation direction. Requiring
complete certainty would stop responsible progress, but crossing an unresolved
consequential boundary can launder uncertainty into accepted project reality.

This problem is cross-cutting. It applies whether work is Direct, uses a
specialist, or persists coordination in Wayfinder.

## Decision

Agents may make evidence-backed judgments within authority already delegated by
the user or accepted project policy. They must not turn an assumption, default,
proposal, precedent, or model preference into an accepted project choice when
the choice belongs to human or project authority.

Dependent work must not cross a consequential decision boundary while required
evidence, approval, or authority remains unresolved. Independent work may
continue. Surface the concrete question, explain why the authority or evidence
is required, and state what its answer will unblock.

A responsible authority may explicitly accept residual uncertainty for one
named boundary. That acceptance unblocks only that boundary: it does not answer
the underlying unknown, grant new authority, or unblock unrelated dependencies.

Workflows, provider instructions, specifications, tickets, and durable state do
not expand authority. Durable state may record who supplied an answer or
accepted uncertainty; it cannot create that authority.

## Consequences

The always-loaded root policy carries a concise form of this invariant because
violations can affect every route. Workflow contracts may define how to retain
or disposition an unresolved boundary, but they do not create separate
authority models.

Tests should observe the public question, allowed independent work, and
prohibited downstream artifacts rather than require hidden reasoning or one
exact workflow trace.

## Alternatives considered

- Require human approval for every technical judgment: rejected because it
  would block ordinary delegated engineering work.
- Apply the rule only inside Wayfinder: rejected because assumptions can enter
  any canonical artifact without Wayfinder being selected.
- Treat accepted residual uncertainty as a resolved fact: rejected because it
  would erase provenance and broaden one authority decision beyond its scope.

## Reconsideration trigger

Reconsider only if accepted project policy deliberately changes which decisions
agents may make or how responsible authorities disposition unresolved risk.
