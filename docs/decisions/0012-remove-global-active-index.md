# ADR-0012: Resume from canonical records and maps

- Status: accepted
- Date: 2026-08-14
- Supersedes: the global active-workflow portions of ADR-0007 and the original
  non-Wayfinder index exception in ADR-0011

## Context

The durable-state contract used `.ai-workflow-state/active.md` as a pointer to
one active and one interrupted DEC, IMP, or DBG record. The index was not
runtime-enforced, while each referenced record already stored its own status,
provider pointer, pending work, and exact resume target.

Project-owned Wayfinder state made the duplication clearer: its canonical
`map.md` is already the natural re-entry artifact and deliberately bypassed the
global index. Keeping both models added transition, conflict, and template rules
without protecting data or making routing reliably more accurate.

## Decision

Remove `active.md` as a current framework concept and remove the distributed
active-state template. DEC, IMP, and DBG workflows resume from their canonical
record; Wayfinder resumes from the relevant effort map. A likely resume without
an exact path inspects only filenames and concise status/title fields needed to
identify plausible records, then asks when ambiguity remains. Direct and
unrelated work does not scan durable state.

Multiple unrelated active or interrupted records may coexist. Conflicts are
scoped to incompatible claims about the same work or accepted decision, not the
mere existence of another record. Stable-ID collision checks and rereading the
target before a write remain required.

Existing `.ai-workflow-state/active.md` files are project-owned and remain
untouched, but the framework never reads, validates, creates, or updates them.
For data safety, the narrow legacy import preserves an old
`.ai-workflow/state/active.md` as inert
`.ai-workflow-state/legacy-active.md` rather than deleting it or presenting it
as current state.

## Consequences

Durable re-entry has one rule: resume from the artifact that owns the work. The
framework loses a constant-time global pointer and global mutual-exclusion
signal, but avoids a second source of truth and permits independent durable work
without false conflicts. Ambiguous unnamed resumes may require reading a few
record headers or asking the user.

Lifecycle operations gain no ownership of project state. Existing and legacy
active-index bytes are preserved, and no migration parses or rewrites them.

## Alternatives considered

- Keep `active.md` for non-Wayfinder workflows: rejected because record files
  already contain the useful resume data and Wayfinder would retain a competing
  continuity model.
- Put Wayfinder behind `active.md`: rejected because it duplicates the canonical
  map and creates unnecessary indirection.
- Delete existing active files during update: rejected because they are
  project-owned data and may contain unique user context.
