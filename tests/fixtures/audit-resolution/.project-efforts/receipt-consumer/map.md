# Receipt consumer

## Objective

Prepare and later implement correct Parcel v2 retries.

## Scope

Local retry consumer preparation and implementation; deployment is separate.

## Ready work

Inventory existing request fields; this does not require the publisher answer.

## Current state

The publisher answer has not yet been incorporated.
[Retry contract](../../docs/retry-contract.md) maintains the useful consumer result.

## Areas and relationships

The publisher API owner establishes protocol behavior.
The consumer uses that guarantee; the project owner has authorized local implementation after it is established.

## Dependencies

Consumer implementation requires the scoped key guarantee tracked in [U7](unknowns.md#u7--can-accounts-reuse-a-request-key-and-for-how-long).
Deployment requires the maintenance window tracked in [U8](unknowns.md#u8--when-is-the-maintenance-window).

## Blockers

The unanswered key guarantee blocks consumer implementation.
The unknown maintenance window blocks deployment only.

## Key references

- [Consumer contract](../../docs/retry-contract.md)
- [Project scope](../../README.md)
