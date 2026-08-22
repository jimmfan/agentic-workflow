# ADR-0006: Use an inert bootstrap payload

- Status: accepted
- Date: 2026-08-12

## Context

The framework must be distributed as one installable skill, but literal nested
`AGENTS.md`, `.agents`, or `.github` customization paths inside that skill may be
interpreted as active repository instructions. A mirrored payload also couples
source organization to target layout.

## Decision

Keep only the outer `agent-workflow/SKILL.md` active. Store installable policy
as `payload/root/AGENTS.md.template`, workflow resources under
`payload/skills`, and other repository data under inert payload paths. Record an
explicit source and target for every framework-owned file in the distribution
manifest. The adopter materializes those mappings and retains its existing
checksum ownership, conflict, merge, update, verification, and removal rules at
the target paths.

## Consequences

Browsing or installing the bootstrap skill does not activate the workflow it
distributes. Package structure can evolve without changing installed paths, and
verification can reject accidental active customization paths. The manifest is
slightly more explicit, but it is generated mechanically from the single package
version and payload files.

## Alternatives considered

- Mirror target paths inside `payload`: simpler copying, but nested agent
  customization files may be active.
- Encode all resources in Python strings: inert, but opaque, difficult to review,
  and awkward to checksum or edit.
- Depend on a package manager: unnecessary infrastructure for Markdown and JSON.
