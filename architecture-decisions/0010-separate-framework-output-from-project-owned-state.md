# ADR-0010: Separate framework output from project-owned state

- Status: accepted
- Date: 2026-08-14

## Context

Agent Workflow must be able to install, repair, update, and remove the files it
manages without risking unique information owned by the project or user.
Framework-owned reconstructable output does not justify package-manager
machinery;
the ownership boundary should protect project data and core routing directly.

The source package also contains policies and skill resources destined for an
installed repository. The supported bootstrap and adoption path needs an
explicit activation boundary between stored package resources and their
installed host discovery locations. Agent Workflow is pre-1.0, has one current
user, and operates only in Git-tracked projects, so Git can provide the recovery
boundary instead of an installation-history database.

## Decision

Separate framework-owned reconstructable output from preservation boundaries:

- `.agent-workflow/` and each current curated `.agents/skills/<name>/` directory
  are framework-owned reconstructable surfaces. Install and update replace each
  complete named surface with current package bytes; remove deletes them.
  Unrelated skill directories remain independent. A curated skill-directory
  name becomes reserved when Agent Workflow is adopted, so a project-owned skill
  with the same name must be moved or renamed before installation.
- `.agent-wayfinder/` is project-owned durable state completely outside the
  lifecycle boundary. Lifecycle operations never create, inventory, interpret,
  migrate, rewrite, or remove it.
- `AGENTS.md` and `CLAUDE.md` are composite project files. Lifecycle operations
  replace or remove only their unambiguous managed regions and preserve every
  project-authored byte outside those regions. Malformed, duplicated, partial,
  or reordered markers stop mutation.
- Every mutating lifecycle command requires the target to be an exact Git
  worktree root with a valid `HEAD` and an entirely clean tracked and untracked
  worktree. Managed destinations must not be ignored, and managed roots and
  parents must not be symlinks or escape the worktree. These checks occur before
  mutation because Git cannot recover ignored, untracked, or out-of-worktree
  content.
- The supported bootstrap and adoption path keeps distributable root policies
  under non-active template names and activates framework resources only by
  projecting explicit source-to-target mappings into host discovery locations.

The ordinary distribution manifest is only the current source-to-target map. Do
not maintain installed manifests, origin or deletion provenance, content
integrity state, historical inventories, automatic retirement, legacy
migration, backup trees, global transactions, or rollback machinery. Git records
and recovers lifecycle changes. A partial failure is reported truthfully and is
recovered by inspecting and restoring the worktree with Git before retrying.

## Consequences

Missing, modified, obsolete, or extra files inside a managed surface are replaced
from current package bytes after the Git safety gate passes. Project-authored
composite regions, unrelated skill directories, and `.agent-wayfinder/` remain
hard preservation boundaries.

Removing a skill from the curated inventory does not authorize automatic cleanup
of its former directory in consuming projects. Future retirement is a manual,
Git-tracked cleanup. Former provider installations likewise require a separate
manual cleanup commit before the current lifecycle may run.

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
- Automatically retire skills or migrate provider installations: rejected
  because historical inventory is not current package state and Git-tracked
  manual cleanup is simpler and reviewable.
- Roll back a cross-surface transaction: rejected because Git is the recovery
  mechanism and a truthful partial-failure report is sufficient for the current
  pre-1.0 use case.

## Reconsideration trigger

Reconsider when a concrete data-loss or core-routing failure cannot be handled
by the clean Git boundary and current desired-state replacement without
weakening supported host behavior.
