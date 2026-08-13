# Acceptance verification

`acceptance-scenarios.json` is the reviewable specification for 32 core
scenarios: the original 24 plus durable decomposition/frontier, coherent-session
bypass, invalid dependency graphs, diagnosis-only, optional TDD, proportional
independent review, review feedback loops, and canonical-workflow coverage.
Automated verification checks its completeness and validates the
static, state, safety, domain-separation, and adoption properties that can be
proven without a running language model.

`hermes-acceptance-scenarios.json` is the separate reviewable specification for
the 30 Codex-first and optional-Hermes integration scenarios. Its IDs map
one-to-one to scenarios 1 through 30 in the refinement request; the original 18
scenarios remain present in `acceptance-scenarios.json`.

`hermes-repo-read-scenarios.json` records the compatibility gate added after the
app-server source audit. The first case is an executable fail-closed behavior,
the second is pinned source/protocol evidence, and the third is a future release
gate—not a claim that local Hermes inspection currently works.

`hermes-learning-scenarios.json` covers the separate self-improvement boundary:
private memory may be automatic, learned skill writes are approval-staged,
curator artifacts stay in the dedicated profile, and promotion into shared
repository policy/state remains a separate reviewable parent-Codex action. These
are static/profile and parent-policy checks; they do not claim that the uninstalled
Hermes runtime completed a live background review.

Every integration scenario uses the same required flat schema:

* `id`, `requirement`, `prompt`, and `setup` identify the requested case and its
  fixture;
* `expected_runtime` names the intended owner/path: `codex`,
  `codex-native-subagent`, `codex-hermes-codex`, `hermes-codex`, or `framework`;
* `expected_route` gives the policy route independently of the runtime;
* `expected_behavior`, `expected_safety_outcome`, and
  `expected_result_outcome` separate process, safety, and useful-result claims;
* `evaluation_category` is one of `manual-codex`, `adapter-simulation`,
  `static-analysis`, `live-hermes`, or `manual-cross-runtime`;
* `evaluation_method` says exactly how the result can honestly be established;
  and
* `evidence` lists what must be retained in the verification report.

An `adapter-simulation` result proves deterministic adapter behavior against a
controlled executable, not successful installation, authentication, provider
selection, or live Hermes behavior. A `static-analysis` result proves only
repository structure/configuration. `manual-codex` requires a fresh Codex task.
`live-hermes` requires the documented compatible Hermes version and a tested
OpenAI/Codex-backed authentication path. `manual-cross-runtime` additionally
requires a supported Hermes-top-level-to-Codex mode. Record a live case as
`not-run`, with its unmet prerequisite, rather than treating a simulation as a
live pass.

Run `python3 scripts/verify_framework.py` in the **macOS host Terminal** with this
repository as the current directory. It is read-only except for temporary test
repositories that Python creates in the system temporary directory and deletes
automatically. Success ends with `OK: all framework verification checks passed.`

Semantic Copilot routing and customization discovery require a manual check. Open
a disposable consuming-project copy as the VS Code workspace root, start a fresh
Chat for each scenario, submit its exact `prompt`, and prepare its `setup` only in
that disposable copy. Inspect Chat **References**, filesystem changes, and the
response against `expected_behavior` and `evidence`. Do not execute example
external or destructive commands; scenario 13 succeeds when Copilot requests
approval or reports them skipped.

Before the scenarios, right-click Chat and choose **Diagnostics**. Confirm the
root policy and all eight skills load without errors and appear in the `/` menu
(seven core workflow skills plus the optional Hermes skill). If the command is
unavailable, use **Developer: Open Agent Debug Panel** or Chat's **Show Agent
Debug Logs**. Static success does not substitute for this UI check.

For state scenarios 4, 10, and 11, copy the templates into the disposable
project, use non-sensitive fictional records, and inspect each transition before
resetting the fixture. For scenario 14, use one example profile at a time without
editing `.github/` files. Record observed route, loaded references, state diff,
commands attempted, and pass/fail for each ID. If behavior diverges, the most
useful diagnostic is the Chat Diagnostics load/error report followed by the exact
skill description and state file referenced by that scenario.

For scenarios 25–27, start from an approved canonical specification in a
disposable project. Exercise local tickets first. For the native-ticket branch,
use a separately configured disposable tracker only after explicitly authorizing
the previewed external writes; otherwise record that branch as not run. Build
four graph fixtures for scenario 27: one missing dependency, one self-edge, one
cycle, and one incomplete graph with no ready frontier. Preserve each failed
fixture and confirm no ticket is selected or silently rewritten.

For scenario 28, snapshot the disposable repository before and after the
diagnosis-only task; creating a record or temporary instrumentation is a failure.
For scenario 29, use the application and infrastructure profiles separately and
record why the chosen feedback loop supplies the strongest signal. For scenarios
30–31, use a fresh read-only review task or bounded reviewer when the host
supports it, then record the parent’s independent finding dispositions and any
rerun evidence. Scenario 32 must not install or emulate the unavailable upstream
skills; confirm the local canonical specification and workflow remain the only
artifacts.

For optional-Hermes scenarios, perform `static-analysis` and
`adapter-simulation` checks first in automatically deleted temporary repositories.
Use only fake credential sentinels and instrumented executable doubles; never
copy or print a real token. Scenarios 4, 11, and 17 have live-runtime aspects.
Run them only after the compatibility, profile, and official authentication
preconditions have independently passed. Compare a complete repository snapshot
before and after each live delegation, and preserve only sanitized contracts and
concise results. A real mutation, recursive call, credential disclosure, unsafe
flag, provider substitution, or unsupported success claim is a failure, even if
the delegated process exits zero.
