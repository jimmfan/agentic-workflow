# Agentic Workflow

Agentic Workflow is a lightweight orchestration framework for Codex, GitHub
Copilot, Claude Code, and compatible agent hosts. It keeps a small repository
router and a few project-specific safety/integration skills, while delegating
mature planning, learning, research, specification, ticketing, implementation,
TDD, and Code Review methods to a curated, tested release of
[`mattpocock/skills`](https://github.com/mattpocock/skills/releases/tag/v1.2.3).

The point of this design is to avoid maintaining weaker local copies of mature
workflows. A successful installation gives the target project one coherent
route from intent to the appropriate pinned skill, preserves provider-native
artifacts and identifiers, and adds independent project acceptance verification
without loading every workflow body into every prompt.

## Curated provider baseline

Version 0.6.0 is tested against upstream tag `v1.2.3`, commit
`6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`. The declaration in
`ai-workflow/providers.json` pins the exact tag, subtree SHA, upstream path, and
complete file inventory for each selected skill.

| Capability | Selected skill |
|---|---|
| Initial provider configuration | `setup-matt-pocock-skills` |
| Huge, foggy multi-session planning | `wayfinder` |
| Sustained learning workspace | `teach` |
| Primary-source repository research | `research` |
| Durable specification | `to-spec` |
| Dependency-ordered work | `to-tickets` |
| Implementation | `implement` |
| Implementation subflows | `tdd`, `code-review` |
| Direct composition dependencies | `grilling`, `domain-modeling`, `prototype`, `codebase-design` |

The four composition dependencies are installed even though the root router
does not select them directly. This prevents a selected upstream workflow from
discovering a missing dependency halfway through a task. `diagnosing-bugs` is
not selected: the local debugging workflow uniquely preserves diagnosis-only
authorization, external-signal handling, and durable resume state.

## Prerequisites

Installation needs Python 3.11+, HTTPS access to GitHub, and GitHub CLI 2.97.0
or newer with the public-preview `gh skill` command. The installer requires an
authenticated GitHub.com CLI session before writing a fresh dependency set;
this avoids unauthenticated API rate limits and makes dependency preflight
reliable. Runtime work and local provider verification use ordinary repository
files and do not contact upstream. Python 3.11 is the compatibility floor, not
an exact pin: newer supported Python 3 releases are accepted.

First, verify Python in the **same macOS host Terminal, VS Code Dev Container
terminal, Linux shell, or native Windows PowerShell that owns the target
project**. These checks are read-only and must report Python 3.11 or newer:

```bash
python3 --version
```

```powershell
py -3 --version
```

If macOS reports an older version, run the following in the **macOS host
Terminal**. This persistently installs Homebrew's current supported Python,
refreshes the shell's command lookup for the current session, and verifies the
interpreter selected by the public commands below:

```bash
brew install python
hash -r
python3 --version
```

If native Windows reports an older version, run the following in **native
Windows PowerShell**. This persistently installs the current Python 3.14 release
line and verifies that the Python launcher can select it:

```powershell
winget install --id Python.Python.3.14 --exact
py -3.14 --version
```

Use `py -3.14` in place of `py -3` in later commands if another installed
Python remains the launcher's default. In a **Debian 12, Ubuntu 24.04, or newer
Linux host or Dev Container terminal**, the distribution Python satisfies the
floor; this persistent install and read-only verification are sufficient:

```bash
sudo apt update
sudo apt install python3 -y
python3 --version
```

If that reports less than 3.11, use a newer supported distribution or Dev
Container base before installation; the framework deliberately does not direct
users to replace an operating system's managed Python. To reverse only the
optional Python installs above, use `brew uninstall python` in the macOS host
Terminal or `winget uninstall --id Python.Python.3.14 --exact` in native Windows
PowerShell. Do not remove a distribution-managed `python3`, because operating
system tools may depend on it.

Install and authenticate `gh` in the **same environment that owns the target
project**. For a normal macOS checkout, that is the macOS host Terminal. For a
project that exists only inside a VS Code Dev Container, use the VS Code
terminal inside that container and install `gh` there. For native Windows, use
PowerShell. Installing `gh` is a persistent machine or container change; login
stores a credential in the platform credential store when one is available.

### macOS

In the **macOS host Terminal**, this persistently installs GitHub CLI with
Homebrew. If it is already installed but older than 2.97.0, use the upgrade
command instead. GitHub lists Homebrew as its supported macOS package path.

```bash
brew install gh
```

```bash
brew update && brew upgrade gh
```

### Windows

In **native Windows PowerShell**, this persistently installs GitHub CLI with
WinGet. Use the second command to update an older installation. GitHub lists
WinGet as its supported Windows package path.

```powershell
winget install --id GitHub.cli --exact
```

```powershell
winget upgrade --id GitHub.cli --exact
```

### Debian, Ubuntu, or a Debian-based Dev Container

In the **Linux host terminal or VS Code Dev Container terminal that owns the
project**, this official procedure persistently adds GitHub's signed APT source
and installs `gh`:

```bash
(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && cat "$out" | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null \
  && sudo apt update \
  && sudo apt install gh -y
```

For Fedora, RHEL, SUSE, and other Linux variants, use the matching complete
procedure in GitHub's [official Linux installation guide](https://github.com/cli/cli/blob/trunk/docs/install_linux.md).

### Verify and authenticate

In that **same host, container, or Windows terminal**, these read-only checks
confirm the required version and `gh skill` interface. Then login opens a web
authentication flow and persistently stores the GitHub credential. The final
command is the success check: it should identify the active GitHub.com account
and exit successfully.

```bash
gh --version
gh skill install --help
gh auth login --hostname github.com --web
gh auth status --hostname github.com
```

In PowerShell the commands are identical. Headless automation may provide
`GH_TOKEN` for the current process instead of storing a login. See the official
[`gh auth login`](https://cli.github.com/manual/gh_auth_login),
[`gh auth status`](https://cli.github.com/manual/gh_auth_status), and
[`gh skill install`](https://cli.github.com/manual/gh_skill_install) contracts.
The skill installer injects source metadata, supports exact `--pin` values, and
shares project-scoped `.agents/skills` between Codex and GitHub Copilot.

To reverse prerequisite setup, first remove the stored login with
`gh auth logout --hostname github.com`. Then use `brew uninstall gh` on macOS,
`winget uninstall --id GitHub.cli --exact` in Windows PowerShell, or
`sudo apt remove gh -y` on Debian/Ubuntu. The APT removal leaves GitHub's package
source configured for future reinstall. To remove that configuration too, run
the following destructive command only in the same Debian/Ubuntu host or
container; it persistently deletes exactly GitHub CLI's source and keyring, then
refreshes APT metadata:

```bash
sudo rm -f /etc/apt/sources.list.d/github-cli.list /etc/apt/keyrings/githubcli-archive-keyring.gpg
sudo apt update
```

Removing `gh` does not remove skills already copied into projects.

## Install the framework

The bootstrap downloads an immutable revision of this package, validates its
version, manifest, mappings, provider declaration, and checksums, preflights
both the local payload and upstream dependencies, then performs one coordinated
installation. If upstream installation fails after the payload write, it rolls
back newly created provider directories, framework files, and unchanged seed
files that did not predate the operation.

Run the command from the **ordinary project directory that should become the
project root**. The change is persistent: it adds the files shown below. Git and
a `.git` directory are recommended for recovery but are not installation or
runtime prerequisites.

On macOS or Linux, use the **host Terminal**, or the **VS Code terminal inside
the Dev Container** when the project exists only there:

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))"
```

On native Windows, run this from the target project in **PowerShell**:

```powershell
py -3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))"
```

Success ends with both provider verification and
`✓ Agentic Workflow payload and curated upstream providers are ready.` Open a
fresh Codex task or Copilot chat from that project root so the host discovers
the new root policy and skills.

To target another existing directory, append `install` and the path. For
example, from a macOS/Linux host terminal:

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" install /path/to/project
```

