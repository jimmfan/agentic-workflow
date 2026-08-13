# Architecture and ownership

## Purpose

The framework adds durable engineering workflow policy while preserving the
host agent's native execution model. Codex remains the primary runtime and owns
normal repository work, sandboxing, approvals, tools, native subagents, edits,
and verification. The expected result is consistent routing and resumption
without a mandatory orchestrator, duplicated policy tree, or optional-runtime
dependency.

## Request and execution path

```text
request
  -> root AGENTS.md policy
      -> explicit learning / blocking knowledge gap -> Teach
      -> consequential unresolved choice -> Discovery
           -> blocking knowledge gap -> Teach -> resume Discovery
      -> unexplained existing failure -> Debugging -> Verification -> Review when meaningful
      -> substantial multi-session approved spec -> Decomposition -> frontier ticket
      -> meaningful specified scope/frontier -> Implementation -> Verification -> Review
      -> clear bounded low risk -> direct handling
  -> execution choice
      -> parent Codex (default)
      -> native Codex subagent (bounded independent engineering work)
      -> optional Hermes research (substantial separable external investigation)
           -> structured result -> parent Codex verification and synthesis
      -> Copilot portable subset (same core workflow policy, host-native execution)
```

Workflow routing and execution choice are separate decisions. Complexity, file
count, or available parallelism does not by itself justify Hermes. The parent
Codex task owns synthesis, accepted decisions, repository changes,
review-finding disposition, and final verification regardless of which bounded
helper gathers evidence.

## Loading model

| Content | Loading | Purpose |
|---|---|---|
| Root `AGENTS.md` | Always | Compact precedence, safety, runtime-selection, state, and learning-promotion rules shared by Codex and Copilot |
| Skill `name` and `description` under `.agents/skills` | Discovered metadata | Match or explicitly select a focused procedure |
| Selected skill body | Conditional or explicit | Discovery, Teach, Decomposition, Implementation, Debugging, Verification, Review, or optional Hermes delegation details |
| Project profile and active record | Conditional file read | Verified project facts, configured commands, decisions, and exact resumption |
| Contracts, templates, archived records, examples, integration docs | Explicit only | Creation, history, adoption, maintenance, and optional-runtime setup |

This is one canonical skill tree. Codex discovers `.agents/skills` natively, and
current VS Code Copilot supports the same project location. The framework does
not create parallel `.github/copilot-instructions.md` or `.github/skills` copies.
Experimental forked skill contexts, custom agents, prompt files, MCP, and Codex
app-server are not core dependencies.

## General core and project layer

Framework-owned core includes root policy, eight skill directories, contracts,
templates, the installed workflow guide, optional Hermes adapter assets, and the
framework version. It knows how to route, persist, decompose, plan, diagnose,
verify, review, and fail optional delegation safely, but names no project language, cloud,
deployment, or test tool.

Project-owned files include `project-profile.md`, `state/active.md`, active and
archived records, preserved pre-install `AGENTS.md` content, and application
code. Durable specifications stay in the project's normal documentation path and
are linked from state instead of copied. Local tickets are project-owned state;
when a native tracker is selected, its issue bodies remain canonical and local
state stores only references and frontier status. The profile supplies technology,
architecture, paths, terminology,
policies, delivery and diagnostic layers, decision considerations, and complete
command definitions. The contrasting fixtures under `examples/` demonstrate
specialization without changing shared policy or skills.

## State and truth model

`active.md` is the sole small index. Typed records hold rationale and accepted
evidence. Discovery writes its pending decision before Teach interrupts it;
Teach restores the exact resume target after sufficient understanding. Invalid,
stale, missing, or conflicting state fails visibly and remains recoverable.
Completed history is archived and periodically compacted without reusing IDs.

For substantial approved work, an `IMP` coordinator links the canonical ticket
set and actionable frontier. Local `TKT` records or explicitly selected native
issues own ticket bodies. Stable blocker edges must be acyclic; implementation
can start only from ready tickets whose blockers are complete. Work that fits
one coherent session bypasses decomposition.

When sources disagree, use this precedence unless a narrower accepted project
rule says otherwise:

1. accepted repository decision or durable state;
2. the validated active workflow artifact;
3. Codex or Hermes memory as a non-authoritative signal; and
4. chat recollection.

A delegated transcript is not state. Persist only a concise, independently
checked result when it materially helps future work.

