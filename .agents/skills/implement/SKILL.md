---
description: Execute a supplied implementation scope with agreed test seams and closing Code Review. This is the inner build method; workflow-implementation owns the outer transition through readiness and independent acceptance verification.
name: implement
---
Implement the defined work supplied by the current user request or invoking workflow.

Before editing, retain the governing request or specification, acceptance criteria, relevant baseline, and intended change scope.
Inspect HEAD, status, staged and unstaged diffs, and relevant untracked files; retain enough pre-edit content to distinguish existing user work from this implementation, including separate hunks in shared files.
Keep this as execution context, not a new required repository artifact.

Use `tdd` where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use `code-review` in implementation-scope mode to review the actual work, including relevant committed, staged, unstaged, and new-file changes.
Pass the governing request or specification, acceptance criteria, baseline, pre-edit context, and attributed change scope, with any exclusions or attribution uncertainty.
The supplied request can define the work without a separate spec file or tracker.
Follow Code Review's coverage and read-only rules; do not commit or otherwise rearrange work merely to make review possible.

Commit only when the current user request or accepted project policy authorizes it.
Otherwise leave the work uncommitted and report its status.
