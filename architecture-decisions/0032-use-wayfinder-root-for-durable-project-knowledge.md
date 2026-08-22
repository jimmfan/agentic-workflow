# ADR-0032: Use the Wayfinder root for durable project knowledge

- Status: accepted
- Date: 2026-08-22
- Amends: ADR-0010, ADR-0011, and ADR-0028

## Context

Wayfinder is now the sole framework-owned durable coordination layer. Keeping
its project knowledge below `.agent-workflow-state/wayfinder/` adds a redundant
namespace and makes the state less discoverable to people working directly in a
repository.

## Decision

The canonical durable project-knowledge root is `.wayfinder/`. A Wayfinder
effort lives directly at `.wayfinder/<effort>/`; there is no intermediate
`wayfinder/` directory. The root remains project-owned and opaque to lifecycle
operations. Other currently defined durable project artifacts use this root as
well.

Install, update, status, remove, and reinstall establish or preserve
`.wayfinder/` but do not migrate, alias, symlink, or parse an old state root.
Existing `.agent-workflow-state/` data is historical project data unless a
project owner deliberately moves it.

## Consequences

Fresh Wayfinder efforts are easier to locate and share with humans without
changing effort structure, map-first semantics, lifecycle safety, or provider
methodology. Current state moves once with the repository; new projects use the
shorter root directly.
