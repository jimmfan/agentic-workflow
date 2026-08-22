# U3: Does Agentic Workflow create net value on long-lived engineering work?

- Status: open
- Resolution mode: prototype
- Blocked by: U1, U2, T2
- Related: D1, D2, D3, D4, T4, U4

## Question

Across uncertainty, decision changes, interruptions, and fresh-agent continuation, does Agentic Workflow produce a repeatable improvement over a capable baseline after accounting for safety, useful progress, correctness, verification, rework, artifacts, and model cost/usage?

## Evidence

- The initial spike was mixed and preliminary: both Direct variants passed; Resume suggested workflow safe-stop value but baseline also preserved continuity.
- The context-confounded three-paired campaign is directional only for Resume because every task had potential exposure and one run was confirmed contaminated.
- The context-isolated Resume campaign is the current primary narrow Resume evidence. It found workflow safe stopping at 2/3 versus baseline 1/3, but AMI recovery and completion at workflow 0/3 versus baseline 3/3. This is evidence of no continuity advantage in that fixture and a possible evidence-precedence/over-conservatism failure mode, not a general product conclusion.
- Execution cost and token use were unavailable or unreliable in the current manual boundary, and sample sizes are not statistically conclusive.
- The isolated `arc-wayfinder-e2e-v2` smoke captured direct runtime usage for
  twelve fresh processes. All three conditions completed the same safe bounded
  outcome; vanilla durable handoff used 515.860 seconds and 1,004,891 input
  tokens, neutral Agentic Workflow used 751.057 seconds and 1,936,136 input
  tokens, and explicit Wayfinder used 621.984 seconds and 1,612,913 input
  tokens. These single trajectories show observable overhead without an outcome
  gain in this fixture, not a repeatable distribution. Neutral treatment
  crossover and semantic-grader defects prevent a general product conclusion.

- In the harder six-phase `arc-wayfinder-state-complexity-v1` trajectory,
  vanilla matched explicit Wayfinder on every valid continuity, blocker,
  state-evolution, safe-progress, W1 supersession, and verification dimension.
  Wayfinder used 1,336.394 versus 816.844 seconds, 3,086,063 versus 1,281,425
  input tokens, 85 versus 51 tool actions, and 127 versus 62 pre-write file
  observations. Its frozen Phase 6 completion advantage is confounded by an
  under-specified W4 fixture and incomplete acceptance check.

- The controlled `itbench-wayfinder-v1` campaign completed 54 bounded offline
  SRE diagnoses. It found no reliable correctness or reasoning gain for normal
  Agentic Workflow or explicit Wayfinder, while B used 58% more elapsed time
  and 42% more input tokens than vanilla and C used 43% more time and 51% more
  input tokens. Native entity matching has material ontology/condition defects,
  and these single-shot tasks did not exercise durable continuation, so this is
  repeatable bounded-task cost evidence rather than an answer about long-lived
  engineering work.

## Resolution

Keep open. T4 adds contrary single-trajectory evidence under harder state, and
T5 adds repeatable evidence of overhead without benefit on bounded incident
diagnosis, but neither resolves net value on long-lived work. No next run is
authorized. Any future conclusion must preserve campaign defects, state its
task domain and uncertainty, and account for observed overhead.
