# D2: Own the runtime projection and stable effort boundary

- Status: accepted
- Authority: user request and ADR-0023
- Related: U1, D1, ADR-0022, ADR-0023

## Decision

Keep the pinned Matt Pocock Wayfinder snapshot byte-for-byte as provenance, but
make Agentic Workflow own the runtime body installed for Wayfinder. The explicit
Wayfinder adapter recognizes the pinned upstream input by metadata and body
fingerprint, rewrites the invocation metadata, and replaces the upstream body
with the authored projection in `runtime-projections/wayfinder.md`. Unknown or
modified provider input remains a fail-closed incompatibility.

Recognize the effort from its map H1, destination, scope boundary, and map
context. Treat the directory slug only as its stable storage location. Honor an
exact requested path. Otherwise progressively inspect candidate names and maps,
resume one clear match, and report ambiguity without mutation. Create a new
lowercase hyphenated slug only when Wayfinder is selected, durable writes are
authorized, structured state is materially useful, no existing effort matches
the destination and boundary, and the destination is materially distinct. Once
created, keep the path stable even when the effort wording is refined.

Use U#/E#/F#/D# as the optional child vocabulary. Repository history supplies no
authoritative released I#/X#/O# contract, so do not invent one or add speculative
compatibility handling. Historical pre-contract T# files remain untouched, but
the runtime projection does not create Wayfinder work items.

## Why

Prepending a local override to the complete upstream tracker workflow made the
effective skill a dual specification with competing storage, ticket, and
completion mechanics. A concise owned body gives agents one operational
contract while retaining raw upstream provenance for audit and selective future
porting. Stable effort selection prevents synonymous wording from silently
forking state.

## Alternatives rejected

- Continue prepending an override: retains contradictory mechanics and needless
  context.
- Fork the full effective provider directory: duplicates metadata and expands
  the maintained surface without improving the boundary.
- Embed the projection in Python: obscures review and couples prose changes to
  adapter code.
- Add I#/X#/O# aliases or migration logic: history provides no trustworthy
  semantics to preserve.
