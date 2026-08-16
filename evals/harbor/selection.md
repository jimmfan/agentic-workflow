# Frozen SlopCodeBench smoke selection

Selection was finalized on 2026-08-15 before any Codex benchmark result was
observed.

Dataset: `gabeorlanski/slopcodebench`

Immutable dataset identifier:
`sha256:73a17cda817d37ce3352d18c272c40a3f6b623061023bee365b4df74adcd11b5`

Selected tasks:

| Task | Immutable task identifier | Checkpoints | Difficulty | Why selected |
|---|---|---:|---|---|
| `circuit_eval` | `sha256:3bbbb4e0f03cc0824f4a77d0e1ab15004eebb01b8774488dd130f0508321a700` | 8 | medium | A parser/evaluator/optimizer evolves across many checkpoints. Later work must preserve earlier scalar and vector behavior, creating meaningful architectural and regression risk. |
| `database_migration` | `sha256:15a6ac32fc6e2ac000df7e634d6f21899aed228418fdb277725ee93790f0d25f` | 5 | medium | DDL grows into transformations, constraints, rollback, and dependency ordering. State correctness and backward compatibility make iterative reasoning consequential. |
| `trajectory_api` | `sha256:e2d4bdf7dffca38ecba7ceffce4e53b1ec16b9ca5824e28819f9a6540e904ae2` | 5 | medium | A REST API accumulates concurrency, lineage, parsing, and sandboxed-execution requirements, providing cross-cutting changes and substantial regression exposure. |

The three tasks were chosen from registry metadata and task structure, not from
any observed result. They deliberately span simulation, databases, and web/API
work while holding the published difficulty level constant. No benchmark task,
instruction, solution, or verifier was edited.

