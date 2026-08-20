# ADR-0028: Use Wayfinder as the sole durable coordinator

- Status: accepted
- Date: 2026-08-20
- Supersedes: ADR-0012
- Amends: ADR-0011, ADR-0023, ADR-0026, and ADR-0027
- Preserves: ADR-0022 and ADR-0025

## Context

Agentic Workflow maintained two framework continuity models. Wayfinder used one
map plus optional U/E/F/D knowledge, while bounded Discovery, Debugging, and
Implementation could allocate DEC, DBG, and IMP records with their own IDs,
statuses, resume targets, conflicts, and archive rules. Supporting work inside
Wayfinder already avoided those records, making their remaining value largely a
second persistence path for standalone specialists.

The specialist skills also have stronger method ownership than Wayfinder:
Discovery compares viable alternatives, Debugging runs a falsifiable causal
loop, Research produces primary-source findings, Prototype learns through a
disposable artifact, Domain Modeling sharpens concepts, and Implementation owns
the execution boundary. Repeating those methods in Wayfinder would increase
context and create drift.

Existing deterministic and live evaluation evidence does not prove that more
structured state improves outcomes. Historical Wayfinder trajectories often
used more instructions, reads, tools, and tokens than one strong durable
handoff, sometimes without an outcome advantage. The defensible target is not
mandatory specialist use; it is one small coordination owner plus progressive
method loading.

## Decision

Wayfinder is the sole framework-owned durable coordination layer. It owns:

- destination, semantic territory, and scope boundary;
- map-first current state, blockers, dependencies, frontier, and next work;
- optional current U/E/F/D knowledge;
- progressive effort and child loading;
- reconciliation, convergence, settlement, and lifecycle; and
- readable pointers and handoffs to canonical project or provider artifacts.

Direct reasoning remains valid inside and outside Wayfinder. Encountering a
decision, failure, research question, prototype opportunity, or domain ambiguity
does not by itself load a specialist. Continue directly when the frontier can be
resolved safely without extra methodology. Load only the smallest specialist
whose method would materially improve resolution, and do not load several
specialists speculatively.

Discovery, Debugging, Research, Prototype, Domain Modeling, and other supporting
activities are stateless from the framework's perspective. They own their
methods and native artifacts, while Wayfinder persists only consequential
coordination needed to resume: unresolved frontier, useful evidence or
conclusions, relevant artifact pointers, resolution mode when useful, blockers,
dependencies, and next work. Obvious specialist dispatch from a selected map
does not require the detailed router.

Implementation remains a transition to execution. It consumes one coherent
canonical map, decision, specification, or native ticket; invokes the selected
implementation provider once; and hands the integrated result to Verification.
It is neither a Wayfinder reasoning mechanism nor an owner of durable workflow
state. If interrupted execution needs continuity not already supplied by a
canonical artifact, Wayfinder records only the consequential return frontier.

Stop allocating, resuming, validating, conflicting, or archiving DEC, IMP, and
DBG records. Remove their templates and runtime rules. Do not replace them with
another specialist record, active index, scratch tree, or lifecycle system.

Existing DEC, IMP, DBG, active-index, record, and archive files remain opaque
project-owned historical data. Lifecycle operations preserve them and no
automatic migration or compatibility parser is added. A project owner may
manually reconcile still-relevant current work into Wayfinder or another
canonical artifact.

The general durable-state contract remains only for shared project-state rules
that still have owners, including canonical-source precedence, ADR conventions,
controlled promotion, the optional IDP opportunity record, and legacy data
preservation. Wayfinder writes load only the Wayfinder contract.

## Consequences

Fresh sessions have one framework re-entry model. Standalone specialist work is
ephemeral unless it crosses the Wayfinder threshold, and supporting specialist
work cannot create a second notebook. Decision and causal methodology remain in
their specialist skills rather than being approximated in the coordinator.

The change intentionally breaks automatic DEC/IMP/DBG resume before 1.0.
Existing bytes survive, but current agents treat them as historical evidence.
An interrupted bounded specialist task that genuinely needs cross-session
continuity now pays for a map; ordinary single-session work becomes smaller.

Decision frontiers can become more expensive if Discovery is loaded
automatically. Deterministic contracts therefore require both direct Wayfinder
decision resolution and lazy Discovery composition, and context budgets include
both paths. Research, Prototype, and Domain Modeling remain optional because
their native methods and artifacts are deliberately heavier than direct work.

The owned Wayfinder runtime retains a compact dispatch vocabulary because the
coordinator must recognize when a specialist may help. It does not copy the
specialist's procedure. Detailed routing remains available for ambiguous
ownership, provider fallback, and material handoff questions.

## Alternatives considered

- Keep DEC only for bounded decisions: rejected because cross-session decision
  continuity already satisfies the Wayfinder threshold and would retain two
  decision namespaces.
- Keep DBG for detailed diagnostic logs: rejected because Debugging methodology
  remains intact and only consequential evidence belongs in durable
  coordination; raw transcripts are not project state.
- Keep IMP for interruption recovery: rejected because canonical maps,
  specifications, tickets, source, and Verification evidence already supply the
  implementation boundary, while Wayfinder covers exceptional continuity.
- Always invoke the specialist matching the frontier type: rejected because it
  would merely move context cost into routine composition and make Direct less
  reliable.
- Add a generic specialist-result or handoff record: rejected because the map
  and native artifacts already carry the needed pointers and next work.
