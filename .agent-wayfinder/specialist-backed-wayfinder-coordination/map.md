# Specialist-backed Wayfinder coordination

- Status: completed

## Destination

Agent Workflow has one framework-owned durable coordination layer: Wayfinder.
Direct reasoning remains valid, specialist methods load only when they materially
help the current frontier, and ready work crosses a clean Implementation and
Verification boundary without DEC, IMP, DBG, or replacement workflow records.

## Territory

- Routing and dispatch — Direct-first selection, obvious Wayfinder composition,
  specialist laziness, provider truthfulness, and route reporting.
- Specialist boundaries — standalone and Wayfinder-supporting Discovery,
  Debugging, Research, Prototype, Domain Modeling, and Implementation behavior.
- Durable ownership — map-first U/E/F/D continuity, legacy record preservation,
  removal of new DEC/IMP/DBG allocation, and remaining shared project-state rules.
- Delivery and evidence — runtime projection, distributable payload, ADRs,
  deterministic scenarios, context measurements, and package verification.

These areas meet at one seam: a specialist may resolve a frontier, but Wayfinder
alone preserves the consequential coordination needed to resume.

## Current state

- [ADR-0028](../../../architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md)
  owns the completed architecture: Wayfinder coordinates durable state,
  specialists own methods, and Direct remains valid.
- Runtime wording was simplified without changing the root gate, Wayfinder
  state schema, durable-state contract, lifecycle, or handoffs.
- The six authored runtime-facing files fell from 26,661 bytes / 4,661 words to
  21,054 bytes / 2,888 words. Direct remains 3,159 / 433; an ambiguous route
  fell from 16,985 / 2,352 to 10,222 / 1,418.
- The full 116-test package suite, nine routing-smoke tests, static package
  verification, projection parity, lifecycle status, and diff whitespace check
  pass.

## Blockers and dependencies

None.

## Next work

None for this effort.

## Notes

- Preserve existing legacy workflow records as opaque project-owned data; add no
  migration or compatibility parser.
- Use existing deterministic routing/behavior harnesses and token/context
  instrumentation; do not create a new benchmark framework.
- The accepted human-authority, canonical-artifact, project-data preservation,
  U/E/F/D, and scoped reconciliation rules remain governing constraints.

## Decisions so far

- Proceed with the user-authorized pre-1.0 simplification: Wayfinder becomes the
  sole framework-owned durable coordination layer, while specialists remain
  stateless from the framework's perspective.
- Obvious specialist selection inside an already selected Wayfinder effort must
  not load the detailed router merely because composition exists.
- Implementation remains a handoff/execution boundary and receives no successor
  to IMP.

## Out of scope

- Migrating, deleting, or normalizing legacy project-owned DEC/IMP/DBG files.
- Adding new micro-skills, scratch state, lifecycle services, migration layers,
  or a new benchmark framework.
- Changing the pinned upstream provider version or rewriting frozen historical
  evaluation results.
