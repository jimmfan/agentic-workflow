# ADR-0011: Use map-first Wayfinder state

- Status: accepted
- Date: 2026-08-14

## Context

Durable coordination must let a fresh maintainer or agent recover the useful
shape of an effort without loading a complete activity history. One
undifferentiated flat ledger used as the whole coordination model loses semantic
relationships, while an ever-growing structured notebook becomes an organized
warehouse. This does not preclude bounded same-type ledgers beneath a map-first
orientation surface. Duplicating source files, specifications, tickets, accepted
decisions, research reports, or other lasting project records inside Wayfinder—or
mirroring an external tracker—would create competing maintained representations.

Agent Workflow's map-first model and its transition from coordination into
decomposition by `to-tickets` also differ materially from the upstream Wayfinder
issue-tracker runtime. Presenting
both operational models at once would force each agent to reconcile conflicting
instructions.

## Decision

When durable coordination is warranted, use project-owned, map-first Wayfinder
state. The current local representation lives under
`.agent-wayfinder/<effort>/`. When resuming an effort, read `map.md` first.

The map is a brief coordination summary, not a type ledger. It preserves the
objective, scope, major areas and relationships, current coordination state,
conditions blocking particular work, relevant dependencies, and ready work.
Optional supporting knowledge exists only when durable preservation adds value;
a map-only effort is valid and supporting detail loads progressively. The contract may
consolidate small same-type records while keeping independently useful
coordination or retrieval units separate; that representation remains a
contract and test detail.

Wayfinder represents current coordination state rather than permanent identities
or an append-only journal. Source files, specifications, tickets, accepted
decisions, research reports, and other project records continue to hold their
lasting results; the map and recognized records converge and shrink, and Git
preserves committed historical evolution.
Preserve a question independently only when retaining it or its eventual answer
could materially improve a later developer's ability to make or evaluate a
choice. A blocker is a condition that currently prevents particular work from
proceeding. An unsatisfied dependency, unresolved consequential uncertainty, or
missing required authority can be a blocker for affected work.
Ready work is work to which no blocker currently applies; independent ready work may proceed
while other work remains blocked.

Work authorized within the current scope that changes represented reality must
reconcile affected map content, recognized records, and references with current
source files, specifications, tickets, accepted decisions, research reports, and
other relevant project records before claiming completion. Read-only work may
report staleness but does not repair project-owned state.

The effective Wayfinder instructions present one coherent operational model
rather than prepend local state rules to a contradictory tracker specification.
Matt Pocock's `v1.2.3` skill remains the attributed methodological source. The
maintained derived skill preserves applicable map, readable-name,
progressive-resolution, and reasoning sensitive to project decision authority
through the project's
objective, scope, literal uncertainty, blocker, and ready-work language.

Lifecycle operations treat the complete `.agent-wayfinder/` tree as project
data uninterpreted by lifecycle. Exact state mechanics remain progressively loaded from the
Wayfinder contract.

## Consequences

A fresh session can orient from one small map and load only relevant detail.
State can remain sparse and human-editable without a database, event log,
global state registry, shadow work tree, or duplicated tracker.

The ticket or ticket set produced by `to-tickets` maintains ticket
contents, dependencies, ordering, and readiness. Wayfinder references that
ticket or ticket set and may identify the current ready-work reference rather than mirroring
T# work as a second ticket/status surface.

U/E/F/D storage topology, schemas, numbering, filenames, effort selection,
reconciliation, pruning, effort ending, statuses, templates, and reference rules are
contract and test details, not architectural commitments.

## Alternatives considered

- Persist a complete journal or permanent child identities: rejected because
  current coordination state should converge instead of accumulating maintenance state.
- Duplicate source files, specifications, tickets, accepted decisions, research
  reports, or other project records inside Wayfinder: rejected because two
  maintained representations would drift.
- Layer map-first rules over the upstream tracker runtime: rejected because one
  effective skill must describe one coherent way of operating.
- Require a database, graph index, external tracker, or lifecycle-wide Markdown
  schema validation: rejected because brief safely resumable maps, targeted contract
  rules, references, agent reasoning, and Git cover the current need without making
  project-owned edits lifecycle failures.

## Reconsideration trigger

Reconsider if fresh sessions repeatedly cannot reconstruct consequential state,
if map convergence loses needed information, or if a different representation
provides materially simpler and safer resumption.
