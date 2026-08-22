# Basic Phase 2 VS Code Wayfinder smoke

## Purpose

This is the smallest live gate for host behavior that deterministic tests cannot
establish: whether VS Code General actually invokes the model-invocable focused
Wayfinder agent after the portable router selects Wayfinder, and whether clear
negative cases remain outside it.

Run all six cases in fresh VS Code chats with **General** selected as the parent
agent. Use the same model, reasoning setting, permissions, and VS Code/Copilot
version throughout. If Auto resolves to a visible model, record it. Do not use an
old conversation, paste prior-case commentary, or enable additional custom
agents. Prepare a fresh disposable workspace for every case.

The decisive invocation evidence is the VS Code subagent UI or tool trace naming
the workspace `Wayfinder` agent. A route marker, a final claim, or General reading
`.agents/skills/wayfinder/SKILL.md` inline is not proof that the focused agent ran.
Agent Debug telemetry is optional and not required.

## Workspace setup

From the source repository root, create a unique temporary copy for each case.
Replace `<case>` and `<fixture>` for each case below:

```bash
case_root="$(mktemp -d "/tmp/agentic-workflow-basic-phase2.<case>.XXXXXX")"
cp -R skills/agentic-workflow/tests/fixtures/<fixture> "$case_root/workspace"
python3 skills/agentic-workflow/scripts/adopt.py install "$case_root/workspace"
printf '%s\n' "$case_root/workspace"
```

Open only the printed `workspace` directory in VS Code. Never reuse a prior
case's temporary directory. Record the initial
`git diff --no-index` or file snapshot if the fixture is not a Git repository;
the relevant evidence is the post-run file diff, not repository history.

## Autonomous live-host practice

Automate this protocol through the real VS Code host when the local environment
supports it. Do not substitute another agent CLI for the acceptance boundary.
Keep the automation disposable and prefer a small shell/Python observer over a
new repository test framework.

Before opening test workspaces:

1. record the source branch, exact commit, and initial `git status`;
2. run `code --version` and `code chat --help`;
3. confirm Copilot Chat, Agent mode, the workspace `Wayfinder` agent, model
   invocation, and agent hooks are available; and
4. prepare one isolated workspace and one fresh chat per case. Install passive
   observer files before taking the disposable workspace's baseline so they do
   not appear as product mutations.

The first opening of a disposable workspace can raise **Trust Folder &
Continue**, **Trust Authors**, memory-read approval, or **Allow in This
Session** prompts. These are environment gates, not product failures. Never
click or bypass them with brittle GUI automation. If a person must act, notify
them immediately with the exact VS Code window and control, pause only the
affected case, and confirm when the prompt is cleared. Do not wait silently.

`code chat -r` targets the active/reused VS Code window, not a workspace path.
Before every submission, confirm the intended disposable workspace is the
active window. Use `code --status`, the visible title/path, and the subsequent
hook session root as cross-checks. If a prompt lands in another case, exclude
that session, record the protocol deviation and any contamination, and rerun in
a new chat in the correct workspace. Never reinterpret a mistargeted run as the
intended case.

Use passive workspace hooks for `SessionStart`, `SubagentStart`,
`SubagentStop`, and `Stop`; add `PreToolUse` only when needed to distinguish
parent work before and after focused execution. Record at least timestamp,
session ID, agent ID, agent type, event, and tool name when the event exposes
them. The primary positive evidence is a documented `SubagentStart` whose
`agent_type` is exactly `Wayfinder`; negative cases require its absence. Count
parent tool calls between `SubagentStop` and `Stop` when evaluating duplicate
investigation. Transcript content and final self-report are supporting evidence,
not substitutes for hooks and filesystem/state assertions.

After a state-writing case, inspect the actual diff and validate semantic
contracts, including the allowed child statuses:

- unknown: `open | resolved`;
- fact: `current | disputed | stale`; and
- decision: `accepted | superseded`.

Also verify that focused Wayfinder exclusively owned framework state mutation,
authority-owned choices remain unresolved, and no competing continuity store
or implementation artifact appeared. A valid `SubagentStart` does not make an
invalid state diff pass.

VS Code's local chat-session artifacts may expose the resolved model, root
prompt/context tokens, root completion tokens, elapsed time, credits, and a
subagent credit value. They may omit separate subagent prompt/completion tokens.
Use `N/O` for unavailable fields, do not estimate them, and do not add root and
subagent values unless the host documents that they are disjoint. Treat these
artifacts as secondary and version-specific.

When the requested rerun combines existing cases but the repository has no
canonical combined prompt, preserve the individual case semantics, record the
exact synthesized prompt, and label comparisons as directional rather than
exact. Do not silently promote the synthesized prompt into a replacement case.

