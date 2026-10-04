# Repeatable behavioral campaigns

This source-only harness turns recurring Agent Workflow failures into frozen conversations, per-turn evidence, and separately reviewed results.
It supports intact historical releases and complete skill-directory substitutions without changing the authoring checkout.
Start with the [case catalog](CATALOG.md) to see exactly what each test measures and [version selection](VERSIONS.md) to choose meaningful comparisons.
Nothing in these files launches a model automatically.
The [acceptance evidence](results/2026-10-03/README.md) distinguishes the delivered tooling checks, actual manual controls, and native-host blocker.

## The repeatable process

1. Choose one question and the cases that can answer it.
   Start with a small smoke run, then a matched release comparison; use a skill substitution only after a useful difference appears.
2. Review and freeze the public requests, hidden requirements, neutral fixtures, product commits, host/model settings, repetition count, and time/turn limits.
   Keep a separate checkout and output directory for each concurrent campaign.
3. Calibrate an independent semantic grader using the controls below.
   Keep answer keys and condition identities away from subjects and grader context.
4. Run sequential subjects with the exact frozen requests.
   Resume the same writer conversation, create a genuinely fresh reader at the specified boundary, and save every attempt before moving on.
5. Export a condition-blinded evidence packet and obtain cited judgments for every semantic requirement.
   Mechanical failures cannot be overridden by favorable prose review.
6. Report each behavior and attempt, including failures, missing observations, and host problems.
   Repeat promising contrasts and check a held-out story before changing production instructions.

One successful conversation is a feasibility observation, not proof that a release is better.
Turns from the same conversation are correlated; the repetition unit is a fresh complete trajectory.
Keep common useful outcomes separate from current-contract conformance, which older releases were never required to follow.

## Prepare and inspect without model use

Use Python 3.11+, Git, and the repository's locked development environment.
Run these commands from the source checkout:

```bash
uv run --locked python -m evals.campaign validate evals/campaign/examples/smoke.json
uv run --locked python -m unittest discover -s evals/tests -p 'test_campaign_*.py' -v
```

Copy an example to a new campaign spec when changing its settings; keep scenario paths valid relative to the spec file.
Set the actual model identifier and reasoning effort available on the selected host and keep them fixed across conditions.
The examples are bounded templates, not evidence of executed comparisons.

```bash
uv run --locked python -m evals.campaign freeze evals/campaign/examples/smoke.json \
  --out /tmp/aw-smoke-001
uv run --locked python -m evals.campaign status /tmp/aw-smoke-001
```

Use a new output path outside the authoring checkout and outside any other project instruction hierarchy.
The preparer resolves each ref to a full commit, exports it without switching branches, uses that revision's own supported installer, and records installed hashes.
Each subject gets a separate consumer, a local Git baseline with no remote, and its own session home.
Fixtures contain project content rather than a copied framework or a modern map that would bias older versions.
Complete donor skill directories, including helpers and agent metadata, replace the corresponding base skill; obvious missing local dependencies reject preparation.
Passing preparation establishes installability and recorded identity, not semantic compatibility.

The manifest binds the schedule, public prompts, requirements, fixture files, installed payloads, tooling hashes, and requested host settings.
Once frozen, do not edit those inputs or the evaluation code and continue the same campaign.
Retain the exact tooling checkout, or start a separately named campaign after a change.
Existing output directories are never reused.

## Calibrate the grader

The control corpus contains two valid alternatives and six deliberate defects, with six criteria per case.
Export only its blind packet to an independent reviewer:

```bash
uv run --locked python -m evals.campaign calibration-packet \
  evals/campaign/examples/calibration.json --out /tmp/aw-calibration-packet.json
```

Give the reviewer the packet and this instruction:

> Judge every declared semantic requirement using only the supplied evidence.
> Return PASS, FAIL, or INCONCLUSIVE with a short rationale and exact evidence quotes.
> A claim that a file was saved is insufficient when the requirement concerns saved state.
> A correct saved file is insufficient when the requirement concerns the fresh reader's answer.
> Do not infer absent execution or prefer a condition from its wording or artifact layout.

Save its actual returned review in the format below, then assess it:

```bash
uv run --locked python -m evals.campaign calibration-assess \
  evals/campaign/examples/calibration.json \
  --review /tmp/aw-calibration-review.json --out /tmp/aw-calibration-result.json
```

The result compares all 48 judgments with the authored expectations.
Missing judgments remain INCONCLUSIVE and cannot pass calibration.
Review disagreements before using the same grading procedure on subjects; an ambiguous control needs a new corpus revision with the original result retained.
Calibration is a separate quality check and never adds passes to subject totals.
The harness validates citations and agreement; it cannot establish reviewer independence or the correctness of an interpretation automatically.

