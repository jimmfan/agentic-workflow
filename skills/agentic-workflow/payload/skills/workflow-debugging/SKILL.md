---
name: workflow-debugging
description: Diagnose an existing unexplained failure through an evidence-driven feedback loop and falsifiable hypotheses. Use for an observable failure, regression, or performance symptom whose cause is unknown; distinguish diagnosis from a separately authorized fix.
---

# Systematic debugging workflow

Find the cause before choosing the fix. The first plausible theory is a
hypothesis, not a diagnosis.

When resuming from `ai-workflow/state/active.md`, require
`Active workflow: debugging`, validate its evidence record, and continue with
the stored hypothesis or diagnostic at `Resume target`.

## Establish the investigation

1. Define expected behavior, observed behavior, impact, onset, frequency, and
   the last known good state.
2. Read the project profile's domain-specific system model and diagnostics, if
   present. The core workflow supplies no technology commands.
3. Fix the mutation boundary before gathering evidence. For diagnosis-only or
   other nonmutating scope, do not create a record, edit instrumentation, write
   diagnostic artifacts, or run a mutating check. Use existing evidence and
   read-only observations; if a mutation becomes necessary, pause and request
   separate authorization.
4. Create a `DBG-NNNN` work record when an authorized investigation must persist
   across chats.
5. Gather the smallest relevant evidence while redacting secrets and sensitive
   output. Record commands actually run and their baseline results.

## Establish the feedback signal

Prefer one safe, repeatable observation that detects the user's exact symptom
and can distinguish before from after. When feasible, reproduce it and minimize
inputs, steps, components, and timing until every remaining element is relevant.
Tighten determinism and speed without substituting a nearby failure.

A fast local red command is not mandatory. Infrastructure, cloud, intermittent,
or externally observed failures may require a bounded log signature, metric,
trace, captured request, state comparison, or approved live check. Name the best
available proxy, its limitations, and what access or evidence would improve it.
If no responsible signal exists, stop with the evidence needed next rather than
forming an unsupported theory.

## Narrow and test

1. Map the layers through which the failing behavior travels and locate the
   earliest divergence.
2. Form 3–5 ranked, falsifiable hypotheses when the evidence permits. For each,
   state confirming and refuting evidence plus the safest discriminating test.
3. When mutation is authorized, instrument only boundaries that distinguish a
   named hypothesis. Tag temporary instrumentation uniquely, change one variable
   at a time, and avoid broad logging that increases sensitive-data exposure.
   Nonmutating investigations use only existing instrumentation or read-only
   probes.
4. Run diagnostics only under the project command contract. Update rankings from
   observed results; do not stack speculative changes.
5. Identify the root cause, or bound the uncertainty and name the next most
   useful diagnostic step.

## Fix and verify

If the request is diagnosis-only, stop after reporting the evidence chain, root
cause or bounded uncertainty, rejected hypotheses, temporary-instrumentation
cleanup, and recommended next action. Do not edit, commit, or imply fix approval.

If the authorized scope includes a fix, turn the minimized reproducer into a
regression check only at a seam that exercises the real failure. When no correct
test seam exists, use the strongest honest validation path and record the gap.
Apply the smallest causal fix, remove all tagged instrumentation and throwaway
artifacts, then invoke Verification on the original symptom or proxy plus
proportionate regressions. A vanished symptom without causal evidence is a
mitigation, not a proven root cause. Use upstream `code-review` only when its
fixed-point Standards/Spec contract adds distinct value; do not duplicate a
review already performed by an upstream `implement` run.

Debugging is complete when cause or bounded uncertainty is supported by the
recorded signal, temporary diagnostics are cleaned up, and the next action is
explicit. An authorized fix additionally requires current Verification evidence
and disposition of any separately justified review findings.
