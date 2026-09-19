# Language coherence

## Objective

Keep consequential terminology and instruction-language questions understandable and resumable as Agent Workflow evolves, preserving the distinction between inconsistent meaning and useful contextual repetition.

## Scope

Framework term meanings, normative wording, and authored-to-consumer language consistency where differences could change behavior or create competing maintenance obligations.
The initial task authorizes a bounded source audit and effort state; framework, glossary, documentation, test, and evaluator corrections and live evaluations remain outside that task.

The completed domain-language normalization work is maintained in canonical terminology, the state contract, and the [map-authoring report](../../evals/map-authoring/REPORT.md).
Its bounded changes merged through PRs #13, #14, and #31; its former map no longer has unfinished implementation to coordinate.
This standing effort retains future consequential language questions in its existing scope, without reopening those accepted choices or turning an optional live smoke into required implementation work.
The map-authoring live acceptance gap remains unaccepted and unresolved in its report; closure of the implementation effort does not resolve it.
The [responsibility-boundary effort's initial committed map](https://github.com/jimmfan/agentic-workflow/blob/d2ee78bd7154c53b431d8d424637920a7a46d13b/.project-efforts/workflow-responsibility-boundaries/map.md) addresses who owns responsibilities and handoffs; this effort addresses whether language consistently expresses intended meanings and obligations.
Consult that effort's current map for continuation, retaining one detailed question owner and linking shared concerns rather than duplicating them.

Resume only during relevant authorized work that materially changes a represented meaning, instruction, or evidence claim.
This map is not self-updating, a second glossary, a normative instruction source, or a requirement to audit unrelated work.
Style-only rewrites, ordinary repetition, generic code deduplication, and speculative cleanup are excluded.

## Ready work

The initial audit is complete.
No new language correction or live evaluation is proposed as ready work: the inspected sources did not establish a consequential terminology defect or harmful instruction duplication.
Future findings may justify a bounded proposal; a proposal does not authorize its implementation.

## Current state

The current glossary, root policy and templates, routing, state contract, distributed skill instructions, architecture decisions, documentation, and relevant coverage distinguish term definitions from required behavior and project decision authority from action authorization.
No second authoritative framework glossary, active use of the former state path, or authored-to-consumer wording divergence was established in the inspected current surfaces.
This is a source-audit conclusion, not proof of reliable agent interpretation.

The following repetitions have supported purposes and do not currently justify consolidation:

- **Truthfulness across scopes:** the [root policy](../../AGENTS.md) and synchronized [consumer template](../../agent_workflow/install/AGENTS.md.template) explicitly prioritize factual accuracy over output completion, extending the existing prohibition on claiming unexecuted work.
  The source repository's [verification guidance](../../AGENTS.md#testing-and-verification), [Code Review](../../.agents/skills/code-review/SKILL.md), and [spec synthesis](../../.agents/skills/to-spec/SKILL.md) retain narrower applications to reporting checks, unavailable reviewers, and unresolved scope.
  These contextual rules add operational detail; their overlap does not make the general priority redundant or establish that agents reliably follow it.
- **Authority at different loading boundaries:** [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) explains why the always-loaded root policy carries authority rules.
  [Discovery](../../.agents/skills/workflow-discovery/SKILL.md#resolve-the-decision) applies them to project choices; [Debugging](../../.agents/skills/workflow-debugging/SKILL.md#fix-and-verify) applies authorization and reconciliation timing to causal work.
  Removing the root obligation would leave work before specialist loading without that instruction; removing contextual clauses could lose the specific trigger or timing.
- **Meaning versus operation:** [terminology](../../.agent-workflow/terminology.md) defines dependencies and blockers; the [state contract](../../.agent-workflow/contracts/wayfinder-state.md#dependencies-and-readiness) applies those meanings to scoped readiness and persistence.
  The latter supplies operational detail rather than another glossary.
- **Different contexts and history:** [Domain Modeling](../../.agents/skills/domain-modeling/SKILL.md) maintains project domain language, while [Codebase Design](../../.agents/skills/codebase-design/SKILL.md#glossary) supplies module-design vocabulary and preserves project meanings.
  These are distinct contexts under [ADR-0029](../../architecture-decisions/0029-distribute-canonical-framework-terminology.md).
  Former paths in the [reinstall/move guidance](../../README.md#one-time-reinstall-for-the-repository-layout-release) and ADR history are explicitly historical; their presence is not evidence of an active competing name.

The unresolved meaningful-Debugging-to-build handoff question remains with the responsibility-boundary effort and the [existing investigation](../../evals/remaining-audit-behavior/REPORT.md#h2--debuggings-transition-may-omit-meaningful-closing-review).
Its attribution remains inconclusive; no independent language-defect record is warranted here on the same evidence.

## Areas and relationships

- **Definitions:** [canonical terminology](../../.agent-workflow/terminology.md) maintains shared framework meanings; [ADR-0029](../../architecture-decisions/0029-distribute-canonical-framework-terminology.md) separates these from specialized behavior and project-owned domain models.
- **Obligations and context:** the [root-policy template](../../agent_workflow/install/AGENTS.md.template), [routing](../../.agent-workflow/routing.md), [state contract](../../.agent-workflow/contracts/wayfinder-state.md), and [selected skills](../../.agents/skills/) maintain their respective rules.
  The [architecture overview](../../docs/architecture.md#instruction-runtime) explains why some obligations must remain available before detailed instructions load.
- **Delivery:** the [manifest](../../agent_workflow/install/manifest.json) maps canonical framework and skill files to their same consumer paths and templates to root policy files.
  [Package verification](../../agent_workflow/verify_package.py) checks managed-root/template synchronization; [distribution tests](../../tests/test_direct_distribution.py) exercise byte-for-byte framework and skill delivery and preserve project domain files.
- **Evidence:** [test ownership and limitations](../../tests/README.md) distinguish delivery observations, literal interfaces, evaluator controls, and live evidence.
  [Term-inventory tests](../../tests/test_routing.py) protect canonical names; the removed [specialist reconciliation guards](https://github.com/jimmfan/agentic-workflow/blob/92d3304473b0fbebdcb6ab08b41bbad1d9710a50/tests/test_specialist_reconciliation.py) and [instruction-coherence controls](https://github.com/jimmfan/agentic-workflow/blob/92d3304473b0fbebdcb6ab08b41bbad1d9710a50/tests/test_instruction_coherence.py) remain historical evidence only.
  Their earlier success did not establish semantic equivalence or agent compliance.

## Blockers

No unresolved dependency prevents completion of this bounded audit.
Reliable agent interpretation remains unproven by source inspection and deterministic controls; no live evaluation was performed.
Existing campaign limitations remain with their maintaining reports and efforts and do not block this source-level conclusion.

## Key references

- [Framework terminology and ownership decision](../../architecture-decisions/0029-distribute-canonical-framework-terminology.md).
- [Progressive-loading decision](../../architecture-decisions/0027-use-direct-first-progressive-routing.md).
- [Prose and verification requirements](../../docs/verification.md#maintainer-and-ci-gate).
- [Completed map-authoring work and unresolved live acceptance](../../evals/map-authoring/REPORT.md).

For a future consequential finding, preserve the relevant passages and sources, the competing interpretations, the affected behavior or maintenance obligation, and the strength and limits of the evidence.
Keep its detail in one maintaining location under the [Wayfinder state contract](../../.agent-workflow/contracts/wayfinder-state.md#current-knowledge); do not create a record merely because wording differs.
