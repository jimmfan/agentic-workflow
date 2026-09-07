# Verification model

Verification covers the current package and its observable boundaries.
It does not preserve or prove former installations.

## Consumer safety

`bootstrap.py` is the public download boundary.
Its default ref is the release tag with the highest stable semantic `vX.Y.Z` version; unrelated and prerelease tags are ignored.
An explicit ref such as `--ref main` is an opt-in development or testing override.
Before executing package code the bootstrap resolves the selected ref to an immutable commit, downloads one snapshot, and runs that snapshot's `agent_workflow/lifecycle.py` against canonical resources from the same repository root.
It rejects corrupt or oversized archives, excessive package contents, excessive whole-archive parsing, absolute, traversing, or duplicate paths, links, special entries, unreviewed modes, filesystem-root targets, and packages missing the minimum lifecycle files.
The archive is streamed, and unrelated repository entries do not consume the tighter distributable-source member allowance.
Extraction selects only the root `VERSION` file plus `agent_workflow/`, `.agent-workflow/`, and `.agents/skills/` beneath one snapshot root; an incidental nested lookalike is not a runtime source.

`lifecycle.py` is the only install, update, status, and remove implementation.
Explicit existing non-root target directories are used directly.
With no target, the CLI may use Git only to discover the containing worktree root and falls back to the current directory when discovery is unavailable.
Repository cleanliness, ignore rules, and `HEAD` are not lifecycle gates.
Before mutation the lifecycle rejects malformed managed markers and symlink, unsupported-entry, or escape hazards at managed roots and parents.
Nested entries inside a replaceable managed directory are removed through convergence.
`status` is read-only and compares managed surfaces against the selected snapshot, not a stored installed release.
Diagnostics distinguish the installed CLI version, selected framework ref/release and resolved SHA, and target directory.
A local archive override has no observed ref or SHA and reports them unavailable.
Exit codes remain 0 for healthy/success, 1 for status drift/conflict, and 2 for command/runtime errors.

Install and update replace every current curated skill directory after the concrete managed-path and composite preflight.
They do not recognize an existing installation, inventory collisions, inspect terminal state, or prompt.
Remove alone uses existing managed surfaces to refuse current curated-name collisions when installation ownership is otherwise unknown.
Ambiguous composite ownership continues to fail before mutation.

The lifecycle writes no installed manifest, hashes, provenance, created-state bits, migration history, backups, or rollback journal.
If a write fails after mutation begins, resolve the reported filesystem error and rerun the command to converge.
Lifecycle code does not directly traverse, interpret, or change `.project-efforts/`.

## Maintainer and CI gate

