# Controlled live synthetic findings

Eighteen fresh-session reviews completed: three conditions × three synthetic
scenarios × two repetitions. Every run used gpt-5.4, high reasoning, an
ephemeral session, a read-only sandbox, the same common/scenario prompt, and a
temporary workspace containing only the constructed fixture plus the exact
condition instructions. Full final reviews and compact metrics are under
`../runs/`.

The rubric was written before these runs. Grading was not blinded, and no
synthetic overall score is used.

## Scenario A — genuinely overengineered architecture

All six runs reached the discriminating result: preserve
`QuoteApplication.execute` and its behavioral tests while consolidating the
normalizer/calculator/domain-service/use-case chain.

- Direct identified the pass-through calls and redundant request packaging in
  both repetitions.
- Vanilla used deletion, depth, in-process dependency, and adapter-count
  language to justify the same result.
- Guarded reached the same result and did not rationalize the shallow layers
  through its new preservation checks.

Result: positive for all conditions; no observable decision-quality advantage
for vanilla or guarded over direct. The guard did not blunt the skill's
strongest use case.

Evidence: `../runs/direct/scenario-a-r1.md`,
`../runs/direct/scenario-a-r2.md`,
`../runs/vanilla/scenario-a-r1.md`,
`../runs/vanilla/scenario-a-r2.md`,
`../runs/guarded/scenario-a-r1.md`, and
`../runs/guarded/scenario-a-r2.md`.

## Scenario B — legitimate modular architecture

All six runs preserved `ApprovalPolicy`, `StockLedger`, and `CheckoutPlanner`.
All respected Approval Policy, Stock Ledger, and Checkout Plan as canonical
project/domain language. No condition introduced ports, protocols, replacement
wrappers, or an in-process mega-module.

This directly fails to reproduce the audit's highest-risk prediction: both
vanilla repetitions balanced the absolute “in-process ... merge” wording
against locality, deletion-test, ownership, and README evidence and kept the
legitimate seams.

One direct repetition uniquely found a plausible mixed-domain result issue:
`CheckoutPlan.explanation_code` carries both compliance codes and fulfillment
statuses. The other five runs focused on preserving boundaries and improving
tests/harness setup. Because this appeared once, it is useful evidence of a
possible specialist-attention trade-off, not a stable condition effect.

Result: positive and stable preservation in all conditions; feared vanilla
module merging and terminology replacement were not reproduced.

Evidence: `../runs/direct/scenario-b-r1.md`,
`../runs/direct/scenario-b-r2.md`,
`../runs/vanilla/scenario-b-r1.md`,
`../runs/vanilla/scenario-b-r2.md`,
`../runs/guarded/scenario-b-r1.md`, and
`../runs/guarded/scenario-b-r2.md`.

## Scenario C — testing trap

All six runs preserved the focused parser tests and the high-level engine
tests. All recognized `parse_rules` as an independently meaningful behavior
surface used by checkout and authoring validation. No run merged the parser
into the engine or replaced parser edge-case tests with checkout-only tests.

The broad blanket-deletion concern therefore was not reproduced. A narrower
problem was reproduced:

- both vanilla repetitions recommended replacing the validator's exact error
  propagation assertion with a looser adapter-shape assertion;
- one guarded repetition made the same recommendation;
- both direct repetitions and the other guarded repetition kept all existing
  tests.

The existing validator assertion is useful: it verifies that the authoring
interface preserves the precise parser error that the fixture README calls
user-visible. A looser non-empty-string assertion loses that regression signal,
even though parser-level coverage remains. The guarded text did not reliably
eliminate this pressure (one of two repetitions), so it is not proven better.

Result: core test preservation is positive for every condition. Vanilla shows
a stable narrower tendency to weaken a valuable adapter-level assertion;
guarded is unstable; direct is strongest on preserving all existing coverage.

Evidence: `../runs/direct/scenario-c-r1.md`,
`../runs/direct/scenario-c-r2.md`,
`../runs/vanilla/scenario-c-r1.md`,
`../runs/vanilla/scenario-c-r2.md`,
`../runs/guarded/scenario-c-r1.md`, and
`../runs/guarded/scenario-c-r2.md`.

## Run-to-run stability

- A: stable recommendation in all six runs; minor differences about retaining
  a private value object/helper.
- B: stable boundary/terminology preservation; secondary recommendations varied
  between direct tests, packaging setup, no change, and one mixed-domain result
  finding.
- C: stable production seam and parser-test preservation. Validator-test advice
  was stable within vanilla, stable within direct, and unstable within guarded.

No run invoked Design It Twice or sub-agents because the common prompt forbade
sub-agent use for every condition. These trials therefore evaluate whether the
skill recommends expansion, not the quality/cost of its multi-agent process.

## Secondary measurements

Means across six runs per condition:

| Condition | Elapsed seconds | Input tokens | Output tokens | Reasoning tokens | Tool calls |
|---|---:|---:|---:|---:|---:|
| Direct | 87.0 | 91,762.8 | 4,414.5 | 1,960.5 | 16.2 |
| Vanilla | 116.7 | 139,942.2 | 5,890.3 | 2,843.8 | 21.3 |
| Guarded | 93.7 | 119,844.0 | 4,729.3 | 1,779.8 | 19.5 |

Vanilla was slower and produced more output and tool calls than direct in every
matched scenario/repetition. Input usage varied widely and includes cached
context plus inspected file/tool output, so these measurements are secondary
and should not be generalized from six runs. The local CLI also emitted cache
and state-database warnings that did not prevent outputs.

## Practical conclusion

Vanilla behaved substantially better than its most dangerous literal wording
suggested: it simplified A, preserved B, and preserved C's lower-level parser
tests. However, direct reasoning made the same primary decisions with lower
observed cost, and vanilla consistently weakened one useful validator test.
The evidence therefore supports keeping Codebase Design available for explicit,
concrete architecture/interface/seam problems, but does not support invoking it
more frequently or broadly favoring it inside Wayfinder.

The guarded candidate preserved A and B and reduced average cost relative to
vanilla, but it did not reliably fix the C behavior and showed no primary
decision-quality gain. Do not adopt it from this experiment.
