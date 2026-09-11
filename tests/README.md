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
- `test_snapshots.py` checks that preservation snapshots exclude root Git metadata before traversal or reads while retaining project bytes, directories, symlinks, and errors reading project files.

## Behavior harness and Wayfinder behavior

- `test_behavior_harness.py` validates scenario schema and vocabulary, blind grading, evaluator assertions, route markers, verification evidence, fixture isolation, destructive-change detection, and intentionally-red fixtures.
- `test_wayfinder_behavior.py` validates Wayfinder scenario semantics, current record presence, authority, progressive loading, conflict promotion, reconciliation, blocked pruning, safe whole-effort ending, and no-state outcomes.
- `test_routing_boundaries.py` challenges evaluators with valid minimum routes, Research/Discovery composition, unauthorized local publication and commits, map-only coordination, settled choices, missing plan steps, and contradictory or prohibited state.
- `test_review_handoff.py` uses disposable Git repositories and the existing scenario evaluator to challenge committed-only versus implementation-scope review boundaries.
- `test_instruction_coherence.py` uses synthetic requests and candidate answers to challenge agreement reuse, bounded synthesis, vocabulary and failure-coverage preservation, ticket prerequisites, prototype scope, and capability reporting through the same evaluator.
- `behavior.py validate` checks every human-authored scenario and fixture reference as part of static package verification.

The lifecycle suite proves framework operations do not directly traverse, interpret, or change `.project-efforts/`.
Wayfinder fixtures independently prove reset, evaluator, and scenario behavior; they do not participate in lifecycle tests.
Routing and behavioral tests challenge observable workflow outcomes using the existing scenario harness.
Their deterministic runs test the evaluators against accepted and rejected outcomes; live-agent compliance remains a separate opt-in evaluation.
The `simple-project` fixture verifier checks the greeting and that its Git history still contains only the baseline commit.
This catches additional commits present during verification; it does not detect rewritten history or later commits.
The draft-publication scenario observes local files; external publication remains outside its evidence.

### Implementation review evidence limits

`test_review_handoff.py` reproduces the omission of staged, unstaged, and untracked defects by `git diff <baseline>...HEAD`, including a plausible earlier implementation commit.
Git-only observations also cover a tracked deletion, staged rename, and a renamed file whose resulting content differs from its index content.
It executes the small defective fixture functions to establish their incorrect results, then submits explicit synthetic candidate responses to the existing `Scenario` / `RunEvidence` evaluator seam.
The controls reject success reports with no concrete defect findings, an earlier-commit-only response, or findings missing the required new file.
Other controls supply acceptance criteria directly in the current request, exclude pending work for an explicitly committed-only request, and distinguish pre-existing unrelated hunks from implementation changes in the same file.
These fixture-specific response checks establish what the evaluator accepts or rejects; they do not establish that a reviewer read any file, selected the right diff, or executed independent Standards and Spec review.
The synthetic scenarios are constructed in the deterministic tests; no new live scenario or review-selection engine is introduced.

Read-only Git observations are bounded by comparisons of project bytes, raw index bytes, and `HEAD` before and after the observations.
Negative controls deliberately alter each of those surfaces in disposable repositories to show the comparisons detect changes.
The existing scenario evaluator separately rejects observed project-file mutation; its project snapshot excludes Git internals, so index and history preservation are direct Git-test evidence, not added evaluator claims.
No live-agent campaign runs in these tests, and successful deterministic controls do not prove compliance with the instruction handoff.

### Instruction-coherence evidence limits

`test_instruction_coherence.py` constructs synthetic scenarios using the existing `Scenario` / `RunEvidence` seam and disposable copies of the existing simple-project fixture.
It submits explicit positive and negative candidate answers, including contradictory success claims, to fixture-specific response predicates.
The controls cover accepted versus missing TDD seam agreement, a supported specification without an interview or invented approval, established project vocabulary and an application-internal module interface, failure tests that must remain until replacement coverage is verified, real versus invented ticket prerequisites, conditional expand-contract, prototype isolation, and synchronous research versus unavailable independent review.
Separate observed project-file mutations demonstrate that the evaluator rejects premature artifacts and unauthorized production adoption even when the response looks acceptable.

These are evaluator controls, not skill implementations or snapshots of instruction prose.
Agreement provenance is supplied in the synthetic requests; the tests do not observe an agent retrieving accepted artifacts, obtaining human agreement, following red-green cycles, verifying replacement failure coverage, researching sources, or running independent reviewers.
Reported research URLs remain `INCONCLUSIVE` because source access and factual correctness are unobserved.
Response predicates reject the supplied counterexamples but do not establish semantic completeness for arbitrary answers, behavioral equivalence of the rewritten instructions, or external publication and commit behavior.
The existing Git review-handoff controls remain the separate evidence for pending changes and Git preservation.
No live scenario or campaign is added or rerun by these controls.

