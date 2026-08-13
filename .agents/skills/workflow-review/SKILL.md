---
name: workflow-review
description: Independently inspect meaningful completed work for specification conformance, repository standards, correctness, security, maintainability, validation gaps, and unintended scope. Use when a fresh review would materially increase confidence; skip trivial changes.
---

# Independent review workflow

Review asks whether the verified change is the right change and is acceptably
built. Verification remains the owner of executable evidence; a clean review is
not proof that behavior works.

When resuming, validate the active record, reviewed revision or file set, and
exact outstanding finding under `ai-workflow/state/README.md`.

## Fix the review boundary

1. Identify the canonical specification, ticket or acceptance criteria,
   changed-file set or local diff, relevant repository standards, verification
   result, risk areas, and the project-profile authority permitted to accept a
   material review limitation. Include working-tree and untracked changes when
   they are part of the implementation; do not require Git or a remote fetch.
2. Report missing specification, standards, diff, or verification evidence as a
   limitation rather than inventing it.
3. Skip formal independent review when the change is clearly bounded, low-risk,
   and trivial. Perform the proportionate sanity check in the parent task.

## Review independent axes

Examine applicable axes separately:

- specification and acceptance-criteria conformance, including missing behavior
  and unintended scope;
- repository standards and maintainability, distinguishing documented
  violations from judgment calls;
- correctness, edge cases, regression risk, security and privacy implications;
  and
- validation gaps, including evidence that is missing, stale, or insensitive to
  the changed behavior.

A separately installed upstream `/code-review` may be used only when explicitly
selected and its committed fixed-point, Standards, and Spec contract fits. It
does not replace the correctness, security, scope, or validation-gap axes here.

## Preserve independence and control

Use a fresh read-only pass or bounded independent subagents only when isolation
materially improves confidence. Give each reviewer complete bounded scope and
prohibit edits, external actions, approvals, and further delegation. On a host
without suitable independent execution, perform separated parent passes and
report the limitation.

Treat reviewer output as leads. The parent rechecks every material finding
against the cited source, assigns impact, reconciles contradictory reports, and
owns disposition. Reviewers cannot accept scope, edit files, mark tickets
complete, or substitute their judgment for configured checks.

## Close the loop

Return confirmed implementation defects to Implementation and validation gaps
to Verification. After any fix, rerun affected checks and re-review the changed
surface. Record concise dispositions on the `TKT` or `IMP` record when durable
state exists and the review scope permits writes; otherwise report them without
persisting. Do not copy full reviewer transcripts.

Review is complete when every applicable axis was examined, each material
finding cites verified evidence and is fixed or explicitly accepted by the
authority named in the project profile, and any affected Verification evidence
is current. An unresolved material limitation remains blocking; recording it is
not acceptance. Zero findings is not itself the completion criterion.
