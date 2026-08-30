# ADR-0025: Preserve project decision authority at consequential boundaries

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

Agents may make evidence-backed technical judgments within the scope delegated
by the user or accepted project policy. They must not turn an assumption,
default, proposal, precedent, or model preference into an accepted project
choice when that choice is reserved for project decision authority.

Dependent work must not cross a consequential decision boundary while required
evidence, action authorization, or project decision authority remains
unresolved. Independent work may continue. Surface the concrete question,
explain why the evidence or project decision authority is required, and state
what its answer will unblock.

Project decision authority may explicitly accept unresolved uncertainty for one
named boundary. The underlying question remains unresolved; any U# recording it
remains current and unresolved. That acceptance unblocks only the named
boundary: it does not commit a broader project choice, grant action
authorization, or unblock any other dependency.

Workflows, provider instructions, specifications, tickets, and durable state
grant neither action authorization nor project decision authority. Durable
state may record the source that supplied an answer or the project decision
authority that accepted uncertainty; it cannot create either.

## Consequences

The always-loaded root policy carries a concise form of this invariant because
violations can affect every route. Workflow contracts may define how to retain
or handle an unresolved boundary, but they do not create separate action
authorization or project decision authority models.

Tests should observe the public question, allowed independent work, and
prohibited downstream artifacts rather than require hidden reasoning or one
exact workflow trace.

## Alternatives considered

- Require a new project decision for every technical judgment: rejected because it
  would block ordinary delegated engineering work.
- Apply the rule only inside Wayfinder: rejected because assumptions can enter
  any project artifact without Wayfinder being selected.
- Treat accepted unresolved uncertainty as a resolved fact: rejected because it
  would erase its direct source-and-scope relationship and broaden one scoped
  acceptance beyond its named boundary.

## Reconsideration trigger

Reconsider only if accepted project policy deliberately changes which choices
agents may make or how project decision authorities handle unresolved questions.
