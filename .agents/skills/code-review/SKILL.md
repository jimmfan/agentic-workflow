---
description: Review a requested committed range or the actual implementation scope, including attributed pending changes, along independent Standards and Spec axes. Runs parallel sub-agents and reports their findings and coverage separately. Use for branch, PR, fixed-point, or work-in-progress review and implementation handoffs.
name: code-review
---
Two-axis review of the established change scope:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating issue / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

## Process

### 1. Establish the review boundary

Use the supplied review mode, baseline or range, and scope before discovering alternatives.
Preserve the user's chosen comparison semantics; do not silently expand an explicitly committed-only review to pending work.

- **Committed-range / fixed-point review:** resolve and record the requested refs to immutable commits.
  For a standalone fixed point without another requested comparison, use `git diff <fixed-point>...HEAD` (merge-base to HEAD) and `git log <fixed-point>..HEAD --oneline`.
  Respect an explicit endpoint comparison or other range instead.
  Inspect content at the reviewed revision, since working-tree files may differ.
- **Implementation-scope / work-in-progress review:** use the handoff's inputs and attribute changes against pre-edit context.
  Establish the relevant committed delta and pending changes through the actual resulting content.
  Inspect `git --no-optional-locks status --short`, staged changes (`git diff --cached`), unstaged changes (`git diff`), and relevant new files (`git ls-files --others --exclude-standard` plus content reads).
  Include applicable additions, deletions, and renames across these surfaces; a commit diff alone is insufficient.
  Inspect the index version where staged and working-tree content differ, as well as the resulting working-tree content and relevant committed versions.
  Compare with pre-edit observations to exclude unrelated user changes, including unrelated hunks in a file also edited for this task.
  File dirtiness alone does not establish attribution.

Keep one shared review-input set for both reviewers:

- Review mode, resolved baseline/range and relevant commits.
- Governing request or specification, existing project rules that govern this work, acceptance criteria, and references to relevant maintaining artifacts, resolved in steps 2 and 3.
- Pre-edit context when applicable, attributed paths/hunks and versions, and any exclusions or uncertainty.
- Commands or content observations needed to inspect the actual scope.
- The read-only review boundary below and any narrower read limits, independently of the parent implementation's write authorization.

Validate refs and coverage before spawning; an empty commit diff does not imply an empty implementation scope, and a nonempty diff does not establish complete coverage.
If a required baseline, mode, or material attribution cannot be established from supplied inputs and repository evidence, obtain only the missing scope information or explicitly limit the review.
Do not claim complete coverage while required inputs remain missing or attribution remains materially ambiguous.

Review is read-only: do not create, modify, or remove files or directories, including temporary setup or cleanup, or mutate the index or Git history.
Do not stage, commit, stash, reset, clean, or rewrite work to make it reviewable.
Use successful read results despite non-blocking warnings; report a blocked required observation to the coordinator instead of performing a mutating environment repair.
If the reviewed content changes during review, identify the affected evidence gap and review only what became uncovered before claiming completion.

Within the requested review and read boundaries, use governing inputs and ordinary repository references to identify unchanged maintaining artifacts needed to assess an in-scope requirement.
Inspect the relevant content without following unrelated references; an artifact's presence or topical similarity alone creates no update obligation.
For a missing required update, identify the governing requirement, concrete stale claim or missing information, affected artifact and consequence for the reviewed work, even when the artifact is absent from the diff.
Do not infer a defect from omitted detail that is adequately maintained elsewhere or demand a rewrite when the obligation is already satisfied.
Context reads do not expand the requested comparison or authorize edits; explicitly excluded obligations remain coverage limitations rather than in-scope findings.

### 2. Identify the spec source

Use the governing request or specification and acceptance criteria supplied by the user or invoking workflow first.
A sufficiently defined current request needs no separate spec file, tracker lookup, or repeated confirmation.
Only for missing requirements, look for the originating spec in this order:

1. A path or source reference supplied with the review.
2. Issue references in the relevant commit messages (`#123`, `Closes #45`, GitLab `!67`, etc.)
   — if the project has a configured, available issue tracker, fetch them using its documented workflow.
3. A spec file under `docs/` or `specs/` matching the branch name or feature.
4. If nothing is found, ask the user where the spec is.
   If requirements remain unavailable, report the **Spec** coverage gap; the Standards axis may still proceed.

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** in [SMELL-BASELINE.md](SMELL-BASELINE.md) — a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing.
A documented repo standard overrides it, and each smell is a judgement call, never a hard violation.
The Standards reviewer reads that file itself, so do not load it here unless step 4's fallback requires pasting it.

### 4. Spawn both sub-agents in parallel

Give both independent reviewers the shared review-input set from step 1, including the specification contents or usable references from step 2.
When the host starts sub-agents only at the user's request, use an answer the user already gave for this review or implementation scope; otherwise ask once before spawning, and let that answer cover later re-review rounds.
If the user declines, independent review is blocked: report `code-review-blocked` when run alone, or `implement-incomplete` with the review gap when run inside `implement`.
Use existing host controls to restrict reviewers to read-only access when available; inherited write capability does not broaden the supplied review boundary.
Each reviewer must inspect that scope and report actual coverage, not merely echo a supplied diff command or success claim.
When the host lets you choose a sub-agent's model, the Standards reviewer may use a smaller model because it checks the diff against supplied rules; keep the Spec reviewer on a model at least as capable as yours.

**Standards sub-agent prompt** — include:

- The list of standards-source files you found in step 3, **plus the absolute path of `SMELL-BASELINE.md`** in this skill's directory, with an instruction to read it in full before reviewing and to state in its coverage whether it could.
  The reviewer has no other access to the smell baseline: paste the file's full contents instead when you know it cannot read that path, and rerun the Standards axis with the contents pasted if its report says the read failed.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk.
  Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline.
  Skip anything tooling enforces.
  Under 400 words."

**Spec sub-agent prompt** — include:

- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong; (d) changed code that is plainly wrong even where no requirement covers it, such as a crash, a wrong result, or a resource leak.
  Quote the spec line for each finding, or the hunk for (d).
  Under 400 words."

If required Spec inputs are missing, report that axis as incomplete.
If an independent reviewer is unavailable, report the unavailable axis and any separately performed checks honestly; do not substitute a fabricated review execution or PASS.
If a reviewer starts but fails or returns without its report, treat that axis as incomplete rather than passed.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned.
Do **not** merge or rerank findings — the two axes are deliberately separate (see _Why two axes_).
Check each reviewer's actual coverage against the established inputs, including relevant pending and new files.
Report omissions and attribution limitations even if a reviewer claims success; zero findings with missing coverage is not a complete review.
Pass covered scope, findings, and remaining evidence gaps to subsequent acceptance verification so it reuses evidence and adds only missing checks.
When a finding reveals consequential coordination needs, include the governing requirement, affected maintaining reference and consequence in the handoff to the coordinating agent for route reassessment.
The reviewer reports the finding read-only; the coordinator owns route changes and authorized state maintenance.

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any).
Don't pick a single winner across axes — that's the reranking the separation exists to prevent.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
