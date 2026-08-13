# ADR-0002: Use checksummed copy adoption

- Status: accepted
- Date: 2026-08-11

## Context

Consuming projects need transparent files, easy reversal, local customization,
and updates without a package registry. Plain copy instructions cannot safely
distinguish framework updates from user edits.

## Decision

Use a Python standard-library installer with dry-run-by-default commands. Record
the version, source Git revision when available, and SHA-256 of framework-owned
files. Seed project profile/state only when absent. Refuse an entire update when
any framework file conflicts. On removal, delete only checksum-matching framework
files created by the installer and preserve project-owned, pre-install, or
modified paths. Merge a pre-existing shared root `AGENTS.md` through explicit managed
markers, authenticate removal against the same source version, preflight
mutations, and roll back ordinary write failures.

## Consequences

Repository contents remain visible and reversible, with no runtime dependency.
Updates do not merge customized managed blocks or same-named skills, so
maintainers must reconcile conflicts. Users must obtain a newer source checkout
to update and retain dirty local source copies for exact recovery.

Requirements-audit note (2026-08-12): this tested adopter is a later expansion
beyond the original 4–8-file version-1 and “do not prematurely build a
distribution system” preference. It is retained because later requirements made
safe adoption, update, and removal part of the implemented scope. It remains
outside runtime routing and is not evidence that the original source-file-count
preference was met.

## Alternatives considered

- Repository template: excellent initial creation but weak incremental updates.
- Manual copy: smallest tooling but unsafe overwrite and poor version tracking.
- Git subtree/submodule: versioned but adds Git workflow complexity and awkward
  project-owned customization.
- Package registry: updateable but unnecessary infrastructure for Markdown files.
