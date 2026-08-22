# Guarded candidate rationale and falsification attempt

The candidate is the vanilla method with guards at the demonstrated conflict
points; it is not a new architecture framework.

## Smallest substantive changes

- Project/domain vocabulary outranks the skill glossary.
- In-process means technically mergeable, not architecturally required to
  merge.
- Adapter count becomes evidence rather than a verdict.
- Interface tests become the primary surface rather than the only legitimate
  surface; deletion requires coverage and diagnostic equivalence.
- Distinct caller interfaces and legitimate side effects are acknowledged.
- Design It Twice gains a consequence/uncertainty/authorization gate and no
  longer requires automatic 3+ agent fan-out.
- Refactoring, renaming, compatibility changes, and test deletion remain inside
  project scope and authority.

## Same-scenario application

### A — falsification target: does guarding blunt useful simplification?

No fixture fact justifies the inner quote layers. The guarded deletion test
still shows that removing the normalizer, calculator wrapper, domain service,
and use case eliminates navigation and constructor wiring without erasing an
owner, domain, trust, lifecycle, or failure boundary. It reaches the same
minimal target as vanilla. The guard therefore does not defeat the strongest
known vanilla use case.

### B — legitimate modules

The candidate preserves Approval Policy, Stock Ledger, and Checkout Plan because
the README gives concrete ownership, domain, release-cadence, invariant, and
audit-language evidence. It may still simplify incidental parameters or wiring,
but technical co-location no longer decides the architecture.

### C — testing trap

The candidate keeps high-level engine tests, parser edge-case tests, and the
validator behavior test. The parser has two callers and concentrated grammar
hazards. No higher-level suite currently supplies equivalent coverage or
diagnostics, so the explicit deletion gate is not met.

### D — Agentic Workflow

The candidate treats `scripts/lifecycle.py` as a small but justified
orchestration surface because it preserves independent core/provider failure
semantics. It recognizes `scripts/providers.py` as already deep behind a small
CLI and does not invent a generic adapter architecture before a second use case.
It preserves router, workflow, provider, and boundary as project terms.

## Attempt to disprove improvement

The guards add instruction length and more reasons to preserve a module. That
can cause conservative false negatives: a reviewer may accept a weak boundary
after hearing an unverified ownership claim, or spend extra time enumerating
exceptions. The candidate therefore requires concrete evidence, not a list of
hypothetical reasons, and retains the original deletion/leverage tests.

## Post-run result

The controlled synthetic runs did not justify adoption. Guarded preserved the
correct Scenario A and B outcomes in both repetitions, but vanilla already did
the same. In Scenario C, one guarded repetition still recommended weakening the
validator's exact error-propagation assertion while the other preserved it;
both vanilla repetitions recommended weakening it and both direct repetitions
kept it.

Guarded used less elapsed time and fewer output/reasoning tokens on average than
vanilla, but these secondary measurements were variable and the candidate did
not improve primary decision quality. Treat it as an evaluation artifact, not a
production recommendation.
