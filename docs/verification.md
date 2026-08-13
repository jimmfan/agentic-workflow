# Verification model

`verify_package.py` is the release and adoption gate. It validates required
files, skill metadata, inert payload placement, version equality, explicit
source-to-target mappings, exact checksums, provider pin/declaration integrity,
forbidden runtime components, package-local links, and installed-skill
references. With `--tests`, it also runs lifecycle integration tests in ordinary
temporary projects and a temporary Git repository.

The static provider gate requires the reviewed `mattpocock/skills` repository,
tag `v1.2.3`, immutable commit, exact curated capability mapping, semantic
minimum GitHub CLI version, unique upstream paths, full subtree SHAs, sorted
complete file inventories, and no name overlap with local skills. It also checks
that the local Implementation adapter delegates TDD and Code Review rather than
copying their procedures.

The integration suite covers:

- fresh one-command bootstrap with payload and compatible provider fixtures;
- two-component preflight before writes and rollback after a simulated
  post-preflight provider failure;
- missing GitHub CLI and unauthenticated CLI diagnostics before writes;
- pinned complete provider installation, injected metadata, adjacent resources,
  idempotency, local-only status, and safe removal;
- preservation of pre-existing compatible and locally changed provider skills;
- rejection of incompatible pins, missing adjacent resources, and provider-state
  path injection;
- fresh and pre-existing composite root policy ownership;
- fail-closed payload conflicts, tamper detection, and checksum-authenticated
  update/removal;
- migration that retires the local Teach, Decomposition, and Review copies plus
  obsolete learning/ticket templates only when unchanged;
- project-owned seeds and target `docs/` preservation;
- installation without Git metadata or a Git executable;
- path-independent package copies and a local archive bootstrap fixture; and
- strict POSIX modes plus bounded native Windows mode normalization.

Tests use hermetic provider directory fixtures rather than calling GitHub. Live
release research separately verifies the real GitHub CLI behavior against the
pinned public upstream repository: exact-path project install, complete
directory copying, injected metadata, idempotency, and pin behavior. This split
keeps ordinary tests deterministic while preserving a documented live
compatibility check before changing the provider baseline.

## Run the checks

From the **macOS host Terminal at this repository root**, refresh generated
manifest data only after an intentional payload or `VERSION` change. This is a
persistent source-repository change:

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
confirm root `AGENTS.md` plus the four local and thirteen upstream skill
directories. For Codex, start a fresh task in the installed project and confirm
the root policy and project skills are present in task context. These checks are
read-only for the installed files but may add prompts to the signed-in product's
chat history.

Replay the five prompts in
`skills/agentic-workflow/tests/route-observability-scenarios.json` and compare
the exact final line with `expected_route_output`. Additional discovered Chat
References are allowed; they must not appear in the route unless materially
used.

Provider compatibility should also be exercised in a disposable non-Git
directory with an authenticated GitHub CLI before changing the declared
baseline. Confirm that all declared adjacent files appear, frontmatter contains
the declared path/ref/tree SHA, repeating install is idempotent, local status is
clean, and removal preserves any pre-existing compatible skill.

## Reversal and cleanup

Temporary directories created by the automated suite are removed automatically.
For a manual disposable-target check, run the documented framework `remove`
command from that target before deleting the disposable directory. If removal
preserves a pre-existing or modified skill, review it explicitly rather than
forcing deletion. Never remove `provider-state.json` first: it is the ownership
evidence that makes safe removal possible.
