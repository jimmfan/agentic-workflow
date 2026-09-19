# Wayfinder representation experiment: retain Markdown

The historical experiment recommended retaining Markdown U/F/D ledgers and Markdown E# files without front matter.
It demonstrated no materially simpler safe editing or overall contract, and no live YAML writer or reader ran.
No prototype, parser dependency, representation change, or compatibility layer is adopted.

## Evidence and decision limits

The prototype's 23 deterministic controls demonstrated representability and selected validation failures, not agent compliance.
Explicit YAML keys helped structural lookup, but direct heading navigation was lost; reference repair, safe textual edits, semantic judgment, and concurrent-state checks remained necessary.
Parsing and serializing could drop comments or alter unrelated formatting; duplicate keys, scalar typing, indentation, and valid-looking truncated prose required care.
Markdown also has malformed-heading and fence failure modes, so this is a bounded tradeoff recommendation rather than proof of superior reliability.
A structured metadata consumer or demonstrated editing problem could justify reconsideration; an optional visualizer alone was not sufficient.
E# front matter is a separate question from U/F/D representation.

The frozen live protocol is `4bb2687cff1947ca7687f10f8110c19b3835fdb9`, based on `4327a838618fc1fbae8f75689dbfed87830360d7`.
Two model invocations completed: a native editing probe and the Markdown writer, using Codex CLI 0.144.6 and `gpt-5.6-sol` at medium reasoning.
The writer preserved required supplied facts, record identity, an unrelated unresolved question, and unrelated bytes.
It repaired invalid links introduced by the frozen runner.
Initial adjudication incorrectly inverted relative-path resolution and reported FAIL; independent Standards and Spec reviewers corrected all six saved map links to PASS.
The corrected runner was never exercised live, so this is not an unmodified current-main baseline.
Some added requirements were design inference beyond the source, and pre-pruning retrievability ordering was not established; overall contract compliance remained INCONCLUSIVE.

The first reader's non-model isolation check failed after relocating disposable files outside the source tree.
No reader prompt, credential copy, or model call followed; both YAML stages and the Markdown reader remained infrastructure-blocked and behaviorally INCONCLUSIVE.
The underlying isolation cause was not established, and no YAML token measurement or comparative savings claim exists.
Historical raw traces and disposable consumers were removed under that experiment's cleanup requirements, limiting later independent re-adjudication.

## Reproducibility

The [reviewed source tree](https://github.com/jimmfan/agentic-workflow/tree/d8bac5b546e1576ef43e8aed628f7ba8e91e709d/evals/wayfinder-yaml) retains the full report, frozen protocol, candidate, fixtures, compact results, and verification fingerprints.
The same commit retains the experimental validator, runner, tests, and dev-only PyYAML 6.0.3 lock inputs.
They can be inspected or recovered from the [verified experimental-history bundle](../wayfinder-persistence/preservation-followups.md#frozen-sources-and-recovery); they are not current evaluation tooling.
Recorded deterministic passes concern that branch's macOS/Python 3.11 environment, not hosted CI, current main, or YAML behavior.
The frozen fixture defect, corrected grade, unexecuted stages, and removed raw evidence must remain visible in any reuse.
No further live attempt is authorized by this result.
