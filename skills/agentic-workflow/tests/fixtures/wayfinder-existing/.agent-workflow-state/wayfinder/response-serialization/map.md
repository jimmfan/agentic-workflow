# Response serialization

## Destination

The service has an accepted response format and an executable path to implement
it without inventing unresolved telemetry policy.

## Notes

- Next executable work: [T1 — Serialize public responses](tickets/T1-serialize-public-responses.md).
- Preserve [U1 — Name the telemetry metric](unknowns/U1-name-telemetry-metric.md); it is explicitly non-blocking for T1.

## Decisions so far

- [D1 — Use compact sorted JSON](decisions/D1-use-compact-sorted-json.md) — public responses use compact JSON with lexicographically sorted keys.

## Not yet specified

None.

## Out of scope

Telemetry naming is outside the response-serialization slice.
