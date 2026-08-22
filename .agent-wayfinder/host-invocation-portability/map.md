# Host invocation portability

## Destination

Establish whether Agent Workflow preserves provider explicit-only invocation semantics across its claimed hosts and, if evidence confirms a gap, make the smallest justified correction with truthful compatibility claims and verification.

## Notes

- The user authorized investigation and the smallest appropriate implementation if evidence confirms a defect or verification/documentation gap.
- Preserve upstream provider artifacts and keep live-host observations distinct from documentation and inference.
- Research findings belong in the canonical research report; this map records only coordination consequences.
- [U1 — Do supported hosts preserve provider explicit-only invocation?](unknowns/U1-supported-host-explicit-only-invocation.md) — resolved: documented Codex and Copilot VS Code/CLI controls match the existing dual metadata; cloud/live behavior stays qualified.
- Canonical evidence: [Host invocation portability research](../../../docs/host-invocation-portability-research.md).
- Result: documentation/verification gap only; no new portability layer or ADR was justified.

## Decisions so far

None. The investigation confirmed the existing host-specific contract rather than adopting a new architectural choice.

## Not yet specified

Copilot cloud-agent/code-review enforcement and live cross-model behavior remain optional follow-up evidence before widening support claims beyond documented VS Code/CLI behavior.

## Out of scope

- A generic metadata translation or plugin framework.
- A benchmark campaign or normal-CI dependency on live hosted models.
