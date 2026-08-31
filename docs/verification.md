# Verification model

Verification covers the current package and its observable boundaries. It does
not preserve or prove former installations.

## Consumer safety

`bootstrap.py` is the public download boundary. Before executing package code it
resolves mutable refs to an immutable commit and rejects corrupt or oversized
archives, excessive package contents, excessive whole-archive parsing,
absolute, traversing, or duplicate paths, links, special entries, unreviewed
modes, filesystem-root targets, and packages missing the minimum lifecycle
files. The archive is streamed, and unrelated repository entries do not consume
the tighter distributable-package member allowance.

`lifecycle.py` is the only install, update, status, and remove implementation.
Mutating commands require the exact Git worktree root, a valid `HEAD`, and a
completely clean porcelain status including untracked files. Before mutation
they also reject untracked files under managed surfaces, ignored managed
destinations, malformed managed markers, symlinks, special entries, and path
escapes. `status` is read-only, does not require a clean tree, and reports the
blockers that would stop mutation.

Git is the recovery mechanism. The lifecycle writes no installed manifest,
hashes, provenance, created-state bits, migration history, backups, or rollback
journal. If a write fails after mutation begins, inspect `git status`, restore
with Git as appropriate, and retry. Lifecycle code does not directly traverse,
interpret, or change `.agent-wayfinder/`; repository-wide Git cleanliness checks
may still observe changes under it.

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
- extra files inside a current curated skill directory are removed, while
  unrelated skill directories remain unchanged;
- `AGENTS.md` and `CLAUDE.md` managed regions update while project-authored
  bytes remain unchanged;
- remove deletes the managed directories and regions, deletes a composite file
  only when no project-authored bytes remain, and preserves unrelated skills;
- lifecycle commands do not directly traverse, interpret, or change
  `.agent-wayfinder/`, while repository-wide Git cleanliness still observes its
  changes;
- dirty tracked or untracked state, an invalid or missing `HEAD`, a non-root
  invocation, ignored or untracked managed destinations, unsafe filesystem
  entries, and malformed markers stop mutation before any write;
- `status` remains read-only on a dirty tree and reports safety blockers;
- a deliberately injected later write failure reports possible partial changes
  and directs the user to Git recovery rather than claiming rollback;
- `.agent-workflow/providers.json` and obsolete Setup, Teach, or Triage skill
  directories produce one manual clean-break instruction and no mutation;
- a future removed skill is not retired automatically; cleanup is a separate
  explicit Git change; and
- bootstrap archive and root-safety boundaries remain enforced offline.

Git cannot recover ignored or previously untracked files. Tests therefore prove
those managed-path cases fail before mutation instead of relying on recovery.

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
For a lifecycle failure, inspect `git status`; never delete project files merely
to make a test pass. Generated Python caches are ignored by Git and package
verification and need no manual cleanup.

The deterministic gate runs on Ubuntu. macOS, Linux, WSL, and Linux-based
devcontainers with a POSIX-style shell are supported; native PowerShell and CMD
are not. Live model runs remain opt-in and must be reported separately. Static
verification does not prove live host or editor skill discovery, external
tracker behavior, or authenticated publication.

See [Behavioral testing](behavioral-testing.md) for behavioral scenario evidence,
commands, side effects, and limitations.
