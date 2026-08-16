# Harbor and SlopCodeBench integration research

Date researched: 2026-08-15

## Practical conclusion

Use the current stable Harbor release, `harbor==0.21.0`, and the immutable
Harbor Hub dataset revision `gabeorlanski/slopcodebench@3`. Pin the Codex CLI
version and reasoning effort through Harbor's Codex agent kwargs. Run exactly
one task at a time, with one attempt, one concurrent trial, and no retries.

For the paired comparison, prepare a fresh host workspace for every
task/condition pair and bind-mount it at `/app` for both conditions. Leave the A
workspace empty. Install the current checked-out Agentic Workflow into the B
workspace with its supported lifecycle command before Harbor starts. This uses
Harbor's normal Codex agent and the product's normal install surface; it does not
rewrite prompts or alter the benchmark.

There is one required stop-gate. SlopCodeBench runs pinned `scb-check==0.1.0`
against all Python files under `/app`. The core Agentic Workflow payload contains
no Python files, so its Markdown/JSON files do not directly affect those metrics.
Before running, nevertheless assert that the *completed* B install, including
optional provider skills, has no `*.py` files. If it does, stop: B would have a
different verbosity/erosion measurement input, and excluding those files would
require a forbidden verifier change.

## Version and provenance pins

| Component | Recommended pin | Why |
| --- | --- | --- |
| Harbor | `0.21.0` | Latest stable PyPI/GitHub release found on the research date. An unpinned install would not define the runner precisely. |
| Harbor source | tag `v0.21.0`, commit `64afbbcb62165950301e1a6407c729aa26d844ff` | Immutable source reference for CLI and result behavior. |
| SlopCodeBench Harbor dataset | `gabeorlanski/slopcodebench@3` | Harbor numeric revisions are immutable. Revision 3 resolves to content hash `73a17cda817d37ce3352d18c272c40a3f6b623061023bee365b4df74adcd11b5` and dataset-version UUID `4e4a46a5-fe29-45cf-b0e2-06b1bef7ccc7`. |
| Agentic Workflow | repository commit `37e35b0be95b1b835f460af15187c91d915ca4dc` and payload version `0.11.1` at research time | Record both in the run manifest. Refuse to silently continue if the checkout changes before execution; either use this commit or deliberately update the manifest and report. |
| Codex CLI | `0.144.6`, supplied as `--ak version=0.144.6` | This was the locally installed current version observed during research. If the experiment deliberately chooses another version, pin and record it; if omitted, Harbor installs `@latest`. |
| Reasoning | `--ak reasoning_effort=high` | This matches the local Codex configuration observed during research and Harbor's current Codex default; the explicit value prevents default drift. |
| Model | `-m gpt-5.6-sol` for all six trials | This matches the local Codex configuration observed during research. Harbor passes the final path component to Codex and records the model in `agent_info.model_info`. |
| `scb-check` | benchmark-owned `0.1.0` | Already pinned by each source-owned verifier. Do not replace it. |

The Harbor conversion is immutable and therefore runnable reproducibly, but its
source-provenance note is weaker than ideal: converted task READMEs report a
source checkout described as `4d38d30-dirty` (2026-04-24). The upstream
SlopCodeBench dataset separately records source revision
`ba1f7fec544dae4ff274d2447d9b65aebfbc5196`. Report this mismatch as a
provenance limitation; do not imply the Harbor package came from a clean source
commit.

Primary sources:

