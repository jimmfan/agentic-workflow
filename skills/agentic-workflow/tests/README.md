# Test architecture

Tests are separated by determinism and product boundary.

Run focused unittest commands with `python3 -m unittest ...`. Python's generated
`__pycache__` files are ignored by Git and by package verification; they do not
need manual cleanup. The full verifier also disables bytecode writes in its test
subprocess.

## Deterministic contract and unit tests

- `test_behavior_contract.py` validates the TOML scenario contract, behavior
  vocabulary, fixture size, observable evaluator, required route-marker syntax,
  demand-driven Wayfinder creation and provider claims, progressive Wayfinder
  state inputs, and live command protocol using a deterministic fake agent.
- `test_routing.py` validates representative selection, lazy specialist
  invocation, authorization, Wayfinder resume, and durable-effect decisions
  without requiring one exact trace.
- `test_session_start_hook.py` exercises the installed VS Code SessionStart
  reminder output without depending on transcript parsing or Stop-hook blocks.
- `test_focused_wayfinder_host.py` validates the thin VS Code custom-agent
  user/model invocation policy, the General parent delegation/result-consumption
  instruction, allowlist, child-agent prohibition, canonical-runtime references,
  distribution mapping, Phase 0 SessionStart behavior, and old-projection update
  preservation.
- `test_basic_phase2_compatibility.py` retains the frozen-main route/state
  categories and the authority, unrelated-state, stale-evidence, and lifecycle
  boundaries. Its injected Direct-to-Wayfinder fault proves that the negative
  routing assertion detects over-selection.
- `test_pre_tool_use_guard.py` checks that normal Wayfinder Update patches are
  allowed while explicit current-schema Delete patches under project-owned
  Wayfinder state are denied.
- `test_wayfinder_state.py` validates the authored, installed, and generated
  settlement contract plus a deterministic state-transition oracle for
  current-state allocation, effort-lock serialization, reference-safe
  retirement without a Git-history gate, identifier reuse, effort lifecycle,
  and projection parity.
- `behavior.py validate` checks every human-authored scenario and fixture
  reference as part of static package verification.

## Static product catalogs

- `acceptance-scenarios.json` indexes lifecycle product acceptance cases.
- `decision-contract-scenarios.json` supplies representative routing decisions
  to `test_routing.py`.

These JSON catalogs are validated directly by `verify_package.py`. They are not
`behavior.py` scenarios and do not use the fixture-backed TOML schema.

## Deterministic fixture and lifecycle integration

- `test_behavior_fixtures.py` copies fixtures to temporary workspaces, checks
  reset behavior, proves install leaves Wayfinder state unseeded, verifies
  implementation fixtures begin red, detects a destructive state mutation, and
  runs install/update/repeated-update/remove/reinstall against every fixture.
- `test_lifecycle.py` retains focused archive, composite, collision,
  provider-isolation, cp1252, and current-state reconciliation coverage.

## Human behavioral contracts and live smoke tests

- `scenarios/*.toml` contain starting state, natural-language request, expected
  behavior, prohibited behavior, and a small observable oracle.
- `fixtures/*` are tiny consuming repositories with no copied framework payload.
- `behavior.py live` installs the framework into disposable fixture copies, runs
  a caller-supplied agent command, captures public evidence, and evaluates the
  scenario without asking for hidden reasoning.

Every scenario marked `live = true` runs by default when the opt-in live command
is used. Six blind focused-Wayfinder cases cover clean resume, stale conflict,
domain-to-architecture navigation, authority, missing knowledge, and the
implementation-ready boundary. Their neutral prompts make a general-agent
versus focused-agent run a broader router-vs-focused product experiment, not the
primary host-projection comparison where both conditions explicitly use
canonical Wayfinder. Live cases are not part of ordinary pull requests.

The smaller Basic Phase 2 manual VS Code gate is documented at
`evals/manual-vscode/basic-phase2-wayfinder-smoke-v1/protocol.md`. It checks
actual General-to-focused invocation, positive and negative selection, sole
durable-state ownership, authority, and duplicated investigation without
requiring unavailable Agent Debug telemetry.

The broader deterministic catalog also covers Domain Modeling surfacing
consequential uncertainty, authority-dependent choices asking a concrete human
question without creating downstream work, Wayfinder assessment concluding that
no durable state is needed, creating canonical map-first state without
implementation work-item children, optional U#/E#/F#/D# knowledge, resolved
unknowns and redundant evidence leaving current state, effort-lock serialization
under concurrent allocation and retirement, uncommitted transient retirement,
completed-effort/new-destination separation, explicit historical access, and
ensuring that an unrelated existing effort neither captures a simple route nor
gets loaded. It also checks selective U# promotion for authority-owned,
external-approval, and cross-area-gating uncertainty without promoting incidental
fog or requiring an exact child count. The live Wayfinder contracts preserve
an unrelated effort during reconciliation, keep stale-state audits read-only,
and require conflicting reconciliation to stop without guessing. Lifecycle
coverage preserves legacy DEC/IMP/DBG files as opaque project data while current
workflow scenarios resume only from Wayfinder or canonical provider artifacts.

See [Behavioral testing](../../../docs/behavioral-testing.md) for the schema,
evidence model, commands, side effects, cleanup, and limitations.
