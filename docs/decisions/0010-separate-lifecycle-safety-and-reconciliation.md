# ADR-0010: Simplify v0 around routing reliability and project-data safety

- Status: accepted
- Date: 2026-08-14
- Supersedes: ADR-0002, provider lifecycle portions of ADR-0007, ADR-0009

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
6. Generated package checksums remain a strict maintainer/CI/release contract but
   are not a runtime availability dependency.
7. Optional providers have no framework ownership database. Install only missing
   skills on a best-effort basis, preserve every existing directory, and make
   cleanup manual. Provider failure never changes core success.
8. Remove the shared lifecycle controller, host hook adapters, and observability
   analyzer. The root policy and detailed routing document are the runtime; an
   optional route marker is enough v0 visibility.
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

Provider updates no longer replace an installed provider baseline, and removal
does not clean provider directories automatically. This is an intentional v0
trade-off; the user can inspect and manage those independent directories.

The framework no longer claims deterministic hook enforcement, live host
capability detection, telemetry normalization, provider provenance, or package
integrity at runtime. Host sandboxing, approval, and instruction adherence remain
the applicable controls.

Release metadata can be stale in a locally modified package and runtime may
still reconcile from its actual source bytes. The release verifier must catch
that drift before publication.

## Rejected alternatives

- Extend the checksum/origin model with more recovery states: rejected because
  it preserves the accidental package manager.
- Treat every target as replaceable: rejected because composite project regions,
  durable state, and unknown external paths contain or may contain user data.
- Keep controller and telemetry code disabled: rejected because dormant public
  contracts still impose maintenance and verification cost.
- Delete providers on remove based on current names: rejected because name
  matching does not prove framework ownership.
- Remove all transactions: rejected because a mid-operation error around
  composite/external writes could leave a partially applied lifecycle change.

## Reconsideration trigger

Revisit a deferred subsystem only after a concrete current failure shows it is
needed to protect project data or make core routing reliable, and after simpler
host or provider mechanisms prove insufficient.
