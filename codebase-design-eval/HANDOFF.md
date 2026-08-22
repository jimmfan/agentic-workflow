# Codebase Design evaluation handoff

## 1. Baseline

- Main commit: `b722b0b1eba1bcdf52a818e06279082edbcb978d`
- Codebase Design: `mattpocock/skills` v1.2.3, skill tree
  `20b7cd1dd1fe5b0bd37ba72649f3a29375574b5b`; exact file hashes are in
  `results.json`.
- Review branch: `review/codebase-design-eval`
- Synthetic settings: codex-cli 0.144.6, gpt-5.4, high reasoning,
  fresh/ephemeral session, read-only sandbox, user config ignored, two
  repetitions per condition/scenario.
- Synthetic isolation: each hosted workspace contained only one constructed
  fixture plus the exact condition instructions—no Agentic Workflow source,
  root `AGENTS.md`, project documentation, or Scenario D content.
- Material limitations: grading was fixed-rubric but unblinded; no sampling
  seed; fixtures are small; Design It Twice was not exercised because the
  common prompt prohibited sub-agents; CLI cache/state warnings may affect time.
  Scenario D is qualitative because exact repository-payload approval for
  separate hosted sessions was rejected.

## 2. Independent skill assessment

Strongest ideas: depth as caller leverage, locality, the deletion test, broad
interface obligations, explicit seam placement, and behavior-oriented tests.

Highest-risk wording: mandatory glossary replacement; “in-process” means always
merge; lower-level tests become waste after interface tests; exactly one
interface per module; and automatic 3+ agent Design It Twice expansion.

Unexpected result: vanilla behaved more safely than its literal absolutes. It
preserved B's modules/terms and C's focused parser tests in both repetitions.
The observed weakness was narrower: both vanilla C runs recommended loosening a
useful validator exact-error assertion.

## 3. Test design

- A: five-layer in-process quote path. Discriminates real simplification from
  sophisticated-sounding preservation.
- B: three in-process modules with distinct owners, domain terms, invariants,
  and release cadences. Discriminates technical mergeability from legitimate
  architecture.
- C: high-level campaign tests plus focused parser/validator edge-case tests.
  Discriminates behavioral testing from blanket lower-level deletion.
- D: real Agentic Workflow routing/provider/Wayfinder baseline. Qualitative
  only; discriminates evidence-backed review from vocabulary-driven rewriting.

All fixture tests pass. Eighteen controlled synthetic runs completed (A/B/C ×
direct/vanilla/guarded × two repetitions). Raw transcripts and temporary
workspaces were discarded; final reviews and compact metrics are retained.

## 4. Results

### A — General/direct

Direct made the correct primary decision in all six runs: consolidate A,
preserve B, and preserve C's production seams and every existing test. One B
run uniquely found a plausible mixed-domain `explanation_code` issue.

### B — Vanilla Codebase Design

Vanilla also made the correct primary decision in all six runs. It did not
merge B, rename B's canonical terms, delete C's parser tests, or invent ports.
Both C runs did recommend replacing the validator's exact error-propagation
assertion with looser adapter-shape coverage, losing a useful user-visible
regression signal.

Vanilla averaged 116.7 seconds, 5,890 output tokens, and 21.3 tool calls versus
direct's 87.0 seconds, 4,415 output tokens, and 16.2 calls. Treat cost as
secondary, but vanilla was slower and more verbose in every matched run.

### C — Guarded Codebase Design

Guarded retained the correct A/B/C primary outcomes and did not blunt A's
simplification. It did not reliably fix C: one run weakened the validator test
and one preserved it. It showed no decision-quality advantage over vanilla or
direct, so the candidate is not supported for adoption.

Run-to-run instability was low for A's target architecture and B's boundary
decision. Secondary recommendations varied. C's validator-test advice was
stable within direct and vanilla but split across guarded repetitions.

Scenario D found no material rewrite qualitatively: `lifecycle.py` owns a real
orchestration/failure seam, `providers.py` is already deep behind a small CLI,
and the explicit Wayfinder adapter should not become a generic framework before
a second use case.

## 5. What the evidence supports

Clearly supported:

- Vanilla's deletion/leverage language is useful on genuinely shallow code.
- Vanilla performed safely on the legitimate-module and parser-test traps.
- Direct matched every primary outcome at lower observed cost.
- Vanilla consistently weakened one useful adapter-level test; guarded did not
  reliably repair it.

Not reproduced:

- merging legitimate in-process modules;
- canonical terminology replacement;
- deletion of focused parser tests;
- gratuitous ports, adapters, or production rewrites.

Unresolved: behavior on larger/ambiguous repositories, whether Codebase Design
ever changes a primary decision for the better versus strong direct reasoning,
Design It Twice outcome/cost, and fresh-session Scenario D behavior.

## 6. Wayfinder implications

Do not broadly favor Codebase Design or automatically add it to Wayfinder's
specialist dispatch. Keep it available for explicit, concrete
module-interface/seam/deepening intent.

Future selective use would need positive evidence such as repeated pass-through
layers, duplicated caller knowledge, callers coordinating internals, or a
consequential open seam-placement decision where review could actually shrink
Wayfinder territory. Avoid it when seams follow domain/ownership/trust/lifecycle/
deployment/failure distinctions; during routine implementation, debugging, or
research; or when no structural pain is observed.

No new general root routing cue is justified; the existing skill description is
already sufficient for explicit architecture intent.

## 7. Recommendation

Keep vanilla at its current narrow explicit-intent availability, but do not
promote it to more frequent use or automatic Wayfinder composition. Do not
adopt the guarded candidate: the live evidence did not establish an outcome
advantage or a reliable fix.

The next useful experiment is a genuinely ambiguous interface decision. Run
Scenario D live only after explicit authorization for the exact repository
payload and hosted destination.

## 8. Files worth reviewing

- `codebase-design-eval/results.json`
- `codebase-design-eval/analysis/live-synthetic-findings.md`
- `codebase-design-eval/analysis/skill-audit.md`
- `codebase-design-eval/analysis/repository-scenario-d.md`
- `codebase-design-eval/candidate-codebase-design/SKILL.md`
- `codebase-design-eval/runs/vanilla/scenario-c-r1.md`
- `codebase-design-eval/runs/guarded/scenario-c-r2.md`
- `codebase-design-eval/PROTOCOL.md`
