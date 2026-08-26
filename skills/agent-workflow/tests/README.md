# Test architecture

Tests are separated by determinism and product boundary.

Run focused unittest commands with `python3 -m unittest ...`. Python's generated
`__pycache__` files are ignored by Git and by package verification; they do not
need manual cleanup. The full verifier also disables bytecode writes in its test
subprocess.

## Deterministic contract and unit tests

- `test_behavior_contract.py` validates the TOML scenario contract, behavior
  vocabulary, blind-rubric isolation, adversarial evaluator cases, required
  route-marker syntax, progressive Wayfinder state inputs, and live command
  protocol using a deterministic fake agent.
- `test_routing.py` validates the executable routing, authorization, lazy
  loading, Wayfinder resume, and fail-closed prose contracts.
- `test_wayfinder_state.py` validates the authored, installed, and generated
  state contract plus a deterministic state-transition oracle for map-only
  efforts; F#/D# ledger creation, allocation, duplicate rejection, mutation,
  and retirement; independent U#/E# files; non-interpretation of unrecognized
  project-owned content; safe collision handling; effort-lock serialization;
  effort lifecycle; progressive retrieval; and projection parity.
- `behavior.py validate` checks every human-authored scenario and fixture
  reference as part of static package verification.

## Static product catalog

- `acceptance-scenarios.json` indexes lifecycle product acceptance cases.

This JSON catalog is validated directly by `verify_package.py`. It is not a
`behavior.py` scenario and does not use the fixture-backed TOML schema. Routing
behavior is exercised by the prose-contract tests here and the separate
evaluation harness under `evals/` rather than a hand-authored answer catalog.

## Deterministic fixture and lifecycle integration

- `test_behavior_fixtures.py` copies fixtures to temporary workspaces, checks
  reset behavior, proves install leaves Wayfinder state unseeded, verifies
  implementation fixtures begin red, detects a destructive state mutation, and
  runs install/update/repeated-update/remove/reinstall once per unique fixture.
- `test_lifecycle.py` retains focused archive, composite, collision,
  provider-isolation, cp1252, and current-state reconciliation coverage.

## Human behavioral contracts and live smoke tests

- `scenarios/*.toml` contain starting state, natural-language request, expected
  behavior, prohibited behavior, and a small observable oracle.
- `fixtures/*` are tiny consuming repositories with no copied framework payload.
- `behavior.py live` installs the framework into disposable fixture copies, runs
  a caller-supplied agent command, captures public evidence, and evaluates the
  scenario without asking for hidden reasoning.

The default live set covers bounded direct work, external research, existing
Wayfinder state, blocked authority, read-only and writable reconciliation,
evidence/fact contradiction, map-only continuation with a native `to-tickets`
handoff, selective uncertainty, unordered work, verification failure/recovery,
and a blocked project. Live cases are opt-in and not part of ordinary pull
requests.

The broader deterministic catalog also covers Domain Modeling surfacing
consequential uncertainty, authority-dependent choices asking a concrete human
question without creating downstream work, Wayfinder assessment concluding that
no durable state is needed, and creating canonical map-first state without
implementation work-item children. Current facts and decisions use optional
`facts.md` and `decisions.md` ledgers; independent unknowns and substantial
evidence retain U#/E# files. Tests cover truthful fact provenance, actual
decision authority, relevant-section retrieval without unrelated detail,
resolved unknowns and redundant evidence leaving current state, effort-lock
serialization across maps, ledgers, U#, and E#, and reference-safe targeted
retirement without requiring a prior commit.

The catalog also covers completed-effort/new-destination separation, explicit
completed-effort access, and ensuring that an unrelated existing effort neither
captures a simple route nor gets loaded. Selective U# promotion keeps
authority-owned, external-approval, and cross-area-gating uncertainty without
promoting incidental fog or requiring an exact artifact count. The live
Wayfinder contracts preserve an unrelated effort during reconciliation, keep
stale-state audits read-only, and require conflicting reconciliation to stop
without guessing. Lifecycle coverage preserves arbitrary unrecognized
project-owned bytes, including binary data and symlink targets, through every
supported lifecycle operation. Deterministic state tests prove unknown content
is not interpreted as current state, independent writes may proceed, and real
recognized-container ambiguity still fails safely.

See [Behavioral testing](../../../docs/behavioral-testing.md) for the schema,
evidence model, commands, side effects, cleanup, and limitations.
