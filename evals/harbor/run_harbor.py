#!/usr/bin/env python3
"""Run the frozen Harbor evaluation with its local tools on PATH."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys


EVAL_ROOT = Path(__file__).resolve().parent
VENV_BIN = EVAL_ROOT / ".venv" / "bin"
HARBOR = VENV_BIN / "harbor"
UV = VENV_BIN / "uv"


def main() -> int:
    missing = [str(path) for path in (HARBOR, UV) if not path.is_file()]
    if missing:
        print(
            "evaluation tools are missing; install evals/harbor/requirements.txt: "
            + ", ".join(missing),
            file=sys.stderr,
        )
        return 2

    gh = shutil.which("gh")
    if gh is None:
        print("host GitHub CLI is required for provider authentication", file=sys.stderr)
        return 2
    token_result = subprocess.run(
        [gh, "auth", "token"],
        capture_output=True,
        check=False,
        text=True,
    )
    gh_token = token_result.stdout.strip()
    if token_result.returncode != 0 or not gh_token:
        print(
            "host GitHub CLI authentication is unavailable; run `gh auth login`",
            file=sys.stderr,
        )
        return 2

    environment = os.environ.copy()
    environment["PATH"] = os.pathsep.join(
        [str(VENV_BIN), environment.get("PATH", "")]
    )
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(EVAL_ROOT), environment.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    environment["CODEX_FORCE_AUTH_JSON"] = "1"
    environment["HARBOR_EVAL_GH_TOKEN"] = gh_token

    command = [str(HARBOR), "jobs", "start", *sys.argv[1:]]
    return subprocess.run(command, env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
