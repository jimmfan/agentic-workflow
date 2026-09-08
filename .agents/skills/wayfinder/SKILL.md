---
description: Keep a lightweight structured map for a consequential objective when durable coordination materially improves continuity across sessions, agents, external dependencies, or participants, including when the route remains unclear. Clear bounded work stays on its minimum useful route.
name: wayfinder
---
# Wayfinder

This maintained skill is derived from Matt Pocock's Wayfinder methodology.
It orients an effort, chooses the minimum useful resolution method, reconsiders the route as evidence develops, and identifies ready work.
Root policy determines when Wayfinder is selected; an objective or existing state alone does not select it.

## Load the state boundary

Once Wayfinder is selected, read `.agent-workflow/contracts/wayfinder-state.md` before inspecting or changing effort state.
The contract owns recognition, creation and resumption identity, map authoring, selective record preservation, identifiers, reconciliation, pruning, and ending.
Resume from `map.md`, following the contract's progressive detail loading; do not substitute a specialist notebook or parallel coordination record.
If the contract is unavailable, stop affected Wayfinder work: do not inspect or change a map, invent substitute persistence, or create tracker, specialist-record, or scratch state.
Report the incomplete installation.

Establish objective and scope from user intent and accepted project evidence, using the contract's identity and creation rules.
Selection may still leave no consequential continuity worth preserving; in that case create no effort or records.
Inspect Git/session state when useful for safe execution; the contract's Current state convention governs what earns durable retention.
Apply root policy's authority, authorization, evidence-precedence, and preservation rules throughout this method.

## Establish areas and relationships

Establish enough relevant areas and relationships to orient the effort before substantial decomposition, then derive the effort name and stable path from its objective and scope under the contract.
Reuse accepted project structure when it supplies a useful objective, scope, areas, and important operating boundaries; otherwise establish the smallest useful structure directly.
Make consequential participant responsibilities and operating boundaries explicit using established assignments or their designated maintaining sources, following the contract's responsibility authoring rules.
Clarify consequential unknown responsibility or decision authority when affected work requires it; continue independent authorized work without inventing assignments or prerequisites.
The effort's view is provisional and adaptive, while established assignments and authority remain grounded in their sources.
Use this view to challenge incomplete framing as evidence develops without silently broadening the user's goal, delegated authority, or implementation scope.

Domain Modeling applies when clarifying or reorganizing domain concepts, terminology and ubiquitous language, domain or context boundaries, or domain responsibilities and relationships would materially improve the work; progress need not already be blocked.
It does not own generic implementation or module architecture, all project structure, or Wayfinder's effort view merely because the map contains areas and relationships.
When it would help, resolve enough domain-model ambiguity before substantial U/E/F/D accumulates.
On resumption, do not reload Domain Modeling merely because Wayfinder resumed.
If the effort view no longer fits current truth, revise the same map or select the specialist appropriate to the actual uncertainty; load Domain Modeling again only for domain-model ambiguity.

## Chart the visible route

After orientation, chart only as far as current evidence supports; do not fully decompose uncertain future work.
Distinguish precise questions that can be addressed now from consequential in-scope territory that is **Not yet specified** because the relevant question cannot yet be stated clearly.
Do not turn that unclear territory into speculative questions, records, tickets, dependencies, implementation scopes, or assumed answers.
For each useful precise question, choose the minimum resolution method below.

After a consequential resolution or material new finding, revisit the affected route before continuing.
Newly understood territory may become precise, earlier questions may no longer apply, and areas, relationships, dependencies, blockers, or ready work may change.
Stop expanding the route when the work that may proceed is sufficiently clear.

## Choose the minimum resolution method

Continue directly when no additional method is needed.
Otherwise select only the smallest specialist needed to resolve or accurately frame the current question, uncertainty, unexplained cause, consequential choice, or domain-model ambiguity:

- **Discovery** for consequential alternatives and tradeoffs.
- **Debugging** for an observed behavior with an unknown cause.
- **Research** for external uncertainty needing primary-source evidence.
- **Prototype** when an interactive logic demo or contrasting UI variants would answer the design question.
  CLI and infrastructure experiments may use Direct or another applicable method.
- **Domain Modeling** for domain concepts, language, context boundaries, responsibilities, and relationships under the rule above.
- **Human clarification or Grilling** for authority, intent, preference, or prioritization.

Research, Prototype, and Debugging operate on uncertainties and questions within established areas and relationships; they do not replace Domain Modeling when the uncertainty concerns the domain model.
Use detailed routing when composition or selected-skill availability materially matters.
Each specialist retains its method and creates no separate Agent Workflow durable coordination state.

A resolution method determines the evidence or authority needed, not merely an artifact label:

- Human clarification requires the person with the relevant intent or preference, or the person, role, or valid delegate with project decision authority.
- Research requires appropriate source evidence.
- Prototype or Debugging requires relevant observed or experimental evidence.

Existing evidence from a source that establishes the scoped claim may satisfy the method without a ceremonial specialist invocation.
One method cannot substitute for another's required authority or evidence.
Do not load specialists speculatively.

## Reconcile and transition ready work

Map uncertainty broadly, then preserve selectively using the contract's Current knowledge rules.
A precise question alone does not earn a U#.
When project knowledge determines whether separate preservation is useful, ask the substantive project question rather than asking merely whether to create a record.
Keep the map brief and sufficient for a fresh session to continue, linking the artifacts that maintain lasting results.
If work is interrupted, retain only consequential coordination and references under the contract rather than a specialist activity log.

Use the contract's Dependencies and readiness rules to distinguish required inputs, conditions blocking particular work, and independent work that may proceed.
When dependency evidence is sufficient, surface the critical path, independent parallel work, and any off-path dependency whose external lead time changes ordering or readiness.
Do not infer a critical path from an unordered backlog or incomplete evidence.
For a consequential unresolved question affecting a transition, obtain the appropriate evidence or project choice, or record authorized scoped acceptance under the contract; acceptance leaves the question unresolved.

Reconcile affected state through the contract's common sequence before handing off ready work.
That sequence distinguishes current-state checks before mutation, retrievability verification before pruning, and saved-result readback before claiming completion.
Transition one or more ready implementation scopes without advancing dependency-blocked work.
Each transition to Implementation consumes one ready scope and its acceptance criteria; Verification follows material execution.
Use `to-tickets` only when approved work needs substantial dependency ordering or independently deliverable sessions.
Follow the contract's map-versus-ticket responsibility rule when referring to that work.
