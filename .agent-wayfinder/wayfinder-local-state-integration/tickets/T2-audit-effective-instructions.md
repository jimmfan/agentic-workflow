# T2: Audit the resulting effective instructions

- Status: done
- Blocked by: T1
- Related: D1, T3

## Outcome

Inspect every instruction source a fresh Codex agent can receive and produce the required concern/effective-behavior/evidence/pass-fail table, fixing and repeating until no material contradiction remains.

## Acceptance

- The audit covers root policy, routing, durable and Wayfinder contracts, provider declaration, projected `SKILL.md`, Codex metadata, ADRs, and tests.
- Green tests alone do not satisfy the gate.
- Agent benchmarking remains prohibited until this ticket is done.

## Result

The post-fix semantic audit passes. It covers instruction precedence, canonical
storage, U/D/T meaning, composition, read-only behavior, progressive re-entry,
evidence precedence, lifecycle ownership, activation, and payload/projection
agreement. The audit also identifies non-blocking repetition and records one
authoritative home per invariant plus measured and estimated route-loading
costs. Only the correctness-relevant read-only load gate was deduplicated now;
the broader cleanup is deferred as a separate decision.

## Follow-up

On 2026-08-18, the separately reviewed targeted cleanup was implemented in the
[runtime routing contract](../../../../skills/agent-workflow/payload/agent-workflow/routing.md),
[always-loaded policy](../../../../skills/agent-workflow/payload/root/AGENTS.md.template),
and [routing documentation](../../../../docs/routing.md). It keeps route
selection, transition, provider resolution, composition, continuity, and route
reporting in the router while leaving universal policy, provider facts,
provider methodology, and state mechanics with their existing owners. Focused
routing coverage records the clarified Direct/Implementation, setup-handoff,
and successful-fallback seams; the full deterministic package gate passes 89
tests. The original audit remains historical evidence of what was deferred at
that time, and this cleanup does not resolve the evaluation program's open
question about automatic Wayfinder value.
