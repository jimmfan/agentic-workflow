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
- `test_routing.py` validates representative selection, invocation,
  authorization, record-based resume, and durable-effect decisions without
  requiring one exact trace.
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

Nine live cases are enabled by default: simple bounded work, external research,
existing Wayfinder state, read-only stale-state reporting, reconciliation
conflict handling, evidence/fact contradiction reconciliation, map-only
continuation with a native `to-tickets` handoff, verification failure/recovery,
and a blocked project. They are opt-in and not part of ordinary pull requests.

The broader deterministic catalog also covers creating canonical map-first
Wayfinder state without implementation work-item children, optional U#/E#/F#/D#
knowledge, and ensuring that an unrelated existing effort neither captures a
simple route nor gets loaded. The live Wayfinder contracts preserve
an unrelated effort during reconciliation, keep stale-state audits read-only,
and require conflicting reconciliation to stop without guessing. Non-Wayfinder
durable work resumes from its named DEC/IMP/DBG record without a global active
index.

See [Behavioral testing](../../../docs/behavioral-testing.md) for the schema,
evidence model, commands, side effects, cleanup, and limitations.
