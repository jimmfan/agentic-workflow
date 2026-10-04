# Matched short objective-acceptance trajectories

Both arms passed the same 28 declared checks once: 12 mechanical or observed-command checks and 16 independent semantic judgments.
The requested CSV implementation, corrected reported print evidence, saved acceptance boundary and fresh-reader reconstruction were observed in both trajectories.
These results do not demonstrate an advantage for the installed workflow on this case; they also do not establish equivalence, reliability or causality beyond these two observations.

| Observation | Installed workflow | Vanilla project |
|---|---:|---:|
| Complete trajectories | 1 | 1 |
| Native turns completed | 8 | 8 |
| Mechanical / command checks | 12 PASS | 12 PASS |
| Independent semantic judgments | 16 PASS | 16 PASS |
| Controller elapsed seconds | 296.9 | 180.1 |
| Final writer input counter | 1,155,153 | 423,358 |
| Final writer cached-input counter | 1,082,496 | 389,888 |
| Final writer output counter | 12,412 | 6,706 |
| Fresh reader input counter | 133,422 | 45,238 |
| Fresh reader output counter | 851 | 631 |

The full public prompts, initial project file contents and permission modes, scenario checks, allowed writes, writer/reader pattern, model (`gpt-6.1-sol`), medium reasoning effort, Fast overrides, no-subagent setting and 300-second turn / 1800-second supervisor bounds matched.
The workflow arm used product commit `deb91942ac45373111a6bc615b359b2bbb230a68` (0.41.2).
Vanilla started with an empty project payload and has no product commit/version.
An external freezer supplied that payload before freezing through the preparation hook; the pinned native runtime and scoring code were unchanged.
All private consumer paths were independent and the vanilla subject path was neutral.

Vanilla excludes installed project workflow policy, AGENTS/CLAUDE files, project skills and prior effort/handoff state.
Native default/provider/managed instructions and five bundled system skills remain; their skill-file hashes matched in both writer and reader homes.
The unchanged task prompt explicitly requests handoff and later acceptance tracking, so this control tests project-workflow absence under those task cues, not an instruction-free or cue-free model.

The vanilla T6 handoff lacked a newly saved rerun-specific provenance entry.
Its reviewer judged the retained current check state accurate and consistent with the captured rerun under the existing criterion.
That PASS does not establish durable per-invocation provenance; the rubric was not tightened after observing execution.
The workflow arm retained its additional effort artifacts; no extra score was assigned for artifact layout alone.

The arms ran sequentially, with one trajectory each and different generation histories; the same independent reviewer graded smoke, workflow and vanilla.
[Reviewer provenance](native-macos-objective-short/reviewer-provenance.json) binds both full-run grades to that same reviewer after prior calibration controls passed 48/48.
Read-only source metadata and app thread history resolve the initially missing artifact-level identity/calibration link without changing original grades; reviewer model and effort remain unspecified.
The same reviewer is not independent replication, and calibration agreement does not establish universal grading correctness.
Review citations and supplied judgments validated against original and publication packets, with disclosed encoding/supplementary-evidence normalization.
Residual file/route cues limit blinding, and parser warnings limit transcript coverage.
Print observations are synthetic secondhand reports; owner physical alignment review and final acceptance remain pending.
Fresh-reader reconstruction is separate from real compaction survival.

Completion usage reports contain cumulative writer counters: continuation reports and rollout snapshots are not summed.
The durations and counters above are descriptive observations, not billed usage, an active-context measurement, a measured Fast-mode speed effect, or evidence that workflow caused the difference.
Both arms requested Fast; native priority labels appear only on writer continuations, with first-writer/fresh-reader actual tier unobserved.

[Workflow evidence](native-macos-objective-short/README.md) and [vanilla evidence](native-macos-vanilla-objective-short/README.md) retain the prompts, responses, saved files, settings, grade citations and privacy manifests.
