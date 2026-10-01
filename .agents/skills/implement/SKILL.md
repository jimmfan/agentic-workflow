---
description: Build one supplied implementation scope test-first where possible, then close with Code Review. Use when workflow-implementation invokes it or the user names it; otherwise start with workflow-implementation.
name: implement
---
Implement the defined work supplied by the current user request or invoking workflow.

Before editing, retain the governing request or specification, existing project rules that govern this work, acceptance criteria, references to relevant maintaining artifacts, relevant baseline, and intended change scope.
Inspect HEAD, status, staged and unstaged diffs, and relevant untracked files; retain enough pre-edit content to distinguish existing user work from this implementation, including separate hunks in shared files.
Keep this as execution context, not a new required repository artifact.

Use `tdd` where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use `code-review` in implementation-scope mode to review the actual work, including relevant committed, staged, unstaged, and new-file changes.
Pass those governing inputs and maintaining-artifact references along with the baseline, pre-edit context, and attributed change scope, with any exclusions or attribution uncertainty.
The supplied request can define the work without a separate spec file or tracker.
Follow Code Review's coverage and read-only rules; do not commit or otherwise rearrange work merely to make review possible.

Then fix each hard Standards violation and each Spec requirement that Code Review reports as missing, partial, or implemented wrongly; each fix round reruns the tests covering the changed code and runs `code-review` again on only the open findings and the fix's own changes.
After three fix rounds, stop and report any finding still open with the evidence from each attempt.
Report judgement calls such as baseline smells, and observations outside the reviewed scope, without fixing them; leave scope creep in place for a decision by the person, role, or valid delegate with project decision authority.
When evidence shows that a finding does not hold, leave the code unchanged and state the finding and that evidence.

For meaningful work, continue at `workflow-implementation`'s Verify the result step with the result, actual review coverage, findings and remaining evidence gaps.

Commit only when the current user request or accepted project policy authorizes it.
Otherwise leave the work uncommitted and report its status.
