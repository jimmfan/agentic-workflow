#!/usr/bin/env python3
"""Codex command adapter for tests/behavior.py; no scoring or routing logic.

Uses the existing persistence pilot's bounded process capture. Each invocation
gets an isolated home, prompt audit and raw directory outside the subject tree.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from evals.persistence import bounded_process, codex_binary  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--web", action="store_true")
    args = parser.parse_args()
    workspace = Path.cwd().resolve()
    output_root = args.output_root.resolve()
    if output_root.is_relative_to(ROOT) or output_root.is_relative_to(workspace):
        raise ValueError("Keep raw evidence outside the repository and subject tree")
    output_root.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="subject-", dir=output_root))
    raw = run / "raw"
    raw.mkdir()
    home = run / "codex-home"
    home.mkdir(mode=0o700)
    scratch = run / "scratch"
    scratch.mkdir()
    prompt = sys.stdin.read()
    binary = Path(codex_binary())
    python = Path(sys.executable).resolve()
    uv = Path(shutil.which("uv")).resolve()
    git = Path(subprocess.check_output(["xcrun", "--find", "git"], text=True).strip())
    source_auth = (
        Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
    )
    if source_auth.is_symlink() or not source_auth.is_file():
        raise ValueError("Existing regular auth.json required")
    filesystem = {
        ":minimal": "read",
        str(workspace): "write",
        str(scratch): "write",
        str(binary): "read",
        str(python.parent.parent): "read",
        str(uv): "read",
        str(git.parent.parent): "read",
    }
    path = ":".join(
        (str(python.parent), str(uv.parent), str(git.parent), "/usr/bin", "/bin")
    )
    child_environment = {
        "PATH": path,
        "UV_PYTHON": str(python),
        "UV_CACHE_DIR": str(scratch / "uv-cache"),
        "UV_OFFLINE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    settings = [
        'model="gpt-5.6-sol"',
        'model_reasoning_effort="medium"',
        'approval_policy="never"',
        'default_permissions="audit"',
        "permissions.audit.filesystem={"
        + ",".join(f"{json.dumps(k)}={json.dumps(v)}" for k, v in filesystem.items())
        + "}",
        "permissions.audit.network.enabled=false",
        f'web_search="{"live" if args.web else "disabled"}"',
        "features.apps=false",
        "features.plugins=false",
        "features.memories=false",
        "features.multi_agent=true",
        "agents.max_threads=3",
        "features.shell_snapshot=false",
        'shell_environment_policy.inherit="none"',
        "shell_environment_policy.set={"
        + ",".join(f"{k}={json.dumps(v)}" for k, v in child_environment.items())
        + "}",
        "allow_login_shell=false",
        'model_provider="openai"',
        "project_doc_max_bytes=65536",
    ]
    config = [item for setting in settings for item in ("-c", setting)]
    env = {"CODEX_HOME": str(home), "PATH": path, "LANG": "en_US.UTF-8"}
    record = {
        "workspace": str(workspace),
        "model": "gpt-5.6-sol",
        "reasoning_effort": "medium",
        "settings": settings,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "execution": "not-started",
        "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "cli_version": subprocess.check_output(
            [binary, "--version"], text=True
        ).strip(),
        "limits": {"seconds": 360, "output_bytes": 2_000_000},
    }
    code = 2
    try:
        shutil.copyfile(source_auth, home / "auth.json")
        (home / "auth.json").chmod(0o600)
        (raw / "prompt.txt").write_text(prompt)
        audit = subprocess.run(
            [binary, *config, "-C", str(workspace), "debug", "prompt-input", prompt],
            cwd=workspace,
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
            check=True,
        )
        (raw / "prompt-input.json").write_text(audit.stdout)
        actual = json.dumps(json.loads(audit.stdout))
        for forbidden in (
            str(ROOT),
            "remaining-audit-behavior/README.md",
            "source-repository instructions",
            "prior_conversation",
            "<memory",
        ):
            if forbidden in actual:
                raise ValueError(f"Prompt isolation failed: {forbidden}")
        for location in re.findall(r"\(file: ([^)]+)\)", actual):
            if not any(
                Path(location).is_relative_to(parent)
                for parent in (workspace, home / "skills/.system")
            ):
                raise ValueError("Unexpected skill location in prompt")
        record["prompt_input_sha256"] = hashlib.sha256(
            audit.stdout.encode()
        ).hexdigest()
        command = [
            str(binary),
            "exec",
            "--ignore-user-config",
            "--ignore-rules",
            *config,
            "-C",
            str(workspace),
            "--skip-git-repo-check",
            "--json",
            "-o",
            str(raw / "response.txt"),
            "-",
        ]
        record["command"] = command
        status, code, elapsed = bounded_process(
            command, cwd=workspace, env=env, prompt=prompt, raw=raw
        )
        record.update(execution=status, returncode=code, elapsed_seconds=elapsed)
        if (raw / "response.txt").exists():
            print((raw / "response.txt").read_text())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        record.update(execution="infrastructure-blocked", error=str(exc))
    finally:
        (home / "auth.json").unlink(missing_ok=True)
        record["credential_copy_removed"] = not (home / "auth.json").exists()
        (run / "invocation.json").write_text(json.dumps(record, indent=2) + "\n")
        print(f"Invocation evidence: {run}", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
