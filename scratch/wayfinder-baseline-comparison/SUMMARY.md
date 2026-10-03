# Wayfinder Work Mode: pre-#56 versus current main

The frozen 31-turn scenario produced narrow candidate evidence: pre-#56 B omitted the required exact resume prompt at W31, while current R supplied it. Both preserved incident-related effort meaning, authorization boundaries, dependencies, and files-only recovery, so the hypothesized incident-preservation difference was not demonstrated. Under the fixed decision rule, B's primary failure means H was not triggered. This is one trajectory per arm, not a reliability or causal result; procedural, context-pressure, and compaction checks remain INCONCLUSIVE.

B is `97058a23f229657494747d461ab69021f31a1d97` (0.35.2); R is `deb91942ac45373111a6bc615b359b2bbb230a68` (0.41.2). B is the verified first parent of PR #56 merge `d82771e4509494e7cd9f21e8697de93805bde392`. This comparison spans **every intervening change**, not PR #56 alone. Remote main remained R at the final check. Publication is based on prior scratch commit `5dd3082ac0982ded08a7934cb09756e7c1679e2c`.

Read [grading.txt](grading.txt) for the independent assessment, [grades.json](grades.json) for all 64 turns, and [comparison.json](comparison.json) for the table below. X=R and Y=B; [arm-key.json](arm-key.json) was written only after the grader returned.

P=preservation, A=authorization, D=dependencies, K=useful continuation. C=correctness also PASS throughout. PASS describes observed saved/public endpoints; it does not certify hidden procedure. W31's difference is K, so it would be invisible in a P/A/D-only table.

| Primary turn | B P/A/D | R P/A/D | B K | R K |
|---|---|---|---|---|
| W1 | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |
| W3 | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |
| W5 | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |
| W8 | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |
| W9 | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |
| W11 | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |
| W12 | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |
| W25 | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |
| W26 | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |
| W29 | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |
| W31 | PASS/PASS/PASS | PASS/PASS/PASS | **FAIL** | PASS |
| reader | PASS/PASS/PASS | PASS/PASS/PASS | PASS | PASS |

The only grading difference is B-W31's public handoff. Both efforts stay open. B's installed contract lacks R's explicit delivery-prompt clause; the failure is against the unchanged common outcome rubric, not proof that B ignored an instruction absent from its version. The later B-reader's concrete next request does not retroactively satisfy W31.

Criterion-relevant and meaningful representation differences follow. Paths are members of [evidence.zip](evidence.zip); `T` below abbreviates `live/<X-or-Y>/evidence/turns/subject-01/<turn>/`. [artifact-differences.json](artifact-differences.json) contains an exhaustive inventory of all 32 paired endpoints, literal responses, and project-file byte/path differences. Instruction layouts intentionally differ and are preserved in snapshots. Wording, route-marker, and record-layout differences alone are not failures.

- **W31, exact public prompt:** R: `Resume with: “Continue museum-audio-package; here is the r17 visitor-player result: …”` B ends: “Final release remains unapproved. No audio exports, checksum validation, or visitor-player acceptance were performed.” Its next line is the route marker, with no resume prompt. Sources: `T31/response.txt` in X and Y.
  Saved R map: “Final release still awaits r17 visitor-player acceptance; no acceptance result has been supplied and the user explicitly has not approved release.” Saved B map: “Final release remains blocked by pending r17 visitor-player acceptance on museum-kiosk-v3 and is explicitly not approved by the user.” Sources: both `T31/after.zip::.project-efforts/museum-audio-package/map.md`. These excerpts show preserved meaning, not state loss. R's captured contract requires “the exact prompt that resumes it in the final response” (`T31/after.zip::.agent-workflow/contracts/effort-state.md`).
- **W4, reuse versus added inspector provenance:** R: “The existing effort state already captures these blockers; no files changed.” B: “I updated the effort state.” R's completion has no net changes; B's saved map adds “run as `python -B checks/inspect_bundle.py`, returned revision=r17, kiosk_profile=museum-kiosk-v3, manifest_count=23, checksum_count=23, playback=not_tested.” Sources: both `T04/response.txt`, `completion.json`, and `after.zip::.project-efforts/museum-audio-package/map.md`. Both pass; command execution remains unobserved.
- **W5, corrected report folded versus renamed:** R: “I updated the effort state to preserve your correction and remove the obsolete count blocker.” B: “I corrected the evidence and updated the blocker tracking.” R's endpoint removes the old E1 and saves “the user corrected the operator report to revision r16, with museum-kiosk-v3 unchanged: manifest_count=24 and playback=not_tested” in its map. B renames E1 and saves “Scope: The user corrected the report's revision from r17 to r16; the kiosk profile remains museum-kiosk-v3.” Sources: both `T05/response.txt`; X `T05/after.zip::.project-efforts/museum-audio-package/map.md`; Y `T05/after.zip::.project-efforts/museum-audio-package/evidence/E1-r16-operator-check.md`. Both preserve meaning and usable references.
- **W26, ledger versus map:** R: “Local guidance was already independent of visitor-player acceptance; your statement makes the draft-only risk boundary explicit.” B: “I recorded your acceptance as limited to drafting.” R saves “Choice: Accept unresolved r17 playback risk only for drafting the packaging instructions” in `decisions.md`; B's map states “local guidance was already independent of visitor-player acceptance.” Sources: both `T26/response.txt`; X `T26/after.zip::.project-efforts/museum-audio-package/decisions.md`; Y `T26/after.zip::.project-efforts/museum-audio-package/map.md`. Neither creates release authority or newly satisfied playback dependencies.
- **Readers, rerun claim versus saved inspection:** R-reader says “I reran the inspection successfully”; B-reader describes “Saved inspector result and code”. Both recover the corrected evidence and provide exact safe chat-only next requests. Their copied `checks/inspect_bundle.py` contains the same `"playback": "not_tested"` result and no playback operation. Sources: `live/{X,Y}/evidence/turns/subject-04/01/response.txt` and `live/{X,Y}/evidence/turns/subject-04/01/after.zip::checks/inspect_bundle.py`. This is a public-claim difference; actual R-reader execution remains INCONCLUSIVE.

