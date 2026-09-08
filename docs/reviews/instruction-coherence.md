# Instruction-coherence review

This review covers the cleanup after `2614824b1e4ffda7c26cb2ea60e2c85f57c67aee` on `fix/implementation-review-handoff`.
It is review evidence, not a runtime contract or a new workflow.
The preceding implementation-review handoff and persistence-map reconciliation remain part of the branch.

## Classification and obligation preservation

The state-contract changes, consolidation in the Wayfinder skill and routing, explanatory routing edits, and Research's duplicate chat-output deletion preserve intended behavior.
The concrete skill corrections and their selection/support-file alignment, including Prototype selection in Wayfinder and routing, intentionally change instructions as requested.
Root policy and its template remain unchanged: their authority and selection rules must apply before optional files load.
Terminology remains unchanged and owns meanings rather than procedures.
Accepted ADRs 0010, 0011, 0025, 0027, 0028, and 0029 continue to govern these boundaries.
No new external fact or methodological ambiguity required research.

In the table, **contract** means [Wayfinder state](../../.agent-workflow/contracts/wayfinder-state.md), **skill** means [Wayfinder](../../.agents/skills/wayfinder/SKILL.md), **routing** means [detailed routing](../../.agent-workflow/routing.md), and **root** means the [distributed root policy](../../agent_workflow/install/AGENTS.md.template).

| Old obligation and repeated locations | Surviving location | When the affected path loads it |
|---|---|---|
| Choice/evidence gate, delegated judgment, action authorization, truthfulness, and responsibility distinct from authority: root, contract Current knowledge, skill Operating rules and transitions | Root retains the complete cross-cutting rules; contract Current knowledge retains how authority and source evidence are represented | Root applies before Direct work, selection, or optional loading; selected Wayfinder loads the whole contract before state work |
| Hard/soft selection thresholds, explicit selection/opt-out, and existing state alone insufficient: root, skill opening, explanatory docs | Root When to use Wayfinder; skill and docs provide short orientation and references | Before Wayfinder selection; no mandatory contract load for Direct work |
| Bounded candidate inspection, semantic objective/scope match, safe regular map and mapless exclusion: routing and contract | Routing Re-evaluate and resume retains the preselection check; contract retains full selected-effort path rules | Routing during the bounded check before selection; contract after selection |
| Sufficient identity before creation, unresolved detail allowed, no invented objective, scope refinement keeps effort/path, ambiguity and collisions: contract Effort shape and skill Operating rules | Contract Effort shape and selection; skill establishes objective/scope as orientation | Contract before effort recognition, creation, or resumption |
| Map-only validity, optional records, independent retention value, no category/pipeline ceremony: contract State model and Current knowledge, several skill sections | Contract State model owns paths; Current knowledge owns selective retention; skill calls that rule | Whole contract before state work, including before choosing records |
| Stronger U# test, precision alone insufficient, external participants/authority and cross-area gates as examples, no temporary record ceremony: skill transitions plus contract | Contract Current knowledge; skill retains asking the substantive project question when project knowledge is needed | Before U# creation/retention; skill during question finding |
| Areas before substantial decomposition; precise questions versus Not yet specified; reconsideration after evidence; no speculative dependencies/tickets | Skill Establish areas and relationships, Chart the visible route | Selected skill before applying its method |
| Domain Modeling's bounded role; minimum specialist; appropriate source, human, or experimental evidence | Skill areas and method selection; routing Decide and compose | At method selection, with selected specialist instructions read before use |
| Blocker/dependency/readiness meanings repeated in terminology, contract and skill | Terminology owns meanings; contract Dependencies and readiness owns representation and scoped effects; skill owns evidence-supported ordering and transitions | Root loads terminology when meanings materially matter; contract before map work; skill before transition |
| Default map order, visible honest assessments, alternate-layout validity, responsibility within Areas and optional Ownership | Contract Map authoring and Responsibilities in the map | Before authoring or reconciliation; never a preselection schema |
| Established assignments directly maintained or summarized with usable source links; no inferred authority or invented ownership blocker | Contract Responsibilities in the map; skill establishes consequential responsibilities during orientation | Contract before representation; skill before decomposition |
| Map versus durable ticket responsibility repeated in contract, skill and docs | Contract Map authoring; routing Preserve responsibilities and transitions owns cross-workflow artifact responsibility; skill references the contract | Contract before Wayfinder representation; routing when handoff/responsibility materially matters |
| Common reconciliation prerequisites repeated across record/prune/end instructions | Contract Reconciliation and pruning declares the shared sequence for all operations | Before each affected authorized state operation; operation sections retain local reminders |
| New/corrected/still-valid details, identity/status/source/scope relationships, and usable maintaining references | Contract Reconcile affected state, common sequence steps 1–2 | During preservation and reconciliation, before pruning or claiming completion |
| Current-state check immediately before mutation; retrievable results verified before pruning; saved-result readback before completion | Three distinct checks in contract Reconcile affected state; skill handoff names their distinction | At those three different times; one check cannot substitute for another |
| Scoped acceptance leaves question unresolved and grants no broader choice, authorization, dependency satisfaction, invented restriction, or unrelated readiness | Root cross-cutting limit; contract Scoped uncertainty acceptance owns the unresolved record and authority/boundary representation; record-specific action references it | Root before action; contract before acceptance is recorded or U# is considered for pruning |
| IDs, anchors, same-type rereads, conditional append, scoped malformed-container handling, and no-overwrite | Contract Identifiers and references | Immediately before affected allocation, creation, or rename |
| F/D correction in place, answered U pruning, unresolved accepted U retained, independently useful E, changed D gate | Contract Apply record-specific changes under the common sequence | At the corresponding record operation |
| Recognized paths and unrecognized bytes; exact file/section pruning; no recursive deletion; preserved continuation and map-last ending | Contract State model, Prune one record, Keep or end the effort | Recognition before state work; destructive-operation reminders at pruning/ending |
| Research repeats chat delivery twice in the same numbered item | Research item 2 retains concise cited findings for chat | Whenever the Research body loads |

