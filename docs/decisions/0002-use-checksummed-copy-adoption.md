# ADR-0002: Use checksummed copy adoption

- Status: accepted
- Date: 2026-08-11

## Context

Consuming projects need transparent files, easy reversal, local customization,
and updates without a package registry. Plain copy instructions cannot safely
distinguish framework updates from user edits.

## Decision

Use one Python standard-library bootstrap operation that resolves an immutable
source revision, validates an inert package, applies the payload, and verifies
the result. A deliberate lifecycle command applies by default; `--dry-run` is an
optional preview. Record the version, immutable Git revision, and SHA-256 of
framework-owned files. Seed project profile/state only when absent. Refuse an
entire update when any framework file conflicts. On removal, delete only
checksum-matching framework files created by the installer and preserve
project-owned, pre-install, or modified paths. Merge a pre-existing shared root
`AGENTS.md` through explicit managed markers, authenticate removal against the
same source revision, preflight mutations, and roll back ordinary write failures.

## Consequences

Repository contents remain visible and reversible, with no runtime dependency.
Updates do not merge customized managed blocks or same-named skills, so
maintainers must reconcile conflicts. Lifecycle operations resolve their package
automatically; installed runtime behavior does not depend on the bootstrap skill
or a local distribution checkout.

The distribution payload uses explicit inert source-to-target mappings rather
than mirroring live `AGENTS.md` or `.agents` paths inside the bootstrap skill.
This prevents the package itself from accidentally participating in agent
customization discovery.

## Alternatives considered

- Repository template: excellent initial creation but weak incremental updates.
- Manual copy: smallest tooling but unsafe overwrite and poor version tracking.
- Git subtree/submodule: versioned but adds Git workflow complexity and awkward
  project-owned customization.
- Package registry: updateable but unnecessary infrastructure for Markdown files.