From native Windows PowerShell:

```powershell
py -3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" install "C:\path\to\project"
```

### Optional dry-run

A dry-run validates the package, target ownership, `gh` version/interface,
authentication, existing compatible skills, and planned writes without making
persistent target changes. Run it in the same terminal and target project root;
on Windows substitute `py -3` for `python3`:

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" --dry-run
```

## What gets installed

```text
target-project/
├── AGENTS.md                         # managed router + project section
├── CLAUDE.md                        # shared-policy import
├── .agents/skills/
│   ├── workflow-debugging/            # local authorization-safe diagnosis
│   ├── workflow-discovery/            # local bounded decision work
│   ├── workflow-implementation/       # provider integration adapter
│   ├── workflow-verification/         # acceptance/integration evidence
│   ├── setup-matt-pocock-skills/      # pinned upstream directories
│   ├── wayfinder/ · teach/ · research/
│   ├── to-spec/ · to-tickets/ · implement/
│   ├── tdd/ · code-review/
│   └── grilling/ · domain-modeling/ · prototype/ · codebase-design/
└── ai-workflow/
    ├── providers.json                  # tested capability declaration
    ├── provider-state.json             # provider ownership/checksums
    ├── install-manifest.json           # local payload ownership/checksums
    ├── project-profile.md              # project-owned seed
    ├── contracts/
    ├── observability/                   # inert optional export analyzer
    ├── state/
    └── templates/
