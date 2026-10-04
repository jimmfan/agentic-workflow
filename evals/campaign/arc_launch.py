"""User-operated native handoff for the recovered ARC v2 comparison."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import signal
import subprocess
import time
from pathlib import Path
import shutil
import sys

from evals.campaign import core, codex

ARC = core.ROOT / "evals/arc-state-complexity-v2"


def prepare(destination: Path, binary: Path, cutoff: str | None = None) -> dict:
    destination = destination.resolve()
    binary = binary.resolve(strict=True)
    spec = json.loads((ARC / "campaign.json").read_text())
    if cutoff is not None:
        spec["limits"]["launch_before_utc"] = cutoff
    else:
        spec["limits"].pop("launch_before_utc", None)
    spec["host"]["command"][0] = str(Path(sys.executable).resolve(strict=True))
    spec["host"]["settings"]["binary"] = str(binary)
    spec["scenarios"] = [str(ARC / "scenario.json")]
    source = destination.parent / (destination.name + ".spec.json")
    if source.exists():
        raise ValueError("Prepared spec already exists")
    core.dump(source, spec)
    manifest = core.freeze_campaign(source, destination)
    core.dump(
        destination / "preparation.json",
        {
            "manifest_sha256": core.fingerprint(manifest),
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "python": str(Path(sys.executable).resolve(strict=True)),
            "expected_subject_calls": 12,
            "same_inputs": "One frozen scenario and fixture shared by both conditions",
            "requested_fast_mode": spec["host"]["settings"]["fast_mode"],
            "service_tier_override": "fast"
            if spec["host"]["settings"]["fast_mode"]
            else None,
            "service_tier_observation": "Actual response tier remains unverified until execution metadata is available",
        },
    )
    return manifest


def verify_launch_identity(destination: Path, manifest: dict) -> None:
    prepared = core.read_json(destination / "preparation.json")
    binary = Path(manifest["spec"]["host"]["settings"]["binary"])
    if hashlib.sha256(binary.read_bytes()).hexdigest() != prepared["binary_sha256"]:
        raise ValueError("Native binary changed after preparation")
    if str(Path(sys.executable).resolve(strict=True)) != prepared["python"]:
        raise ValueError("Use the canonical Python recorded at preparation")


def preflight(destination: Path) -> dict:
    manifest = core.verify_campaign(destination)
    verify_launch_identity(destination, manifest)
    results = {}
    for row in manifest["schedule"]:
        key = row["condition"]
        base = destination / "native-preflight" / key
        if base.exists():
            raise ValueError("Preflight already attempted; retain it")
        workspace = base / "consumer"
        shutil.copytree(destination / "payloads" / key, workspace)
        fixture = destination / "inputs" / row["scenario"] / "fixture"
        shutil.copytree(fixture, workspace, dirs_exist_ok=True)
        host = manifest["spec"]["host"]
        results[key] = codex.run(
            {
                "schema": 1,
                "workspace": str(workspace),
                "artifact_dir": str(base / "raw"),
                "session_home": str(base / "session"),
                "session_id": None,
                "prompt": "",
                "model": host["model"],
                "reasoning_effort": host["reasoning_effort"],
                "timeout_seconds": 30,
                "settings": {**host["settings"], "preflight_only": True},
            }
        )
    result = {
        "manifest_sha256": core.fingerprint(manifest),
        "results": results,
        "passed": all(r["execution_status"] == "completed" for r in results.values()),
    }
    core.dump(destination / "native-preflight-result.json", result)
    return result


def stop_owned_processes(process) -> None:
    """Stop only the controller's descendants, including separate sessions."""
    rows = (
        subprocess.check_output(["/bin/ps", "-axo", "pid=,ppid="], timeout=5)
        .decode()
        .splitlines()
    )
    parents = {int(pid): int(parent) for pid, parent in (row.split() for row in rows)}
    owned = {process.pid}
    while True:
        children = {pid for pid, parent in parents.items() if parent in owned}
        if children <= owned:
            break
        owned |= children
    for pid in owned:
        try:
            os.kill(pid, signal.SIGSTOP)
        except ProcessLookupError:
            pass
    for pid in owned:
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def cleanup_owned_credentials(destination: Path, manifest: dict) -> list[str]:
    removed = []
    for row in manifest["schedule"]:
        workspace = destination / "workspaces" / row["id"]
        for turn in manifest["scenarios"][row["scenario"]]["turns"]:
            home = destination / "sessions" / row["id"] / turn["session"]
            owner = home / ".campaign-owned.json"
            if owner.is_file() and core.read_json(owner) == {
                "schema": 1,
                "workspace": str(workspace),
            }:
                credential = home / "codex-home/auth.json"
                credential.unlink(missing_ok=True)
                removed.append(str(credential.relative_to(destination)))
    return removed


