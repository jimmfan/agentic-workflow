# Basic Phase 2 regression plan

Date frozen: 2026-08-21

## Frozen baseline

- `main`: `b722b0b1eba1bcdf52a818e06279082edbcb978d`
- experimental branch start: `5c031fee090d6ebbbc21005d479335bd7403dd2d`
- package: `0.19.0` on `main`; `0.19.1` at the branch start
- provider: Matt Pocock skills `v1.2.3`, resolved commit
  `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`, declared snapshot SHA-256
  `42d7a91dbb898c92fa81354a0aa4547e33e3adf5136c2e3ea0c5a46e74aafcbc`
  on both revisions
- owned Wayfinder runtime SHA-256: `d9f839aee294799664cbabfe053255dc461e8a8eeb7944f3677014e7cbb308eb`
  on `main`; `3adf5942468cd454df6cc7c18161046e72bc76a06457429b233859c426a3db58`
  at the branch start
- focused VS Code Wayfinder projection: absent on `main`; SHA-256
  `6e76192cccc8399e9ee94cc6bf9a87ca5c3c5229cf0bfd59e45450f58ca949d8`
  at the branch start, where model invocation is disabled

The revisions above are immutable comparison inputs for this work. The source
worktree already contained an uncommitted edit to
`.github/agents/wayfinder.agent.md` that changes its description and enables
model invocation. That edit is pre-existing user work, not part of the frozen
branch-start baseline, and must be preserved while the packaged source and tests
are brought into agreement with it.

## Baseline health

Equivalent source archives were extracted into separate temporary directories.
The eval tests require a Git index, so each disposable archive was initialized
as a fresh local repository and staged before the valid eval run. This changes
only the temporary copies.

| Revision | Command | Result before Phase 2 |
| --- | --- | --- |
| `main` | `python3 skills/agentic-workflow/scripts/verify_package.py --tests` | 115/116 passed; one pre-existing failure because the authored and installed Wayfinder state contracts differ |
| branch start | `python3 skills/agentic-workflow/scripts/verify_package.py --tests` | 138/138 passed |
| `main` | `python3 -m unittest discover -s evals/tests -v` | 78/78 passed |
| branch start | `python3 -m unittest discover -s evals/tests -v` | 78/78 passed |

The first eval attempt in archive-only copies failed because `git ls-files` and
`git check-ignore` had no repository metadata. It is fixture-invalid evidence,
not a product failure; the indexed-copy rerun above is the baseline result.

## Compatibility boundary

### A. Behavior retained from `main`

- Direct is the default for trivial work and unrelated existing Wayfinder state.
- Research, Debugging, Discovery, Implementation, and Verification remain the
  selected methods for their existing intent classes.
- Wayfinder selection retains the accepted hard-signal / two-soft-signal
  threshold; one isolated or routine unknown remains outside Wayfinder.
- Explicit Wayfinder use and explicit opt-out remain authoritative.
- Read-only work creates or updates no Wayfinder state.
- Current canonical evidence outranks stale state.
- Human/project authority questions are surfaced and not fabricated.
- Lifecycle operations preserve project-owned state and unrelated files.
- Provider fallback and native artifact ownership remain unchanged.

### B. Accepted branch deltas before Phase 2

- Phase 0 moves the final route-marker reminder into the VS Code SessionStart
  hook while retaining the detailed portable reporting contract.
- Phase 1 adds the thin, user-selected VS Code Wayfinder projection, its narrow
  map-deletion guard, focused behavioral cases, and the current Wayfinder
  methodology/state refinements.
- Package `0.19.1` and its install map include those Phase 0/1 artifacts.

These deltas are not regressions relative to `main`.

### C. New Basic Phase 2 delta

- The focused VS Code Wayfinder projection becomes explicitly user-invocable
  and model-invocable, while retaining `agents: []` and its current tool set.
- Its description exposes the same durable-coordination selection boundary to
  VS Code. The portable router and canonical Wayfinder methodology do not gain
  VS Code-specific invocation semantics.
- Disabling model invocation in that one projection is the rollback switch.
- Live evidence showed eligibility metadata and description were insufficient
  alone. The corrected host projection also installs one VS Code General-parent
  instruction that delegates only after Wayfinder semantic selection and
  consumes the focused result without substantial duplicate investigation.

## Test seams

The pre-agreed public seams are:

1. installed route categories and repository-state effects;
2. `.github/agents/wayfinder.agent.md` frontmatter, description, capabilities,
   and canonical links;
3. the real adopt/update/remove/reinstall projection into disposable projects;
4. the existing behavioral fixture contracts for state, evidence, authority,
   and unrelated-map boundaries; and
5. a minimal live VS Code smoke for actual parent-to-focused-agent execution.

Tests assert observable categories, metadata, preserved bytes, and artifacts.
They do not require exact model prose, hidden reasoning, or internal tool order.
The testing basis and primary sources are recorded in
[`basic-phase-2-testing-practice-research.md`](basic-phase-2-testing-practice-research.md).

## Deterministic compatibility matrix

| Behavior | Frozen `main` / branch-start contract | Phase 2 expectation | Evidence seam |
| --- | --- | --- | --- |
| trivial request | Direct | compatible | decision contract + unrelated-state fixture |
| external uncertainty | Research | compatible | decision contract + external-fact fixture |
| unexplained failure | Debugging | compatible | decision contract |
| consequential choice | Discovery | compatible | decision contract |
| ready substantial change | Implementation | compatible | decision contract + implementation fixture |
| completed meaningful change | Verification | compatible | decision contract |
| durable coordination | Wayfinder | compatible selection; focused VS Code invocation is the intended Phase 2 delta | decision contract + host projection |
| single/routine unknown | Discovery or Direct, not Wayfinder | compatible | negative decision contract |
| explicit Wayfinder | Wayfinder | compatible; focused agent remains selectable | decision contract + host projection |
| explicit opt-out | no Wayfinder | compatible | decision contract |
| read-only Wayfinder-shaped work | no durable mutation | compatible | decision contract + read-only fixture |
| human authority blocker | question surfaced; no fabricated decision | compatible | authority fixture |
| unrelated map | does not select Wayfinder | compatible | unrelated-state fixture |
| stale state | canonical/current evidence wins | compatible | decision contract + stale-state fixtures |
| lifecycle preservation | state and unrelated work survive | compatible | real lifecycle integration |

The new host-invocation tests must be demonstrated to fail when model invocation
is disabled. The negative-routing assertions must also be demonstrated to fail
when a Direct case is temporarily reclassified as Wayfinder. Temporary variants
must remain outside production files.

## Live boundary

Deterministic tests can establish discoverability, model/user invocation policy,
subagent prohibition, canonical links, and package reconciliation. They cannot
prove that a live VS Code General agent semantically chooses and executes the
focused agent. That final behavior remains a small manual, fresh-chat smoke gate
with exact prompts and observable execution evidence.
