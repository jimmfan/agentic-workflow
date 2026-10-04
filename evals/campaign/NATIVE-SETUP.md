# Native Codex setup

Use this host checklist with the [campaign runbook](README.md#native-codex-execution).
It records a working path for one bounded macOS control, not release reliability or long-context evidence.
No command in this guide authorizes a live run, login, credential inspection, or global configuration change.

## Prepare an independent consumer

Keep the authoring checkout, frozen campaign, consumer workspaces, session homes, and raw evidence separate.
Choose a new canonical temporary campaign directory outside the checkout and the user's home hierarchy.
On macOS, a fresh directory beneath `/private/tmp` can satisfy this requirement; check its actual ancestry before freezing or launching.
Every resolved consumer ancestor must lack `AGENTS.md`, `AGENTS.override.md`, and `.codex/config.toml`.
A home-level Codex config triggers this guard even when the campaign is outside the repository.
The consumer itself must also lack `.codex/config.toml`.
Do not delete those files or weaken the guard to make a campaign run.

Record the exact source commit and reviewed working diff, product commit, CLI binary hash/version, Python interpreter, model, reasoning effort, and subagent setting.
Freeze explicit turn, campaign, repetition, and output limits; verify the manifest and file inventories before launch.
Use a fresh destination for a separately authorized attempt and retain failed attempts.

## Check native isolation without a model

Run from a normal Terminal on the execution Mac when the controller's agent shell is already sandboxed.
macOS can reject nested Seatbelt initialization with `sandbox_apply: Operation not permitted`; this is an infrastructure result.
Normal Terminal execution still applies the adapter's native sandbox and never requires bypass flags.

The controller must resolve the Python executable with `Path(sys.executable).resolve(strict=True)` before entering the sandbox and embed that canonical path in the child-spawn probe.
An interpreter alias outside the granted framework path can fail inside the sandbox, where resolving the alias may itself be denied.
Keep the granted paths and deny canaries intact.

Replace the absolute path placeholders below with the selected host binary and a fresh independent output location:

```bash
uv run --locked python -m evals.campaign.codex --preflight \
  --binary /absolute/path/to/codex \
  --artifact-dir /absolute/independent/preflight-output
```

Require completed status, exit 0, readable/writable consumer canaries, denied synthetic artifact/credential canaries, and successful Python child startup.
This preflight does not read real authentication or call a model.
Passing it does not establish authentication, model availability, or every later tool dependency.

## Authorize and launch once

The user owns authentication and starts the reviewed live command from normal Terminal.
The adapter uses an existing regular auth file, temporarily copies it into its isolated session home, and removes the copy afterward.
Never inspect or include credential contents in a spec, transcript, documentation, or Git.

For a subscription-only run, require explicit native overrides `forced_login_method="chatgpt"` and `cli_auth_credentials_store="file"`, an isolated `CODEX_HOME`, and a launcher environment without API keys.
The ordinary adapter alone does not impose these authentication-method overrides; use a reviewed wrapper that adds them and rejects mismatched public settings.
If ChatGPT authentication is unavailable, stop rather than falling back to separately billed API authentication.
These controls restrict authentication method; time limits do not cap tokens or account usage.

Before claiming an attempt, verify the resolved ancestor guard, disjoint paths, executable identities, frozen inputs, public adapter request, and unused state.
Keep one persistent launch claim and no automatic retry.
For a one-turn smoke, one tested configuration used a 300-second turn deadline, a 600-second campaign launch window, a 630-second outer controller limit, and up to 15 seconds for shutdown.
The outer supervisor must account for inner runners using separate process groups and remove only its own temporary credential copy if interrupted.
That supervisor is a reviewed launch artifact, not built into the campaign's launch-window limit.

## Read the outcome and retain limits

Check `response.json`, `raw/invocation.json`, `checkpoint.json`, and the outer launch result together.
Native exit 0 with `execution_status="completed"` establishes completed execution; mechanical checks and semantic review establish behavior separately.
Controller exit 2 can mean a successful subject remains ungraded and therefore INCONCLUSIVE, or an infrastructure error; inspect the retained status and error.
Never score authentication, quota, network, sandbox, or timeout problems as a workflow failure solely because execution failed.
Observed unauthorized writes remain failures even on an incomplete run.

In the successful macOS control, `git diff` failed inside the restricted subject environment with an `xcrun` invalid developer-path error.
Text inspection and retained snapshots established the exact edit; the Git error's cause remains unresolved.
Check required tool behavior under the same isolation before depending on Git or developer tools in a larger scenario.
Do not infer that the host's developer tools are globally missing or change global settings from this error alone.

Use the runbook's blinded control calibration and independent semantic review before a formal PASS.
Token usage is not active context occupancy, and one routine edit establishes neither release superiority, reader continuity, nor compaction survival.
Keep raw traces and temporary homes outside Git under the [storage contract](../README.md#storage-contract).

## Verified feasibility result

One `routine-edit` turn completed on macOS 15.7.3 arm64 with Codex CLI 0.160.0, Python 3.14.6, and `gpt-6.1-sol` at medium reasoning effort.
The native preflight completed in about 0.079 seconds, native execution exited 0, and the outer controller completed in about 20.4 seconds without timeout.
Retained snapshots established the exact `recieve` to `receive` correction in README.md with no other net consumer changes, and the temporary credential copy was removed.
An independent reviewer matched all 48 synthetic calibration judgments and passed the subject's proportionate-response criterion; the combined mechanical and semantic report is PASS for this one turn.
Observation extraction emitted invalid-JSON and unrecognized-event warnings, so the review does not attest to complete transcript coverage or an absence of transient actions.
This is one successful feasibility control with the Git limitation above, not a measured reliability rate or version comparison.
