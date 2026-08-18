# ADR-0023: Own the Wayfinder runtime projection

- Status: accepted
- Date: 2026-08-18
- Amends: ADR-0007, ADR-0011, ADR-0013, ADR-0020, and ADR-0022

## Context

The effective Wayfinder skill combined an authoritative Agentic Workflow
local-state block with the complete pinned upstream issue-tracker runtime. The
block overrode storage, item identity, claiming, blocking, resolution,
continuation, concurrency, implementation handoff, and lifecycle behavior in
the body that followed it. This was no longer a narrow persistence adapter: a
consuming agent received two specifications and had to apply precedence across
contradictory operational rules.

Agentic Workflow's map-first U/E/F/D contract and native `to-tickets` boundary
are materially distinct from the upstream tracker implementation, but the
upstream destination, map, fog, frontier, readable-name, and progressive-
resolution methodology remains valuable and must remain attributed.

The local contract also called an effort directory a short stable slug without
fully specifying how a fresh session should match an existing effort, choose a
durable readable name, or create a stable new path. Repository history was
searched for `I/X/O`, `I#`, `X#`, `O#`, and surrounding identity, destination,
scope, and outcome vocabulary. No released Agentic Workflow record syntax or
canonical I/X/O meanings were found. The durable historical concepts that were
found are the map H1 effort name, Destination, Not yet specified, Out of scope,
progressive candidate loading, and stable slugs.

## Decision

Agentic Workflow owns the effective Wayfinder runtime projection. Matt
Pocock's pinned Wayfinder remains the unchanged methodological source,
acknowledged influence, reviewed release input, and future reference. The
effective runtime is intentionally derived rather than byte-equivalent.

Keep one explicit Wayfinder exception in the current provider adapter. The
provider declaration names a package-owned authored runtime body. During
staging, the adapter:

1. validates the declared pinned source metadata and upstream body fingerprint;
2. retains the compatible upstream frontmatter provenance;
3. applies the existing reviewed invocation-metadata changes; and
4. replaces the upstream body with the Agentic Workflow-owned body.

The runtime body lives outside Python so it can be reviewed as instructions.
The raw snapshot, its metadata, and license remain byte-for-byte unchanged.
Unrecognized upstream input or malformed projection source fails before target
mutation. All other declared provider skills retain their current exact or
narrowly adapted projection behavior.

The map H1 is the durable human-readable effort name. Destination and Out of
scope define its substantive endpoint and boundary; Not yet specified holds
in-scope fog. The directory slug is derived once from the durable name using a
simple lowercase, filesystem-safe, hyphen-separated default and then remains a
stable storage key. It is not a separate identity system.

Likely resume lists directory names first, loads only the smallest plausible
candidate-map set, and compares readable names, destinations, boundaries, and
context. Ambiguity remains read-only until resolved. Creation requires a
materially distinct destination, authorized durable writes, a final concurrent
directory recheck, and collision handling that never overwrites or merges a
different effort. Established paths remain valid even when awkward. A
materially redrawn destination, especially one that brings excluded work inside
the boundary, normally starts a fresh effort.

U/E/F/D remains the sparse child-knowledge model, not a mandatory promotion
pipeline or append-only journal. Wayfinder creates no T# implementation tree;
substantial decomposition remains owned by native `to-tickets` artifacts. No
I#, X#, O#, Identity heading, registry, or compatibility parser is introduced
because repository history establishes no released syntax requiring one.

Future upstream upgrades follow a deliberate porting model: review the new
upstream release, identify useful methodological improvements, selectively
port them into the owned runtime, and then update provenance, projection
expectations, and tests. Effective behavior does not automatically inherit
every upstream change.

## Consequences

Consuming agents receive one coherent Wayfinder runtime plus a progressively
loaded detailed state contract. The full tracker body, issue assignment,
resolution comments, issue closing, tracker-native blocking, required tracker
setup, and local `.scratch/` fallback are absent from the effective runtime.

The provider projection remains reproducible, transactional, idempotent, and
fail-closed. Fresh, raw-upstream, legacy prepend, stale, and damaged but safely
replaceable declared directories converge through the existing complete-set
reconciliation transaction. Project-owned Wayfinder state remains opaque to
lifecycle operations and receives no automatic migration.

Wayfinder is an explicit evidence-backed exception to the default that selected
providers own their complete methodology and native artifacts. The exception
does not weaken provider ownership for any other workflow and does not create a
generic projection framework.

## Alternatives considered

- Keep the prepend overlay: rejected because it preserves two conflicting
  specifications and the largest context and precedence risk.
- Embed the complete owned runtime in `providers.py`: mechanically small, but
  poor for instruction review and maintenance.
- Maintain a complete first-party effective Wayfinder directory: workable, but
  duplicates upstream metadata and projection structure when only the body and
  existing invocation metadata differ.
- Add a generic provider-extension framework: rejected because one explicit
  exception is simpler and no second use case demonstrates the abstraction.
- Restore I/X/O primitives: rejected because no authoritative released meaning
  or syntax was recovered, while current readable vocabulary covers the useful
  roles directly.
