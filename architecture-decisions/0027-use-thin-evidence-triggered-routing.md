# ADR-0027: Use thin evidence-triggered routing

- Status: accepted
- Date: 2026-08-19
- Amends: ADR-0013 and ADR-0021

## Context

The installed root policy and detailed router previously contributed 2,169
words before a route-specific skill. Uncertain bounded work loaded the detailed
router before the agent had inspected enough evidence to classify the request,
and one obvious selected skill paid the same routing cost. The framework's
installed skill descriptions already provide a cheap first selection interface.

Automatic Wayfinder selection remains valuable when consequential state would
otherwise be lost or conflated, but raw item counts are poor proxies: several
routine actions may stay Direct while one authoritative conflict may justify
durable coordination. The project also needs to retain Domain Modeling,
specification, ticketing, provider, and lifecycle capabilities without loading
their complete instructions for unrelated work.

An opt-in cross-model smoke test later showed that the original wording was not
deterministic enough after reconnaissance. A frontier model escalated when a
synthetic target revealed several hard signals; a smaller model correctly began
Direct and identified the same blocker, conflict, and provenance needs, but
completed Direct instead of selecting Wayfinder. The phrase "re-evaluate when
evidence changes" did not reliably force the assessment step.

## Decision

Use a thin, Direct-first root router. Classify from user intent and installed
skill descriptions, then perform only the smallest authorized read-only
reconnaissance needed when evidence is insufficient. Load the detailed routing
contract only for unresolved ambiguity, multi-workflow composition, material
provider fallback or handoff, or unclear ownership of a relevant durable
resume. One obvious skill loads directly.

Keep authorization, human/project authority, truthful execution reporting,
unrelated-work preservation, canonical-artifact precedence, read-only
non-mutation, and the pre-write durable-state gate in always-loaded policy.
Methodology and detailed storage mechanics remain progressively loaded.

Three or more meaningful items trigger a Wayfinder assessment, never selection
by count alone. Select Wayfinder when any hard signal or at least two soft
signals make durable coordination materially safer. Hard signals cover
cross-session continuity, authoritative conflicts, authority-owned blockers
alongside work that can proceed, coordinated owners or areas, and provenance
needed to distinguish assumptions from facts. Soft signals cover interacting
consequential unknowns, multiple durable state categories, evidence-driven plan
change, meaningful dependency graphs, and material fresh-agent reconstruction
risk. This is a qualitative activation rubric, not a weighted complexity score.

After any reconnaissance, require an explicit Wayfinder assessment before
completion. When the rubric finds any hard signal or at least two soft signals,
selection is mandatory unless the user opted out or authorization or host
compatibility blocks execution. Keep this gate in the thin root policy; do not
restore unconditional loading of the detailed router.

Treat route sequences as default transitions with entry conditions, not
mandatory pipelines. Host todos hold current-session actions; Wayfinder holds
durable coordination; specifications hold settled scope and acceptance; tickets
hold approved independently deliverable work and blocking edges. Their native
artifacts remain canonical.

Retain the route marker during this change so routing-context effects can be
isolated from observability changes. Retain all provider skills and lifecycle
automation.

Because the project is pre-1.0, adoption does not require live or model-based
grading. The release gate uses deterministic contract scenarios, lifecycle and
state-safety tests, fresh-session fixture integrity, source/payload checks, and
word-count budgets. The budgets require at least an approximately 80% reduction
when the old ambiguity gate would have loaded both root and router, 35% for work
that was already confidently Direct and loaded only the old root, and 50% for
ordinary selected workflows. These checks prove packaged contracts, state
survival, and continuation structure—not that a live model will select the
right route or consume a fresh-session handoff successfully.

## Consequences

Bounded work and one obvious skill avoid the detailed router. Complex
composition still pays for the policy it needs. The framework becomes more
dependent on concise, accurate skill descriptions and on agents re-evaluating
the route when evidence changes.

The main risks are under-routing, late Wayfinder escalation, over-routing from
mechanical counts, rigid pipeline interpretation, host-specific catalog drift,
and durable writes occurring before safety contracts load. Deterministic tests
therefore preserve negative and positive routing cases, explicit read-only and
authority boundaries, relevant fresh-session continuation, provider
truthfulness, and the pre-write contract gate. Without live model-based grading,
missed-route and fresh-agent outcome regressions remain observable risks rather
than deterministically proven absences.

The mandatory post-reconnaissance assessment slightly strengthens the thin
gate without increasing its 433-word budget. It may expose more false-positive
assessments, but counts still cannot select Wayfinder and isolated unknowns and
routine actions retain their explicit Direct boundary.

Reconsider this decision if ordinary work repeatedly misses an applicable
workflow, fresh sessions lose consequential state, host catalogs cannot expose
reliable descriptions, or deterministic tests pass while observed agent
behavior regresses. Such evidence may justify tightening the thin gate or adding
targeted live evaluation; it does not by itself justify restoring unconditional
detailed-router loading.

## Alternatives considered

- Keep the existing ambiguity-first detailed-router gate: rejected because it
  charges maximum classification context at the point of least evidence.
- Remove Domain Modeling, `to-spec`, `to-tickets`, providers, or lifecycle
  automation: rejected because capability availability is inexpensive when
  bodies load lazily, and lifecycle automation protects project-owned data.
- Select Wayfinder at a fixed item count: rejected because quantity does not
  establish consequence, interaction, persistence, or coordination risk.
- Require model-based grading before a pre-1.0 change: rejected for this release
  because deterministic safety and contract gates make the change reversible;
  live evaluation remains a reconsideration tool when behavior warrants it.