## Native Codex execution

Follow the [native setup checklist](NATIVE-SETUP.md) for canonical paths, macOS isolation, subscription-only launch controls, and outcome interpretation.

Install an authenticated supported Codex CLI on the execution host.
The adapter checks the required command surface and supported isolation before copying an existing credential into a temporary session home.
It does not perform login or bypass the sandbox.
Use an absolute binary path in `host.settings.binary` when `codex` is not on PATH.
An optional `host.settings.auth_file` selects an existing regular authentication file; do not put credential contents in a spec or Git.

Run the no-model preflight first:

```bash
uv run --locked python -m evals.campaign.codex --preflight
```

After successful preflight, the explicit live command consumes model allowance:

```bash
uv run --locked python -m evals.campaign run /tmp/aw-smoke-001 --allow-live
```

The native adapter creates a persistent writer with `codex exec`, then resumes its exact session ID.
A reader starts with a different session home and ID.
Model, reasoning effort, binary identity, and subagent availability cannot change within a resumed writer.
The adapter disables memory, apps/plugins, and web search, uses isolated HOME/CODEX_HOME, and rejects inherited project instructions outside the consumer.
Native subagents are enabled by default with at most two concurrent children so the installed implementation/review workflow can execute.
Setting `host.settings.allow_subagents` to false defines a restricted host condition and may prevent required review; do not interpret that restriction as a release defect.
The sandbox probe observes the parent process only; child permission inheritance follows the native host contract and is not independently proven by that probe.
The primary model is frozen, but explicit child model overrides and unavailable child telemetry limit claims about all descendant settings and cost.

Limits count controller-issued subject turns, not every descendant generation or tool call.
The adapter bounds each primary invocation and the campaign's launch window, retains timeout/failure output, and removes its temporary credential copy afterward.
The invocation deadline and output bound apply while delivering stdin as well as while collecting the response, including when the child stops reading its prompt.
It does not automatically retry or replace an inconvenient result.
No retry should silently become the same sample: retain the failed attempt and freeze a separately identified rerun if needed.

## Manual host or Dot/Glitch operation

Set `host.kind` to `manual` before freezing, and record the actual host/model settings or explicitly mark unavailable observations.
Dot can operate these steps on a connected machine or suitable Codex environment; it should act as the controller, with each subject confined to the requested consumer and public request.
Do not run the subject inside the controller's existing conversation.

```bash
uv run --locked python -m evals.campaign begin /tmp/aw-smoke-001 --run run-0001
```

The returned JSON gives the consumer path, one public prompt, raw-evidence directory, session home, required prior session ID, and deadline.
Give the subject the workspace and exact public prompt, with ordinary host instructions to follow the consumer's installed policy.
Do not give it the scenario rubric, version-comparison rationale, calibration answers, other subjects' artifacts, or future turns.
Resume the exact subject when `session_id` is present; create a fresh one when it is null.
Observe completion and save the actual response envelope outside the consumer:

```json
{
  "schema": 1,
  "execution_status": "completed",
  "session_id": "actual-host-session-id",
  "response": "Actual final response, unchanged.",
  "observations": {"host": "manual", "model_observed": null},
  "traces": []
}
```

```bash
uv run --locked python -m evals.campaign record /tmp/aw-smoke-001 \
  --run run-0001 --response /tmp/actual-response.json
```

Repeat `begin` and `record` until that run completes, then proceed in the frozen schedule order.
Use `infrastructure-blocked`, `timeout`, or `error` for incomplete execution and retain its actual explanation.
Never fabricate native JSONL from a subject's summary or manually assert a command observation as if it were a captured native event.
The native parser accepts retained trace files only from that attempt's raw directory.
Manual responses and file snapshots can establish useful outcomes while missing native actions remain INCONCLUSIVE.

## Grade and report

Export the completed evidence without condition names or installed policy text:

```bash
uv run --locked python -m evals.campaign packet /tmp/aw-smoke-001 \
  --out /tmp/aw-smoke-packet.json
```

Use an independent grader that has passed the control calibration under the same review procedure.
The packet includes public requests, saved project content, diffs, responses, native observations, and declared checks.
Generated filenames or wording can still reveal a treatment; label blinding is not complete anonymity.
Use the exact packet hash and item/check IDs:

