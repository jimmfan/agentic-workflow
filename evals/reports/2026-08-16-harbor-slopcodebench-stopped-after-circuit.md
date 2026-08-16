# Harbor SlopCodeBench evaluation: stopped after the circuit pair

## Conclusion

The benchmark was stopped by human direction on 2026-08-16 after one valid
paired task. No database or trajectory pair completed, so this is not the
planned three-task experiment and does not support a broad product conclusion.

On the completed `circuit_eval` pair, Agentic Workflow did **not** improve
externally graded correctness. Vanilla A kept a `1.0` mean core pass rate;
Agentic Workflow B fell to `0.985294` because it passed 15/17 core tests at the
final checkpoint while A passed 17/17. B also had lower mean isolated and
strict pass rates. B produced lower measured code erosion and verbosity, but at
higher time, token, tool-call, and dollar cost.

The narrow classification is **no demonstrated advantage yet** for the one
completed pair. The overall stopped experiment is **inconclusive** because only
one of three preregistered pairs ran. No product change is justified from this
evidence.

## What was actually tested

Both circuit arms used Harbor `0.21.0`, Codex CLI `0.144.6`, model
`gpt-5.6-sol`, high reasoning, the same Linux/arm64 Docker task environment,
one attempt, zero retries, one concurrent trial, timeout multiplier `1.0`, and
the immutable task
`sha256:3bbbb4e0f03cc0824f4a77d0e1ab15004eebb01b8774488dd130f0508321a700`.
Each checkpoint used a fresh Codex session against the evolving workspace.

Condition A was vanilla Codex with Agentic Workflow absent. Condition B was
Agentic Workflow `0.11.1` from frozen revision
`37e35b0be95b1b835f460af15187c91d915ca4dc`, installed through the normal
lifecycle with all 14 declared `mattpocock/skills@v1.2.3` providers present,
zero missing or incompatible providers, and no workflow/provider `*.py`
contamination in application scoring roots. The task and verifier inputs were
shared immutable packages and were not edited.

## Circuit result

| SlopCodeBench aggregate | Vanilla A | Agentic Workflow B | B minus A |
| --- | ---: | ---: | ---: |
| Core pass rate mean | 1.000000 | 0.985294 | -0.014706 |
| Isolated pass rate mean | 0.988095 | 0.980783 | -0.007312 |
| Strict pass rate mean | 0.999086 | 0.997377 | -0.001709 |
| Erosion mean | 0.717174 | 0.662147 | -0.055027 |
| Erosion increase rate | 4/7 (0.571429) | 3/7 (0.428571) | -1 checkpoint |
| Verbosity mean | 0.344762 | 0.329988 | -0.014774 |
| Verbosity increase rate | 4/7 (0.571429) | 2/7 (0.285714) | -2 checkpoints |

The lower erosion and verbosity values are favorable structural signals, but
they did not translate into better externally graded behavior.

### Checkpoint detail

| Checkpoint | A core | B core | A isolated | B isolated | A strict | B strict | A erosion | B erosion | A verbosity | B verbosity |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.601555 | 0.700706 | 0.240829 | 0.340289 |
| 2 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.556370 | 0.678281 | 0.220472 | 0.306966 |
| 3 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.738636 | 0.654496 | 0.353245 | 0.351371 |
| 4 | 1.000000 | 1.000000 | 1.000000 | 0.995556 | 1.000000 | 0.997674 | 0.795483 | 0.669251 | 0.402621 | 0.335570 |
| 5 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.997812 | 0.789647 | 0.675217 | 0.401624 | 0.374019 |
| 6 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.998031 | 0.737473 | 0.645874 | 0.365217 | 0.323509 |
| 7 | 1.000000 | 1.000000 | 0.904762 | 0.904762 | 0.996219 | 0.994329 | 0.745572 | 0.614819 | 0.369444 | 0.311341 |
| 8 | 1.000000 | 0.882353 | 1.000000 | 0.945946 | 0.996466 | 0.991166 | 0.772657 | 0.658533 | 0.404645 | 0.296843 |

At checkpoint 8, A passed 17/17 core, 37/37 isolated, and 564/566 strict
tests. B passed 15/17 core, 35/37 isolated, and 561/566 strict tests. Both arms
missed the same two invalid-seed error cases inherited from checkpoint 7. B
additionally regressed a checkpoint-4 width-one three-valued-vector behavior and
failed two checkpoint-8 absorption postconditions. Those are real graded
regressions; the scores are preserved exactly as emitted.

## Cost and trajectory activity

| Observed cost | Vanilla A | Agentic Workflow B | B relative to A |
| --- | ---: | ---: | ---: |
| Wall time | 3,336.223 s | 4,032.980 s | +696.757 s (+20.9%) |
| Input tokens | 7,627,106 | 10,380,675 | +2,753,569 (+36.1%) |
| Cached input tokens | 7,131,392 | 9,708,032 | +2,576,640 (+36.1%) |
| Output tokens | 130,452 | 158,603 | +28,151 (+21.6%) |
| Reasoning output tokens | 45,569 | 57,464 | +11,895 (+26.1%) |
| Harbor ATIF top-level tool calls | 163 | 186 | +23 (+14.1%) |
| Recorded cost | $9.957826 | $12.975321 | +$3.017495 (+30.3%) |

