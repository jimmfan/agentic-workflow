# EKS focused Wayfinder A/B protocol

## Purpose and stop boundary

Answer one causal question:

> Does a focused Wayfinder host projection improve Wayfinder behavior compared
> with a general-purpose agent using the same canonical Wayfinder methodology
> and state contract?

Both conditions explicitly use Wayfinder. The primary comparison does not test
whether the general router selects Wayfinder.

This is a manual live-host comparison. The current Codex environment cannot
execute and capture a real VS Code Copilot custom-agent session, so preparation
stops before either evaluated prompt is sent. Do not simulate condition B, alter
Agentic Workflow between runs, advance a learning exercise, or add Phase 2
workers.

## Frozen repositories

- Original EKS repository (read-only source):
  `/Users/james/Desktop/projects/learn-kubernetes`
- Frozen pre-install source snapshot:
  `/Users/james/Desktop/projects/wayfinder-eks-vscode-ab-20260821/source-snapshot`
- A — General Wayfinder:
  `/Users/james/Desktop/projects/wayfinder-eks-vscode-ab-20260821/A-general-wayfinder`
- B — Focused Wayfinder:
  `/Users/james/Desktop/projects/wayfinder-eks-vscode-ab-20260821/B-focused-wayfinder`
- Result export directories:
  `/Users/james/Desktop/projects/wayfinder-eks-vscode-ab-20260821/results/A`
  and `/Users/james/Desktop/projects/wayfinder-eks-vscode-ab-20260821/results/B`

The source snapshot preserves the original working directory, including its
modified tracked files and untracked learning material. It is not a clean clone
of `HEAD`.

Frozen identities:

| Item | Identity |
| --- | --- |
| EKS Git `HEAD` | `21b857766b74fddddd51029c34299e848a268cc6` |
| Pre-install working-file digest, excluding `.git` | `f3a33b851678720fee44255c49ff25086dd8c9879577725aad99ed591331b095` |
| Agentic Workflow branch | `wayfinder-replace` |
| Agentic Workflow revision | `1ac833d08640ff5eb5246355273c4105fb40e5bf` |
| Agentic Workflow package version | `0.19.1` |
| Pinned provider | `mattpocock/skills@v1.2.3` (`6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`) |
| A and B post-install working-file digest, excluding `.git` | `3632359279cace5afcd5daee629913a6468d0ee8acda4af1181821a08fb1c6a4` |

`diff -qr` found no A/B difference after installation. Agentic Workflow status
was healthy in both, all 14 provider skills were ready, and both
`.agent-workflow-state/` directories were empty.

## Conditions

Both repositories contain byte-identical Agentic Workflow configuration,
including `.github/agents/wayfinder.agent.md`, the canonical Wayfinder skill,
the Wayfinder state contract, the root router, and the VS Code hooks.

- A selects the built-in general `Agent` in a fresh VS Code Copilot session.
  The shared prompt explicitly requires it to use the installed canonical
  Wayfinder runtime and state contract without the focused host wrapper.
- B selects the workspace `Wayfinder` custom agent in a fresh VS Code Copilot
  session. The same shared prompt explicitly requires Wayfinder, and the custom
  agent is a thin host wrapper over the same canonical runtime and state
  contract.

No repository configuration differs. The treatment is the selected host agent
and therefore the focused projection's declared role/tool restriction. Canonical
Wayfinder selection is a controlled constant.

## Controlled settings

Use these values for both runs:

- Session target/harness: VS Code `Copilot`
- Model: `Terra 5.6` (`gpt-5.6-terra`)
- Thinking/reasoning effort: `Medium`
- Workspace trust: trusted
- Permission/approval level: the same label and behavior in both runs
- Prompt attachments or `#` mentions: none
- Conversation history: none; use a newly created chat
- Cross-device session history sync: disabled
- Local memory tool: disabled
- GitHub-hosted Copilot Memory: disabled for the account during both runs
- User/profile and organization customizations: excluded or disabled as below
- Execution order: sequential, without changing settings between runs