## Human behavioral contracts and live smoke tests

- `scenarios/*.toml` contain starting state, natural-language request, expected behavior, prohibited behavior, and a small observable oracle.
- `fixtures/*` are tiny consuming repositories with no copied framework payload.
- `behavior.py live` installs the framework into disposable fixture copies, runs a caller-supplied agent command, captures public evidence, and evaluates the scenario without asking for hidden reasoning.

The default live set is a representative smoke sample covering direct work, external research, blocked authority, read-only and writable reconciliation, evidence/fact contradiction, map-only continuation with a `to-tickets` ticket or ticket set workflow transition, selective uncertainty, verification recovery, blocked work, and the valid outcome that Wayfinder assessment creates no state.
Live cases are opt-in and not part of ordinary pull requests.

The broader deterministic catalog also covers clear requests with an objective staying on the minimum route, ambiguous intent stopping before invented Wayfinder creation, consequential objectives selecting durable coordination without naming Wayfinder, and scope refinement resuming the semantically matching effort without exact wording or a sibling effort.
It covers bounded architectural choices using Discovery rather than Domain Modeling, Discovery composing Research for external facts, Domain Modeling surfacing consequential domain-language or context-boundary uncertainty, choices requiring project decision authority asking a concrete human question without creating downstream work, Wayfinder assessment concluding that no durable state is needed, and creating recognized map-first state without implementation work-item children.
Current U#/F#/D# records use optional `unknowns.md`, `facts.md`, and `decisions.md` ledgers; independently useful evidence retains E# files.
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
The current contract and Wayfinder skill define agent behavior; these fixture checks do not execute those instructions.

| Removed test-local claim | Retained evidence or explicit limit |
|---|---|
| Semantic selection, exact-path selection, mapless exclusion, collisions, in-place scope refinement | Existing scenario inputs and negative evaluator controls remain; actual semantic matching and safe agent path selection are unverified without a live run. |
| F/D/U/E parsing and duplicate detection | Small explicit fixture checks reject zero/malformed/duplicate IDs and symlink records; these validate fixture syntax only. |
| ID allocation after the highest current ID, no interior recycling, late duplicates | Required by the current contract; agent allocation and immediate rereads remain unverified. |
| No-overwrite creation/rename, changed-map/ledger rejection, optimistic concurrency | Required by the current contract; no test-local implementation is presented as execution evidence. |
| Rename/prune reference reconciliation, direct fact support, stable F8/D4 identity | Explicit before/after settlement fixtures and dangling-file/renamed-anchor negative cases check the claimed final references and identities; other scenarios retain outcome assertions. |
| Scoped ambiguity and unrecognized-content isolation | Fixture shape checks and scenario preservation assertions remain; agent interpretation and operation scoping remain unverified. |
| Byte preservation, symlink/root safety, composite handling, partial failure | Real lifecycle/bootstrap/direct-distribution tests remain, including historical composite bytes, permissive consumer updates, non-Git/dirty targets, and injected later-write failure. These prove lifecycle safety, not Wayfinder mutation safety. |
| Effort ending, continuation artifacts, map-last removal, no recursive deletion | Existing blocked/ending scenarios retain final-state negative controls. Timing, concurrent change detection, and map-last agent execution remain unverified. |

A synthetic evaluator positive may contain no observed failure while its overall behavioral verdict is still INCONCLUSIVE.
`None` is never a behavioral PASS.
The deterministic suite's success means its graders accept/reject/abstain on those synthetic observations as specified.

### Question ledger and human-review controls

`test_question_review_controls.py` uses the existing Scenario/RunEvidence evaluator and one synthetic parcel-review fixture.
Section identity snapshots allow an answered middle section to disappear while neighboring questions retain their exact contents; malformed or duplicate U IDs and unsafe ledger targets cannot masquerade as section absence.
Controls also expose stale replacement, dangling references, unauthorized review writes, selected prerequisite/answer mistakes, changed deferral consequences, and unavailable or standalone Grilling.
Map-only question meaning is left for adjudication when only a map mutation is observable.
These checks do not execute conversion, agent race checks, actual questioning, interruption recovery, or fresh-session continuation.
See the [bounded smoke procedure and execution limitation](../evals/wayfinder-question-resolution/README.md).
