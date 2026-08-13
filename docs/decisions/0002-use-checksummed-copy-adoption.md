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
the result. Coordinate the local payload transaction with a separately
checksummed provider transaction; preflight both before writes. A deliberate
lifecycle command applies by default; `--dry-run` is an optional preview. Record
the version, immutable Git revision, and SHA-256 of framework-owned files. For
provider directories also record whether each was framework-created or already
compatible, plus every file checksum. Seed project profile/state only when
absent. Refuse an entire update when any framework file conflicts. On removal,
delete only checksum-matching framework files or provider directories created
by the installer and preserve project-owned, pre-install, or modified paths.
Always compose root `AGENTS.md`
through explicit markers: the framework owns the compact router and the project
owns the editable section beneath it, which starts empty when no file existed.
Record whether the composite was framework-created so removal can delete an
untouched empty shell or retain project instructions. Authenticate removal
against the same source revision, preflight mutations, and roll back ordinary
write failures.

## Consequences

Repository contents remain visible and reversible, with no runtime dependency.
Updates do not merge customized managed blocks or same-named skills, so
maintainers must reconcile conflicts. Project edits beneath the `AGENTS.md`
project marker do not dirty the installation and survive update and removal.
Clean framework-created policies from earlier installations migrate to the
composite layout during update; locally changed legacy policies fail closed.
Lifecycle operations resolve their package automatically; installed runtime
behavior does not depend on the bootstrap skill or a local distribution checkout.
Curated provider installation additionally depends on GitHub CLI during install
or a declared upgrade, but normal runtime and status remain repository-local.

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
