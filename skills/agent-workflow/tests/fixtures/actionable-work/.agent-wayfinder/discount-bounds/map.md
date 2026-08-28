# Discount bounds

## Destination

Implement the accepted bounded-discount behavior and verify it.

## Territory

- `pricing.py` owns the bounded calculation.
- `docs/decisions/0001-discount-bounds.md` is the accepted policy.

## Current state

The scope is ready: integer percentages clamp to the inclusive range 0 through
100. No material decision or causal uncertainty remains.

## Blockers and dependencies

None.

## Next work

Implement `bounded_discount` in `pricing.py`, then run `python verify.py`.
