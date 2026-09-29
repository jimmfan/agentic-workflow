# Language coherence

## Objective

Keep consequential terminology and instruction-language questions understandable and resumable as Agent Workflow evolves, preserving the distinction between inconsistent meaning and useful contextual repetition.

## Scope

Framework term meanings, normative wording, and authored-to-consumer language consistency where differences could change behavior or create competing maintenance obligations.
The initial task authorized a bounded source audit and effort state; framework, glossary, documentation, test, and evaluator corrections and live evaluations were outside it.
jimmfan later authorized the instruction-meaning corrections merged in [PR #54](https://github.com/jimmfan/agentic-workflow/pull/54) on 2026-09-20; architecture, runtime behavior, interfaces, data formats, ownership, evaluation design, and live evaluations were outside that cleanup.
On 2026-09-29 jimmfan authorized committing and pushing the glossary additions in 0.38.0 to a branch.

The completed domain-language normalization is maintained in canonical terminology, the state contract, and the [map-authoring report](../../evals/map-authoring/REPORT.md); it merged through PRs #13, #14, and #31.
This standing effort retains future consequential language questions without reopening those accepted choices or turning an optional live smoke into required implementation work.
The map-authoring live acceptance gap remains unaccepted and unresolved in its report; closure of the implementation effort does not resolve it.
The [responsibility-boundary effort](../workflow-responsibility-boundaries/map.md) addresses who owns responsibilities and handoffs; this effort addresses whether language consistently expresses intended meanings and obligations.
Keep one detailed owner for each question and link shared concerns rather than duplicating them.

Resume only during relevant authorized work that materially changes a represented meaning, instruction, or evidence claim.
This map is not self-updating, a second glossary, a normative instruction source, or a requirement to audit unrelated work.
Style-only rewrites, ordinary repetition, generic code deduplication, and speculative cleanup are excluded.

## Ready work

No language correction or live evaluation is ready.
Replacing the root policy's long authority phrases with the new glossary terms waits on the live baseline that gates root-policy condensing in the [context-efficiency effort](../context-efficiency/map.md#ready-work).

## Current state

**Glossary coverage (0.38.0).**
The root policy and contracts rely on Direct, action authorization, accepted project policy, committed project choices, and maintaining artifacts, and the records contract defines E# and D# records alongside U# and F#.
[Terminology](../../.agent-workflow/terminology.md) has an entry for each, restating meanings already set by [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md), [ADR-0027](../../architecture-decisions/0027-use-direct-first-progressive-routing.md), [ADR-0028](../../architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md), routing, and the [records contract](../../.agent-workflow/contracts/effort-records.md) without renaming anything; before 0.38.0 none of them had one.
Shorter replacement names for the authority phrases, such as "decision owner", were considered and not introduced, because renaming a canonical term needs the [terminology change procedure](../../docs/maintenance.md#changing-canonical-terminology) and would change the gated root policy.

**PR #54 corrections.**
Implementation permits reporting execution only after actually executing the method, and Prototype states its in-memory default and allows scratch persistence when persistence is part of the question.
The `to-spec` and `to-tickets` snippet rule requires both prototype origin and greater precision in the snippet itself.
PR #54 maintains the detailed changes and verification evidence.
No live evaluation checked those corrections, and clearer wording does not establish improved agent behavior.
No new consequential language question remained from that cleanup; the token-forensics `skills_materially_invoked` schema concern deferred from it remains open.

The initial audit found that the glossary, root policy and templates, routing, state contract, distributed skill instructions, architecture decisions, documentation, and relevant coverage distinguish term definitions from required behavior and project decision authority from action authorization.
That audit established no consequential terminology defect, harmful instruction duplication, second authoritative framework glossary, active use of the former state path, or authored-to-consumer wording divergence in the surfaces it inspected.
These conclusions retain that audit's scope and evidence limits; they are not an exhaustive absence-of-defects finding or proof of reliable agent interpretation.

The following repetitions have supported purposes and do not currently justify consolidation:

- **Truthfulness across scopes:** the [root policy](../../AGENTS.md) and synchronized [consumer template](../../agent_workflow/install/AGENTS.md.template) explicitly prioritize factual accuracy over output completion, extending the existing prohibition on claiming unexecuted work.
  The source repository's [verification guidance](../../AGENTS.md#testing-and-verification), [Code Review](../../.agents/skills/code-review/SKILL.md), and [spec synthesis](../../.agents/skills/to-spec/SKILL.md) retain narrower applications to reporting checks, unavailable reviewers, and unresolved scope.
  These contextual rules add operational detail; their overlap does not make the general priority redundant or establish that agents reliably follow it.
- **Authority at different loading boundaries:** [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) explains why the always-loaded root policy carries authority rules.
  [Discovery](../../.agents/skills/workflow-discovery/SKILL.md#resolve-the-decision) applies them to project choices; [Debugging](../../.agents/skills/workflow-debugging/SKILL.md#fix-and-verify) applies authorization and reconciliation timing to causal work.
  Removing the root obligation would leave work before specialist loading without that instruction; removing contextual clauses could lose the specific trigger or timing.
- **Meaning versus operation:** [terminology](../../.agent-workflow/terminology.md) defines dependencies and blockers; the [state contract](../../.agent-workflow/contracts/effort-state.md#dependencies-and-readiness) applies those meanings to scoped readiness and persistence.
  The latter supplies operational detail rather than another glossary.
- **Authority reminders where rules load:** [routing](../../.agent-workflow/routing.md), the [state](../../.agent-workflow/contracts/effort-state.md) and [records](../../.agent-workflow/contracts/effort-records.md) contracts, and [Wayfinder](../../.agents/skills/wayfinder/SKILL.md) each carry a one-sentence reminder that the root authority, authorization, and preservation rules still bind, about 60 words in all.
  They re-anchor those rules in files read long after the root policy.
- **Different contexts and history:** [Domain Modeling](../../.agents/skills/domain-modeling/SKILL.md) maintains project domain language, while [Codebase Design](../../.agents/skills/codebase-design/SKILL.md#glossary) supplies module-design vocabulary and preserves project meanings.
  These are distinct contexts under [ADR-0029](../../architecture-decisions/0029-distribute-canonical-framework-terminology.md).
  Former paths in the [reinstall/move guidance](../../README.md#one-time-reinstall-for-the-repository-layout-release) and ADR history are explicitly historical; their presence is not evidence of an active competing name.

## Areas and relationships

- **Definitions:** [canonical terminology](../../.agent-workflow/terminology.md) maintains shared framework meanings; [ADR-0029](../../architecture-decisions/0029-distribute-canonical-framework-terminology.md) separates these from specialized behavior and project-owned domain models.
- **Obligations and context:** the [root-policy template](../../agent_workflow/install/AGENTS.md.template), [routing](../../.agent-workflow/routing.md), [state contract](../../.agent-workflow/contracts/effort-state.md), and [selected skills](../../.agents/skills/) maintain their respective rules.
  The [architecture overview](../../docs/architecture.md#instruction-runtime) explains why some obligations must remain available before detailed instructions load.
- **Delivery:** the [manifest](../../agent_workflow/install/manifest.json) maps canonical framework and skill files to their same consumer paths and templates to root policy files.
  [Package verification](../../agent_workflow/verify_package.py) checks managed-root/template synchronization; [distribution tests](../../tests/test_direct_distribution.py) exercise byte-for-byte framework and skill delivery and preserve project domain files.
- **Evidence:** [test ownership and limitations](../../tests/README.md) distinguish delivery observations, literal interfaces, evaluator controls, and live evidence.
  [Term-inventory tests](../../tests/test_routing.py) protect canonical names; the removed [specialist reconciliation guards](https://github.com/jimmfan/agentic-workflow/blob/92d3304473b0fbebdcb6ab08b41bbad1d9710a50/tests/test_specialist_reconciliation.py) and [instruction-coherence controls](https://github.com/jimmfan/agentic-workflow/blob/92d3304473b0fbebdcb6ab08b41bbad1d9710a50/tests/test_instruction_coherence.py) remain historical evidence only.
  Their earlier success did not establish semantic equivalence or agent compliance.

## Blockers

No unresolved dependency blocks this effort's current work.
Reliable agent interpretation remains unproven by source inspection and deterministic controls; no live evaluation was performed.
Existing campaign limitations remain with their maintaining reports and efforts and do not block this source-level conclusion.

## Key references

- [Framework terminology and ownership decision](../../architecture-decisions/0029-distribute-canonical-framework-terminology.md).
- [Progressive-loading decision](../../architecture-decisions/0027-use-direct-first-progressive-routing.md).
- [Prose and verification requirements](../../docs/verification.md#maintainer-and-ci-gate).
- [Completed map-authoring work and unresolved live acceptance](../../evals/map-authoring/REPORT.md).

For a future consequential finding, preserve the relevant passages and sources, the competing interpretations, the affected behavior or maintenance obligation, and the strength and limits of the evidence.
Keep its detail in one maintaining location under the [effort state contract](../../.agent-workflow/contracts/effort-state.md#current-knowledge); do not create a record merely because wording differs.
