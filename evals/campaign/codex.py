"""Opt-in native Codex adapter for the campaign JSON stdin/stdout protocol.

Only synthetic disposable consumers belong here. Profiles are checked with an
unauthenticated sandbox command before any credential is copied or model runs.
See https://learn.chatgpt.com/docs/non-interactive-mode and /docs/permissions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

from evals.persistence import bounded_process

PROFILE = "campaign"
SETTINGS = {"binary", "auth_file", "allow_live", "preflight_only", "allow_subagents"}


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def _base_result() -> dict:
    return {
        "schema": 1,
        "execution_status": "infrastructure-blocked",
        "session_id": None,
        "response": "",
        "observations": {
            "same_session": None,
            "compaction_events": None,
            "active_context_tokens": None,
            "model": None,
            "reasoning_effort": None,
        },
        "traces": [],
        "error": None,
    }


def _directory(value: str, label: str) -> Path:
    path = Path(value)
    if not path.is_absolute() or path.is_symlink():
        raise ValueError(f"{label} must be an absolute, non-symlink directory")
    return path.resolve()


def _settings(
    request: dict, workspace: Path, home: Path, artifact: Path, binary: Path
) -> tuple[list[str], dict]:
    python = Path(sys.executable).resolve()
    scratch = home / "scratch"
    scratch.mkdir(exist_ok=True)
    (scratch / "bin").mkdir(exist_ok=True)
    alias = scratch / "bin/python"
    if not alias.exists():
        alias.symlink_to(python)
    path = os.pathsep.join(
        (str(scratch / "bin"), str(python.parent), "/usr/local/bin", "/usr/bin", "/bin")
    )
    child_env = {
        "PATH": path,
        "HOME": str(home / "user-home"),
        "TMPDIR": str(scratch),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "UV_OFFLINE": "1",
        "UV_CACHE_DIR": str(scratch / "uv-cache"),
    }
    filesystem = {
        ":root": "deny",
        ":minimal": "read",
        ":tmpdir": "deny",
        ":slash_tmp": "deny",
        str(artifact): "deny",
        str(home): "deny",
        str(home / "codex-home/skills/.system"): "read",
        str(workspace): "write",
        str(scratch): "write",
        str(binary): "read",
        str(python.parent.parent): "read",
        str(workspace / ".codex"): "deny",
    }

    def table(d):
        return (
            "{"
            + ",".join(f"{json.dumps(k)}={json.dumps(v)}" for k, v in d.items())
            + "}"
        )

    config = [
        f"model={json.dumps(request['model'])}",
        f"model_reasoning_effort={json.dumps(request['reasoning_effort'])}",
        'approval_policy="never"',
        f'default_permissions="{PROFILE}"',
        f"permissions.{PROFILE}.filesystem={table(filesystem)}",
        f"permissions.{PROFILE}.network.enabled=false",
        'web_search="disabled"',
        "features.apps=false",
        "features.plugins=false",
        "features.memories=false",
        f"agents.enabled={str(request.get('settings', {}).get('allow_subagents', True)).lower()}",
        "agents.max_concurrent_threads_per_session=2",
        "features.shell_snapshot=false",
        'shell_environment_policy.inherit="none"',
        f"shell_environment_policy.set={table(child_env)}",
        "allow_login_shell=false",
        'model_provider="openai"',
        "project_doc_max_bytes=65536",
    ]
    env = {
        "CODEX_HOME": str(home / "codex-home"),
        "HOME": str(home / "user-home"),
        "PATH": path,
        "LANG": "en_US.UTF-8",
        "TMPDIR": str(home / "launcher-tmp"),
    }
    for directory in ("codex-home", "user-home", "launcher-tmp"):
        (home / directory).mkdir(exist_ok=True)
    return config, env


def _config_args(config: list[str]) -> list[str]:
    return [part for setting in config for part in ("-c", setting)]


def _inspect_cli(binary: Path, env: dict, deadline: float | None = None) -> str:
    def inspect(*argv: str) -> str:
        timeout = min(15, deadline - time.monotonic()) if deadline is not None else 15
        if timeout <= 0:
            raise ValueError("Native setup exhausted the turn time budget")
        completed = subprocess.run(
            [str(binary), *argv],
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
        )
        return completed.stdout

    version = inspect("--version").strip()
    required = {
        ("exec", "--help"): (
            "--json",
            "--ignore-user-config",
            "--ignore-rules",
            "resume",
        ),
        ("exec", "resume", "--help"): ("SESSION_ID", "--json", "--ignore-user-config"),
        ("sandbox", "--help"): ("--permission-profile", "--cd"),
    }
    for argv, flags in required.items():
        help_text = inspect(*argv)
        if any(flag not in help_text for flag in flags):
            raise ValueError(f"Unsupported Codex CLI capabilities: {' '.join(argv)}")
    return version


def _preflight(
    binary: Path,
    config: list[str],
    workspace: Path,
    home: Path,
    artifact: Path,
    env: dict,
    timeout_seconds: float = 30,
) -> dict:
    """Use synthetic canaries; credentials are absent throughout this command."""
    python = Path(sys.executable).resolve(strict=True)
    canaries = [
        artifact / "controller-canary.txt",
        home / "codex-home/credential-canary.txt",
    ]
    with tempfile.NamedTemporaryFile(
        prefix=".campaign-probe-", dir=workspace, delete=False
    ) as file:
        probe = Path(file.name)
        file.write(b"synthetic read/write probe\n")
    for canary in canaries:
        canary.write_text("synthetic canary; no secrets\n")
    script = f"test -r {shlex.quote(str(probe))} || exit 10; "
    for i, canary in enumerate(canaries, 11):
        script += f"if test -r {shlex.quote(str(canary))}; then echo denied-path-readable; exit {i}; fi; "
    script += f"printf checked > {shlex.quote(str(probe))} || exit 13; "
    script += "python -c " + shlex.quote(
        f"import subprocess; subprocess.run([{json.dumps(str(python))},'-c','pass'],check=True)"
    )
    try:
        # Codex sandbox rejects --strict-config; exec validates its configuration
        # strictly before inference, after this separate isolation check.
        raw = artifact / "preflight-process"
        raw.mkdir()
        status, code, elapsed = bounded_process(
            [
                str(binary),
                "sandbox",
                *_config_args(config),
                "-C",
                str(workspace),
                "-P",
                PROFILE,
                "/bin/sh",
                "-c",
                script,
            ],
            cwd=workspace,
            env=env,
            prompt="",
            raw=raw,
            limits={"seconds": timeout_seconds, "output_bytes": 200_000},
        )
        result = {
            "status": status,
            "returncode": code,
            "elapsed_seconds": elapsed,
            "stdout": (raw / "codex.jsonl").read_text(errors="replace"),
            "stderr": (raw / "stderr.txt").read_text(errors="replace"),
        }
        _write(artifact / "preflight.json", result)
        if status != "completed" or code:
            raise ValueError(
                "Sandbox preflight failed; no credentials copied or model launched (see preflight.json)"
            )
        return result
    finally:
        probe.unlink(missing_ok=True)
        for canary in canaries:
            canary.unlink(missing_ok=True)


def _events(path: Path) -> list[dict]:
    events = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Incomplete or invalid JSON event at {path.name}:{number}"
            ) from exc
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise ValueError(f"Invalid event object at {path.name}:{number}")
        events.append(event)
    return events


def parse_execution(path: Path, expected_session: str | None = None) -> dict:
    """Require observed identity and terminal success; usage is not occupancy."""
    events = _events(path)
    ids = {
        event.get("thread_id") for event in events if event["type"] == "thread.started"
    }
    if len(ids) != 1 or not isinstance(next(iter(ids), None), str):
        raise ValueError("Trace does not identify exactly one native session")
    session_id = ids.pop()
    if expected_session is not None and session_id != expected_session:
        raise ValueError("Resumed native session ID differs from the requested session")
    if any(event["type"] in {"turn.failed", "error"} for event in events):
        raise ValueError("Native trace records a failed turn or error")
    turn_events = [
        event["type"] for event in events if event["type"].startswith("turn.")
    ]
    if not turn_events or turn_events[-1] != "turn.completed":
        raise ValueError("Native trace has no completed turn")
    messages = [
        event["item"]["text"]
        for event in events
        if event["type"] == "item.completed"
        and isinstance(event.get("item"), dict)
        and event["item"].get("type") == "agent_message"
        and isinstance(event["item"].get("text"), str)
    ]
    return {
        "session_id": session_id,
        "response": messages[-1] if messages else "",
        "same_session": expected_session == session_id
        if expected_session is not None
        else False,
    }


def _payload(event: dict) -> dict:
    value = event.get("payload")
    return value if isinstance(value, dict) else {}


def _rollout_observations(
    home: Path, artifact: Path, session_id: str, offsets: dict[str, int]
) -> tuple[dict, list[str]]:
    """Read only this isolated session's rollouts, retaining raw per-turn deltas.

    New CLI history stores may omit JSONL rollouts. Missing data stays unknown.
    Never call cumulative token usage, context-window capacity, or billed input
    tokens active context occupancy.
    """
    observed = {
        "compaction_events": None,
        "active_context_tokens": None,
        "model": None,
        "reasoning_effort": None,
    }
    traces = []
    for path in sorted((home / "codex-home/sessions").rglob("*.jsonl")):
        try:
            all_events = _events(path)
        except (OSError, ValueError):
            continue
        if not any(
            e["type"] == "session_meta" and _payload(e).get("id") == session_id
            for e in all_events
        ):
            continue
        raw = path.read_bytes()[offsets.get(str(path), 0) :]
        target = artifact / f"rollout-{len(traces) + 1}.jsonl"
        target.write_bytes(raw)
        traces.append(str(target))
        try:
            events = _events(target)
        except ValueError:
            continue
        observed["compaction_events"] = sum(
            e["type"] == "compacted"
            or (
                e["type"] == "event_msg"
                and _payload(e).get("type") == "context_compacted"
            )
            for e in events
        )
        for event in events:
            payload = _payload(event)
            if event["type"] == "turn_context":
                if isinstance(payload.get("model"), str):
                    observed["model"] = payload["model"]
                if isinstance(payload.get("effort"), str):
                    observed["reasoning_effort"] = payload["effort"]
            # This deliberately accepts only an explicitly named observation.
            value = payload.get("active_context_tokens")
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                observed["active_context_tokens"] = value
    return observed, traces


def run(request: dict) -> dict:
    result = _base_result()
    started = time.monotonic()
    artifact = home = lock = credential = None
    owns_lock = owns_artifact = False
    record: dict = {"execution": "not-started"}
    try:
        if not isinstance(request, dict) or request.get("schema") != 1:
            raise ValueError("Unsupported adapter schema")
        settings = request.get("settings", {})
        if not isinstance(settings, dict) or set(settings) - SETTINGS:
            raise ValueError("Unsupported adapter settings")
        dry = settings.get("preflight_only", False)
        if not isinstance(dry, bool) or not isinstance(
            settings.get("allow_live", False), bool
        ):
            raise ValueError("preflight_only and allow_live must be booleans")
        if not isinstance(settings.get("allow_subagents", True), bool):
            raise ValueError("allow_subagents must be a boolean")
        if not dry and not settings.get("allow_live", False):
            raise ValueError("Native generation requires settings.allow_live=true")
        for key in ("model", "reasoning_effort", "prompt"):
            if not isinstance(request.get(key), str) or (
                key != "prompt" and not request[key]
            ):
                raise ValueError(f"{key} must be a string")
        timeout = request.get("timeout_seconds", 300)
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not 1 <= timeout <= 900
        ):
            raise ValueError("timeout_seconds must be between 1 and 900")
        deadline = started + timeout
        expected = request.get("session_id")
        if expected is not None and (
            not isinstance(expected, str) or not expected or expected.startswith("-")
        ):
            raise ValueError("session_id must be null or a native session ID")
        workspace = _directory(request["workspace"], "workspace")
        artifact = _directory(request["artifact_dir"], "artifact_dir")
        home = _directory(request["session_home"], "session_home")
        paths = (workspace, artifact, home)
        if any(
            a == b or a.is_relative_to(b) for a in paths for b in paths if a is not b
        ):
            raise ValueError(
                "workspace, artifact_dir and session_home must be disjoint"
            )
        if not workspace.is_dir():
            raise ValueError("workspace does not exist")
        for parent in workspace.parents:
            if any(
                (parent / name).exists()
                for name in ("AGENTS.md", "AGENTS.override.md", ".codex/config.toml")
            ):
                raise ValueError(
                    "Consumer has ancestor instructions or config; use an independent temporary directory"
                )
        if (workspace / ".codex/config.toml").exists():
            raise ValueError(
                "Consumer Codex config can override campaign permissions; remove it from the fixture"
            )
        artifact.mkdir(parents=True, exist_ok=True)
        if any(artifact.iterdir()):
            raise ValueError("artifact_dir must be empty for each invocation")
        owns_artifact = True
        home.mkdir(parents=True, exist_ok=True, mode=0o700)
        owner = home / ".campaign-owned.json"
        if not owner.exists():
            if any(home.iterdir()):
                raise ValueError("Refusing a nonempty unowned session_home")
            _write(owner, {"schema": 1, "workspace": str(workspace)})
        elif json.loads(owner.read_text()) != {
            "schema": 1,
            "workspace": str(workspace),
        }:
            raise ValueError("session_home belongs to another consumer")
        lock = home / ".campaign-lock"
        lock.mkdir()  # Refuse simultaneous use of this logical session.
        owns_lock = True
        state_path = home / ".campaign-session.json"
        previous = json.loads(state_path.read_text()) if state_path.exists() else None
        if (expected is None and previous is not None) or (
            expected is not None
            and (previous is None or previous.get("session_id") != expected)
        ):
            raise ValueError(
                "Requested session does not match the isolated session home"
            )
        binary_name = settings.get("binary") or shutil.which("codex")
        if not binary_name:
            raise ValueError("Codex executable not found; set settings.binary")
        binary = Path(binary_name).resolve()
        config, env = _settings(request, workspace, home, artifact, binary)
        version = _inspect_cli(binary, env, deadline=deadline)
        identity = {
            "model": request["model"],
            "reasoning_effort": request["reasoning_effort"],
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "cli_version": version,
            "allow_subagents": settings.get("allow_subagents", True),
        }
        if previous and previous["identity"] != identity:
            raise ValueError(
                "Model, effort, CLI, or subagent capability changed within a resumed session"
            )
        record.update(
            identity,
            config=config,
            config_sha256=_hash(config),
            config_scope="explicit CLI overrides; managed and host defaults are not fully observed",
            host_capabilities={
                "subagents_enabled_requested": settings.get("allow_subagents", True),
                "max_concurrent_subagents_requested": 2,
                "subagents_observed": None,
                "subagent_model_calls_observed": None,
                "subagent_models_observed": None,
                "sandbox_probe_scope": "parent command only",
                "child_sandbox_inheritance": "documented; not empirically probed by this adapter",
                "model_scope": "parent fixed; children inherit unless an explicit spawn override applies",
            },
            workspace=str(workspace),
            prompt_sha256=hashlib.sha256(request["prompt"].encode()).hexdigest(),
        )
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("Native setup exhausted the turn time budget")
        _preflight(
            binary,
            config,
            workspace,
            home,
            artifact,
            env,
            timeout_seconds=min(30, remaining),
        )
        result["traces"].append(str(artifact / "preflight.json"))
        if dry:
            result["execution_status"] = "completed"
            record["execution"] = "preflight-completed"
            return result
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError(
                "Sandbox preflight exhausted the turn time budget; no model launched"
            )
        source = Path(
            settings.get("auth_file")
            or Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
        )
        if source.is_symlink() or not source.is_file():
            raise ValueError(
                "Existing regular auth.json required; adapter does not perform login"
            )
        credential = home / "codex-home/auth.json"
        shutil.copyfile(source, credential)
        credential.chmod(0o600)
        offsets = {
            str(p): p.stat().st_size
            for p in (home / "codex-home/sessions").rglob("*.jsonl")
        }
        command = [
            str(binary),
            "exec",
            "--ignore-user-config",
            "--ignore-rules",
            "--strict-config",
            *_config_args(config),
            "-C",
            str(workspace),
            "--skip-git-repo-check",
            "--json",
        ]
        if expected:
            command += ["resume", expected, "-"]
        else:
            command += ["-"]
        record["command"] = command
        (artifact / "prompt.txt").write_text(request["prompt"])
        status, code, elapsed = bounded_process(
            command,
            cwd=workspace,
            env=env,
            prompt=request["prompt"],
            raw=artifact,
            limits={
                "seconds": max(0, deadline - time.monotonic()),
                "output_bytes": 4_000_000,
            },
        )
        record.update(execution=status, returncode=code, elapsed_seconds=elapsed)
        result["traces"].extend(
            str(artifact / name) for name in ("codex.jsonl", "stderr.txt")
        )
        if status != "completed":
            result["execution_status"] = (
                "timeout" if status == "timeout" else "infrastructure-blocked"
            )
            result["error"] = f"Native process {status}, exit {code}; inspect raw trace"
            return result
        parsed = parse_execution(artifact / "codex.jsonl", expected)
        observed, rollouts = _rollout_observations(
            home, artifact, parsed["session_id"], offsets
        )
        result["observations"].update(observed, same_session=parsed["same_session"])
        result["traces"].extend(rollouts)
        for field in ("model", "reasoning_effort"):
            if observed[field] is not None and observed[field] != request[field]:
                raise ValueError(f"Observed {field} differs from the frozen request")
        result.update(
            execution_status="completed",
            session_id=parsed["session_id"],
            response=parsed["response"],
        )
        _write(state_path, {"session_id": parsed["session_id"], "identity": identity})
    except (
        KeyError,
        OSError,
        TypeError,
        ValueError,
        subprocess.SubprocessError,
    ) as exc:
        result.update(execution_status="infrastructure-blocked", error=str(exc))
    finally:
        if credential is not None:
            credential.unlink(missing_ok=True)
        if owns_lock and lock is not None:
            lock.rmdir()
        if owns_artifact and artifact is not None:
            for name in (
                "preflight.json",
                "preflight-process/codex.jsonl",
                "preflight-process/stderr.txt",
            ):
                path = str(artifact / name)
                if Path(path).is_file() and path not in result["traces"]:
                    result["traces"].append(path)
            record.update(
                result=result,
                credential_copy_removed=credential is None or not credential.exists(),
            )
            _write(artifact / "invocation.json", record)
            result["traces"].append(str(artifact / "invocation.json"))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="No credentials, no model; test a disposable consumer",
    )
    parser.add_argument("--binary")
    parser.add_argument("--artifact-dir", type=Path)
    args = parser.parse_args(argv)
    if args.preflight:
        root = Path(tempfile.mkdtemp(prefix="campaign-preflight-"))
        workspace = root / "consumer"
        workspace.mkdir()
        (workspace / "AGENTS.md").write_text("Synthetic sandbox preflight.\n")
        request = {
            "schema": 1,
            "workspace": str(workspace),
            "session_home": str(root / "session"),
            "artifact_dir": str(
                args.artifact_dir.resolve() if args.artifact_dir else root / "evidence"
            ),
            "session_id": None,
            "prompt": "",
            "model": "preflight-only",
            "reasoning_effort": "high",
            "settings": {
                "preflight_only": True,
                **({"binary": args.binary} if args.binary else {}),
            },
        }
    else:
        try:
            request = json.load(sys.stdin)
        except (ValueError, OSError) as exc:
            result = _base_result()
            result["error"] = str(exc)
            print(json.dumps(result))
            return 2
    result = run(request)
    print(json.dumps(result))
    return 0 if result["execution_status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
