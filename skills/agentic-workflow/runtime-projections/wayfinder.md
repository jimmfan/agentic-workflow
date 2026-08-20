# Wayfinder

Wayfinder is Agentic Workflow's sole framework-owned durable coordination
layer. Use it when structured project notes materially reduce the risk of
losing or conflating consequential state across sessions, handoffs, owners, or
interacting areas. Clear bounded work, one isolated unknown, and read-only work
stay on their minimum useful route. Assessment may conclude that no durable map
is needed.

This framework-owned runtime projection covers Git-native effort selection,
continuation, concurrency, U/E/F/D, reconciliation, convergence, and the
`to-tickets` boundary. It is derived from Matt Pocock's Wayfinder methodology;
the pinned snapshot remains reviewed provenance.

## Core invariants

- Route before inspecting state. Existing state never selects Wayfinder.
- Name the destination and understand the territory before decomposing the
  route. Keep `map.md` low resolution, represent fog honestly, identify the
  current frontier, and load detail only when relevant.
- `map.md` organizes destination, boundary, areas, seams, current state,
  blockers, dependencies, and next work. Optional U/E/F/D classify current
  knowledge; they do not replace the map.
- Live source and accepted project artifacts outrank stale map state. Reconcile
  consequential changes and retire state when its navigational value ends.
- Never decide an authority-dependent choice for the human or project. Keep the
  concrete question and what it blocks explicit.
- Wayfinder owns coordination, not every reasoning method or executable work
  item. Specialists remain stateless from the framework's perspective.

When selected or resuming a relevant effort, read
`.agent-workflow/contracts/wayfinder-state.md` before the map. That contract owns
paths, effort selection, identifiers, links, locking, settlement, and lifecycle
mechanics. Do not load `.agent-workflow/contracts/durable-state.md` merely to
write Wayfinder state. If the Wayfinder contract is missing, do not invent a
tracker, specialist record, or `.scratch/` fallback.

## Establish territory

For a new durable effort, establish enough structure to navigate: destination,
scope boundary, major coherent areas or domains, and important relationships or
seams. Reuse accepted project structure when it supplies those bearings. When
material ambiguity in concepts, terminology, boundaries, or relationships
prevents that, Domain Modeling may help; it is never setup ceremony.

Derive the readable effort name and stable path from that understanding. Keep
in-scope fog under **Not yet specified**, distinguish **Out of scope**, and
choose the smallest coherent unblocked frontier. On resume, reuse a coherent
map instead of rediscovering its structure.

## Resolve the frontier progressively

Continue directly when the frontier can be resolved safely without additional
methodology. Load only the smallest specialist whose method would materially
improve resolution. An obvious specialist choice inside a selected Wayfinder
effort does not require the detailed router.

- **Discovery** may help when a consequential choice benefits from explicit
  alternative and tradeoff analysis.
- **Debugging** may help when observed behavior has an unknown cause.
- **Research** may help when an externally answerable question warrants a
  primary-source, cited artifact; a simple lookup stays direct.
- **Prototype** may help when a concrete disposable experiment is the cheapest
  honest way to learn.
- **Domain Modeling** may help when structural or vocabulary ambiguity blocks a
  coherent territory or decision.
- **Human clarification or Grilling** may help with intent, preference,
  approval, prioritization, or another authority-owned choice.

Do not load several specialists speculatively. Each selected specialist owns its
method and native artifacts but creates no DEC, IMP, DBG, or other framework
continuity record. If specialist work must continue later, reconcile only its
consequential frontier, evidence or conclusions, useful artifact pointers,
resolution mode when useful, and next work into Wayfinder. Do not copy the
specialist method or transcript into the map.

When authority is required, surface the concrete question, why that authority
is required, and what the answer unblocks. An assumption cannot become an
accepted D#, specification, ticket, or implementation direction.

## Reconcile, converge, and hand off

Keep `map.md` sufficient for a fresh session to recover the destination,
current state, blockers, dependencies, and smallest coherent next work. Use
readable links and optional current knowledge only when it has independent
value:

- U# is an unresolved consequential question.
- E# is useful evidence with provenance, scope, and limitations.
- F# is a sufficiently established scoped descriptive conclusion.
- D# is a committed choice made under project authority.

These are distinctions, not a U# -> E# -> F# -> D# pipeline. The map may be the
whole result.

An area is settled when no consequential fog remains and every durable outcome
has reached its canonical project owner or owning workflow. Reconcile the map,
point to those outcomes, and retire redundant children under the state
contract. A completed effort should shrink toward a concise map rather than
become a permanent investigation warehouse.

When one coherent scope is ready, hand it to Implementation with its acceptance
criteria and canonical map, specification, or decision. Implementation owns
execution and Verification follows it; neither is a Wayfinder reasoning method
or durable record. When approved work needs dependency ordering or separately
deliverable sessions, use `to-tickets` and link its native frontier without a
shadow copy.

## Boundaries

Read-only analysis, audit, diagnosis, or review may use structured reasoning but
must not create or update state. Authorized mutations follow the Wayfinder
contract; never improvise identifiers, locking, retirement, settlement, or
lifecycle behavior.

Do not create specialist persistence records, a Wayfinder `.scratch/` mirror,
external tracker mirror, global active index, T# work items, automatic state
migration, or replacement lifecycle machinery. Legacy project-owned records
remain untouched historical data.
