# Test architecture

Tests are separated by determinism and product boundary.

Run focused unittest commands with `python3 -m unittest ...`.
Python's generated `__pycache__` files are ignored by Git and by package verification; they do not need manual cleanup.
The full verifier also disables bytecode writes in its test subprocess.

Run `python3 skills/agent-workflow/tests/wheel_smoke.py -v` separately to build the wheel through an isolated PEP 517 build, install it into a disposable virtual environment, and invoke its `agent-workflow` entry point against one plain non-Git directory using a local archive.
This packaging-isolation smoke does not exercise live or mocked latest-release discovery.
It is intentionally outside the deterministic unittest discovery gate because resolving the declared build backend may require package-index access.

## Production-boundary unit and integration tests

- `test_lifecycle.py` owns install, update, status, remove, composite-file and managed-path safety boundaries.
- `test_direct_distribution.py` owns whole-directory direct skill replacement, current mapping, current-name convergence, unrelated-skill preservation, noninteractive reserved-name convergence, conservative unrecognized removal, obsolete framework-file convergence, partial-failure reporting, and removal.
- `test_verify_package.py` owns package shape, exact payload inventory, attribution, focused semantic contracts, and distribution-map refresh validation.
- `test_bootstrap.py` owns latest-stable semantic release selection, immutable ref resolution, explicit-ref bypass, coherent downloaded lifecycle and payload, optional Git root discovery, archive parsing, extraction and root safety, offline bootstrap, and CLI delegation.
- `test_routing.py` owns direct/progressive routing, explicit selection, specialist boundaries, Wayfinder loading, authority blocking, fail-closed state loading, and semantic progressive-loading boundaries.
- `test_wayfinder_state.py` owns deterministic state representation, allocation, changed-state detection, no-overwrite creation, reconciliation, reference safety, and project-data preservation.

## Behavior harness and Wayfinder behavior

- `test_behavior_harness.py` validates scenario schema and vocabulary, blind grading, evaluator assertions, route markers, verification evidence, fixture isolation, destructive-change detection, and intentionally-red fixtures.
- `test_wayfinder_behavior.py` validates Wayfinder scenario semantics, current record presence, authority, progressive loading, conflict promotion, reconciliation, blocked pruning, safe whole-effort ending, and no-state outcomes.
- `behavior.py validate` checks every human-authored scenario and fixture reference as part of static package verification.

The lifecycle suite proves framework operations do not directly traverse, interpret, or change `.agent-wayfinder/`.
Wayfinder fixtures independently prove reset, evaluator, and scenario behavior; they do not participate in lifecycle tests.

## Human behavioral contracts and live smoke tests

- `scenarios/*.toml` contain starting state, natural-language request, expected behavior, prohibited behavior, and a small observable oracle.
- `fixtures/*` are tiny consuming repositories with no copied framework payload.
- `behavior.py live` installs the framework into disposable fixture copies, runs a caller-supplied agent command, captures public evidence, and evaluates the scenario without asking for hidden reasoning.

The default live set is a representative smoke sample covering direct work, external research, blocked authority, read-only and writable reconciliation, evidence/fact contradiction, map-only continuation with a `to-tickets` ticket or ticket set workflow transition, selective uncertainty, verification recovery, blocked work, and the valid outcome that Wayfinder assessment creates no state.
Live cases are opt-in and not part of ordinary pull requests.

The broader deterministic catalog also covers Domain Modeling surfacing consequential uncertainty, choices requiring project decision authority asking a concrete human question without creating downstream work, Wayfinder assessment concluding that no durable state is needed, and creating recognized map-first state without implementation work-item children.
Current facts and decisions use optional `facts.md` and `decisions.md` ledgers; independently useful unresolved questions and substantial evidence retain U#/E# files.
Presence means a U# remains unresolved and a D# remains the current choice committed by project decision authority; neither uses a lifecycle status field.
Tests cover direct fact-source relations, project decision authority, relevant-section retrieval without unrelated detail, answered questions and redundant evidence leaving current coordination state, reference-safe targeted pruning without requiring a prior commit, changed-state rejection, and no-overwrite U#/E# creation.
Unrecognized content inside U/E containers is preserved, while identity-like malformed entries block the affected U/E operation.

The catalog also covers blocked-effort resumption, mapless directories being excluded from selection, and ensuring that an unrelated existing effort neither captures a simple route nor gets loaded.
Selective U#/E# promotion keeps questions requiring project decision authority, external-approval questions, and cross-area-gating uncertainty without promoting incidental uncertainty or requiring an exact artifact count.
The live Wayfinder contracts preserve an unrelated effort during reconciliation, keep outdated-state audits read-only, and require conflicting reconciliation to stop without guessing.

Repository evaluation-tooling tests under `evals/tests/` remain a separate network-free CI step and are not part of the distributed package gate.

See [Behavioral testing](../../../docs/behavioral-testing.md) for the schema, evidence model, commands, side effects, cleanup, and limitations.
