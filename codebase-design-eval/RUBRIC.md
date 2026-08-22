# Observable review rubric

Review each run without rewarding fluency or use of preferred vocabulary.
Record concrete recommendations and whether they are supported by fixture or
repository evidence.

## Common observations

- Finds genuinely shallow pass-through abstractions.
- Preserves legitimate responsibility, ownership, domain, or evolution seams.
- Avoids merging modules merely because they are in-process.
- Avoids inventing replacement wrappers while claiming simplification.
- Preserves valuable high-level and edge-case test coverage.
- Preserves established project/domain terminology unless a demonstrated
  ambiguity justifies change.
- Respects scope, project authority, and read-only constraints.
- Produces a smaller conceptual surface where simplification is warranted.
- Keeps the proposed architecture understandable to a new maintainer.
- Avoids unnecessary multi-agent or Design-It-Twice expansion.

## Scenario-specific discriminator

- A: a strong run consolidates most or all pass-through quote layers while
  retaining a coherent public operation.
- B: a strong run preserves the Compliance, Inventory, and Checkout modules,
  even though they are all in-process, and may simplify only incidental
  mechanics.
- C: a strong run preserves both higher-level behavior tests and focused parser
  tests because the parser has independently meaningful edge cases and callers.
- D: a strong run identifies evidence-backed structural problems in Agentic
  Workflow without treating Codebase Design vocabulary as a migration goal or
  proposing a gratuitous rewrite.
