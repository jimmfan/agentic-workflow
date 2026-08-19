---
description: Keep a lightweight structured map when important unknowns, decisions, dependencies, blockers, or conflicting facts are becoming unreliable to hold in ordinary context.
disable-model-invocation: false
metadata:
    github-path: skills/engineering/wayfinder
    github-pinned: v1.2.3
    github-ref: refs/tags/v1.2.3
    github-repo: https://github.com/mattpocock/skills
    github-tree-sha: 48c3a8b0a9705d6310d37f7f9b53bcb2c55955c7
name: wayfinder
---
# Wayfinder

Wayfinder keeps a lightweight durable map when important unknowns, decisions,
dependencies, blockers, or conflicting facts are becoming unreliable to hold
in ordinary context. Agentic Workflow's effective Wayfinder workflow is a
framework-owned runtime projection derived from Matt Pocock's Wayfinder
methodology. The pinned upstream snapshot remains unchanged as reviewed
provenance and reference; Agentic Workflow owns this runtime's routing,
Git-native state, effort selection, continuation, concurrency, U/E/F/D, and
`to-tickets` handoff contracts.

Use Wayfinder when structured project notes materially reduce the risk of
losing or conflating several consequential state distinctions. Explicit use is
allowed, and an explicit opt-out prevents automatic selection. Keep clear,
bounded, low-risk, unrelated, and read-only work on its minimum useful route;
one ordinary implementation detail or isolated unknown does not justify a map.

## Core invariants

- Route before inspecting Wayfinder state. Existing state never selects
  Wayfinder by itself, and considering or selecting Wayfinder does not require a
  write. An assessment may conclude that no durable Wayfinder state is needed.
- Name the destination and understand the territory before decomposing the
  route. Keep `map.md` at low resolution, represent fog honestly, identify the
  current frontier, and load detail only as it becomes relevant.
- `map.md` organizes the destination, boundary, major areas, and important
  seams. U/E/F/D classify current knowledge within that territory; they do not
  replace its structure. `map.md` alone is valid.
- Live source and accepted project artifacts outrank stale Wayfinder state.
  Reconcile only consequential current results, preserve conflicts honestly,
  and retire state when its navigational value disappears.
- Never decide an authority-dependent choice on the human's behalf. Surface the
  concrete question, explain why that authority is required, and state what the
  answer will unblock.
- Use the resolution mechanism that fits the uncertainty. Domain Modeling,
  Research, Prototype, Debugging, human clarification, or Grilling supplies
  reasoning, evidence, or clarification; Wayfinder preserves only consequential
  durable results.
- Wayfinder does not own implementation work items. Pass substantial
  dependency-ordered or independently deliverable work to `to-tickets` and
  link its canonical frontier without a shadow copy.

When Wayfinder is selected or a request continues a relevant effort, read
`.agent-workflow/contracts/wayfinder-state.md` before the map. Before an
authorized durable write, also read
`.agent-workflow/contracts/durable-state.md`. Those contracts own detailed
effort selection, paths, identifiers, links, locking, reconciliation,
settlement, and lifecycle mechanics. If the Wayfinder contract is missing, do
not invent tracker or `.scratch/` fallback state; treat the installation as
incomplete and stop safely or continue through another truthful authorized
route.

## Method

### Establish territory

First decide whether durable Wayfinder state is useful. For a new durable
effort, establish enough low-resolution structure to navigate: the destination,
scope boundary, major coherent areas or domains, and important relationships or
seams. Reuse accepted project structure when it already supplies those bearings.
If it does not, Domain Modeling is the preferred way to discover them before
substantial U/E/F/D state accumulates.

Derive the effort's identity, readable name, and stable path from that
understanding. Do not invent a directory name first and rationalize its purpose
afterward. Keep the semantic structure in `map.md`, using a short **Territory**
section or another clear shape; do not create nested area storage. On resume,
reuse a coherent map instead of rerunning structural discovery as ceremony.