An optional `IDP-NNNN` record may capture meaningful recurring manual or
cross-team friction with plausible reusable platform value. It is supplemental,
never an active workflow, and must not interrupt routine engineering.

## Command and authorization model

Project-profile command entries combine purpose, action or manual check,
execution location, prerequisites, environment names, scope, safety class,
approval, expected success, unavailable behavior, and reversal. Unknown safety
or scope does not run. Safe repository-local checks may run automatically only
when not marked approval-required; every explicit approval requirement,
external-scope action, external mutation, and destructive action requires
specific authorization.

The repository is a trust boundary: a command entry is executable content and
must be reviewed rather than treated as inert configuration. The framework does
not weaken Codex's sandbox or approval policy.

## Native subagent boundary

Use one capable parent by default. A native Codex subagent is appropriate for a
bounded independent analysis or review when isolation or parallelism materially
helps. Children inherit the active sandbox and approval context. Keep tightly
coupled editing in the parent, avoid concurrent write-heavy work, and treat a
child result as evidence for the parent rather than an accepted decision.

## Optional Hermes boundary

Hermes is disabled by default and cannot become a required hop. The only enabled
capability for the pinned v0.20.0 release is `research`: authorized external/web
investigation through the exact `openai-codex` provider and dedicated private
profile. It starts outside the repository, receives no repository tools, and
uses isolated process, Hermes, Codex, and temporary homes before returning to
the parent. `repo-read` is represented as a compatibility level but
fails closed because the audited app-server integration cannot enforce and
isolate Codex `:read-only` end to end. Write-capable Hermes repository delegation
is outside the MVP.

The handoff request is a bounded JSON contract containing the objective,
delegation reason, scope, curated context, known facts, constraints, prohibited
actions, authorization flags, expected output, state references, and evidence
requirements. Repository modification and external writes are always false.

The result contract separates status, conclusions, evidence, source URLs,
assumptions, tools used, repository files inspected, unresolved uncertainty,
recommendations, actions, prohibited-action confirmation, and items the parent
must verify. A missing, invalid, incompatible, mutated, recursive, or incomplete
result is not silently promoted to success. Parent Codex checks material claims,
reconciles them with repository truth, and decides whether any concise result is
worth persisting.

Recursion is prohibited. The adapter refuses to start when
`AI_ENGINEERING_WORKFLOW_CHAIN` is already present, sets it to `codex>hermes` for
the child, and instructs the child not to invoke Codex or another delegate. This
prevents Codex -> Hermes -> Codex loops; it is not a general process sandbox.

## Private learning and controlled promotion

Hermes may retain useful memory, learned-skill proposals, curator changes, and
other self-improvement artifacts in its dedicated profile. Learned skill writes
are approval-gated where supported, and no repository skill directory is exposed
as an external Hermes skill directory. Automatic or approved private learning is
never repository truth.

Promotion into root `AGENTS.md`, `.agents/skills`, a project profile, a decision,
or durable state is a distinct Codex-owned change. It requires reusable evidence,
a duplication and staleness check, placement at the narrowest appropriate scope,
a reviewable diff, and normal verification. Raw transcripts, credentials, and
unnecessary personal data are never promotion inputs.

## Copilot portability boundary

Current VS Code Copilot recognizes root `AGENTS.md` and `.agents/skills`, so the
seven core workflows, project profile, state contract, and safety rules can be
used without a second copy. Copilot supplies its own agent loop and tool controls;
the framework does not claim Codex sandbox equivalence, native Codex subagents,
or Codex-parent Hermes delegation there. Runtime discovery and semantic routing
still require a signed-in live Copilot check.

The shared Hermes skill may be visible in Copilot discovery, but its contract
refuses execution outside a Codex parent. Copilot continues with host-native
capabilities; visibility is not support for that adapter path.

## Distribution model

The source manifest separates framework-owned files from one-time project seeds.
Installation records SHA-256 checksums, provenance (`created`,
`preexisting-identical`, or `composite`), framework version, clean or explicitly
dirty/local Git revision status, and UTC installation time. Existing project
instructions remain outside a marked managed block in root `AGENTS.md`.

Update preflights targets, rolls back ordinary write failures, refuses
downgrades and managed conflicts, seeds new project files only when absent, and
preserves ownership transitions. Removal authenticates ownership against the
exact source version, deletes only unchanged files created by the framework, and
restores or preserves prior and project-owned content. No registry or service is
needed. Adoption installs inert Hermes adapter assets but never installs,
authenticates, configures, starts, updates, or removes the host Hermes runtime.
