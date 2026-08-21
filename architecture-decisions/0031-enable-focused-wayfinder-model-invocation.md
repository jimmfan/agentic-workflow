# ADR-0031: Enable focused Wayfinder model invocation in VS Code

- Status: accepted
- Date: 2026-08-21
- Amends: ADR-0030
- Preserves: ADR-0013, ADR-0023, ADR-0025, ADR-0027, ADR-0028, and ADR-0029

## Context

ADR-0030 added a thin VS Code Wayfinder custom agent for an explicit Phase 1
comparison and deliberately kept model invocation disabled. The focused
projection remained manually selectable, while ordinary semantic routing used
the portable Wayfinder skill inline through the General agent.

Phase 1 found no material semantic loss from the focused projection and modest
directional benefits in provenance, uncertainty framing, architecture
selectivity, and resource use. It also confirmed that the instruction limiting
`execute` to the mutation-lock lifecycle is not a capability boundary. Basic
Phase 2 asks only whether the existing semantic Wayfinder selection can use the
focused VS Code projection automatically, without introducing a general
multi-agent runtime or additional specialist agents.

VS Code's custom-agent contract independently controls user and model access.
`user-invocable: true` keeps an agent in the picker, while
`disable-model-invocation: false` makes it available for another agent to invoke
as a subagent. An empty `agents` list prevents the focused agent from invoking
other agents. The description is the host's semantic selection interface.

## Decision

Make the existing VS Code Wayfinder projection explicitly user-invocable and
model-invocable. Keep `agents: []`, the Phase 1 `read`/`search`/`edit`/`execute`
allowlist, the canonical runtime and state-contract links, and the focused body
unchanged. Refine only its description so the host sees the same durable
coordination signals used by the portable router.

This is the complete General-to-focused-Wayfinder bridge for Basic Phase 2:

1. the portable root router semantically selects Wayfinder under its existing
   hard-signal / two-soft-signal contract;
2. VS Code exposes the focused Wayfinder agent as a model-invocable candidate;
3. the focused agent's description identifies that durable-coordination role;
4. VS Code may invoke it in a child context, where it owns Wayfinder
   coordination and no child agents are available to it.

Do not add VS Code agent names, invocation fields, or handoff protocol to the
portable router, Wayfinder runtime, or state contract. Do not create custom
agents for other methodologies. Actual model selection is nondeterministic host
behavior and requires a small live VS Code smoke; deterministic tests establish
eligibility, configuration, packaging, and preservation only.

The reversible escape hatch is the single
`disable-model-invocation: true` field in the focused projection. Reverting that
field restores manual-only focused use and leaves semantic routing on the
general/portable path.

## Consequences

The change is host-specific and thin: two invocation fields plus a selection
description on one already packaged `.agent.md` file. General may now isolate a
Wayfinder-selected task in the focused context without changing the meaning of
Wayfinder or adding a framework-owned subagent protocol.

Deterministic compatibility tests retain Direct, Research, Debugging,
Discovery, Implementation, Verification, Wayfinder threshold, explicit use and
opt-out, read-only, authority, evidence-precedence, unrelated-state, and
lifecycle boundaries. A disposable old-projection-to-current update test
verifies that the agent changes while project-owned state and an unrelated
custom agent remain byte-identical.

The focused projection still exposes a general `execute` capability because the
canonical atomic mutation lock requires it. VS Code provides no lock-only shell
capability or path-scoped edit boundary. The instruction remains advisory, and
the existing narrow `apply_patch` deletion guard remains defense in depth. Basic
Phase 2 does not claim mechanical lock-only enforcement and adds no policy
engine.

## Alternatives considered

- Put an explicit focused-agent handoff in the portable router: rejected because
  it would make VS Code mechanics part of canonical Wayfinder semantics.
- Add a generic specialist invocation protocol: rejected because one existing
  host projection needs only native metadata and no second use case exists.
- Add custom agents for other methodologies: rejected because Research,
  Debugging, Discovery, Implementation, Verification, Domain Modeling, and the
  remaining methods continue to work as skills/workflows in this phase.
- Mechanically enforce lock-only shell use: rejected because the host has no
  suitably narrow stable capability and a shell-policy layer is outside the
  Phase 2 safety boundary.
