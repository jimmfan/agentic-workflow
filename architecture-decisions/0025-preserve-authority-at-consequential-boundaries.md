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
choice. Do not treat a consequential project choice as committed until required
evidence is sufficient and either accepted project policy determines the choice
for that boundary or the person, role, or valid delegate with project decision
authority commits it. Responsibility alone does not establish that authority.

Dependent work stops while a required project choice remains uncommitted;
independent work may continue. Obtain a required project choice from the person,
role, or valid delegate with project decision authority, apply accepted project
policy when it already determines the choice, or clarify who may decide when
decision authority itself is unclear. State the concrete question, why the
evidence or choice is required, and what its answer will unblock.

Perform only actions authorized by the current user request or accepted project
policy and only within that scope. Authorization to perform an action does not
commit a project choice. A committed project choice does not authorize an
unrelated action. Host permission supplies neither action authorization nor a
committed project choice. A workflow or skill, its instructions, a test,
specification, ticket, or Wayfinder record grants neither.

The person, role, or valid delegate with project decision authority may
explicitly accept unresolved uncertainty for one named boundary. The underlying
question remains unresolved; any U# recording it remains current and unresolved.
That acceptance unblocks only the named boundary: no broader project choice is
committed, no unrelated action is authorized, and no other dependency is
satisfied.

Durable state may record the accepted project policy that determines a choice, the
person, role, or valid delegate who commits it, or the authority that accepted
uncertainty; it cannot create policy, authority, or authorization.

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
agents may make or how holders of project decision authority handle unresolved
questions.