Useful reminders remain at creation/allocation, scoped acceptance, pruning, and ending.
The root/template synchronization and preselection candidate check are deliberately retained; moving either into the optional contract would lose an earlier loading boundary.
Useful source-linked summaries remain valid.
The complete default-map authoring block and consequential responsibility rules remain in the contract rather than being copied into the skill.

## Intentional corrections

- Implementation descriptions identify inner build versus outer orchestration; explicit invocation, Direct-first behavior, verification transitions, and the fixed handoff bodies remain intact.
- `to-spec` reuses supported scope/testing decisions without interviewing, inventing approval, or multiplying unsupported stories.
- TDD reuses agreed or delegated seams, asks only for missing material agreement, identifies the module's caller-facing surface, and retains the existing red-to-green method.
- Grilling keeps thorough requested exploration and dependency rounds, while reusing settled, policy-determined, and delegated choices.
- Codebase Design preserves distinct project/platform vocabulary and application-internal caller interfaces; Deepening checks retained behavior and failure coverage before test deletion.
- Tickets cross applicable layers, record genuine external prerequisites separately from ticket edges, and confer no execution authority.
  Safe bounded atomic changes are allowed; expand–contract remains for compatibility or independently transitioning callers.
- Prototype selection matches interactive logic/UI methods, isolates mutations, and separates authorized production adoption and verification from commit/publication authorization.
- Research and factual lookup can be synchronous with the same evidence requirements.
  Required independent/parallel work remains required, including Code Review and Design-It-Twice; unavailable capability is reported honestly.

No historical fixture, frozen campaign artifact, reconciled map, canonical term, VERSION, inventory, or lifecycle behavior is intentionally changed.
No initializer, parser, schema, migration, registry, automatic normalization, or runtime subsystem is added.

## Size comparison

Counts use whitespace-delimited words in the complete files, including frontmatter and examples, comparing `2614824` with the reviewed result.
The root template is counted once as the distributed root policy, excluding source-checkout maintenance instructions in AGENTS.md.
These are file-size observations, not token counts or inferred runtime savings.

| Runtime file | Before | After |
|---|---:|---:|
| `.agent-workflow/contracts/wayfinder-state.md` | 4,136 | 3,797 |
| `.agent-workflow/routing.md` | 1,367 | 1,340 |
| `.agent-workflow/terminology.md` | 480 | 480 |
| `.agents/skills/code-review/SKILL.md` | 1,477 | 1,477 |
| `.agents/skills/codebase-design/DEEPENING.md` | 388 | 425 |
| `.agents/skills/codebase-design/DESIGN-IT-TWICE.md` | 402 | 438 |
| `.agents/skills/codebase-design/SKILL.md` | 865 | 894 |
| `.agents/skills/grilling/SKILL.md` | 317 | 377 |
| `.agents/skills/implement/SKILL.md` | 199 | 223 |
| `.agents/skills/prototype/LOGIC.md` | 1,045 | 1,013 |
| `.agents/skills/prototype/SKILL.md` | 495 | 552 |
| `.agents/skills/prototype/UI.md` | 1,136 | 1,162 |
| `.agents/skills/research/SKILL.md` | 227 | 262 |
| `.agents/skills/tdd/SKILL.md` | 567 | 639 |
| `.agents/skills/tdd/mocking.md` | 202 | 258 |
| `.agents/skills/tdd/tests.md` | 291 | 326 |
| `.agents/skills/to-spec/SKILL.md` | 487 | 539 |
| `.agents/skills/to-tickets/SKILL.md` | 859 | 948 |
| `.agents/skills/wayfinder/SKILL.md` | 2,144 | 1,123 |
| `.agents/skills/workflow-implementation/SKILL.md` | 378 | 390 |
| `agent_workflow/install/AGENTS.md.template` | 875 | 875 |
| **Combined measured files** | **18,337** | **17,538** |

## Verification and independent review

