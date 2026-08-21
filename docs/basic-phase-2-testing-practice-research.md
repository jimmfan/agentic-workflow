# Basic Phase 2 testing-practice research

Date researched: 2026-08-21

## Practical conclusion

Basic Phase 2 should use the repository's existing layered test architecture,
not a new framework or another large model benchmark. Retain the current
acceptance, routing, lifecycle, package, and behavioral contracts; run equivalent
scenarios against the frozen pre-change baseline and the candidate; add mostly
deterministic contract tests for the new invocation configuration; exercise the
install/projection seam in disposable copies; and reserve a few live VS Code
smokes for the host behavior that static tests cannot establish.

The evidence claim should be bounded: **no material regression was detected
across the defined compatibility surface**, with intentional deltas and untested
host behavior identified. Testing can reveal defects and reduce undiscovered
risk, but cannot prove that no defects remain. [ISTQB's current Foundation Level
syllabus, sections 1.3 and 2.2.3](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)
states both that limit and the role of repeated, preferably automated regression
suites after change.

## Principles to apply

### 1. Preserve behavior with retained tests and a frozen comparison

Regression means checking that a change did not unacceptably alter desired
functionality that previously worked. [NIST's regression-testing
definition](https://www.nist.gov/glossary-term/30681) expresses that criterion
directly. Google's engineering guidance recommends adding tests for important
pre-existing behavior before a refactor so the same tests establish that the
behavior is unchanged afterward. [Google Engineering Practices: Small
CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)

For Phase 2, freeze the main and pre-change experimental SHAs, then run the same
retained behavior scenarios against the baseline and candidate wherever both can
support them. Compare route categories, durable effects, preservation outcomes,
and lifecycle results rather than exact prose. Keep an explicit allowed-delta
list for Phase 0/1 behavior and the new Phase 2 invocation. This is a small form
of differential regression testing: Google's larger-test guidance describes
sending equivalent inputs to base and candidate versions, reconciling every
difference as intended or a regression, and using same-version comparisons to
expose noise. [Software Engineering at Google, “A/B Diff Regression
Testing”](https://abseil.io/resources/swe-book/html/ch14.html#ab-diff-regression-testing)

### 2. Assert observable contracts, not incidental implementation

Tests should invoke the public boundary and inspect observable state or output.
Google's unit-testing guidance says public-API tests form explicit contracts and
that state assertions are usually less brittle than assertions about the exact
sequence of internal interactions. [Software Engineering at Google, “Test via
Public APIs”](https://abseil.io/resources/swe-book/html/ch12.html#test-via-public-apis)
ISTQB similarly defines black-box tests from specified behavior independently of
implementation, so they remain useful when implementation changes but required
behavior does not. [ISTQB CTFL 4.0.1, section
4.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)

Applied here, assert outcomes such as “Wayfinder selected,” “routine request did
not select Wayfinder,” “read-only work caused no durable write,” “authority
question surfaced,” and “update preserved project-owned state.” Do not lock tests
to exact model prose, hidden reasoning, tool-call order, helper names, or the
portable router knowing VS Code-specific mechanics. Static host-projection tests
may inspect required frontmatter because that file is itself the public host
configuration contract.

### 3. Keep a pyramid-shaped, deterministic suite

Google recommends the smallest practical test for a behavior and gives a rough,
non-mandatory pyramid of many narrow tests, fewer integration tests, and very few
end-to-end tests. Smaller tests are generally faster and more deterministic;
integration tests cover component interactions that unit tests cannot; full
end-to-end tests are expensive and more exposed to nondeterminism. [Software
Engineering at Google, “Designing a Test
Suite”](https://abseil.io/resources/swe-book/html/ch11.html#designing-a-test-suite)

The Phase 2 shape should be:

- **Majority — deterministic contract/unit:** routing decision tables,
  invocation-control frontmatter, user/model invocability, `agents: []`, canonical
  links, host-neutral portable routing, and precise negative/opt-out behavior.
- **Focused integration:** adopt, update, repeated update, remove, and reinstall
  through the real package/projection seam in temporary consuming-project copies;
  verify durable state and unrelated files byte-for-byte where applicable.
- **Few end-to-end smokes:** only actual VS Code General-to-focused-agent
  invocation, automatic positive selection, representative non-Wayfinder
  selection, state ownership, and authority return behavior that cannot be proven
  statically.

The percentages in Google's example are a heuristic, not a Phase 2 quota. The
important property is that live model runs supplement rather than replace the
deterministic gate.

### 4. Use hermetic, resettable fixtures

Hermetic tests are self-contained, with controlled dependencies, and therefore
improve determinism and isolation. [Software Engineering at Google, “Hermetic
Testing”](https://abseil.io/resources/swe-book/html/ch23.html#hermetic-testing)
Pytest's `tmp_path` similarly supplies a directory unique to each test
invocation. [pytest temporary-directory
documentation](https://docs.pytest.org/en/stable/how-to/tmp_path.html)

The repository already follows this principle with `tempfile.TemporaryDirectory`
and `shutil.copytree`. Continue using immutable source fixtures and a fresh copy
per run. Do not let baseline and candidate share mutable state, depend on test
order, use moving revisions, or contact live services in the deterministic gate.
Live VS Code cases should use fresh chats, clean disposable workspaces, fixed
model/settings where observable, and captured contamination or protocol
deviations.

### 5. Cover distinct input classes and failure behavior

ISTQB's equivalence partitioning requires both valid and invalid partitions, and
boundary-value analysis exercises values at and adjacent to decision boundaries.
[ISTQB CTFL 4.0.1, sections 4.2.1–4.2.2](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)
Google also recommends simulating exceptions and errors rather than waiting for
real failures. [Software Engineering at Google, “Testing for
Failure”](https://abseil.io/resources/swe-book/html/ch11.html#testing-for-failure)

For every consequential Phase 2 rule, include a compact matrix:

- positive: durable coordination automatically invokes focused Wayfinder;
- negative: routine Direct and a clear specialist case stay outside Wayfinder;
- boundary: one meaningful item versus the documented hard/two-soft threshold,
  explicit use, explicit opt-out, and an unrelated existing map;
- failure: missing or malformed projection, unavailable canonical link,
  lifecycle collision, authority-owned decision, and read-only/no-write behavior.

These are behavior partitions, not a demand for exhaustive prompt combinations.

### 6. Make failures immediately actionable

A failure should identify the broken contract from its test name and report the
expected outcome, actual outcome, and relevant context without requiring a
diagnostic rerun. [Google Testing Blog, “Test Failures Should Be
Actionable”](https://testing.googleblog.com/2024/05/test-failures-should-be-actionable.html)
Both Python `unittest` and pytest already support contextual messages and rich
comparison diagnostics. [Python `unittest`
documentation](https://docs.python.org/3/library/unittest.html), [pytest assertion
documentation](https://docs.pytest.org/en/stable/how-to/assert.html)

Prefer one contract per test, stable scenario IDs, narrow assertions, and failure
output that includes the baseline/candidate revision, scenario, expected and
actual route category, relevant path or field, and a focused diff. Avoid a bare
Boolean assertion or a giant snapshot whose unrelated churn hides the cause.

### 7. Demonstrate that important tests can detect the defect

Mutation testing evaluates a suite by injecting behavior-changing faults and
checking that tests fail; a surviving mutant was not detected, subject to the
important caveat that some mutations are behaviorally equivalent. [PIT's official
mutation-testing concepts](https://pitest.org/quickstart/basic_concepts/)

Phase 2 does not need a mutation-testing dependency. For each important new
invocation contract, use an isolated temporary variant: disable model invocation
or force Wayfinder over-selection, run the focused test, confirm it fails for the
intended reason, then discard the variant. Also run new positive invocation tests
against the pre-Phase-2 branch when technically possible. Record the command,
variant, expected failure, and observed diagnostic. A test that passes the
baseline and candidate despite supposedly detecting the new behavior is not
evidence for that behavior.

## Repository fit

This guidance matches the existing convention in
`docs/behavioral-testing.md` and `skills/agentic-workflow/tests/README.md`:
standard-library `unittest`, deterministic contract tests, temporary-copy
lifecycle integration, and opt-in live behavioral smoke tests. Extend those
surfaces and their existing catalogs. Do not add pytest, a mutation framework,
property testing, or another eval harness unless a concrete coverage gap cannot
be addressed simply with the current stack.
