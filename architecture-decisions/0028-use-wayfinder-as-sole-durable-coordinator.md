# ADR-0028: Use Wayfinder as the sole durable coordinator

- Status: accepted
- Date: 2026-08-20

## Context

Multiple specialist-specific continuity systems would create competing resume
identities, statuses, and lifecycle behavior. Specialists already provide
better methods, and their results belong in source files, specifications,
tickets, research reports, prototypes, domain-model updates, or review
reports—not Wayfinder. Copying their procedures into Wayfinder would increase
context and create drift.

The project needs one small durable coordination model, not mandatory durable state for
every method that might help during an effort.

## Decision

Agent Workflow defines Wayfinder as its sole durable coordination model. It persists
only consequential cross-session coordination: objective, scope, areas and
relationships, conditions blocking particular work, dependencies, ready work,
optional current knowledge, and readable references to relevant source files,
specifications, tickets, accepted decisions, research reports, prototypes,
domain-model updates, and reviews.

Each specialist retains its method and produces the result described by its
skill. The specialist creates no Agent Workflow durable coordination state.
Direct reasoning remains valid; load only a specialist whose method materially
helps the current work or unresolved question.

The ticket or ticket set produced by `to-tickets` remains in its project or
tracker location and maintains ticket contents, dependencies, ordering, and
readiness. Wayfinder may reference it and identify the current ready-work
reference but never mirrors T# work as a second ticket or status surface.
Specifications, research results, prototypes, domain-model updates, and reviews
likewise remain where they were produced.

When interrupted work lacks a source file, specification, ticket, research
finding, review, or other record sufficient for continuation, Wayfinder records
only consequential coordination needed for resumption—such as a current
question, a condition blocking particular work, a dependency, or ready work—and
links to relevant results. Unrecognized project-owned content is not current
coordination state or an automatic resumption source.

## Consequences

Fresh sessions have one Agent Workflow resumption model. Standalone specialist
work may still return findings or produce its normal result without creating
Agent Workflow coordination state, while specialist methodology stays in its
skill.

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
  would become large and drift from the specialist method.
- Add a generic specialist-result or workflow-transition record: rejected because
  the map and its referenced specifications, tickets, research reports,
  prototypes, domain-model updates, or reviews already carry the required
  references and next work.

## Reconsideration trigger

Reconsider if a specialist demonstrates a durable coordination need that cannot
be represented safely by the specialist's normal result plus a concise Wayfinder
reference.
