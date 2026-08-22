# Wayfinder fresh-agent regression rollback

- Status: current

## Destination

Restore the matched pre-treatment Wayfinder behavior on a branch based exactly
on `origin/main` `153f61d3971a69257e679394444ac34d4cdac426`, preserving every unrelated
current-main change and publishing only `fix/wayfinder-fresh-agent-regression`.

## Territory

- Authored behavior: the package-owned Wayfinder runtime projection and state
  contract are the source surfaces.
- Derived behavior: installed `.agents` and `.agent-workflow` copies must be
  regenerated through the repository's existing adoption/projection mechanism.
- Regression boundary: remove only the exact fresh-agent persistence-admission,
  procedural-history/current-truth treatment isolated by the reviewed B/C patch.
- Preservation boundary: current paths, naming, routing, U/E/F/D, lifecycle,
  locking, authority, ADR conventions, install/update behavior, and later-main
  simplifications remain unchanged.

## Current state

History inspection found that commit `9e4574d` touched 289 files and cannot be
reverted wholesale. Its parent is `18c2cfc`; the frozen evaluation candidate is
`911c248`. The experiment branch's reviewed matched-control patch identifies a
two-surface semantic delta. The five expected current-main treatment/generated
surfaces are byte-identical from `9e4574d`/`911c248` through current `origin/main`,
so no later main commit intentionally changed those same semantics.

The v1 report observed C success/B failure once. The corrected v2 report observed
B 4/4 and C 3/4, with C2 losing the established AMI parameter. Combined
completion tied 4/5 and the experiment classified the refinement Unresolved.

The exact matched-control semantics are now restored in the two authored
sources and regenerated installed projections. The rejected treatment test was
replaced by focused regression coverage. After review-driven refinements, the
focused tests passed 21/21 again, the complete maintainer gate passed 131/131
again, and `git diff --check` passed. Standards has no remaining finding; the
Spec review's only remaining observation was this frontier reconciliation.

## Blockers and dependencies

None. The user's 2026-08-22 request in this task explicitly authorizes a commit
and push only to `fix/wayfinder-fresh-agent-regression`. Projection ownership is
governed by accepted ADR-0023; state/lifecycle, authority, current path, and
preservation constraints remain governed by their existing accepted ADRs.

## Next work

Inspect and commit the final diff, push only the authorized fix branch, verify
the remote ref, and then reconcile this map to completed.

## Notes

- Do not run a live campaign or add a replacement retention policy.
- Do not modify `main` or `experiment/wayfinder-fresh-agent-continuation`.
- The experiment reports remain canonical evidence on the experiment branch;
  this map records only the rollback consequence and branch/base boundary.

## Out of scope

Wayfinder redesign, new memory/context systems, evaluation changes, repository-
level decision documentation, PR creation, merging, and force-pushing.
