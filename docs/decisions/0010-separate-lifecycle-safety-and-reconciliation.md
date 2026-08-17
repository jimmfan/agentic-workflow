# ADR-0010: Simplify v0 around routing reliability and project-data safety

- Status: accepted
- Date: 2026-08-14
- Supersedes: ADR-0002, provider lifecycle portions of ADR-0007, ADR-0009
- Amended by: ADR-0020

## Context

The pre-1.0 implementation accumulated package-manager behavior: per-file
framework checksums, origin states, encoded restoration data, retirement
catalogs, provider inventories and upgrade transactions, a shared hook
controller, host capability adapters, and an observability normalizer. Tests and
documentation then defended those mechanisms as public contracts.

Most of that complexity did not protect unique project data or make minimum
workflow routing more reliable. It also caused missing or modified
reconstructable files to be treated like forensic integrity failures, increasing
the chance that lifecycle maintenance itself would become the product's main
failure mode.

The source project is pre-1.0. The engineering priority is to protect
project/user-owned data and keep core routing reliable; other features should be
simple, replaceable, optional, best-effort, or CI-only.

## Decision

Adopt current desired-state reconciliation with explicit ownership classes.

1. `.ai-workflow/` is entirely reconstructable. Stage and replace it from the
   current mapping. Missing, drifted, extra, and obsolete contents require no
   historical checksum proof.
2. `.ai-workflow-state/` is entirely project-owned. Never inventory or mutate
   its current contents. Compatibility migration is limited to four named old
   locations and stops on a differing destination.
3. `AGENTS.md` and `CLAUDE.md` use one parsed managed region and byte-preserved
   project region. Ambiguous markers stop before mutation.
4. Other external integration paths use the minimum evidence needed for safe
   deletion: created/pre-existing and a last-written hash. Unknown collisions
   are preserved and block writes.
5. Obsolete external paths come only from the previous local install manifest.
   Missing is a no-op; unchanged created content may be removed; uncertain
   content is preserved. Keep no global retirement history.
6. The distribution manifest records only the current framework version and
   explicit source-to-target install map. The maintainer verifier compares that
   map with the current payload inventory, but ordinary content edits use current
   package bytes and require no generated checksum refresh.
7. Optional providers have no ownership database. The finite declared provider
   projection is reconstructable framework output: install/update replaces
   missing or different declared directories transactionally, remove deletes
   exactly those declarations, and unrelated skill directories are preserved.
   Provider failure never changes core success.
8. Remove the shared lifecycle controller, host hook adapters, and observability
   analyzer. The root policy and detailed routing document are the runtime; one
   required response marker provides v0 route visibility without triggering
   additional workflow work.
9. Keep archive/path/link/special-entry/root/symlink safety, narrow durable-state
   conflict checks, rollback around external/composite mutation, Python 3.11+,
   and ASCII/cp1252-safe CLI presentation.

The new install manifest schema is intentionally small: version, revision,
external deletion evidence, and composite creation evidence. A narrow reader
extracts only data-safety evidence from the prior pre-1.0 manifest.

## Consequences

Framework repair is predictable: update converges to current bytes even after a
file is deleted or edited. Historical absence is irrelevant. Project-state and
unknown external data retain hard preservation boundaries.

Provider lifecycle owns only the finite declared projection. Custom skills stay
outside those names; edits within a declared provider directory are disposable.

The framework no longer claims deterministic hook enforcement, live host
capability detection, telemetry normalization, provider provenance, or package
integrity at runtime. Host sandboxing, approval, and instruction adherence remain
the applicable controls.

Ordinary payload content edits create no release-metadata churn. Adding,
removing, or remapping a packaged file—or changing the framework version—makes
the explicit distribution map stale until a maintainer reviews and refreshes
it. Runtime reconciliation always uses the actual mapped source bytes.

## Rejected alternatives

- Extend the checksum/origin model with more recovery states: rejected because
  it preserves the accidental package manager.
- Keep generated payload checksums as CI-only release metadata: rejected because
  Git and the validated immutable archive already identify package bytes, while
  content-only staleness adds maintenance cost without protecting project data
  or routing reliability.
- Treat every target as replaceable: rejected because composite project regions,
  durable state, and unknown external paths contain or may contain user data.
- Keep controller and telemetry code disabled: rejected because dormant public
  contracts still impose maintenance and verification cost.
- Delete arbitrary providers on remove based on discovery: rejected because only
  the finite declared projection is framework-owned.
- Remove all transactions: rejected because a mid-operation error around
  composite/external writes could leave a partially applied lifecycle change.

## Reconsideration trigger

Revisit a deferred subsystem only after a concrete current failure shows it is
needed to protect project data or make core routing reliable, and after simpler
host or provider mechanisms prove insufficient.

ADR-0020 records the concrete provider failures and amends item 7. The exact
effective projection is sourced from the release, staged and validated as a
whole, and reconciled transactionally without a target ownership database.
