# ADR-0028: Use Wayfinder as the sole durable coordinator

- Status: accepted
- Date: 2026-08-20

## Context

Multiple specialist-specific continuity systems would create competing resume
identities, statuses, and lifecycle behavior. Specialists already provide
better methods and provider-native artifacts than a coordinator could reproduce,
so copying
their procedures into Wayfinder would increase context and create drift.

The project needs one small durable coordination model, not mandatory durable state for
every method that might help during an effort.

## Decision

Agent Workflow defines Wayfinder as its sole durable coordination model. It persists
only consequential cross-session coordination: objective, scope, areas and
relationships, conditions blocking particular work, dependencies, ready work,
optional current knowledge, and readable references to project artifacts that
maintain lasting results.

Specialists retain responsibility for their methods and provider-native
artifacts. A specialist may create a durable provider-native artifact or
evidence. The specialist creates no Agent Workflow durable coordination state.
Direct reasoning remains valid; load only a specialist whose method materially
helps the current work or unresolved question.

Provider-native artifacts remain in the locations designated to maintain them.
In particular, the `to-tickets` ticket artifact or ticket set maintains ticket
contents, dependencies, ordering, and readiness. Wayfinder may reference that
output and identify the current ready-work reference but never mirrors T# work
as a second ticket/status surface. Other provider-native or accepted project
artifacts likewise remain outside the coordination model.

When interrupted work lacks an artifact sufficient for continuation, Wayfinder records
only consequential coordination needed for resumption—such as a current
question, a condition blocking particular work, a dependency, or ready work—and
references. Unrecognized project-owned content is not current coordination state or an
automatic resumption source.

## Consequences

Fresh sessions have one Agent Workflow resumption model. Standalone specialist
work may still create provider-native artifacts or evidence without creating
Agent Workflow coordination state, while specialist methodology stays in its
provider skill.

This decision does not require Wayfinder's current Markdown representation.
Representation and resumption are governed separately by ADR-0011, so either
choice may change without silently changing the other.

Exact specialist integrations, implementation mechanics and workflow transitions,
context budgets, and evaluation outcomes belong in runtime instructions,
contracts, tests, and history rather than this decision.

## Alternatives considered

- Retain specialist-specific durable notebooks: rejected because they create
  competing continuity models for work that already crosses the Wayfinder
  threshold.
- Copy specialist methods into Wayfinder: rejected because the coordinator
  would become large and drift from the provider method.
- Add a generic specialist-result or workflow-transition record: rejected because
  the map and provider-native artifacts already carry the required references
  and next work.

## Reconsideration trigger

Reconsider if a specialist demonstrates a durable coordination need that cannot
be represented safely as a provider-native artifact plus a concise Wayfinder
reference.
