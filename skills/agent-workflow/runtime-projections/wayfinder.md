# Wayfinder

Wayfinder is Agent Workflow's sole framework-owned durable coordination
layer. Use it when consequential state needs reliable continuity across
sessions, handoffs, owners, or interacting areas. Clear bounded work, one
isolated unknown, and read-only work stay on their minimum useful route.

This framework-owned runtime projection is derived from Matt Pocock's
Wayfinder methodology. It chooses how to navigate and resolve the frontier;
`.agent-workflow/contracts/wayfinder-state.md` owns state mechanics.

## Core invariants

- Route before inspecting state; an existing map never selects Wayfinder.
- Establish the destination and enough relevant territory to orient the effort
  before substantial decomposition. Keep `map.md` low-resolution and load
  detail only when relevant.
- The map owns current state, blockers, dependencies, frontier, and next work.
  Optional F/D ledger sections and U/E artifacts preserve only useful current
  knowledge.
- Create a separate artifact because it is an independently useful coordination
  or retrieval unit, not merely because it belongs to a semantic category.
- Live source and accepted project artifacts outrank stale map state.
- Inspect Git/session state when useful for safe execution, but do not normally
  persist volatile observations. Retain durable Git constraints and
  dependencies under the state contract.
- Durable Wayfinder state can record authority; it cannot create authority.
  Use an actual human or project source, or valid delegated scope, for an
  authority-owned choice. Keep the question and what it blocks explicit.

When selecting or resuming Wayfinder, read the state contract before the map.
It defines effort selection, paths, identifiers, locking, reconciliation,
settlement, and lifecycle. If the state contract is unavailable, fail closed
for the affected Wayfinder work: do not inspect or mutate a map; do not invent
substitute persistence or create tracker, specialist-record, or scratch state.
Report the incomplete installation.

## Establish territory

Reuse accepted project structure when it supplies a useful destination, scope,
areas, and important seams. Otherwise establish the smallest useful structure
directly. Territory is provisional, adaptive, and judgment-based. It helps
Wayfinder explore relevant areas and seams, challenge incomplete framing, and
revise its understanding as evidence develops. Exploration may broaden
understanding, but must not silently broaden the user's goal, delegated
authority, or implementation scope.

Domain Modeling is the preferred structural fallback when clarifying
or reorganizing concepts, vocabulary, boundaries, responsibilities, or
relationships would materially improve the map's usefulness or coherence;
progress need not already be blocked. When it would help, establish enough
territory before substantial U/E/F/D accumulates, then derive the effort name
and stable path from that territory.

On a coherent resume, do not reload Domain Modeling merely because Wayfinder
resumed. If later authoritative evidence materially invalidates the territory,
Domain Modeling may re-enter to revise the same map. Reconcile the current
structure rather than preserving stale or parallel territory.

## Resolve the frontier progressively

Continue directly when the frontier can be resolved safely without additional
methodology. Load only the smallest specialist whose method would materially
improve resolution:

- **Discovery** for consequential alternatives and tradeoffs.
- **Debugging** for an observed behavior with an unknown cause.
- **Research** for external uncertainty needing primary-source evidence.
- **Prototype** when a disposable experiment is the cheapest honest test.
- **Domain Modeling** to establish, improve, or revise territory under the rule
  above.
- **Human clarification or Grilling** for authority, intent, preference, or
  prioritization.

Research, Prototype, and Debugging usually resolve ordinary fog within coherent
territory; they do not replace structural modeling when the territory itself
needs improvement or revision.

The resolution method determines what evidence or authority is sufficient to
answer the question. It is not merely an artifact label: human clarification
requires the responsible authority, research requires appropriate source
evidence, and prototype or debugging requires relevant observed or experimental
evidence. Existing authoritative evidence may satisfy the method without a
ceremonial specialist invocation, but one method cannot substitute for another's
required authority or evidence.

Do not load specialists speculatively. Specialists own their methods and native
artifacts and create no framework continuity record. If work is interrupted,
reconcile only the consequential frontier, evidence or conclusions, artifact
pointers, resolution mode when useful, and next work into Wayfinder. The map,
not DEC/IMP/DBG or a specialist notebook, is the re-entry point.

## Reconcile and hand off

Keep the map sufficient for a fresh session to recover the destination,
current state, blockers, dependencies, and coherent ready frontier. Link
canonical artifacts instead of copying them. The state contract defines when
U/E/F/D detail is worth retaining and how settled state shrinks.

Map uncertainty broadly, then promote selectively. A precise question becomes
U# when preserving the question or its eventual answer could materially improve
a later developer’s ability to make or evaluate a decision. This applies within
the current destination and relevant territory, especially when the answer
requires human or project authority, depends on an external owner or approval,
or gates multiple downstream areas or a meaningful seam. Ask the substantive
project question when project knowledge determines materiality; do not ask
merely whether to create a U#. Keep incidental or merely unspecified detail
under `Not yet specified` in the map. Precision alone is insufficient. Ordinary
research or debugging fog, a long list, or a template does not by itself
justify a U#. A temporary U# is useful only when separate preservation improves
current coordination or later continuation, not as create-and-retire ceremony.

When dependency evidence is sufficient, surface the navigation shape concisely:
the critical path, independent parallel work, and any off-path dependency whose
external lead time materially affects the route. Do not infer a critical path
from an unordered backlog or incomplete evidence.

The ready frontier is the set of coherent scopes whose material decision
dependencies are answered or explicitly dispositioned and can therefore
proceed now. Answer the consequential U#, or canonically record the responsible
authority’s explicit acceptance of the remaining uncertainty for that boundary.
The U# then remains factually unanswered and does not become resolved; the
acceptance unblocks only the named boundary. Reconcile and shrink the map, then
hand off one or more ready scopes without advancing work that remains
dependency-blocked. Each Implementation handoff consumes one coherent scope and
its acceptance criteria; Verification follows execution. Use `to-tickets` only
when approved work needs substantial dependency ordering or independently
deliverable sessions, and link its native frontier without a shadow copy.

Read-only work never mutates state. Follow the state contract for every
authorized mutation. Per-record F#/D# files are historical and never mutated by
Wayfinder; an affected current ledger write fails closed until manual project
reconciliation.
