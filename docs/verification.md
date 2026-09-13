# Verification model

## Maintainer and CI gate

Run from the **source repository root** with Python 3.11+, `uv`, Git, and a POSIX-style shell.
Dependency setup and isolated builds may need package-index access; model credentials are not required.
Exercise install, update, and remove only against disposable consumers, never this authoring checkout; see [source-checkout ownership](../AGENTS.md#source-checkout-ownership).

```bash
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked python agent_workflow/verify_package.py --tests
uv run --locked python -m unittest discover -s evals/tests -p 'test_*.py' -v
uv run --locked python tests/wheel_smoke.py
git diff --check
```

If the default uv cache is outside the host's writable area, set `UV_CACHE_DIR` to a writable temporary directory for these commands.
Do not change global configuration or refresh metadata to hide an unexplained failure.

| Check | What it establishes |
|---|---|
| Ruff | Python formatting and lint conformance. |
| Package verifier with `--tests` | Current package shape, `VERSION`, distribution mapping, safe canonical files, skill metadata/support-file closure, attribution, root/template synchronization, local links, and deterministic package tests. |
| `evals/tests/` | Network-free evaluation-tooling unit tests, separately from the distributed package gate. |
| Wheel smoke | A build from current source, isolated CLI installation, and all four lifecycle commands against local snapshot resources in a disposable non-Git consumer. |

Successful package verification ends with `OK: Agent Workflow package verification passed.`
Package validity concerns structure, safety, attribution, and machine-readable contracts; ordinary instruction wording is not a literal package interface.
For derived-skill prose edits, distinguish editorial changes from intentional instruction changes, preserve complete support files and attribution, and run the package gate.
For focused commands and ownership, see [tests](../tests/README.md).

The verifier's documentation-link check covers `README.md`, `docs/`, and `.agent-workflow/`; skill-local links are checked separately.
It checks local targets, not Markdown anchors or every tracked document/reference form.
For documentation moves or deletions, search all tracked files, including dot-directories, and manually check incoming links, reference-style links, anchors, and code-formatted paths.
Keep frozen historical references tied to their original revision.

## Build and platform coverage

The wheel smoke copies current tracked and unignored source, including pending edits and canonical dot-directories, into a disposable build tree.
It builds an sdist, builds a wheel from that archive, checks version/build inputs/licensing and intended wheel contents, then invokes the installed entry point outside checkout imports.
Canonical runtime framework and skill resources come from a separate local repository-snapshot archive, and installation must not create `.project-efforts/` state.
The sdist may contain ordinary tests or documentation; wheel contents are limited by [`pyproject.toml`](../pyproject.toml) to the intended Python package, install resources, distribution metadata, and licensing material.
This packaging exercise does not test live latest-release discovery.

The lockfile-drift control first completes a locked run with a fresh cache, then changes a dependency only in its disposable copy.
An offline locked run must reject that drift without running the requested command or rewriting `uv.lock`.
However, the isolated `setuptools.build_meta` backend resolves the declared `setuptools>=68` requirement separately from the project lockfile.
Builds are therefore not fully locked or bit-for-bit reproducible; check clean builds without inherited constraint overrides.

[CI](../.github/workflows/verify.yml) configures the full gate on Ubuntu/Python 3.11, package and evaluation tests on Ubuntu/Python 3.14, and focused bootstrap/lifecycle/direct-distribution plus wheel checks on macOS/Python 3.11.
Release publication waits for all three jobs.
Configured coverage is not evidence that a particular hosted run succeeded.
WSL and Linux devcontainers are supported environments without separate CI jobs; native PowerShell/CMD are unsupported and Git Bash on native Windows is best-effort.

## Distribution-map refresh

Only after intentionally adding, removing, or remapping a packaged file, inspect the mapping diff and run:

```bash
uv run --locked python agent_workflow/verify_package.py --refresh-manifest
uv run --locked python agent_workflow/verify_package.py --tests
```

Refresh rewrites only `agent_workflow/install/manifest.json`.
Ordinary content edits to already mapped files and source-only documentation changes need no refresh.
The manifest maps current snapshot sources to targets; it is neither installed state nor a history ledger.

## Release tags

The root `VERSION` is the human-controlled `x.y.z` release switch and the source for Python distribution metadata.
Changes to distributed behavior or installed content require a version increase in the same PR unless explicitly excluded from release; source-only documentation leaves it unchanged.
Compare against both the PR base and existing semantic release tags before delivery.

PR CI validates explicit base/head revisions using fetched tags and read-only remote tag observation.
The [release script](../.github/scripts/release_tag.py) accepts canonical `x.y.z`, requires a changed version to exceed both the base version and existing semantic release tags, and treats unchanged `VERSION` as no release.
After all three jobs pass on a push to `main`, it revalidates and creates one annotated tag on that exact verified commit.
Do not create release tags while preparing a branch.

A retry succeeds only when an already-published annotated remote tag resolves to that same commit.
Conflicting tag types or commits fail; a matching local-only tag remains pending and may be pushed again after a failed push.
Never force, move, or rewrite release tags.
For older CLI layouts, retain the [one-time reinstall procedure](../README.md#one-time-reinstall-for-the-repository-layout-release).

## Diagnostics and evidence limits

Start with the first reported error.
For a mapping mismatch, inspect source and target inventories before refreshing.
For lifecycle failures, inspect the named managed path, malformed marker, or filesystem error; never delete project-owned files to make verification pass.
A failure after mutation may leave partial changes, so resolve the error and rerun convergence rather than assuming rollback.
Generated Python caches are ignored and need no manual cleanup.

CLI diagnostics distinguish installed CLI version, selected framework ref/release, resolved commit, and target.
A local archive override has no observed ref or commit and reports them unavailable.
`agent-workflow --version` identifies only the CLI; `status` compares managed surfaces to the selected snapshot rather than recovering an installed-release history.
Exit codes are 0 for healthy/success, 1 for status drift/conflict, and 2 for command/runtime errors.

Deterministic lifecycle tests exercise real filesystem and bootstrap boundaries in disposable consumers.
Scenario controls validate evaluators and fixture outcomes; they do not establish live instruction compliance, actual state reads, independent review, editor skill discovery, authenticated publication, or external tracker behavior.
Keep model quota, authentication, network, timeout, host, and harness failures distinct from product outcomes.
Live runs remain opt-in; see [behavioral testing](behavioral-testing.md) and the [Wayfinder coverage gaps](../tests/README.md#wayfinder-coverage-and-evidence-limits).

## Dependency and action updates

Change declared dependencies intentionally, refresh `uv.lock` only when its inputs change, inspect the diff, and run the full gate.
For GitHub Actions, read official release notes, resolve the selected release with `git ls-remote <official-repository> refs/tags/<version>` (including its peeled ref for an annotated tag), and update all occurrences of the full SHA and release comment together.
Keep full commit pins; avoid moving major tags and unrelated major upgrades.
When revisiting the current-stable Python CI job, verify the stable minor against the official Python release list; retain the Python 3.11 minimum gate.
