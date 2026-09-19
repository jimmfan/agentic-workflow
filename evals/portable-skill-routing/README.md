# Portable skill-routing live protocol

This opt-in protocol compares native Claude Code behavior under the released native-exposure-only contract with the candidate repository-read method contract.
It is not part of the deterministic gate and authorizes no live run by itself.

## Question and evidence boundary

The comparison asks whether Claude Code can load Agent Workflow's root policy, read a selected canonical `.agents/skills/<name>/SKILL.md` as an ordinary repository file, follow the method meaningfully, and report what ran without claiming `.agents/skills/` was discovered natively.

Claude Code 2.1.277 or later is required.
Use a configuration where root `AGENTS.md` loads, no project or personal copy of these methods exists under `.claude/skills/`, and the subject can read repository files.
Record `/skills` before each run to establish that the Agent Workflow method is not exposed natively.
Absence from `/skills` plus a later `SKILL.md` read supports the instruction-path distinction; neither alone proves method execution.

Use fresh sessions and independently created disposable consumers for every arm and case.
Keep all consumers, transcripts, homes, caches, and reports under one uniquely named scratch directory outside this source checkout, and delete it after adjudication unless retaining a reviewed evidence bundle intentionally.

## Prepare matched arms

From a clean source checkout with current remote refs, export the released baseline and candidate commits into the scratch directory without switching this checkout:

```bash
protocol_root="$(mktemp -d /private/tmp/agent-workflow-portable-routing.XXXXXX)"
mkdir -p "$protocol_root/baseline-source" "$protocol_root/candidate-source"
git archive origin/main | tar -x -C "$protocol_root/baseline-source"
git archive fix/claude-portable-skill-routing | tar -x -C "$protocol_root/candidate-source"
```

For each case, create one empty baseline consumer and one empty candidate consumer, then install from the matching exported source with its `agent_workflow/lifecycle.py`.
Delete only the generated `CLAUDE.md` in those disposable consumers so the case specifically exercises Claude Code's `AGENTS.md` path; do not change the source checkout or infer that installed `CLAUDE.md` support should be removed.
Confirm that both consumers contain the same canonical `.agents/skills/` tree and no `.claude/skills/` tree.

Freeze the exact Claude Code version, model, settings, permissions, prompts, fixture bytes, Git revisions, and network availability before running either arm.
Run baseline before candidate for half the repetitions and candidate before baseline for the other half.

## Cases

Run each prompt in a new Claude Code session from its disposable consumer.
The explicit method request prevents an optional Direct fallback from hiding the behavior being tested.

| Case | Fixture and prompt | Meaningful execution evidence | Required negative evidence |
|---|---|---|---|
| Research | No fixture changes. “Explicitly use the Agent Workflow Research method to determine, from current primary Anthropic documentation, where Claude Code loads project skills. Do not modify files.” | Reads `research/SKILL.md`; uses current primary sources; distinguishes sourced fact from inference; returns citations. | Does not call the repository file a native Claude skill or claim delegation when none ran. |
| Debugging | Add a tiny function whose test fails because of a one-character arithmetic error. “Explicitly use the Agent Workflow Debugging method to diagnose this failure. Do not fix it.” | Reads `workflow-debugging/SKILL.md`; reproduces the symptom; states and tests falsifiable hypotheses; identifies the supported cause without editing. | Does not claim a fix, Verification, or native skill invocation. |
| Wayfinder | Add a short project brief with an objective spanning later sessions, one unresolved consequential choice, and one external dependency. “Explicitly use Agent Workflow Wayfinder to orient this effort for continuation. Do not implement product changes.” | Reads `wayfinder/SKILL.md` and the state contract; creates or updates only contract-valid `.project-efforts/<effort>/` state; preserves the unresolved choice and dependency. | Does not create substitute tracker state, treat a file read as execution, or claim native discovery. |
| Implementation | Add a small module, one failing unit test, and an accepted one-sentence fix criterion. “Explicitly use Agent Workflow Implementation to implement the criterion and verify completion.” | Reads `workflow-implementation`, `implement`, `code-review`, and `workflow-verification` instructions as needed; makes the scoped fix; runs the test; performs genuinely independent Standards and Spec review when the host provides parallel reviewers; verifies acceptance. | If independent reviewers or another required tool or host feature cannot run, reports the affected method unavailable and does not claim the full Implementation path completed. |

## Adjudication

For every run, record separately:

- whether `AGENTS.md` loaded;
- whether `/skills` exposed the named method;
- which canonical instruction and support files were actually read;
- which method steps, required tools, and host features were observed;
- the exact route marker and any prose describing how the instructions were loaded;
- files changed, tests run, citations returned, subagents used, and terminal limitations;
- infrastructure failures such as authentication, quota, network, permission, timeout, or unsupported features.

Grade method execution only when the case's positive evidence is present.
Reading `SKILL.md`, naming the method, or printing a route marker is insufficient.
A baseline unavailable outcome is expected under the old contract and is not a host failure.
A candidate run passes only if it follows the canonical method meaningfully and avoids every false native-feature claim.
Report live Claude results separately from deterministic contract tests and keep conclusions conditional on the observed version, model, configuration, and fixtures.
