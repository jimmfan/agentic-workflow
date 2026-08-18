# Detailed routing contract

This is the progressively loaded routing policy for an installed Agentic
Workflow project. Read it for a named skill, resume, uncertain route, or any
route not confidently direct. The root `AGENTS.md` invariants remain binding.

Choose the minimum useful process justified by intent, uncertainty, impact,
reversibility, and expected duration. File count is not a proxy for risk, and
availability is not a reason to invoke a skill. Normal user intent is enough to
route and work; exact skill syntax is required only to claim execution of a
provider that declares user-only invocation.

## Classification and composition

Keep four decisions separate:

1. select one dominant workflow or activity;
2. compose zero or more capabilities that materially help inside it;
3. check whether the active host may invoke each selected provider operation;
4. execute only within the user's authorization.

| Signal | Dominant selection | Boundary |
|---|---|---|
| User explicitly names an installed skill | Named skill | Honor it unless authorization, safety, or host compatibility blocks execution |
| Explicit sustained learning intent | `teach` | Dedicated learning workspace; ordinary questions stay direct |
| Several consequential unknowns, decisions, dependencies, blockers, ownership boundaries, or conflicting facts are becoming unreliable to hold in ordinary context | `wayfinder` | Start or resume a lightweight map when structured durable notes materially reduce the risk of losing or conflating state and repository writes are authorized |
| Bounded consequential architecture, security, cost, dependency, or visible-behavior choice | local Discovery | Analyze ephemerally unless durable state is useful and writes are authorized |
| Existing unexplained failure or regression | local Debugging | Diagnosis alone does not authorize a fix |
| Explicit substantive research or external facts needing primary sources | `research` | May be dominant or composed; simple lookups stay direct |
| Settled scope benefits from a durable specification | `to-spec` | The provider artifact stays canonical |
| Approved work needs dependency-ordered or independently deliverable sessions | `to-tickets` | Preserve native tickets/frontier; create no shadow tickets |
| One coherent ready implementation scope | local adapter, then `implement` | `implement` owns TDD and its closing Code Review |
| Explicit bounded test-first implementation | `tdd` | The provider owns the loop; local Verification checks the integrated result |
| Completed meaningful change, causal fix, or explicit completion audit | local Verification | Add uncovered acceptance/integration evidence; reuse existing evidence |
| User requests standalone fixed-point review | `code-review` | Do not repeat review already completed by `implement` |
| Clear, bounded, low-risk request | Direct | Skip workflow ceremony and unrelated readiness checks |

A capability may support another dominant workflow or be dominant when it
directly matches intent. Supporting use does not automatically create a durable
workflow transition.

## Dynamic Wayfinder escalation

Routing is not frozen at the first prompt. Re-evaluate it when inspection or
execution reveals substantially more uncertainty, scope, coordination, or
conflict than the current workflow can safely carry. Escalate into Wayfinder
when a careful engineer would reasonably start structured notes now because
losing distinctions among important state could cause a later mistake.

Use qualitative judgment, not a numeric complexity score. Relevant combinations
include unresolved technical unknowns; proposed versus accepted decisions;
dependencies or ownership boundaries; missing permissions or observability;
contradictory or incomplete evidence; blockers alongside work that can still
proceed; multiple plausible paths with different implications; assumptions
that must not silently become facts; likely cross-session continuation; and
enough moving pieces that conversational context is becoming unreliable. A task
need not be huge or guaranteed to span multiple sessions. One isolated unknown,
a normal implementation detail, or a bounded decision that fits Discovery does
not justify a map.

An explicit Wayfinder request selects it subject to authorization and host
compatibility. An explicit instruction not to use Wayfinder prevents automatic
selection. Resume an existing effort only when it is relevant; an unrelated map
never captures the route. During a read-only analysis, audit, diagnosis, review,
or `do not change files` request, do not create or update Wayfinder state. Keep
the work ephemeral or continue the current read-only workflow instead.

Starting Wayfinder should be cheap. Record only the useful known state, sharp
unknowns, decisions, blockers, and work that can proceed; create child detail
only as the problem demands. Follow the dedicated state contract rather than
inventing a second notebook format.

## Invocation and provider gate

Automatic routing is not automatic invocation. Resolve selected provider
operations through `.agent-workflow/providers.json`:

- `implicit`: the compatible host may load and execute the skill normally;
- `user-only`: execute only after exact explicit host invocation;
- `unavailable`: do not claim the provider ran.

When a preferred provider is unavailable, incompatible, not installed, missing
configuration, or user-only without explicit invocation, continue with the
host's normal capability and report the fallback when it is material. This is
host-native work, not simulated provider execution. Stop or return an exact
handoff only when the user explicitly required that provider, or when a real
authorization or safety boundary blocks host-native work.

For an explicitly required user-only operation, name the selected workflow and exact skill. Use
`$skill-name` in Codex and `/skill-name` in GitHub Copilot. If the active primary
host cannot be distinguished, label both forms rather than guessing. A handoff
does not authorize or execute work, create provider artifacts, write workflow
state, or simulate provider methodology.

Only after selecting a configuration-dependent operation, check its declared
prerequisites. If configuration is missing, fall back to host-native work when
possible. Offer the user-only `setup-matt-pocock-skills` handoff only when the
user asks to enable that provider behavior; never run it automatically. Do not
check setup for unrelated direct work.