After capturing evidence, close only the VS Code windows proven to belong to
the disposable workspaces, then remove the exact temporary roots. Verify that
pre-existing/source windows remain open, the original repository has no
unexpected changes, observer files and mutation locks are absent, and
`git diff --check` still passes. If the bounded correction's stop-loss fires,
stop testing or redesign work as directed; do not grow the observer into
orchestration machinery.

## A. Explicit plumbing

- Fixture: `wayfinder-existing`
- Case directory: `a-explicit-plumbing`
- Exact prompt:

> Invoke the workspace Wayfinder custom agent as a subagent. Have it inspect the named current coordination effort, report its destination, the strongest established fact, the most important unresolved uncertainty, and the next safe boundary. Do not change any files. After it returns, summarize its answer without repeating the investigation.

Expected:

- General visibly invokes the `Wayfinder` custom agent.
- The focused agent executes in its own child context and performs the inspection.
- No files change.
- General summarizes the returned result and does not reread most of the same
  files after the child completes.

## B. Automatic positive selection

- Fixture: `focused-wayfinder-stale-truth`
- Case directory: `b-automatic-positive`
- Exact prompt:

> Reconcile this deployment-mode coordination work for continuation across sessions. Current source may conflict with the accepted state, several downstream areas depend on the result, and an authority review may still be required. Establish what is current, preserve the unresolved boundary, and expose the next safe work. Do not implement downstream changes.

Expected:

- The prompt does not name Wayfinder, but General visibly invokes the focused
  `Wayfinder` agent.
- The focused agent reconciles only the relevant effort, treats current source
  as stronger than stale state, and preserves the authority boundary.
- No competing durable coordination store is created.
- General does not repeat most of the child investigation.

## C. Negative Direct and unrelated state

- Fixture: `wayfinder-unrelated`
- Case directory: `c-negative-direct`
- Exact prompt:

> What exact string does `greeting()` currently return? Explain only; do not change files.

Expected:

- General answers Directly.
- It does not invoke the focused Wayfinder agent or load the unrelated
  database-migration effort.
- No files change.

## D. Negative specialist

- Fixture: `verification-failure`
- Case directory: `d-negative-debugging`
- Exact prompt:

> Diagnose why `python verify.py` fails in this repository. Identify the supported cause and remaining uncertainty, but do not fix anything or create durable planning state.

Expected:

- General uses the existing Debugging methodology or an equivalent bounded
  diagnosis, not the focused Wayfinder agent.
- No Wayfinder state or other files are created or changed.

## E. Durable-state ownership

- Fixture: `wayfinder-new`
- Case directory: `e-state-ownership`
- Exact prompt:

> Coordinate this migration so different owners can continue it across several sessions. Preserve the consequential unknowns, accepted evidence, dependencies, blockers, and one coherent next boundary. Do not implement the migration or publish implementation tickets.

Expected:

- General automatically invokes the focused Wayfinder agent.
- The focused agent is the observable owner of all framework Wayfinder-state
  mutation under one relevant effort.
- General does not independently create another map, notes tree, or competing
  framework coordination state before or after the child run.
- The resulting diff contains only the expected coordination state and no
  implementation work.

## F. Human authority

- Fixture: `decision-only`
- Case directory: `f-human-authority`
- Exact prompt:

> Coordinate the persistence work for continuation across owners and sessions. The durable backend and operating owner have not been chosen, those choices belong to project authority, and independent work may proceed only where it does not cross that boundary. Surface the concrete question, why that authority is required, and what its answer will unblock. Do not assume an answer or publish implementation work.

Expected:

- General automatically invokes the focused Wayfinder agent.
- The focused agent records or returns the authority-owned uncertainty and asks
  the concrete backend/owner question.
- It creates no accepted decision, specification, ticket, or implementation
  direction that manufactures the answer.
- General surfaces the question without resolving it on the user's behalf.

## Minimal evidence to return

For each case, return only:

1. case letter and exact prompt confirmation;
2. parent agent and selected model/settings as shown;
3. screenshot or copied UI/tool event proving whether `Wayfinder` executed;
4. final response;
5. concise post-run file diff or “no changes” result;
6. whether General reread/repeated most of the focused investigation after the
   child returned; and
7. visible elapsed time, token, tool, or credit data if the host exposes it,
   otherwise `not available`.

Record contamination, permission changes, retries, model changes, or protocol
deviations. Do not infer missing telemetry.

## Acceptance

The live gate passes only when A proves the explicit child plumbing, B proves
neutral automatic positive selection, C and D stay outside Wayfinder, E shows
one durable-state owner, F preserves human authority, and no case shows severe
duplicate investigation. One ordinary negative case is insufficient if the
automatic positive case never executes.
