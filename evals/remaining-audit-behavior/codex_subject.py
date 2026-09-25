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
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from evals.persistence import bounded_process, codex_binary  # noqa: E402


def verify_isolation(binary, config, workspace, env, run, scratch):
    """Reject this adapter before loading credentials when deny checks fail."""
    outside = run / "isolation-canary.txt"
    credential = run / "codex-home/credential-canary.txt"
    outside.write_text("synthetic evaluation canary\n")
    credential.write_text("synthetic credential canary; not authentication\n")
    probe = scratch / "write-probe.txt"
    script = (
        "test -r AGENTS.md || exit 10; "
        f"if test -r {shlex.quote(str(outside))}; then "
        "echo outside-read-permitted; exit 11; fi; "
        f"if test -r {shlex.quote(str(credential))}; then "
        "echo credential-canary-readable; exit 12; fi; "
        f"printf probe > {shlex.quote(str(probe))} && "
        f"test -r {shlex.quote(str(probe))} && rm {shlex.quote(str(probe))} && "
        "python -c "
        + shlex.quote(
            "import subprocess, sys; "
            "subprocess.run([sys.executable, '-c', 'pass'], check=True)"
        )
    )
    checked = subprocess.run(
        [
            str(binary),
            "sandbox",
            *config,
            "-C",
            str(workspace),
            "-P",
            "audit",
            "/bin/sh",
            "-c",
            script,
        ],
        cwd=workspace,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    result = {
        "returncode": checked.returncode,
        "stdout": checked.stdout,
        "stderr": checked.stderr,
    }
    (run / "isolation.json").write_text(json.dumps(result, indent=2) + "\n")
    if checked.returncode:
        raise ValueError(
            "Subject isolation preflight failed; no credentials copied or model launched"
        )
    return result


def check_prompt_context(
    actual, *, workspace, home, output_root, scratch, launcher_tmp, runtime_root=None
):
    # Ignored task roots can be inside the authoring repository. Allow only
    # the subject and bundled-system-skill locations before checking leakage.
    audited = actual.replace(str(workspace), "<subject>").replace(
        str(home / "skills/.system"), "<system-skills>"
    )
    if runtime_root is not None:
        audited = audited.replace(str(runtime_root) + "/", "<cli-runtime>/")
    # Permission metadata names denied controller containers and writable
    # scratch. Match whole paths, not arbitrary descendants in those roots.
    for location in sorted(
        [
            str(output_root.parent),
            str(output_root),
            str(home),
            str(scratch),
            str(launcher_tmp),
        ],
        key=len,
        reverse=True,
    ):
        audited = re.sub(
            re.escape(location) + r'(?=[`"<>\\\s]|$)', "<permission-path>", audited
        )
    audited = re.sub(
        re.escape(str(home / "tmp/arg0")) + r"/[A-Za-z0-9_-]+",
        "<runtime-alias>",
        audited,
    )
    for forbidden in (
        str(ROOT),
        "remaining-audit-behavior/README.md",
        "source-repository instructions",
        "prior_conversation",
        "<memory",
    ):
        if forbidden in audited:
            raise ValueError(f"Prompt isolation failed: {forbidden}")
    allowed_roots = (workspace.resolve(), (home / "skills/.system").resolve())
    aliases = {}
    for alias, root in re.findall(r"- `(r\d+)` = `([^`]+)`", actual):
        resolved = Path(root).resolve()
        if not any(resolved.is_relative_to(parent) for parent in allowed_roots):
            raise ValueError("Unexpected skill root in prompt")
        if alias in aliases and aliases[alias] != resolved:
            raise ValueError("Conflicting skill roots in prompt")
        aliases[alias] = resolved
    for location in re.findall(r"\(file: ([^)]+)\)", actual):
        path = Path(location)
        if not path.is_absolute():
            if not path.parts or path.parts[0] not in aliases:
                raise ValueError("Unknown skill root in prompt")
            path = aliases[path.parts[0]].joinpath(*path.parts[1:])
        if not any(path.resolve().is_relative_to(parent) for parent in allowed_roots):
            raise ValueError("Unexpected skill location in prompt")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--web", action="store_true")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--timeout-seconds", type=int, default=360)
    args = parser.parse_args()
    if not 1 <= args.timeout_seconds <= 900:
        parser.error("--timeout-seconds must be between 1 and 900")
    workspace = Path.cwd().resolve()
    output_root = args.output_root.resolve()
    if (
        output_root.is_relative_to(ROOT)
        and not output_root.is_relative_to(ROOT / "evals/artifacts")
    ) or output_root.is_relative_to(workspace):
        raise ValueError(
            "Keep raw evidence outside the subject and in ignored artifacts or outside the repository"
        )
    output_root.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="subject-", dir=output_root))
    raw = run / "raw"
    raw.mkdir()
    home = run / "codex-home"
    home.mkdir(mode=0o700)
    scratch = run / "scratch"
    scratch.mkdir()
    launcher_tmp = run / "launcher-tmp"
    launcher_tmp.mkdir()
    prompt = sys.stdin.read()
    binary = Path(codex_binary())
    python = Path(sys.executable).resolve()
    uv = Path(shutil.which("uv")).resolve()
    git = Path(subprocess.check_output(["xcrun", "--find", "git"], text=True).strip())
    # Homebrew exposes python3 but the fixtures use the conventional `python`
    # command. Supply that alias only inside this disposable runtime directory.
    (scratch / "bin").mkdir()
    (scratch / "bin/python").symlink_to(python)
    source_auth = (
        Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
    )
    if source_auth.is_symlink() or not source_auth.is_file():
        raise ValueError("Existing regular auth.json required")
    filesystem = {
        ":root": "deny",
        ":minimal": "read",
        ":tmpdir": "deny",
        ":slash_tmp": "deny",
        str(output_root.parent): "deny",
        str(output_root): "deny",
        str(home): "deny",
        str(home / "skills/.system"): "read",
        str(workspace): "write",
        str(scratch): "write",
        str(binary): "read",
        str(python.parent.parent): "read",
        str(uv): "read",
        str(git.parent.parent): "read",
    }
    path = ":".join(
        (
            str(scratch / "bin"),
            str(python.parent),
            str(uv.parent),
            str(git.parent),
            "/usr/bin",
            "/bin",
        )
    )
    child_environment = {
        "PATH": path,
        # macOS framework Python otherwise reports a Homebrew alias outside
        # its allowed runtime directory when a fixture starts subprocesses.
        "PYTHONEXECUTABLE": str(python),
        "UV_PYTHON": str(python),
        "UV_CACHE_DIR": str(scratch / "uv-cache"),
        "UV_OFFLINE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "TMPDIR": str(scratch),
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    settings = [
        f"model={json.dumps(args.model)}",
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
    env = {
        "CODEX_HOME": str(home),
        "PATH": path,
        "LANG": "en_US.UTF-8",
        # :tmpdir is denied to subject tools; do not alias it to allowed scratch.
        "TMPDIR": str(launcher_tmp),
    }
    record = {
        "workspace": str(workspace),
        "model": args.model,
        "reasoning_effort": "medium",
        "settings": settings,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "execution": "not-started",
        "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "cli_version": subprocess.check_output(
            [binary, "--version"], text=True
        ).strip(),
        "limits": {"seconds": args.timeout_seconds, "output_bytes": 2_000_000},
    }
    code = 2
    try:
        record["isolation"] = verify_isolation(
            binary, config, workspace, env, run, scratch
        )
        if args.preflight_only:
            record.update(execution="preflight-completed", returncode=0)
            return 0
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
        check_prompt_context(
            actual,
            workspace=workspace,
            home=home,
            output_root=output_root,
            scratch=scratch,
            launcher_tmp=launcher_tmp,
            runtime_root=binary.parent.parent,
        )
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
            command,
            cwd=workspace,
            env=env,
            prompt=prompt,
            raw=raw,
            limits=record["limits"],
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
