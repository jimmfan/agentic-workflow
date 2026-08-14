---
name: agentic-workflow
description: Install, update, inspect, or safely remove the Agentic Workflow orchestration payload and its pinned curated upstream skills. Use when adopting the framework into a project directory or maintaining an existing installation.
license: MIT
---

# Agentic Workflow bootstrap

This skill is the inert distribution boundary. `scripts/lifecycle.py`
coordinates the local project payload owned by `scripts/adopt.py` with the
pinned upstream provider set owned by `scripts/providers.py`.
`scripts/verify_package.py` validates both declarations before any adoption
operation.

The purpose of the coordinated path is to prevent a project from receiving only
half of the framework. Install and dry-run preflight both local ownership and
provider compatibility before writes. A successful install leaves the compact
router, four local integration/safety skills, all complete pinned provider
directories, and both clean ownership records in the target.

Before a fresh provider install, GitHub CLI 2.97.0 or newer must expose
`gh skill`, and `gh auth status --hostname github.com` must succeed. Install and
authenticate `gh` in the same host, Dev Container, or Windows environment that
owns the target project. Do not install `gh`, start login, or mutate a target
unless the user has authorized the adoption task. Existing exact-compatible
provider directories can be adopted without a network call; incompatible
same-named skills always fail closed.

All bootstrap and lifecycle entry points require Python 3.11 or newer and fail
before network or target filesystem work on an older interpreter. The public
README contains environment-specific installation, verification, side-effect,
and reversal guidance; do not bypass the runtime check.

For a deliberate install request, run the lifecycle once with `install`; it
performs preflight, applies both components, rolls back a failed fresh install,
and verifies the result. Use `--dry-run` only when the user requests a preview.
Do not require a separate preview, apply, or status command for normal
installation.

Run these commands from this skill directory, or use absolute script and target
paths. They make persistent target changes except `status` and commands with
`--dry-run`:

```bash
python3 scripts/lifecycle.py install /path/to/project
python3 scripts/lifecycle.py update /path/to/project
python3 scripts/lifecycle.py status /path/to/project
python3 scripts/lifecycle.py remove /path/to/project
```

Before packaging or adoption, run the read-only verifier from this skill
directory:

```bash
python3 scripts/verify_package.py
```

For end users, prefer the public README bootstrap. It resolves and downloads an
immutable GitHub revision, validates it, and hides the package location. Never
call `adopt.py` alone for a public installation, bypass provider preflight, edit
either target ownership file to force deletion, use `gh skill update --unpin`,
or overwrite a project-owned path.
