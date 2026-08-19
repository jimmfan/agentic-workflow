# ADR-0021: Maintain compact current decision context

- Status: accepted
- Date: 2026-08-17
- Related: ADR-0020
- Amended by: ADR-0027

## Context

Agents need current project decisions while routing and working, but an
append-only instruction and ADR set makes obsolete rules look authoritative and
consumes context on every request. Git already preserves the complete history.
The current work also exposed a repeated interaction failure: after the user
explicitly settled the same structural choice, an agent repeatedly treated it
as an open question.

These are cross-project instruction-governance concerns, not provider lifecycle
details. They need a lasting decision separate from ADR-0020 without expanding
the always-loaded root policy into a process manual.

## Decision

Keep only rules needed during routing or needed to prevent cross-cutting
authorization, preservation, or truthfulness failures in the managed root
policy. Treat a choice the user explicitly resolves as settled; reopen it only
for new conflicting evidence, an authorization or safety issue, or the user's
request. Put detailed procedures in progressively loaded contracts.

Treat ADRs as a maintained set of current decisions rather than an append-only
working-tree archive. The canonical ADR directory keeps a concise index that
separates current records from superseded tombstones. Consolidate amendment
chains when one current record states the operative contract more clearly. A
fully superseded ADR may be removed when recoverable version-control history
retains it and the index names its replacement; otherwise archive it. Do not
create ADRs for routine implementation details, and do not seed an ADR directory
or index during installation.

## Consequences

Consuming projects receive one small settled-choice rule in always-loaded
context and load the detailed ADR policy only when durable state is relevant.
Current decisions are easier to identify, while superseded identifiers remain
traceable through tombstones and Git. Projects without recoverable history keep
superseded rationale in an archive instead of deleting it.

This policy requires maintainers to update the ADR index when accepting,
superseding, consolidating, or removing a decision. It deliberately uses no
hook, database, generated ledger, or installer-seeded documentation.

## Alternatives considered

- Keep every instruction and ADR indefinitely in the active context: rejected
  because obsolete decisions compete with current contracts and increase agent
  context cost.
- Rely only on Git without tombstones: rejected because old identifiers and
  links would have no visible current replacement.
- Add automated ADR lifecycle machinery: rejected because a maintained Markdown
  index is sufficient for this pre-1.0 single-user project.
