# Response serialization

## Destination

The service has an accepted response format and an executable path to implement
it without inventing unresolved telemetry policy.

## Current state

- [D1 — Use compact sorted JSON](decisions.md#d1--use-compact-sorted-json) is accepted.
- [U1 — Name the telemetry metric](unknowns/U1-name-telemetry-metric.md) remains unresolved and does not constrain response serialization.

## Blockers and dependencies

None. D1 settles the only dependency for the current implementation slice.

## Next work

- Implement `serialize_payload` in `service.py` using D1, then run `python verify.py`.

## Notes

- Preserve U1; telemetry naming is explicitly non-blocking for this work.

## Decisions so far

- [D1 — Use compact sorted JSON](decisions.md#d1--use-compact-sorted-json) — public responses use compact JSON with lexicographically sorted keys.

## Not yet specified

None.

## Out of scope

Telemetry naming is outside the response-serialization slice.
