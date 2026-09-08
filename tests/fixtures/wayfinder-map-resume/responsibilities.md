# Consumer delivery agreement

## Assignments

This artifact maintains these established assignments for the consumer handoff:
- Platform team maintains the test environment.
- Application team implements the consumer.

## Integration constraints

The consumer must preserve event_id across retries.
Synthetic test payloads must be discarded after each run.
