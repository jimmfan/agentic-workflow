# Focused Wayfinder VS Code projection

- Status: current

## Destination

Test whether a thin native VS Code projection can focus Wayfinder on durable
project understanding and coordination while preserving the portable runtime,
state schema, routing behavior, provider boundaries, and human authority.

## Territory

- Portable Wayfinder semantics — the owned runtime projection and local state
  contract remain canonical.
- VS Code projection — a small host wrapper selects the canonical runtime and
  exposes only the capabilities needed for repository navigation and legitimate
  state reconciliation.
- Durable-state protection — one narrow `PreToolUse` guard rejects explicit
  `apply_patch` deletion of an effort map while allowing child retirement.
- Evaluation — focused behavioral scenarios cover resume, reconciliation,
  progressive architecture loading, authority, missing knowledge, readiness,
  and the guard without embedding expected answers in live prompts.

The host projection and guard depend on current VS Code tool and hook contracts;
the scenarios and deterministic package checks then verify the distributable
artifacts without claiming a live editor run.

## Current state

- Phase 1 established that the focused VS Code Wayfinder projection can run
  when selected explicitly while preserving durable-state ownership and human
  authority.
- The Basic Phase 2 live gate at `3c80dfcc352bfa847a09a476e1248f4c3e6702c3`
  falsified ADR-0031's assumption that model-invocable metadata plus the custom
  agent description form a complete General-to-Wayfinder bridge: automatic B
  ran Wayfinder inline, and a delegated combined run repeated substantial
  investigation in General.
- One bounded native-host correction is present in the current working tree at
  `52715bbd304478f81f8731ad5753ee5572f2de78`: an always-on VS Code parent
  instruction tells General to invoke the exact `Wayfinder` custom agent when
  semantic routing selects it and to consume its returned result. ADR-0031,
  lifecycle projection, package metadata, tests, and verification docs were
  updated without changing the portable router or focused methodology.
- The full deterministic package gate passes 146 tests.
- The corrected live rerun produced `SubagentStart agent_type="Wayfinder"` in
  automatic B and Combined; Direct C and Debugging D produced no
  `SubagentStart`.
- The correction did not satisfy the live stop-loss. In B, General made eight
  tool calls after `SubagentStop`, substantially re-investigating the focused
  result. In Combined, General consumed the result without further tools, but
  focused Wayfinder wrote invalid child statuses (`contradicted` for a fact and
  `unresolved` for an unknown) even though the contract permits
  `current|disputed|stale` and `open|resolved` respectively.

## Blockers and dependencies

- Basic Phase 2 automatic routing is not reliable enough to dogfood: the one
  authorized native-host correction still duplicated investigation in B and
  delegated Wayfinder still violated the existing state contract in Combined.
- The user's stop-loss prohibits another orchestration correction in this
  effort. Direct and Debugging isolation, exclusive focused state ownership,
  and human/project authority behavior remain intact.
- No human- or project-authority decision is required to interpret this gate;
  the evidence supports retaining focused Wayfinder as explicit/manual unless
  the Basic Phase 2 changes are intentionally reverted.

## Next work

Keep focused Wayfinder explicit/manual. Do not add another parent prompt,
routing hook, delegation layer, specialist agent, or orchestration mechanism as
part of Basic Phase 2. If the current correction is not retained as documented
experimental evidence, revert Basic Phase 2 rather than extending it.

## Notes

- Preserve successful Phase 0 route-report enforcement.
- Do not change the Wayfinder state schema or duplicate runtime semantics into
  the VS Code wrapper.
- Reusable live-host lessons are now captured in the existing
  [Basic Phase 2 VS Code smoke protocol](../../../evals/manual-vscode/basic-phase2-wayfinder-smoke-v1/protocol.md#autonomous-live-host-practice),
  not a new test framework. They cover capability preflight, fresh isolated
  workspaces/chats, passive lifecycle hooks, semantic validation of state
  statuses, secondary token accounting, precise cleanup, and stop-loss behavior.
- Treat Trust Folder, Trust Authors, memory-read, Allow in This Session,
  authentication, and similar prompts as environment gates. A future agent must
  immediately name the exact VS Code window/control when human action is
  unavoidable, pause only the affected case, and confirm when it is cleared.
- `code chat -r` can target the wrong active window. Confirm the intended
  workspace before every submission and reject, record, and isolate any
  mistargeted session rather than repairing its evidence after the fact.
- Invocation evidence and state correctness are independent: a documented
  `SubagentStart agent_type="Wayfinder"` proves focused execution, but the
  resulting diff must still satisfy the Wayfinder contract and ownership and
  authority boundaries.
- The live observer was passive; transcript data was used only for secondary
  usage accounting. A mistargeted first Combined submission landed in B and is
  excluded from the B result; the correctly targeted Combined rerun used a
  fresh chat and session identifier.
- Do not add Phase 2 agents, protocols, handoffs, memory, reputation, generic
  host abstractions, semantic-router rewrites, or additional hook machinery.

## Out of scope

Another Basic Phase 2 correction attempt; Phase 3 or specialist agents; Codex
or Claude projections; broader security or authorization enforcement; and
live-editor success claims not actually run.