```

`gh skill` copies each complete selected directory, including adjacent Markdown
resources and `agents/openai.yaml`; the installer rejects a missing, extra, or
metadata-incompatible file. It does not copy only `SKILL.md`.

The provider skills are project scoped, which is the common `.agents/skills`
location documented by GitHub CLI for Codex and GitHub Copilot. Detailed skill
bodies load on demand. The root router is under 5 KB and contains capability
names and integration boundaries, not copied provider prompt bodies.

The optional observability directory contains a read-only, standard-library
analyzer for user-supplied OTLP or Copilot JSON exports. It is never imported by
the router or a workflow, enables no telemetry, stores no data, and is fully
documented in
[`ai-workflow/observability/README.md`](skills/agentic-workflow/payload/ai-workflow/observability/README.md).
The tested baseline, supported contracts, privacy boundary, limitations, and
BUILD SMALLER decision are in [Optional observability](docs/observability.md).

## First runtime setup

Installation deliberately does not run `setup-matt-pocock-skills`: setup is a
prompt-driven, project-specific operation that may write
`docs/agents/issue-tracker.md`, `docs/agents/domain.md`, optional triage-label
configuration, and a root `## Agent skills` block. Before the first
tracker-dependent upstream workflow, the router invokes setup visibly if the
tracker or domain file is missing. It should not run on every prompt or ordinary
framework update.

Teach is also bounded deliberately. An explicit sustained learning request uses
`teach` in a dedicated learning workspace, where its `MISSION.md`, glossary,
resources, lessons, and learning records belong. A normal knowledge question is
answered directly and does not seed course artifacts into the engineering
project.

Responses governed by the router end with one compact effective-path line such
as `[route: router → implement → verification]`. The marker lists only
workflows that materially affected that response; skill availability does not
count, and producing the marker never triggers another workflow.

## Lifecycle

All commands below run in the **terminal environment that owns the target
project, from that project root**. They download and validate the appropriate
framework package automatically. On native Windows PowerShell, substitute
`py -3` for `python3`.

### Update

Update preflights both lifecycle components, replaces only checksum-clean
framework-owned content, preserves project sections and seeds, and changes a
provider pin only when the reviewed framework declaration changes. Pinned
skills never float merely because upstream publishes a release; GitHub CLI also
documents that ordinary `gh skill update` skips pinned skills. The framework
stages a declared provider upgrade separately and never uses `--unpin` or
`--force` against project skills.

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" update
```

Success ends with `✓ Agentic Workflow payload and curated upstream providers
are updated and verified.` Upgrade from 0.4.x also retires unchanged local
`workflow-teach`, `workflow-decomposition`, and `workflow-review` copies and
their obsolete learning/ticket templates. A locally modified retired file is
preserved as project-owned for manual reconciliation.

If update reports a changed framework-created provider, inspect the named
directory and either preserve the intentional customization under a new
project-owned skill name or restore the recorded bytes before retrying. A
pre-existing compatible provider is never silently claimed or replaced; if a
new framework pin requires it to change, reinstall that dependency explicitly
at the declared version and rerun update.

### Status

Status is read-only for the target. The public bootstrap downloads the exact
framework package recorded at installation, then verifies both manifests,
managed blocks, provider metadata, complete directory inventories, and every
recorded checksum. It does not query or update the upstream skill repository.

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" status
```