- [Harbor 0.21.0 on PyPI](https://pypi.org/project/harbor/0.21.0/) and [GitHub release](https://github.com/harbor-framework/harbor/releases/tag/v0.21.0)
- [Harbor package-version rules](https://github.com/harbor-framework/harbor/blob/v0.21.0/src/harbor/models/package/version_ref.py)
- [SlopCodeBench revision 3 on Harbor Hub](https://hub.harborframework.com/datasets/gabeorlanski/slopcodebench/3)
- [Source-owned SlopCodeBench runner](https://github.com/SprocketLab/slop-code-bench), [problem repository](https://github.com/SprocketLab/scb-problems), and [published dataset](https://huggingface.co/datasets/gabeorlanski/slopcodebench)
- [SlopCodeBench paper](https://arxiv.org/abs/2603.24755)

## Supported setup and discovery commands

Harbor's official quick start recommends `uv tool install harbor`; pinning the
same supported package install makes it reproducible:

```bash
uv tool install 'harbor==0.21.0'
harbor --version
docker version
```

Harbor 0.21.0 uses singular package-management command groups:

```bash
harbor dataset list
harbor dataset download 'gabeorlanski/slopcodebench@3' \
  --output-dir evals/harbor/cache \
  --export
```

Some older examples use plural command groups; the pinned runner's `--help` and
tagged source define the applicable syntax. Keep the exported dataset read-only
and record its dataset hash and each selected task's digest from its lock
metadata. A numeric dataset revision is immutable; `latest` is mutable. For maximum task-level
traceability, a selected task can also be addressed directly as
`gabeorlanski/<task>@sha256:<task-digest>`, although running it through the
dataset retains the dataset-level aggregate metric.

Revision 3 and its member task digests can be captured without relying on a
mutable registry view:

```bash
harbor version show 'gabeorlanski/slopcodebench@3' --tasks --files --json
```

Primary sources:

- [Harbor getting started](https://www.harborframework.com/docs/getting-started)
- [Harbor dataset documentation](https://www.harborframework.com/docs/datasets)
- [Harbor 0.21.0 dataset CLI](https://github.com/harbor-framework/harbor/blob/v0.21.0/src/harbor/cli/datasets.py)
- [Harbor 0.21.0 version CLI](https://github.com/harbor-framework/harbor/blob/v0.21.0/src/harbor/cli/versions.py)

## Codex configuration under Harbor 0.21.0

Use the installed `codex` agent with agent kwargs, not an extra instruction file
or custom agent:

```text
-a codex
-m gpt-5.6-sol
--ak version=0.144.6
--ak reasoning_effort=high
```

Harbor 0.21.0 installs `@openai/codex@<version>` inside the task environment,
uses an isolated `CODEX_HOME=/tmp/codex-home`, and runs `codex exec` with JSON
output. Its outer Docker environment is the sandbox, so the inner command uses
Codex's sandbox/approval bypass. Default API authentication is
`OPENAI_API_KEY`. The agent also supports uploading a host Codex `auth.json`
when `CODEX_AUTH_JSON_PATH` is supplied as an agent environment variable or
`CODEX_FORCE_AUTH_JSON` is enabled. Choose one authentication mechanism before
the smoke test and keep it identical for A and B. Never write secrets to the
repository or report.

Harbor 0.21.0 supports a native Codex TOML file or inline JSON object through
`--ak "config=..."`; Harbor uploads the effective configuration to its isolated
Codex home after applying explicit runtime inputs. This feature is not needed
for the B treatment, which requires a real workspace installation rather than
merely Codex configuration. If a baseline Codex config is needed for model or
provider access, use the exact same file in A and B, archive its non-secret
contents, and pin its hash.

Harbor supports `--skill`, but that mechanism copies/registers skill directories
into the agent's home. It cannot install Agentic Workflow's root `AGENTS.md` and
`.ai-workflow/` routing contract, so it is not a faithful B condition.
`--extra-instruction-path` appends content to each benchmark instruction and
would change prompt presentation. Do not use it for B.

Primary sources:

- [Harbor agent documentation](https://www.harborframework.com/docs/agents)
- [Codex agent at Harbor v0.21.0](https://github.com/harbor-framework/harbor/blob/v0.21.0/src/harbor/agents/installed/codex.py)

## Fair B-only injection

For each selected task, create two new, independent workspace directories under
`evals/harbor/workspaces/<task>/A` and `.../B`. Do not reuse a workspace across
tasks or conditions. A must begin empty. Install B from the pinned current
checkout with the repository's supported lifecycle entrypoint:

```bash
python3 skills/agentic-workflow/scripts/lifecycle.py install \
  evals/harbor/workspaces/<task>/B \
  --source-revision 37e35b0be95b1b835f460af15187c91d915ca4dc

python3 skills/agentic-workflow/scripts/lifecycle.py status \
  evals/harbor/workspaces/<task>/B \
  --source-revision 37e35b0be95b1b835f460af15187c91d915ca4dc
```

The lifecycle installer treats optional provider installation as best-effort.
Capture its output and status. Decide and record before the run whether B means
core Agentic Workflow or core plus every declared provider; do not silently run
a partially installed provider set. The most faithful reading of “current
Agentic Workflow” is the complete checked-in configuration, so the recommended
acceptance condition is that all declared provider skills are present.

Run this additional metric-integrity check on each installed B workspace:

```bash
find evals/harbor/workspaces/<task>/B -type f -name '*.py' -print
```

The expected output is empty. The benchmark's pinned `scb-check` recursively
walks Python files; `--include-all` includes suppressed findings, not arbitrary
non-Python files. If the command finds provider scripts, stop rather than adding
verifier exclusions. The product's Markdown and JSON files remain visible to
Codex by design, but do not enter `scb-check`'s code metrics.

Bind-mount the workspace to `/app` with Harbor's supported Docker Compose volume
shape. Use this same mechanism in both conditions; only the host source path and
its intentional initial contents differ:

```json
[{"type":"bind","source":"/absolute/path/to/workspace","target":"/app"}]
```

This is preferable to mounting only B because it equalizes Docker mechanics.
Use absolute paths. Confirm in the infrastructure smoke test that the empty bind
mount works with the chosen source-owned task image and that the same workspace
persists across checkpoints. Harbor's multi-step implementation reuses the
environment workspace while, by default, starting a fresh Codex session for each
checkpoint. Preserve that default unless the benchmark publisher explicitly
specifies session resumption; do not add `--resume-trajectory` merely because it
exists.

Before each paired task, also verify:

1. A contains none of `AGENTS.md`, `.ai-workflow/`, or `.agents/skills/`.
2. B lifecycle status is healthy and its initial contents match the pinned
   install evidence.
3. Both commands have the same task digest, model, Codex version, reasoning
   effort, authentication mode, environment, timeouts, attempt count, retry
   count, concurrency, and trajectory policy.
4. The two completed trial `lock.json` files resolve the same task digest and
   differ only in expected job identity and mount source.
5. No task or verifier file was edited.

Primary sources:

- [Harbor 0.21.0 job CLI (`--mounts`, task filters, concurrency, attempts, retries)](https://github.com/harbor-framework/harbor/blob/v0.21.0/src/harbor/cli/jobs.py)
- [Harbor 0.21.0 multi-step runner](https://github.com/harbor-framework/harbor/blob/v0.21.0/src/harbor/trial/multi_step.py)
- [Source-owned `scb-check` package description](https://pypi.org/project/scb-check/0.1.0/)
- [Agentic Workflow lifecycle contract](../../skills/agentic-workflow/SKILL.md)

## Paired-run command shape

Run sequentially, one task and condition at a time. Use the dataset selector to
retain the source-owned dataset metric:

```bash
harbor run \
  -d 'gabeorlanski/slopcodebench@3' \
  -i 'gabeorlanski/<task>' \
  -a codex \
  -m 'gpt-5.6-sol' \
  --ak 'version=0.144.6' \
  --ak 'reasoning_effort=high' \
  -e docker \
  -n 1 \
  -k 1 \
  -r 0 \
  --mounts '[{"type":"bind","source":"/absolute/path/to/evals/harbor/workspaces/<task>/<condition>","target":"/app"}]' \
  --job-name '<task>-<condition>' \
  --jobs-dir '/absolute/path/to/evals/harbor/jobs'
```

Add only the preselected, identical authentication flag(s). Do not add web
search, MCP, extra instructions, skills, trajectory resume, or timeout overrides
to one condition. If a timeout multiplier is needed after the smoke test, set it
identically in both conditions and record the change before any scored trial.
The source tasks specify 7,200 seconds per agent checkpoint and 900 seconds per
verifier checkpoint; leaving the multiplier at `1.0` preserves those definitions.

`-n 1 -k 1 -r 0` means one concurrent trial, one attempt, and no automatic
retries. A failed infrastructure smoke is not a scored trial. Once a scored task
starts, do not rerun one condition selectively; preserve and report failures.

## Source-owned metrics and success interpretation

The Harbor conversion contains 36 multi-step tasks. Harbor first mean-reduces
checkpoint rewards into each trial, then its dataset `metric.py` emits:

- `core_pass_rate_mean`
- `isolated_pass_rate_mean`
- `strict_pass_rate_mean`
- `verbosity_mean`
- `erosion_mean`
- `verbosity_increase_rate`
- `erosion_increase_rate`
- `trial_count`
- `missing_trial_count`

At each checkpoint:

- `core_pass_rate` includes CORE tests only.
- `isolated_pass_rate` includes CORE, FUNCTIONALITY, and ERROR tests but excludes
  regression tests.
- `strict_pass_rate` covers every supplied test, including regression tests when
  that task/checkpoint supplies them; it is the checkpoint advance gate.
- `verbosity` and `erosion` come from pinned `scb-check`.
- `reward_details.json` includes group-level passed/collected counts, pytest
  return code, regression pass rate, and raw `scb-check` details.

Not every source task includes prior tests at every checkpoint. Therefore
“regression prevention” must be interpreted using the selected task's own README
and `reward_details.json`, not inferred from `strict_pass_rate` alone.

Harbor does not expose one universal Boolean named “success.” Distinguish:

- **Infrastructure completion:** no trial/step `exception_info`.
- **Checkpoint correctness:** the source verifier's rewards and test counts.
- **Final success:** define before running as final-checkpoint
  `strict_pass_rate == 1.0` (recommended), and report the final checkpoint's
  detailed counts. Do not substitute the mean-across-checkpoints dataset score
  for this final-checkpoint criterion.

The sample is only three paired tasks. Report per-task deltas and the mean/median
descriptively, with no claim of general statistical superiority.

Primary sources:

- [SlopCodeBench Harbor dataset page](https://hub.harborframework.com/datasets/gabeorlanski/slopcodebench/3)
- The immutable dataset's source-owned `metric.py` and per-task README/test files
  in the downloaded export

## Results, tokens, timings, and trajectories

Preserve each complete job directory. The important stable 0.21.0 artifacts are:

| Artifact | Use |
| --- | --- |
| `<job>/config.json` and `<job>/lock.json` | Resolved job and immutable package evidence. |
| `<job>/result.json` | Job-level aggregate metrics and token/cost totals. |
| `<job>/<trial>/result.json` | Authoritative per-trial identity, checksum, agent/model version, timestamps, exception state, and per-step results. |
| `<job>/<trial>/steps/<checkpoint>/verifier/reward.json` | Source verifier reward for the checkpoint. |
| `<job>/<trial>/steps/<checkpoint>/verifier/reward_details.json` | Per-test-group counts and raw diagnostic evidence. |
| `<job>/<trial>/steps/<checkpoint>/agent/trajectory.json` | Harbor's Codex ATIF trajectory for the checkpoint. |
| `<job>/<trial>/steps/<checkpoint>/agent/codex.txt` and downloaded session logs | Native/raw fallback evidence when needed. |

For multi-step trials, token fields live in each
`step_results[i].agent_result`: `n_input_tokens` (input including cache),
`n_cache_tokens`, `n_output_tokens`, and `cost_usd`. Harbor's job statistics sum
these. Do not calculate “uncached input” as the primary figure; if useful, label
`n_input_tokens - n_cache_tokens` explicitly as a derived value. Missing token
fields remain missing—do not coerce them to zero.

Overall elapsed time is `finished_at - started_at`. Per-checkpoint agent and
verifier elapsed times come from the `agent_execution` and `verifier` timing
objects in each step result. State whether setup time is included in any reported
duration.

Codex automatically produces the standardized Agent Trajectory Interchange
Format (ATIF) file. It contains the interaction history, assistant messages,
tool calls, environment observations, and token/cost metrics available from the
native session. Preserve it unmodified. If conversion fails or a trajectory is
absent, preserve the native logs and report that limitation rather than
reconstructing a synthetic trajectory.

Primary sources:

- [Harbor ATIF documentation](https://www.harborframework.com/docs/agents/trajectory-format)
- [Harbor 0.21.0 trial result model](https://github.com/harbor-framework/harbor/blob/v0.21.0/src/harbor/models/trial/result.py)
- [Harbor 0.21.0 token context](https://github.com/harbor-framework/harbor/blob/v0.21.0/src/harbor/models/agent/context.py)
- [Harbor 0.21.0 trial paths](https://github.com/harbor-framework/harbor/blob/v0.21.0/src/harbor/models/trial/paths.py)
- [Harbor 0.21.0 Codex-to-ATIF conversion](https://github.com/harbor-framework/harbor/blob/v0.21.0/src/harbor/agents/installed/codex.py)

## Minimal infrastructure smoke test

Before any scored trial, use one disposable source-owned task and verify only the
integration boundary:

1. Harbor 0.21.0 starts the task image through Docker.
2. Exact Codex installation and authentication work.
3. The `/app` bind mount is writable and persists between task checkpoints.
4. A starts without Agentic Workflow; B discovers the installed root
   `AGENTS.md` and skill paths without appending text to benchmark instructions.
5. The verifier runs unchanged and emits `reward.json` plus
   `reward_details.json`.
6. Each checkpoint produces `trajectory.json`, token fields, and timing fields,
   or the missing field is documented.
7. The resolved task digests match across A/B and the B workspace has no Python
   files before agent work begins.

This smoke is for infrastructure only and is not part of the three-task score.
Do not use it to tune prompts, task selection, or verifier behavior. If any item
fails, stop and document the limitation instead of modifying the benchmark.
