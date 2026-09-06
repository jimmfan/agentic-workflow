# Test architecture

Tests are separated by determinism and product boundary.

Run focused unittest commands with `python3 -m unittest ...`.
Python's generated `__pycache__` files are ignored by Git and by package verification; they do not need manual cleanup.
The full verifier also disables bytecode writes in its test subprocess.

Run `python3 tests/wheel_smoke.py -v` separately to build the wheel through an isolated PEP 517 build, install it into a disposable virtual environment, and invoke its `agent-workflow` entry point against one plain non-Git directory using a local archive.
This packaging-isolation smoke does not exercise live or mocked latest-release discovery.
It is intentionally outside the deterministic unittest discovery gate because resolving the declared build backend may require package-index access.

## Production-boundary unit and integration tests

- `test_lifecycle.py` owns install, update, status, remove, composite-file and managed-path safety boundaries.
- `test_direct_distribution.py` owns whole-directory direct skill replacement, current mapping, current-name convergence, unrelated-skill preservation, noninteractive reserved-name convergence, conservative unrecognized removal, obsolete framework-file convergence, partial-failure reporting, and removal.
- `test_verify_package.py` owns package shape, exact source inventories, distribution integrity, safety, attribution, machine-readable contracts, and distribution-map refresh validation.
- `test_bootstrap.py` owns latest-stable semantic release selection, immutable ref resolution, explicit-ref bypass, coherent downloaded lifecycle and resources, optional Git root discovery, archive parsing, extraction and root safety, offline bootstrap, and CLI delegation.
- `test_routing.py` owns canonical term names, routing interface syntax, and framework reference paths; ordinary instruction wording and terminology definitions are not literal test contracts.
- `test_release_tag.py` exercises read-only validation and immutable publication/retry against disposable local repositories and remotes.
- `test_wheel_inputs.py` checks faithful pending-source snapshot capture without building.

## Behavior harness and Wayfinder behavior

- `test_behavior_harness.py` validates scenario schema and vocabulary, blind grading, evaluator assertions, route markers, verification evidence, fixture isolation, destructive-change detection, and intentionally-red fixtures.
- `test_wayfinder_behavior.py` validates Wayfinder scenario semantics, current record presence, authority, progressive loading, conflict promotion, reconciliation, blocked pruning, safe whole-effort ending, and no-state outcomes.
- `test_routing_boundaries.py` challenges evaluators with valid minimum routes, Research/Discovery composition, unauthorized local publication and commits, map-only coordination, settled choices, missing plan steps, and contradictory or prohibited state.
- `behavior.py validate` checks every human-authored scenario and fixture reference as part of static package verification.

The lifecycle suite proves framework operations do not directly traverse, interpret, or change `.project-efforts/`.
Wayfinder fixtures independently prove reset, evaluator, and scenario behavior; they do not participate in lifecycle tests.
Routing and behavioral tests challenge observable workflow outcomes using the existing scenario harness.
Their deterministic runs test the evaluators against accepted and rejected outcomes; live-agent compliance remains a separate opt-in evaluation.
The `simple-project` fixture verifier checks the greeting and that its Git history still contains only the baseline commit.
This catches additional commits present during verification; it does not detect rewritten history or later commits.
The draft-publication scenario observes local files; external publication remains outside its evidence.

## Human behavioral contracts and live smoke tests

- `scenarios/*.toml` contain starting state, natural-language request, expected behavior, prohibited behavior, and a small observable oracle.
- `fixtures/*` are tiny consuming repositories with no copied framework payload.
- `behavior.py live` installs the framework into disposable fixture copies, runs a caller-supplied agent command, captures public evidence, and evaluates the scenario without asking for hidden reasoning.

The default live set is a representative smoke sample covering direct work, external research, blocked authority, read-only and writable reconciliation, evidence/fact contradiction, map-only continuation with a `to-tickets` ticket or ticket set workflow transition, selective uncertainty, verification recovery, blocked work, and the valid outcome that Wayfinder assessment creates no state.
Live cases are opt-in and not part of ordinary pull requests.

