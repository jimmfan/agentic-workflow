# Remaining behavior evidence

## Objective

Evaluate the four remaining pre-existing Agent Workflow behavior hypotheses after PR #32 and deliver bounded evidence without preemptive runtime changes.

## Scope

The user's four-hypothesis campaign on `eval/remaining-audit-behavior`, based on fetched main `1510e74540e3ebdb7c07966274fae7aeeac09386`.
Evaluation fixtures, controls, scripts and reporting only; commit and non-force push are authorized, with no merge, release, VERSION change or real consumer mutation.

## Ready work

Independent reviews and deterministic gates are complete.
Further live subject work requires a verified execution-isolation boundary; use the existing adapter preflight and then a native-tool denial probe before resuming the frozen cases.

## Current state

The [report](../../evals/remaining-audit-behavior/REPORT.md) maintains the current findings, completed/interrupted/unexecuted cases, infrastructure evidence and smallest follow-ups.
All four hypothesis-level results are INCONCLUSIVE; no runtime correction is justified.
The existing adapter now fails closed before credential copying or model launch when its isolation preflight fails.

## Areas and relationships

The controller maintains disposable fixtures and evidence.
Independent Standards and Spec reviewers assess design and conclusions; their reviews do not substitute for subject execution.
The report maintains the lasting results; this map retains only the unresolved continuation boundary.

## Dependencies

Live conclusions require an isolated host that can execute subject tools.
Delivery requires focused controls, independent reviews and the current deterministic gates.

## Blockers

Standalone and native-tool probes could read a synthetic sibling file despite intended deny settings.
The effective isolation cause remains unknown; the current adapter refuses further subject launches.
This blocks remaining live cases, without turning unexecuted behavior into a product failure or blocking independent evidence review.
The prior map-authoring failure remains a separate historical result.

## Key references

- [Campaign protocol](../../evals/remaining-audit-behavior/README.md)
- [Behavior harness](../../docs/behavioral-testing.md)
