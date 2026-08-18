# D1: Use compact sorted JSON

- Related: response-serialization map

## Decision

Public response serialization uses compact JSON with keys sorted
lexicographically.

## Why

The accepted API behavior requires deterministic response bytes.

## Consequences

Serialization must omit optional whitespace and set `sort_keys=True`.
