# U3: Does Agentic Workflow create net value on long-lived engineering work?

- Status: open
- Resolution mode: prototype
- Blocked by: U1, U2, T2
- Related: D1, D2, D3, D4

## Question

Across uncertainty, decision changes, interruptions, and fresh-agent continuation, does Agentic Workflow produce a repeatable improvement over a capable baseline after accounting for safety, useful progress, correctness, verification, rework, artifacts, and model cost/usage?

## Evidence

- The initial spike was mixed and preliminary: both Direct variants passed; Resume suggested workflow safe-stop value but baseline also preserved continuity.
- The context-confounded three-paired campaign is directional only for Resume because every task had potential exposure and one run was confirmed contaminated.
- The context-isolated Resume campaign is the current primary narrow Resume evidence. It found workflow safe stopping at 2/3 versus baseline 1/3, but AMI recovery and completion at workflow 0/3 versus baseline 3/3. This is evidence of no continuity advantage in that fixture and a possible evidence-precedence/over-conservatism failure mode, not a general product conclusion.
- Execution cost and token use were unavailable or unreliable in the current manual boundary, and sample sizes are not statistically conclusive.

## Resolution

Keep open until harder, isolated, multi-phase comparisons yield repeatable distributions across the distinct D2 behavior layers. Any final conclusion must state its task domain and uncertainty rather than generalizing beyond observed fixtures.
