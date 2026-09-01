# ADR-0010: Separate framework output from project-owned state

- Status: accepted
- Date: 2026-08-14
- Amended: 2026-08-31

## Context

Agent Workflow must be able to install, repair, update, and remove the files it
manages without risking unique information owned by the project or user.
Framework-owned reconstructable output should converge to current desired state;
it does not justify package-manager machinery or manual migration ceremony.

The source package also contains policies and skill resources destined for an
installed repository. The supported bootstrap and adoption path needs an
explicit activation boundary between stored package resources and their
installed host discovery locations. Agent Workflow is pre-1.0, and normal
lifecycle use should converge declared framework surfaces regardless of whether
the target is Git-tracked or what unrelated repository state exists.

## Decision

Separate framework-owned reconstructable output from preservation boundaries:

- `.agent-workflow/` is one framework-owned reconstructable surface. Install and
  update may replace it completely with current package bytes, removing missing,
  modified, obsolete, or extra content as ordinary desired-state convergence.
- For skills, each current curated `.agents/skills/<name>/` directory is likewise
  a complete framework-owned reconstructable surface. Install and update replace
  each complete named surface; remove deletes it. Unrelated skill directories
  remain independent and are not deleted or interpreted through historical skill
  inventories. Current curated names are reserved framework surfaces; existing
  content at those names does not require adoption recognition before
  replacement.
- `.agent-wayfinder/` is project-owned durable state. Lifecycle operations do
  not directly traverse, interpret, or change it.
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
- Every lifecycle command requires an existing non-root target directory. An
  explicit target is used directly. When the CLI target is omitted, Git may be
  used only to discover the containing worktree root; failed or unavailable
  discovery falls back to the current directory. Repository state, `HEAD`,
  tracked changes, untracked files, and ignore rules are not prerequisites or
  recovery boundaries. Managed roots and their parents must not themselves be
  symlinks, unsupported entry types, or escapes from the target, and ambiguous
  composite ownership stops mutation before project-authored bytes can be lost.
  Nested entries inside a replaceable managed directory are ordinary convergence
  input.
- The supported bootstrap and adoption path keeps distributable root policies
  under non-active template names and activates framework resources only by
  projecting explicit source-to-target mappings into host discovery locations.
  A released CLI defaults to the release tag matching its own package version;
  mutable refs remain explicit development overrides.

The ordinary distribution manifest is only the current source-to-target map.
Agent Workflow maintains no installation history or migration subsystem: no
installed manifests, origin or deletion provenance, content-integrity state,
historical inventories, retirement registries, legacy-name policy, backup
trees, global transactions, or rollback machinery. Pre-1.0 historical layouts
do not become permanent runtime migration policy. A partial filesystem failure
is reported truthfully; after resolving the concrete error, rerunning the
command converges the managed surfaces.

## Consequences

Missing, modified, obsolete, or extra files inside a managed surface are replaced
from current package bytes. Project-owned bytes
outside a composite managed region, unrelated skill directories, and
`.agent-wayfinder/` remain hard preservation boundaries.

An existing installation normally converges with one install or update despite
ordinary repository state. An obsolete file inside `.agent-workflow/` disappears
through complete replacement; no preliminary deletion or cleanup commit is
required. A skill name absent from the current curated inventory is outside
current lifecycle ownership and remains untouched unless the project explicitly
removes it.

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
- Track per-file creation or deletion evidence: rejected because the declared
  managed-directory names make the current ownership
  boundary explicit without persistent provenance.
- Maintain historical layout or skill-name rules as permanent runtime policy:
  rejected because current desired state and current ownership boundaries are
  sufficient; pre-1.0 history does not justify a migration or retirement
  subsystem.
- Require Git cleanliness and use Git as lifecycle recovery: superseded because
  ordinary repository state is unrelated to the declared ownership boundary and
  creates user-facing ceremony without preventing loss of project-owned data.
- Roll back a cross-surface transaction: rejected because truthful
  partial-failure reporting plus rerunnable convergence is sufficient for the
  current pre-1.0 use case.

## Reconsideration trigger

Reconsider when a concrete project-data-loss or core-routing failure cannot be
handled by current desired-state replacement and the managed-path safety checks
without weakening supported host behavior.
