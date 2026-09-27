#!/usr/bin/env bash
# Prepare the persistent Codex and Claude Code state volumes, then verify the complete
# development toolchain.

set -euo pipefail

sudo install -d -m 0700 -o vscode -g vscode /home/vscode/.codex
sudo chown -R vscode:vscode /home/vscode/.codex
chmod 0700 /home/vscode/.codex

if [[ -f /home/vscode/.codex/auth.json ]]; then
  chmod 0600 /home/vscode/.codex/auth.json
fi

sudo install -d -m 0700 -o vscode -g vscode /home/vscode/.claude
sudo chown -R vscode:vscode /home/vscode/.claude
chmod 0700 /home/vscode/.claude

if [[ -f /home/vscode/.claude/.credentials.json ]]; then
  chmod 0600 /home/vscode/.claude/.credentials.json
fi

python3 .devcontainer/check_environment.py
