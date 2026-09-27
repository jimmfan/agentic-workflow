# Architecture decisions

This directory contains only current, independently reconsiderable architecture decisions:

- [ADR-0010 — Separate framework output from project-owned state](0010-separate-framework-output-from-project-owned-state.md)
- [ADR-0011 — Use map-first effort state](0011-use-map-first-wayfinder-state.md)
- [ADR-0025 — Preserve project decision authority at consequential boundaries](0025-preserve-authority-at-consequential-boundaries.md)
- [ADR-0027 — Use Direct-first progressive routing](0027-use-direct-first-progressive-routing.md)
- [ADR-0028 — Use Wayfinder as the sole durable coordinator](0028-use-wayfinder-as-sole-durable-coordinator.md)
- [ADR-0029 — Distribute canonical framework terminology](0029-distribute-canonical-framework-terminology.md)

## Maintaining decision records

Keep ADRs for architecturally significant choices that can reasonably be reconsidered independently and whose rationale would otherwise be lost.
Before adding one, check whether an existing ADR already owns the boundary.
Put current system shape in [`docs/architecture.md`](../docs/architecture.md) and exact required behavior in contracts, source, and tests.

Do not use ADRs merely to record experiments, bug fixes, dependency or version updates, numeric limits, path cleanup, benchmark results, or routine implementation mechanics.
During explicit ADR maintenance, consolidate or remove obsolete pre-1.0 records rather than keeping them as a changelog; Git preserves historical evolution.
