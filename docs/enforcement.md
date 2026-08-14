# Lifecycle enforcement and hard-rule audit

## Purpose and result

Agentic Workflow historically expressed routing and completion guarantees only
as model instructions. This design adds a small deterministic boundary for facts
a host can observe without moving semantic workflow judgment into code. GitHub
Copilot in VS Code is the reference host; Codex is a strong secondary target,
Claude Code is a compatibility target, and Copilot CLI/cloud are separate
runtimes.

The successful outcome is not “unbypassable policy.” It is a narrower and
truthful contract: supported hooks reject inconsistent lifecycle transitions;
instructions continue to govern when hooks are unavailable; lifecycle `status`
states the actual guarantee.

## Common semantic contract

The shared controller recognizes these host-neutral transitions:

1. `checkpoint`: a model-selected route, authorization boundary, provider set,
   and verification requirement exist before substantive tool use.
2. `action`: the model classifies the next opaque operation without the
   controller parsing arbitrary shell or MCP semantics.
3. `provider`: an actual provider execution must enter `started` before it can
   end as `executed`; `started` is rejected when installation, prerequisites, or
   host policy make execution impossible. A selected optional provider does not
   block host-native tools or completion when no provider execution is claimed.
4. `durable`: the current `active.md` digest and any conflicting dominant
   workflow are validated before the native write.
5. `evidence` or `limitation`: required verification has an observed successful
   tool reference or an explicitly authorized limitation before completion.

The model owns route selection, action meaning, verification relevance, and
evidence sufficiency. The controller owns enum/schema validity, transition
order, host/provider compatibility, authorization consistency, native write
denial, state-digest freshness, evidence-to-observed-tool linkage, and bounded
Stop behavior.

```text
                   Agentic Workflow
                  shared policy/core
                         |
                shared controller
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
    VS Code Copilot     Codex       Claude Code
       adapter          adapter        adapter
      reference       optional        optional
```

## Host capability research

Research was refreshed from primary documentation on 2026-08-14.

| Host | Current lifecycle surface | Enforcement consequence |
|---|---|---|
| GitHub Copilot in VS Code | Workspace `.github/hooks/*.json`; PascalCase `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop`; structured JSON; PreToolUse allow/ask/deny; Stop continuation. `SessionStart` can inject model context, but `UserPromptSubmit` has common user-facing output only. The feature is **Preview**, may be organization-disabled, and does not run in an untrusted workspace. | Active reference adapter at `.github/hooks/agentic-workflow.json`. It auto-approves only strictly parsed controller declarations and enforces observable gates, but remains `partial/Preview`, never a hard adoption prerequisite. |
| OpenAI Codex | Project `.codex/hooks.json` or config; trust is recorded against the hook definition; `UserPromptSubmit` can inject context; broad local tool coverage, but hosted and specialized paths can be uncovered. PreToolUse can deny and Stop can continue; permission approval is a separate event. | Shared controller supplies fresh prompt guidance and core wire decisions. The template is opt-in because `.codex/hooks.json` may be user-owned and commands can start below the repository root. |
| Claude Code | Project `.claude/settings.json`; `UserPromptSubmit` can inject context; PreToolUse can allow/ask/deny, while managed deny/ask rules still win; commands run with user permissions. Interactive trust and noninteractive `-p`/SDK behavior differ. | Shared controller supplies fresh prompt guidance and auto-approves strictly parsed declarations. The template is opt-in; fixed settings ownership and noninteractive trust require deliberate integration. Current provider skills remain unavailable because there is no `.claude/skills` projection. |
| GitHub Copilot CLI | Version-1 `.github/hooks/*.json`; both lower-camel native and PascalCase VS Code-compatible payloads; local command runtime and failure behavior differ from VS Code. | The versioned reference file is structurally discoverable, but live CLI enforcement is not release-validated or claimed. Instruction fallback remains. |
| GitHub Copilot cloud agent | Discovers the repository hook file in an ephemeral Linux sandbox; event/runtime subset, restricted environment, and no interactive user approval. | The shared file may run, but cloud enforcement is not inferred from VS Code validation or claimed by this release. Instruction fallback remains. |

Primary references:

