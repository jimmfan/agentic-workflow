---
description: Implement a defined piece of work.
disable-model-invocation: false
name: implement
---
Implement the work described by the current user request or the accepted project
record designated to maintain the result.

Use `tdd` where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use `code-review` to review the work.

Commit only when the current user request or accepted project policy authorizes
it. Otherwise leave the work uncommitted and report its status.

This skill owns the inner build, test, and Code Review loop. Independent
acceptance verification remains separate.
