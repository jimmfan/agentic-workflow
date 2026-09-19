# Test architecture

Run focused checks from the source repository root with Python 3.11+, Git, and `uv`:

```bash
uv run --locked python -m unittest discover -s tests -p 'test_lifecycle.py' -v
uv run --locked python -m unittest discover -s tests -p 'test_behavior_harness.py' -v
uv run --locked python -m unittest discover -s tests -p 'test_wayfinder_behavior.py' -v
uv run --locked python tests/behavior.py validate
```

The [full required gate](../docs/verification.md#maintainer-and-ci-gate) also covers formatting, package verification, evaluation tooling, and the isolated wheel build.
Use disposable consumers for lifecycle exercises, never the authoring checkout.
Python caches are ignored and need no manual cleanup.

## Test ownership

| Tests | Boundary |
|---|---|
| `test_lifecycle.py`, `test_direct_distribution.py` | Real install/update/status/remove, managed-path safety, complete reserved-skill replacement, unrelated-byte preservation, and partial failures. |
| `test_bootstrap.py` | Release selection, immutable refs, coherent snapshots, optional Git target discovery, archive safety, and CLI delegation. |
| `test_verify_package.py`, `test_routing.py` | Package/distribution structure, attribution, machine-readable interfaces, canonical names, and framework references, including the canonical path for repository-read skill instructions. |
| `test_release_tag.py` | Release validation and immutable publication/retry using disposable repositories and remotes. |
| `test_wheel_inputs.py`, `wheel_smoke.py` | Faithful pending-source capture; separately, sdist/wheel build and CLI execution outside checkout imports. Build dependency resolution may need network access. |
| `test_snapshots.py` | Preservation snapshots that exclude root Git metadata before reads while retaining project entries and read errors. |
| `test_behavior_harness.py` | Scenario validation, blind grading, assertions, route markers, verification evidence, fixture isolation, and negative controls. |
| `test_behavior_interruption.py` | Real SIGINT in disposable POSIX harness processes, evidence retention before default cleanup, and stopping after the interrupted attempt. |
| `test_wayfinder_state.py`, `test_wayfinder_behavior.py`, `test_routing_boundaries.py` | Literal state fixtures and evaluator acceptance/rejection of routing, authority, reconciliation, and no-state outcomes. |
| `test_export_continuity.py` | Maintained photo-export scenarios covering exact configuration bytes, unchanged source artifacts, ambiguous intent, unrelated work, read-only requests and unsafe paths. |
| `test_question_review_controls.py`, `test_map_authoring_controls.py` | Question-section preservation, incoming references, stale-state rejection, and map-authoring evaluator controls. |
| `test_scenario_constraints.py` | Active preservation/forbidden-path declarations and acceptance/rejection of authorized title changes, relevant resumption, read-only review, and forbidden tickets. |
| `test_smoke_expectations.py` | Smoke evaluator rejection of missing required evidence and invented critical paths, with supported layout and truthful uncertainty controls. |
| `evals/tests/` | Separate network-free tests of evaluation tooling. |

`scenarios/*.toml` define human-authored requests and observable outcomes; `fixtures/*` supply small starting repositories without copied framework payload.
The [behavioral guide](../docs/behavioral-testing.md) owns scenario syntax, wrapper conventions, live commands, side effects, and cleanup.
Live runs are opt-in and do not belong to ordinary PR gates.

Synthetic-answer tests validate evaluators, not actual agent reads, independent Standards/Spec review, research, TDD cycles, or compliance with instructions.
Retained response controls exercise maintained scenario rubrics or the harness's assertion operators.
Their predicates are fixture-specific, not proof of semantic completeness for arbitrary answers.
Static checks protect literal paths, canonical names, record syntax and protocol fields; instruction meaning requires review and applicable live evidence.
When changing a scenario's grading rules, retain historical results under their original rules and compare future subjects using the same revised harness and scenario version.
Blind prompts must remain unchanged when only hidden grading requirements change; guided rubric changes must be disclosed.
Historical obligation-preservation rationale and review evidence remain retrievable in the [instruction-coherence review at its immutable revision](https://github.com/jimmfan/agentic-workflow/blob/727e9c9299c980e29dee5589b4638e779bf49209/docs/reviews/instruction-coherence.md); it is not the current test contract.
The [implementation-completion protocol](../evals/implementation-completion/README.md#fixture-preparation) retains the historical fixture recipe and frozen evaluation interpretation separately from the current suite.

## Wayfinder coverage and evidence limits

The [state contract](../.agent-workflow/contracts/wayfinder-state.md) and [Wayfinder skill](../.agents/skills/wayfinder/SKILL.md) define agent behavior.
There is no shipped Wayfinder initializer; fixture validation does not execute those instructions.

| Requirement | Evidence and remaining gap |
|---|---|
| Semantic effort selection, mapless exclusion, collisions, and scope refinement | Scenario inputs and negative evaluator controls cover candidate outcomes; actual matching and safe agent path selection need live evidence. |
| Record syntax, identity, and references | Explicit fixtures reject malformed/duplicate IDs and dangling references; before/after settlement examples check stable identities and source relations. Agent allocation, immediate rereads, and no-overwrite execution remain unverified. |
| Reconciliation, scoped ambiguity, and preservation | Assertions inspect final state, neighboring question sections, external/hidden backlinks, and unrelated bytes. They do not prove reference discovery, preservation before pruning, or concurrent-change checks. |
| Effort ending and continuation | Blocked/ending scenarios retain final-state controls; map-last removal, temporal ordering, and safe agent deletion remain unverified. |
| Progressive loading and existing-state reuse | `state_used` records a public claim. Actual reads and reuse remain INCONCLUSIVE without separate evidence. |
| Human question review and map meaning | Controls reject supplied stale-state, authority, and content errors. Actual questioning, interruption recovery, fresh-session continuation, and map-only question meaning need separate adjudication. |
| Filesystem safety | Real lifecycle/bootstrap tests establish framework delivery boundaries, including no direct traversal or mutation of `.project-efforts/`; they do not prove Wayfinder mutation safety. |

The simple-project verifier detects extra commits present during verification, not rewritten history or later commits.
Local draft-publication checks do not observe external publication.
Research URLs and route markers remain claims unless independently supported.
A synthetic positive can still be INCONCLUSIVE when required behavior is unobserved; `None` never means PASS.
See the [question-review smoke procedure and execution limitation](../evals/wayfinder-question-resolution/README.md) and [evaluation index](../evals/README.md) for preserved live evidence.
