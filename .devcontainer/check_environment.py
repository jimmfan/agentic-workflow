#!/usr/bin/env python3
"""Fail fast when the development container is missing a project prerequisite."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
from typing import Sequence


MINIMUM_GH_VERSION = (2, 97, 0)
EXPECTED_CODEX_EXTENSION = "openai.chatgpt@26.715.31925"
EXPECTED_CODEX_HOME = Path("/home/vscode/.codex")
CODEX_SYSTEM_CONFIG = Path("/etc/codex/config.toml")
DEVCONTAINER_CONFIG = Path(".devcontainer/devcontainer.json")


def run(command: Sequence[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
    return result.stdout


def require_command(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(f"required command is not on PATH: {name}")
    return path


def require_codex_configuration() -> None:
    configured_home = os.environ.get("CODEX_HOME")
    if configured_home != str(EXPECTED_CODEX_HOME):
        raise RuntimeError(
            f"CODEX_HOME must be {EXPECTED_CODEX_HOME}; found {configured_home!r}"
        )
    if not EXPECTED_CODEX_HOME.is_dir() or not os.access(EXPECTED_CODEX_HOME, os.W_OK):
        raise RuntimeError(f"Codex state directory is missing or not writable: {EXPECTED_CODEX_HOME}")
    home_mode = stat.S_IMODE(EXPECTED_CODEX_HOME.stat().st_mode)
    if home_mode != 0o700:
        raise RuntimeError(
            f"Codex state directory must have mode 700; found {home_mode:03o}"
        )

    if not CODEX_SYSTEM_CONFIG.is_file():
        raise RuntimeError(f"Codex system configuration is missing: {CODEX_SYSTEM_CONFIG}")
    config_text = CODEX_SYSTEM_CONFIG.read_text(encoding="utf-8")
    if not re.search(
        r'^\s*cli_auth_credentials_store\s*=\s*"file"\s*$',
        config_text,
        re.MULTILINE,
    ):
        raise RuntimeError("Codex file-backed credential storage is not configured")

    auth_file = EXPECTED_CODEX_HOME / "auth.json"
    if auth_file.exists():
        auth_mode = stat.S_IMODE(auth_file.stat().st_mode)
        if auth_mode != 0o600:
            raise RuntimeError(f"Codex auth.json must have mode 600; found {auth_mode:03o}")

    devcontainer = json.loads(DEVCONTAINER_CONFIG.read_text(encoding="utf-8"))
    extensions = devcontainer["customizations"]["vscode"]["extensions"]
    if EXPECTED_CODEX_EXTENSION not in extensions:
        raise RuntimeError(
            f"Dev Container must pin the Codex extension to {EXPECTED_CODEX_EXTENSION}"
        )

    bubblewrap = require_command("bwrap")
    run([bubblewrap, "--version"])
    unshare = require_command("unshare")
    run([unshare, "--user", "--map-root-user", "true"])


def main() -> int:
    if sys.version_info[:2] != (3, 14):
        found = ".".join(str(part) for part in sys.version_info[:3])
        raise RuntimeError(f"Python 3.14 is required in this container; found {found}")

    uv = require_command("uv")
    uv_version = run([uv, "--version"]).strip()

    git = require_command("git")
    git_version = run([git, "--version"]).strip()

    gh = require_command("gh")
    gh_output = run([gh, "--version"])
    match = re.search(r"gh version ([0-9]+)\.([0-9]+)\.([0-9]+)", gh_output)
    if match is None:
        raise RuntimeError(f"could not parse GitHub CLI version from: {gh_output.strip()!r}")
    gh_version = tuple(int(part) for part in match.groups())
    if gh_version < MINIMUM_GH_VERSION:
        found = ".".join(str(part) for part in gh_version)
        required = ".".join(str(part) for part in MINIMUM_GH_VERSION)
        raise RuntimeError(f"GitHub CLI {required} or newer is required; found {found}")

    gh_skill_help = run([gh, "skill", "install", "--help"])
    missing_options = [option for option in ("--pin", "--scope") if option not in gh_skill_help]
    if missing_options:
        raise RuntimeError(
            "gh skill install is missing required options: " + ", ".join(missing_options)
        )

    require_codex_configuration()

    python_version = ".".join(str(part) for part in sys.version_info[:3])
    print(
        "OK: development container is ready "
        f"(Python {python_version}; {uv_version}; {git_version}; "
        f"GitHub CLI {'.'.join(str(part) for part in gh_version)}; "
        f"Codex {EXPECTED_CODEX_EXTENSION.removeprefix('openai.chatgpt@')})."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
