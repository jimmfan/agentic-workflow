# ADR-0010: Separate framework output from project-owned state

- Status: accepted
- Date: 2026-08-14

## Context

Agent Workflow must be able to install, repair, update, and remove the files it
manages without risking unique information owned by the project or user.
Reconstructable framework output does not justify package-manager machinery;
the ownership boundary should protect project data and core routing directly.

The source package also contains policies and skill resources destined for an
installed repository. The supported bootstrap and adoption path needs an
explicit activation boundary between stored package resources and their
installed host discovery locations.

## Decision

Separate reconstructable framework output from preservation boundaries:

- `.agent-workflow/` and the finite set of declared provider directories are
  reconstructable output. Lifecycle operations converge them to the current
  declared state without requiring historical ownership or checksum evidence.
  Unrelated skill directories remain independent; local edits inside a declared
  provider name are disposable.
- `.agent-wayfinder/` is project-owned durable state. Lifecycle operations may
  establish its root when absent but otherwise treat the entire tree as opaque:
  they do not inventory, interpret, migrate, rewrite, or remove its contents.
- Managed regions in composite project files and required external integration
  paths use only the evidence necessary to avoid overwriting or deleting
  ambiguous project or user content. Uncertainty stops mutation.
- The supported bootstrap and adoption path keeps distributable root policies
  under non-active template names and activates framework resources only by
  projecting explicit source-to-target mappings into host discovery locations.

Prefer current desired-state reconciliation over package-manager-style history,
compatibility, or migration machinery. Add deeper lifecycle machinery only
after a concrete current failure shows it is needed to protect project-owned
data or make core routing reliable.

## Consequences

Missing, modified, obsolete, or extra reconstructable files can be repaired
from current package bytes. Project-owned state and ambiguous external content
remain hard preservation boundaries. Provider failure does not invalidate an
otherwise successful core lifecycle operation.

The distribution manifest, external-write evidence, staging, validation,
rollback, archive limits, supported runtimes, and provider adapters are current
implementation and contract details. They belong in architecture documentation,
source, and tests rather than this decision.

## Alternatives considered

- Preserve historical ownership and restoration metadata for every framework
  file: rejected because reconstructable output does not justify a package
  manager before 1.0.
- Treat every target as replaceable: rejected because durable state, composite
  project regions, and unknown external content may contain unique information.
- Mirror installed root-policy and host-customization paths literally inside
  the distributable package: rejected because supported adoption needs a clear
  activation boundary.
- Discover and remove arbitrary provider directories: rejected because only the
  finite declared provider set is framework-owned.

## Reconsideration trigger

Reconsider when a concrete data-loss or core-routing failure cannot be handled
by current desired-state reconciliation and host or provider capabilities.
