# ADR-0026: Structure Wayfinder territory and converge it

- Status: accepted
- Date: 2026-08-18
- Amends: ADR-0022 and ADR-0023
- Amended by: ADR-0028 and ADR-0029

## Context

ADR-0022 established U/E/F/D as a sparse taxonomy for current knowledge and
ADR-0023 preserved destination, fog, frontier, and progressive loading in the
framework-owned runtime. Those decisions prevent mandatory record pipelines,
but the taxonomy alone does not explain the territory of a complex effort. A
map can still degrade into a flat ledger whose children are well classified but
whose major areas, boundaries, relationships, direction, and convergence are
unclear.

The pinned upstream Wayfinder treats the destination, low-resolution map, fog,
and frontier as navigation toward a clear route rather than permanent
documentation. Its Domain Modeling integration supplies useful structural
discipline, although its tracker storage, mandatory invocations, ticket types,
and claiming/closing mechanics conflict with this framework's ownership model.

Repository history contains no released I#/X#/O# syntax to restore. The useful
intent behind the earlier identity and structure discussion is semantic: agents
must understand an effort before naming its directory, organize its territory
before accumulating records, and move resolved outcomes out of temporary
navigation state.

Without both structure and convergence, Wayfinder has two failure modes:
decomposition without convergence creates an organized warehouse, while
convergence without decomposition leaves a flat, unnavigable ledger.

## Decision

Wayfinder maps territory, resolves consequential fog, and converges toward the
effort's destination. It does not merely classify notes.

Every durable effort keeps enough low-resolution semantic structure in
`map.md` for a fresh agent to understand the destination, substantive scope
boundary, major coherent areas or domains, and important relationships or seams.
The representation remains flexible; `Territory` is a useful heading, not a
rigid schema or new record type.

Territory is provisional, adaptive, and judgment-based. It helps Wayfinder
explore relevant areas and seams, challenge incomplete framing, and revise its
understanding as evidence develops. Exploration may broaden understanding, but
must not silently broaden the user's goal, delegated authority, or
implementation scope. This flexibility is intentional while the project gathers
behavioral evidence; it does not justify a formal territory schema.

For a new durable effort, reuse authoritative structure from accepted project
artifacts when it already supplies those bearings. Otherwise establish them
directly when current context supports them confidently. When material
structural ambiguity remains and structural discovery is actually needed,
Domain Modeling is the preferred discovery mechanism before substantial U/E/F/D
state accumulates. Domain Modeling is not mandatory ceremony for every new
effort or resume. Research, Prototype, and Debugging generally resolve fog
within established territory. Human or project authority remains non-delegable
under ADR-0025.

Effort identity, readable name, destination, boundary, major areas, and stable
path follow that understanding. Agents do not invent
`wayfinder/<effort-name>/` first and rationalize its structure afterward. The
directory remains only a stable storage key; no I#/X#/O# compatibility syntax,
identity object, or registry is introduced.

U/E/F/D continues to classify optional current knowledge within the semantic
territory. It does not replace the map. Physical storage remains one flat set of
optional type directories under the effort; areas do not receive nested trees,
parallel maps, identifiers, or lifecycle files.

A semantic area is settled when no consequential fog remains there and every
durable outcome has reached its proper canonical project owner or the workflow
that owns the resulting work. Depending on the result, that owner may be an ADR,
specification, project documentation or source, `to-tickets`, Implementation,
another project-native artifact, or no separate artifact. Not every area or D#
becomes an ADR, and not every area becomes a ticket.

Settlement exposes a coherent ready frontier rather than requiring one global
next action. The frontier may contain one or more independently ready scopes,
each handed to Implementation coherently, while dependency-blocked work remains
behind its unresolved boundary.

Settlement reconciles the current map and its canonical pointers, then retires
U/E/F/D records as their independent navigational value disappears. New evidence
updates the same current semantic structure rather than creating permanent
parallel structures. Git provides history; Wayfinder does not add archives or
retain stale knowledge merely because it was once written.

A completed effort has reached its destination, has no consequential in-scope
fog, has handed off or canonically placed durable outcomes, and has retired
redundant temporary knowledge. Completed efforts should normally become
materially smaller than active exploration and may end with little more than a
concise `map.md` pointing to canonical outcomes.

Assessment may still conclude that no durable Wayfinder state is useful. This
decision does not create a mandatory Wayfinder-to-Domain-Modeling-to-map
pipeline.

## Consequences

Fresh sessions receive both kinds of orientation they need: the semantic map
shows what the effort contains and how its areas relate, while U/E/F/D preserves
only independently useful current knowledge. Naming becomes a consequence of
understanding rather than an input that biases discovery.

Wayfinder has an explicit pressure toward smaller state. Canonical project
artifacts own lasting outcomes, supporting workflows own their native results,
and the map retains only the pointers and current navigation needed to proceed.

The runtime carries the navigation method and convergence boundary. The
progressively loaded state contract owns effort selection, identifiers, links,
locking, retirement algorithms, lifecycle mutation, and detailed settlement.
Existing clear maps remain valid and receive no automatic migration.

## Alternatives considered

- Add I#/X#/O# records or a separate identity file: rejected because no released
  contract requires them and the useful semantics fit the map directly.
- Create nested directories per area: rejected because semantic organization
  does not require a physical hierarchy and nested state would increase loading,
  migration, and reconciliation costs.
- Always run Domain Modeling: rejected because authoritative project structure
  or confident current context may already be sufficient, and resumed coherent
  efforts need no ceremony.
- Keep all resolved records for completeness: rejected because Wayfinder is
  current navigation state and Git already owns recoverable history.
- Promote every settlement to an ADR or ticket: rejected because canonical
  ownership depends on the result's actual durability and work shape.
- Formalize territory boundaries or scoring now: deferred until evaluation shows
  that provisional judgment causes agents to get stuck, drift scope, or
  reconstruct the same effort inconsistently.
