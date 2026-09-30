# E1 — Route coverage inventory at 64be830

Source: a read-only inventory made on 2026-09-30 at commit `64be830` of the [detailed routing table](../../../.agent-workflow/routing.md#decide-and-compose), the `route_must_include` and `route_must_not_include` fields and `expect` outcomes of the 60 [behavior scenarios](../../../tests/scenarios/), the [routing smoke cases](../../../evals/routing-smoke/README.md), and the [remaining-audit campaign's hypothesis table](../../../evals/remaining-audit-behavior/README.md).

Scope: which evidence each routing entry, main transition, and terminal outcome currently has.
Routes are grouped as Direct, Decide (Discovery, Grilling, Research, Domain Modeling, Codebase Design, Prototype), Shape (`to-spec`, `to-tickets`, `wayfinder-effort`), Build (Implementation, `implement`, TDD, Code Review), Diagnose (Debugging), Audit (Verification, standalone Code Review), and Coordinate (Wayfinder).
This grouping is an inventory aid, not a second routing specification; detailed routing remains the owner.

## Observation

| Route | Scenario route declarations | Other evidence sources |
|---|---|---|
| Direct | 12 scenarios exclude `wayfinder`, among them `simple-bounded-task` and `objective-clear-request`; none requires `direct`. | Smoke `direct`, `choice-without-parallel-work`, `opt-out`. |
| Wayfinder threshold | 6 require `wayfinder`. | 9 smoke cases covering hard signals, re-evaluation after reconnaissance, and explicit use; the objective-scope routing campaign. |
| Discovery | 2 require it (`architectural-choice-uses-discovery`, `discovery-composes-research`); 5 exclude it. | None. |
| Research | 1 requires it (`discovery-composes-research`); `external-factual-uncertainty` checks the `external_fact_researched` outcome instead. | Audit H3 `audit-research`. |
| Domain Modeling | 1 requires it; 6 exclude it. | None. |
| Codebase Design | 1 excludes it (`audit-rename`). | None. |
| Grilling | None. | None. |
| Prototype | None. | Audit H3 `audit-ui`. |
| `to-spec`, `to-tickets` | 1 requires both (`drafts-without-publication`). | Audit H3 `audit-spec`. |
| Implementation, `implement` | None require it; `wayfinder-contract-smoke` excludes it. | Audit H2 `audit-causal-fix`, H3 `audit-integration`. |
| Explicit TDD | None. | Audit H3 `audit-test-first`. |
| Verification | None; 8 scenarios check the `verification_performed` outcome and `verification-failure-recovery` checks recovery. | Audit H2. |
| Standalone Code Review | None. | None. |
| Debugging, including its [trivial-fix and Implementation handoff](../../../.agents/skills/workflow-debugging/SKILL.md#fix-and-verify) | None. | Audit H2 `audit-diagnosis`, `audit-trivial-fix`, `audit-causal-fix`. |
| Curated skill over an overlapping host skill | None. | None. |
| Explicit skill request | None. | Smoke `explicit-wayfinder` only. |
| Loop guards (Discovery stays bounded, Verification runs once) | None. | None. |
| `-blocked` outcome | `blocked_cleanly` in 5 scenarios, including `blocked-project`. | None. |
| `-handoff`, `-unavailable`, `-incomplete` outcomes | None. | `test_routing.py` checks only that route reporting is documented. |

Coverage is concentrated on Direct versus Wayfinder selection and on effort-state behavior: 23 of the 60 scenarios have effort-state fixtures or state assertions.
The specialist "Direct or X" rows, the Debugging-to-Build-to-Audit chain, and the non-blocked terminal outcomes have no positive scenario route declaration, and several have no evidence source at all.

## Limitations

A route declaration grades the agent's reported route marker, which remains a claim unless independently supported ([test ownership](../../../tests/README.md#test-ownership)).
Deterministic tests exercise evaluators with synthetic answers, not agent behavior; scenarios produce behavioral evidence only in opt-in live runs.
The audit campaign judges H2 and H3 by trace adjudication of sufficient method rather than route sequence, and its isolation limitations remain unresolved under its [maintaining effort](../../remaining-behavior-evidence/map.md).
The routing smoke harness sends only the root policy and detailed routing, not skill descriptions, so it cannot test specialist selection without a change to its contract.
This inventory counts declared checks, not results, and does not show whether any uncovered route misroutes in practice.
Changing an existing scenario's grading rules requires retaining historical results under their original rules ([test ownership](../../../tests/README.md#test-ownership)).
