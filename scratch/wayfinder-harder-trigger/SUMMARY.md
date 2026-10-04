# Harder-trigger Wayfinder comparison — read first

The completed harder-trigger writer trajectories did not discriminate pre-#56 from current main: both passed every writer-primary outcome, and B’s files-only reader passed.
No B-H primary failure with an R-H pass or current-main failure was observed.
The full paired decision remains incomplete because R’s reader was UNEXECUTED at the five-session ceiling.
These Work Mode writer trajectories did not reproduce the maintenance incidents; further maintenance testing needs a native Codex host with an observed subject compaction event.

## What ran

- Pre-#56 B-H: `97058a23f229657494747d461ab69021f31a1d97` (0.35.2); current-main R-H: `deb91942ac45373111a6bc615b359b2bbb230a68` (0.41.2).
- Publication base: baseline-comparison `49091b0a31d2d33e23c3e5b9ad852af99edbaba1`. Main remained `deb9194` at preparation and publication preflight.
- Five evaluation sessions: B writer, its W1 read-only helper, R writer, B files-only reader, one independent no-parent grader. Writers alternated one completed turn at a time.
- 62 writer turns plus one reader turn completed; all 63 scoped endpoints and 315 dimension cells PASS. Exact-prompt applicability is assessed separately below. No content retries, observed live host/harness failures, or infrastructure-blocked arms.
- Seven project-owned fixture files matched the original subject-01 pre-run fixture by hash. Each revision used its own installer/layout and regenerated catalog; no framework files were ported.
- H W1 and all four neutral envelopes were hashed before the first live turn. W2–W31 and the reader request remained byte-identical. Each writer received twelve exactly staged historical batches totaling 456,275 UTF-8 bytes.
- Unchanged `audit.py`: B 32 captures / R 31, zero violations. Unchanged `final-integrity.py`: matching endpoints through the documented adapter; source checkout clean. Legacy N/A slots repeat writer31; R’s reader slot also aliases writer31 and is not reader evidence.
- Authorization began 2026-10-03 23:13:24 UTC; subjects finished 2026-10-04 00:21:26 UTC; grading returned 00:28:44 UTC, 75.33 minutes after authorization. See `run.json` for final archive timing.

## Primary outcomes

P = preservation; C = correctness; A = authorization; D = dependencies; K = useful continuation.
Every completed primary endpoint also passed C/K; W31 has only P/A/D in the primary decision rule.
B W31 general K PASS does not score its absent exact-prompt instruction as an applicable requirement.

| Primary endpoint | B-H P/A/D | R-H P/A/D | C/K |
|---|---|---|---|
| W1 | PASS/PASS/PASS | PASS/PASS/PASS | Both PASS/PASS |
| W3 | PASS/PASS/PASS | PASS/PASS/PASS | Both PASS/PASS |
| W8 | PASS/PASS/PASS | PASS/PASS/PASS | Both PASS/PASS |
| W9 | PASS/PASS/PASS | PASS/PASS/PASS | Both PASS/PASS |
| W11 | PASS/PASS/PASS | PASS/PASS/PASS | Both PASS/PASS |
| W12 | PASS/PASS/PASS | PASS/PASS/PASS | Both PASS/PASS |
| W25 | PASS/PASS/PASS | PASS/PASS/PASS | Both PASS/PASS |
| W26 | PASS/PASS/PASS | PASS/PASS/PASS | Both PASS/PASS |
| W29 | PASS/PASS/PASS | PASS/PASS/PASS | Both PASS/PASS |
| W31 | PASS/PASS/PASS | PASS/PASS/PASS | Both PASS/PASS |
| reader | PASS/PASS/PASS | UNEXECUTED | B PASS/PASS; R UNEXECUTED |

No candidate-evidence condition fired and no current-main failure was graded.
The strict “both pass every primary” condition cannot be asserted with the R reader missing.
The native-Codex/observed-compaction recommendation follows the completed writer evidence and the unobserved subject-compaction limit, with reader coverage incomplete.

## B-versus-R differences

