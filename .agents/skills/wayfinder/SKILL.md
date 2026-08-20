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

Wayfinder is Agentic Workflow's sole framework-owned durable coordination
layer. Use it when consequential state needs reliable continuity across
sessions, handoffs, owners, or interacting areas. Clear bounded work, one
isolated unknown, and read-only work stay on their minimum useful route.

This framework-owned runtime projection is derived from Matt Pocock's
Wayfinder methodology. It chooses how to navigate and resolve the frontier;
`.agent-workflow/contracts/wayfinder-state.md` owns state mechanics.

## Core invariants

- Route before inspecting state; an existing map never selects Wayfinder.
- Name the destination and territory before decomposing work. Keep `map.md`
  low-resolution and load detail only when relevant.
- The map owns current state, blockers, dependencies, frontier, and next work.
  Optional U/E/F/D preserves only independently useful knowledge.
- Live source and accepted project artifacts outrank stale map state.
- Never decide an authority-owned choice. Keep the question and what it blocks
  explicit.

When selecting or resuming Wayfinder, read the state contract before the map.
It defines effort selection, paths, identifiers, locking, reconciliation,
settlement, and lifecycle. Do not load the general durable-state contract merely
to write Wayfinder state.

## Establish territory

Reuse accepted project structure when it supplies the destination, scope,
areas, and important seams. Otherwise establish the smallest useful structure
directly. Load Domain Modeling only when structural or vocabulary ambiguity
prevents a coherent map. Derive the effort name and stable path from that
territory, and reuse it on resume.

## Resolve the frontier progressively

Continue directly when the frontier can be resolved safely without additional
methodology. Load only the smallest specialist whose method would materially
improve resolution:

- **Discovery** for consequential alternatives and tradeoffs.
- **Debugging** for an observed behavior with an unknown cause.
- **Research** for external uncertainty needing primary-source evidence.
- **Prototype** when a disposable experiment is the cheapest honest test.
- **Domain Modeling** when concepts, boundaries, or vocabulary block progress.
- **Human clarification or Grilling** for authority, intent, preference, or
  prioritization.

Do not load specialists speculatively. Specialists own their methods and native
artifacts and create no framework continuity record. If work is interrupted,
reconcile only the consequential frontier, evidence or conclusions, artifact
pointers, resolution mode when useful, and next work into Wayfinder. The map,
not DEC/IMP/DBG or a specialist notebook, is the re-entry point.

## Reconcile and hand off

Keep the map sufficient for a fresh session to recover the destination,
current state, blockers, dependencies, and smallest coherent next work. Link
canonical artifacts instead of copying them. The state contract defines when
U/E/F/D detail is worth retaining and how settled state shrinks.

Hand one coherent ready scope and its acceptance criteria to Implementation;
Verification follows execution. Use `to-tickets` only when approved work needs
dependency ordering or independently deliverable sessions, and link its native
frontier without a shadow copy.

Read-only work never mutates state. Follow the state contract for every
authorized mutation. Legacy project-owned records remain untouched historical
data.
