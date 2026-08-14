#!/usr/bin/env python3
"""Fail fast when a rebuilt development container is missing a prerequisite."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from typing import Sequence


MINIMUM_GH_VERSION = (2, 97, 0)


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

    python_version = ".".join(str(part) for part in sys.version_info[:3])
    print(
        "OK: development container is ready "
        f"(Python {python_version}; {uv_version}; {git_version}; "
        f"GitHub CLI {'.'.join(str(part) for part in gh_version)})."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
