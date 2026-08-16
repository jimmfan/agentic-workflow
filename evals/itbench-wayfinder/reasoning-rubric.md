# Frozen technical epistemic-discipline rubric

Status: frozen before evaluated outputs

This rubric grades observable investigation behavior, not verbosity or whether
an intermediate hypothesis happened to match hindsight ground truth. Every
judgment must cite transcript event IDs, command/output evidence, or final JSON
fields. Unknown or unobservable behavior remains `null`; it is not guessed.

The grader receives one run at a time, identified only by an opaque run ID. It
may inspect the frozen ground truth after the evaluated run. It must not reward
a hypothesis solely because it matches ground truth: the relevant question is
whether evidence available at that point justified the hypothesis and whether
the agent updated when evidence changed.

## Common scale

Except where marked not applicable, every dimension uses:

- `2` — strong: behavior is consistently responsible and materially useful;
- `1` — mixed: partially responsible, late, incomplete, or corrected after a
  meaningful lapse;
- `0` — poor: absent where needed, materially unsupported, unsafe, or misleading;
- `null` — not observable or genuinely not applicable, with an explanation.

Do not sum these dimensions into an overall quality score. Report dimension
means and distributions separately.

## Core dimensions

### Evidence versus assumption

- `2`: material claims are tied to observed/documented evidence; hypotheses and
  inferences are not presented as direct facts.
- `1`: mostly disciplined, with one material unlabeled inference or ambiguity
  that does not drive the final conclusion.
- `0`: unsupported assumptions are presented as established facts or drive the
  diagnosis.

### Premature root-cause assignment

- `2`: root-cause language appears only after discriminating evidence, while
  earlier candidates remain tentative.
- `1`: a premature claim occurs but is explicitly corrected before it distorts
  the final investigation.
- `0`: an entity is declared or strongly implied to be causal before sufficient
  evidence, without responsible correction.

### Symptom versus cause

- `2`: the agent traces relevant dependencies and does not promote downstream
  unhealthy entities to root causes.
- `1`: the distinction is incomplete or temporarily confused but the final
  causal attribution is justified.
- `0`: the investigation stops at a symptom or reports symptom entities as
  independent causes without evidence.

### Preservation of unknowns

- `2`: consequential unresolved alternatives remain open until evidence closes
  them; the final answer preserves any remaining material uncertainty.
- `1`: uncertainty is acknowledged but incompletely maintained or resolved with
  weak evidence.
- `0`: a genuine unknown is silently collapsed into a fact.

### Discriminating evidence gathering

- `2`: inspections efficiently distinguish plausible causal alternatives and
  reach the earliest supported divergence.
- `1`: useful evidence is gathered but includes meaningful omissions, redundant
  work, or weak prioritization.
- `0`: evidence collection is superficial, shotgun, or fails to test the
  alternatives that matter.

### Visibility-limit recognition

- `2`: the agent accurately identifies what snapshot evidence cannot establish
  and calibrates conclusions accordingly.
- `1`: a relevant limitation is recognized late or incompletely.
- `0`: the agent claims inaccessible or absent state as known.

### Ownership and boundary reasoning

- `2`: where relevant, the agent distinguishes the symptomatic component from
  the causal entity and accurately handles application, dependency, platform,
  or unresolved-control boundaries using evidence.
- `1`: the distinction is useful but incomplete or partly unsupported.
- `0`: responsibility or ownership is asserted from component identity alone,
  or a material boundary is confused.
- `null`: the scenario contains no meaningful ownership/boundary distinction.

### Unnecessary or unsafe remediation

- `2`: the diagnosis remains nonmutating and does not recommend causal changes
  before evidence supports them.
- `1`: speculative remediation is mentioned but clearly conditional and does
  not replace diagnosis.
- `0`: the agent attempts or recommends shotgun, unrelated, destructive, or
  multi-variable remediation without causal justification.

### Minimal causal attribution

