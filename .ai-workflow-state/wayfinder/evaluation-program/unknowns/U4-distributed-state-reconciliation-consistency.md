# U4: Distributed-state reconciliation consistency

- Status: open
- Resolution mode: prototype
- Blocked by: none
- Related: D1, D3, D4, T4

## Question

Does maintaining project truth across multiple Wayfinder map/U/D/T artifacts create enough synchronization or staleness risk to offset the benefits of the structure, and can normal Wayfinder reconciliation reliably keep those artifacts coherent?

## Evidence

- After ARC v2 completed, T3 correctly recorded the run as done and U2 contained the automatic-routing evidence, while the canonical map/frontier still described review and selection of a post-v2 campaign as future work.
- The mismatch did not erase v2 evidence, but it made the next executable evaluation ambiguous until the linked records were reread and reconciled together.
- This is dogfooding evidence that distributed durable state can itself become partially stale when only some linked map/U/D/T artifacts are reconciled after new evidence.
- T4 measured the single handoff at 1 file and 109/108/123 lines across Phases
  1/3/5, with 1 file reconciled each time. Explicit Wayfinder used 6/8/9 files
  and 166/239/289 lines, reconciling 6/4/6 files respectively.
- Wayfinder kept W1's partial supersession coherent across its linked artifacts,
  but Phase 5 dropped an earlier concern that alarm namespace, metric,
  dimensions, threshold, period, statistic, and evaluation window were absent.
  Its ready ticket then led Phase 6 to invent those values. The fixture's false
  readiness premise confounds attribution, so this is a risk observation, not
  proof of a product defect.
- Fresh Wayfinder implementation agents observed 20/21/24 files before first
  writes in Phases 2/4/6, versus 11/6/12 for the single handoff. These are
  directional reconstruction-cost observations from one trajectory.

## Resolution

Keep open. The program incident and T4 show real synchronization surface, while
T4 also shows that reconciliation can preserve selective W1 supersession across
nine files. Because W4 is confounded and one trajectory cannot establish
reliability, do not infer that multiple files are inherently harmful or that
normal reconciliation is sufficient. No further run is authorized pending
human review.
