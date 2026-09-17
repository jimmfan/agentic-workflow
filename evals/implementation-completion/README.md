# Implementation completion controls

These controls use a fictional photo-processing application.
An earlier image-export configuration provides a fallback while a new export engine remains unfinished.
No live model evaluations or sandbox experiments are part of this work.

## Test boundaries

[Export continuity tests](../../tests/test_export_continuity.py) exercise four [scenarios](../../tests/scenarios/photo-export-primary.toml) against local synthetic configuration snapshots.
The primary request specifies a useful fallback without asking for tracking.
Controls preserve an existing effort when purpose is ambiguous, the work is unrelated, or the request is read-only.
The exact-version assertion rejects the different latest snapshot, altered bytes and symlink substitution.
Blind prompts keep grading expectations out of the evaluated request.
Strict read-only requests do not require a report-file write and reject changes even in the harness evidence directory.

[Export completion tests](../../tests/test_export_completion.py) generate historical Git commits in disposable repositories, restore the earlier configuration and leave an existing plan unchanged outside the implementation diff.
Ordinary repository references and project policy establish the plan's relevance.
The tests check three boundaries separately:

| Boundary | Observable requirement |
|---|---|
| Review detection | Identify the concrete unmet requirement or stale claim, governing source, affected artifact and practical consequence within the requested review scope. |
| Handoff | Return the finding, relevant reference, consequence and actual coverage to the coordinating agent. |
| Completion | Reuse adequate verification, check saved recovery information, and reconcile authorized consequential state before claiming completion. |

Already-sufficient content requires no rewrite or repeated review.
Unrelated work remains unchanged, review-only work performs no writes, and an explicitly excluded obligation is reported as a coverage limit.
No particular route label, additional effort or supporting ledger is required.

## Evidence limits

The controls execute local Git and filesystem operations and evaluate constructed answers and verification records.
They do not observe an agent selecting an effort, conducting independent review, invoking acceptance verification or recovering context in a fresh session.
Text predicates discriminate the supplied examples; they are not a general semantic grader.
Exact configuration bytes establish local preservation, not a successful photo export.
A user's report of a working configuration, an independently checked image, a saved file, a commit and publication establish different claims.

Behavioral improvement remains INCONCLUSIVE without suitable live evidence.
A future bounded evaluation must use a verified execution boundary and inspect actual reviewer inputs, reads, findings, coordinator actions and saved content.
Readers should receive only saved project artifacts and no grading rubric or original conversation.
No earlier run is evidence for these fixtures.

See [findings and validation](REPORT.md) and [compact results](results.json).
