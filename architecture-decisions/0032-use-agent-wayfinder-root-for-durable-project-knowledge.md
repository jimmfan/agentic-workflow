# ADR-0032: Use `.agent-wayfinder` for durable project knowledge

- Status: accepted
- Date: 2026-08-22
- Amends: ADR-0010, ADR-0011, and ADR-0028

## Context

Wayfinder is now the sole framework-owned durable coordination layer. Its state
root should be clearly project-owned and distinct from the generic name of the
Wayfinder skill and methodology.

## Decision

The canonical durable project-knowledge root is `.agent-wayfinder/`. A
Wayfinder effort lives directly at `.agent-wayfinder/<effort>/`; there is no intermediate
`wayfinder/` directory. The root remains project-owned and opaque to lifecycle
operations. Other currently defined durable project artifacts use this root as
well.

Install, update, status, remove, and reinstall establish or preserve
`.agent-wayfinder/` but do not migrate, detect, alias, symlink, or parse an old
state root. Existing users manually rename `.wayfinder/` before updating when
they want that state to remain current.

## Consequences

Fresh Wayfinder efforts are easier to locate and share with humans without
changing effort structure, map-first semantics, lifecycle safety, or provider
methodology. This repository moves its tracked state once; new projects use the
new root directly.
