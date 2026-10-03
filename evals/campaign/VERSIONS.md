# Choosing historical comparisons

These are proposed experiment candidates, not performance results or recommendations to revert framework changes.
The selection follows changes in distributed behavior and known failure families, rather than round version numbers.
Source inspection is pinned to `deb91942ac45373111a6bc615b359b2bbb230a68` (v0.41.2).
No live historical comparison has been executed by creating this document.

## First screen: four intact instruction bundles

Run the same common-outcome stories against these four candidates before trying skill combinations.
The [milestone example](examples/milestones.json) freezes the selected commits.
One trajectory per candidate is a screen for useful differences, not a reliability estimate or a winner selection.

| Candidate | Immutable commit | Evidence-based reason to include it |
|---|---|---|
| v0.33.2: consolidated state contract | `e3efb70456b3fb94fe4e5d2e380a36b879f3b905` | PR #40 consolidated the state contract in place, reducing it from 383 to 320 physical lines relative to v0.33.1 while retaining the new specialist-result and evidence-preservation obligations. This provides an earlier coherent policy before the later completion, objective-scope, and per-turn maintenance changes. It is not assumed to be the shortest or best policy. |
| v0.35.1: completion handoff and native exposure | `910200a3cf6f5c9a06a329cb64f7830b2487489c` | Includes PR #48's handoff from direct `implement` into acceptance verification and route reassessment, and PR #54's restoration of the session-exposed-skill requirement. It immediately precedes the objective-scope and guidance-maintenance fixes, making it a useful boundary for both stories. |
| v0.35.3: persistent maintenance authorization | `d82771e4509494e7cd9f21e8697de93805bde392` | Includes PR #55's objective-wide continuation trigger and early-map instruction, then PR #56's explicit continuation of maintenance authorization across question/guidance turns, per-turn reconciliation, saved-state reread, and distinction between required post-delivery verification and optional residual uncertainty. |
| v0.41.2: current anchor | `deb91942ac45373111a6bc615b359b2bbb230a68` | Includes the later progressive records-contract split, routing-conflict corrections, bounded verification-fix loops, in-place map updates, failed-attempt preservation, dated/owned external facts, and same-turn preservation of relevant reported environment facts. This tests the combined current policy against the earlier bundles. |

The first screen answers which bundles preserve the user's required outcomes on these cases.
Differences between nonadjacent releases cannot identify which individual instruction caused an outcome.
In particular, v0.35.3 combines authorization, reconciliation, and effort-ending changes; it is not a clean ablation of one sentence.

Do not repeat the separate Work Mode baseline-comparison campaign or add another no-framework arm here by default.
That campaign's evidence remains under its own frozen protocol and branch.
An existing run can substitute for this screen's current anchor only if its scenario, initial files, model, host, permissions, observations, repetition, and grading requirements actually match; a shared framework SHA alone is insufficient.
Otherwise the current anchor is a necessary matched control for these new cases, not a rerun of that earlier experiment.

## Optional expansion: at most two more bundles

Add a candidate only when the first screen leaves its question unresolved.

| Candidate | Immutable commit | Question and reason to defer |
|---|---|---|
| v0.31.0: earlier map and record representation | `96ec2fbd4b75d03f1828771bb10ec4b396bbfda0` | Includes PR #30's corrected-detail preservation and bounded readback, and PR #31's map-authoring guidance, but still uses separate `unknowns/U<ID>-<slug>.md` files rather than the later question ledger. Add it if map shape, record fragmentation, or the effect of later simplification matters; it is a larger representation change than the first screen needs. |
| v0.37.0: progressive record loading | `cea59870b4287f4914a7ac07a26e5aef872f731c` | Splits record mechanics into lazily loaded `effort-records.md` and makes hard-signal precedence explicit. Add it if v0.35.3 and current differ and observed reading/maintenance work suggests instruction loading or later growth. The existing stories do not independently establish that map-only work avoids record-contract loading; inspect traces or add a focused map-only case. |

This keeps the initial search to four bundles and a justified expansion to six.
Do not test every release simply because its tag exists.

## Three adjacent comparisons for diagnosis

Use a pair only after a corresponding failure or meaningful difference appears, and retain both positive cases and boundary controls.
These are first-parent before/after release changes, so their distributed diffs can be inspected directly without mixing skills.
They isolate a change set more closely than the broad screen, but do not establish causation from a single stochastic trial.

