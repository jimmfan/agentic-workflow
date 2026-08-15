#!/usr/bin/env bash
# Prepare the persistent Codex state volume, then verify the complete development toolchain.

set -euo pipefail

sudo install -d -m 0700 -o vscode -g vscode /home/vscode/.codex
sudo chown -R vscode:vscode /home/vscode/.codex
chmod 0700 /home/vscode/.codex

if [[ -f /home/vscode/.codex/auth.json ]]; then
  chmod 0600 /home/vscode/.codex/auth.json
fi

python3 .devcontainer/check_environment.py
