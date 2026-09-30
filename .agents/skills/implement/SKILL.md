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

Then resolve the review findings.
Fix each hard Standards violation and each Spec requirement that Code Review reports as missing, partial, or implemented wrongly.
A defect that Verification returns is a finding under these rules.
A fix round fixes the open findings, reruns the tests that cover the changed code, and runs `code-review` again with only the open findings and the fix's own changes as its scope.
A finding stays open until the specific defect no longer exists; an attempted fix does not close it.
After three fix rounds leave a finding open, stop fixing it and report it with the evidence from each attempt.

List baseline smells and other judgement calls, and observations outside the reviewed scope, in the handoff without fixing them.
Leave behavior that Code Review identifies as unrequested in place and report it for a decision by the person, role, or valid delegate with project decision authority over the accepted scope.
When evidence shows that a finding does not hold, leave the code unchanged and state the finding and that evidence in the final response.

When the current user request or accepted project policy turns on a findings log, append one entry per fix round to the file it names.
Each entry names the date, scope, and round, then lists findings under Fixed, Open, Judged not to hold, Not fixed, and Needs decision.
If no file is named, give the same entries in the final response.
The log is a record only; it never replaces this reporting and is never used to resume work.

For meaningful work, continue at `workflow-implementation`'s Verify the result step with the result, actual review coverage, findings and remaining evidence gaps.

Commit only when the current user request or accepted project policy authorizes it.
Otherwise leave the work uncommitted and report its status.
