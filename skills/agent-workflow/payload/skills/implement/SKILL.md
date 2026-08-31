---
description: Implement a piece of work based on a spec or set of tickets.
disable-model-invocation: false
name: implement
---
Implement the work described by the user in the spec or tickets.

Use `tdd` where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use `code-review` to review the work.

Commit only when the current user request or accepted project policy authorizes
it. Otherwise leave the work uncommitted and report its status.

This skill owns the inner build, test, and review loop. It does not select the
outer workflow route, create durable coordination state, authorize actions, or
perform Agent Workflow's independent acceptance verification.
