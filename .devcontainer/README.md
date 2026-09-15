# Development container

This development container supplies the complete toolchain needed to develop and verify Agent Workflow without changing the macOS host's Python setup.
It uses Python 3.14 on Debian Bookworm, `uv`, Git, the GitHub CLI for authorized GitHub work, and an exactly pinned Codex extension with a persistent project-specific login volume.

The runtime uses only the Python standard library; development verification also uses Ruff and isolated package-build tooling.
Opening this container does not create a virtual environment or run a package sync.
The [documented locked verification commands](../docs/verification.md#maintainer-and-ci-gate) use `uv` to prepare the project environment and run its checks.

Codex stores its login and local state in the Docker volume `agent-workflow-instructions-codex-home`, mounted at `/home/vscode/.codex`.
The image configures file-backed credential storage through `/etc/codex/config.toml`; credentials are never copied into the image or repository.
`bubblewrap` and an unprivileged user namespace provide Codex's nested Linux sandbox.
The container uses `seccomp=unconfined` because Docker's default seccomp profile blocks that namespace operation.
This weakens syscall filtering for the entire development container, although the container remains non-privileged and does not mount the Docker socket.

## Open the repository in the container

On the **macOS host in VS Code**, install and enable the Microsoft **Dev Containers** extension if it is not already available.
Then open the Command Palette and select **Dev Containers: Reopen in Container**.
This builds the image and persistently caches it in Docker; it does not change the host Python installation.
The first build downloads the base image, the pinned `uv` image, the GitHub CLI feature, `bubblewrap`, and the configured VS Code extensions.
It also creates the project-specific Codex volume, but it does not authenticate it.

For this repository's sibling-checkout layout, the container adds a secondary mount of the workspace's parent directory at the same absolute path used on the macOS host.
This is required when the workspace is a linked Git worktree: its `.git` file points to metadata in the main checkout using an absolute host path.
Preserving that path makes the metadata reachable without depending on either checkout's directory name.
VS Code always opens the explicit short path `/workspace`, avoiding the secondary host-path alias.

After the workspace opens, the post-create check runs automatically.
Success ends with output resembling:

```text
OK: development container is ready (Python 3.14.x; uv 0.11.32; git version ...; GitHub CLI 2.98.0; Codex 26.715.31925).
```

The Dev Container selects `python3` as the default interpreter and Pylance as the language server.
This prevents its VS Code window from falling back to Jedi with a stale, deleted `.venv` interpreter.

## Verify and develop

Run the environment check from a **VS Code terminal inside this Dev Container**.
It is read-only and confirms the exact interpreter, required command-line interfaces, repository metadata access, Codex credential-store configuration, state permissions, extension pin, and Linux sandbox namespace support:

```bash
python3 .devcontainer/check_environment.py
```

Run every command in the [maintainer and CI gate](../docs/verification.md#maintainer-and-ci-gate) from the **same Dev Container terminal at the repository root**.
The gate checks Python formatting and lint, package contracts, evaluation tooling, wheel installation, and diff whitespace.
Dependency setup and isolated builds may need package-index access; lifecycle tests use disposable consumers and leave tracked source unchanged.

Normal CLI install and update require HTTPS access to GitHub to resolve and download a framework snapshot; they do not require GitHub CLI authentication.
Local snapshot overrides used by tests can avoid those network requests; see [distribution and lifecycle](../docs/architecture.md#distribution-and-lifecycle).
GitHub CLI authentication is needed only for separately authorized GitHub work that requires it.
If that work is required, run this persistent login in the **Dev Container terminal**:

```bash
gh auth login --hostname github.com --web
```

Verify it from the **same terminal** with this read-only command:

```bash
gh auth status --hostname github.com
```

Reverse that GitHub CLI login from the **same terminal** with:

```bash
gh auth logout --hostname github.com
```

## Authenticate and verify Codex

Open Codex in the **VS Code window attached to this Dev Container** and sign in when prompted.
That login persistently writes only to the `agent-workflow-instructions-codex-home` Docker volume.
A container rebuild remounts the same volume, so it should not require another login.

Verify the extension from a **VS Code terminal inside this Dev Container**:

```bash
code --list-extensions --show-versions |
  grep -F 'openai.chatgpt@26.715.31925'
```

Expected output is `openai.chatgpt@26.715.31925`.
Verify credential permissions without displaying their contents from the **same terminal**:

```bash
stat -c '%U:%G %a %n' \
  /home/vscode/.codex \
  /home/vscode/.codex/auth.json
```

Expected ownership is `vscode:vscode`; expected modes are `700` for the directory and `600` for `auth.json`.
If `auth.json` does not exist, complete the Codex sign-in first.

## Side effects and reversal

Container builds consume local Docker image/cache space.
Live GitHub CLI login stores credentials in the container user's configuration; Codex login stores credentials in `agent-workflow-instructions-codex-home`.
Rebuilding the container reapplies its configuration and preserves that volume.
To stop using the container, reopen the repository locally from the VS Code Command Palette.

Removing the Dev Container or its image does not delete the Codex volume.
After confirming that no remaining container needs it, remove that persistent login and state from the **macOS host Terminal** with:

```bash
docker volume rm agent-workflow-instructions-codex-home
```

This permanently deletes only this project's copied or newly created Codex login and local state.
Verify removal from the **same macOS host Terminal** with:

```bash
if docker volume inspect agent-workflow-instructions-codex-home >/dev/null 2>&1; then
  echo 'ERROR: Codex volume still exists.'
  exit 1
else
  echo 'Verified: project Codex volume is absent.'
fi
```

To reverse the committed configuration itself, restore the `.devcontainer/` files with version control after preserving any uncommitted work.
That removes Codex from future rebuilds but does not remove an existing container, image, or the persistent volume; clean those up separately only after confirming they are no longer needed.
