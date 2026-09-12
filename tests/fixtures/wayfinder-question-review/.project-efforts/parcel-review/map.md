# Parcel review

## Objective

Prepare a bounded pilot with an approved exposure and support plan.

## Scope

Coordinate the pilot; implementation and deployment are excluded from this review.
The project owner decides exposure and support preferences.

## Ready work

Inventory existing retry call sites independently of exposure or capacity decisions.

## Current state

The account-scoped retry mechanism is settled in the [pilot plan](../../docs/pilot.md).
The owner can choose pilot exposure now; its support schedule depends on that choice.
The support contact preference is recorded only in the pilot plan, and can be asked now.

## Dependencies

Exposure gates the support schedule choice.
Production sizing needs the publisher capacity result; humans cannot establish it by preference.

## Blockers

Exposure remains uncommitted for support scheduling.
Capacity uncertainty is accepted for the bounded pilot only; production sizing remains blocked.

## Key references

- [Exposure](unknowns.md#u2--which-pilot-exposure-is-approved)
- [Capacity](unknowns.md#u3--what-capacity-does-the-publisher-support)
- [Pilot plan](../../docs/pilot.md)
