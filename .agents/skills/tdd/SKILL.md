---
description: Build features or fix bugs test-first through a red-to-green loop at agreed seams. Use for test-first work; integration tests alone do not imply TDD. Refactoring belongs to the later review stage.
name: tdd
---
# Test-Driven Development

TDD is the red → green loop.
Apply these test-quality, seam, and loop rules before and during each cycle.

When exploring the codebase, read `CONTEXT.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

## What a good test is

Identify the module under test and verify behavior through its caller-facing interface, not its private implementation.
That interface may be internal to the application; public here means available to the module's callers, not necessarily an end-user or platform API.
Name the behavior being specified, such as "user can checkout with valid cart"; tests should survive refactors that preserve that behavior.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Seams — where tests go

A **seam** is where you exercise the module's caller-facing interface and observe behavior without reaching inside.

**Test only at pre-agreed seams.**
Reuse seam agreement from the current request, accepted artifacts, or invoking workflow and identify those seams before writing tests.
Ask which caller-facing behavior and seams need coverage only when material agreement is missing.
A needed new or changed seam requires agreement unless choosing it is already delegated by the user or accepted project policy.
Focus coverage on critical paths and complex logic rather than every edge case.

When the shape of that interface is itself in question — how deep the module is, where the seam belongs, what the interface should expose — use the `/codebase-design` skill for the vocabulary.
It is the shared source of the module, interface, depth, seam, adapter, leverage and locality terms, and it is a reference to consult, not a session to run.

## Anti-patterns

- **Implementation-coupled** — mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface).
  The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological** — the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code.
  Expected values must come from an independent source of truth — a known-good literal, a worked example, the spec.
- **Horizontal slicing** — writing all tests before implementation commits to imagined behavior and test structure before learning from execution.
  Use the one-slice loop below so each test responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.**
  Write the failing test first, then only enough code to pass it.
  Don't anticipate future tests or add speculative features.
- **One slice at a time.**
  One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.**
  It belongs to the review stage (see the `code-review` skill), not the red → green implementation cycle.
