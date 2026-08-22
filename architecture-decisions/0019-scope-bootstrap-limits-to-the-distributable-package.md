# ADR-0019: Scope bootstrap limits to the distributable package

- Status: accepted
- Date: 2026-08-17
- Amends: ADR-0010

## Context

The public bootstrap downloads GitHub's archive for the whole source repository
but extracts only `skills/agent-workflow`. Its single 500-member limit was
checked against every repository entry before package selection. Unrelated
evaluation and documentation growth therefore made normal install and update
fail even though the distributable package remained within its reviewed bounds.

The member limit is still useful against resource exhaustion. Removing it or
raising it whenever the repository grows would weaken that protection or merely
postpone the same failure. A package-only release asset would remove the source
of the coupling, but this pre-1.0 repository has no tagged release or artifact
publishing contract yet.

## Decision

Stream the source archive instead of materializing its complete member list.
Apply the 500-member limit to entries inside `skills/agent-workflow`, which is
the subtree bootstrap processes and extracts. Retain a separate 10,000-member
whole-archive parsing ceiling as an emergency resource-exhaustion bound.

Keep the existing compressed-download, per-file, aggregate-package, path,
duplicate, link, special-file, and mode protections unchanged. Test the package
limit and whole-archive ceiling independently.

This is an explicitly transitional source transport. Reconsider a package-only
immutable release asset when the project establishes a real tagged-release
process; do not keep increasing the whole-archive ceiling as normal repository
growth approaches it.

## Consequences

- Unrelated repository entries no longer consume the package's 500-member
  allowance.
- A genuinely excessive package still fails before package code executes.
- Whole-archive parsing remains bounded without retaining every member in
  memory.
- Bootstrap still downloads the whole repository archive, so bandwidth and
  parsing remain coupled to repository size until a package-only transport is
  adopted.

## Alternatives considered

- Raise the original 500-member limit: rejected because unrelated growth would
  exhaust the replacement value later.
- Remove the whole-archive bound: rejected because compressed download size
  alone does not bound archive parsing work.
- Introduce a package-only GitHub Release asset now: deferred because it would
  add the repository's first tag, release, and publishing policy while leaving
  the existing consumer validation and lifecycle handoff necessary.
- Replace bootstrap with `gh skill`: rejected for this package because GitHub
  CLI rewrites nested `SKILL.md` files and does not preserve the required
  bootstrap, provenance, update, and bounded-resource contracts.
