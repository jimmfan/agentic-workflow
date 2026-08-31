# ADR-0010: Separate framework output from project-owned state

- Status: accepted
- Date: 2026-08-14

## Context

Agent Workflow must be able to install, repair, update, and remove the files it
manages without risking unique information owned by the project or user.
Framework-owned reconstructable output should converge to current desired state;
it does not justify package-manager machinery or manual migration ceremony.

The source package also contains policies and skill resources destined for an
installed repository. The supported bootstrap and adoption path needs an
explicit activation boundary between stored package resources and their
installed host discovery locations. Agent Workflow is pre-1.0, has one current
user, and operates only in Git-tracked projects, so Git can provide the recovery
boundary instead of an installation-history database.

## Decision

Separate framework-owned reconstructable output from preservation boundaries:

- `.agent-workflow/` is one framework-owned reconstructable surface. Install and
  update may replace it completely with current package bytes, removing missing,
  modified, obsolete, or extra content as ordinary desired-state convergence.
- For skills, each current curated `.agents/skills/<name>/` directory is likewise
  a complete framework-owned reconstructable surface. Install and update replace
  each complete named surface; remove deletes it. Unrelated skill directories
  remain independent and are not deleted or interpreted through historical skill
  inventories. A current curated name is reserved when Agent Workflow is adopted,
  so a project-owned skill with the same name must be moved or renamed before
  installation.
- `.agent-wayfinder/` is project-owned durable state. Lifecycle operations do
  not directly traverse, interpret, or change it. Repository-wide Git
  cleanliness checks may still observe changes under it.
- `AGENTS.md` is a composite project file. In current desired state, one
  unambiguous managed region may be replaced or removed idempotently; every byte
  outside it is project-owned and opaque to Agent Workflow. When no region
  exists, installation adds one without changing existing project bytes. Prior
  reconstructable framework bytes may be normalized only when their framework
  ownership and the project-byte boundary are both unambiguous. Otherwise,
  ambiguous ownership stops destructive mutation rather than inviting guessed
  recovery.
- `CLAUDE.md` remains under its existing composite integration for this decision.
  Lifecycle operations continue to preserve its project-authored portion; this
  decision does not change that host protocol or its support boundary.
- Every mutating lifecycle command requires the target to be an exact Git
  worktree root with a valid `HEAD` and an entirely clean tracked and untracked
  worktree. Managed destinations must not be ignored, and managed roots and
  parents must not be symlinks or escape the worktree. These checks occur before
  mutation because Git cannot recover ignored, untracked, or out-of-worktree
  content.
- The supported bootstrap and adoption path keeps distributable root policies
  under non-active template names and activates framework resources only by
  projecting explicit source-to-target mappings into host discovery locations.

The ordinary distribution manifest is only the current source-to-target map.
Agent Workflow maintains no installation history or migration subsystem: no
installed manifests, origin or deletion provenance, content-integrity state,
historical inventories, retirement registries, legacy-name policy, backup
trees, global transactions, or rollback machinery. Pre-1.0 historical layouts
do not become permanent runtime migration policy. Git records and recovers
lifecycle changes. A partial failure is reported truthfully and is recovered by
inspecting and restoring the worktree with Git before retrying.

## Consequences

Missing, modified, obsolete, or extra files inside a managed surface are replaced
from current package bytes after the Git safety gate passes. Project-owned bytes
outside a composite managed region, unrelated skill directories, and
`.agent-wayfinder/` remain hard preservation boundaries.

A clean existing installation normally converges with one install or update and
produces one reviewable Git diff. An obsolete file inside `.agent-workflow/`
disappears through complete replacement; no preliminary deletion or cleanup
commit is required. A skill name absent from the current curated inventory is
outside current lifecycle ownership and remains untouched unless the project
explicitly removes it.

## Alternatives considered

- Preserve historical install/origin and restoration metadata for every framework
  file: rejected because reconstructable output does not justify a package
  manager before 1.0.
- Treat every project target as replaceable: rejected because durable state,
  composite project regions, and unrelated skills may contain unique information.
  Only the explicitly named managed directories and composite regions are
  replaceable.
- Mirror installed root-policy and host-customization paths literally inside
  the distributable package: rejected because supported adoption needs a clear
  activation boundary.
- Track per-file creation or deletion evidence: rejected because the clean Git
  worktree and reserved managed-directory names make the current ownership
  boundary explicit without persistent provenance.
- Maintain historical layout or skill-name rules as permanent runtime policy:
  rejected because current desired state and current ownership boundaries are
  sufficient; pre-1.0 history does not justify a migration or retirement
  subsystem.
- Roll back a cross-surface transaction: rejected because Git is the recovery
  mechanism and a truthful partial-failure report is sufficient for the current
  pre-1.0 use case.

## Reconsideration trigger

Reconsider when a concrete data-loss or core-routing failure cannot be handled
by the clean Git boundary and current desired-state replacement without
weakening supported host behavior.
