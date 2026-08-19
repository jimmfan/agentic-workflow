# Architecture decisions

This directory is a maintained index of current architecture decisions. Git is
the full historical record. A removed identifier remains here as a tombstone so
links and old discussions can be traced without treating obsolete rules as
current instructions.

## Current

- [ADR-0006 — Use an inert bootstrap payload](0006-use-inert-bootstrap-payload.md)
- [ADR-0007 — Orchestrate pinned upstream skills](0007-orchestrate-pinned-upstream-skills.md) (partially superseded)
- [ADR-0008 — Require supported Python](0008-require-supported-python.md) (provider-tool portion superseded)
- [ADR-0010 — Separate lifecycle safety and reconciliation](0010-separate-lifecycle-safety-and-reconciliation.md)
- [ADR-0011 — Use project-owned Wayfinder state](0011-use-project-owned-wayfinder-state.md)
- [ADR-0012 — Remove the global active index](0012-remove-global-active-index.md)
- [ADR-0013 — Enable automatic Wayfinder routing](0013-enable-automatic-wayfinder-routing.md)
- [ADR-0016 — Reconcile relevant Wayfinder state at completion](0016-reconcile-relevant-wayfinder-state-at-completion.md)
- [ADR-0019 — Scope bootstrap limits to the distributable package](0019-scope-bootstrap-limits-to-the-distributable-package.md)
- [ADR-0020 — Own the declared provider projection](0020-own-the-declared-provider-projection.md)
- [ADR-0021 — Maintain compact current decision context](0021-maintain-compact-current-decision-context.md)
- [ADR-0022 — Separate Wayfinder knowledge from implementation tickets](0022-separate-wayfinder-knowledge-from-implementation-tickets.md)
- [ADR-0023 — Own the Wayfinder runtime projection](0023-own-the-wayfinder-runtime-projection.md)
- [ADR-0024 — Use current-state Wayfinder identifiers](0024-use-current-state-wayfinder-identifiers.md)
- [ADR-0025 — Preserve human authority across workflows](0025-preserve-human-authority-across-workflows.md)

## Superseded tombstones

- [ADR-0002 — Use checksummed copy adoption](0002-use-checksummed-copy-adoption.md); superseded by ADR-0010.
- [ADR-0003 — Keep Wayfinder and Teach optional references](0003-use-internal-reference-inspired-workflows.md); superseded by ADR-0007.
- [ADR-0005 — Add durable decomposition and independent review](0005-add-decomposition-and-independent-review.md); superseded by ADR-0007.
- [ADR-0009 — Use a host-neutral lifecycle controller](0009-use-host-neutral-lifecycle-controller.md); superseded by ADR-0010.
- ADR-0014 — Complete provider projection; superseded and consolidated into ADR-0020.
- ADR-0015 — Effective local-mode Wayfinder adapter; superseded and consolidated into ADR-0020.
- ADR-0017 — Routed provider invocation adapters; superseded and consolidated into ADR-0020.
- ADR-0018 — Bundled pinned provider snapshot; superseded and consolidated into ADR-0020.
