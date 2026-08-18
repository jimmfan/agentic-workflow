# ADR-0011: Use project-owned Git-native Wayfinder state

- Status: accepted
- Date: 2026-08-14
- Supersedes: local Wayfinder artifact and pointer portions of ADR-0007
- Amended by: ADR-0012, ADR-0013, ADR-0016, ADR-0020, and ADR-0022

## Context

The pinned Wayfinder provider supplies a strong multi-session planning method:
a low-resolution destination map, decision-oriented investigation, fog of war,
dependency-derived frontier work, and progressive loading of child detail. Its
configured issue tracker owns physical storage. The upstream local-Markdown
default uses `.scratch/<effort>/map.md` and child issue files.

Agentic Workflow already reserves `.agent-workflow-state/` for project-owned
durable continuity and guarantees that lifecycle operations never own its
contents. Keeping local Wayfinder state elsewhere would split durable planning
across ownership roots, while pointing to it through a separate global index
would add unnecessary continuity state. The project also needs explicit unknown,
evidence, fact, and decision identities without introducing an external tracker
or service.

## Decision

Configure local Wayfinder persistence as the canonical project-owned tree under
`.agent-workflow-state/wayfinder/<effort>/`. Use `map.md` plus optional stable
`U#`, `E#`, `F#`, and `D#` Markdown files. Keep the map low resolution and make
it the owner of current state, blockers, dependencies, and next work. Load child
bodies only when relevant. ADR-0022 moves executable work out of the current
representation; substantial decomposition belongs to `to-tickets`.

The upstream provider continues to own Wayfinder reasoning. Agentic Workflow
owns this local storage and re-entry contract plus the narrow effective-
instruction adapter later consolidated in ADR-0020. The local tree is the native
configured representation, not a mirror of `.scratch/` or an external tracker.
The relevant effort map is the re-entry point. ADR-0012 later removes the global
active index for non-Wayfinder workflows as well; those workflows resume from
their canonical record.

Keep the Markdown contract permissive. Lifecycle code treats every byte below
`.agent-workflow-state/` as opaque project data. Agents may recommend compact
authoring shapes, but install, update, status, and remove do not validate,
inventory, migrate, checksum, rewrite, or delete them.

## Consequences

Long-running local planning survives framework replacement and Git provides its
history. A normal request pays only one small root routing hint; the detailed
contract, map, and relevant child files load progressively. Merely having an
effort on disk does not route unrelated work through Wayfinder.

This deliberately differs from the pinned provider's default `.scratch/` local
tracker and from its single decision-ticket representation. The divergence is
limited to the configured local storage boundary: provider concepts such as
Destination, Decisions so far, Not yet specified, Out of scope, named links,
and dependency-derived frontier remain intact. Optional U/E/F/D files separate
unresolved questions, sourced observations, established conclusions, and
committed choices without forcing bookkeeping or adding a database or graph
model. A map-only effort remains valid.

The framework contract is distributed under `.agent-workflow/`, but no project
state below `.agent-workflow-state/wayfinder/` is placed in the distribution
manifest. Lifecycle performs no migration, and Jira or other external
synchronization remains out of scope.

## Alternatives considered

- Keep upstream `.scratch/` storage and add a framework pointer: rejected
  because it splits local durable state and requires separate index indirection.
- Copy provider artifacts into `.agent-workflow-state/`: rejected because two
  canonical copies would drift.
- Add a database, event log, graph index, or persisted frontier: rejected
  because Markdown links, dependencies, agent reasoning, and Git already cover
  the required behavior.
- Validate a strict Markdown schema: rejected because ordinary human edits are
  project-owned and should not make lifecycle or routing unsafe.