def emit_progress(
    destination: Path,
    manifest: dict,
    elapsed: float,
    previous: dict | None = None,
    *,
    heartbeat: bool = False,
    controller_active: bool = True,
) -> dict:
    """Read nonsecret controller state; never project progress into subject inputs."""
    try:
        state = core.read_json(destination / "state.json")
    except (OSError, ValueError):
        if heartbeat or previous is None:
            print(
                f"[{int(elapsed) // 60:02d}:{int(elapsed) % 60:02d}] Controller starting; waiting for saved state",
                flush=True,
            )
        return previous or {}
    runs = state.get("runs", {})
    changed = runs != previous
    if changed:
        for row in manifest["schedule"]:
            run = runs.get(row["id"], {})
            old = (previous or {}).get(row["id"], {})
            for index in range(old.get("next", 0), run.get("next", 0)):
                checkpoint = (
                    destination
                    / "runs"
                    / row["id"]
                    / f"{index + 1:03d}"
                    / "checkpoint.json"
                )
                try:
                    status = core.read_json(checkpoint)["execution_status"]
                except (OSError, ValueError, KeyError):
                    status = "recorded"
                print(
                    f"[{int(elapsed) // 60:02d}:{int(elapsed) % 60:02d}] END {row['condition']} P{index + 1}: execution {status}; semantic grading pending",
                    flush=True,
                )
            pending = run.get("pending")
            old_pending = old.get("pending")
            if pending and (
                not old_pending
                or pending.get("index") != old_pending.get("index")
                or pending.get("phase") != old_pending.get("phase")
            ):
                print(
                    f"[{int(elapsed) // 60:02d}:{int(elapsed) % 60:02d}] START {row['condition']} P{pending['index'] + 1}: {pending.get('phase', 'preparing')}; fresh session",
                    flush=True,
                )
    if changed or heartbeat:
        completed = sum(run.get("next", 0) for run in runs.values())
        active = [
            f"{row['condition']} P{runs[row['id']]['pending']['index'] + 1}"
            for row in manifest["schedule"]
            if runs.get(row["id"], {}).get("pending")
        ]
        print(
            f"[{int(elapsed) // 60:02d}:{int(elapsed) % 60:02d}] Controller {'active' if controller_active else 'stopped'}; completed {completed}/{manifest['expected_turns']}; launched {state.get('launched_turns', 0)}; saved phase: {', '.join(active) or 'between phases'}",
            flush=True,
        )
    return runs