| Failure family | Before commit | After commit | Actual distributed change and focused probe |
|---|---|---|---|
| Corrected evidence loses detail or changes scope | `a963f707f9123d5af870dfe06f06d3d1ee1802f8` | `b8ac8a4c48b61ac7fbca923c2c673ab19945577e` | PR #30 changes only the Wayfinder skill and state contract among distributed surfaces. It adds preservation of new, corrected, and still-valid details; identity/status/source/scope relationships; consequence reconciliation; pre-pruning retrievability; and bounded saved-result readback. Probe reported versus verified evidence, corrected counts, preserved qualifications, and what a fresh reader can recover. |
| Immediate edit obscures the continuing objective | `910200a3cf6f5c9a06a329cb64f7830b2487489c` | `97058a23f229657494747d461ab69021f31a1d97` | PR #55 changes the distributed root template: assess continuation required by the whole requested objective, and establish/resume the required effort map before substantive implementation. Probe the neutral implementation-plus-later-acceptance story and the routine-edit control; inspect action ordering as well as final files. |
| Guidance turns silently stop updating authorized effort state | `97058a23f229657494747d461ab69021f31a1d97` | `d82771e4509494e7cd9f21e8697de93805bde392` | PR #56 adds standing maintenance authorization and before-final-response reconciliation, separates method routing from effort continuity, requires rereading saved state, and clarifies remaining verification at effort ending. Probe guidance corrections, unchanged follow-ups, explicit write pause, renewal, and fresh continuation. The contract rename and ending rules travel with this intact change set. |

The earlier [persistence report](../wayfinder-persistence/REPORT.md) found overall comparative benefit INCONCLUSIVE; its successful deterministic controls and merged change do not establish that PR #30 solved the motivating omission.
The [objective-scope report](../objective-scope-routing/REPORT.md) observed late coordination in two of three revised positive baseline trials, with one positive pass and passing bounded controls; the candidate instruction change was not run in that historical campaign.
Those are reasons to target the mechanisms with new cases, not to predeclare expected winners or to rerun old evidence until it passes.

## Coverage and interpretation

| Concern | Relevant history | What these scenarios can establish |
|---|---|---|
| Objective routing and acceptance | PR #48 (v0.34.4), PR #55 (v0.35.2) | Whether local implementation retains later acceptance and required coordination. Early-map compliance also needs captured write/command ordering; eventual file presence alone is insufficient. |
| Authorization during guidance | PR #56 (v0.35.3) | Whether standing authorization continues, meaningful corrections are saved, unchanged turns avoid needless edits, and explicit no-change instructions pause writes. |
| Evidence precedence and corrections | PR #30, PR #39 (v0.33.1), PR #70 (v0.41.0) | Whether reports remain reports, locally observed checks remain distinguishable, stale values are replaced, and still-valid details remain usable. PR #70 additionally preserves useful failed attempts and records source/date/owner qualifications; older versions may satisfy the outcome through another layout. |
| Delivery and effort ending | PR #48, PR #56, later delivery-resumption guidance | Whether required acceptance remains open and is explained. A story that ends with acceptance still pending cannot prove correct closure after all requirements are satisfied; add that final turn before making an effort-ending claim. |
| Native skill exposure | PR #49 (v0.34.5) allowed repository-read fallback; PR #54 (v0.35.1) removed it; v0.36.0 added consumer Claude skill links | The host must demonstrate that the intended skill catalog is exposed. Missing exposure is a host limitation, not a Wayfinder failure. This Codex screen does not test Claude's skill links or prove native invocation from a route marker. |
| Map structure and instruction load | PR #31 map authoring, later question ledger, PR #40 simplification, v0.37.0 record split, PR #70 status ordering | Whether a reader recovers the objective, blockers, and next work and whether maintained state stays accurate. Static file size is not observed loading, token cost, context pressure, or compaction. |

For context-size hypotheses, these are measured UTF-8 source bytes at the named commits:

| Candidate | Root template | State contract | Separate records contract |
|---|---:|---:|---:|
| v0.33.2 | 6,169 | 28,107 | Absent |
| v0.35.1 | 6,559 | 26,282 | Absent |
| v0.35.3 | 7,942 | 27,953 | Absent |
| v0.37.0, optional | 8,010 | 21,133 | 7,691 |
| v0.41.2 | 8,225 | 22,275 | 9,042 |

The v0.37.0 split reduced the size of the state contract that map-only work needs while placing other instructions behind a conditional read.
It did not remove those instructions from the package.
Record actual reads and native context observations before attributing any behavioral change to load.
The accumulated scenarios add intervening discussion; they do not demonstrate near-limit context pressure or observed compaction.

