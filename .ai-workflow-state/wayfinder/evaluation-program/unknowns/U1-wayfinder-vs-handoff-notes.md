# U1: Does structured Wayfinder state outperform ordinary handoff notes?

- Status: open
- Resolution mode: prototype
- Blocked by: T2
- Related: D2, D3

## Question

On genuinely long-lived work with uncertainty, changing decisions, and interrupted sessions, does the canonical Wayfinder map plus U#/D#/T# structure improve continuity, correctness, state evolution, or rework relative to telling an otherwise capable vanilla Codex agent to leave good repository-native handoff notes?

## Evidence

- The initial Resume spike showed that baseline could preserve the transient fact by writing it into Terraform; workflow did not demonstrate unique memory.
- In the clean Resume rerun, baseline recovered the AMI in 3/3 and workflow in 0/3, but workflow used explicit Wayfinder in 0/3. That result cannot answer this question.
- Repository documentation explicitly treats the current fixture as smaller than the threshold where routing policy normally selects Wayfinder.
- The clean `arc-wayfinder-e2e-v1` smoke pair directly compared strong generic handoff notes with explicit Wayfinder across four fresh phases. Wayfinder recovered and implemented the exact deleted-source SSM fact; baseline preserved the literal in Phase 1 but did not consume it in Phase 2. Wayfinder was faster and used fewer recorded tokens in this pair, but read more state files and repeated more paths.
- Both arms evolved state safely after D1 and neither completed the expected Phase 4 slice. The Wayfinder trajectory made its own U2/U3 questions blockers for T2 and then made no Phase 4 code change. The frozen grader also misclassified some explicit unresolved/prohibited Phase 1 text, so v1 supports hypotheses rather than resolution.
- The corrected `arc-wayfinder-e2e-v2` smoke found no outcome advantage for
  structured state: vanilla durable notes, neutral Agentic Workflow, and
  explicit Wayfinder all preserved/consumed the exact fact and completed every
  phase-4 component with zero speculative rework. Vanilla used the least
  recorded time, tokens, tools, and reconstruction reads. Neutral Agentic
  Workflow selected Wayfinder automatically, so v2 does not cleanly identify
  the incremental effect of explicit invocation; the frozen semantic classifier
  also retains material known limitations.

## Resolution

Keep open. Preserve v1 and v2. Before repetitions or the full four-arm T2
campaign, repair treatment separation and semantic grading in a new
preregistered campaign. Resolve only from matched, repeatable evidence that
controls persistence instructions while varying the representation.
