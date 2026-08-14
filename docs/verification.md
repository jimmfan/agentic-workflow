# Verification model

`verify_package.py` is the release and adoption gate. It validates required
files, skill metadata, inert payload placement, version equality, explicit
source-to-target mappings, exact checksums, provider pin/declaration integrity,
provider/host invocation semantics, configuration dependencies, prerequisite
documentation consistency, forbidden runtime components, package-local links,
and installed-skill references. With `--tests`, it also runs lifecycle and
decision-contract tests in ordinary temporary projects and a temporary Git
repository.

The gate also validates the VS Code reference hook schema, host capability
matrix, controller runtime contract, and executable controller scenarios for
fresh-prompt protocol bootstrap, exact-declaration auto-approval, route
checkpointing/reset, opaque terminal actions, diagnosis-only write denial,
truthful provider execution, durable-state conflicts, verification evidence,
metadata privacy, and bounded Stop behavior. These tests prove controller/package
behavior; they are not live validation inside VS Code, Codex, Claude Code,
Copilot CLI, or Copilot cloud.

The workflow contract check separately enforces the compact root-policy budget,
the six audited universal hard invariants, progressive-loading pointers, and the
complete installed `.ai-workflow/routing.md` contract. Lifecycle tests inspect
the composed installed `AGENTS.md`, not only its source template.

The static provider gate requires the reviewed `mattpocock/skills` repository,
tag `v1.2.3`, curated capability mapping, semantic minimum GitHub CLI 2.97.0 or
newer, unique upstream paths, and no name overlap with local skills. It validates
the declared host/invocation matrix and configuration relationships without
duplicating upstream tree SHAs or complete file inventories. It proves that
to-spec and to-tickets require triage-label
configuration, setup provisions it only through the installed `triage`
dependency, and triage is not a routed capability. Exact requirements are frozen
for every selected skill, including Wayfinder's domain/tracker requirements,
Code Review's tracker requirement, and `implement`'s effective tracker
requirement through its mandatory closing review. It also checks that the local
Implementation adapter delegates TDD and Code Review rather than copying their
procedures.

The integration suite covers:

- fresh one-command bootstrap with compatible provider fixtures and successful
  framework installation when optional provider prerequisites are unavailable;
- payload install/update post-checks inside the file transaction, exact
  byte/mode restoration on failure and preservation of pre-existing empty parent
  directories;
- missing GitHub CLI and unauthenticated CLI diagnostics before writes;
- pinned provider installation, required metadata, representative adjacent resources,
  installer serialization changes, recorded installed-file hashes, idempotency,
  local-only inner status checks, and safe removal;
- implicit and user-only invocation declarations, truthful host-native fallback,
  explicit-provider blocking, and required metadata mismatch rejection;
- rejection of unknown same-named directories and preservation of locally
  changed provider skills;
- rejection of incompatible pins, missing recorded resources, provider-state
  path injection, and unowned path collisions;
- declaration-change updates that preserve clean retained origins, add a missing
  dependency, replace only checksum-clean locally owned directories, recreate a
  missing directory, aggregate conflicts before staging, and preserve modified
  or pre-existing content;
- fresh and pre-existing composite root policy ownership, authenticated
  restoration of an exact pre-existing `AGENTS.md` across managed-source
  updates, migration of previous fully-owned policy records, and preservation
  of legitimate project/setup edits through status, update, and removal;
- fail-closed payload conflicts, tamper detection, and checksum-authenticated
  update/removal;
- local ownership-record checks across versions and revision-independent
  status/removal, with current-byte conflicts blocking mutation;
- independent framework/provider transactions, including payload rollback and
  optional-provider failure that leaves the valid framework usable;
- migration that retires the local Teach, Decomposition, and Review copies plus
  obsolete learning/ticket templates only when unchanged;
- reconstructable `.ai-workflow/` installation content across fresh install,
  status, update, removal, and reinstall; durable `.ai-workflow-state/`
  byte-preservation; validated update-only migration from `ai-workflow/`;
  dual-directory conflict rejection; and repository-local isolation;
- empty canonical state-directory creation on clean install and repeated update;
  no seeded profile or active file; permissive missing/present/empty/unreadable/
  unsafe profile states; byte-preserving lifecycle operations; lazy authorized
  profile and active-state creation; strict existing active-state handling;
  narrow migration of the four known development-era durable paths with conflict
  rejection; integrity-first status output; progressive profile guidance; and
  target `docs/` preservation;
- installation without Git metadata or a Git executable;
- path-independent package copies and a local archive bootstrap fixture; and
- strict POSIX modes plus bounded native Windows mode normalization; and
- install, update, status, verification, bootstrap, provider status, and error
  output under a strict `cp1252` console simulation, including non-encodable paths.

Three semantic scenario files cover route observability, end-to-end acceptance,
and decision contracts. The verifier requires categories rather than a fixed
scenario count. Coverage includes direct work with missing setup, Wayfinder plus
Research composition, standalone Research/Debugging, user-only and setup
handoffs, read-only Discovery, named external reads, denied external mutation,
active-state conflict, and provider-native artifact ownership. A negative test
also mutates prerequisite documentation and proves version drift fails the
release gate.

Tests use hermetic provider directory fixtures rather than calling GitHub. Live
release research separately verifies the real GitHub CLI behavior against the
pinned public upstream repository: exact-path project install, complete
directory copying, injected metadata, idempotency, and pin behavior. This split
keeps ordinary tests deterministic while preserving a documented live
compatibility check before changing the provider baseline.