def run_supervised(destination: Path, manifest: dict) -> dict:
    """Bound the full controller and clean its own temporary credential copies."""
    output = destination / "controller-run"
    output.mkdir()
    command = [
        str(Path(sys.executable).resolve(strict=True)),
        "-B",
        "-m",
        "evals.campaign",
        "run",
        str(destination),
        "--allow-live",
    ]
    env = {
        key: value
        for key, value in os.environ.items()
        if key in {"PATH", "HOME", "LANG", "TMPDIR", "CODEX_HOME"}
    }
    env.update(
        PYTHONDONTWRITEBYTECODE="1",
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
    )
    process = None
    interrupted = timed_out = False
    started = time.monotonic()
    print(
        f"Starting ARC comparison: {manifest['expected_turns']} fresh phases; {manifest['spec']['limits']['campaign_seconds']}s campaign budget; no retries",
        flush=True,
    )
    print(f"Logs: {output}; phase artifacts: {destination / 'runs'}", flush=True)
    previous_progress = None
    last_heartbeat = -30.0
    previous_term = signal.getsignal(signal.SIGTERM)

    def terminate(*_):
        raise KeyboardInterrupt("Supervisor termination requested")

    signal.signal(signal.SIGTERM, terminate)
    cleanup_error = None
    try:
        with (
            (output / "stdout.json").open("wb") as stdout,
            (output / "stderr.txt").open("wb") as stderr,
        ):
            process = subprocess.Popen(
                command,
                cwd=core.ROOT,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            try:
                while True:
                    elapsed = time.monotonic() - started
                    remaining = manifest["spec"]["limits"]["campaign_seconds"] - elapsed
                    if remaining <= 0:
                        timed_out = True
                        break
                    heartbeat = elapsed - last_heartbeat >= 30
                    previous_progress = emit_progress(
                        destination,
                        manifest,
                        elapsed,
                        previous_progress,
                        heartbeat=heartbeat,
                    )
                    if heartbeat:
                        last_heartbeat = elapsed
                    try:
                        process.wait(timeout=min(1, remaining))
                        break
                    except subprocess.TimeoutExpired:
                        continue
            except KeyboardInterrupt:
                interrupted = True
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        try:
            if process is not None:
                if process.poll() is None:
                    stop_owned_processes(process)
                process.wait(timeout=10)
        except (OSError, subprocess.SubprocessError) as exc:
            cleanup_error = str(exc)
        removed = cleanup_owned_credentials(destination, manifest)
        audit = {
            "controller_exit_code": process.returncode if process else None,
            "timed_out": timed_out,
            "interrupted": interrupted,
            "elapsed_seconds": time.monotonic() - started,
            "owned_credential_paths_cleaned": removed,
            "retry_allowed": False,
            "process_cleanup_error": cleanup_error,
        }
        core.dump(output / "launch-result.json", audit)
        emit_progress(
            destination,
            manifest,
            audit["elapsed_seconds"],
            previous_progress,
            heartbeat=True,
            controller_active=False,
        )
        outcome = (
            "interrupted"
            if interrupted
            else "timed out"
            if timed_out
            else "stopped with cleanup error"
            if cleanup_error
            else f"controller exited {audit['controller_exit_code']}"
        )
        print(
            f"ARC {outcome}; elapsed {audit['elapsed_seconds']:.1f}s; retained result: {output / 'launch-result.json'}; no retry",
            flush=True,
        )
    if timed_out or interrupted or cleanup_error:
        result = {
            "verdict": "INCONCLUSIVE",
            "execution_status": "timeout" if timed_out else "error",
            "outer_supervisor": audit,
        }
    else:
        try:
            result = json.loads((output / "stdout.json").read_text())
        except (ValueError, OSError):
            result = {
                "verdict": "INCONCLUSIVE",
                "execution_status": "infrastructure-blocked",
                "outer_supervisor": audit,
            }
    core.dump(destination / "launch-report.json", result)
    return result


def run_once(destination: Path) -> dict:
    state = core.read_json(destination / "state.json")
    if (
        state["launched_turns"]
        or any(r["pending"] for r in state["runs"].values())
        or (destination / ".user-launch-claimed").exists()
    ):
        raise ValueError(
            "Campaign already used; evidence preserved; prepare a new explicitly authorized attempt"
        )
    manifest = core.verify_campaign(destination)
    verify_launch_identity(destination, manifest)
    pre = core.read_json(destination / "native-preflight-result.json")
    if not pre["passed"] or pre["manifest_sha256"] != core.fingerprint(manifest):
        raise ValueError("Matching native preflight must pass before live launch")
    cutoff = manifest["spec"]["limits"].get("launch_before_utc")
    if cutoff is not None and datetime.now(timezone.utc) >= datetime.fromisoformat(
        cutoff
    ):
        raise ValueError("Launch window ended; obtain a new launch handoff")
    state = core.read_json(destination / "state.json")
    if state["launched_turns"] or any(r["pending"] for r in state["runs"].values()):
        raise ValueError("Campaign already used; no retry")
    with (destination / ".user-launch-claimed").open("x") as claim:
        claim.write(datetime.now(timezone.utc).isoformat() + "\n")
    return run_supervised(destination, manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "preflight", "run"))
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--launch-before")
    args = parser.parse_args()
    try:
        if args.action == "prepare":
            if args.binary is None:
                parser.error("prepare needs --binary")
            result = prepare(args.out, args.binary, args.launch_before)
            print(
                json.dumps(
                    {
                        "manifest_sha256": core.fingerprint(result),
                        "expected_turns": result["expected_turns"],
                    }
                )
            )
            return 0
        if args.action == "preflight":
            result = preflight(args.out.resolve())
            print(json.dumps(result, indent=2))
            return 0 if result["passed"] else 2
        result = run_once(args.out.resolve())
        print(json.dumps(result, indent=2))
        return 0 if result.get("verdict") == "PASS" else 2
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