- [VS Code agent hooks (Preview)](https://code.visualstudio.com/docs/agent-customization/hooks)
- [VS Code hooks wire reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference)
- [VS Code agent trust and safety](https://code.visualstudio.com/docs/agents/security)
- [Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)

## Hard-rule audit

The audit searched root policy, local skills, state/profile contracts, provider
declaration, lifecycle scripts, tests, and source documentation for normative
terms including `must`, `required`, `always`, `never`, `before execution`, and
`before completion`. The table groups every behavioral rule family by the layer
that can truthfully own it. Source-repository maintenance rules remain in the
source `AGENTS.md`; they are not installed into consuming projects.

| Behavioral rule family | Classification | Authoritative implementation | Duplicate or supporting expression |
|---|---|---|---|
| Evaluate every request through routing before substantive execution | Programmatic invariant where hooks run; model contract elsewhere | Controller checkpoint gate | Root policy, routing docs, route scenarios |
| Choose the minimum useful route; direct work stays direct | Model contract | Root router | Routing docs and local skill entry criteria |
| Honor explicitly named skills and compose only useful capabilities | Model contract | Root router/provider skill discovery | Routing docs, provider declaration |
| Keep selection, invocation, authorization, and execution distinct | Programmatic transition plus model contract | Provider start/outcome gate validates installation, prerequisites, declared host policy, and explicit user-only invocation | Root policy, provider schema, provider verifier |
| Report missing/incompatible providers truthfully; use host-native fallback unless explicitly required | Programmatic execution-claim invariant plus model fallback contract | Provider lifecycle and controller provider transition | Root policy and architecture docs |
| Run setup only after a selected workflow needs missing configuration | Model contract with programmatic provider/prerequisite schema | Router plus provider declaration | Root policy, package skill, readiness output |
| Provider instructions never expand user authority | Programmatic authorization consistency for native/declared actions; model contract for semantics | Controller authorization checkpoint and host sandbox | Root policy and every local workflow |
| Diagnosis/review/read-only does not authorize a repository write | Programmatic invariant for native writes and declared opaque actions | Controller PreToolUse gate | Debugging skill, root policy, acceptance scenarios |
| Exact external read authorization does not authorize broad search or mutation | Model contract; declared action gate where hooks run | Controller requires an opaque-action classification | Root policy and workflow skills |
| Inspect and explicitly resolve conflicting durable workflow state | Programmatic invariant for native `active.md` edits | Digest-bound durable transition grant | State contract and all durable local workflows |
| Preserve provider-native identifiers and canonical artifacts; create no shadows | Model contract | State and routing contracts | Root policy and architecture docs |
| Allocate stable local IDs without overwrite and preserve questionable history | Model contract | State contract | Local workflow skills and templates |
| Decide verification relevance before completion | Programmatic invariant after observed repository writes; model judgment for relevance | Checkpoint/Stop gate | Root policy and Verification skill |
| Do not claim required verification without evidence or an accepted limitation | Programmatic transition plus model sufficiency judgment | Evidence-to-observed-tool link and Stop gate | Verification skill and acceptance scenarios |
| Never invent project commands; separate passed, failed, skipped, blocked, unavailable | Model contract | Verification workflow | Profile contract and root policy |
| Keep the project profile soft, evidence-backed, and non-blocking | Filesystem-safety and readability classification only | Lifecycle readiness/profile classifier | Root policy and profile contract/template |
| Keep any emitted route marker truthful and informational | Optional observability contract | Root route-visibility guidance | Route scenarios and package verifier; VS Code Stop has no documented final-message field |
| Install/update/remove only authenticated, owned, clean paths | Programmatic invariant | `adopt.py`, `providers.py`, distribution and target manifests | Package skill, architecture, lifecycle tests |
| Preserve uncommitted/user-owned content and fail closed on conflicts | Programmatic invariant | Transaction preflight, rollback, ownership hashes | Source/installed policy and lifecycle tests |
| Pin provider version and validate required provenance while protecting local edits | Programmatic invariant | Provider verifier and local ownership hashes | Provider declaration/research docs |
| Require supported Python and portable filesystem behavior | Programmatic invariant | Every executable entry point and package verifier | README, package skill, ADR 0008 |
| Keep observability optional, read-only, metadata-first, and content-free | Programmatic boundary plus model contract | Leaf analyzer/package checks | Observability docs and source policy |
| Keep upstream `implement` ownership of TDD/review; avoid repeated stages | Model contract | Root router/implementation adapter | Routing and architecture docs |
| Discovery gathers evidence before durable decisions | Model contract | Discovery skill | Decision template/state contract |
| Debugging separates reproduction, diagnosis, and fix authorization | Model contract plus native-write denial in diagnosis mode | Debugging skill and controller | Root policy and scenarios |
| Implementation checks readiness/authority and hands off truthfully | Model contract plus provider outcome gate | Implementation adapter/controller | Provider declaration and scenarios |
| Verification checks acceptance/integration without duplicating provider internals | Model contract plus completion gate | Verification skill/controller | Root policy and verification docs |
| Source changes update implementation, tests, docs, decisions, and release evidence together | Source-repository model contract | Source `AGENTS.md` and release gate | This audit and ADR 0009 |

The intentional duplication left after this change is reinforcement at a public
boundary: a compact root instruction, detailed owner document, machine check,
and acceptance scenario may describe the same invariant. Detailed methodology
is not copied into the root policy or controller.

## Instruction placement

The installed root policy is the always-loaded orchestration kernel. It owns
only routing existence, authorization non-expansion, truthful execution claims,
host/provider separation, preservation of user/canonical work, and
evidence-grounded completion, plus minimum-process defaults and progressive
loading pointers.

Conditional detail has one installed owner:

- `.ai-workflow/routing.md`: classification ladder, provider invocation/setup,
  host availability fallback, composition, authorization examples, evidence
  semantics, and route-marker labels;
- `.ai-workflow/runtime/README.md` and `capabilities.json`: controller protocol,
  host lifecycle surfaces, deterministic guarantees, and degradation;
- `.ai-workflow/contracts/durable-state.md`: durable conflicts, identifiers, pointers,
  re-entry, and transitions;
- `.ai-workflow/contracts/project-profile.md`: optional lazy profile creation,
  precedence, commands, safety metadata, and maintenance; and
- selected workflow/provider skills: specialized methodology, including
  Implementation-owned TDD/Code Review composition and Verification procedure.

This placement keeps hooks-off behavior safe: the root still supplies the
universal semantic boundaries and directs every non-obvious route to the full
installed routing contract. It does not duplicate controller state mechanics or
load provider methodology for confidently direct work.

## State and privacy

Transient controller state lives under the operating system temporary directory,
partitioned by a per-user namespace and hashes of project path, host, and session
identity. The controller finds the installation by walking upward from the hook
working directory. State contains only enum values, compact labels, timestamps,
and hashes. It does not contain prompts, tool arguments/results, source, or
credentials, and it is removed after a successful Stop gate. It is orchestration
evidence, not canonical project state and not a tamper-resistant audit log.

Durable state remains `.ai-workflow-state/active.md` and provider-native
artifacts. The controller does not create a second durable workflow model.

## Security and trust boundary

- The active hook is executable repository content. VS Code requires workspace
  trust and may be organization-disabled; Codex separately reviews exact hook
  hashes. Claude interactive trust differs from `-p`/SDK, and Copilot cloud can
  execute repository hooks noninteractively in its sandbox. Review hooks before
  trusting a clone.
- The hook file supplies no environment variables and the controller does not
  read credentials. Cloud-provided tokens remain host-owned and are not copied
  into state.
- Controller declarations are parsed as an exact Python/script argv. Newlines,
  shell control/expansion syntax, alternate controller paths, ambiguous command
  fields, unknown trailing arguments, invalid enums, and unsafe compact labels
  are rejected; arbitrary shell text is never interpreted as policy.
- Provider prerequisites, installed skill files, active state, and transient
  state reject path traversal and symlinked components. Native tool path text is
  normalized for Windows separators before protected-path checks.
- Hook commands run from the host-selected project working directory. The
  controller writes only to its bounded OS-temporary state path; repository
  mutation remains the invoked tool's responsibility and the host sandbox is
  still the outer boundary.
- Hook/controller files are ordinary repository bytes. Lifecycle manifests
  detect changes and native writes to them are blocked, but local actors and
  opaque commands can tamper with them. This is a guardrail, not a privilege or
  tamper-resistance boundary.

## Failure and fallback model

- A policy denial returns structured hook output with exit code zero. The VS Code
  adapter returns `allow` only for an exact framework declaration already
  applied to transient state; all requested calls retain normal host approval
  behavior, and a more restrictive hook or managed rule still wins.
- A malformed controller transition stops processing with a concise diagnostic.
- Stop blocks once. If the host reports `stop_hook_active`, or a second Stop
  arrives for the same failure, the controller returns a terminating failure
  instead of continuing indefinitely.
- If hooks are absent, disabled, unsupported, untrusted, or bypassed, routing and
  workflow skills continue instruction-first. `status` reports the downgraded
  capability separately from package integrity.
- Direct native edits to the installed controller or active VS Code hook are
  denied. Transactional package update is the supported replacement path.

## Known limitations

Hooks are guardrails, not a security boundary. An opaque command can be
misclassified by the model, tools outside a host hook path are invisible, and a
successful PostToolUse event cannot prove semantic test success. A provider
must pass a validated `started` transition before substantive work and before
`executed` can be recorded, but the host exposes no provider-skill lifecycle
event that proves the body ran. Repository
actors can tamper with local files or temporary state. The active VS Code API is
Preview and can change. If a host supplies neither a session ID nor a transcript
path, concurrent sessions in the same project share the conservative fallback
state key. These constraints are why the common contract is small, the fallback
remains complete, and lifecycle status says `partial` rather than `enforced`.

The VS Code transport still costs a compact model tool call because the host has
no native semantic declaration channel. It should no longer produce a routine
approval prompt, but the declaration can remain visible in tool history. A
managed host rule or another hook can legitimately require approval or deny it.
