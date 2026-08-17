# ADR-0013: Enable automatic Wayfinder routing

- Status: accepted
- Date: 2026-08-16
- Amends: ADR-0007 and ADR-0011
- Amended by: ADR-0015 and ADR-0016

## Context

Agentic Workflow owns minimum-workflow routing, but the pinned Wayfinder v1.2.3
metadata disables model invocation in both shared `SKILL.md` metadata and Codex
`agents/openai.yaml` metadata. Its discovery descriptions also limit the skill
to a huge effort beyond one session. The framework declaration mirrored the
invocation policy, and its router repeated the same high threshold. Together
these gates made explicit user invocation the only reliable way to run the
provider.

That threshold is later than a careful engineer would normally start structured
notes. Work can become unsafe to hold only in conversational context when
several unknowns, proposed and accepted decisions, dependencies, ownership
boundaries, blockers, assumptions, or conflicting facts must remain distinct,
even if the effort did not begin as huge or multi-session.

## Decision

Permit the router to select Wayfinder implicitly and to escalate into it after
work starts. Use qualitative judgment: Wayfinder is appropriate when structured
durable notes materially reduce the risk of losing or conflating consequential
state. Do not add a numeric score. Keep simple work direct, keep normal bounded
implementation/debugging/discovery in its existing workflow, resume only
relevant maps, honor explicit Wayfinder requests, and honor explicit opt-outs.

Normal authorized project work may create or update the selected workflow's
canonical state without a second notes-specific permission request. Read-only
analysis, audit, diagnosis, review, and `do not change files` requests remain
non-mutating. A new map starts with only useful current state and grows lazily.

Declare Wayfinder `implicit` for Codex and GitHub Copilot and `unavailable` for
Claude Code, which has no native provider projection. Remove Wayfinder's setup
prerequisites because Agentic Workflow's local state contract already configures
the canonical tracker representation.

Adapt the pinned provider during fresh installation and later lifecycle updates
with one narrow invocation/selection overlay. ADR-0015 extends that mechanism
into a fingerprinted local-mode adapter because metadata alone cannot reconcile
the loaded method body. Provider removal remains manual and preserves the
directory.

Agentic Workflow preserves Wayfinder's methodology but permits implicit
invocation because Agentic Workflow owns workflow routing.

## Consequences

Users no longer need to recognize the notebook threshold or remember exact
Wayfinder syntax. Routing can respond when complexity emerges rather than only
to the initial prompt. Explicit invocation still works because an implicitly
invocable skill may also be named directly.

The framework initially diverged from four upstream metadata scalars. ADR-0015
adds one clearly delimited local-mode block while preserving the provider method
below it. Both divergences are reviewable in the provider declaration and
mechanically reapplied after fresh install or update, so they are not one-off
edits to a generated provider directory. A future upstream method or metadata
shape change fails closed for the adapter while leaving the provider and core
framework usable.

GitHub Copilot support follows its current shared `SKILL.md` discovery contract.
Codex support follows `agents/openai.yaml`. No Claude support is claimed, and no
new provider projection is introduced.

## Alternatives considered

- Keep explicit-only invocation: rejected because it makes the user responsible
  for noticing a routing transition that the framework is designed to own.
- Lower only the router wording: rejected because both host metadata files would
  still prevent actual implicit provider execution.
- Edit installed Wayfinder directories manually: rejected because fresh install
  or provider refresh would restore upstream metadata.
- Fork or rewrite Wayfinder: rejected because the desired divergence concerns
  invocation policy and configured local mechanics, not the upstream planning
  method. ADR-0015 preserves that conclusion with a thin inserted adapter.
- Add a generic provider-patching framework: rejected as unnecessary before
  another real provider adaptation demonstrates the need.
