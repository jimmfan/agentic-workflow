# ADR-0029: Preserve material decision context and gate dependent work

- Status: accepted
- Date: 2026-08-20
- Amends: ADR-0026
- Preserves: ADR-0025 and ADR-0028

## Context

Agentic Workflow is an agent-context system: its value is not merely recording
activity, but preserving the material context that humans and later agents need
to make or evaluate responsible project decisions. ADR-0025 establishes who may
decide, ADR-0026 explains how Wayfinder territory converges, and ADR-0028 makes
Wayfinder the sole durable coordinator. None states plainly when missing context
must stop dependent work or why a precise unresolved question deserves durable
preservation.

Requiring complete information would make agents stall and would promise more
certainty than engineering permits. Advancing through an unresolved material
boundary, however, can turn an assumption into implementation before the
responsible authority can evaluate it. Independent work must remain possible so
one blocked area does not serialize the whole effort.

## Decision

Agentic Workflow preserves material decision context so a later developer can
make or evaluate the decision responsibly. A precise question becomes U# when
preserving the question or its eventual answer could materially improve a later
developer’s ability to make or evaluate a decision.

Work must not cross a consequential decision boundary while material evidence,
approval, or authority remains unresolved. The affected work remains blocked.
Independent work may continue. Dependent work may proceed when the responsible
authority has sufficient evidence to decide, or the responsible authority
explicitly accepts the remaining uncertainty. The agent may make ordinary
evidence-backed judgments inside authority already delegated by the user or
accepted project policy.

Wayfinder maps uncertainty broadly and promotes only questions whose independent
preservation materially improves continuation. Precision alone does not make a
question durable. Incidental, routine, easily reconstructed, or ordinary
research and debugging fog remains lightweight. Human/project authority,
external ownership or approval, cross-area gating, and meaningful risk of a
later mistaken decision are strong promotion signals rather than a mechanical
checklist.

After consequential U# resolves, Wayfinder reconciles and shrinks the canonical
map, exposes the coherent ready frontier, and may hand off one or more
independently ready scopes. It does not advance dependency-blocked work. Each
Implementation invocation still consumes one coherent scope; substantial
execution graphs remain owned by `to-tickets`.

This decision does not promise complete information or correct decisions. It
requires sufficient context for the responsible authority to proceed honestly,
including explicit acceptance of material residual uncertainty when appropriate.
It introduces no evidence score, approval schema, tracker lifecycle, or new
state category.

## Consequences

Wayfinder is less likely to bury authority-owned, externally owned, or
cross-cutting blockers in `map.md`, while routine fog still avoids U#
proliferation. A fresh developer can find the question and eventual answer that
govern a consequential choice without loading every investigation detail.

Independent scopes may proceed in parallel, but unresolved dependencies remain
visible and enforced. The rule relies on engineering judgment for materiality
and sufficient evidence; behavioral evaluation should test both under-promotion
and needless state growth before adding formal machinery.

## Alternatives considered

- Require all information before any work proceeds: rejected because complete
  certainty is generally unavailable and unrelated ready work should continue.
- Promote every precise question to U#: rejected because precision does not show
  that independent preservation helps a later decision.
- Ask the user whether each U# file should be created: rejected because the user
  should answer substantive project questions, not manage Wayfinder storage.
- Add evidence scores or a decision-ready schema: deferred until repeated
  evaluation shows judgment is insufficient.