If the model, reasoning effort, prompt, workspace, selected agent, or permission
policy is wrong, do not repair the run in the same chat. Preserve the failed
evidence, mark the run invalid, and recreate that condition from the frozen
source snapshot before retrying.

## Exact prompt

Paste these four sentences exactly, with no prefix, suffix, file attachment, or
follow-up hint:

> Use Wayfinder to orient yourself in this repository and tell me where this project currently stands. It is an intentionally incomplete EKS/Terraform learning project. Determine what has actually been established so far, what important uncertainty remains, and what the most useful next boundary is. Do not implement the next exercise.

## Before running either condition

1. Create one temporary VS Code **Empty Profile** named, for example,
   `Wayfinder EKS A-B`. Do not copy settings, extensions, prompts,
   instructions, agents, skills, or Settings Sync content from the normal
   profile. Use this same temporary profile for A and B.
2. Sign the empty profile into the GitHub account needed for Copilot, but do not
   enable Settings Sync. If Copilot must be enabled or installed in the profile,
   do that before either run and leave the profile unchanged between runs.
3. In that profile's user settings, set:

   ```json
   {
     "chat.tools.memory.enabled": false,
     "chat.copilotMemory.enabled": false,
     "github.copilot.chat.organizationInstructions.enabled": false,
     "github.copilot.chat.organizationCustomAgents.enabled": false,
     "chat.useCustomizationsInParentRepositories": false,
     "chat.sessionSync.enabled": false,
     "github.copilot.chat.agentDebugLog.fileLogging.enabled": true
   }
   ```

   Do not clear or delete existing memories; disabling the relevant layers is
   enough for this experiment and preserves user-owned data.
4. In GitHub.com, open **Copilot settings**, find **Copilot Memory** under
   **Features**, and set it to **Disabled** for the duration of both runs. This
   prevents GitHub-hosted repository facts and user-level preferences from
   being applied by supported Copilot surfaces. Re-enable it afterward only if
   desired.
5. In VS Code, use Chat customization diagnostics to confirm that no user-level
   instruction, prompt, agent, skill, or organization customization is loaded.
   The EKS repository's own `AGENTS.md`, installed workspace skills, hooks, and
   B's workspace `Wayfinder` agent are intentional inputs and must remain.
6. Enable and retain
   `github.copilot.chat.agentDebugLog.fileLogging.enabled` so the Agent Debug Log
   can capture tool calls, token usage, errors, and duration.
7. Use a new VS Code window and open the condition directory itself as the
   workspace root. Do not open the original repository, the frozen source
   snapshot, or their common parent.
8. Keep the workspace local. Do not rebuild or reopen it in the devcontainer,
   because setup activity would add a condition-independent mutation and timing
   confound.
9. Confirm the workspace is trusted and the Copilot session target is selected.
10. Use the model picker to select `Terra 5.6`, open its Thinking Effort submenu,
   and select `Medium`. Confirm the input label shows the intended model and
   effort before sending the prompt.
11. Keep the same permission level for A and B. Record its displayed label.
12. Do not preload files, open evaluator material, attach context, or mention
   Wayfinder internals in the chat.

The Empty Profile and settings remove the documented local-memory and
user/organization-customization paths. The exported Agent Debug log is the
final audit: if its discovery events or system/context payloads show a memory,
personal preference, or non-workspace customization, qualify or invalidate the
affected run instead of assuming isolation.

## Run A — general Agent

1. Open
   `/Users/james/Desktop/projects/wayfinder-eks-vscode-ab-20260821/A-general-wayfinder`
   in a new VS Code window.
2. Create a new, empty Copilot chat.
3. Select the built-in general `Agent`, not `Wayfinder`, `Plan`, `Ask`, or
   another custom agent.
4. Reconfirm `Terra 5.6 · Medium` and the shared permission level. The exact
   prompt supplies the explicit Wayfinder invocation; do not add a slash
   command, attachment, or separate instruction.
5. Paste the exact prompt once and let the agent finish.
6. Approve only ordinary in-scope prompts required to continue, using the same
   policy intended for B. Do not answer substantive clarification questions or
   steer the response; record them as part of the result.
