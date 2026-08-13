# Agentic Workflow

Agentic Workflow is a lightweight, repository-native engineering process for
Codex, GitHub Copilot Chat, and compatible agent tooling. It routes simple work
directly while giving consequential decisions, debugging, implementation,
verification, and review durable structure. Runtime behavior is Markdown and
JSON in the repository—no daemon, service, container, package registry, or
external agent runtime is required.

## Install

The installer downloads an immutable revision of this package, validates its
version, manifest, mappings, and checksums, safely adopts the payload, and
verifies the installed files. A successful run ends with
`✓ Agentic workflow <version> installed and verified.`

Run one of these commands from the **ordinary project directory you want to use
as the project root**. The current directory is the target unless an explicit
target is supplied. The command persistently adds the framework files and needs
Python 3.9+ plus HTTPS access to GitHub; it does not need Git or a `.git`
directory.

On macOS or Linux, run this in the host Terminal. If the project exists only
inside a VS Code Dev Container, run it instead in that container's VS Code
terminal:

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))"
```

On native Windows, run this equivalent command in PowerShell from the target
project directory:

```powershell
py -3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))"
```

To install into a different existing directory, append `install` and the target
path. For example, from a macOS or Linux host Terminal:

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" install /path/to/project
```

On Windows PowerShell, the equivalent explicit-target form is:

```powershell
py -3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" install "C:\path\to\project"
```

That's it. Open the project in Codex or VS Code with GitHub Copilot Chat and work
normally. Git is recommended for additional history and recovery, but is not an
installation or runtime prerequisite.

## What gets installed

```text
target-project/
├── AGENTS.md
├── .agents/
│   └── skills/
│       ├── workflow-debugging/SKILL.md
│       ├── workflow-decomposition/SKILL.md
│       ├── workflow-discovery/SKILL.md
│       ├── workflow-implementation/SKILL.md
│       ├── workflow-review/SKILL.md
│       ├── workflow-teach/SKILL.md
│       └── workflow-verification/SKILL.md
├── ai-workflow/
│   ├── install-manifest.json
│   ├── project-profile.md
│   ├── contracts/
│   ├── state/
│   └── templates/
└── docs/
```

`AGENTS.md`, workflow skills, contracts, templates, and installed documentation
are framework-owned. The project profile and active/state record locations are
project-owned seeds: installation creates them only when absent, and updates or
removal never overwrite or delete them.

## Optional dry-run

A dry-run performs package validation and target preflight but makes no files.
It is optional; a deliberate normal install already authorizes the safe,
transactional operation.

Run this in the same **host or container terminal and target project root**. It
is read-only apart from automatically removed temporary download files. On
Windows PowerShell, use `py -3` in place of `python3`:

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" --dry-run
```

## Lifecycle

All lifecycle commands run in the **terminal environment that owns the target
project, from that explicitly selected project root**. They download and
validate the needed package revision automatically; no local clone, Git
repository, or local Git executable is needed. On native Windows PowerShell,
use `py -3` in place of `python3` in these commands.

### Update

Update resolves the current `main` revision, replaces only clean
framework-owned content, preserves project-owned files and the project portion
of a composite `AGENTS.md`, removes explicitly allowlisted retired framework
files only when unchanged, and verifies the result. It is a persistent project
change; `remove` or version control provides reversal.

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" update
```

Success prints `✓ Agentic workflow updated to <version> and verified.` A locally
modified framework file or downgrade fails before writes; reconcile that file
explicitly and rerun rather than forcing ownership.

### Status

