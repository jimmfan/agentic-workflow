"""Freeze experiments, capture turns, and bind judgments to observed evidence.

This coordinator does not generate subject answers or infer prose correctness.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
import difflib
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shlex
import shutil
import stat
import subprocess
import tempfile
import time
import zipfile

from evals.persistence import bounded_process, snapshot
from evals.token_forensics.parsers.codex import parse_codex_trace
from evals.campaign.revisions import prepare_revision, snapshot_files, verify_files
from evals.campaign.schema import (
    VERDICTS,
    identifier,
    load_spec,
    read_json,
    validate_response,
)


ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK_ROOTS = (".agent-workflow", ".agents", ".claude", ".codex", ".opencode")
FRAMEWORK_FILES = {"AGENTS.md", "CLAUDE.md"}


def fingerprint(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
            handle.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def _framework(path: str) -> bool:
    return path in FRAMEWORK_FILES or any(
        path == root or path.startswith(root + "/") for root in FRAMEWORK_ROOTS
    )


def _artifact_root(path: Path) -> Path:
    # Resolve existing ancestors too: a symlink must not redirect artifacts into source.
    path = path.resolve()
    if path == ROOT or ROOT.is_relative_to(path):
        raise ValueError("Campaign output cannot contain the authoring checkout")
    if path.is_relative_to(ROOT):
        raise ValueError(
            "Keep campaign output outside the authoring checkout to avoid ancestor policy contamination"
        )
    return path


def _copy_fixture(source: Path, destination: Path) -> None:
    for path in source.rglob("*"):
        name = path.relative_to(source).as_posix()
        if (
            path.is_symlink()
            or name == ".git"
            or name.startswith(".git/")
            or _framework(name)
        ):
            raise ValueError(
                f"Fixture contains a policy, Git metadata, or symlink: {name}"
            )
        if not path.is_file() and not path.is_dir():
            raise ValueError(f"Unsupported fixture entry: {name}")
    shutil.copytree(source, destination)


def _tooling() -> dict:
    paths = [
        *Path(__file__).parent.glob("*.py"),
        ROOT / "evals/persistence.py",
        ROOT / "tests/behavior.py",
    ]
    paths += list((ROOT / "evals/token_forensics").rglob("*.py"))
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(paths)
    }


def freeze_campaign(spec_path: Path, destination: Path, *, repo: Path = ROOT) -> dict:
    """Prepare immutable treatments and inputs without calling a model."""
    spec, scenarios = load_spec(spec_path)
    destination = _artifact_root(destination)
    if destination.exists():
        raise ValueError(
            "Use a new campaign directory; an existing run is never overwritten"
        )
    for _, fixture in scenarios:
        if destination.is_relative_to(fixture) or fixture.is_relative_to(destination):
            raise ValueError("Campaign output and source fixture overlap")
    destination.mkdir(parents=True)
    try:
        (destination / "payloads").mkdir()
        conditions = {}
        for condition in spec["conditions"]:
            key = condition["id"]
            conditions[key] = prepare_revision(
                repo,
                condition["ref"],
                destination / "payloads" / key,
                overlays=condition.get("overlays", []),
            )
        frozen_scenarios = {}
        for scenario, fixture in scenarios:
            key = scenario["id"]
            target = destination / "inputs" / key
            target.mkdir(parents=True)
            _copy_fixture(fixture, target / "fixture")
            dump(target / "scenario.json", scenario)
            frozen_scenarios[key] = scenario
        schedule = []
        rng = random.Random(spec["seed"])
        for repetition in range(1, spec["repetitions"] + 1):
            for scenario in frozen_scenarios:
                order = list(conditions)
                rng.shuffle(order)
                for condition in order:
                    schedule.append(
                        {
                            "id": f"run-{len(schedule) + 1:04d}",
                            "scenario": scenario,
                            "condition": condition,
                            "repetition": repetition,
                        }
                    )
        manifest = {
            "schema": 1,
            "created_at": time.time(),
            "spec": spec,
            "conditions": conditions,
            "scenarios": frozen_scenarios,
            "schedule": schedule,
            "tooling": _tooling(),
            "inputs": snapshot_files(destination / "inputs"),
            "expected_turns": sum(
                len(frozen_scenarios[row["scenario"]]["turns"]) for row in schedule
            ),
        }
        dump(destination / "manifest.json", manifest)
        dump(destination / "seal.json", {"manifest_sha256": fingerprint(manifest)})
        dump(
            destination / "state.json",
            {
                "started_at": None,
                "launched_turns": 0,
                "runs": {
                    row["id"]: {
                        "next": 0,
                        "pending": None,
                        "sessions": {},
                        "status": "ready",
                    }
                    for row in schedule
                },
            },
        )
        return manifest
    except BaseException as exc:
        dump(
            destination / "preparation-error.json",
            {
                "execution_status": "infrastructure-blocked",
                "error": str(exc),
                "behavioral_verdict": "INCONCLUSIVE",
            },
        )
        raise


def verify_campaign(campaign: Path, *, tooling=True) -> dict:
    manifest = read_json(campaign / "manifest.json")
    if read_json(campaign / "seal.json").get("manifest_sha256") != fingerprint(
        manifest
    ):
        raise ValueError("Frozen campaign manifest changed")
    verify_files(campaign / "inputs", manifest["inputs"])
    for key, metadata in manifest["conditions"].items():
        verify_files(campaign / "payloads" / key, metadata["files"])
    if tooling and manifest["tooling"] != _tooling():
        raise ValueError(
            "Campaign tooling changed; finish with the frozen tooling or create a new campaign"
        )
    return manifest


@contextmanager
def _lock(campaign: Path):
    lock = campaign / ".campaign-lock"
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError(
            "Campaign is locked by another operation; inspect before recovering a stale lock"
        ) from exc
    try:
        os.write(descriptor, str(os.getpid()).encode())
        os.close(descriptor)
        yield
    finally:
        lock.unlink(missing_ok=True)


def _row(manifest: dict, run_id: str) -> dict:
    identifier(run_id, "run id")
    for row in manifest["schedule"]:
        if row["id"] == run_id:
            return row
    raise ValueError(f"Unknown run: {run_id}")


def _capture(workspace: Path, directory: Path, name: str) -> dict:
    entries = {key: asdict(value) for key, value in snapshot(workspace).items()}
    git = {key: asdict(value) for key, value in snapshot(workspace / ".git").items()}
    files = {}
    total = 0
    with zipfile.ZipFile(
        directory / f"{name}.zip", "w", zipfile.ZIP_DEFLATED
    ) as archive:
        for key, entry in entries.items():
            if entry["kind"] != "file":
                continue
            path = workspace / key
            if not path.resolve().is_relative_to(workspace.resolve()):
                raise ValueError(f"Snapshot file escapes workspace: {key}")
            content = path.read_bytes()
            total += len(content)
            if total > 50_000_000:
                raise ValueError("Snapshot exceeds the 50 MB evidence bound")
            archive.writestr(key, content)
            if not _framework(key):
                files[key] = content.decode("utf-8", errors="replace")
    git_root = workspace / ".git"
    data = {
        "entries": entries,
        "git": git,
        "files": files,
        "root_mode": stat.S_IMODE(workspace.lstat().st_mode),
        "git_root_mode": stat.S_IMODE(git_root.lstat().st_mode)
        if git_root.exists()
        else None,
    }
    dump(directory / f"{name}.json", data)
    return data


def _initialize_consumer_git(workspace: Path) -> None:
    """Give implementation subjects an ordinary, local-only comparison baseline."""
    env = {
        **{
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GIT_")
        },
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
        "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
    }
    command = [
        "git",
        "-c",
        "init.templateDir=",
        "-c",
        f"core.hooksPath={os.devnull}",
        "-c",
        "user.name=Campaign fixture",
        "-c",
        "user.email=campaign@example.invalid",
    ]
    for arguments in (
        ["init", "-q", "-b", "eval-consumer"],
        ["add", "--all"],
        [
            "-c",
            "commit.gpgSign=false",
            "commit",
            "-q",
            "-m",
            "Frozen evaluation fixture",
        ],
    ):
        result = subprocess.run(
            [*command, *arguments],
            cwd=workspace,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode:
            raise ValueError(f"Disposable Git baseline failed: {result.stderr.strip()}")


def begin_turn(campaign: Path, run_id: str) -> dict:
    """Record an attempt before exposing one public request to a subject."""
    campaign = campaign.resolve()
    with _lock(campaign):
        manifest = verify_campaign(campaign)
        row = _row(manifest, run_id)
        state = read_json(campaign / "state.json")
        run = state["runs"][run_id]
        if run["pending"] is not None:
            raise ValueError(
                "An attempt is already pending; record its outcome instead of retrying"
            )
        turns = manifest["scenarios"][row["scenario"]]["turns"]
        if run["status"] != "ready" or run["next"] >= len(turns):
            raise ValueError(
                "Run is complete or stopped; create a new run for another attempt"
            )
        now = time.time()
        limits = manifest["spec"]["limits"]
        if (
            state["started_at"] is not None
            and now - state["started_at"] >= limits["campaign_seconds"]
        ):
            raise ValueError("Campaign time budget exhausted")
        if state["launched_turns"] >= limits["max_turns"]:
            raise ValueError("Campaign turn budget exhausted")
        run["pending"] = {"index": run["next"], "started_at": now, "phase": "preparing"}
        state["started_at"] = state["started_at"] or now
        state["launched_turns"] += 1
        dump(campaign / "state.json", state)
        try:
            workspace = campaign / "workspaces" / run_id
            if run["next"] == 0:
                if workspace.exists():
                    raise ValueError(
                        "Unexpected existing consumer; do not reuse another run"
                    )
                shutil.copytree(
                    campaign / "payloads" / row["condition"], workspace, symlinks=True
                )
                shutil.copytree(
                    campaign / "inputs" / row["scenario"] / "fixture",
                    workspace,
                    dirs_exist_ok=True,
                )
                _initialize_consumer_git(workspace)
            elif not workspace.is_dir():
                raise ValueError("Consumer workspace is missing")
            directory = campaign / "runs" / run_id / f"{run['next'] + 1:03d}"
            directory.mkdir(parents=True, exist_ok=False)
            before = _capture(workspace, directory, "before")
            if run["next"]:
                previous = read_json(
                    directory.parent / f"{run['next']:03d}" / "after.json"
                )
                if before != previous:
                    raise ValueError("Consumer changed between recorded turns")
            turn = turns[run["next"]]
            home = campaign / "sessions" / run_id / turn["session"]
            home.mkdir(parents=True, exist_ok=True)
            raw = directory / "raw"
            raw.mkdir()
            host = manifest["spec"]["host"]
            request = {
                "schema": 1,
                "workspace": str(workspace),
                "artifact_dir": str(raw),
                "session_home": str(home),
                "session_id": run["sessions"].get(turn["session"]),
                "prompt": turn["request"],
                "model": host["model"],
                "reasoning_effort": host["reasoning_effort"],
                "timeout_seconds": min(
                    limits["turn_seconds"],
                    int(
                        limits["campaign_seconds"]
                        - (now - (state["started_at"] or now))
                    ),
                ),
                "settings": host.get("settings", {}),
            }
            dump(directory / "request.json", request)
        except BaseException as exc:
            run["status"] = "stopped"
            run["pending"] = None
            run["preparation_error"] = str(exc)
            run["failed_attempt"] = {
                "index": run["next"],
                "execution_status": "infrastructure-blocked",
                "error": str(exc),
            }
            dump(campaign / "state.json", state)
            raise
        run["pending"] = {
            "index": run["next"],
            "started_at": now,
            "phase": "subject",
            "inputs_sha256": {
                name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                for name in ("request.json", "before.json", "before.zip")
            },
        }
        dump(campaign / "state.json", state)
        return request


def _changes(before: dict, after: dict) -> list[str]:
    return sorted(
        key for key in before.keys() | after.keys() if before.get(key) != after.get(key)
    )


def _allowed(path: str, patterns: list[str], *, directory=False) -> bool:
    return any(
        fnmatch.fnmatchcase(path, pattern)
        or (directory and pattern.startswith(path + "/"))
        for pattern in patterns
    )


def _trace_evidence(response: dict, directory: Path) -> dict:
    """Normalize only retained native event records; subject claims are not events."""
    observed = {
        "commands": [],
        "command_outputs": [],
        "compactions": [],
        "thread_ids": [],
        "usage": [],
        "warnings": [],
        "sources": [],
    }
    for index, value in enumerate(response.get("traces", [])):
        path = Path(value)
        if not path.is_absolute() or path.is_symlink() or not path.is_file():
            raise ValueError("Trace must name an existing regular absolute file")
        # An adapter writes its owned traces under this turn's raw directory.
        if not path.resolve().is_relative_to((directory / "raw").resolve()):
            raise ValueError("Trace is outside the attempt's raw evidence directory")
        trace = parse_codex_trace(path)
        observed["sources"].append(
            {
                "path": path.relative_to(directory).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
        observed["commands"].extend(
            asdict(tool)
            for tool in trace.tool_invocations
            if tool.tool_type == "command_execution"
        )
        observed["compactions"].extend(asdict(event) for event in trace.compactions)
        observed["usage"].extend(asdict(item) for item in trace.usage_observations)
        if trace.thread_id:
            observed["thread_ids"].append(trace.thread_id)
        observed["warnings"].extend(trace.parse_warnings)
        # Token forensics retains byte counts, while semantic review also needs
        # the public result text. Do not copy private reasoning or other events.
        for line_number, line in enumerate(
            path.read_text(errors="replace").splitlines(), 1
        ):
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict) or event.get("type") != "item.completed":
                continue
            item = event.get("item", {})
            if not isinstance(item, dict) or item.get("type") != "command_execution":
                continue
            observed["command_outputs"].append(
                {
                    "source": path.relative_to(directory).as_posix(),
                    "line": line_number,
                    "command": item.get("command"),
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status"),
                    "output": {
                        key: item[key]
                        for key in ("aggregated_output", "stdout", "stderr", "output")
                        if key in item
                    },
                }
            )
    # Dataclass observations can contain tuples; checkpoints round-trip JSON.
    return json.loads(json.dumps(observed))


def _command_executes(command: str | None, target: str) -> bool:
    """Recognize a literal executable or Python script, not an argument mention.

    Native command strings are shell syntax, not an argv array. Only a simple
    invocation (optionally wrapped by a shell -c/-lc) establishes this check;
    compound commands, expansion, and unknown launcher modes remain unproven.
    """
    if not isinstance(command, str):
        return False

    def simple_argv(value: str) -> list[str]:
        if any(character in value for character in "\r\n\0`$;&|<>(){}*?[#"):
            return []
        try:
            return shlex.split(value)
        except ValueError:
            return []

    argv = simple_argv(command)
    if not argv:
        return False
    if Path(argv[0]).name in {"sh", "bash", "zsh", "dash"}:
        if len(argv) != 3 or argv[1] not in {"-c", "-lc"}:
            return False
        argv = simple_argv(argv[2])
        if not argv:
            return False
    executable = argv[0]
    if re.fullmatch(r"python(?:3(?:\.\d+)?)?", Path(executable).name):
        arguments = iter(argv[1:])
        for argument in arguments:
            if argument == "--":
                executable = next(arguments, "")
                break
            if re.fullmatch(r"-[bBdEIOPqsSu]+", argument):
                continue
            if argument.startswith("-"):
                return False
            executable = argument
            break
        else:
            return False
    # Strip only harmless leading ./ segments, not trailing slashes or internal
    # path components whose meaning may depend on symlinks. Keep .// relative.
    while executable.startswith("./") and not executable.startswith(".//"):
        executable = executable[2:]
    while target.startswith("./") and not target.startswith(".//"):
        target = target[2:]
    return bool(executable) and executable == target


def _checks(
    turn: dict,
    before: dict,
    after: dict,
    response: dict,
    traces: dict,
    *,
    protected: set[str],
) -> list[dict]:
    changes = _changes(before["entries"], after["entries"])
    if before.get("root_mode") != after.get("root_mode"):
        changes.insert(0, ".")
    git_unchanged = before["git"] == after["git"] and before.get(
        "git_root_mode"
    ) == after.get("git_root_mode")
    forbidden = [
        path
        for path in changes
        if path == "."
        or _framework(path)
        or path in protected
        or not _allowed(
            path,
            turn["allowed_writes"],
            directory=path not in before["entries"]
            and after["entries"][path]["kind"] == "directory",
        )
    ]
    unsafe_links = [
        path
        for path in changes
        if after["entries"].get(path, {}).get("kind") == "symlink"
    ]
    checks = [
        {
            "id": "boundary-writes",
            "kind": "mechanical",
            "verdict": "FAIL" if forbidden or unsafe_links else "PASS",
            "detail": {
                "unauthorized_paths": forbidden,
                "new_or_changed_symlinks": unsafe_links,
            },
        }
    ]
    if not turn["allowed_writes"]:
        checks.append(
            {
                "id": "boundary-git",
                "kind": "mechanical",
                "verdict": "PASS" if git_unchanged else "FAIL",
                "detail": "No net Git metadata changes",
            }
        )
    complete = response["execution_status"] == "completed"
    for check in turn["checks"]:
        kind = check["kind"]
        passed = None
        detail = (
            "Requires independent semantic review"
            if kind == "semantic"
            else "Required observation unavailable"
        )
        path = check.get("path")
        if kind == "unchanged":
            passed = not changes and git_unchanged
            detail = {"changed_paths": changes}
        elif kind == "path_exists":
            passed = after["entries"].get(path, {}).get("kind") == "file"
            detail = {
                "path": path,
                "observed_kind": after["entries"].get(path, {}).get("kind"),
            }
        elif kind == "path_absent":
            passed = path not in after["entries"]
            detail = {"path": path, "present": path in after["entries"]}
        elif kind == "file_equals":
            passed = (
                after["entries"].get(path, {}).get("kind") == "file"
                and after["files"].get(path) == check["value"]
            )
            detail = {"path": path, "matches_expected_text": passed}
        elif kind == "command_observed":
            commands = [
                c
                for c in traces["commands"]
                if _command_executes(c.get("command"), check["argv_contains"])
                and c.get("status") == "completed"
                and c.get("exit_code") is not None
            ]
            passed = True if commands else None
            detail = commands or detail
        elif kind == "compaction_observed":
            passed = True if traces["compactions"] else None
            detail = traces["compactions"] or detail
        elif kind == "context_observed":
            # Token usage counters are not active context occupancy.
            detail = "Active context occupancy is not established by token usage or staged bytes"
        if not complete and kind not in {"unchanged", "path_absent"}:
            passed = None
        verdict = "INCONCLUSIVE" if passed is None else "PASS" if passed else "FAIL"
        checks.append({**check, "verdict": verdict, "detail": detail})
    return checks


def finish_turn(campaign: Path, run_id: str, response: dict) -> dict:
    campaign = campaign.resolve()
    validate_response(response)
    with _lock(campaign):
        manifest = verify_campaign(campaign)
        row = _row(manifest, run_id)
        state = read_json(campaign / "state.json")
        run = state["runs"][run_id]
        pending = run["pending"]
        if pending is None:
            raise ValueError("No pending turn to complete")
        if pending.get("phase") != "subject":
            raise ValueError(
                "Preparation was interrupted; recover the recorded attempt"
            )
        index = pending["index"]
        turn = manifest["scenarios"][row["scenario"]]["turns"][index]
        directory = campaign / "runs" / run_id / f"{index + 1:03d}"
        for name, digest in pending["inputs_sha256"].items():
            if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
                raise ValueError("Pending attempt inputs changed after launch")
        request = read_json(directory / "request.json")
        before = read_json(directory / "before.json")
        after = _capture(campaign / "workspaces" / run_id, directory, "after")
        dump(directory / "response.json", response)
        traces = _trace_evidence(response, directory)
        continuity = "fresh" if request["session_id"] is None else "resumed"
        session = response.get("session_id")
        reused_fresh_session = (
            request["session_id"] is None
            and session
            and any(
                session in prior["sessions"].values()
                for prior in state["runs"].values()
            )
        )
        mismatched_trace = bool(traces["thread_ids"]) and set(traces["thread_ids"]) != {
            session
        }
        if response["execution_status"] == "completed" and (
            not session
            or (request["session_id"] is not None and session != request["session_id"])
            or reused_fresh_session
            or mismatched_trace
        ):
            response = {
                **response,
                "execution_status": "error",
                "error": "Missing or changed subject session identity",
            }
            dump(directory / "response.json", response)
        checks = _checks(
            turn,
            before,
            after,
            response,
            traces,
            protected=set(manifest["conditions"][row["condition"]]["files"]),
        )
        checkpoint = {
            "schema": 1,
            "run_id": run_id,
            "turn_id": turn["id"],
            "turn_index": index,
            "execution_status": response["execution_status"],
            "continuation": continuity,
            "elapsed_seconds": time.time() - pending["started_at"],
            "checks": checks,
            "observed": traces,
            "adapter_observations": response.get("observations", {}),
            "evidence_sha256": {
                file: hashlib.sha256((directory / file).read_bytes()).hexdigest()
                for file in (
                    "request.json",
                    "response.json",
                    "before.json",
                    "after.json",
                    "before.zip",
                    "after.zip",
                )
            },
        }
        dump(directory / "checkpoint.json", checkpoint)
        run["pending"] = None
        run["next"] += 1
        if session:
            run["sessions"][turn["session"]] = session
        if response["execution_status"] != "completed":
            run["status"] = "stopped"
        elif run["next"] == len(manifest["scenarios"][row["scenario"]]["turns"]):
            run["status"] = "completed"
        dump(campaign / "state.json", state)
        return checkpoint


def recover_turn(campaign: Path, run_id: str, reason: str) -> dict:
    """Finalize an interrupted attempt without launching or retrying a subject.

    The operator must first stop any subject still running outside this process.
    """
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("Recovery needs the observed interruption reason")
    with _lock(campaign):
        manifest = verify_campaign(campaign)
        row = _row(manifest, run_id)
        state = read_json(campaign / "state.json")
        run = state["runs"][run_id]
        pending = run["pending"]
        if not pending:
            raise ValueError("No interrupted attempt is pending")
        index = pending["index"]
        directory = campaign / "runs" / run_id / f"{index + 1:03d}"
        if (directory / "checkpoint.json").exists():
            checkpoint = _verified_checkpoint(directory, manifest, row, index)
            response = read_json(directory / "response.json")
            turn = manifest["scenarios"][row["scenario"]]["turns"][index]
            run["next"] = index + 1
            run["pending"] = None
            if response.get("session_id"):
                run["sessions"][turn["session"]] = response["session_id"]
            run["status"] = (
                "stopped"
                if checkpoint["execution_status"] != "completed"
                else "completed"
                if run["next"] == len(manifest["scenarios"][row["scenario"]]["turns"])
                else "ready"
            )
            run["recovery"] = reason
            dump(campaign / "state.json", state)
            return run
        if pending.get("phase") == "preparing":
            run.update(status="stopped", pending=None, preparation_error=reason)
            run["failed_attempt"] = {
                "index": index,
                "execution_status": "infrastructure-blocked",
                "error": reason,
            }
            dump(campaign / "state.json", state)
            return run
        prior_session = read_json(directory / "request.json")["session_id"]
        response_path = directory / "response.json"
        retained_response = (
            read_json(response_path)
            if response_path.exists()
            else {
                "schema": 1,
                "execution_status": "error",
                "session_id": prior_session,
                "response": "",
                "error": reason,
            }
        )
    try:
        return finish_turn(campaign, run_id, retained_response)
    except (ValueError, OSError) as exc:
        # Retain the consumer and partial evidence when observation itself is
        # impossible. Recovery must not rerun the subject or erase its effects.
        with _lock(campaign):
            verify_campaign(campaign)
            state = read_json(campaign / "state.json")
            run = state["runs"][run_id]
            if (directory / "checkpoint.json").exists():
                raise
            run.update(status="stopped", pending=None)
            run["failed_attempt"] = {
                "index": index,
                "execution_status": "error",
                "error": f"{reason}; evidence capture unavailable: {exc}",
            }
            dump(campaign / "state.json", state)
            return run


def run_campaign(campaign: Path, *, allow_live=False, run_id=None) -> dict:
    """Run the frozen command adapter sequentially, with no automatic retry."""
    manifest = verify_campaign(campaign)
    host = manifest["spec"]["host"]
    if host["kind"] != "command" or not allow_live:
        raise ValueError(
            "Command execution requires a command host and explicit --allow-live"
        )
    if run_id is not None:
        _row(manifest, run_id)
    for row in manifest["schedule"]:
        if run_id and row["id"] != run_id:
            continue
        while True:
            state = read_json(campaign / "state.json")["runs"][row["id"]]
            if state["status"] != "ready":
                break
            if state["pending"] is not None:
                raise ValueError(
                    "Interrupted attempt remains pending; record it before resuming"
                )
            request = begin_turn(campaign, row["id"])
            request["settings"] = {**request["settings"], "allow_live": True}
            raw = Path(request["artifact_dir"])
            transport = raw.parent / "adapter-process"
            transport.mkdir()
            try:
                status, code, _ = bounded_process(
                    host["command"],
                    cwd=ROOT,
                    env=os.environ.copy(),
                    prompt=json.dumps(request),
                    raw=transport,
                    limits={
                        "seconds": request["timeout_seconds"] + 10,
                        "output_bytes": 10_000_000,
                    },
                )
                if (
                    status in {"completed", "infrastructure-blocked"}
                    and (transport / "codex.jsonl").stat().st_size
                ):
                    response = json.loads((transport / "codex.jsonl").read_text())
                    validate_response(response)
                    if code and response["execution_status"] == "completed":
                        raise ValueError(
                            "Adapter claimed completion but returned a failing exit code"
                        )
                else:
                    response = {
                        "schema": 1,
                        "execution_status": "timeout"
                        if status == "timeout"
                        else "infrastructure-blocked",
                        "session_id": request["session_id"],
                        "response": "",
                        "error": f"Adapter process {status}, exit {code}",
                    }
            except (OSError, ValueError) as exc:
                response = {
                    "schema": 1,
                    "execution_status": "error",
                    "session_id": request["session_id"],
                    "response": "",
                    "error": str(exc),
                }
            finish_turn(campaign, row["id"], response)
            if response["execution_status"] != "completed":
                return report_campaign(campaign)
    return report_campaign(campaign)


def _verified_checkpoint(
    directory: Path, manifest: dict, row: dict, index: int
) -> dict:
    checkpoint = read_json(directory / "checkpoint.json")
    turn = manifest["scenarios"][row["scenario"]]["turns"][index]
    if (
        checkpoint.get("run_id"),
        checkpoint.get("turn_id"),
        checkpoint.get("turn_index"),
    ) != (row["id"], turn["id"], index):
        raise ValueError("Checkpoint identity does not match frozen schedule")
    required = {
        "request.json",
        "response.json",
        "before.json",
        "after.json",
        "before.zip",
        "after.zip",
    }
    if set(checkpoint["evidence_sha256"]) != required:
        raise ValueError("Checkpoint lacks the required evidence hashes")
    for path, expected in checkpoint["evidence_sha256"].items():
        if hashlib.sha256((directory / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Recorded turn evidence changed: {directory.name}/{path}")
    for trace in checkpoint["observed"]["sources"]:
        if (
            hashlib.sha256((directory / trace["path"]).read_bytes()).hexdigest()
            != trace["sha256"]
        ):
            raise ValueError("Recorded trace changed")
    request = read_json(directory / "request.json")
    if request["prompt"] != turn["request"]:
        raise ValueError("Recorded request differs from frozen public request")
    before, after = (
        read_json(directory / f"{name}.json") for name in ("before", "after")
    )
    response = validate_response(read_json(directory / "response.json"))
    traces = _trace_evidence(response, directory)
    checks = _checks(
        turn,
        before,
        after,
        response,
        traces,
        protected=set(manifest["conditions"][row["condition"]]["files"]),
    )
    if (
        checkpoint["checks"] != checks
        or checkpoint["observed"] != traces
        or checkpoint["execution_status"] != response["execution_status"]
    ):
        raise ValueError("Checkpoint judgments differ from recorded evidence")
    return checkpoint


def grading_packet(campaign: Path) -> dict:
    """Hide condition labels; generated content can still reveal the treatment."""
    manifest = verify_campaign(campaign)
    packets = []
    for row in manifest["schedule"]:
        for index, turn in enumerate(manifest["scenarios"][row["scenario"]]["turns"]):
            directory = campaign / "runs" / row["id"] / f"{index + 1:03d}"
            if not (directory / "checkpoint.json").exists():
                continue
            checkpoint = _verified_checkpoint(directory, manifest, row, index)
            before, after = (
                read_json(directory / f"{name}.json") for name in ("before", "after")
            )
            response = read_json(directory / "response.json")
            diff = "\n".join(
                line
                for path in sorted(before["files"].keys() | after["files"].keys())
                for line in difflib.unified_diff(
                    before["files"].get(path, "").splitlines(),
                    after["files"].get(path, "").splitlines(),
                    fromfile=path,
                    tofile=path,
                    lineterm="",
                )
            )
            packets.append(
                {
                    "id": f"{row['id']}/{turn['id']}",
                    "request": turn["request"],
                    "execution_status": checkpoint["execution_status"],
                    "checks": checkpoint["checks"],
                    "evidence": {
                        **after["files"],
                        "@response": response["response"],
                        "@requests": "\n\n".join(
                            t["request"]
                            for t in manifest["scenarios"][row["scenario"]]["turns"][
                                : index + 1
                            ]
                        ),
                        "@diff": diff,
                        "@inventory": "\n".join(after["files"]),
                        "@observations": json.dumps(
                            checkpoint["observed"], sort_keys=True
                        ),
                    },
                    "limits": "Snapshots establish net file effects, not absence of transient actions; label blinding cannot conceal all treatment cues.",
                }
            )
    return {
        "schema": 1,
        "purpose": "Judge each semantic requirement from cited evidence; do not infer a preferred condition",
        "items": packets,
    }


def _validate_review(packet: dict, review: dict) -> None:
    digest = fingerprint(packet)
    if review.get("packet_sha256") != digest:
        raise ValueError("Review does not match the current evidence packet")
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        raise ValueError("Review must identify its reviewer and context")
    expected = {item["id"]: item for item in packet["items"]}
    judgments = review.get("items")
    if not isinstance(judgments, list):
        raise ValueError("Review items must be a list")
    seen = set()
    for judgment in judgments:
        key = judgment.get("id")
        if key not in expected or key in seen:
            raise ValueError("Unknown or duplicate review item")
        seen.add(key)
        item = expected[key]
        semantic = {c["id"] for c in item["checks"] if c["kind"] == "semantic"}
        checks = judgment.get("checks", {})
        if not isinstance(checks, dict) or set(checks) - semantic:
            raise ValueError("Review can judge only declared semantic checks")
        definitions = {c["id"]: c for c in item["checks"]}
        for check_id, check in checks.items():
            if (
                check.get("verdict") not in VERDICTS
                or not check.get("rationale")
                or not check.get("evidence")
            ):
                raise ValueError(
                    "Judgments need a verdict, rationale, and evidence citations"
                )
            for cite in check["evidence"]:
                quote = cite.get("quote")
                if (
                    not isinstance(quote, str)
                    or not quote
                    or quote not in item["evidence"].get(cite.get("path"), "")
                ):
                    raise ValueError(
                        "Review citation is absent from the evidence packet"
                    )
            if (
                definitions[check_id].get("evidence_scope") == "saved"
                and check["verdict"] == "PASS"
                and not any(
                    not cite["path"].startswith("@") for cite in check["evidence"]
                )
            ):
                raise ValueError(
                    "Saved-state PASS requires citation of a saved project artifact"
                )
            if (
                definitions[check_id].get("evidence_scope") == "response"
                and check["verdict"] == "PASS"
                and not any(cite["path"] == "@response" for cite in check["evidence"])
            ):
                raise ValueError(
                    "Response PASS requires citation of the subject response"
                )


def apply_review(campaign: Path, review: dict) -> dict:
    packet = grading_packet(campaign)
    _validate_review(packet, review)
    digest = fingerprint(packet)
    target = campaign / "reviews" / f"{digest}.json"
    if target.exists():
        raise ValueError(
            "A review for this packet already exists; retain it rather than overwrite"
        )
    dump(target, review)
    return report_campaign(campaign)


def _verdict(checks: list[dict]) -> str:
    values = [check["verdict"] for check in checks]
    if "FAIL" in values:
        return "FAIL"
    if not values or "INCONCLUSIVE" in values:
        return "INCONCLUSIVE"
    return "PASS"


def report_campaign(campaign: Path) -> dict:
    manifest = verify_campaign(campaign)
    packet = grading_packet(campaign)
    review_path = campaign / "reviews" / f"{fingerprint(packet)}.json"
    reviews = {}
    if review_path.exists():
        saved_review = read_json(review_path)
        _validate_review(packet, saved_review)
        reviews = {row["id"]: row.get("checks", {}) for row in saved_review["items"]}
    rows = []
    applicability_totals = {}
    behavior_totals = {}
    state = read_json(campaign / "state.json")
    totals = {
        key: {
            "PASS": 0,
            "FAIL": 0,
            "INCONCLUSIVE": 0,
            "unexecuted": 0,
            "execution_failures": 0,
        }
        for key in manifest["conditions"]
    }
    for row in manifest["schedule"]:
        for index, turn in enumerate(manifest["scenarios"][row["scenario"]]["turns"]):
            applicability = manifest["scenarios"][row["scenario"]]["applicability"]
            directory = campaign / "runs" / row["id"] / f"{index + 1:03d}"
            receipt = {}
            if not (directory / "checkpoint.json").exists():
                run_state = state["runs"][row["id"]]
                failed = run_state.get("failed_attempt", {})
                status = (
                    failed["execution_status"]
                    if failed.get("index") == index
                    else "pending"
                    if run_state["pending"] and run_state["pending"]["index"] == index
                    else "unexecuted"
                )
                checks = [
                    {
                        **check,
                        "verdict": "INCONCLUSIVE",
                        "detail": "No completed checkpoint",
                    }
                    for check in turn["checks"]
                ]
                verdict = "INCONCLUSIVE"
                if status == "unexecuted":
                    totals[row["condition"]]["unexecuted"] += 1
                elif status in {"error", "infrastructure-blocked"}:
                    totals[row["condition"]]["execution_failures"] += 1
            else:
                checkpoint = _verified_checkpoint(directory, manifest, row, index)
                status = checkpoint["execution_status"]
                receipt = {
                    "elapsed_seconds": checkpoint["elapsed_seconds"],
                    "continuation": checkpoint["continuation"],
                    "adapter_observations": checkpoint["adapter_observations"],
                    "command_count": len(checkpoint["observed"]["commands"]),
                    "usage_observations": checkpoint["observed"]["usage"],
                }
                judgments = reviews.get(f"{row['id']}/{turn['id']}", {})
                checks = []
                for check in checkpoint["checks"]:
                    if (
                        check["kind"] == "semantic"
                        and check["id"] in judgments
                        and status == "completed"
                    ):
                        check = {
                            **check,
                            "verdict": judgments[check["id"]]["verdict"],
                            "detail": "Cited semantic judgment attached",
                            "review": judgments[check["id"]],
                        }
                    checks.append(check)
                verdict = _verdict(checks)
                if status != "completed":
                    totals[row["condition"]]["execution_failures"] += 1
                    if verdict != "FAIL":
                        verdict = "INCONCLUSIVE"
            totals[row["condition"]][verdict] += 1
            counts = applicability_totals.setdefault(applicability, {}).setdefault(
                row["condition"], {"PASS": 0, "FAIL": 0, "INCONCLUSIVE": 0}
            )
            counts[verdict] += 1
            for check in checks:
                counts = behavior_totals.setdefault(
                    f"{applicability}/{row['scenario']}/{check['id']}", {}
                ).setdefault(
                    row["condition"], {"PASS": 0, "FAIL": 0, "INCONCLUSIVE": 0}
                )
                counts[check["verdict"]] += 1
            rows.append(
                {
                    **row,
                    "applicability": applicability,
                    "turn": turn["id"],
                    "execution_status": status,
                    "verdict": verdict,
                    "checks": checks,
                    "receipt": receipt,
                }
            )
    return {
        "schema": 1,
        "campaign": manifest["spec"]["name"],
        "question": manifest["spec"]["question"],
        "manifest_sha256": fingerprint(manifest),
        "packet_sha256": fingerprint(packet),
        "conditions": {
            key: {
                k: metadata[k]
                for k in ("commit", "version", "layout", "warnings", "overlays")
            }
            for key, metadata in manifest["conditions"].items()
        },
        "expected_turns": manifest["expected_turns"],
        "host": manifest["spec"]["host"],
        "verdict": _verdict(rows),
        "totals": totals,
        "by_applicability": applicability_totals,
        "by_behavior": behavior_totals,
        "rows": rows,
        "limits": [
            "Turn counts are descriptive; turns in a conversation are correlated, not independent samples.",
            "Missing execution, observations, or required review remain INCONCLUSIVE.",
            "Common outcomes and current-contract conformance must be interpreted separately.",
            "Whole-version comparisons do not identify which individual instruction caused a difference.",
            "A hybrid is an experimental treatment, not a released framework version.",
            "No single combined score or automatic rollback recommendation is produced.",
        ],
    }


def render_report(report: dict) -> str:
    lines = [
        f"# {report['campaign']}",
        "",
        report["question"],
        "",
        f"Frozen manifest: `{report['manifest_sha256']}`",
        "",
        "| Applicability | Condition | Commit | PASS turns | FAIL turns | INCONCLUSIVE turns |",
        "|---|---|---|---:|---:|---:|",
    ]
    for applicability, conditions in report["by_applicability"].items():
        for name, total in conditions.items():
            lines.append(
                f"| {applicability} | {name} | {report['conditions'][name]['commit'][:12]} | {total['PASS']} | {total['FAIL']} | {total['INCONCLUSIVE']} |"
            )
    lines.extend(
        [
            "",
            "| Run | Scenario | Repetition | Condition | Turn | Execution | Verdict |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for row in report["rows"]:
        lines.append(
            f"| {row['id']} | {row['scenario']} | {row['repetition']} | {row['condition']} | {row['turn']} | {row['execution_status']} | {row['verdict']} |"
        )
    lines.extend(["", *[f"- {limit}" for limit in report["limits"]], ""])
    return "\n".join(lines)