7. Do not ask for a correction, summary, or second attempt in that chat.

## Run B — focused Wayfinder

1. Close A's chat/window, then open
   `/Users/james/Desktop/projects/wayfinder-eks-vscode-ab-20260821/B-focused-wayfinder`
   in a new VS Code window.
2. Create a new, empty Copilot chat.
3. Select the workspace custom agent named `Wayfinder`. If it is absent, use
   `Chat: Open Customizations` or Chat diagnostics only to confirm whether
   `.github/agents/wayfinder.agent.md` loaded. Do not substitute another mode.
4. Reconfirm `Terra 5.6 · Medium` and the same permission level used for A.
5. Paste the exact prompt once and let the agent finish.
6. Apply the same approval and no-steering rules used for A.
7. Do not ask for a correction, summary, or second attempt in that chat.

## Capture after each run

Save each condition before opening or running the other:

1. Run `Chat: Export Chat...` and save the complete chat JSON as
   `A-chat.json` or `B-chat.json` in the matching result directory.
2. In the chat context menu, use `Copy All` and save the Markdown as
   `A-chat.md` or `B-chat.md`. This is a useful redundant capture of prompts,
   responses, thinking steps, and tool calls.
3. Open `Developer: Open Agent Debug Logs`, select the evaluated session, open
   its Summary view, and record or screenshot total tool calls, token usage,
   error count, and duration.
4. From the Agent Debug Log panel, use Export and save the OTLP JSON as
   `A-agent-debug.json` or `B-agent-debug.json`.
5. Preserve the condition repository in place. In particular, do not clean,
   commit, normalize, or edit `.agent-workflow-state/` after the run.
6. Record the visible agent name, model, thinking effort, permission level,
   start/end time, approvals, errors, corrections, and whether the final
   response included a route marker in `A-run-notes.md` or `B-run-notes.md`.
7. Save the Chat customization diagnostics evidence showing which instructions,
   agents, skills, hooks, and other customizations were loaded.

Return or make available for each condition:

- exported chat JSON and Copy All Markdown;
- Agent Debug OTLP JSON and Summary screenshot/metrics;
- the complete `.agent-workflow-state/` tree, including an empty tree if no
  state was created;
- `git status --short --branch`, the repository diff, and every untracked file
  created by the run;
- the run-notes file with settings, timing, approvals, errors, and route;
- any VS Code customization diagnostic that reported a loading error;
- the clean customization diagnostic, so absence of user memory/preferences can
  be audited rather than asserted.

If these paths remain available in the shared workspace, the evaluator can
inspect the repositories directly; attach the exported chat/debug files and
tell the evaluator the runs are complete. If the paths will not remain
available, archive each whole condition directory so state and unexpected
changes are not lost.

## Validity rules

- Evaluate A and B separately before comparing them.
- Treat missing telemetry as unavailable evidence, not zero activity.
- Treat self-reported file reads, route, or state changes as weaker evidence
  than debug logs and repository artifacts.
- A state-free run is valid if the behavior honestly decided durable state was
  unnecessary; it is not automatically success or failure.
- Both runs must actually apply the canonical Wayfinder runtime and state
  contract. If A routes away from Wayfinder or B does not load the selected
  workspace agent and its canonical dependencies, the primary mechanism was
  not exercised and the affected run is invalid for this causal comparison.
- Any implementation of the next exercise, original-repository mutation,
  prompt contamination, model/effort mismatch, reused chat history, or
  simulated focused-agent behavior is a protocol violation and must be
  reported rather than silently repaired.
- If local memory, Copilot Memory, user-profile customizations, or organization
  customizations cannot be disabled or are observed in the actual request
  context, label the run qualified or invalid according to whether the leaked
  content could affect orientation. Do not inspect and hand-delete user-owned
  memories merely to force a clean result.

## Separate later router experiment

A neutral-prompt comparison that lets the general Agent's router decide whether
to use Wayfinder can test broader product behavior. Preserve that as a separate
later router-vs-focused experiment with its own protocol and results. Do not
combine it with, substitute it for, or use it to support this primary Phase 1
host-projection comparison.
