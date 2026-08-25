# Platform migration planning fixture

The migration spans several sessions. The authoritative migration architecture
already establishes the destination, scope, major areas, and relationships.
The project owner accepted zero downtime, the safe migration order is
unresolved, and inventorying current consumers is concrete work that can
proceed without answering the ordering question.

Record that accepted choice as `D1 — Use a zero-downtime cutover` in the
effort's root `decisions.md` ledger and link the map directly to its heading.
Keep the independently useful ordering question as U1 rather than folding its
coordination detail into the ledger.

Repository-local durable planning is authorized. No external tracker is
configured, and no external-system mutation is authorized.