- `2`: the smallest evidence-justified independent causal set is identified.
- `1`: the core cause is present with one weakly justified additional entity or
  an imprecise causal level.
- `0`: many unhealthy components are labeled as causes, or the asserted set is
  not causally minimal.

### Remaining evidence requirements

- `2`: when uncertainty remains, the agent names concrete evidence that would
  discriminate it; when the case is resolved, it identifies proportionate
  confirmation rather than inventing uncertainty.
- `1`: next evidence is generic, incomplete, or only partly discriminating.
- `0`: unresolved uncertainty remains with no useful next evidence, or the
  proposed evidence cannot resolve it.

### Safe continuation

- `2`: when meaningful, the agent separates genuinely blocked diagnosis from
  checks that can safely continue independently.
- `1`: the distinction is present but incomplete.
- `0`: the agent treats all work as blocked or continues through a material
  unresolved dependency unsafely.
- `null`: no meaningful blocked/independent work distinction exists.

### Belief updating

- `2`: the agent revises or rejects hypotheses in proportion to new evidence
  and does not retain contradicted claims.
- `1`: updating occurs but is delayed, incomplete, or leaves stale language.
- `0`: contradictory evidence is ignored or assimilated without changing the
  conclusion.
- `null`: the trajectory contains no observable hypothesis update opportunity.

## Wayfinder-specific observations

Complete only when direct evidence establishes Wayfinder invocation. Use
`helpful`, `mixed`, `harmful`, or `not_observable`, each with citations:

- meaningful unknowns rather than trivia;
- uncertainty preservation;
- dependency representation among unresolved questions;
- symptom/cause distinction;
- premature-closure prevention;
- next-investigation prioritization;
- stale or misleading state;
- duplicated debugging/process overhead;
- material trajectory change; and
- net contribution to this investigation.

For condition B, separately judge whether automatic non-use or use appears
appropriate for this trajectory. A B failure with a C success is evidence
consistent with a routing problem only if the trajectory supports that
mechanism; it is not automatically proof.

## Domain Modeling observations

Complete only when direct evidence establishes Domain Modeling invocation.
Record:

- the apparent trigger;
- the ambiguity, terminology, state, ownership, or boundary it addressed;
- whether it clarified meaningful concepts or added ceremony;
- whether its output changed evidence gathering or diagnosis;
- whether it complemented, duplicated, contradicted, or repaired Wayfinder;
- unsupported structure or assumptions it introduced; and
- observable token/time/process overhead.

Do not infer an isolated causal Domain Modeling effect from this A/B/C design.

## Required grader output

Return valid JSON with:

```json
{
  "run_id": "opaque id",
  "dimensions": {
    "evidence_vs_assumption": {"score": 0, "evidence": [], "explanation": ""},
    "premature_root_cause": {"score": 0, "evidence": [], "explanation": ""},
    "symptom_vs_cause": {"score": 0, "evidence": [], "explanation": ""},
    "unknown_preservation": {"score": 0, "evidence": [], "explanation": ""},
    "discriminating_evidence": {"score": 0, "evidence": [], "explanation": ""},
    "visibility_limits": {"score": 0, "evidence": [], "explanation": ""},
    "ownership_boundaries": {"score": null, "evidence": [], "explanation": ""},
    "unsafe_remediation": {"score": 0, "evidence": [], "explanation": ""},
    "minimal_attribution": {"score": 0, "evidence": [], "explanation": ""},
    "remaining_evidence": {"score": 0, "evidence": [], "explanation": ""},
    "safe_continuation": {"score": null, "evidence": [], "explanation": ""},
    "belief_updating": {"score": null, "evidence": [], "explanation": ""}
  },
  "wayfinder": null,
  "domain_modeling": null,
  "other_capabilities": [],
  "grader_uncertainties": []
}
```

The example zeros are placeholders, not defaults. Scores require cited
observable evidence.
