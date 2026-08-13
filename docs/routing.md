# Routing policy

Choose the minimum workflow justified by intent, uncertainty, risk,
reversibility, and scope. Diff size is not a risk measure. After choosing the
workflow, separately choose who should execute each bounded part; Codex remains
the parent and default runtime.

## Workflow precedence

1. Honor an explicit request to learn or use a named workflow.
2. Resolve an explicitly identified knowledge gap that blocks safe progress with
   Teach.
3. Resolve a prerequisite decision gap with Discovery when materially different
   choices change architecture, security, cost, dependencies, or externally
   visible behavior.
4. Diagnose an existing unexplained failure before changing the system.
5. After specification approval, decompose only work that needs multiple
   dependency-ordered or independently deliverable sessions; otherwise proceed
   directly to Implementation.
6. Plan and build meaningful specified work, gather executable evidence with
   Verification, and independently Review meaningful changes when it adds
   confidence.
7. Handle clear, bounded, low-risk work directly.

If classification is uncertain but the action is low-risk and reversible, use
the lighter route and state the assumption. Do not infer lack of knowledge from
an advanced topic. A known error with complete causal evidence can be explained
directly; a live unexplained symptom requires Debugging.

An explicit resume request is resolved before this precedence: validate
`ai-workflow/state/active.md`, select the matching `workflow-*` skill, and
continue its exact `Resume target`. Missing, malformed, stale, or conflicting
state is reported and repaired only from repository evidence or user-confirmed
facts, never reconstructed from chat memory.

## Optional upstream capabilities and audited exclusions

The local Discovery and Teach skills are complete defaults. Upstream Wayfinder
and Teach are optional explicit-only capabilities, not silent router targets:

- Use an installed `/wayfinder` only when the user explicitly invokes it for a
  foggy effort too large for one session. Its tracker map is canonical; external
  tracker writes require authorization, and the local fallback mutates the
  repository. Keep only the origin and return target in framework state.
- Use an installed `/teach` only when the user explicitly invokes it for a
  multi-session learning project in a dedicated teaching workspace. Its course
  files are canonical; keep only the interrupted workflow and return target here.
- If either named skill is unavailable, say so and offer the corresponding local
  workflow. Never claim it ran or duplicate native artifacts in local records.

An installed upstream `/to-tickets` may be explicitly selected inside
Decomposition when its configured native issue tracker should own the tickets.
External reads and writes still follow the project authorization contract, and
framework state stores references and frontier status without copying issue
bodies. An installed upstream `/code-review` may be explicitly selected for its
committed fixed-point Standards/Spec review when that contract fits; parent
Review still covers correctness, security, validation gaps, and unintended scope.

Upstream `/to-spec` does not replace the project-owned canonical specification
transition. Upstream `/implement` does not replace Implementation and
Verification. The useful mechanics from `diagnosing-bugs` and `tdd` live inside
the existing Debugging and Implementation workflows, while
`writing-for-agents` remains authoring guidance rather than a route.

## Execution choice

| Executor | Use when | Do not use as |
|---|---|---|
| Parent Codex | Default for routing, repository exploration, planning, editing, debugging, commands, synthesis, and verification | A reason to add ceremony to a clear bounded task |
| Native Codex subagent | Bounded independent engineering analysis or review where context isolation or parallelism materially helps | A concurrent write-heavy editor or substitute for parent verification |
| Optional Hermes `research` | A substantial, separable external/general investigation whose concrete benefit exceeds handoff cost, after compatible status and explicit network-read authorization | A repository explorer/editor, required stage, provider fallback, or response to mere task complexity |
| Copilot portable subset | The same seven core workflows are being used in a current VS Code Copilot session | A claim of Codex-native sandbox, subagent, or Hermes-adapter equivalence |

The parent owns all accepted decisions, repository writes, command authorization,
and final verification. If a native subagent or Hermes result is incomplete, the
parent either verifies and completes the missing work itself or reports the gap;
it never relabels partial evidence as success.

## Hermes decision and fallback

Hermes has three conceptual capability levels:

- `disabled` is the default when Hermes is absent, unauthenticated,
  incompatible, or not justified. Continue in Codex when the requested outcome
  remains achievable; report only the optional investigation unavailable when it
  is genuinely essential.
- `research` is the only enabled v0.20.0 path. It is bounded external research
  using the exact audited `openai-codex` provider, dedicated profile, and adapter
  contract. It receives no repository tools and requires explicit authorization
  for network reads.
- `repo-read` is recognized but unavailable for the audited release. The adapter
  exits before runtime startup because Hermes cannot select and isolate Codex's
  `:read-only` profile end to end. Do not claim or simulate success.

Write-capable Hermes repository delegation is not part of the MVP. Prefer parent
Codex for ordinary repository exploration and a native Codex subagent for
bounded independent repository analysis.

Before a `research` call, the parent checks adapter status, refuses an already-set
`AI_ENGINEERING_WORKFLOW_CHAIN`, obtains network-read authorization, and creates
a schema-valid request with a precise objective, bounded scope, curated context,
known facts, constraints, prohibited actions, expected output, and evidence
requirements. Repository modification and external writes are false.

