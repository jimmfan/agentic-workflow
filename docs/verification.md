# Verification model

Verification covers the current package and its observable boundaries. It does
not preserve or prove former installations.

## Consumer safety

`bootstrap.py` is the public download boundary. Its default ref is the release
tag with the highest stable semantic `vX.Y.Z` version; unrelated and prerelease
tags are ignored. An explicit ref such as `--ref main` is an opt-in development
or testing override. Before executing package code the bootstrap resolves the
selected ref to an immutable commit, downloads one snapshot, and runs that
snapshot's lifecycle against its own payload. It rejects corrupt or oversized
archives, excessive package contents, excessive whole-archive parsing, absolute,
traversing, or duplicate paths, links, special entries, unreviewed modes,
filesystem-root targets, and packages missing the minimum lifecycle files. The
archive is streamed, and unrelated repository entries do not consume the tighter
distributable-package member allowance.

`lifecycle.py` is the only install, update, status, and remove implementation.
Explicit existing non-root target directories are used directly. With no target,
the CLI may use Git only to discover the containing worktree root and falls back
to the current directory when discovery is unavailable. Repository cleanliness,
ignore rules, and `HEAD` are not lifecycle gates. Before mutation the lifecycle
rejects malformed managed markers and symlink, unsupported-entry, or escape
hazards at managed roots and parents. Nested entries inside a replaceable managed
directory are removed through convergence. `status` is read-only and reports
only managed drift or conflicts.

The lifecycle writes no installed manifest, hashes, provenance, created-state
bits, migration history, backups, or rollback journal. If a write fails after
mutation begins, resolve the reported filesystem error and rerun the command to
converge. Lifecycle code does not directly traverse, interpret, or change
`.agent-wayfinder/`.

## Maintainer and CI gate

Run from the source repository root:

```bash
uv run python skills/agent-workflow/scripts/verify_package.py --tests
uv run python -m unittest discover -s evals/tests -p 'test_*.py' -v
```

The package verifier checks:

- required package structure, the current `VERSION` format and single-source
  boundary, and required files being regular non-symlink files;
- the ordinary current source-to-target distribution mapping;
- the exact current fifteen-skill payload inventory and activation-sensitive
  path exclusions;
- skill frontmatter, packaged support-file closure, local links, the checked-in
  installed projection, and complete attribution for retained derived skills;
- small behavior-bearing semantics: Research writes repository output only with
  explicit authorization;
  Wayfinder is the sole durable coordinator and does not own specialist results;
  `to-spec` and `to-tickets` create no `.scratch` output, invent no local
  destination, label, or status, and publish only to a user- or project-named
  destination with authorization; `implement` does not infer commit
  authorization; and route markers report executed work only;
- deterministic lifecycle, bootstrap, routing, behavior-harness, Wayfinder, and
  verifier tests; and
- local documentation links.

Success ends with:

```text
OK: Agent Workflow package verification passed.
```

The `evals/` unit tests are a separate deterministic, network-free step because
evaluation tooling is not part of the distributed package.

## Distribution-map refresh

After intentionally adding, removing, or remapping a packaged file, inspect the
diff and run:

```bash
uv run python skills/agent-workflow/scripts/verify_package.py --refresh-manifest
uv run python skills/agent-workflow/scripts/verify_package.py --tests
```

Refresh rewrites only
`skills/agent-workflow/payload/distribution/manifest.json`. Ordinary content
edits to an already mapped file do not require a refresh. The manifest is a
current source-to-target map, not installed state and not a content-hash or
retirement ledger.

## Lifecycle acceptance boundary

The deterministic suite proves that:

- install and update converge to the same current state by replacing the full
  `.agent-workflow/` directory and all current curated skill directories;
- obsolete or extra content inside `.agent-workflow/` is removed by ordinary
  desired-state replacement without a preliminary cleanup commit;
- extra files inside a current curated skill directory are removed, while
  unrelated skill directories remain unchanged;
- repeated install and update leave exactly one managed block in `AGENTS.md` and
  `CLAUDE.md` while preserving project-authored bytes byte-for-byte; both accept
  logical LF or CRLF marker lines and narrowly recover the evidenced historical
  duplicate, while `AGENTS.md` uses only managed-begin/managed-end delimiters and
  the existing `CLAUDE.md` output protocol remains unchanged;
- remove deletes the managed directories and regions, deletes a composite file
  only when no project-authored bytes remain, and preserves unrelated skills;
- lifecycle commands do not directly traverse, interpret, or change
  `.agent-wayfinder/`;
- plain non-Git targets, invalid or missing `HEAD`, explicit nested targets, and
  dirty tracked, untracked, or ignored repository state do not block mutation;
- an omitted target inside a Git worktree resolves to that worktree root when
  discovery is available, while an explicit target is never rewritten;
- unsafe managed root or parent entries and malformed markers stop mutation
  before any write, while nested entries inside replaceable directories are
  removed without following symlinks;
- `status` remains read-only and has no repository-wide Git safety concept;
- a deliberately injected later write failure reports possible partial changes
  and directs the user to resolve the filesystem error and rerun convergence
  rather than claiming rollback;
- skill directories outside the current curated inventory are preserved without
  consulting a historical retirement list; and
- bootstrap archive and root-safety boundaries remain enforced offline;
- default bootstrap discovery chooses the highest stable semantic release,
  resolves it to a commit, and fails clearly when no stable release exists;
- a bootstrap originating from an older package release can install a simulated
  newer stable framework release without a CLI upgrade, with lifecycle and
  payload taken from the same downloaded snapshot; and
- explicit branch, tag, or commit refs bypass stable-release discovery.

Wayfinder's state and behavioral tests remain separate from lifecycle tests.
They cover map-first coordination, records, allocation, reconciliation,
reference safety, progressive loading, and project-choice authority without
making lifecycle code interpret durable state.

## Release tags

`skills/agent-workflow/VERSION` is the sole authored framework version and the
human-controlled release switch. After the deterministic verifier succeeds on a
push to `main`, a version change requests one annotated release tag on that exact
verified commit. The release job accepts only `x.y.z`, requires a version greater
than existing semantic release tags, and never reuses, moves, or force-pushes a
tag.

Do not create a release tag while preparing a branch; the verified `main`
workflow owns tag creation.

## Failure diagnostics and limits

Use the first reported error or failed test as the primary diagnostic. For a
mapping mismatch, inspect the source and target inventories before refreshing.
For a lifecycle failure, inspect the exact reported managed path or filesystem
error; never delete project files merely to make a test pass. Generated Python
caches are ignored by Git and package verification and need no manual cleanup.

The deterministic gate runs on Ubuntu. macOS, Linux, WSL, and Linux-based
devcontainers with a POSIX-style shell are supported; native PowerShell and CMD
are not. Live model runs remain opt-in and must be reported separately. Static
verification does not prove live host or editor skill discovery, external
tracker behavior, or authenticated publication.

See [Behavioral testing](behavioral-testing.md) for behavioral scenario evidence,
commands, side effects, and limitations.
