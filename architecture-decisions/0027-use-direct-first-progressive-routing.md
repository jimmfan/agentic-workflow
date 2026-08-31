# ADR-0027: Use Direct-first progressive routing

- Status: accepted
- Date: 2026-08-19

## Context

Loading maximum classification and workflow policy before gathering evidence
charges the most context at the point of least understanding. Installed skill
descriptions already provide a cheap first selection interface, while raw item
counts are poor proxies for consequence or coordination risk.

Users also should not need to recognize that an initially bounded task has
developed enough interacting state to warrant durable coordination.

## Decision

Begin with the simplest reasonable route. Classify from user intent and cheap
capability descriptions, then perform only the smallest read-only
reconnaissance within delegated scope when evidence is insufficient. Choose
Direct or one primary workflow, and add only supporting capabilities that
materially help.
Load specialist method, detailed routing policy, or durable coordination only
when its boundary becomes relevant.

Routing is not frozen at the first prompt. Re-evaluate when evidence changes.
The router may select or transition to Wayfinder implicitly when durable
coordination materially reduces the chance of losing or conflating
consequential state; users need not diagnose that transition themselves.
Explicit user selection or opt-out controls the route, and read-only scope does
not grant action authorization for writes.

Keep always-loaded classification context small and progressively load deeper
methodology, installed-skill invocation policy, and state contracts only after their boundaries
become relevant. Route sequences are default transitions with entry conditions,
not mandatory pipelines.

## Consequences

Bounded work and one obvious skill avoid unrelated routing policy. Complex
composition still pays for the instructions it needs. The design depends on
concise skill descriptions and truthful re-evaluation as new evidence appears.

The exact Wayfinder assessment signals, route marker, skill-availability fallback rules,
thresholds, context budgets, and evaluation outcomes remain in root policy,
routing contracts, tests, and evaluation history. They may evolve without
rewriting this decision.

## Alternatives considered

- Load the detailed router before inspecting ambiguous work: rejected because
  it charges maximum context before useful evidence exists.
- Select Wayfinder at a fixed item count: rejected because quantity alone does
  not establish consequence, interaction, persistence, or coordination risk.
- Require the user to request every route transition: rejected because the routing
  layer is responsible for recognizing when its current process is no longer sufficient.
- Treat workflows as mandatory pipelines: rejected because capability
  composition should follow actual entry conditions and evidence.

## Reconsideration trigger

Reconsider if observed agents repeatedly miss applicable workflows, fresh
sessions lose consequential state, or host-native capability selection makes an
explicit Direct-first router unnecessary.
