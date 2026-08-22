# Focused Wayfinder VS Code experiment history

## Outcome

The focused Wayfinder custom-agent architecture was tested and not adopted.
General remains the semantic router and, when durable coordination is warranted,
executes the canonical Wayfinder skill inline. Explicit Wayfinder invocation
also remains supported by providers that expose it.

This conclusion rejects the VS Code-specific projection, not automatic semantic
selection of the ordinary Wayfinder workflow. The latter remains an open routing
and evaluation question.

## What was tested

The experiment on `wayfinder-replace` culminated at
`7a8ad8fd28527cbbbdc65551703f67a03ee22568`. It evaluated three related ideas:

1. A focused `.github/agents/wayfinder.agent.md` custom agent that loaded the
   canonical portable Wayfinder skill with a narrower VS Code tool surface.
2. Automatic General-to-focused-Wayfinder delegation, including a parent bridge
   that told General to invoke the custom agent and consume its result.
3. A VS Code `SessionStart` hook that injected the final route-marker reminder,
   plus a narrow `PreToolUse` guard intended to reject explicit effort-map
   deletion.

The experiment also produced generic improvements to Wayfinder's authored and
installed contracts, state vocabulary, authority/evidence handling, decision
context, selective promotion, ready-frontier behavior, and deterministic tests.
Those independent improvements were retained separately from the host-specific
architecture.

## Evidence and interpretation

### Explicit focused projection

The explicit custom agent was feasible, but the EKS orientation comparison did
not show a better core outcome. General and focused Wayfinder reached the same
project orientation and next-boundary decision. Focused Wayfinder was somewhat
more selective and precise about provenance and unresolved evidence, and its
single corrected run used fewer observed calls and tokens. It also violated its
lock-only execution constraint, encountered a sandbox restriction, and caused an
unnecessary approval flow. The exact preregistered model was not available, so
this remains qualified evidence rather than a clean causal result.

### Automatic custom-agent delegation

Model-invocable metadata and agent description alone did not cause General to
delegate. Adding an always-on parent instruction produced native
`SubagentStart agent_type="Wayfinder"` events, but did not satisfy the experiment's
stop-loss:

- one automatic run substantially repeated the focused agent's investigation
  after it returned;
- another run consumed the result but wrote child statuses outside the canonical
  Wayfinder state contract.

This showed that invocation was possible, not that the parent/child contract was
reliable or simpler than inline skill execution.

### SessionStart route-marker hook

A follow-up isolated comparison used five fresh VS Code agent sessions per
condition after disabling the failed focused-agent instructions:

| Condition | Correct route | Marker present | Marker accurate |
| --- | ---: | ---: | ---: |
| Minimal portable `AGENTS.md` marker | 5/5 | 5/5 | 5/5 |
| `SessionStart` injected marker | 5/5 | 5/5 | 3/5 |

The hook did not improve marker presence or route correctness. On comparable
Direct and Discovery prompts, the hook condition averaged 202 more total tokens.
An apparent aggregate saving across all prompts was confounded by less Wayfinder
validation and a missed file inconsistency, so it is not evidence of a real
efficiency gain. The portable marker therefore has the better cost/portability
tradeoff and avoids VS Code-specific installation, lifecycle, payload, and
failure surfaces.

### `PreToolUse` guard

The narrow deletion guard protected only one textual `apply_patch` shape and
required host-specific hook machinery. It was not a general authorization or
durable-state safety boundary, so it was not retained. This does not change the
canonical `.wayfinder-mutation-lock/` contract, which remains the generic
mutual-exclusion mechanism for Wayfinder state mutation.

## Reconstructed product boundary

The clean reconstruction keeps:

- General as the only semantic router;
- selective inline execution of the canonical Wayfinder skill;
- explicit Wayfinder invocation where the provider supports it;
- the compact portable final route marker;
- the generic Wayfinder contracts and deterministic state/routing tests; and
- source-repository external-action notifications.

It excludes the focused custom agent, parent delegation/result-consumption
instructions, route-marker hook, deletion guard, and their distribution,
adoption, and lifecycle machinery.

## Preserved and omitted evidence

This report and the completed effort map preserve the decision-relevant history.
The experimental branch retains the fuller research, protocols, result report,
and three raw VS Code chat exports. The raw exports total approximately 7.55 MB
and are intentionally not copied into the reconstructed product history because
they are large host transcripts rather than maintainable project documentation.

Useful branch sources include:

- `docs/vscode-focused-wayfinder-research.md`
- `docs/focused-wayfinder-eks-experiment-research.md`
- `evals/manual-vscode/eks-focused-wayfinder-v1/`
- `evals/manual-vscode/basic-phase2-wayfinder-smoke-v1/protocol.md`
- `architecture-decisions/0030-use-thin-focused-vscode-wayfinder-projection.md`
- `architecture-decisions/0031-enable-focused-wayfinder-model-invocation.md`

## Revisit triggers

Reconsider a separate focused host agent only if the host later provides all of
the following and a representative repeated evaluation shows a material benefit:

- deterministic semantic binding from the parent router to the intended agent;
- a complete, schema-checkable result channel that avoids duplicate parent work;
- enforceable least-capability behavior without prompt-only restrictions; and
- a reliability or efficiency gain large enough to justify host-specific
  installation and lifecycle machinery.

Until then, the simpler inline canonical-skill architecture is the settled
product design.