Clean payload and provider checks both exit 0. Missing or modified managed
content exits 1; malformed state, a mismatched source package, or an unsafe path
exits 2. The first named `modified`, `missing`, or `missing-or-incompatible`
path is the most useful next diagnostic.

### Remove

Remove uses the exact recorded framework package. It deletes only unchanged
local files and upstream skill directories created by this framework, restores
clean pre-existing root policies, and preserves pre-existing compatible or
locally changed skills plus all project-owned state. Provider state must match
the exact declaration before any provider directory can be removed.

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" remove
```

Reinstall the recorded version or restore from version control to reverse a
removal. Project-owned profile, state, setup documents, specifications, tickets,
learning workspaces, and modified/pre-existing skills intentionally remain and
must be reviewed separately before deletion.

## Safety and ownership

- Root `AGENTS.md` is composite: the framework owns only its marked policy
  block, while the project owns the section below the project marker.
- `provider-state.json` distinguishes `created` from
  `preexisting-compatible`; removal never claims the latter.
- A same-named incompatible skill blocks the whole operation before writes.
- Installation is idempotent when both payload and provider baseline are clean.
- Updates refuse local changes rather than merging or overwriting them.
- Source paths, target paths, symlinks, special files, exact file inventories,
  injected GitHub metadata, subtree SHAs, and SHA-256 checksums are validated.
- Normal filesystem failures roll back component transactions. Coordinated
  operations preflight both components; if an unexpected second-component
  failure survives preflight, rerun `status` to identify the exact partial
  boundary before retrying or restoring from version control.

The manifests are ownership evidence, never authority to delete arbitrary
paths. Provider removal binds target-controlled state back to the exact curated
declaration before resolving any directory.

## Distribution architecture

The package is inert while stored in this repository: it contains templates and
explicit source-to-target mappings rather than live nested `AGENTS.md` or
`.agents` customization paths.

```text
docs/                         # maintainer architecture, routing, ADRs
skills/agentic-workflow/
├── SKILL.md
├── VERSION
├── scripts/
│   ├── bootstrap.py             # immutable download and dispatch
│   ├── lifecycle.py             # coordinated one-command lifecycle
│   ├── adopt.py                 # local payload transaction
│   ├── providers.py             # pinned gh skill transaction
│   └── verify_package.py        # release/package gate
├── payload/
│   ├── distribution/manifest.json
│   ├── root/AGENTS.md.template
│   ├── skills/workflow-*/SKILL.md
│   └── ai-workflow/
│       ├── providers.json
│       └── observability/          # optional read-only export analyzer
└── tests/
```

Installed repositories need none of the bootstrap package at runtime. Framework
maintainer docs remain in this source repository and are never installed into a
target's generic `docs/` namespace.

## Develop and verify

After an intentional payload or version change, run this persistent metadata
refresh in the **macOS host Terminal from this repository root**. It rewrites
only generated payload version and distribution-manifest data:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --refresh-manifest
```

Then run the full verification suite from the **same repository root**. The
tests create and automatically remove temporary ordinary projects, a temporary
Git repository, and local archive/provider fixtures; they do not alter the
target projects on your machine:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

Success ends with `OK: distributable package is internally consistent.` If it
fails, the first named invariant or lifecycle test is the next diagnostic.
Interactive host discovery remains a separate read-only smoke test because
static files cannot prove that a running editor mounted its skill catalog.

## Requirements and limitations

The supported target environments are macOS, Linux, and native Windows with
Python 3.11+ and filesystem semantics visible to Python. Fresh provider install
also needs GitHub CLI 2.97.0+, HTTPS access, and GitHub.com authentication. Git
is recommended but not required by the installer.

Routing is instruction-driven, not host telemetry. The compact route line is an
instruction-enforced declaration. Provider instructions cannot enlarge the
user's authorization: commits, publishing, external tracker mutation, setup
writes, and course-workspace writes still require the request and host approval
boundary to allow them.

The first-stage public command retrieves mutable `main` over TLS before the
bootstrap resolves an immutable commit. A published tag may replace `main` for
a reproducible first stage. The project is available under the [MIT License](LICENSE).
