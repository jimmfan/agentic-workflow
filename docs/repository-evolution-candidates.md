# Repository evolution candidates

Status: Exploration

Last reviewed: 2026-08-22

## Purpose

This document preserves candidate improvements for future review. The
dispositions below describe the current next step; they are not accepted
architectural decisions, committed backlog items, or implementation plans.

When a candidate becomes actionable, validate it against current repository
evidence and either create a scoped issue, capture an accepted decision in
`architecture-decisions/`, or remove it if it is no longer relevant.

## Candidates

| Candidate | Current disposition | Why |
| --- | --- | --- |
| **Simplify repository architecture and establish canonical sources of truth** | **Definitely issue-worthy; wait for blind audit before writing the final issue** | This is the largest concern: source/payload/dogfood duplication, `.agent-workflow` versus `skills/agent-workflow/payload`, scattered configuration, nesting, version duplication, and generated versus authored files. YAML is a possible solution, not a separate issue. |
| **Audit installed skills versus actual routing and utilization** | **Create or investigate next** | Codebase Design is installed but largely absent from routing and Wayfinder. Systematically inspect all skills before assuming there are no similar gaps. |
| **Evaluate Codebase Design before increasing automatic use** | **Definitely worth tracking** | Test direct behavior versus vanilla Codebase Design versus a guarded version, then evaluate selective Wayfinder composition. This is a concrete experiment with falsifiable hypotheses. |
| **Rationalize tests and evaluations around current product invariants** | **Definitely issue-worthy** | Old ARC runners, historical reports, ITBench/Harbor artifacts, large lifecycle/state tests, and tests that may freeze obsolete implementation choices deserve an explicit pruning exercise. |
| **Reassess Wayfinder state mechanics for accidental complexity** | **Important; wait for the current feature-by-feature review** | Mutation locking, identifier reuse and retirement, settlement, state-contract size, and facts/evidence lifecycle need review. Some may survive; others may disappear as the architecture simplifies. Avoid duplicating the review already in progress. |
| **General agent plus selective Wayfinder architecture** | **Active work; not a new backlog issue yet** | This decision is already being worked through elsewhere. Finish it first, then capture the resulting architecture instead of tracking each intermediate idea. |
| **Cross-host invocation and portability** | **Real future issue; intentionally deferred** | Codex, Copilot, and Claude Code differ in explicit invocation, hooks, and host contracts. This is valuable work, but it should follow simplification of the core architecture. |

## Review guidance

- Treat each disposition as provisional and re-check it against the current
  codebase before acting.
- Keep proposed solutions separate from the problem statement. For example,
  YAML is one possible response to source-of-truth problems, not a goal by
  itself.
- Avoid creating duplicate issues for work already active elsewhere.
- Promote only settled architectural choices to `architecture-decisions/`.