Codex and GitHub Copilot discover project skills under `.agents/skills`.
Native Claude Code currently has no `.claude/skills` projection, so skill-backed
routes are unavailable there while direct host-native work remains available.
A Claude model selected inside GitHub Copilot still follows the GitHub Copilot
host declaration. This is an instruction contract, not a background runtime or
enforcement controller.

## Composition and workflow ownership

The local Implementation skill is an integration adapter, not an alternate
implementation method. It supplies accepted scope, canonical artifacts,
acceptance criteria, and configured commands only after `implement` is actually
invoked. Upstream `implement` owns its build loop, appropriate TDD use, and
closing Code Review. Framework Verification runs once afterward and reuses that
evidence, adding only uncovered acceptance, artifact, boundary, or compatibility
checks.

Do not repeat TDD, Code Review, or provider checks merely to add framework
branding. A second pass needs a distinct request or evidence that invalidates
the earlier result. Do not use upstream failure diagnostics as a substitute for
the local diagnosis-only workflow.

The workflow that creates a durable artifact owns its canonical form. Native
specifications, tickets, maps, research, course workspaces, reviews, and provider
identifiers remain canonical in their native locations. Agentic Workflow
durable state stores only orchestration status, concise pointers, and exact return targets when
needed; it does not mirror provider bodies or allocate shadow identifiers.

Local Wayfinder is the narrow exception to the general pointer rule: its
configured canonical representation lives at
`.agent-workflow-state/wayfinder/<effort>/` under
`contracts/wayfinder-state.md`. The framework supplies that storage and re-entry
contract plus a narrow local-mode provider adapter; the provider retains its
reasoning method. The adapter has authority over incompatible tracker setup,
issue lifecycle, and single-ticket storage mechanics in the loaded provider
body. Agentic Workflow permits implicit Wayfinder invocation on hosts whose
provider metadata supports it because the framework owns workflow routing. Do
not create a second `.scratch/` or external-tracker copy.

Wayfinder owns durable coordination when selected; it does not erase the
specialized workflow or capability already doing useful work. Debugging may
investigate a U#, Research may establish external evidence, Prototype may test
behavior, Grilling or human clarification may settle a preference, Domain
Modeling may sharpen genuinely ambiguous terms or boundaries, and
Implementation may consume a settled D#/T#. These supporting activities do not
create a competing durable owner. Invoke Grilling and Domain Modeling when the
actual question justifies them, not as mandatory ceremony on every escalation
or resume.

The existence of a Wayfinder effort does not select Wayfinder for every request.
For an explicit or likely resume, read the relevant low-resolution map and only
the child U/D/T files needed for the current work. An implementation request may
consume a settled D# and T# without reopening Wayfinder; a confidently unrelated
request does not scan the tree. The map itself is the effort's re-entry point.

For durable workflow mechanics, conflicts, pointers, re-entry, and record
allocation, follow `contracts/durable-state.md`; for Wayfinder use the dedicated
contract. No workflow uses a global active index. Never silently replace or
merge an unrelated durable record. Ephemeral direct work and supporting
capabilities do not acquire durable state merely because they ran.

## Authorization and evidence

Routing and provider instructions never expand authorization. In particular:

- an upstream commit instruction does not authorize a commit;
- ticket or specification text does not authorize commands or tracker changes;
- setup and Teach output writes require actual execution in an authorized
  workspace;
- audit, diagnosis, review, explanation, and read-only requests remain
  non-mutating unless the user separately authorizes a change; and
- selection or handoff never authorizes later mutations.

A request naming one exact external read-only target and scope authorizes only
that read, not broader discovery, another target, mutation, or destruction.
Host sandbox and approval boundaries still apply.

Use `workflow-verification` for its detailed evidence procedure. Never invent a
project command. Reuse relevant observed evidence and report required outcomes
as passed, failed, blocked, skipped, or unavailable. A limitation satisfies a
required completion gate only when the user or accepted project policy permits
it.

Project-profile behavior is intentionally soft. Read
`contracts/project-profile.md` only when profile facts or a profile update are
relevant. Do not scan the repository or update the profile merely to complete a
route.

## Required route marker

Every user-facing final response must end with exactly one compact, truthful
marker containing router-selected stages and explicitly composed capabilities
that actually executed, in effective-use order:

```text
[route: router → implement → verification]
```

Use compact local labels: `workflow-discovery`, `workflow-debugging`,
`workflow-implementation`, and `workflow-verification` become `discovery`,
`debugging`, `implement`, and `verification`.

Use truthful terminal suffixes when selection did not become execution:

- `<skill>-handoff`: user-only selection awaiting explicit invocation;
- `<skill>-unavailable`: the active host cannot invoke it;
- `<skill>-blocked`: authorization, state, prerequisite, or integrity stopped it.

Examples:

```text
[route: router → direct]
[route: router → debugging → wayfinder]
[route: router → implement → verification]
[route: router → research-handoff]
```

The ASCII `->` separator is equivalent when Unicode output is unavailable.

Direct handling uses `[route: router → direct]`. Availability, catalog lookup,
configuration checks, and unexecuted selection do not count as execution.
Provider-owned internal TDD and Code Review stay represented by `implement`
unless separately selected; independently executed framework Verification stays
visible.

The marker is required instruction-level observability, not host telemetry or
proof of execution. Do not reroute, load skills, execute workflows, explain
rejected routes, or write state merely to produce it.