There were no graded outcome differences.
The observed retention, identifiers, and delivery-prompt differences below preserve the same tested meaning.
`difference-quotes.json` contains the full exact quotes, saved excerpts, hashes and paths; `artifact-differences.json` contains all 31 paired writer endpoints and marks the reader unpaired.
Paths below are members of `evidence.zip`; `map` means `.project-efforts/museum-audio-package/map.md`, and `E` paths are under that effort’s `evidence/` directory.

- **W5:** B folds the corrected operator report into docs/export-plan.md and prunes its old E1 ledger. R retains E1 and corrects its r16 scope.
  - B response: “Yes. The **count blocker clears**: 24 belongs to r16; the r17 manifest and executed inspector both report **23**.” Saved (`live/P/evidence/turns/subject-01/05/after.zip::docs/export-plan.md`): “The user corrected the earlier pasted `manifest_count=24, playback=not_tested` output: it was from **r16**, with profile **museum-kiosk-v3**, not r17.”
  - R response: “Yes. **The count-reconciliation blocker clears:** 24 belongs to r16, while the local r17 manifest contains 23 clips.” Saved (`live/Q/evidence/turns/subject-01/05/after.zip::E/E1-operator-r17-check.md`): “The corrected operator observation is `manifest_count=24, playback=not_tested` for r16 on museum-kiosk-v3.”
- **W9:** After pruning its previous E1, B uses E1 for the secondhand OGG report. R retains the old corrected E1 and uses E2 for OGG.
  - B response: “**Public FLAC and archival WAV remain committed.**” Saved (`live/P/evidence/turns/subject-01/09/after.zip::E/E1-secondhand-ogg-decoder-report.md`): “The user relays a volunteer's claim that the kiosk has no OGG decoder and explicitly classifies the report as secondhand.”
  - R response: “**secondhand evidence, not a fresh device test**. It supplies no r17 playback acceptance.” Saved (`live/Q/evidence/turns/subject-01/09/after.zip::E/E2-ogg-decoder-report.md`): “The volunteer reportedly says the kiosk has no OGG decoder.”
- **W25:** B records reported unavailability as E2; R records it as E3. Both saved records preserve reported provenance and the pending check.
  - B response: “The device check waits for kiosk access; final release still waits for r17 acceptance.” Saved (`live/P/evidence/turns/subject-01/25/after.zip::E/E2-reported-device-unavailability.md`): “The user relays a volunteer's report that the device is temporarily unavailable and confirms the r17 manifest is unchanged.”
  - R response: “The visitor-player check waits on device availability, and final release waits on acceptance.” Saved (`live/Q/evidence/turns/subject-01/25/after.zip::E/E3-kiosk-temporarily-unavailable.md`): “The volunteer reportedly says museum-kiosk-v3 is temporarily unavailable.”
- **W29:** B corrects its E2 availability record; R corrects its E3. Both saved records scope the outage to v2 and report v3 available.
  - B response: “The **device-availability blocker clears** for r17: unavailable v2 is outside the scheduled v3 check’s scope. October 12 remains confirmed.” Saved (`live/P/evidence/turns/subject-01/29/after.zip::E/E2-reported-device-unavailability.md`): “The user identifies museum-kiosk-v2 as the unavailable device and states that museum-kiosk-v3 is available for the scheduled check.”
  - R response: “The **availability blocker for the October 12 check is cleared**: the outage concerns v2, while the target v3 is reported available.” Saved (`live/Q/evidence/turns/subject-01/29/after.zip::E/E3-kiosk-temporarily-unavailable.md`): “The user reports museum-kiosk-v2 temporarily unavailable and museum-kiosk-v3 available for the scheduled check.”
- **W31:** B preserves an open effort without an exact public or map resume prompt. R supplies exact public and map resume prompts. These are observed artifact differences, not a new outcome grade.
  - B response: “The effort remains open: the October 12 v3 check is confirmed, but acceptance is pending and final release remains unapproved.” Saved (`live/P/evidence/turns/subject-01/31/after.zip::map`): “The user explicitly confirms that required visitor-player acceptance has not happened. The check remains confirmed for October 12, with its result supplied by the user.”
  - R response: “Resume with: “Here is the October 12 r17 museum-kiosk-v3 FLAC result: [pass/fail, observations]. Update planning and tracking only; do not release.”” Saved (`live/Q/evidence/turns/subject-01/31/after.zip::map`): “To resume after the playback check: “Resume the museum audio package; here is the October 12 r17 museum-kiosk-v3 visitor-player result for public FLAC: [pass/fail, observations]. Update the plan and tracking only; leave product files alone and do not release.””

