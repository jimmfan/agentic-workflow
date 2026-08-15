# IMP-0001: Bound discounts

- Type: implementation
- Status: active
- Created: 2026-08-14
- Last reviewed: 2026-08-14
- Review after: none
- Related decisions: docs/decisions/0001-discount-bounds.md
- Provider artifact: none
- Current provider target: none

## Intended outcome

`bounded_discount` clamps integer percentages to the accepted range and the
repository verification passes.

## Scope and non-goals

- In scope: `pricing.py`.
- Non-goals: pricing policy redesign.

## Plan or investigation

Implement the accepted bounds, then run `python verify.py`.

## Risks and reversal

Small local reversible code change.

## Evidence and outcome

Pending.

## Resume target

Implement `bounded_discount` without reopening the accepted decision.

