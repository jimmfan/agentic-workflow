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
cross-version migration, make the immutable new package own explicit accepted
predecessor records. Select one only when framework version, exact source
revision, installation-manifest schema, complete managed-path key set, and every
source SHA-256 match; reject an unknown, partial, or forged identity before
planning writes or retirements. Keep these reviewed historical records separate
from generated current-payload checksums so manifest refresh cannot invent a
trust relationship. For provider directories, make the immutable package declaration own each file's
repository/tag/revision, path, subtree SHA, complete inventory, and invocation
contract. Do not make precomputed upstream file hashes an installed-output
requirement. Reject unowned same-named directories, record framework-created
ownership plus checksums of the bytes actually installed, and use those
checksums as local cleanliness evidence. Seed
project profile/state only when absent. Refuse an entire update when any
framework file conflicts.

Across a provider declaration change, require the new package to authenticate
the exact predecessor payload, its installed `providers.json`, and the provider
state identity/inventory before planning migration. Preserve the origin of
directories already compatible with the new declaration and install genuinely
missing declared directories. Replace an incompatible directory only when the
authenticated predecessor recorded it as created, its full metadata/inventory
still matches that declaration, and every installed-file checksum is clean.
Modified, pre-existing-compatible, unknown, partial, and inconsistent cases fail
closed. Stage and authenticate the complete new baseline before applying all
validated transitions. On removal, delete only checksum-matching framework files
or exact declared provider directories that are package-authentic,
record-checksum-clean, and recorded as created. Preserve pre-install,
incompatible, modified, extra-file, undeclared, and project-owned paths.
Always compose root `AGENTS.md` and `CLAUDE.md` through explicit markers: the
framework owns the compact router/import and the project owns the editable
section beneath it, which starts empty when no file existed.
Record whether the composite was framework-created so removal can delete an
untouched empty shell or retain project instructions. Authenticate removal
against the same source revision and preflight mutations. Provider removal uses
same-filesystem quarantine renames: failures before every selected directory
and the state file are quarantined roll back; a cleanup failure after that commit
retains and reports the exact quarantine path instead of claiming rollback.
Run payload install/update integrity post-checks before committing the local
file transaction, restoring prior bytes and modes on failure. During update,
commit that payload transaction inside the provider rollback window so a later
failure restores predecessor provider directories and exact state. Remove only
transaction-created parent directories during rollback; do not prune untracked
empty parents after a successful removal.

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
or a declared upgrade. Normal runtime and the inner status checks remain
repository-local after the exact package is loaded; the public bootstrap uses
HTTPS to fetch that recorded package before invoking them.

Provider origin and installed-hash history is repository-local ownership
evidence, not a tamper-evident authority. A deliberate coordinated state forgery
can reclassify a provider directory or its bytes. In ordinary operation,
recorded-hash comparison plus declaration inventory bounds prevent automatic
replacement or deletion of modified, extra-file, or undeclared content.

Payload origin and composite-restoration history have the same local-trust
limit. A deliberate coordinated manifest forgery can reclassify exact canonical
managed bytes or substitute an exact current/audited historical canonical
policy identity; it cannot authorize an invented source identity or deletion of
modified, extra, undeclared, or unique project content. This limitation is
accepted because removal remains useful and the framework deliberately has no
external state service. A stronger historical-origin guarantee would require
either never deleting exact installed content automatically or storing a trust
anchor outside the target repository.

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