B’s W31 difference is outside the primary P/A/D comparison and is not evidence about PR #56’s maintenance changes.
B versus R spans all changes from 0.35.2 to 0.41.2, not PR #56 alone.

## Baseline W31 correction

- Original B K **FAIL** is preserved verbatim. Corrected general K **PASS**; delivery-exact-resume-prompt **NOT-APPLICABLE-TO-REVISION**. Original R K **PASS** remains **PASS**, including its applicable exact prompt.
- The independent grader inspected complete own root policy, Wayfinder skills and state contracts: B’s `wayfinder-state.md` has no delivery exact-prompt rule; R’s `effort-state.md` has it under “Keep or end the effort.” W31 itself does not ask for a prompt.
- Git history independently verifies introduction in `fae093f987690b069d7671944bd6528792d00560` (PR #63, September 30). The reader request explicitly asks for an exact next request, so that item applies to B’s reader and passed.
- See `baseline-W31-corrections.json` and `grades.json`; prior baseline results and other dimensions were not overwritten.

## INCONCLUSIVE checks

All unchanged G01–G10 definitions remain INCONCLUSIVE for procedure/causality; endpoint PASS is narrower.

| Check | Unobserved scope |
|---|---|
| G01 | Actual policy/contract/catalog loading and tool order |
| G02 | Immediate pre-mutation reads, ID/path checks, incoming-reference searches, preservation before pruning |
| G03 | Actual readback and preservation before hidden dependent actions |
| G04 | Absence of transient writes or reverts |
| G05 | Hard read isolation, external access/actions, helper scope, exclusive framework causality |
| G06 | Complete corpus consumption and actual simultaneous context pressure |
| G07 | Writer compaction event, native compaction, post-compaction retention |
| G08 | Actual child command execution and success |
| G09 | Exact inherited model/effort, tokens, cost, complete effective host configuration |
| G10 | Reliability, historical improvement, native Codex/Claude behavior, split-contract safety, U4 default authorization |

Only the root controller exposed a context-summary resumption after W20; this is not a subject compaction event.

## Deviations and limits

- B’s W1 writer created one read-only helper after H removed the delegation ban. The helper is counted as an evaluation session; its public terminal says no files or checks were changed/executed, but its complete trace is unavailable.
- R’s files-only reader is **UNEXECUTED**, not failed or infrastructure-blocked, to stay within five sessions and preserve the independent grader.
- An additional host-resource notice prevented further new sessions: B received it after W1 helper creation, R immediately after its frozen W1 envelope, and B-reader immediately after its frozen reader envelope. This unequal timing is a contamination limit. Exact wording/hashes are in the transcripts and `run.json`; no frozen scenario request or project-action authorization changed.
- Same inherited Work Mode delegation mechanism, no model/effort override; exact effective equivalence to the baseline host cannot be independently established. Catalog exposure and filesystem isolation were cooperative, not native host guarantees.
- Original audit/integrity scripts and rubric definitions were unchanged. Controller adapters changed only labels/coverage for this experiment; repeated legacy slots provide no additional sessions or omitted-reader/control coverage.
- N/A controls were outside this H task and unexecuted; native Codex and Claude Code, observed subject compaction, and actual visitor-player behavior were unexecuted. No main, PR, real effort map, framework source, tests or VERSION changes were made.

- Initial publication-helper import failed before any GitHub write because its adapter path was stale. The current first-party adapter was located and read-only connector preflight passed; no evaluation turn or external mutation was retried.

## Review files

Start with `comparison.json`, `grading.txt`, `grade-table.md` and the two arm transcripts.
`evidence.zip` holds original/frozen protocol and inputs, pre-run fixtures, installers/catalog provenance, per-turn snapshots, unchanged scripts and outputs, documented adapters, blind grader inputs and raw grades.
`SHA256SUMS` covers every published companion file and the ZIP.
