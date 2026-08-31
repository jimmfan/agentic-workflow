# Domain language normalization

## Objective

Keep Agent Workflow's canonical language coherent across routing, Wayfinder,
authority boundaries, packaged projections, documentation, and deterministic
tests while preserving the accepted Phase 2 design.

## Scope

Included:

- default-map authoring guidance and blocker semantics;
- the distinction among project decision authority, action authorization, host
  permission, and delegated technical judgment;
- the relationship between a U# unresolved-question record and unresolved
  consequential uncertainty that may block particular work;
- the identified ambiguous `settled`, `project-owned`, Current state, and nearby
  acceptance wording;
- synchronization of authored, packaged, runtime, generated, and installed
  surfaces; and
- focused semantic, structural, synchronization, and compatibility coverage.

Excluded:

- redesigning the 18-term glossary, U/E/F/D records, Wayfinder storage, routing
  architecture, provider integration, lifecycle behavior, or public interfaces;
- changing identifiers, provider schemas, lifecycle commands or statuses,
  `<skill>-handoff`, or `Derived from`;
- modifying pinned provider snapshots, adding an ADR, or creating migration or
  compatibility machinery; and
- another broad terminology or architecture audit.

## Areas and relationships

- **Canonical language:** [CONTEXT.md](../../CONTEXT.md) defines the 18 project
  terms and their bounded meanings.
- **Authority and policy:** [AGENTS.md](../../AGENTS.md), its
  [distributed template](../../skills/agent-workflow/payload/root/AGENTS.md.template),
  and [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md)
  maintain the operational separation among project choices, action
  authorization, host permission, and delegated technical judgment.
- **Wayfinder coordination:** the
  [state contract](../../skills/agent-workflow/payload/agent-workflow/contracts/wayfinder-state.md)
  and [runtime projection](../../skills/agent-workflow/runtime-projections/wayfinder.md)
  maintain map authoring, blocker, uncertainty, authority, and resumption
  semantics. Installed surfaces are reconstructable projections of these
  sources.
- **Routing and verification:** [routing](../../docs/routing.md),
  [verification guidance](../../docs/verification.md), and the focused
  [routing](../../skills/agent-workflow/tests/test_routing.py) and
  [Wayfinder](../../skills/agent-workflow/tests/test_wayfinder_state.py) tests
  protect cross-surface meaning and compatibility boundaries.

## Current state

- The accepted Phase 2 language is part of current project source. Current
  surfaces distinguish project decision authority from action authorization
  and host permission, use unresolved consequential uncertainty as the
  potentially blocking condition, preserve U# as the unresolved-question
  record, and retain delegated technical judgment within its authorized scope.
- The identified ambiguous `settled`, decision-related `project-owned`, and
  `semantic coordination state` constructions have been removed from current
  canonical prose while historical fixture names and identifiers remain
  available for compatibility coverage.
- One concrete inconsistency remains: current default-map guidance still
  requires new maps to retain `Blockers and dependencies` and write `None`.
  The accepted direction is that all default headings remain guidance rather
  than required schema; empty headings are omitted, while a map may state that
  no blocker or dependency applies when that information is useful.

## Blockers and dependencies

None.

## Ready work

- Remove the mandatory empty blocker-section convention from its current
  contract, runtime, documentation, verifier, and focused test surfaces while
  preserving the clarification that actual blockers and required inputs belong
  there and unfinished workflow steps do not.
- Review the already-made coherence changes only against the accepted correction
  scope and address concrete remaining mismatches without broadening the work.
- Run the documented deterministic verification and closing Standards and Spec
  review before treating the effort as complete.

## Key links

- [Project language](../../CONTEXT.md)
- [Architecture](../../docs/architecture.md)
- [Routing](../../docs/routing.md)
- [Verification](../../docs/verification.md)
- [Wayfinder state contract](../../skills/agent-workflow/payload/agent-workflow/contracts/wayfinder-state.md)
