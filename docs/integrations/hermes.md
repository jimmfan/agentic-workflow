# Optional Hermes integration

## Purpose and supported outcome

This integration adds bounded external research without changing the normal
Codex engineering loop. Codex remains the top-level owner, Hermes receives a
minimal research capability, and repository files stay outside the child
runtime. If Hermes is absent, all core workflows remain functional.

| Level | Hermes v0.20.0 status | Boundary |
|---|---|---|
| `disabled` | Default when Hermes is absent, unjustified, incompatible, unconfigured, or unauthenticated | Codex continues alone or reports only the optional investigation unavailable. |
| `research` | Implemented; a live call requires separate installation, profile creation, authentication, and network authorization | Normal non-YOLO chat lifecycle, exact `openai-codex` provider, `web,memory,skills`, isolated process home, no repository working directory, and no external writes. |
| `repo-read` | Recognized but deliberately unavailable | The pinned Codex app-server integration cannot enforce and isolate `:read-only` end to end; the adapter exits 4 before starting Hermes. |

Write-capable Hermes repository work is not supported. Parent Codex or a native
Codex subagent owns repository exploration and every repository edit.

## Audited release and trust boundary

The integration was inspected on 2026-08-11 against Hermes Agent v0.20.0,
release tag `v2026.8.3`, at exact commit
[`3c27eb6234bf91b8ceee9e9071591b31e9b148cb`](https://github.com/NousResearch/hermes-agent/tree/3c27eb6234bf91b8ceee9e9071591b31e9b148cb).
The project is MIT-licensed at that revision. The tag itself is mutable, so
installation uses the full commit. Adapter preflight checks the checkout's Git
revision and cleanliness plus the exact first line of `--version`; a version
string alone is not source attestation.

No Hermes source, binary, skill, or installer is redistributed by this
repository. The framework contains original interoperability code and
documentation only.

Relevant pinned sources are the
[installer](https://github.com/NousResearch/hermes-agent/blob/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/scripts/install.sh),
[installation guide](https://github.com/NousResearch/hermes-agent/blob/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/website/docs/getting-started/installation.md),
[profiles guide](https://github.com/NousResearch/hermes-agent/blob/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/website/docs/user-guide/profiles.md),
[skills guide](https://github.com/NousResearch/hermes-agent/blob/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/website/docs/user-guide/features/skills.md),
[provider guide](https://github.com/NousResearch/hermes-agent/blob/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/website/docs/integrations/providers.md),
[toolset reference](https://github.com/NousResearch/hermes-agent/blob/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/website/docs/reference/toolsets-reference.md),
and [CLI parser](https://github.com/NousResearch/hermes-agent/blob/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/hermes_cli/_parser.py#L270-L438).

Hermes profiles isolate application state, not arbitrary host filesystem access.
The adapter therefore combines these fail-closed controls:

- derive the official-layout interpreter and entrypoint from
  `~/.hermes-ai-engineering-workflow/hermes-agent`, not a global launcher;
- attest source commit/cleanliness, version, exact profile bytes, disabled
  fallbacks, and the private-learning policy;
- isolate child `HOME`, `HERMES_HOME`, `CODEX_HOME`, and temporary storage under
  the dedicated integration root;
- use a small environment allowlist so normal host credentials do not propagate;
- exclude `file`, `terminal`, `code_execution`, browser automation, delegation,
  MCP, plugins, and the broad `safe` toolset;
- start in private temporary storage outside the repository;
- bound output while reading it and reject malformed or credential-bearing
  source URLs; and
- compare repository contents, links, directories, and Git status before and
  after every attempted invocation, including timeout and interruption.

These controls minimize and detect capability misuse; they are not an operating-
system sandbox. A process running as the same host user can access more than its
model-facing tool list. Use Codex-only mode when that residual risk is unsuitable.

## Why `repo-read` fails closed in v0.20.0

Hermes documents a Codex app-server runtime and Codex permission profiles. The
desired chain was Hermes -> `codex app-server` -> `:read-only`. Pinned source and
disposable protocol checks found four blockers:

1. Hermes constructs a permission-profile value but omits it from
   `thread/start`; only the Codex configuration default governs the child.
2. `/codex-runtime codex_app_server` has no read-only override. Migration writes
   `default_permissions = ":workspace"`, migrates integrations, and registers a
   Hermes callback.
3. Migration ignores `CODEX_HOME` and derives `<process HOME>/.codex`, while
   the eventual runtime child inherits `CODEX_HOME`. With an ordinary process
   home this can touch normal Codex configuration; with this framework's
   isolated process home it instead writes a second private Codex directory,
   leaving migration and runtime pointed at different configurations.
4. A separate user `default_permissions = ":read-only"` plus the managed value
   produces duplicate top-level TOML; Codex CLI 0.144.6 rejected that disposable
   configuration.

Pinned evidence is in the
[app-server request construction](https://github.com/NousResearch/hermes-agent/blob/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/agent/transports/codex_app_server_session.py#L274-L346),
[runtime switch](https://github.com/NousResearch/hermes-agent/blob/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/hermes_cli/codex_runtime_switch.py),
and [migration](https://github.com/NousResearch/hermes-agent/blob/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/hermes_cli/codex_runtime_plugin_migration.py).

An isolated Codex 0.144.6 app-server canary verified that one valid
`default_permissions = ":read-only"` config reports a read-only sandbox and
blocks shell redirection. That proves the Codex primitive, not the Hermes
boundary. A future release may enable `repo-read` only after it can select the
profile without unsafe migration, attest effective permissions, leave normal
Codex config byte-identical, and make both shell-write and `apply_patch`-write
canaries fail without an approval the adapter can accept.

The Hermes-first app-server topology is a different opt-in beta: Hermes owns the
session while Codex owns the model/tool loop. This Codex-first framework does not
adopt it.

## Profile-private self-improvement

The dedicated profile preserves useful Hermes learning without making it shared
project truth. The complete supplied config enables automatic private memory,
weekly curator maintenance, and `skills.write_approval: true`, which stages
learned-skill changes for profile-local review. It sets
`skills.external_dirs: []`, disables cross-provider fallback, and never mounts a
repository skill directory.

Private artifacts can include:

- `memories/MEMORY.md` and `memories/USER.md`;
- profile `skills/`, usage records, archives, and curator backups;
- `pending/skills/*.json` for approval-staged learned-skill changes;
- curator state/reports, sessions, logs, and `state.db`; and
- isolated runtime/cache/auth support under the dedicated integration root.

Memory, learned-skill, and curator targets stay beneath
`~/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow/`.
Preflight rejects links, repository/profile overlap, and multiply linked regular
files in mutable private trees, so a private write cannot alias a shared file.
`guard_agent_created` is an additional content scan, not a sandbox. The adapter
uses the normal `chat -q -Q` lifecycle instead of `-z`, avoiding YOLO/auto-hook
mode and allowing normal session finalization. It still does not claim every
turn produces a durable lesson.

Repository `.agents/skills` is the one canonical shared skill tree for Codex and
Copilot. Hermes must never receive it through `external_dirs`, because Hermes's
foreground skill manager can edit external skills. A private lesson becomes
shared only through a **separate parent-Codex change**. Promotion requires:

1. evidence that the lesson is reusable and sufficiently stable;
2. review for duplication and stale or conflicting policy;
3. placement at the narrowest appropriate scope;
4. an explicit reviewable diff; and
5. normal verification before acceptance.

Hermes sessions may retain private transcripts inside the isolated profile. Raw
transcripts, private memory, credentials, and session-only details are not
automatically copied into parent context or durable repository state.

## Separate, explicit installation

Framework adoption never installs Hermes. The official installer can install or
offer to install Git, Apple Command Line Tools, system packages, managed Python,
managed Node, Python dependencies, and Node dependencies. In its normal layout
it also creates launchers and may edit shell startup files. The procedure below
uses a private process `HOME`, isolated caches, `--skip-setup`,
`--skip-browser`, and strict prerequisites to keep effects under
`~/.hermes-ai-engineering-workflow`. It remains a separate networked software-
installation decision.

Run every command in this section in the **macOS host Terminal**, not a VS Code
terminal inside a Dev Container. Start with the current directory set to this
framework repository. Nothing in the framework invokes these commands.

First verify prerequisites. This is read-only and makes no persistent change.
Requiring existing Git, compatible Node/npm, ripgrep, and ffmpeg prevents this
procedure from invoking Homebrew or Apple Command Line Tools:

```bash
command -v git
git --version
command -v node
node --version
command -v npm
npm --version
command -v rg
rg --version
command -v ffmpeg
ffmpeg -version
node -e 'const [a,b]=process.versions.node.split(".").map(Number); process.exit(a > 22 || (a === 22 && b >= 22) ? 0 : 1)'
node -e 'const {execFileSync}=require("node:child_process"); const [a,b]=execFileSync("npm",["--version"],{encoding:"utf8"}).trim().split(".").map(Number); process.exit(a === 11 && b >= 10 && b <= 16 ? 1 : 0)'
```

Every `command -v` must print a path, Git must run, Node must be at least
22.22, and both `node -e` commands must exit silently with status 0. The second
rejects npm 11.10 through 11.16. If any check fails, stop and keep `disabled`
mode. Installing or updating a prerequisite is a separate host change.

Prove that no prior isolated checkout would be overwritten. This is read-only;
success is silent exit status 0:

```bash
test ! -e "$HOME/.hermes-ai-engineering-workflow/hermes-agent"
```

Record hashes of any normal Codex config/auth files. This reads those files and
creates one temporary checksum list but never copies or prints credential
contents. It supports the post-setup isolation check:

```bash
: > /tmp/ai-workflow-codex-before.sha256
for AI_WORKFLOW_CODEX_FILE in "$HOME/.codex/config.toml" "$HOME/.codex/auth.json"; do
  if [ -f "$AI_WORKFLOW_CODEX_FILE" ]; then
    shasum -a 256 "$AI_WORKFLOW_CODEX_FILE" >> /tmp/ai-workflow-codex-before.sha256
  fi
done
```

Create private host/Codex homes, temporary storage, and installer caches. This
persistently writes only beneath the isolated root and is reversed by removing
that root after the uninstall procedure:

```bash
mkdir -p \
  "$HOME/.hermes-ai-engineering-workflow/home" \
  "$HOME/.hermes-ai-engineering-workflow/codex-home" \
  "$HOME/.hermes-ai-engineering-workflow/tmp" \
  "$HOME/.hermes-ai-engineering-workflow/cache/uv" \
  "$HOME/.hermes-ai-engineering-workflow/cache/npm"
chmod 700 \
  "$HOME/.hermes-ai-engineering-workflow" \
  "$HOME/.hermes-ai-engineering-workflow/home" \
  "$HOME/.hermes-ai-engineering-workflow/codex-home" \
  "$HOME/.hermes-ai-engineering-workflow/tmp"
```

Download the installer from the exact audited commit. This performs a network
read and creates one removable `/tmp` file; it does not install:

```bash
curl -fL https://raw.githubusercontent.com/NousResearch/hermes-agent/3c27eb6234bf91b8ceee9e9071591b31e9b148cb/scripts/install.sh -o /tmp/hermes-agent-3c27eb6-install.sh
```

Inspect the complete script and options before deciding to continue. This is
read-only:

```bash
less /tmp/hermes-agent-3c27eb6-install.sh
```

Only after accepting the audited side effects, run the installer. This is a
persistent networked install. The environment redirects host home, state,
temporary files, and caches to the isolated root. The flags pin the source and
skip setup, browser installation, bundled skills, and interactive stages:

```bash
env \
  HOME="$HOME/.hermes-ai-engineering-workflow/home" \
  HERMES_HOME="$HOME/.hermes-ai-engineering-workflow" \
  HERMES_INSTALL_DIR="$HOME/.hermes-ai-engineering-workflow/hermes-agent" \
  TMPDIR="$HOME/.hermes-ai-engineering-workflow/tmp" \
  XDG_CACHE_HOME="$HOME/.hermes-ai-engineering-workflow/cache" \
  UV_CACHE_DIR="$HOME/.hermes-ai-engineering-workflow/cache/uv" \
  UV_PYTHON_INSTALL_DIR="$HOME/.hermes-ai-engineering-workflow/python" \
  UV_PYTHON_BIN_DIR="$HOME/.hermes-ai-engineering-workflow/python-bin" \
  npm_config_cache="$HOME/.hermes-ai-engineering-workflow/cache/npm" \
  PATH="$HOME/.hermes-ai-engineering-workflow/home/.local/bin:$PATH" \
  bash /tmp/hermes-agent-3c27eb6-install.sh \
    --commit 3c27eb6234bf91b8ceee9e9071591b31e9b148cb \
    --dir "$HOME/.hermes-ai-engineering-workflow/hermes-agent" \
    --hermes-home "$HOME/.hermes-ai-engineering-workflow" \
    --skip-setup \
    --skip-browser \
    --no-skills \
    --non-interactive
```

Expected persistent output is the pinned checkout, virtual environment, managed
uv/Python where needed, dependencies, and private launchers beneath the isolated
root. The explicit uv locations also keep the virtual environment's interpreter
symlink inside that root so adapter attestation can accept the official layout
without trusting a system or normal-home interpreter. With passed prerequisites
and private `HOME`, this procedure should not
invoke Homebrew/Command Line Tools, overwrite normal `~/.local/bin`, edit normal
shell startup files, create normal `~/.hermes`, or touch normal `~/.codex`.
Abort and review if output proposes one of those actions.

Verify the runtime, commit, and clean checkout. These commands are read-only.
The version and commit must match exactly; the final Git command prints nothing:

```bash
env \
  HOME="$HOME/.hermes-ai-engineering-workflow/home" \
  HERMES_HOME="$HOME/.hermes-ai-engineering-workflow" \
  CODEX_HOME="$HOME/.hermes-ai-engineering-workflow/codex-home" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/venv/bin/python" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/hermes" --version
git -C "$HOME/.hermes-ai-engineering-workflow/hermes-agent" rev-parse HEAD
git -C "$HOME/.hermes-ai-engineering-workflow/hermes-agent" status --porcelain --untracked-files=all
```

Expected version: `Hermes Agent v0.20.0 (2026.8.3)`. Expected commit:
`3c27eb6234bf91b8ceee9e9071591b31e9b148cb`.

After verification, remove the downloaded installer. The first command reports
the size reclaimed by deleting only that file:

```bash
du -h /tmp/hermes-agent-3c27eb6-install.sh
rm /tmp/hermes-agent-3c27eb6-install.sh
```

## Dedicated profile and authentication

Continue in the **macOS host Terminal** at the framework repository root. These
commands always pass isolated `HOME`, `HERMES_HOME`, and `CODEX_HOME`; do not
replace them with plain global `hermes` commands.

Create a fresh profile without an alias or bundled skills. This persistently
creates only the dedicated profile and its private marker:

```bash
env \
  HOME="$HOME/.hermes-ai-engineering-workflow/home" \
  HERMES_HOME="$HOME/.hermes-ai-engineering-workflow" \
  CODEX_HOME="$HOME/.hermes-ai-engineering-workflow/codex-home" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/venv/bin/python" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/hermes" \
  profile create ai-engineering-workflow --no-skills --no-alias
chmod 700 \
  "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow"
```

Profile creation follows the host umask; the final persistent `chmod` makes the
adapter's owner-only profile boundary deterministic.

Authenticate before installing the byte-exact profile template. This networked,
interactive OAuth/device action writes credentials only inside the isolated
Hermes profile. The isolated `CODEX_HOME` prevents importing or refreshing
normal Codex credentials. Hermes may update generated profile config during
login, so the reviewed template comes afterward:

```bash
env \
  HOME="$HOME/.hermes-ai-engineering-workflow/home" \
  HERMES_HOME="$HOME/.hermes-ai-engineering-workflow" \
  CODEX_HOME="$HOME/.hermes-ai-engineering-workflow/codex-home" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/venv/bin/python" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/hermes" \
  -p ai-engineering-workflow auth add openai-codex
```

Back up post-auth config, then replace it with the complete reviewed template.
These are persistent profile-local writes. The backup supplies reversal until
the adapter check succeeds:

```bash
cp \
  "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow/config.yaml" \
  "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow/config.yaml.pre-ai-workflow"
install -m 600 \
  "$PWD/adapters/hermes/profile-config.yaml" \
  "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow/config.yaml"
```

Run the adapter's local status check from this framework root. It validates the
official layout, pinned source, version, isolated paths, exact profile, and local
presence of dedicated auth without performing an OAuth refresh. It makes no
repository or external change:

```bash
python3 scripts/hermes_adapter.py status
```

Expected JSON contains `"state": "ready"`, provider `openai-codex`, toolsets
`web`, `memory`, and `skills`, and `"repository_access": "none"`. This proves
local readiness, not a live provider call. If disabled, use its classified
reason; do not switch providers, update, reinstall, or reauthenticate
automatically.

After success, delete the config backup. The first command reports the space
reclaimed by removing only that profile-local copy:

```bash
du -h "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow/config.yaml.pre-ai-workflow"
rm "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow/config.yaml.pre-ai-workflow"
```

## Use from Codex and smoke verification

The parent applies routing policy, obtains explicit authorization for network
reads, and prepares request JSON matching `request.schema.json`. The adapter
uses Hermes's supported `chat -q -Q` form with explicit provider, toolsets,
source, and turn limit. Provider enforcement comes from explicit argv plus an
exact profile with both fallback mechanisms disabled; Hermes v0.20.0 offers no
independent usage-file attestation for this chat path.

For the supplied harmless smoke request, stay in the **macOS host Terminal** and
make the consuming repository current. This performs authorized network reads
and writes private Hermes session/memory/skill-review state. It does not
intentionally write the repository:

```bash
python3 scripts/hermes_adapter.py research \
  --repo "$PWD" \
  --request adapters/hermes/smoke-request.json \
  --network-authorized
```

Success is exit 0 plus one schema-valid result with cited sources, empty
`repository_files_inspected`, and `prohibited_actions_not_performed: true`.
Parent Codex still verifies material claims. Recursion, repository mutation,
invalid or oversized output, credential-bearing URLs, timeout, interruption,
incompatible source/version/profile, missing dedicated auth, or non-success
child status is a nonzero failure.

Now verify normal Codex files remain byte-identical. This is read-only; existing
files report `OK`. The final commands show and remove the temporary checksum
list, reclaiming its displayed size:

```bash
if [ -s /tmp/ai-workflow-codex-before.sha256 ]; then
  shasum -a 256 -c /tmp/ai-workflow-codex-before.sha256
else
  echo "No normal Codex config/auth files existed before setup."
fi
du -h /tmp/ai-workflow-codex-before.sha256
rm /tmp/ai-workflow-codex-before.sha256
```

No live smoke was run while producing the framework because Hermes was absent
and the host prerequisites were incomplete. Executable-fixture coverage and
unverified live boundaries are in `docs/verification.md`.

## Manual external-research entry

A manual Hermes-first repository session is not an MVP mode. For manual external
research only, create and enter the private workspace from the **macOS host
Terminal**. Directory creation persists; `cd` affects only the current shell:

```bash
mkdir -p "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow/workspace"
cd "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow/workspace"
```

Start normal interactive chat with only the reviewed toolsets and isolated
homes. This may perform network reads and persist profile-private sessions,
memory, approval-staged skills, and curator state. It bypasses adapter result and
snapshot guards, so it is not Codex delegation:

```bash
env \
  HOME="$HOME/.hermes-ai-engineering-workflow/home" \
  HERMES_HOME="$HOME/.hermes-ai-engineering-workflow" \
  CODEX_HOME="$HOME/.hermes-ai-engineering-workflow/codex-home" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/venv/bin/python" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/hermes" \
  -p ai-engineering-workflow chat \
  --provider openai-codex \
  --toolsets web,memory,skills
```

Do not enable `/codex-runtime`, use `--yolo`/`-z`, add repository paths to
`skills.external_dirs`, or point manual Hermes at a repository.

## Context overhead

Normal Codex loads compact root `AGENTS.md` plus eight skill metadata entries.
Selected bodies, the Hermes guide, schemas, profile, and adapter load only when
relevant. Hermes does not start during ordinary work.

After installation, this read-only **macOS host Terminal** diagnostic measures
Hermes prompt composition using the isolated profile:

```bash
env \
  HOME="$HOME/.hermes-ai-engineering-workflow/home" \
  HERMES_HOME="$HOME/.hermes-ai-engineering-workflow" \
  CODEX_HOME="$HOME/.hermes-ai-engineering-workflow/codex-home" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/venv/bin/python" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/hermes" \
  -p ai-engineering-workflow prompt-size --json
```

Record output before and after reviewed profile changes. No value is claimed
because Hermes was not installed in the verification environment.

## Update, disable, and reverse

Do not run plain `hermes update`. The adapter accepts exactly the audited
v0.20.0 source. Updating requires a new framework release to pin and audit the
replacement, update source/version checks, and rerun provider, isolation,
learning, recursion, output-limit, and negative-write tests.

The simplest disablement is to stop invoking the optional skill or adapter; no
daemon, gateway, hook, service, or scheduled job was enabled. For a hard but
reversible disable, run this in the **macOS host Terminal**. It persistently
renames only the dedicated profile, so preflight fails:

```bash
mv \
  "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow" \
  "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow.disabled"
```

Restore it with:

```bash
mv \
  "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow.disabled" \
  "$HOME/.hermes-ai-engineering-workflow/profiles/ai-engineering-workflow"
```

Before uninstalling, inspect the official dry run from the **macOS host
Terminal**. It should name only isolated installation/data and private-home
launchers. This performs no persistent change:

```bash
env \
  HOME="$HOME/.hermes-ai-engineering-workflow/home" \
  HERMES_HOME="$HOME/.hermes-ai-engineering-workflow" \
  CODEX_HOME="$HOME/.hermes-ai-engineering-workflow/codex-home" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/venv/bin/python" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/hermes" \
  uninstall --dry-run
```

Default uninstall persistently removes code/launchers while retaining data for
recovery. Use it only if that is the reviewed dry-run outcome:

```bash
env \
  HOME="$HOME/.hermes-ai-engineering-workflow/home" \
  HERMES_HOME="$HOME/.hermes-ai-engineering-workflow" \
  CODEX_HOME="$HOME/.hermes-ai-engineering-workflow/codex-home" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/venv/bin/python" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/hermes" \
  uninstall
```

Full uninstall is destructive: it removes private auth, memories, learned and
pending skills, curator data, sessions, logs, caches, and the isolated Codex
home. If that is the explicit intent, run `uninstall --full` instead of the
previous command after reviewing the dry run:

```bash
env \
  HOME="$HOME/.hermes-ai-engineering-workflow/home" \
  HERMES_HOME="$HOME/.hermes-ai-engineering-workflow" \
  CODEX_HOME="$HOME/.hermes-ai-engineering-workflow/codex-home" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/venv/bin/python" \
  "$HOME/.hermes-ai-engineering-workflow/hermes-agent/hermes" \
  uninstall --full
```

Verify removal with this read-only check; success is silent when the isolated
checkout is gone:

```bash
test ! -e "$HOME/.hermes-ai-engineering-workflow/hermes-agent"
```

If full uninstall retains an unexpected isolated artifact, inspect it before
moving the one exact root to macOS Trash for recoverable cleanup:

```bash
du -sh "$HOME/.hermes-ai-engineering-workflow"
test ! -e "$HOME/.Trash/hermes-ai-engineering-workflow-disabled"
mv \
  "$HOME/.hermes-ai-engineering-workflow" \
  "$HOME/.Trash/hermes-ai-engineering-workflow-disabled"
```

The move reclaims no space until Trash is emptied, but it is reversible by
moving the directory back with this **macOS host Terminal** command, provided
the original path is still absent:

```bash
test ! -e "$HOME/.hermes-ai-engineering-workflow"
mv \
  "$HOME/.Trash/hermes-ai-engineering-workflow-disabled" \
  "$HOME/.hermes-ai-engineering-workflow"
```

Because installation/runtime used private `HOME`, `HERMES_HOME`, and
`CODEX_HOME`, reversal does not delete normal `~/.hermes`,
`~/.codex`, Keychain entries, shared repository policy, project profiles, or
durable state. Framework removal remains independent through
`scripts/adopt.py remove` from the exact installed framework version. If any
verification fails, the most useful diagnostic is adapter `status` plus the
exact failing Git/path/profile reason; do not auto-update or switch providers.
