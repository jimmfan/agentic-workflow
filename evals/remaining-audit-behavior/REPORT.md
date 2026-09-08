# Remaining behavior audit

The live campaign is in progress; no runtime source change is justified by the evidence collected so far.
The [protocol](README.md), [input fingerprints](inputs.json), and `tests/scenarios/audit-*.toml` define the bounded campaign against `1510e74540e3ebdb7c07966274fae7aeeac09386`.
Only evaluation inputs, controls, adapter and reporting are being changed.

The focused deterministic controls pass (10 tests), as do the existing behavior-harness controls (19 tests).
These establish fixture and evaluator behavior, not live skill selection or lifecycle compliance.
One isolated infrastructure probe successfully read, patched and reread a disposable file with the subject sandbox enabled.
The first source-grounded negative case completed with a correct source-scoped answer, Direct behavior and no Wayfinder state.
Remaining observations and independent closing reviews are pending.

The earlier map-authoring campaign remains infrastructure-blocked and behaviorally INCONCLUSIVE.
Its result is not changed by this campaign's successful host probe.
