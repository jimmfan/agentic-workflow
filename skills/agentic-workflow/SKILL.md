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
root policy remains the functional fallback and `status` reports installed/static
host integration separately from package integrity and live host verification.

The installed root is a compact orchestration kernel. Detailed classification,
provider invocation, composition, state, and route-output behavior is
progressively loaded from `.ai-workflow/routing.md` and the selected owner
contracts rather than duplicated in always-loaded context.

`.ai-workflow/` is the reconstructable framework installation.
`.ai-workflow-state/` is the canonical durable project-owned state location.
Install and update create the directory when absent, but do not seed any state
files; existing contents survive install, update, remove, and reinstall
unchanged. Framework-owned
**agent integration files** remain at paths required by each supported
environment. Per-session controller state stays in the operating system
temporary directory, outside the repository.

The coordinated path installs the framework transactionally and then attempts
the optional provider set. A provider failure does not undo a valid framework
installation; the installed router and local safety/integration skills remain
usable through host-native fallback. Installation success is distinct from
project readiness: a missing optional profile, active state, provider set, or
tracker/domain/triage configuration is not package corruption.

Before a fresh provider install or provider-baseline upgrade, GitHub CLI 2.97.0
or newer must expose
`gh skill`, and `gh auth status --hostname github.com` must succeed. Install and
authenticate `gh` in the same host, Dev Container, or Windows environment that
owns the target project. Do not install `gh`, start login, or mutate a target
unless the user has authorized the adoption task. Initial adoption rejects any
same-named provider directory without framework ownership state. The narrow
reinstall exception requires a structurally valid managed-policy footprint plus
compatible surviving provider skills; it reconstructs conservative ownership
metadata locally without claiming deleted historical origin. Ordinary provider
installation pins a reviewed tag, validates required repository/path/ref and
invocation metadata, then records hashes of the bytes actually installed. Inner
status checks use those hashes to detect local edits without a provider network
call. Unknown and locally modified skills are never overwritten.

The provider declaration separates capability routing from invocation policy.
When a preferred provider is unavailable or user-only but was not explicitly
invoked, normal intent continues with truthful host-native capability. Return an
exact `$skill-name` or `/skill-name` handoff only when the user required that
provider or a real configuration boundary cannot be crossed host-natively.
Never simulate provider execution or bypass upstream invocation metadata.

All bootstrap and lifecycle entry points require Python 3.11 or newer and fail
before network or target filesystem work on an older interpreter. The public
README contains environment-specific installation, verification, side-effect,
and reversal guidance; do not bypass the runtime check.

For a deliberate install request, run the lifecycle once with `install`; it
preflights and transactionally applies the framework, then attempts the optional
providers. A provider failure is reported without rolling back the framework.
Successful install output stays compact and does not dump optional host or setup
matrices. It creates only the empty canonical project-state directory and does
not create a profile, active state, configuration, or execute interactive setup. Use
`--dry-run` only when the user requests a preview. Do not require a separate
preview, apply, or status command for normal installation.

Run these commands from this skill directory, or use absolute script and target
paths. They make persistent target changes except `status` and commands with
`--dry-run`:

```bash
python3 scripts/lifecycle.py install /path/to/project
python3 scripts/lifecycle.py update /path/to/project
python3 scripts/lifecycle.py status /path/to/project
python3 scripts/lifecycle.py remove /path/to/project
```

`status` answers framework health, project-state readiness, and normal workflow
availability first, then groups optional provider/configuration and static host
details separately. Missing optional profile or active-workflow state is normal
and keeps the clean status exit code; a healthy status explicitly says no action
is required. Host entries describe installed/static capability and do not claim
live host loading. Optional
malformed or unsafe active state remains a resumability warning, and
managed-file failures do not pass. Optional provider failures are reported as
degraded capability while host-native work remains available. A selected
configuration-dependent workflow checks its declared requirements and, when
missing, directs the user to the user-only setup skill only when configuration
is genuinely required; otherwise host-native fallback remains available.
Unrelated direct work does not require setup.

Cross-version payload updates use the structurally valid installed ownership
record and compare current bytes with its recorded checksums before mutation.
The package manifest authenticates the new payload, not a catalog of historical
releases. Payload install/update post-checks run before transaction commit and
restore prior bytes and modes on failure. Rollback removes only
transaction-created parent directories; successful removal leaves unowned empty
parents in place.

On a provider declaration change, `update` uses local provider state to validate
ownership and current checksums. A missing recorded directory may receive the
new declared skill. Retain a compatible directory and preserve its recorded
origin. Replace an incompatible directory only when its origin is `created` or
`reconstructed` and every installed-file SHA-256 still matches recorded state.
Modified and pre-existing-compatible directories are preserved with clear
diagnostics. Reconstructed directories remain managed for update but are
preserved on removal. Stage and verify new provider bytes before replacement;
provider versions never float.

Framework update commits independently of the optional provider update. Each
layer retains its own reversible staging and rollback, so a provider failure
preserves its existing files while leaving the successfully updated framework
usable. During a normal clean upgrade, keep `.agents` and `.ai-workflow/` intact
so their local records preserve ownership. Deleting only
`.ai-workflow/` is instead an explicit reinstall/repair path: the installer
reconstructs conservative ownership from exact surviving managed files and
preserves `.ai-workflow-state/` contents. Install and update safely move only
the known development-era profile, active, records, and archive paths when the
canonical state directory is absent or empty; any populated destination or
unsafe path blocks migration without overwriting project state.

`remove` is bounded to provider-state records. Delete only a directory whose
current files and checksums still match its record and whose origin is
`created`; preserve incompatible, modified, extra-file,
`preexisting-compatible`, and `reconstructed` directories. Origin history is
repository-local evidence, not tamper-evident.

Payload origin and composite restoration fields have the same repository-local
trust limit. Without editing ownership records, modified, extra, undeclared, or
unique project content remains outside automatic replacement or deletion.

Before packaging or adoption, run the read-only verifier from this skill
directory:

```bash
python3 scripts/verify_package.py
```

For end users, prefer the public README bootstrap. It resolves and downloads an
immutable GitHub revision, validates it, and hides the package location. Never
call `adopt.py` alone for a public installation, edit
either target ownership file to force deletion, use `gh skill update --unpin`,
or overwrite a project-owned path.
