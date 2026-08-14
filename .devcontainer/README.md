# Development container

This development container supplies the complete toolchain needed to develop
and verify Agentic Workflow without changing the macOS host's Python setup. It
uses Python 3.14 on Debian Bookworm, `uv`, Git, and the GitHub CLI version whose
`gh skill` interface is the project's live-tested provider baseline.

The project itself has no third-party Python dependencies: its runtime,
installer, analyzer, release gate, and tests intentionally use only the Python
standard library. For that reason, opening this container does not create a
virtual environment or run a package sync. `uv` remains available for running
Python commands and for future dependency work if the project contract changes.

## Open the repository in the container

On the **macOS host in VS Code**, install and enable the Microsoft **Dev
Containers** extension if it is not already available. Then open the Command
Palette and select **Dev Containers: Reopen in Container**. This builds the
image and persistently caches it in Docker; it does not change the host Python
installation. The first build downloads the base image, the pinned `uv` image,
the GitHub CLI feature, and the configured VS Code extensions.

After the workspace opens, the post-create check runs automatically. Success
ends with output resembling:

```text
OK: development container is ready (Python 3.14.x; uv 0.11.32; git version ...; GitHub CLI 2.97.0).
```

## Verify and develop

Run the environment check from a **VS Code terminal inside this Dev
Container**. It is read-only and confirms the exact interpreter plus every
required command-line interface:

```bash
python3 .devcontainer/check_environment.py
```

Run the full repository gate from the **same Dev Container terminal at the
repository root**. It is read-only for tracked repository files and removes its
temporary test directories automatically:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

To run that same gate through `uv` without inventing a package or virtual
environment, use this equivalent command in the **same Dev Container terminal**:

```bash
uv run --no-project python skills/agentic-workflow/scripts/verify_package.py --tests
```

Provider installation and update additionally require GitHub authentication.
Authentication is not needed for ordinary development or the hermetic release
gate. If live provider work is required, run `gh auth login --hostname
github.com --web` in the **Dev Container terminal**, then verify it with `gh
auth status --hostname github.com` before running the lifecycle command.

## Side effects and reversal

Container builds consume local Docker image/cache space, and live GitHub CLI
login stores credentials in the container user's configuration. Rebuilding the
container reapplies this configuration. To stop using it, reopen the repository
locally from the VS Code Command Palette. To remove it completely, delete the
container and its image/cache from Docker, then remove the `.devcontainer/`
directory from the repository; none of those actions is required for normal
development.