## Fair comparisons and bounded skill mixing

Use `common-outcome` cases for historical screening: preserve the user's accepted objective, authority boundaries, evidence qualifications, continuing work, and useful fresh-reader state.
Keep current-contract conformance separate; do not require older releases to use today's filenames, exact headings, identifiers, or newly introduced metadata fields.
A claimed historical-contract violation requires reading that revision's own instructions, not projecting the current contract backward.
Start with neutral fixture files, avoiding seeded effort structures that assume one release's layout.

The accepted design boundaries remain relevant to interpretation:

- [ADR-0011](../../architecture-decisions/0011-use-map-first-wayfinder-state.md) makes map-first resumption and preservation of useful coordination architectural; record topology, numbering, exact headings, and mechanics remain contract details.
- [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) separates action authorization from project choice and explicitly retains maintenance authorization across conversational turns.
- [ADR-0027](../../architecture-decisions/0027-use-direct-first-progressive-routing.md) requires progressive loading and re-evaluation while retaining the small always-loaded continuity rules.
- [ADR-0028](../../architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md) keeps one durable coordination model; a benchmark should not reward competing notebooks merely for producing more files.
- [ADR-0010](../../architecture-decisions/0010-separate-framework-output-from-project-owned-state.md) protects project-owned state and treats complete skill directories as the replaceable unit.

After screening, test one named donor skill or a separately specified coherent policy change at a time.
The preparer replaces complete installed skill directories and records base and donor commits plus file hashes.
It rejects obvious missing local dependencies and never silently imports a different contract to repair an invalid treatment.
For example, a current Wayfinder skill on a v0.35.1 base references `effort-state.md` and `effort-records.md`, which that base does not provide; this is an incompatible mixture, not a behavioral failure.
Passing those static checks does not establish semantic compatibility.

The [compatible overlay example](examples/compatible-skill-screen.json) uses current v0.41.2 as base with `implement` from v0.41.1, commit `c05a8ea416b8ac28a6f850fbe8ec9756ea72fe37`.
That donor differs in its fixed typechecking/test cadence versus checks tied to changed behavior, giving a narrow motivated illustration without renaming state contracts.
It addresses verification behavior, not the primary guidance-persistence question, and is not a recommended rollback.

Before recommending adoption or reversion, repeat the promising contrast under matched host settings, preserve failed/inconclusive attempts, and confirm on a held-out story with authority and ordinary-work controls.
An improvement on one case must not erase a current safety or project-data boundary.
Reliable conflicting evidence can justify reopening an accepted decision; an isolated score cannot.

## Why other milestones are deferred

- Early August history includes automatic Wayfinder routing, replacement of the older coordination architecture, and an explicit rollback of unvalidated continuation policy (`f17a11562e67307b6669c044049db11d20dbb686`).
  These bundles change many architectural and host assumptions together; use them only for a deliberate architecture-history question after the nearer comparisons work.
- v0.20.0, v0.24.0, v0.26.0, and v0.30.0 span provider projection, direct distribution, installer simplification, and canonical source layout.
  Those transitions matter to installation fidelity, but round-number sampling would entangle packaging and state-path changes with the current behavioral questions.
  They remain preparer compatibility checks, not default subject candidates.
- v0.32.x, v0.33.0, and v0.33.1 introduce the question ledger, an effort-entry skill, and specialist/evidence handoffs; v0.33.2 already includes them in the initial screen.
  Recover their adjacent boundaries only if the observed difference implicates one of those mechanisms.
- v0.34.x and v0.35.0 contain instruction cleanup, debugging authorization, factual-accuracy guidance, completion handoff, portable routing, and Claude root-policy removal.
  v0.35.1 provides the coherent endpoint for this Codex screen; if native exposure is itself the hypothesis, compare the actual fallback-removal boundary in a separate host-focused study.
- v0.35.2 is reserved for the two targeted adjacent comparisons rather than making every initial story run five ways.
- v0.36.0 is primarily a Claude discovery milestone; v0.38.x–v0.41.1 include terminology, review loops, identifier renumbering, route-marker simplification, map maintenance, and review/check changes.
  Include a narrower boundary only when it explains an observed outcome; route-marker wording is never the behavioral score.

No v0.1.x tag or recorded VERSION was found in the available complete history; the first substantive source snapshot declares 0.3.0.
The current preparer supports the two known later installer layouts and fails explicitly for unsupported layouts.
Neither an unavailable early release nor an incompatible mixture should be assigned a product FAIL.