Status downloads the exact immutable source revision recorded at installation
and compares every managed file with its recorded checksum. It makes no
persistent target change.

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" status
```

Success exits 0 and prints `✓ Installation is clean.` Missing or changed managed
content exits 1; malformed state or an unavailable exact source revision exits
2. The most useful next diagnostic is the first `missing:` or `modified:` path
in the output.

### Remove

Remove downloads the exact recorded source revision and persistently deletes
only unchanged files created by that version. It restores the original bytes of
a clean pre-existing `AGENTS.md`, preserves pre-existing identical or locally
modified framework paths, and keeps all project-owned profile and state files.

```bash
python3 -c "from urllib.request import urlopen; exec(compile(urlopen('https://raw.githubusercontent.com/jimmfan/agentic-workflow-instructions/main/skills/agentic-workflow/scripts/bootstrap.py', timeout=30).read(), 'agentic-workflow-bootstrap.py', 'exec'))" remove
```

Reinstall the recorded version or restore from version control to reverse a
removal. Project-owned files intentionally remain and may be deleted separately
only after human review.

## Safety and ownership

- An existing differing `AGENTS.md` is preserved byte-for-byte as the project
  section beneath explicit managed markers. Removal restores it exactly.
- A different existing framework target, such as a same-named workflow skill,
  blocks the whole operation before any file is written.
- Repeating a clean installation is idempotent and reports that it is already
  installed and verified.
- Updates refuse locally modified managed content instead of merging or
  overwriting it.
- Every source and installed managed file has a SHA-256 checksum. Target paths
  are validated against absolute paths, traversal, symlinks, and non-directory
  parents.
- Writes are atomic and ordinary Python-visible failures roll back all changes
  in the operation. A machine crash or failing storage can still require backup
  or version-control recovery.

The installation manifest is ownership evidence, not a license to delete
arbitrary paths. Removal authenticates its ownership set against the exact
source package; updates remove retired paths only when the current package
explicitly allowlists them and the installed bytes are unchanged.

## Distribution architecture

The bootstrap skill is the source/distribution boundary. Its payload is inert:
it deliberately does not contain a literal `AGENTS.md`, `.agents` tree, or
`.github` customization tree that an editor could interpret while browsing this
repository.

```text
skills/agentic-workflow/
├── SKILL.md
├── VERSION                 # single version source of truth
├── scripts/
│   ├── bootstrap.py        # resolve/download/verify/dispatch
│   ├── adopt.py            # safe target lifecycle
│   └── verify_package.py   # release and package integrity gate
├── payload/
│   ├── VERSION             # generated/verified from package VERSION
│   ├── distribution/manifest.json
│   ├── root/AGENTS.md.template
│   ├── skills/workflow-*/SKILL.md
│   ├── ai-workflow/
│   └── docs/
└── tests/
```

The manifest explicitly maps inert source paths to installed targets, for
example `payload/root/AGENTS.md.template → AGENTS.md` and
`payload/skills/workflow-teach/SKILL.md →
.agents/skills/workflow-teach/SKILL.md`. Installed repositories need none of the
bootstrap package for runtime use.

Package `VERSION` is authoritative. Maintainers change that one file and run the
refresh command; the verifier derives payload `VERSION`, manifest version, file
mappings, and checksums, then rejects any later drift.

## Develop and verify the package

The refresh command persistently rewrites only generated payload version and
manifest metadata. Run it in the **macOS host Terminal from this distribution
repository root** after an intentional version or payload change:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --refresh-manifest
```

Then run the complete read-only verification suite from the same location. It
creates ordinary non-Git project directories, one temporary Git repository,
and local archives under the system temporary directory, then removes them
automatically. Git is needed only for the contributor test that proves existing
Git repositories remain supported; the installer itself does not invoke Git:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

Success ends with `OK: distributable package is internally consistent.` If it
fails, use the named invariant or first failing lifecycle test as the next
diagnostic. Interactive editor discovery remains a separate manual check because
static files cannot prove a running extension loaded them.

## Requirements and limitations

Installation is supported on macOS, Linux, and native Windows and needs Python
3.9+, HTTPS access to GitHub, and an existing ordinary project directory. Git,
a `.git` directory, and prior `git init` are not required. Git is recommended
for additional recovery and change history. Runtime use needs compatible agent
tooling that discovers root `AGENTS.md` and project skills under
`.agents/skills`; current GitHub Copilot documentation lists both conventions.
Routing is instruction-driven rather than a deterministic policy engine, and
customized managed blocks are deliberately not auto-merged.

The first-stage command retrieves mutable `main` over TLS before the bootstrap
resolves an immutable commit and validates the package. Published releases can
replace `main` with a tag for a reproducible first stage. This repository does
not publish or sign releases as part of the v0 refactor.

The framework is general-purpose and includes no third-party agent runtime,
adapter, daemon, telemetry, credential store, or mandatory infrastructure
integration. It is available under the [MIT License](LICENSE).
