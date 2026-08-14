# Verification model

`verify_package.py` is the release and adoption gate. It validates required
files, skill metadata, inert payload placement, version equality, explicit
source-to-target mappings, exact checksums, provider pin/declaration integrity,
provider/host invocation semantics, configuration dependencies, prerequisite
documentation consistency, forbidden runtime components, package-local links,
and installed-skill references. With `--tests`, it also runs lifecycle and
decision-contract tests in ordinary temporary projects and a temporary Git
repository.

The static provider gate requires the reviewed `mattpocock/skills` repository,
tag `v1.2.3`, immutable commit, exact curated capability mapping, semantic
minimum GitHub CLI 2.97.0 or newer, unique upstream paths, full subtree SHAs, sorted
complete file inventories, exact per-file source SHA-256 maps, and no name
overlap with local skills. It validates
Codex invocation modes against the exact pinned `agents/openai.yaml`, Copilot
modes against exact pinned `SKILL.md` frontmatter, and the complete declared
host matrix. It proves that to-spec and to-tickets require triage-label
configuration, setup provisions it only through the installed `triage`
dependency, and triage is not a routed capability. Exact requirements are frozen
for every selected skill, including Wayfinder's domain/tracker requirements,
Code Review's tracker requirement, and `implement`'s effective tracker
requirement through its mandatory closing review. It also checks that the local
Implementation adapter delegates TDD and Code Review rather than copying their
procedures.

A separately reviewed static digest freezes the provider repository, tag,
revision, every selected path and subtree SHA, and every file/source-hash map.
It is intentionally independent of generated distribution-manifest checksums:
`--refresh-manifest` cannot update it. Change that lock only after primary-source
review and live compatibility validation of the complete new provider identity.

The integration suite covers:

- fresh one-command bootstrap with payload and compatible provider fixtures;
- two-component preflight before writes and rollback after a simulated
  post-preflight provider failure;
- payload install/update post-checks inside the file transaction, exact
  byte/mode restoration on failure, manifest-derived seed rollback, and
  preservation of pre-existing empty parent directories;
- missing GitHub CLI and unauthenticated CLI diagnostics before writes;
- pinned complete provider installation, injected metadata, adjacent resources,
  canonical source hashes, idempotency, local-only inner status checks, and safe
  removal;
- implicit and user-only invocation declarations, selected-but-not-executed
  handoffs, unsupported-host behavior, and pinned metadata mismatch rejection;
- preservation of pre-existing compatible and locally changed provider skills;
- rejection of incompatible pins, missing adjacent resources, provider-state
  path injection, forged body checksums, forged extra-file inventories, and
  unknown old-state names during declaration changes;
- authenticated declaration-change migration that preserves clean retained
  origins, adds a missing dependency, replaces only checksum-clean
  predecessor-created directories, accepts a missing old directory, aggregates
  multiple conflicts before staging, and fails modified, pre-existing,
  malformed, or unknown ownership without mutation;
- fresh and pre-existing composite root policy ownership, authenticated
  restoration of an exact pre-existing `AGENTS.md` across managed-source
  updates, migration of previous fully-owned policy records, and preservation
  of legitimate project/setup edits through status, update, and removal;
- fail-closed payload conflicts, tamper detection, and checksum-authenticated
  update/removal;
- exact package-owned predecessor authentication across version, revision,
  installation-manifest schema, complete path set, and every source hash, plus
  negative cases for changed/omitted current records, forged retired paths, and
  unauthenticated composite-restoration bytes;
- coordinated update ordering that commits the payload inside the provider
  rollback window, with exact provider directory/state restoration when that
  callback fails;
- migration that retires the local Teach, Decomposition, and Review copies plus
  obsolete learning/ticket templates only when unchanged;
- the canonical uninitialized project-profile seed, readiness versus integrity,
  one-time/progressive profile rules, and target `docs/` preservation;
- installation without Git metadata or a Git executable;
- path-independent package copies and a local archive bootstrap fixture; and
- strict POSIX modes plus bounded native Windows mode normalization.

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
Their copied new package receives an explicit fixture-only accepted-predecessor
record derived from that installed fixture. This does not expand the production
predecessor table: production records remain the exact audited historical
release identities in the immutable package.

## Run the checks

From the **macOS host Terminal at this repository root**, refresh generated
manifest data only after an intentional payload or `VERSION` change. This is a
persistent source-repository change. It derives current payload checksums and
serializes already reviewed predecessor constants; it does not discover a
historical predecessor or update the separate provider identity lock:

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
| Foggy multi-session architecture effort | Select Wayfinder; return `$wayfinder` in Codex or `/wayfinder` in Copilot; do not claim execution |
| Foggy architecture effort needing current evidence | Select Wayfinder with Research as a capability; preserve the dominant-workflow distinction |
| Standalone substantive research | Research is dominant and may execute implicitly |
| Existing unexplained failure | Local Debugging is dominant; diagnosis does not authorize a fix |
| Explicit sustained learning request | Select Teach; return the host-specific user-only handoff |
| Configuration-dependent request with setup files absent | Select setup and return the exact setup handoff; write nothing before invocation |
| Mature repository with uninitialized profile | Report initialization guidance without treating package integrity as failed |
| Verified durable project fact discovered during authorized work | Offer or make one concise progressive profile update; do not rescan the repository |
| Read-only bounded decision analysis | Use Discovery ephemerally; leave profile, active state, and decision records byte-identical |

For every response, compare the final route line with the semantic expectation
in the scenario files. A handoff must use `<skill>-handoff`, not the unexecuted
skill name. Additional discovered Chat References are allowed; they must not
appear in the route unless materially used. Before and after the read-only case,
compare the target's version-control diff or file hashes to prove no repository
state changed.

Provider compatibility should also be exercised in a disposable non-Git
directory with an authenticated GitHub CLI before changing the declared
baseline. Confirm that all declared adjacent files appear, frontmatter contains
the declared path/ref/tree SHA, normalized files match the package-owned source
hashes, fresh adoption rejects a body-edited
same-metadata pre-existing skill, repeating install is idempotent, inner status
is clean and local, and removal preserves any authenticated pre-existing skill.

## Reversal and cleanup

Temporary directories created by the automated suite are removed automatically.
For a manual disposable-target check, run the documented framework `remove`
command from that target before deleting the disposable directory. If removal
preserves a pre-existing or modified skill, review it explicitly rather than
forcing deletion. Never remove `provider-state.json` first: it is the ownership
history needed for bounded removal. It is not tamper-evident content authority;
the exact recorded package declaration supplies content authority. Payload and
provider origin/restoration history is likewise local and not tamper-evident;
coordinated forgery can reclassify exact canonical bytes, while modified,
extra, undeclared, and unique project content remains protected.

## Continuous integration

`.github/workflows/verify.yml` runs the same hermetic `--tests` gate on pull
requests and pushes to `main`, using the minimum supported Python 3.11 on Linux
and Windows. The jobs need only normal source checkout access: they use local
provider fixtures and do not authenticate GitHub CLI, install live skills,
launch Codex/Copilot, collect telemetry, or mutate an external system. A green
workflow therefore proves package contracts on those runners, not live host
discovery or behavioral compliance; the interactive suite above remains the
host acceptance boundary.
