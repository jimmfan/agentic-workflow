# Final A/B parity validation

Validated: 2026-08-15 (America/New_York)

## Decision

The final smoke conditions are valid and comparable enough to start the frozen
three-task paired experiment. Both fresh smokes completed the immutable Harbor
hello-world task with reward `1.0`, no exception, one attempt, and no retry.

Condition A proof shows Agentic Workflow absent both before and after Codex
setup. Condition B proof shows a normal lifecycle installation of Agentic
Workflow `0.11.1` from frozen source revision
`37e35b0be95b1b835f460af15187c91d915ca4dc`, with all 14
`mattpocock/skills@v1.2.3` providers present, none missing or incompatible, and
no `*.py` files in the installed framework/provider roots.

## Equivalent settings

| Setting | A | B |
| --- | --- | --- |
| Harbor | `0.21.0` | `0.21.0` |
| Codex CLI | `0.144.6` | `0.144.6` |
| Model | `gpt-5.6-sol` | `gpt-5.6-sol` |
| Reasoning effort | `high` | `high` |
| Environment | Docker | Docker |
| Attempts | 1 | 1 |
| Retries | 0 | 0 |
| Concurrent trials | 1 | 1 |
| Timeout multiplier | `1.0` | `1.0` |
| Session policy | fresh session per checkpoint | fresh session per checkpoint |
| Harbor-injected skills | none | none |
| MCP servers | none | none |
| Extra instruction paths | none | none |
| Extra allowed hosts | none | none |
| Hello-world task digest | `sha256:38d7a077f07fbee8efc78db5dec9a72f82e727510ad1dcfeac0b55fa845256b7` | same |
| Smoke reward | `1.0` | `1.0` |

Both conditions run through `run_harbor.py`, which puts the evaluation-local
`uv==0.11.32` on the host `PATH` so the unchanged SlopCodeBench aggregate metric
can execute.

## Intended difference and setup isolation

The agent import paths differ only to enforce the experimental condition:

- A uses `harbor_agents:VanillaCodex`, which rejects any Agentic Workflow
  installation or managed instruction region.
- B uses `harbor_agents:AgenticWorkflowCodex`, which runs the checked-in public
  lifecycle installer and then fails closed unless the frozen revision, all 14
  provider pins, and the no-workflow-Python constraint are proven.

The B lifecycle receives the official GitHub CLI `2.97.0` Linux/arm64 binary
and authenticated GitHub access only during setup. The GitHub token is obtained
from the host credential store at runtime, is not written to configuration or
job artifacts, and is passed only to the lifecycle subprocess. Before Codex
receives a task instruction, both the transient `gh` binary and the uploaded
lifecycle source bundle are removed. A scan of the final B smoke artifacts found
no token markers.

The resulting intended task-time difference is therefore the complete installed
Agentic Workflow product: its managed `AGENTS.md`/`CLAUDE.md` regions,
`.ai-workflow/`, durable-state directory, four local workflow adapters, and all
14 pinned providers.

## Frozen scored inputs

The scored conditions use the same immutable dataset:

`gabeorlanski/slopcodebench@sha256:73a17cda817d37ce3352d18c272c40a3f6b623061023bee365b4df74adcd11b5`

Only the previously selected tasks will run:

| Task | Immutable task hash | Checkpoints |
| --- | --- | ---: |
| `gabeorlanski/circuit_eval` | `sha256:3bbbb4e0f03cc0824f4a77d0e1ab15004eebb01b8774488dd130f0508321a700` | 8 |
| `gabeorlanski/database_migration` | `sha256:15a6ac32fc6e2ac000df7e634d6f21899aed228418fdb277725ee93790f0d25f` | 5 |
| `gabeorlanski/trajectory_api` | `sha256:e2d4bdf7dffca38ecba7ceffce4e53b1ec16b9ca5824e28819f9a6540e904ae2` | 5 |

The downloaded task packages and source-owned verifiers are shared immutable
inputs. No benchmark task, instruction, verifier, or scoring file was changed.

## Superseded evidence

The interrupted earlier vanilla `circuit_eval` checkpoint remains under
`evals/harbor/jobs/2026-08-15-slopcodebench-a/` for audit only. It uses a
different pre-validation run identity and will not be included in the final
paired comparison.
