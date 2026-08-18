# D1: Use a fingerprinted local-mode provider overlay

- Related: U1, T1, T2

## Decision

Extend the existing narrow Wayfinder provider adaptation so it inserts one clearly delimited, authoritative Agentic Workflow local-mode block before the unchanged pinned upstream method and continues to adapt the known activation metadata.

Recognize the provider by its pinned source metadata and upstream method-body fingerprint. Treat the exact adapted form idempotently. If the fingerprint, source metadata, expected metadata values, or adapter markers are unexpected, report incompatibility and write nothing.

## Why

Codex loads the complete selected `SKILL.md`, so the current metadata-only overlay cannot reconcile the effective instructions. A separate wrapper would not fix explicit `$wayfinder` use and Codex does not merge duplicate skill names. A full fork would duplicate the provider-owned method and increase drift.

## Consequences

- Agentic Workflow owns routing plus the local storage/re-entry adapter; upstream retains its reasoning method.
- The adapter explicitly maps decision/investigation questions to U#, durable choices to D#, and executable outcomes to T# without forcing every item through all three.
- Tracker setup, `.scratch/`, issue assignment/comments/closing, and external tracker mutation do not apply in local mode.
- Debugging, Research, Prototype, Grilling, Domain Modeling, human clarification, and Implementation may support the effort without becoming competing durable-state owners.
- Grilling and Domain Modeling run when the actual destination or domain needs them, not ceremonially on every dynamic escalation or resume.
- Read-only work remains non-mutating; live/source evidence wins over stale state and affected state is reconciled explicitly.

## Alternatives rejected

- Keep the metadata-only overlay: it changes activation but not the loaded contradictory method body.
- Put the override only in root routing/contracts: the selected skill still presents a later, operationally specific tracker workflow.
- Add a separate local wrapper skill: explicit Wayfinder still loads the provider skill, and same-named skill bodies are not merged.
- Fork the upstream skill: unnecessary duplication of the method and a larger upgrade surface.
