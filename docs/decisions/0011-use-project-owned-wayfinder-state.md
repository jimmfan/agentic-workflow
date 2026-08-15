# ADR-0011: Use project-owned Git-native Wayfinder state

- Status: accepted
- Date: 2026-08-14
- Supersedes: local Wayfinder artifact and pointer portions of ADR-0007
- Amended by: ADR-0012

## Context

The pinned Wayfinder provider supplies a strong multi-session planning method:
a low-resolution destination map, decision-oriented investigation, fog of war,
dependency-derived frontier work, and progressive loading of child detail. Its
configured issue tracker owns physical storage. The upstream local-Markdown
default uses `.scratch/<effort>/map.md` and child issue files.

Agentic Workflow already reserves `.ai-workflow-state/` for project-owned
durable continuity and guarantees that lifecycle operations never own its
contents. Keeping local Wayfinder state elsewhere would split durable planning
across ownership roots, while pointing to it through a separate global index
would add unnecessary continuity state. The project also needs explicit unknown,
decision, and executable-work identities without introducing an external
tracker or service.

## Decision

Configure local Wayfinder persistence as the canonical project-owned tree under
`.ai-workflow-state/wayfinder/<effort>/`. Use `map.md` plus stable `U#`, `D#`,
and `T#` Markdown files. Keep the map low resolution, derive frontier work from
current item status and dependencies, and load child bodies only when relevant.

The upstream provider continues to own Wayfinder reasoning. Agentic Workflow
owns only this local storage and re-entry contract. The local tree is the native
configured representation, not a mirror of `.scratch/` or an external tracker.
The relevant effort map is the re-entry point. ADR-0012 later removes the global
active index for non-Wayfinder workflows as well; those workflows resume from
their canonical record.

Keep the Markdown contract permissive. Lifecycle code treats every byte below
`.ai-workflow-state/` as opaque project data. Agents may recommend compact
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
and dependency-derived frontier remain intact. Separate U/D/T files make
uncertainty, durable decisions, and implementation handoff explicit without a
database or graph model.

The framework contract is distributed under `.ai-workflow/`, but no project
state below `.ai-workflow-state/wayfinder/` is placed in the distribution
manifest. No migration is introduced, and Jira or other external
synchronization remains out of scope.

## Alternatives considered

- Keep upstream `.scratch/` storage and add a framework pointer: rejected
  because it splits local durable state and requires separate index indirection.
- Copy provider artifacts into `.ai-workflow-state/`: rejected because two
  canonical copies would drift.
- Add a database, event log, graph index, or persisted frontier: rejected
  because Markdown links, dependencies, agent reasoning, and Git already cover
  the required behavior.
- Validate a strict Markdown schema: rejected because ordinary human edits are
  project-owned and should not make lifecycle or routing unsafe.