Some migration tests create synthetic old packages to isolate planner behavior.
Updates consume those fixtures' ordinary installed ownership records; no
historical predecessor catalog is synthesized.

## Run the checks

From the **macOS host Terminal at this repository root**, refresh generated
manifest data only after an intentional payload or `VERSION` change. This is a
persistent source-repository change. It derives current payload checksums and
does not discover or serialize historical predecessor identities:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --refresh-manifest
```

Then run the full suite from the **same repository root**. This check is
read-only for the repository apart from automatically removed Python/runtime
temporary files:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

Success ends with:

```text
OK: distributable package is internally consistent.
```

If it fails, the first named invariant or failing lifecycle test is the most
useful diagnostic. Do not refresh the manifest merely to hide an unexplained
checksum failure; inspect the changed payload first.

## Interactive host verification

Static checks cannot prove that a running editor discovered instructions. In a
fresh non-production target, run the public bootstrap from the environment that
owns that target, then start a new host session.

For the primary VS Code reference check, use a trusted disposable workspace and
confirm that `.github/hooks/agentic-workflow.json` appears in the Agent
Customizations hooks view. Open **Developer: Show Agent Debug Logs** and verify
that SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, and Stop load.
Start a new chat with “Inspect the recent git history and summarize what
changed.” Confirm that Copilot records a direct/read-only checkpoint before
`git log`, that the checkpoint declaration's PreToolUse result is `allow`, and
that no **Run bash command?** prompt appears for the checkpoint. Any prompt for
the actual `git` command is governed by VS Code and is not a framework failure.
Then submit a second prompt and confirm the first route is reset and the next
checkpoint is again accepted without a preliminary denial. Exercise one
diagnosis-mode native write denial and one required-verification Stop
continuation. Record the VS Code/Copilot version and whether organization policy
enables hooks. This manually validates the Preview host surface and must be
reported separately from the hermetic release gate. Removing the disposable
workspace reverses the test; no production project should be used.

For GitHub Copilot, inspect Chat Diagnostics or the agent customization view and
confirm root `AGENTS.md` plus the four local and fourteen upstream skill
directories. For Codex, start a fresh task in the installed project and confirm
the root policy and project skills are present in task context. These checks are
read-only for the installed files but may add prompts to the signed-in product's
chat history.

Automated checks do not launch either host. In a disposable initialized target,
repeat this semantic smoke suite in both a fresh Codex task and a fresh VS Code
GitHub Copilot agent-mode chat. Use ordinary wording; only the expected handoff
step uses skill syntax.

| Scenario | Expected behavior |
|---|---|
| Simple bounded change or explanation | Direct; no readiness gate or workflow state write |
| Foggy multi-session architecture effort | Prefer Wayfinder when invoked; otherwise plan host-natively without claiming provider execution |
| Foggy architecture effort needing current evidence | Select Wayfinder with Research as a capability; preserve the dominant-workflow distinction |
| Standalone substantive research | Research is dominant and may execute implicitly |
| Existing unexplained failure | Local Debugging is dominant; diagnosis does not authorize a fix |
| Explicit sustained learning request | Prefer Teach when invoked; otherwise teach host-natively and add state only if continuity needs it |
| Configuration-dependent request with setup files absent | Select setup and return the exact setup handoff; write nothing before invocation |
| Healthy project with no durable state | Keep `.ai-workflow-state/` empty, report `ready / none active`, and say `No action required.` |
| Verified durable project fact discovered during authorized work | Create or update one concise profile entry; do not rescan the repository |
| Read-only bounded decision analysis | Use Discovery ephemerally; leave profile, active state, and decision records byte-identical |

When a response includes an optional route diagnostic, compare it with the
semantic expectation in the scenario files. Absence of a marker is normal and
does not invalidate successful work. Additional discovered Chat References are
allowed; they must not appear in a diagnostic unless materially used. Before and after the read-only case,
compare the target's version-control diff or file hashes to prove no repository
state changed.

Provider compatibility should also be exercised in a disposable non-Git
directory with an authenticated GitHub CLI before changing the declared
baseline. Confirm that the installed skill includes required adjacent resources,
frontmatter contains the declared path/ref, and installer-transformed
serialization is accepted and recorded. Fresh adoption rejects every same-named unowned directory,
repeating install is idempotent, inner status is clean and local, and removal
preserves locally modified content.

## Reversal and cleanup

Temporary directories created by the automated suite are removed automatically.
For a manual disposable-target check, run the documented framework `remove`
command from that target before deleting the disposable directory. If removal
preserves a pre-existing or modified skill, review it explicitly rather than
forcing deletion. Never remove `provider-state.json` first: it is the ownership
and installed-byte history needed for bounded update and removal. It is not
tamper-evident; coordinated state forgery can reclassify provider bytes. The
package declaration still bounds repository, tag, paths, invocation policy, and
configuration requirements; ordinary modified, extra, undeclared, and unique
project content remains protected.

## Continuous integration

`.github/workflows/verify.yml` runs the same hermetic `--tests` gate on pull
requests and pushes to `main`, using the minimum supported Python 3.11 on Linux
and Windows. The jobs need only normal source checkout access: they use local
provider fixtures and do not authenticate GitHub CLI, install live skills,
launch Codex/Copilot, collect telemetry, or mutate an external system. A green
workflow therefore proves package contracts on those runners, not live host
discovery or behavioral compliance; the interactive suite above remains the
host acceptance boundary.
