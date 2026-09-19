# Preservation follow-up findings

These historical comparisons did not establish a repeated preservation or continuation advantage sufficient to adopt their candidates.
The final experimental branches restored their baseline runtime instructions and VERSION.
These results do not verify current main, establish equivalence, or resolve the motivating omission's cause.
The earlier [persistence campaign](REPORT.md) is a distinct comparison with different cases and conditions; its results remain unchanged.

## Frozen sources and recovery

The source reports, protocols, compact results, checkpoint citations, controllers, and candidate text remain together at the immutable revisions below.
Each linked directory contains `README.md`, `REPORT.md`, and `results.json`, except the prepared corrected rerun, which has no retained outcome report or results.
Recovering those trees preserves their internal relative links and original qualifications without importing experimental code into current tooling.

| Campaign | Baseline | Frozen candidate/controller | Maintaining source at reviewed tip |
|---|---|---|---|
| Initial unprompted-evidence pilot | `4327a838618fc1fbae8f75689dbfed87830360d7` | `fae83da4fbfdb309fe3816f54dacb4483760034c` | [Initial pilot](https://github.com/jimmfan/agentic-workflow/tree/8ea90b27ed4dd61e71e1b0554af55b67f694eca4/evals/unprompted-evidence) |
| Missing-evidence checkpoint follow-up | `4327a838618fc1fbae8f75689dbfed87830360d7` | `2087455d8c8f4c1db44eba46d7124852bd107201` | [Follow-up](https://github.com/jimmfan/agentic-workflow/tree/8ea90b27ed4dd61e71e1b0554af55b67f694eca4/evals/unprompted-evidence-followup) |
| Seven-turn skill-salience comparison | `26a637de2bc81c7aaee89fd93e23bab84808119d` | `e96529b1e8ad19d1d643290144bdb96d3d57a390` | [Skill salience](https://github.com/jimmfan/agentic-workflow/tree/8ea90b27ed4dd61e71e1b0554af55b67f694eca4/evals/wayfinder-skill-salience) |
| Fixture-blocked incident-derived attempt | `62f84b885c9439c3a6a68e3b030cf17927dc90e7` | `7da736b7b5d68ea3388b7a4149c8e2dd1785963e` | [Stopped attempt](https://github.com/jimmfan/agentic-workflow/tree/8ea90b27ed4dd61e71e1b0554af55b67f694eca4/evals/incident-derived-evidence) |
| Separate isolation-blocked attempt | `4327a838618fc1fbae8f75689dbfed87830360d7` | `ba9a3082139954f39d2014b48e1eae82afb41adf` | [Isolation evidence](https://github.com/jimmfan/agentic-workflow/tree/6760cc6d1764f1ba69200b2ff6a2412268bcd214/evals/wayfinder-incident-evidence) |

Original manifest SHA-256 values are `da42a30a0e2f0aed38903afa364228aacf9c7329ad73a64bb16b18d172d31269` for the initial pilot, `bf64e56445e050dda377d34d1c7209b81a41e42783f5d70f1bca6eb687e55925` for the checkpoint follow-up, and `a8832d9d350ea656eb9ffa9a2f0b8222bedd85d9f34be1856370c5c46d48e278` for the separate isolation-blocked attempt.
Public manifests may normalize machine paths; preserve their recorded original fingerprints rather than expecting normalized bytes to hash identically.

A complete-history Git bundle also preserves these sources, the three local-only corrected-rerun commits, and the [YAML experiment](../wayfinder-yaml/README.md): `2026-09-19-experiments.bundle`, SHA-256 `7d495c22526c7cd317abbb1d427a3f1f1cfb987389f95218a7fce7ea3aabd293`.
The delivery PR records its machine-local absolute location.
Bundle verification and a fresh bare-repository recovery verified all six bundled tips and the frozen candidate commits.
Git hosting may not retain unreachable commits indefinitely; the verified local bundle is the recovery source if an immutable web link becomes unavailable.
Use `git clone --mirror /absolute/path/to/2026-09-19-experiments.bundle recovered.git`, then `git --git-dir=recovered.git show <revision>:<path>` to inspect preserved content.
The mirror may report an unborn default `main`; use the recorded refs or commits explicitly.
This archive contains committed history, not ignored raw evidence or permission to rerun subjects.

## Completed comparisons

All three comparisons used Codex CLI 0.144.6, `gpt-5.6-sol` at medium reasoning, approval `never`, and bounded disposable synthetic consumers.
Their retained protocols/results distinguish intended isolation from observed execution checks and disclose reviewer exposure to implementation context; grading was not fully blind.
No subject outputs were repaired or replaced to improve a result.

**Initial pilot:** twelve comparison stages plus one native probe completed.
Both conditions saved every newly supplied consequential observation, so the motivating omission was not reproduced.
Both tool trajectories lost an earlier diagnostic detail and kept a link to a source removed before fresh reading.
The old-detail failure depends on a stricter frozen rubric whose independent diagnostic value was uncertain; it is not a general requirement to retain every observation.
The broken durable links remain a distinct concrete failure.
The candidate also introduced an unsupported mechanism assertion; read-only controls correctly made no changes, while sufficient-source controls made redundant edits.
Affected-file readback occurred but did not establish semantic correctness.
The first report's provisional recommendation to retain a clarification was superseded by later baseline restoration, not by retroactively changing its observations.

**Checkpoint follow-up:** all 28 planned calls completed, including eight writer/reader trajectories and four controls.
All eight writers saved the new observation and all eight readers recovered its useful meaning; read-only and already-sufficient controls made no writes.
One baseline initialization introduced an unsupported component dependency that persisted in the saved map through stages 16–18, although its reader did not repeat it and recovered the new observation correctly.
One occurrence did not establish repeated candidate benefit.
Process-state interpretations and some readiness wording remained inconclusive; stage 2's initially reported readiness failure was corrected to INCONCLUSIVE after considering the complete saved scope.
That is a grading correction, not a repaired subject result.
Some readers and controls read only part of the contract or read effort state first; successful core recovery does not establish loading compliance.

**Skill salience:** all 36 allocated calls completed, comprising four seven-turn writers, four fresh readers, and four controls.
All writers preserved the consequential finding before dependent work, and every reader recovered useful continuation state.
Baseline reader 08 incorrectly said replay was unavailable despite retained complete input rows; replay and independent source authentication are different capabilities.
Candidate reader 24's similar wording was INCONCLUSIVE because its retained patterns supported reconstruction but not exact-original verification.
Baseline reader 32 actually reconstructed the pattern, preventing a repeated-advantage claim.
The candidate's sufficient-evidence control made one useful map clarification and link; it passed maintenance review without demonstrating a preservation advantage.
Partial contract loading remained observable in reader 24 and controls 33, 34, and 36.
Earlier authorization refusals for control 33 launched no model; later direct authorization allowed the four unchanged controls to finish.
These were authorization events, not behavioral failures or missing final controls.

The skill cue and both contract candidates were rejected for adoption under their frozen repeated-benefit criteria.
Lower aggregate usage was not sufficient: checkpoint-follow-up input differences reversed in the second repetitions, and skill-salience controls cost more even though main trajectories cost less.
Resumed writer counters are cumulative; subtract the preceding turn and do not add cached-input or reasoning-output subsets twice.
Fixed/small samples, cache and latency effects, different investigations, guided prompts, and no observed compaction prevent causal efficiency or long-session reliability claims.
The [context-efficiency effort](../../.project-efforts/context-efficiency/map.md) may use available evidence within its own authorization; it does not reopen these completed campaigns.

## Fixture failure, infrastructure block, and unexecuted preparation

**Fixture-blocked attempt:** one baseline initialization of 34 scheduled calls completed.
Invalid relative map links escaped the synthetic workspace; the writer propagated the bad prefix, and the checkpoint gate stopped continuation before consequential evidence arrival.
No candidate writer, control, isolation case, or fresh reader ran.
The fixture tests and pre-freeze review had missed the link defect.
This is a fixture failure with observed propagation, not a preservation comparison or an observed failure to save the later evidence.
Frozen candidate `7da736b` remains distinct from preliminary unexecuted candidate `a75cee9` and runtime restoration `e917af2`.

**Separate isolation-blocked attempt:** zero evaluated-model invocations, including probes and failed starts; all 36 scheduled calls remained unrun.
Non-model checks allowed a synthetic sibling read and nominally forbidden reader writes.
Changing the permission setup and freezing again did not establish isolation; independent probes reproduced the boundary problem.
A direct operating-system denial worked, narrowing the observation to the CLI/profile integration without establishing its root cause or actual model-tool behavior.
No credentials were copied and no model was contacted.
Intended settings, installed policy hashes, and static cue size are not observed loading, model usage, or behavior.
Its first frozen design `b7638e45e0f9edef3548281a640c9c73eae156f5` and final `ba9a308` remain separate from the fixture-blocked campaign.

**Corrected rerun preparation:** local commits `3a85afb4f9c8281ef30e27d0bcb13021abff6e06`, `ac151178d4b8226ed97659d3c8819cdf6d2ffe66`, and `5a6c7ea8c1563a4b097877fa816a8f04f60365d2` follow remote tip `8ea90b27ed4dd61e71e1b0554af55b67f694eca4`.
They prepare corrected fixture references, materialized-reference preflight and regression controls, freeze the unchanged cue, then restore baseline runtime pending results.
The archive's `5a6c7ea:evals/incident-derived-evidence-rerun/` retains those inputs and protocol.
No outcome report, compact result, execution manifest, or subject traces for that corrected attempt were found in its committed tree or named local raw-evidence location; preparation does not establish execution or a passing preflight.
The branch's map explicitly records previously authorized unfinished work, preserved in the [continuing effort](../../.project-efforts/unprompted-consequential-evidence/map.md).
The cleanup authorizes no new live evaluations and does not silently mark that preparation completed.

## Raw evidence availability

A local inspection on 2026-09-19 found the following ignored locations and left all their contents unchanged.
A recorded location alone does not establish availability on another machine.

| Location under `evals/artifacts/` | Observed retained evidence |
|---|---|
| `unprompted-evidence-20260914/` | 1,262 regular files, 41,793,105 bytes; presence/count checked, not a new full trace adjudication. |
| `unprompted-evidence-followup-20260914/` | All 2,195 inventory entries matched hashes after applying recorded `raw-run/` and `provenance/` relocation. |
| `wayfinder-skill-salience-20260914/` | All 1,621 current inventory entries matched hashes; the prior inventory and retention metadata are additional files. |
| `incident-derived-20260915/execution/` | All 172 inventory entries matched hashes; adjacent metadata and copies remain untouched. |
| `wayfinder-incident-evidence-20260915/` | All 949 inventory entries matched hashes; non-model evidence and policy consumers, not subject traces. |
| `incident-rerun-20260915/` | Only `historical-inventory.json`; no corrected-rerun execution evidence found there. |

The older `/tmp/persistence-quality-final-4`, `/private/tmp/remaining-audit-behavior-live`, and `/private/tmp/wayfinder-question-isolation` roots were absent on that date.
Their committed compact evidence remains available; absence at those locations does not prove no copies exist elsewhere.
The Git bundle preserves none of these ignored files.
Historical deterministic test success remains evidence at its recorded revision, not verification of current main or live reliability.