The adapter sets the chain marker to `codex>hermes`, starts Hermes outside the
repository, and prohibits Codex or further delegation in the child request. A
result must separate conclusions, evidence, sources, assumptions, uncertainty,
actions, and parent verification needs. Provider/version mismatch, recursion,
invalid output, a changed repository snapshot, or child failure is a failed
delegation. Parent Codex independently checks material claims and persists only
a concise accepted result when useful.

## State and learning precedence

When sources disagree, accepted repository decisions and durable state outrank
the validated active artifact, which outranks model memory, which outranks chat
recollection. Hermes memory is a convenience signal, not project state.

Hermes-private memory, learned skills, curator changes, and other
self-improvement artifacts stay in the dedicated profile. Learned skill writes
use profile-local approval where supported. Promoting a lesson into `AGENTS.md`,
`.agents/skills`, the project profile, a decision, or durable state is a separate
Codex-owned change requiring reusable evidence, duplication and staleness review,
the narrowest useful placement, an explicit diff, and normal verification.

Durable specifications remain project-owned documents at the location named in
the project profile; workflow records link instead of copying them. IDP
opportunities are supplemental records for meaningful recurring manual or
cross-team friction, never a routing stage or routine-task interruption.
For decomposed work, canonical local `TKT` records or native issues carry ticket
bodies and blockers; `IMP` state stores only links and the actionable frontier.

## Examples

| Request | Workflow | Executor | Reason |
|---|---|---|---|
| “Fix this typo in the setup paragraph.” | Direct | Parent Codex | Clear, bounded, low-risk |
| “Teach me how eventual consistency affects this retry design.” | Teach | Parent Codex | Explicit learning intent |
| “I understand both identity options; which should this service use?” | Discovery | Parent Codex | Consequential unresolved choice |
| “I cannot compare those identity options because I do not understand token exchange.” | Teach, then resume Discovery | Parent Codex | Knowledge is prerequisite to the pending decision |
| “The API started returning 500 and we do not know why.” | Debugging, then Verification and proportional Review after a causal fix | Parent Codex, optionally a bounded native subagent | Existing unexplained failure; independent log analysis might benefit from isolation |
| “Explain this documented validation error; here is the confirmed cause.” | Direct | Parent Codex | No investigation is needed |
| “Add the approved pagination behavior across the service and tests.” | Implementation, Verification, then proportional Review | Parent Codex | Meaningful, specified repository change that fits one coherent session |
| “Implement this approved migration over several dependency-ordered sessions.” | Decomposition, then one frontier ticket through Implementation, Verification, and Review | Parent Codex | Durable tickets and a work frontier are justified |
| “Change one production access-policy line.” | Discovery or Implementation with approval | Parent Codex | High impact despite one-line diff |
| “Compare the current official public guidance from four vendors; do not inspect or change this repository.” | Discovery or direct research, as context requires | Parent Codex by default; optional Hermes `research` only if handoff benefit is concrete | Substantial separable external investigation may justify the adapter |
| “Have Hermes inspect this repository read-only.” | No Hermes execution at v0.20.0 | Parent Codex or native Codex subagent | `repo-read` compatibility gate is unavailable |
| “Teach me the cache model, decide whether to add a cache, then implement if chosen.” | Teach -> Discovery -> Implementation -> Verification -> Review | Parent Codex | Explicit intent and prerequisites set the order |
| “Use installed Wayfinder to map this foggy year-long migration.” | Explicit upstream `/wayfinder` | Current host, if installed and authorized | Native map owns multi-session decisions; local Discovery is the fallback |
| “This same manual onboarding handoff has blocked three teams.” | Current workflow, then optionally record `IDP-NNNN` | Parent | Meaningful recurring platform friction; capture does not interrupt the task |

## Workflow outputs

- Discovery: a durable decision with facts, alternatives, rationale,
  consequences, status, and implementation handoff.
- Teach: a useful mental model, evidence of understanding when needed, and an
  exact return to the interrupted workflow.
- Decomposition: canonical independently completable tickets, acyclic blockers,
  and a validated actionable frontier without mirrored ticket bodies.
- Implementation: an explicit plan, scoped edits, a justified feedback loop,
  and Verification handoff.
- Debugging: an evidence chain, falsifiable hypotheses, root cause or remaining
  uncertainty, smallest authorized fix, and verification handoff.
- Verification: criterion-by-criterion observed evidence and honest gaps.
- Review: an independent, evidence-cited assessment of meaningful work with
  parent-confirmed dispositions; it does not replace executable Verification.
- Hermes delegation: a schema-valid bounded research result that the parent
  verifies, rejects, or records concisely; never an automatic policy change.
- IDP opportunity: an optional concise friction record, not a workflow or an
  automatic commitment to build platform functionality.

The 32 core workflow cases are in `tests/acceptance-scenarios.json`. The 30
Codex/Hermes integration cases are in
`tests/hermes-acceptance-scenarios.json`, and the explicit v0.20.0 `repo-read`
compatibility gate is in `tests/hermes-repo-read-scenarios.json`.
`scripts/verify_framework.py` validates catalog and artifact properties plus
adapter simulations. Manual Codex/Copilot behavior and live Hermes execution
remain separate evaluations; a static or simulated pass is not a live-runtime
claim.
