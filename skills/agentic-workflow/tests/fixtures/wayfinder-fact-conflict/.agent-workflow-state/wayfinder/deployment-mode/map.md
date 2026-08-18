# Deployment mode

## Destination

Establish which deployment mode is currently true before relying on the
capacity-policy decision.

## Current state

- [F1 — Deployment mode is dedicated](facts/F1-deployment-mode-is-dedicated.md) is currently treated as established.
- [D1 — Use dedicated capacity policy](decisions/D1-use-dedicated-capacity-policy.md) is accepted under the original evidence.

## Blockers and dependencies

D1 depends on F1 remaining current.

## Next work

Compare current `config.txt` with F1 and reconcile any contradiction.

## Notes

Current source and observed behavior outrank this summary.

## Decisions so far

- [D1 — Use dedicated capacity policy](decisions/D1-use-dedicated-capacity-policy.md) — accepted under F1.

## Not yet specified

None.

## Out of scope

Changing the capacity-policy decision without its authority.
