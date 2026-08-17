# ADR-0018: Bundle the pinned provider projection

- Status: accepted
- Date: 2026-08-16
- Supersedes: provider installation conclusions in ADR-0007
- Amends: ADR-0010 and ADR-0014
- Preserves: ADR-0015 and ADR-0017

## Context

Agentic Workflow's runtime provider path used `gh skill install` once for every
missing declared skill. That made a usable routed provider depend on GitHub CLI
2.97+, its public-preview `skill` command, authentication, GitHub availability,
and network access after the framework itself was installed. The Harbor task
image demonstrated the concrete failure: core adoption succeeded, but all 14
declared provider directories remained absent because `gh skill` was not
available. The general evaluation harness intentionally avoided provider setup
to prevent that availability difference from confounding results.

The reviewed provider release is small and mechanically self-contained: the 14
declared Matt Pocock skill directories at `v1.2.3` contain 47 regular files and
their relative resources, with no selected symlinks, executables, submodules, or
runtime scripts. The annotated tag object
`835450ef244ab7335f75d95b83e7d979eae22a6d` resolves to commit
`6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`. The upstream repository is MIT
licensed. There is no immutable npm release artifact or uploaded GitHub release
asset that supplies the selected projection.

ADR-0015 and ADR-0017 still require Agentic Workflow-owned staging adaptations:
Wayfinder's local-state contract and the implicit-invocation metadata for To
Spec, To Tickets, and Implement. Existing project skill directories may contain
independent or user-modified content and must not be overwritten.

## Decision

Bundle exactly the tested 14-skill `gh skill install` projection from
`mattpocock/skills` tag `v1.2.3`, before Agentic Workflow adapters, plus the
upstream MIT license. Record the full resolved commit, annotated tag object,
upstream root tree, snapshot checksum, and per-skill GitHub tree metadata in the
release. Do not bundle the rest of the upstream repository.

Runtime install and update are fully offline:

1. validate the bundled checksum, exact declared inventory, source metadata,
   license, and safe regular-file shape;
2. copy the complete snapshot into temporary same-filesystem staging;
3. apply the existing Wayfinder and implicit-invocation adapters in staging;
4. validate the effective host metadata;
5. compare every declared target directory with the effective staged tree; and
6. if there are no conflicts, move every missing directory together, rolling
   back a partially completed move.

An exact effective target is reused without an ownership claim. A differing,
malformed, older, independently installed, or locally modified target is
preserved as a conflict. One conflict blocks every missing provider write so a
newly partial dependency graph is never exposed. Update does not automatically
replace or upgrade a conflict. Remove preserves every provider directory and
keeps cleanup manual; there is no provider ownership database.

Provider failure remains best-effort relative to the core. It reports a warning
but cannot roll back or invalidate successful core reconciliation.

Provider acquisition moves to a maintainer-only command that generates a new
candidate outside the package. It verifies that the annotated tag still resolves
to the declared commit, checks the root and each installed skill tree against
that commit, rejects local resource references that escape a selected skill,
copies the license, and prints the deterministic snapshot checksum. A maintainer
reviews the diff and updates provenance, adapters, tests, and documentation in a
normal Agentic Workflow release. There is no runtime remote fallback.

## Consequences

Fresh provider-enabled installs and future benchmarks no longer depend on task
image tooling, credentials, or network conditions. A benchmark can invoke the
normal lifecycle, record the Agentic Workflow revision, upstream commit,
effective Wayfinder hash, and `network=false`, while still keeping neutral,
normal-router, and explicit-Wayfinder conditions distinct.

The source distribution now carries about 140 KB of provider content and must
retain the MIT notice. Provider behavior remains stale until a reviewed Agentic
Workflow release refreshes it. Snapshot bytes are generated and checksummed to
make accidental hand edits fail closed, but this is not a general package
manager, dependency resolver, ownership ledger, or automatic update system.

Existing targets that differ from the new effective projection require manual
reconciliation. This includes a raw upstream user-only Wayfinder directory and
older Agentic Workflow-adapted bytes. Preserving those bytes is preferable to an
automatic migration because the framework cannot prove their ownership.

## Alternatives considered

- Keep runtime `gh skill install`: rejected because the demonstrated task-image
  failure blocks the provider selected by the router and makes experiments
  depend on unrelated environment availability.
- Bundle the entire upstream repository: rejected because it expands the
  reviewed surface beyond the tested composition closure.
- Download an archive at runtime: rejected because it retains network and remote
  availability as adoption prerequisites and adds a custom downloader.
- Hybrid bundled-plus-remote fallback: rejected because it creates two runtime
  sources of truth and weakens reproducibility without solving ownership.
- Track tag text without a commit: rejected because Git tags can move; the full
  resolved commit is the reproducible identity.
- Automatically replace old or modified targets: rejected because name and
  historical framework presence do not prove current ownership.