```json
{
  "packet_sha256": "copy the exported packet hash",
  "reviewer": "actual reviewer/session; model and settings if observed",
  "items": [{
    "id": "run-0001/T1",
    "checks": {
      "semantic-check-id": {
        "verdict": "PASS",
        "rationale": "Explain why the cited evidence satisfies this requirement.",
        "evidence": [{"path": "docs/visit.md", "quote": "Exact nonempty text from the packet"}]
      }
    }
  }]
}
```

`@response`, `@requests`, `@diff`, `@inventory`, and `@observations` are packet evidence keys.
Calibration packets use `@request` for their single supplied request.
A saved-state PASS needs a saved-file citation; a response PASS needs an `@response` citation.
For an omission, cite the relevant current artifact or inventory and explain what is missing.
Leave genuinely unavailable behavior INCONCLUSIVE rather than inventing evidence.

```bash
uv run --locked python -m evals.campaign grade /tmp/aw-smoke-001 \
  --review /tmp/aw-smoke-review.json
uv run --locked python -m evals.campaign report /tmp/aw-smoke-001 \
  --out /tmp/aw-smoke-report.json
```

The second command writes JSON and adjacent Markdown, refusing to replace either destination.
Reports include every scheduled turn, grouped outcomes, per-behavior counts, commit identities, and explicit unexecuted/infrastructure states.
PASS requires every required check to pass; any observed violation yields FAIL; otherwise missing execution, observation, or semantic review yields INCONCLUSIVE.
`run`, `grade`, `report`, and `calibration-assess` exit 0 for PASS, 1 for FAIL, and 2 for INCONCLUSIVE/error.
Setup/export commands exit 0 on success and 2 on error.
The ungraded end of a successful live run normally exits 2 because semantic review is still required.

## Interrupted attempts and evidence limits

An attempt is recorded before consumer preparation or subject execution.
Inspect `status` after interruption; never start a second subject to fill the same pending turn.
If the external subject is still running, stop it before recovering:

```bash
uv run --locked python -m evals.campaign recover /tmp/aw-smoke-001 \
  --run run-0001 --reason "Describe the observed interruption"
```

Recovery adopts an already saved valid checkpoint or records the interrupted attempt without a model retry.
If evidence capture itself fails, recovery stops the run with unavailable evidence and retains the consumer and partial files.
A hard-killed coordinator can leave `.campaign-lock`; inspect the recorded PID and verify no operation remains active before removing that one stale lock.
Never remove a live lock or repair a run by editing its manifest/checkpoints.

Snapshots compare file content, entry type, symlink target, and POSIX permission bits for files and directories.
Frozen input and installed-payload inventories include those permission bits, empty directories, and each inventory root, so permission drift is rejected before starting a turn.
Campaign captures also retain the workspace root and `.git` root permission bits; read-only turns compare Git metadata permissions as well.
A permission-only change counts as a write, including a change to a protected path or an existing parent directory whose child is writable.
Snapshots establish net effects between turns, not every transient filesystem action or an absence of external actions; they do not capture ownership, ACLs, or extended attributes.
Older snapshots and frozen inventories without permission bits do not establish that permissions were preserved; retain their original tooling and evidence, and freeze a new campaign for the stronger check.
Current inventory verification rejects older content-only inventories rather than inferring their missing permissions or rewriting their hashes.
Unauthorized saved changes remain failures even when execution times out.
Observed native commands establish invocation/result metadata and retained public output; final prose is not a tool trace.
For `command_observed`, the existing `argv_contains` field names the exact executable or Python script path to observe; it no longer matches arbitrary command text.
Simple direct commands and Python script invocations, optionally inside one `sh`, `bash`, `zsh`, or `dash` `-c`/`-lc` wrapper, are recognized; `./verify.py` and `verify.py` identify the same target.
Filename mentions such as `cat verify.py` or `echo verify.py`, different paths, inline Python, and unsupported compound or expanded shell commands remain INCONCLUSIVE.
A completed invocation with a recorded nonzero exit still establishes invocation; successful verification requires separate result evidence.
Token usage is not active context occupancy.
An absent compaction event is INCONCLUSIVE, and fresh-reader reconstruction is a separate property from survival through real compaction.
The accumulated variants add conversation content; they do not establish near-limit context pressure.
File hashes detect drift and bind reviews to retained evidence; this is a cooperative experiment record, not a defense against a malicious operator rewriting all evidence and hashes.

Follow the [evaluation storage contract](../README.md#storage-contract): commit frozen inputs, compact reports, relevant quotations, and adjudication; keep raw traces, copied workspaces, and temporary homes out of Git.
Retain the complete external campaign directory securely when a later reviewer needs raw evidence.
Synthetic control tests verify the harness and evaluator; they never count as live Agent Workflow passes.
