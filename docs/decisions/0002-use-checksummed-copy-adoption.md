# ADR-0002: Use checksummed copy adoption

- Status: superseded by ADR-0010
- Date: 2026-08-11

## Context

Consuming projects need transparent files, easy reversal, local customization,
and updates without a package registry. Plain copy instructions cannot safely
distinguish framework updates from user edits.

## Decision

Use one Python standard-library bootstrap operation that resolves an immutable
source revision, validates an inert package, applies the payload, and verifies
the result. A deliberate lifecycle command applies by default; `--dry-run` is an
optional preview. Record the version, source revision, ownership origin, and
SHA-256 of framework-owned files. Cross-version update validates the installed
ownership record structurally and compares current bytes with its recorded
checksums. The new package authenticates its own payload; it does not carry a
historical predecessor catalog.

Treat providers as optional capability. Install the framework transactionally,
then attempt a separately staged provider transaction. A provider failure leaves
the valid framework installed and host-native workflows available. The provider
declaration owns repository, tag, paths, invocation policy, and configuration
requirements without duplicating upstream tree SHAs or complete inventories.
Record checksums of the bytes actually installed and use those checksums as
local ownership and cleanliness evidence. Reject unowned same-named directories.

Across a provider declaration change, preserve compatible origins, add missing
declared directories, and replace an incompatible directory only when local
state records it as created or reconstructed and every installed-file checksum
is clean. Preserve modified and pre-existing-compatible directories. Stage and
validate new provider bytes before replacement. On removal, delete only
checksum-clean framework files or provider directories locally recorded as
created. Preserve pre-install, reconstructed, incompatible, modified, extra-file,
undeclared, and project-owned paths.

Keep lifecycle ownership confined to framework files while establishing the
canonical `.ai-workflow-state/` directory during install and update. The
directory and every entry inside it are project-owned and excluded from the
framework ownership manifest. Lifecycle operations never seed profile, active,
or configuration files; authorized workflows create those lazily only when
useful context or cross-session continuity must be persisted. Migrate only the
four known development-era durable paths when the canonical directory is absent
or empty, preserve bytes, and reject conflicts rather than merging. Refuse a
framework update when any owned framework file conflicts.
Always compose root `AGENTS.md` and `CLAUDE.md` through explicit markers: the
framework owns the compact router/import and the project owns the editable
section beneath it, which starts empty when no file existed.
Record whether the composite was framework-created so removal can delete an
untouched empty shell or retain project instructions. Preflight removal against
local ownership records. Provider removal uses
same-filesystem quarantine renames: failures before every selected directory
and the state file are quarantined roll back; a cleanup failure after that commit
retains and reports the exact quarantine path instead of claiming rollback.
Run payload install/update integrity post-checks before committing the local
file transaction, restoring prior bytes and modes on failure. Provider update
has its own rollback boundary and does not undo a verified payload update. Remove only
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
Curated provider installation additionally depends on GitHub CLI, but provider
failure does not invalidate the framework installation. Normal runtime and inner
status checks remain repository-local; the public bootstrap uses HTTPS to fetch
the requested framework package.

ADR-0018 supersedes the first sentence above: provider projection is now sourced
from the framework release and needs no GitHub CLI or network access at runtime.

Provider origin and installed-hash history is repository-local ownership
evidence, not a tamper-evident authority. A deliberate coordinated state forgery
can reclassify a provider directory or its bytes. In ordinary operation,
recorded-hash and file-set comparison prevents automatic replacement or deletion
of modified or extra-file content.

Payload origin and composite-restoration history have the same local-trust
limit. A deliberate coordinated manifest forgery can reclassify exact canonical
managed bytes or restoration data. Without that forgery, modified, extra,
undeclared, or unique project content remains protected. This limitation is
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
