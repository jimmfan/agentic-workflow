# Scenario D — qualitative Agentic Workflow repository evidence

This is a read-only, non-controlled review by the primary evaluator. The real
repository was not sent to a separate hosted-model session. A narrow request to
run direct/vanilla/guarded gpt-5.4 sessions against baseline
`b722b0b1eba1bcdf52a818e06279082edbcb978d` was rejected because the user had
not explicitly authorized that exact repository payload and destination.

## Qualitative finding

No material architectural rewrite is justified by the inspected baseline.

`skills/agentic-workflow/scripts/lifecycle.py` is superficially shallow, but it
owns a real orchestration responsibility: core adoption succeeds independently
from best-effort provider projection, and the two subprocess failure policies
are explicitly documented in `docs/architecture.md`. Folding it into
`adopt.py` or `providers.py` would combine distinct reasons to change and blur
the failure contract.

`skills/agentic-workflow/scripts/providers.py` is large, but it hides declaration
validation, pinned staging, adapter application, tree comparison,
rollback-protected replacement/removal, status, and CLI behavior behind a small
command surface. On current evidence it already has a deep-module shape.

The explicit Wayfinder adapter branch is not evidence for a generic adapter
framework. ADR-0023 records why Wayfinder is a single owned-runtime exception,
and explicitly rejects generalization before a second demonstrated use case.
Codebase Design's deletion/leverage lens helps validate that choice; its
adapter-count and in-process absolutes would be harmful if applied without the
repository's failure and ownership evidence.

One watch item is the flat `ProviderSkill` shape: `adapter`,
`upstream_body_sha256`, and `projection_source` are conditionally valid fields.
A tagged configuration could make invalid states less representable, but
`load_provider` currently validates the combination centrally and only one
specialized body projection exists. Adding that abstraction now would be
speculative.

## Implication

Scenario D supports a conservative conclusion: the Codebase Design vocabulary
can help test whether a seam earns its keep, but it does not reveal a current
rewrite opportunity in Agentic Workflow. Because this is not a fresh-session
condition comparison, it cannot establish direct-versus-vanilla-versus-guarded
behavior on the real repository.
