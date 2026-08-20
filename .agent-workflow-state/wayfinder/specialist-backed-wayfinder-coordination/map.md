# Specialist-backed Wayfinder coordination

- Status: current

## Destination

Agentic Workflow has one framework-owned durable coordination layer: Wayfinder.
Direct reasoning remains valid, specialist methods load only when they materially
help the current frontier, and ready work crosses a clean Implementation and
Verification boundary without DEC, IMP, DBG, or replacement workflow records.

## Territory

- Routing and dispatch — Direct-first selection, obvious Wayfinder composition,
  specialist laziness, provider truthfulness, and route reporting.
- Specialist boundaries — standalone and Wayfinder-supporting Discovery,
  Debugging, Research, Prototype, Domain Modeling, and Implementation behavior.
- Durable ownership — map-first U/E/F/D continuity, legacy record preservation,
  removal of new DEC/IMP/DBG allocation, and remaining shared project-state rules.
- Delivery and evidence — runtime projection, distributable payload, ADRs,
  deterministic scenarios, context measurements, and package verification.

These areas meet at one seam: a specialist may resolve a frontier, but Wayfinder
alone preserves the consequential coordination needed to resume.

## Current state

- Authored package contracts, runtime projection, specialist adapters,
  documentation, ADR-0028, distribution inventory, deterministic scenarios,
  and tests now implement the sole-coordinator model.
- DEC/IMP/DBG allocation, resumption, conflicts, archive rules, and two obsolete
  templates are removed. Lifecycle preserves existing files as opaque data.
- Discovery and Debugging retain their bounded decision and causal methods;
  Implementation retains execution plus Verification without specialist state.
- The two known stale root-policy assertions were corrected before comparison.
- Directional instruction profiles decreased from the established baselines:
  Direct 3,362/466 to 3,159/433 bytes/words; standalone Discovery 7,642/1,050
  to 5,937/811; direct Wayfinder decision 54,264/7,683 to 38,554/5,542;
  Wayfinder plus Discovery 41,332/5,920; causal 71,751/10,118 to
  43,098/6,177; research 68,316/9,636 to 39,582/5,686; implementation
  52,822/7,462 to 45,547/6,459; all-specialist multi-front 79,626/11,294 to
  60,082/8,567.
- Source/static verification passes; 65 lifecycle tests, 18 routing tests, 15
  behavior-contract tests, and 78 existing eval tests pass. The package's full
  suite now has 115 independently passing tests and one dogfood-parity failure
  because the local installed projection remains stale.

## Blockers and dependencies

The repository's `.agents/` tree is read-only in this session. The authorized
lifecycle update was attempted with escalation and rejected, so managed local
skills, installed contracts, root managed policy, and obsolete installed
templates remain repairable rather than current. Do not bypass the safeguard by
editing generated surfaces independently.

## Next work

After explicit filesystem approval, run
`python3 skills/agentic-workflow/scripts/lifecycle.py update
/Users/james/Desktop/projects/agentic-wayfinder-auto`, then rerun the full
package verifier and close this effort if parity passes.

## Notes

- Preserve existing legacy workflow records as opaque project-owned data; add no
  migration or compatibility parser.
- Use existing deterministic routing/behavior harnesses and token/context
  instrumentation; do not create a new benchmark framework.
- The accepted human-authority, canonical-artifact, project-data preservation,
  U/E/F/D, and scoped reconciliation rules remain governing constraints.

## Decisions so far

- Proceed with the user-authorized pre-1.0 simplification: Wayfinder becomes the
  sole framework-owned durable coordination layer, while specialists remain
  stateless from the framework's perspective.
- Obvious specialist selection inside an already selected Wayfinder effort must
  not load the detailed router merely because composition exists.
- Implementation remains a handoff/execution boundary and receives no successor
  to IMP.

## Out of scope

- Migrating, deleting, or normalizing legacy project-owned DEC/IMP/DBG files.
- Adding new micro-skills, scratch state, lifecycle services, migration layers,
  or a new benchmark framework.
- Changing the pinned upstream provider version or rewriting frozen historical
  evaluation results.