The broader deterministic catalog also covers clear requests with an objective staying on the minimum route, ambiguous intent stopping before invented Wayfinder creation, consequential objectives selecting durable coordination without naming Wayfinder, and scope refinement resuming the semantically matching effort without exact wording or a sibling effort.
It covers bounded architectural choices using Discovery rather than Domain Modeling, Discovery composing Research for external facts, Domain Modeling surfacing consequential domain-language or context-boundary uncertainty, choices requiring project decision authority asking a concrete human question without creating downstream work, Wayfinder assessment concluding that no durable state is needed, and creating recognized map-first state without implementation work-item children.
Current facts and decisions use optional `facts.md` and `decisions.md` ledgers; independently useful unresolved questions and substantial evidence retain U#/E# files.
Presence means a U# remains unresolved and a D# remains the current choice committed by project decision authority; neither uses a lifecycle status field.
Fixtures encode direct fact-source relations, project decision authority, relevant-section retrieval, and reference reconciliation for answered questions and redundant evidence.
They do not execute an agent's retrieval, allocation, race checks, pruning, or no-overwrite behavior.

The catalog also covers blocked-effort resumption, mapless directories being excluded from selection, and ensuring that an unrelated existing effort neither captures a simple route nor gets loaded.
Selective U#/E# promotion keeps questions requiring project decision authority, external-approval questions, and cross-area-gating uncertainty without promoting incidental uncertainty or requiring an exact artifact count.
The live Wayfinder contracts preserve an unrelated effort during reconciliation, keep outdated-state audits read-only, and require conflicting reconciliation to stop without guessing.

Repository evaluation-tooling tests under `evals/tests/` remain a separate network-free CI step and are not part of the distributed package gate.

See [Behavioral testing](../docs/behavioral-testing.md) for the schema, evidence model, commands, side effects, cleanup, and limitations.

## Wayfinder coverage and evidence limits

`test_wayfinder_state.py` now contains contract/fixture validation only.
The former test-local substring selector and create/update/rename/prune/end algorithms had no callers outside that file and were not shipped implementations.
No Wayfinder initializer exists in current shipped source; the actual lifecycle/CLI and disposable fixture initialization tests remain.
The contract, routing policy, skill prose, identifiers, map shape, and empty-blocker authoring convention are unchanged.

| Removed test-local claim | Retained evidence or explicit limit |
|---|---|
| Semantic selection, exact-path selection, mapless exclusion, collisions, in-place scope refinement | Existing scenario inputs and negative evaluator controls remain; actual semantic matching and safe agent path selection are unverified without a live run. |
| F/D/U/E parsing and duplicate detection | Small explicit fixture checks reject zero/malformed/duplicate IDs and symlink records; these validate fixture syntax only. |
| ID allocation after the highest current ID, no interior recycling, late duplicates | Required by the unchanged contract; agent allocation and immediate rereads remain unverified. |
| No-overwrite creation/rename, changed-map/ledger rejection, optimistic concurrency | Required by the unchanged contract; no test-local implementation is presented as execution evidence. |
| Rename/prune reference reconciliation, direct fact support, stable F8/D4 identity | Explicit before/after settlement fixtures and dangling-file/renamed-anchor negative cases check the claimed final references and identities; other scenarios retain outcome assertions. |
| Scoped ambiguity and unrecognized-content isolation | Fixture shape checks and scenario preservation assertions remain; agent interpretation and operation scoping remain unverified. |
| Byte preservation, symlink/root safety, composite handling, partial failure | Real lifecycle/bootstrap/direct-distribution tests remain, including historical composite bytes, permissive consumer updates, non-Git/dirty targets, and injected later-write failure. These prove lifecycle safety, not Wayfinder mutation safety. |
| Effort ending, continuation artifacts, map-last removal, no recursive deletion | Existing blocked/ending scenarios retain final-state negative controls. Timing, concurrent change detection, and map-last agent execution remain unverified. |

A synthetic evaluator positive may contain no observed failure while its overall behavioral verdict is still INCONCLUSIVE.
`None` is never a behavioral PASS.
The deterministic suite's success means its graders accept/reject/abstain on those synthetic observations as specified.
