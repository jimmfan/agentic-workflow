---
name: workflow-debugging
description: Diagnose an existing unexplained failure through an evidence-driven feedback loop and falsifiable hypotheses. Use for an observable failure, regression, or performance symptom whose cause is unknown; distinguish diagnosis from a separately authorized fix.
---

# Systematic debugging workflow

Find the cause before choosing the fix. Debugging owns causal investigation,
not durable continuity. Run it standalone when the work fits the current
session. Use Wayfinder when consequential investigation must survive a handoff;
resume from its map without creating a DBG or specialist notebook.

## Establish the investigation

1. Define expected and observed behavior, impact, onset, frequency, and last
   known good state.
2. Read relevant project diagnostics and system context. Read
   `.wayfinder/project-profile.md` only when its debugging model,
   verified facts, pointers, or commands materially inform the investigation.
   Before running a recorded command, read
   `.agent-workflow/contracts/project-profile.md` and apply its safety gate. The
   workflow supplies no technology-specific commands.
3. Fix the mutation boundary. Diagnosis-only work uses existing evidence and
   read-only observations; request authorization before adding instrumentation
   or running a mutating check.
4. Gather the smallest useful evidence. Redact secrets and record commands and
   baseline results actually observed.

## Establish the feedback signal

Prefer one safe, repeatable observation that detects the reported symptom and
distinguishes before from after. Minimize the reproducer when feasible without
substituting a nearby failure.

Infrastructure, intermittent, or external failures may instead need a bounded
log signature, metric, trace, captured request, state comparison, or approved
live check. State the proxy's limitations. If no responsible signal exists,
stop with the evidence needed next.

## Narrow and test

1. Map the path of the failing behavior and locate the earliest divergence.
2. Form 3–5 ranked, falsifiable hypotheses when evidence permits. For each,
   state confirming and refuting evidence plus the safest discriminating test.
3. Instrument only authorized boundaries that distinguish a named hypothesis.
   Tag temporary instrumentation, change one variable at a time, and avoid
   broad sensitive logging.
4. Run only configured project diagnostics and update rankings from observed
   results; do not stack speculative changes.
5. Identify the root cause or bound the uncertainty and name the next useful
   check.

## Fix and verify

For diagnosis-only work, report the evidence chain, root cause or bounded
uncertainty, rejected hypotheses, cleanup, and next action without editing or
implying fix approval.

When a fix is authorized, turn the minimized reproducer into a regression check
at the real failure seam when possible. Apply the smallest causal fix, remove
temporary diagnostics, and invoke Verification on the original symptom or
honest proxy plus proportionate regressions. A vanished symptom without causal
evidence is a mitigation, not a proven root cause. Do not duplicate Code Review
already performed by `implement`.

Inside Wayfinder, reconcile only consequential evidence, conclusions, blockers,
and next work; the map remains the durable owner.
