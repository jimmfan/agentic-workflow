# Architecture decisions

This directory is a maintained index of current architecture decisions. Git is
the full historical record. A removed identifier remains here as a tombstone so
links and old discussions can be traced without treating obsolete rules as
current instructions.

## Current

- [ADR-0006 — Use an inert bootstrap payload](0006-use-inert-bootstrap-payload.md)
- [ADR-0008 — Require supported Python](0008-require-supported-python.md) (provider-tool portion superseded)
- [ADR-0010 — Separate lifecycle safety and reconciliation](0010-separate-lifecycle-safety-and-reconciliation.md)
- [ADR-0011 — Use project-owned Wayfinder state](0011-use-project-owned-wayfinder-state.md)
- [ADR-0013 — Enable automatic Wayfinder routing](0013-enable-automatic-wayfinder-routing.md)
- [ADR-0016 — Reconcile relevant Wayfinder state at completion](0016-reconcile-relevant-wayfinder-state-at-completion.md)
- [ADR-0019 — Scope bootstrap limits to the distributable package](0019-scope-bootstrap-limits-to-the-distributable-package.md)
- [ADR-0020 — Own the declared provider projection](0020-own-the-declared-provider-projection.md)
- [ADR-0021 — Maintain compact current decision context](0021-maintain-compact-current-decision-context.md)
- [ADR-0022 — Separate Wayfinder knowledge from implementation tickets](0022-separate-wayfinder-knowledge-from-implementation-tickets.md)
- [ADR-0023 — Own the Wayfinder runtime projection](0023-own-the-wayfinder-runtime-projection.md)
- [ADR-0024 — Use current-state Wayfinder identifiers](0024-use-current-state-wayfinder-identifiers.md)
- [ADR-0025 — Preserve human authority across workflows](0025-preserve-human-authority-across-workflows.md)
- [ADR-0026 — Structure Wayfinder territory and converge it](0026-structure-wayfinder-territory-and-converge-it.md)
- [ADR-0027 — Use thin evidence-triggered routing](0027-use-thin-evidence-triggered-routing.md)
- [ADR-0028 — Use Wayfinder as the sole durable coordinator](0028-use-wayfinder-as-sole-durable-coordinator.md)
- [ADR-0029 — Preserve material decision context and gate dependent work](0029-preserve-material-decision-context.md)
- [ADR-0032 — Use `.agent-wayfinder` for durable project knowledge](0032-use-agent-wayfinder-root-for-durable-project-knowledge.md)

## Superseded tombstones

- ADR-0002 — Use checksummed copy adoption; superseded by ADR-0010.
- ADR-0003 — Keep Wayfinder and Teach optional references; superseded by ADR-0007.
- ADR-0005 — Add durable decomposition and independent review; superseded by ADR-0007.
- ADR-0007 — Orchestrate pinned upstream skills; superseded by ADR-0008, ADR-0010, ADR-0011, ADR-0013, ADR-0020, ADR-0023, ADR-0027, and ADR-0028.
- ADR-0009 — Use a host-neutral lifecycle controller; superseded by ADR-0010.
- ADR-0012 — Resume from canonical records and maps; superseded by ADR-0028.
- ADR-0014 — Complete provider projection; superseded and consolidated into ADR-0020.
- ADR-0015 — Effective local-mode Wayfinder adapter; superseded and consolidated into ADR-0020.
- ADR-0017 — Routed provider invocation adapters; superseded and consolidated into ADR-0020.
- ADR-0018 — Bundled pinned provider snapshot; superseded and consolidated into ADR-0020.
- ADR-0030 — Thin focused VS Code Wayfinder projection; experimental on
  `wayfinder-replace`, completed without adoption after mixed explicit-agent
  evidence and failed automatic-delegation gates.
- ADR-0031 — Focused Wayfinder model invocation in VS Code; experimental on
  `wayfinder-replace`, not adopted because invocation required an always-loaded
  parent bridge and still produced duplicated investigation and invalid state.
