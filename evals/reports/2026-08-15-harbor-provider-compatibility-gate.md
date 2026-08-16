# Harbor SlopCodeBench provider compatibility gate

Date: 2026-08-15

## Conclusion

Do not run the scored condition B with the current Harbor task image. Its
supported Agentic Workflow lifecycle install produced a healthy core router but
installed none of the 14 declared upstream provider skills. That is a supported
core-only installation, but it is a reduced provider configuration and does not
represent the complete condition B required for this comparison.

The experiment is not inherently incompatible with SlopCodeBench's Python-file
metric. A clean supported lifecycle probe installed all 14 providers and found
no `*.py` files in the Agentic Workflow core or provider trees. No product,
provider, task, or verifier change is needed to satisfy the contamination
constraint. The scored B run remains blocked until the actual Harbor task
environment can perform the supported provider installation and passes the same
`14 present, 0 missing, 0 incompatible` and no-Python checks.

No scored B trial was started.

## Exact missing provider inventory

The condition-B infrastructure smoke ran the checked-in lifecycle installer in
`/app` at source revision
`37e35b0be95b1b835f460af15187c91d915ca4dc`. Lifecycle status reported:

```text
Agentic Workflow: healthy
Optional provider: mattpocock/skills@v1.2.3
Optional provider skills: 0 present, 14 missing, 0 preserved incompatible
```

The install log explains why: the Harbor task image did not have a GitHub CLI
with the `gh skill` command, so optional provider setup was skipped. The missing
skills, their Codex invocation policy, and their declared role are:

| Upstream skill | Codex invocation | Declared role or likely effect |
| --- | --- | --- |
| `setup-matt-pocock-skills` | user-only | Provider configuration |
| `wayfinder` | user-only | Large, uncertain multi-session planning |
| `teach` | user-only | Sustained learning workflow |
| `research` | implicit | Substantive external research |
| `to-spec` | user-only | Durable specification |
| `to-tickets` | user-only | Dependency-ordered work tickets |
| `implement` | user-only | Provider-owned implementation, TDD, and closing review loop |
| `tdd` | implicit | Explicit test-first implementation |
| `code-review` | implicit | Standalone fixed-point review |
| `grilling` | implicit | Requirements interrogation |
| `domain-modeling` | implicit | Domain-model exploration |
| `prototype` | implicit | Prototyping |
| `codebase-design` | implicit | Codebase design analysis |
| `triage` | user-only | Issue triage |

This list is the complete `mattpocock/skills@v1.2.3` declaration in
`skills/agentic-workflow/payload/ai-workflow/providers.json`. The documented
lifecycle install attempts to install every missing declared skill after the
core transaction using `gh skill install`; provider installation is explicitly
best-effort, so its failure does not make core status unhealthy.

## Does the absence matter on the three selected tasks?

It can materially change routing or execution, although the likely effect is
smaller than it would be for an explicit provider request.

The selected SlopCodeBench instructions ask Codex to build and iteratively
extend a circuit evaluator, a database migration tool, and a trajectory API.
They do not use Codex's exact `$skill-name` invocation syntax. Consequently, the
seven user-only providers cannot execute under the installed routing contract;
in particular, ordinary prose such as “implement” is not an invocation of
`$implement`. A normal implementation route would use the local implementation
adapter and truthfully fall back to host-native Codex work.

The other seven providers are implicit. The tasks do not ask for external
research, a standalone review, or a test-first process, and they are bounded
checkpoint tasks rather than Wayfinder-scale work. That makes activation of
`research`, `tdd`, and `code-review` unlikely. However, the database and API
tasks could plausibly trigger domain-modeling, prototyping, codebase-design, or
requirements-interrogation behavior. Removing all implicit skills also changes
the capability catalog visible to Codex. It would therefore be unjustified to
declare the reduced configuration behaviorally equivalent before observing the
runs.

For this experiment, condition B with `0/14` providers is invalid even though
the core lifecycle status is healthy.

## Python contamination result

A separate clean target outside any Git worktree was installed using the same
checked-in lifecycle entrypoint and source revision, with the documented GitHub
CLI provider capability available. Its status was:

```text
Current package version: 0.11.1
Agentic Workflow: healthy
Optional provider: mattpocock/skills@v1.2.3
Optional provider skills: 14 present, 0 missing, 0 preserved incompatible
```

Recursive inspection of `.ai-workflow/`, the four framework-owned local
workflow skill directories, and all 14 upstream provider directories found zero
`*.py` files. The installed provider content is Markdown/YAML. Therefore
SlopCodeBench's recursive Python analysis need not be weakened or given an
exclusion: Agentic Workflow adds no Python file to its measurement input.

The evaluation harness now independently enforces both properties before Codex
runs in condition B:

1. every provider declared by the installed `providers.json` has a `SKILL.md`;
2. the framework and provider roots contain no `*.py` files.

This is an evaluation preflight only. It does not alter Agentic Workflow,
provider bytes, benchmark tasks, or verifiers.

## Preserved vanilla evidence and infrastructure issues

The A run was interrupted at this gate rather than allowed to consume more
credits. `circuit_eval` checkpoint 1 had already completed and remains preserved
in `evals/harbor/jobs/2026-08-15-slopcodebench-a/`:

- functionality: 15/15 tests passed;
- core: 9/9 passed;
- error cases: 12/12 passed;
- strict pass rate: `1.0`;
- erosion: `0.6575266820229108`;
- verbosity: `0.34177215189873417`.

Checkpoint 2 was active when the trial was cancelled, so this is not a completed
task result and must not be compared with B. The partial trajectory at
cancellation recorded 250,785 prompt tokens, 221,952 cached tokens, 5,870
completion tokens, 18 agent steps, and USD 0.431241; those totals include work
from the interrupted checkpoint 2 and are not checkpoint-1-only metrics.

After cancellation, Harbor's dataset aggregation attempted to invoke host
`uv`, which is absent, and exited with an infrastructure error. The already
written checkpoint reward and trajectory artifacts were retained. Install
host `uv` before resuming so the source-owned aggregate metric can run unchanged.

## Resume gate

Before any scored B run:

1. make a supported `gh skill` installation capability available inside the
   actual Harbor task environment;
2. use an install-only B trial to prove `14 present, 0 missing, 0 incompatible`;
3. prove the installed Agentic Workflow/provider roots contain zero Python
   files;
4. install host `uv` for the unchanged SlopCodeBench aggregate metric;
5. restart the paired scored runs from clean workspaces while retaining, but not
   counting, the interrupted vanilla artifacts.

Until those checks pass, the experiment is paused at an infrastructure
compatibility gate. It is not classified as product/benchmark incompatible,
because the complete installed product was directly shown to satisfy the
no-Python constraint.
