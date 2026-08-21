# ADR-0001: Delivery adapter owns retries

- Status: accepted

The Delivery adapter owns retry scheduling and idempotency for failed exports.
Export preparation supplies an immutable payload and does not schedule retries.