Keep in-scope fog under **Not yet specified**, distinguish **Out of scope**, and
choose the smallest coherent unblocked next work as the frontier. Resolve
consequential uncertainty incrementally; each answer may reshape an area,
expose another unknown, change dependencies, or make new work takeable.

### Choose a resolution mechanism

- **Domain Modeling** — prefer it when a new effort's concepts, terminology,
  boundaries, areas, or relationships lack authoritative structure. It may also
  expose assumptions, unknowns, dependencies, and authority-dependent choices.
- **Research** — use for externally answerable uncertainty that needs
  trustworthy sources.
- **Prototype** — use when uncertainty is best resolved by trying something
  concrete and inexpensive.
- **Debugging** — use for uncertainty about observed behavior and its cause.
- **Human clarification or Grilling** — use for intent, preference, approval,
  prioritization, or another authority-dependent choice.

These activities keep their own native artifacts. Reconcile only consequential
results into the current effort: sharpen the Destination, map state, fog,
blockers, dependencies, frontier, or next work; create or retain U/E/F/D detail
only when independent durable value justifies it. Domain Modeling is
conditional, not ceremony for every new effort or resume.

When progress depends on human or project authority, do not infer the answer
from convenience, precedent, or an agent proposal. Surface the concrete
question, explain why that authority is required, state what the answer will
unblock, and leave the relevant uncertainty or blocker explicit. Do not turn an
assumed answer into an accepted D#, specification, or implementation ticket.

### Converge and shrink

Treat a semantic area as settled when no consequential fog remains there and
every durable outcome has reached its proper canonical owner or the workflow
that owns the resulting work. That owner may be an ADR, specification,
documentation or source, `to-tickets`, Implementation, another project-native
artifact, or nothing separate when the result has no independent long-term
value. Do not turn every area or D# into an ADR or ticket.

As areas settle, update the same semantic map, point to canonical outcomes, and
retire redundant U/E/F/D children under the state contract. If new evidence
changes the territory, reconcile its current areas and seams instead of keeping
parallel structures. Git preserves history. A completed effort should normally
shrink toward a concise map that records its outcome and canonical pointers.

If assessment finds no consequential uncertainty, dependency, blocker,
conflicting fact, or continuity need worth preserving, state that no durable
Wayfinder state is needed and continue or hand off through the minimum useful
route. Do not manufacture a map or child merely because Wayfinder was considered
or automatically selected.

## Work from the map

Route first. For a relevant resume, use an exact supplied map path when
available; otherwise follow the contract's progressive candidate-selection
rules. Read `map.md` first and only the child files or linked canonical
artifacts needed for the current question. If multiple efforts remain plausible,
ask the user rather than choosing, merging, or creating a synonym.

Keep `map.md` self-contained enough for a fresh session to recover the
destination, current state, blockers and dependencies, and smallest coherent
next work. Use readable names and links:

- U# is an unresolved consequential question.
- E# is independently useful evidence with provenance, scope, and limitations.
- F# is a sufficiently established scoped descriptive conclusion.
- D# is a committed choice made under project authority.

These are semantic distinctions, not a U# -> E# -> F# -> D# pipeline. The map
may be the whole current result. When an answer or project change matters,
reconcile the map and only independently useful child knowledge according to the
state contract.

Advance the frontier until the route is sufficiently clear, then continue the
authorized work, hand it to its owning workflow, or stop with next work explicit.
One coherent scope may pass directly to implementation. When substantial work
needs dependency ordering or separately deliverable sessions, use `to-tickets`;
its native artifacts remain canonical and the map records only the coordination
consequence.

## Boundaries

Read-only analysis, audit, diagnosis, or review may use Wayfinder reasoning but
must not create or update state. Authorized mutations follow the state
contract's concurrency and reconciliation rules; never improvise identifier,
lock, retirement, settlement, or lifecycle behavior in the runtime.

Do not create a Wayfinder `.scratch/` mirror, external issue-tracker mirror,
global active index, T# work items, automatic state migration, or a separate
settlement/archive subsystem.