The added controls submit explicit candidate outcomes to the existing scenario evaluator.
They cover accepted/missing agreement, bounded synthesis, vocabulary and failure coverage, real versus invented prerequisites, prototype scope, and honest capability fallback.
They do not execute the skills or prove that rewritten instructions cause those outcomes.
Existing handoff Git/evaluator controls and Wayfinder controls remain separate evidence.

All current locked gates in [the verification guide](../verification.md#maintainer-and-ci-gate) passed locally with uv on macOS and Python 3.14.6.
The task used `UV_CACHE_DIR=/private/tmp/agent-workflow-instruction-coherence-uv-cache` because the default cache was outside the writable sandbox; no global configuration changed.

| Check | Result and evidence boundary |
|---|---|
| `uv run --locked ruff format --check .` | PASS; 198 Python files already formatted |
| `uv run --locked ruff check .` | PASS |
| `uv run --locked python agent_workflow/verify_package.py --tests` | PASS; 171 deterministic tests on the final runtime instructions |
| `uv run --locked python -m unittest discover -s evals/tests -p 'test_*.py' -v` | PASS; 65 evaluation-tooling unit tests |
| `uv run --locked python tests/wheel_smoke.py` | PASS; current-source sdist/wheel build, isolated CLI lifecycle exercise, and two smoke controls |
| `git diff --check` | PASS |

Focused checks also passed: 11 new instruction-coherence evaluator controls, nine retained review-handoff controls, and three retained map-authoring controls.
These are included in the 171-test package gate, not additional independent executions of the skills.
Ten changed skill entrypoints passed the skill author's metadata validator.
The package verifier checked derived-skill attribution, support-file closure, local links, distribution mapping, and root/template synchronization.
No intentional mapping change required a manifest refresh.

An intermediate package run failed three existing structure assertions after explicit map/record path references were removed during consolidation.
Restoring the applicable path references corrected the source; the tests were unchanged.
Focused checks and the full package gate then passed, including the final ticket-ownership correction.

Both independent reviewers received the same implementation-scope handoff against immutable baseline `2614824b1e4ffda7c26cb2ea60e2c85f57c67aee`.
They inspected all 23 included paths: 21 tracked pending modifications and both complete new files, including this report and the new controls.
Their coverage included the full resulting instructions and support files, changed baseline hunks, the obligation table, loading paths, governing root policy/template, terminology, and accepted ADRs.
No attribution exclusion or missing scope was reported.
A before/after check confirmed that review left all 282 tracked or relevant untracked files, HEAD, and the raw index unchanged.

### Standards

The initial independent Standards review reported zero documented-standard violations and zero actionable smell-baseline findings.
It independently reproduced the runtime counts and confirmed protected policy, metadata, maps, and historical fixtures had no pending delta.
Focused reinspection of the corrected ticket paragraph and complete updated report confirmed zero remaining Standards findings.

### Spec

The initial independent Spec review reported one P2 preservation finding: replacing “Once a durable ticket or ticket set exists” with “Once `to-tickets` creates” narrowed the rule for tickets created elsewhere.
The final contract restores the existence-based condition while retaining the consolidated ticket/map responsibility statement.
Focused independent reinspection confirmed that the correction preserves the original obligation and that the complete updated report accurately describes coverage and evidence limits.
Spec has zero remaining findings; its original P2 finding is resolved.
Both follow-up reviews were confirmed read-only against the same 282-file, HEAD, and raw-index snapshot.

### Acceptance and limitations

| Required boundary | Outcome and basis |
|---|---|
| Consolidation retains obligations and loading paths | PASS on full authored-contract review and focused reinspection; the table records surviving owners and action-time reminders |
| Concrete skill corrections and supporting instructions | PASS on full-content review and bounded positive/negative evaluator controls; no general live compliance claim |
| Prior review handoff remains intact | PASS; Code Review and both implementation bodies are unchanged, and nine Git/evaluator controls pass |
| Wayfinder representation, preservation, and authority | PASS on retained deterministic controls and full-contract review; root thresholds, terminology, default authoring, alternate-layout rules, IDs, timed checks, and map-last ending remain |
| Protected source and durable state | PASS; root/template, terminology, attribution, manifest, VERSION, reconciled maps, historical fixtures, and frozen evaluation evidence remain unchanged |
| Current required local gates | PASS as listed above; no hosted CI or additional platform execution claimed |
| Commits, non-force push, and branch availability | Delivery evidence is recorded in the final task response after these source checks |

The reviewers did not rerun suites or observe live skill execution; command results above are implementation evidence supplied to them.
Authored-contract review, deterministic candidate grading, disposable Git/file operations, and local package/CLI execution are separate evidence.
Deterministic success does not establish general behavioral equivalence or satisfy an unrelated missing required check.

No separate live campaign or persistence/map-authoring rerun is part of this cleanup.
Prior Create/Correct/Read/Resume and persistence comparative-benefit conclusions remain INCONCLUSIVE; previously recorded stage-specific outcomes are unchanged.
Infrastructure failures are not product PASS or FAIL.
