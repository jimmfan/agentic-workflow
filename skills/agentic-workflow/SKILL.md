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

GitHub Copilot in VS Code is the primary/reference runtime. Adoption installs a
unique `.github/hooks/agentic-workflow.json` Preview adapter plus the shared
standard-library Python controller. Codex and Claude examples remain opt-in to
avoid overwriting user-owned fixed hook settings; Copilot CLI/cloud are separate
compatibility investigations. Hooks are not a hard prerequisite: the installed
root policy remains the functional fallback and `status` reports host
enforcement separately from package integrity.

The installed root is a compact orchestration kernel. Detailed classification,
provider invocation, composition, state, and route-output behavior is
progressively loaded from `.ai-workflow/routing.md` and the selected owner
contracts rather than duplicated in always-loaded context.

`.ai-workflow/` is the reconstructable framework installation.
`.ai-workflow-state/` is durable project-owned state and survives install,
update, remove, and reinstall unchanged. Framework-owned **agent integration
files** remain at paths required by each supported environment. Per-session
controller state stays in the operating system temporary directory, outside the
repository.

The purpose of the coordinated path is to prevent a project from receiving only
half of the framework. Install and dry-run preflight both local ownership and
provider compatibility before writes. A successful install leaves the compact
router, four local integration/safety skills, all complete pinned provider
directories, and both clean ownership records in the target. Installation
success is distinct from project readiness: the optional project-owned profile
is classified only by filesystem safety, readability, emptiness, and its advisory
uninitialized marker. Its state and missing tracker/domain/triage configuration
are readiness observations, not package corruption.

Before a fresh provider install or provider-baseline upgrade, GitHub CLI 2.97.0
or newer must expose
`gh skill`, and `gh auth status --hostname github.com` must succeed. Install and
authenticate `gh` in the same host, Dev Container, or Windows environment that
owns the target project. Do not install `gh`, start login, or mutate a target
unless the user has authorized the adoption task. Initial adoption rejects any
same-named provider directory without framework ownership state. The narrow
reinstall exception requires an exact authenticated managed-policy footprint
plus the complete exact pinned provider set; it reconstructs conservative
ownership metadata locally without claiming deleted historical origin. Ordinary
installation stages the exact pin, validates its repository/ref/tree metadata
and inventory, then records hashes of the bytes actually installed. Inner status
checks use those hashes to detect local edits without a provider network call;
the public bootstrap still needs HTTPS to fetch the recorded package. Unknown
and locally modified skills always fail closed.

The provider declaration separates capability routing from invocation policy.
Codex and GitHub Copilot discover the installed `.agents/skills` tree; a
user-only selection results in an exact `$skill-name` or `/skill-name` handoff,
not simulated execution or state writes. Claude Code can read the installed root
policy but cannot natively discover either the local or provider skill tree, so
only policy/direct handling is available and every skill-backed route is
reported unavailable there. Never remove or bypass upstream user-only metadata.

All bootstrap and lifecycle entry points require Python 3.11 or newer and fail
before network or target filesystem work on an older interpreter. The public
README contains environment-specific installation, verification, side-effect,
and reversal guidance; do not bypass the runtime check.

For a deliberate install request, run the lifecycle once with `install`; it
performs preflight, applies both components, rolls back a failed fresh install,
and verifies integrity. It may also report readiness guidance for one-time
profile or provider setup initialization; it does not execute that interactive
setup. Use `--dry-run` only when the user requests a preview. Do not require a
separate preview, apply, or status command for normal installation.

Run these commands from this skill directory, or use absolute script and target
paths. They make persistent target changes except `status` and commands with
`--dry-run`:

```bash
python3 scripts/lifecycle.py install /path/to/project
python3 scripts/lifecycle.py update /path/to/project
python3 scripts/lifecycle.py status /path/to/project
python3 scripts/lifecycle.py remove /path/to/project
```

`status` reports framework integrity, provider integrity, host enforcement,
durable project readiness, and setup capability separately. Missing optional
profile or active-workflow state keeps the clean status exit code; malformed or
unsafe active state remains a resumability warning, and managed-file or
provider-integrity failures do not pass. A selected
configuration-dependent workflow checks its declared requirements and, when
missing, directs the user to the user-only setup skill on a supported host or
reports the provider unavailable on an unsupported host. Unrelated direct work
does not require setup.

Cross-version payload updates trust only an exact predecessor identity embedded
in the new immutable package: version, source revision, installation-manifest
schema, complete managed-path set, and every source SHA-256 must match before
mutation planning. Never add a predecessor merely to make a fixture or unknown
installation pass. Payload install/update post-checks run before transaction
commit and restore prior bytes and modes on failure. Rollback removes only
transaction-created parent directories; successful removal leaves unowned empty
parents in place.

On a provider declaration change, `update` must first authenticate the complete
installed framework as an audited predecessor and use that predecessor's
checksummed `providers.json` to validate the exact provider state identity,
skill set, paths, and tree SHAs. Validate every transition before staging or
mutation. A missing predecessor-recorded directory is absence and may receive
the new declared skill. Retain a directory already compatible with the new
declaration and preserve its recorded origin. Replace an incompatible directory
only when the authenticated predecessor recorded it as `created` or
conservatively `reconstructed`, its complete inventory and metadata match that
predecessor, and every installed-file SHA-256 still matches predecessor state.
Modified and `preexisting-compatible` directories fail closed with
ownership/integrity diagnostics. Reconstructed directories remain managed for
update but are preserved on removal. Stage and verify the complete new pin
before any replacement; provider versions never float.

The coordinated update commits the payload while provider backups remain
reversible. A payload or provider post-check failure restores the predecessor
provider directories and exact state file, while the payload transaction
restores its own bytes and modes. During a normal clean upgrade, keep `.agents`
and `.ai-workflow/` intact so their records prove exact origin. Deleting only
`.ai-workflow/` is instead an explicit reinstall/repair path: the installer
reconstructs conservative ownership from exact surviving managed files and
never touches `.ai-workflow-state/`.

`remove` is bounded to exact declaration names. Delete only a directory whose
complete inventory is package-authentic, whose installed checksums still match
its record, and whose origin is `created`; preserve incompatible, modified,
extra-file, undeclared, `preexisting-compatible`, and `reconstructed`
directories. Origin history is repository-local evidence, not tamper-evident. Coordinated forgery can
reclassify an exact unmodified canonical directory, but cannot authorize
deletion of modified, extra-file, or undeclared content.

Payload origin and composite restoration fields have the same repository-local
trust limit. Coordinated forgery can reclassify exact canonical managed bytes or
substitute an exact current/audited historical policy identity, but cannot
authorize invented source identities or deletion of modified, extra,
undeclared, or unique project content. Eliminating that limitation would require
no-delete semantics or a trust anchor outside the target repository.

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
