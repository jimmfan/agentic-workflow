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
- **Implementation-scope / work-in-progress review:** use the handoff's governing request or specification, acceptance criteria, baseline, pre-edit context, and attributed changes.
  Establish the relevant committed delta and pending changes through the actual resulting content.
  Inspect `git --no-optional-locks status --short`, staged changes (`git diff --cached`), unstaged changes (`git diff`), and relevant new files (`git ls-files --others --exclude-standard` plus content reads).
  Include applicable additions, deletions, and renames across these surfaces; a commit diff alone is insufficient.
  Inspect the index version where staged and working-tree content differ, as well as the resulting working-tree content and relevant committed versions.
  Compare with pre-edit observations to exclude unrelated user changes, including unrelated hunks in a file also edited for this task.
  File dirtiness alone does not establish attribution.

Record the included paths/hunks, relevant versions, commands or content observations, and exclusions once for both reviewers.
Validate refs and coverage before spawning; an empty commit diff does not imply an empty implementation scope, and a nonempty diff does not establish complete coverage.
If a required baseline, mode, or material attribution cannot be established from supplied inputs and repository evidence, obtain only the missing scope information or explicitly limit the review.
Do not claim complete coverage while required inputs remain missing or attribution remains materially ambiguous.

Review is read-only: do not modify project files, the index, or Git history, or stage, commit, stash, reset, clean, or rewrite work to make it reviewable.
Run Git observations with `GIT_OPTIONAL_LOCKS=0` to suppress optional index writes.
If the reviewed content changes during review, identify the affected evidence gap and review only what became uncovered before claiming completion.

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

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below — a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing.
Two rules bind it:

- **The repo overrides.**
  A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.**
  Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation — and, like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds.
  → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change.
  → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own.
  → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born).
  → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type.
  → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change.
  → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff.
  → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons.
  → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have.
  → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on.
  → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward.
  → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits.
  → drop the inheritance, use composition.

### 4. Spawn both sub-agents in parallel

Give both independent reviewers the same established inputs: review mode, resolved baseline/range and relevant commits, governing request/specification and acceptance criteria, pre-edit context when applicable, included paths/hunks and versions, exclusions or uncertainty, and commands/content needed to inspect the actual scope.
Each reviewer must inspect that scope and report actual coverage, not merely echo a supplied diff command or success claim.

**Standards sub-agent prompt** — include:

- The established review inputs above.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full — the sub-agent has no other access to it.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk.
  Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline.
  Skip anything tooling enforces.
  Under 400 words."

**Spec sub-agent prompt** — include:

- The same established review inputs, including the supplied request/specification contents or usable references.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong.
  Quote the spec line for each finding.
  Under 400 words."

If required Spec inputs are missing, report that axis as incomplete.
If an independent reviewer is unavailable, report the unavailable axis and any separately performed checks honestly; do not substitute a fabricated review execution or PASS.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned.
Do **not** merge or rerank findings — the two axes are deliberately separate (see _Why two axes_).
Check each reviewer's actual coverage against the established inputs, including relevant pending and new files.
Report omissions and attribution limitations even if a reviewer claims success; zero findings with missing coverage is not a complete review.
Pass covered scope, findings, and remaining evidence gaps to subsequent acceptance verification so it reuses evidence and adds only missing checks.

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any).
Don't pick a single winner across axes — that's the reranking the separation exists to prevent.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
