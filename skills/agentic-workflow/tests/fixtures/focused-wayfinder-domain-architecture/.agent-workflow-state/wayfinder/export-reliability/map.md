# Export reliability

- Status: current

## Destination

Make failed export delivery safe to retry without changing payload preparation.

## Territory

- Export preparation creates immutable payloads.
- Export delivery sends payloads and records outcomes.

## Current state

The active territory is Export delivery. Retry ownership has not yet been
reconciled with accepted architecture.

## Blockers and dependencies

Identify the architecture seam that owns retry scheduling.

## Next work

Inspect only the accepted architecture relevant to retry ownership and expose
the next safe boundary.

## Out of scope

Account access and implementation.