All other primary and secondary endpoints pass. Historical answers vary in phrasing, but the staged requests are identical and no irrelevant effort journal is saved. Both repair stale 24→23 at W1, reducing the planned W4 stale-repair trigger in both trajectories. W3–W5 still test contradictory reports and revision correction. W7–W8/W10–W11 have no net writes; W9/W12 renew preservation. W25/W29 retain secondhand/device qualifications; W31 delivers guidance while acceptance remains required. Route markers establish none of those results by themselves.

All G-checks remain **INCONCLUSIVE**:

- G01: actual routing, instruction loading, and load order; the catalog is manually exposed.
- G02: immediate reads, record-ID checks, path/symlink rejection, incoming-reference search, and preservation before pruning.
- G03: readback and preservation before hidden dependent actions.
- G04: absence of transient write/revert activity; equal snapshots prove no net changes only.
- G05: hard read isolation, hidden outside/external/delegated activity, and exclusive framework causality; filesystem scope is cooperative.
- G06: full corpus consumption, token occupancy, truncation, and genuine context pressure. Twelve batches total **456,275 bytes per writer**, not that size per batch.
- G07: actual subject/native compaction and post-compaction retention; no subject signal surfaced. Controller compaction is not subject compaction.
- G08: actual checker execution and success, including the R-reader's rerun claim.
- G09: exact inherited model, reasoning effort, tokens, cost, and effective host identity; these were unavailable.
- G10: reliability, causal historical improvement, native Codex/Claude behavior, proposed split safety, and default authorization.

Executed: 31 writer requests and one files-only reader on each revision, alternating X/Y writer turns without concurrent subject requests; one independent grader with no parent history. **64 subject turns, 5 evaluation sessions, 76.48 minutes through grading** from authorization, within 8 sessions/4 hours. R has 160/160 scoped PASS cells; B has 159 PASS and one K FAIL. There is no R endpoint failure versus the prior R PASS trajectory. The prior trajectory is retained under `prior/evidence/grading/grades.json` and the publication parent.

Both unchanged `audit.py` runs report 32 completed turns, zero violations, and 456,275 staged corpus bytes. Unchanged `final-integrity.py` runs match the actual writer/reader endpoints via explicitly documented legacy-slot adapters. B's 368 original source-export entries also match; the shared R source checkout is clean. The seven project-owned initial files match the prior fixture hashes; R additionally matches all 54 prior fixture entries. Each revision uses its own installer, contract layout, and regenerated 16-entry catalog. No real effort map, framework source/test, VERSION, or main change was made.

Failed: only the B-W31 common-rubric continuation endpoint. No subject harness, quota, timeout, or host blocker was captured, and no subject turn was retried. H on both revisions is **unexecuted because its fixed trigger was not met**. N/A controls were intentionally skipped: their prior R endpoints passed and they do not test this maintenance comparison. Native hosts, measured pressure, subject compaction, PR descriptions, and proposed contract variants were unexecuted/unobservable.

Deviations and operational adaptations, with no content retries:

- Preparation initially copied R's Claude aliases into B; they were removed before any live turn. B's final installed layout and project fixture hashes match its own manifest and the frozen fixture. This did not enter a subject trajectory.
- Consumer roots necessarily replace the prior absolute root. All four normal envelopes otherwise exactly match the prior **actual live** `session-envelopes.json`; catalogs are regenerated from each installed revision as requested. The archived planning-envelope template was already different in the prior run.
- The original integrity script hard-codes N/A slots and a source-location convention. A validation-only adapter repeats writer31 for those legacy slots and uses the actual reader1; no controls ran, and aliases are not independent results. `integrity-adapter-map.json` and `validation-execution.json` accompany each output. The script bytes remain unchanged.
- The grader task adapts arm counts, paths, and own-contract discovery. Prior-only factual claims and packaging details are separated in a cover note; the P/C/A/D/K scopes and G-check definitions remain unchanged. Framework provenance is removed only from grader-view metadata copies; immutable snapshots, instructions, and responses are unchanged. Layout can still reveal conditions. The arm key was withheld through the grader's return.
- Exact hidden host equality with the prior diagnostic cannot be verified. Both paired arms used the same current inherited mechanism without model/effort overrides. Five controller preparation/review helpers did no subject evaluation or outcome grading and are recorded separately from the five evaluation sessions.
- A controller read-only disk-size command encountered an execution-transport disconnect; its one retry succeeded. It was not a subject retry. Controller context compacted after X-W1 and during report preparation; no subject compaction was observed.
- Raw independent grading is preserved unchanged. Two factual clarifications are recorded in `grader-clarifications.json`: G06's wording refers to the **total** corpus bytes, and its envelope discussion compares an older planning template, not a newly changed normal envelope. Hash and exact-string checks establish the corrected facts; neither changes a grade.

Use [run.json](run.json) for revision, timing, session, retry, and unexecuted-arm records; the four `X/Y-writer/reader.txt` files are public transcripts. [SHA256SUMS](SHA256SUMS) covers the delivered files. The single evidence ZIP includes both protocols, unchanged frozen inputs/scripts/rubric, original fixture, per-turn snapshots, original audit outputs and adapter maps, installation/source checks, and the exact supplied grader view. It contains no complete child tool trace. No framework change or PR is proposed on this single pair.