Run from the source repository root:
Lifecycle tests use disposable consumers under the [source-checkout ownership rule](../AGENTS.md#source-checkout-ownership).

```bash
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked python agent_workflow/verify_package.py --tests
uv run --locked python -m unittest discover -s evals/tests -p 'test_*.py' -v
uv run --locked python tests/wheel_smoke.py
git diff --check
```

The package verifier checks:

- required package structure, the current `VERSION` format and single-source boundary, and required files being regular non-symlink files;
- the ordinary current source-to-target distribution mapping;
- the exact canonical framework and fifteen-skill inventories and non-active composite template locations;
- canonical `.agent-workflow/terminology.md` distribution;
- skill frontmatter, canonical support-file closure, local links, checked-in composite managed regions, and complete attribution for retained derived skills; and
- local documentation links.

Package validity depends on structure, distribution integrity, safety, attribution, and machine-readable contracts.
Ordinary instruction wording and terminology definitions are not package interfaces.
Routing and Wayfinder behavioral tests challenge observable outcomes in the existing scenario harness; deterministic evaluator tests do not establish live-agent compliance with those instructions.
The `--tests` option also runs the deterministic lifecycle, bootstrap, routing, behavior-harness, Wayfinder, and verifier suites.

Success ends with:

```text
OK: Agent Workflow package verification passed.
```

The `evals/` unit tests are a separate deterministic, network-free step because evaluation tooling is not part of the distributed package.
The wheel smoke test copies current tracked and unignored source, including pending edits and canonical dot-directories, while excluding temporary environments and build outputs.
It builds an sdist and then a wheel from that archive, checks the root `VERSION`, required build inputs, licensing material, and intended wheel contents, installs into an isolated environment, and exercises all four commands outside checkout imports against local snapshot resources.
The explicit `packages = ["agent_workflow"]` selects the Python package without automatic discovery; `include-package-data = false` and the explicit `install/*` package-data pattern select its install resources.
Setuptools may include ordinary tests or documentation in the sdist without installing them in the wheel; source-archive minimality is not a requirement.
The wheel contains only the intended Python package and install resources plus distribution metadata and licensing material.
See [setuptools file selection](https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html) and [package data](https://setuptools.pypa.io/en/latest/userguide/datafiles.html) for these distinct boundaries.
The temporary repository-snapshot archive used for lifecycle commands is separate from the Python sdist and retains the canonical framework and skill resources.
It proves that canonical framework and skill resources need not be bundled in the wheel, `evals/token_forensics/` remains outside the runtime package, and installation creates no `.project-efforts/` state.
The local snapshot exercise is deterministic; building may need network access for build dependencies that are not already cached.
The lockfile-drift smoke prepares a fresh cache with a successful locked run of the source snapshot, then removes a development dependency only in that disposable copy.
An offline locked run must reject the changed inputs without executing its command or rewriting `uv.lock`; the test does not rely on registry metadata left in the maintainer's or CI runner's cache.

## Distribution-map refresh

After intentionally adding, removing, or remapping a packaged file, inspect the diff and run:

```bash
uv run --locked python agent_workflow/verify_package.py --refresh-manifest
uv run --locked python agent_workflow/verify_package.py --tests
```

Refresh rewrites only `agent_workflow/install/manifest.json`.
Ordinary content edits to an already mapped file do not require a refresh.
Manifest sources resolve from the repository snapshot root.
The manifest is a current source-to-target map, not installed state and not a content-hash or retirement ledger.

## Lifecycle acceptance boundary

The deterministic suite proves that:

- install and update converge to the same current state by replacing the full `.agent-workflow/` directory and all current curated skill directories;
- terminology follows framework install, status, repair, and removal behavior while project-owned `CONTEXT.md`, `CONTEXT-MAP.md`, and per-context files retain their bytes;
- obsolete or extra content inside `.agent-workflow/` is removed by ordinary desired-state replacement without a preliminary cleanup commit;
- extra files inside a current curated skill directory are removed, while unrelated skill directories remain unchanged;
- first installation replaces one or multiple existing current curated-name directories without prompting, including during noninteractive execution;
- stale pre-1.0 framework content and modified current curated skills converge in one install or update without recognition, while unrelated skills, `.project-efforts/`, and project-authored composite bytes remain preserved;
- repeated install and update leave exactly one managed block in `AGENTS.md` and `CLAUDE.md` while preserving project-authored bytes byte-for-byte; both accept logical LF or CRLF marker lines and narrowly recover the evidenced historical duplicate, while `AGENTS.md` uses only managed-begin/managed-end delimiters and the existing `CLAUDE.md` output protocol remains unchanged;
- remove deletes recognized managed directories and regions, deletes a composite file only when no project-authored bytes remain, preserves unrelated skills, and refuses current curated-name collisions on an unrecognized target;
- lifecycle commands do not directly traverse, interpret, or change `.project-efforts/`;
- plain non-Git targets, invalid or missing `HEAD`, explicit nested targets, and dirty tracked, untracked, or ignored repository state do not block mutation;
- an omitted target inside a Git worktree resolves to that worktree root when discovery is available, while an explicit target is never rewritten;
- unsafe managed root or parent entries and malformed markers stop mutation before any write, while nested entries inside replaceable directories are removed without following symlinks;
- `status` remains read-only and has no repository-wide Git safety concept;
- a deliberately injected later write failure reports possible partial changes and directs the user to resolve the filesystem error and rerun convergence rather than claiming rollback;
- skill directories outside the current curated inventory are preserved without consulting a historical retirement list; and
- bootstrap archive and root-safety boundaries remain enforced offline;
- default bootstrap discovery chooses the highest stable semantic release, resolves it to a commit, and fails clearly when no stable release exists;
- a bootstrap using the current layout can install a simulated newer stable framework release without a CLI upgrade, with lifecycle and content taken from the same downloaded snapshot; and
- explicit branch, tag, or commit refs bypass stable-release discovery.

Wayfinder's state and behavioral tests remain separate from lifecycle tests.
Literal fixture checks cover IDs, references, and preservation in explicit before/after examples.
Scenario evaluator tests challenge map-first outcomes, reconciliation, and authority, but do not establish agent selection, reads, concurrent mutation checks, or no-overwrite execution.
The [coverage ledger](../tests/README.md#wayfinder-coverage-and-evidence-limits) distinguishes retained checks from unverified instruction requirements.

## Release tags

The repository-root `VERSION` is the sole authored framework version and the human-controlled `x.y.z` release switch.
Python distribution metadata derives from this file; the wheel contains no authored version-file copy.
The selected repository snapshot supplies its own root `VERSION` to bootstrap, and lifecycle does not install it into consuming projects.
PR verification checks the explicit PR base/head revisions with fetched tags and read-only remote tag observation.
The shared release policy accepts canonical `x.y.z`, requires an increase over both base VERSION and existing semantic release tags, and treats unchanged VERSION as no release.
After all three deterministic jobs succeed on a push to `main`, publication revalidates that policy and creates one annotated release tag on that exact verified commit.
An already published annotated remote tag resolving to that commit is a successful retry; conflicting types or commits fail.
A local-only matching tag remains pending and can be pushed again after a failed push; it never counts as successful publication.
Tags are never forced, moved, or rewritten.

Do not create a release tag while preparing a branch; the verified `main` workflow owns tag creation.
The repository-layout release requires one CLI reinstall because earlier bootstraps hard-coded the former archive path.
See the [one-time reinstall instructions](../README.md#one-time-reinstall-for-the-repository-layout-release); after that, ordinary updates remain one command.

## Failure diagnostics and limits

Use the first reported error or failed test as the primary diagnostic.
For a mapping mismatch, inspect the source and target inventories before refreshing.
For a lifecycle failure, inspect the exact reported managed path or filesystem error; never delete project files merely to make a test pass.
Generated Python caches are ignored by Git and package verification and need no manual cleanup.

The minimum Python 3.11 gate runs on Ubuntu; Python 3.14 adds the current stable interpreter gate.
A focused macOS Python 3.11 job exercises bootstrap, lifecycle, direct distribution, and the built CLI.
Release publication waits for all three jobs.
These are configured coverage targets, not evidence of an unexecuted hosted run.
macOS, Linux, WSL, and Linux-based devcontainers with a POSIX-style shell are supported; native PowerShell and CMD are not.
Live model runs remain opt-in and must be reported separately.
Static verification does not prove live host or editor skill discovery, external tracker behavior, or authenticated publication.

See [Behavioral testing](behavioral-testing.md) for behavioral scenario evidence, commands, side effects, and limitations.

## Dependency and action updates

`uv run --locked` rejects unexpected lockfile drift.
The isolated builds use `setuptools.build_meta` with the existing `setuptools>=68` build requirement; the backend is not pinned separately.
The committed project lockfile and isolated build-dependency selection solve different problems: build-tool selection can change over time, so these are not fully locked or bit-for-bit reproducible builds.
Verify clean builds without inherited constraint overrides when checking this boundary.
See [uv builds](https://docs.astral.sh/uv/concepts/projects/build/) and [setuptools build requirements](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html#build-system-requirement).
The Python 3.11 minimum remains unchanged.

For a dependency update, change the declared requirement intentionally, refresh `uv.lock` only when its inputs changed, inspect the diff, and run the commands above.
For an action update, inspect the official release notes, resolve the chosen release with `git ls-remote <official-repository> refs/tags/<version>` (and its peeled ref for an annotated tag), and update every occurrence of the full SHA and release comment together.
Do not follow a moving major tag or make an unrelated major upgrade.
GitHub recommends [full commit SHA pins](https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions).
Python 3.14 is the stable line on the [official release list](https://www.python.org/downloads/); revisit that one job when a new stable minor is released.