Tool calls are the reliably available top-level ATIF calls emitted by Codex;
they are not a reconstruction of every nested shell action.

## Which workflow behavior activated

Wayfinder did not activate. This is an important treatment boundary, not a
missing-provider problem: B had the full 14-provider installation, but the
frozen current configuration declares `wayfinder` as `user-only` for Codex.
The SlopCodeBench prompts did not explicitly invoke `$wayfinder`, so Wayfinder
was not implicitly or automatically routable. No Wayfinder map or U/D/T state
was created.

The local `workflow-implementation` adapter did route the settled checkpoint
work, and the local independent verification skill was used. The upstream
`implement` provider is also declared `user-only`; because the benchmark did
not explicitly invoke `$implement`, every checkpoint truthfully used the
host-native implementation fallback rather than claiming upstream provider
execution. The B trajectory therefore measures the current installed product's
normal routing/verification behavior under these prompts, but not Wayfinder or
the upstream `implement` methodology.

The trajectory suggests a plausible mechanism for both the cost and the mixed
outcome: B repeatedly loaded routing/provider policy, ran additional acceptance
audits, and added broader local tests. This coincided with lower structural
erosion from checkpoint 3 onward, but the final verification still failed to
catch three externally graded behaviors that A preserved or implemented.
Because this is one stochastic pair, that mechanism is an observation, not a
causal estimate.

## Database infrastructure failure and repair work

No valid database score exists.

The first database A scored command produced job
`2026-08-15-slopcodebench-database-migration-a-validated`, but Docker failed
before the image existed, Codex started, or a checkpoint ran. The immutable
task Dockerfile pins Node 22.12.0 while installing `npm@latest`; on 2026-08-16
that resolved to npm 12.0.2, whose engine requirement rejected Node 22.12.0.
Harbor recorded one infrastructure `RuntimeError`, zero evaluated trials, no
tokens, and no score. This artifact must not be interpreted as condition A.

Evaluation-only repair work then:

1. created a derived Dockerfile whose nonempty instructions match the immutable
   source except for pinning npm 11.16.0; npm's official package metadata says
   that release supports Node `^20.17.0 || >=22.9.0`, which includes 22.12.0
   ([npm v11.16.0 package.json](https://raw.githubusercontent.com/npm/cli/v11.16.0/package.json));
2. added a custom Harbor Docker adapter that verifies the original task
   Dockerfile SHA-256 and the derived image's provenance labels before use;
3. built Linux/arm64 image
   `sha256:a9c5988d414f33115abaeaccc53746625320c5b07978ad628193f2d97fdb34e0`;
4. ran an A install-only smoke, which failed before inference because the task
   exports `NVM_DIR=/usr/local/nvm` while Harbor's Codex installer loads
   `$HOME/.nvm`;
5. added an evaluation-image-only symlink bridging those paths, rebuilt image
   `sha256:a9b52d91d7220dff045e2252bf95cf4e108ce7d5087721ca872d27f17c6f3db2`,
   and started a second A install-only smoke;
6. interrupted that smoke immediately on the user's stop request. Harbor's
   unfinished result marks it cancelled; no task prompt or verifier score was
   produced. The exact leftover container was stopped and retained rather than
   removed.

No database B scored run started. The second A install-only smoke did not reach
a completed proof, so the repair is preserved as unfinished infrastructure work,
not claimed as validated. The immutable task package, task instructions,
verifier, scoring logic, Agentic Workflow behavior, provider versions, and
provider contents were never modified.

## Comparison with earlier ARC evaluations

The circuit observation is directionally consistent with the corrected ARC v2
and state-complexity smokes in one respect: extra workflow structure and process
cost did not produce a better engineering outcome in the observed pair. It is
more negative on externally graded correctness because circuit B introduced
three additional final-checkpoint failures while A did not.

The treatments are materially different. Earlier ARC campaigns explicitly
tested Wayfinder or observed an automatic Wayfinder crossover under an older
treatment. This Harbor B condition used the current configuration in which
Wayfinder is user-only under Codex and was not explicitly invoked, so the
circuit result cannot confirm or refute Wayfinder's durable-state hypothesis.

## Stop state and evidence pointers

- Completed A result:
  `evals/harbor/jobs/2026-08-15-slopcodebench-circuit-eval-a-validated/result.json`
- Completed B result:
  `evals/harbor/jobs/2026-08-15-slopcodebench-circuit-eval-b-validated/result.json`
- Failed database image build:
  `evals/harbor/jobs/2026-08-15-slopcodebench-database-migration-a-validated/`
- Failed first database install-only smoke:
  `evals/harbor/jobs/2026-08-16-database-envfix-smoke-a/`
- Interrupted second database install-only smoke:
  `evals/harbor/jobs/2026-08-16-database-envfix-smoke-a-2/`
- Superseded earlier vanilla partial:
  `evals/harbor/jobs/2026-08-15-slopcodebench-a/`

No Harbor benchmark container or Harbor job process remained running after the
stop. No `trajectory_api` run started. No completed score was changed,
normalized, retried, or combined with partial evidence.
