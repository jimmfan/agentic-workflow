# Decisions

## D1 — Use compact sorted JSON

- Status: accepted
- Authority: Project owner, with acceptance recorded in README.md
- Based on: The accepted API requirement for deterministic response bytes
- Consequences: Serialization omits optional whitespace and sorts keys lexicographically

Public response serialization uses compact JSON with keys sorted
lexicographically. This produces deterministic response bytes.
