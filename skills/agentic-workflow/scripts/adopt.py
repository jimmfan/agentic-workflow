#!/usr/bin/env python3
"""Reconcile the small local Agentic Workflow payload with a project."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
from typing import Iterable, Mapping, MutableMapping, Sequence


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PAYLOAD_ROOT = PACKAGE_ROOT / "payload"
DISTRIBUTION_MANIFEST = PAYLOAD_ROOT / "distribution" / "manifest.json"
FRAMEWORK_ROOT = PurePosixPath(".agent-workflow")
DURABLE_ROOT = PurePosixPath(".agent-workflow-state")
INSTALL_MANIFEST = FRAMEWORK_ROOT / "install-manifest.json"
COMPOSITE_PATHS = {PurePosixPath("AGENTS.md"), PurePosixPath("CLAUDE.md")}
MANAGED_BEGIN = b"<!-- agent-workflow:managed-begin -->\n"
MANAGED_END = b"<!-- agent-workflow:managed-end -->\n"
PROJECT_BEGIN = b"\n<!-- agent-workflow:project-instructions -->\n"
MINIMUM_PYTHON = (3, 11)
DISTRIBUTION_SCHEMA = 6
INSTALL_SCHEMA = 1
LOCAL_REVISION = "unreleased-local-package"
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}")


class AdoptionError(RuntimeError):
    """A safe, user-actionable lifecycle failure."""


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except (AttributeError, OSError, ValueError):
                pass


def require_supported_python() -> None:
    if sys.version_info < MINIMUM_PYTHON:
        raise AdoptionError("Agentic Workflow requires Python 3.11 or newer")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise AdoptionError(f"unsafe relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise AdoptionError(f"unsafe relative path: {value!r}")
    return path


def validate_revision(value: str) -> str:
    if value != LOCAL_REVISION and REVISION_PATTERN.fullmatch(value) is None:
        raise AdoptionError("source revision must be a 40-character lowercase Git commit or unreleased-local-package")
    return value


def validate_root(raw: Path) -> Path:
    if not raw.exists() or raw.is_symlink() or not raw.is_dir():
        raise AdoptionError(f"target must be an existing regular directory: {raw}")
    root = raw.resolve()
    if root.parent == root:
        raise AdoptionError("refusing to use a filesystem root as the project target")
    return root


def checked_target(root: Path, relative: PurePosixPath) -> Path:
    path = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise AdoptionError(f"unsafe symlink in target path: {current}")
        if current.exists() and not current.is_dir():
            raise AdoptionError(f"target parent is not a directory: {current}")
    return path


def read_regular(root: Path, relative: PurePosixPath) -> bytes | None:
    path = checked_target(root, relative)
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or not path.is_file():
        raise AdoptionError(f"target must be a regular non-symlink file: {relative}")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise AdoptionError(f"cannot read target {relative}: {exc}") from exc


def load_json(path: Path, label: str) -> MutableMapping[str, object]:
    if path.is_symlink() or not path.is_file():
        raise AdoptionError(f"{label} must be a regular non-symlink file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AdoptionError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise AdoptionError(f"{label} must contain a JSON object")
    return value


def load_distribution() -> tuple[str, list[tuple[PurePosixPath, PurePosixPath]]]:
    raw = load_json(DISTRIBUTION_MANIFEST, "distribution manifest")
    if raw.get("schema_version") != DISTRIBUTION_SCHEMA:
        raise AdoptionError("unsupported distribution manifest schema")
    version = raw.get("framework_version")
    mappings = raw.get("framework_owned")
    if not isinstance(version, str) or re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        raise AdoptionError("distribution manifest has an invalid framework_version")
    if not isinstance(mappings, list):
        raise AdoptionError("distribution manifest needs a framework_owned array")

    result: list[tuple[PurePosixPath, PurePosixPath]] = []
    for item in mappings:
        if not isinstance(item, dict) or set(item) != {"source", "target"}:
            raise AdoptionError("distribution mappings require only source and target")
        source = safe_relative(item["source"])
        target = safe_relative(item["target"])
        if target == INSTALL_MANIFEST or target == DURABLE_ROOT or DURABLE_ROOT in target.parents:
            raise AdoptionError(f"distribution must not own lifecycle state: {target}")
        source_path = PAYLOAD_ROOT.joinpath(*source.parts)
        if source_path.is_symlink() or not source_path.is_file():
            raise AdoptionError(f"required current payload source is missing or unsafe: {source}")
        result.append((source, target))

    sources = [source for source, _target in result]
    targets = [target for _source, target in result]
    if len(sources) != len(set(sources)) or len(targets) != len(set(targets)):
        raise AdoptionError("distribution mappings must have unique sources and targets")
    return version, result


def empty_install_state() -> dict[str, object]:
    return {"external_files": {}, "composites": {}}


def load_install_state(root: Path) -> dict[str, object]:
    """Load useful local evidence; missing/malformed framework metadata is disposable."""
    data = read_regular(root, INSTALL_MANIFEST)
    if data is None:
        return empty_install_state()
    try:
        raw = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return empty_install_state()
    if not isinstance(raw, dict):
        return empty_install_state()

    if raw.get("schema_version") == INSTALL_SCHEMA:
        external_raw = raw.get("external_files", {})
        composite_raw = raw.get("composites", {})
        if not isinstance(external_raw, dict) or not isinstance(composite_raw, dict):
            return empty_install_state()
        external: dict[str, dict[str, object]] = {}
        composites: dict[str, dict[str, object]] = {}
        try:
            for key, details in external_raw.items():
                relative = safe_relative(key)
                if relative == DURABLE_ROOT or DURABLE_ROOT in relative.parents:
                    raise AdoptionError("install state must not own durable state")
                if not isinstance(details, dict):
                    raise AdoptionError("invalid external state")
                created = details.get("created")
                checksum = details.get("sha256")
                if not isinstance(created, bool) or not isinstance(checksum, str) or SHA256_PATTERN.fullmatch(checksum) is None:
                    raise AdoptionError("invalid external state")
                external[relative.as_posix()] = {"created": created, "sha256": checksum}
            for key, details in composite_raw.items():
                relative = safe_relative(key)
                if relative not in COMPOSITE_PATHS or not isinstance(details, dict) or not isinstance(details.get("created"), bool):
                    raise AdoptionError("invalid composite state")
                composites[relative.as_posix()] = {"created": details["created"]}
        except AdoptionError:
            return empty_install_state()
        return {"external_files": external, "composites": composites}
    return empty_install_state()


def compose_policy(managed: bytes, project: bytes) -> bytes:
    managed_body = managed.rstrip(b"\n") + b"\n"
    return MANAGED_BEGIN + managed_body + MANAGED_END + PROJECT_BEGIN + project


def has_any_marker(data: bytes) -> bool:
    return any(marker in data for marker in (MANAGED_BEGIN, MANAGED_END, PROJECT_BEGIN))


def parse_policy(data: bytes) -> tuple[bytes, bytes]:
    if data.count(MANAGED_BEGIN) != 1 or data.count(MANAGED_END) != 1 or data.count(PROJECT_BEGIN) != 1:
        raise AdoptionError("managed policy markers are missing, duplicated, or ambiguous")
    if not data.startswith(MANAGED_BEGIN):
        raise AdoptionError("managed policy must start with its managed marker")
    managed_end = data.find(MANAGED_END, len(MANAGED_BEGIN))
    project_begin = data.find(PROJECT_BEGIN, managed_end + len(MANAGED_END))
    if managed_end < 0 or project_begin != managed_end + len(MANAGED_END):
        raise AdoptionError("managed policy markers are out of order")
    managed = data[len(MANAGED_BEGIN):managed_end]
    project = data[project_begin + len(PROJECT_BEGIN):]
    return managed, project


def source_bytes(source: PurePosixPath) -> bytes:
    try:
        return PAYLOAD_ROOT.joinpath(*source.parts).read_bytes()
    except OSError as exc:
        raise AdoptionError(f"cannot read current payload source {source}: {exc}") from exc


def ensure_parent(path: Path, root: Path, created: list[Path]) -> None:
    missing: list[Path] = []
    current = path.parent
    while current != root and not current.exists() and not current.is_symlink():
        missing.append(current)
        current = current.parent
    if current.is_symlink() or (current.exists() and not current.is_dir()):
        raise AdoptionError(f"unsafe parent for target write: {current}")
    for directory in reversed(missing):
        directory.mkdir(mode=0o755)
        created.append(directory)


def atomic_write(path: Path, data: bytes, mode: int, root: Path, created: list[Path]) -> None:
    ensure_parent(path, root, created)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def apply_external_transaction(
    root: Path,
    writes: Mapping[PurePosixPath, bytes],
    removals: Sequence[PurePosixPath],
) -> tuple[dict[PurePosixPath, tuple[bytes, int] | None], list[Path]]:
    affected = sorted(set(writes) | set(removals), key=lambda item: item.as_posix())
    snapshots: dict[PurePosixPath, tuple[bytes, int] | None] = {}
    for relative in affected:
        current = read_regular(root, relative)
        if current is None:
            snapshots[relative] = None
        else:
            mode = stat.S_IMODE(checked_target(root, relative).stat().st_mode)
            snapshots[relative] = (current, mode)

    created_directories: list[Path] = []
    try:
        for relative in removals:
            path = checked_target(root, relative)
            if path.exists() or path.is_symlink():
                if path.is_symlink() or not path.is_file():
                    raise AdoptionError(f"refusing to remove non-file external target: {relative}")
                path.unlink()
        for relative, data in writes.items():
            prior = snapshots[relative]
            mode = prior[1] if prior is not None else 0o644
            atomic_write(checked_target(root, relative), data, mode, root, created_directories)
    except Exception:
        rollback_external(root, snapshots, created_directories)
        raise
    return snapshots, created_directories


def rollback_external(
    root: Path,
    snapshots: Mapping[PurePosixPath, tuple[bytes, int] | None],
    created_directories: Sequence[Path],
) -> None:
    for relative, snapshot in reversed(list(snapshots.items())):
        path = checked_target(root, relative)
        try:
            if snapshot is None:
                if path.exists() and path.is_file() and not path.is_symlink():
                    path.unlink()
            else:
                atomic_write(path, snapshot[0], snapshot[1], root, [])
        except OSError:
            pass
    for directory in reversed(created_directories):
        try:
            directory.rmdir()
        except OSError:
            pass


def ensure_durable_state(root: Path) -> bool:
    canonical = checked_target(root, DURABLE_ROOT)
    if not canonical.exists():
        canonical.mkdir(mode=0o755)
        return True
    if canonical.is_symlink() or not canonical.is_dir():
        raise AdoptionError(".agent-workflow-state must be a regular non-symlink directory")
    return False


def rollback_created_durable_state(root: Path, created: bool) -> None:
    if created:
        try:
            checked_target(root, DURABLE_ROOT).rmdir()
        except OSError:
            pass


def install_manifest_bytes(
    version: str,
    revision: str,
    external: Mapping[str, Mapping[str, object]],
    composites: Mapping[str, Mapping[str, object]],
) -> bytes:
    value = {
        "schema_version": INSTALL_SCHEMA,
        "framework_version": version,
        "source_revision": revision,
        "external_files": dict(sorted(external.items())),
        "composites": dict(sorted(composites.items())),
    }
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def make_framework_stage(
    root: Path,
    mappings: Sequence[tuple[PurePosixPath, PurePosixPath]],
    manifest: bytes,
) -> Path:
    stage = Path(tempfile.mkdtemp(prefix=".agent-workflow-stage-", dir=root))
    try:
        for source, target in mappings:
            if target != FRAMEWORK_ROOT and FRAMEWORK_ROOT in target.parents:
                relative = target.relative_to(FRAMEWORK_ROOT)
                destination = stage.joinpath(*relative.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source_bytes(source))
                os.chmod(destination, 0o644)
        (stage / INSTALL_MANIFEST.name).write_bytes(manifest)
        os.chmod(stage / INSTALL_MANIFEST.name, 0o644)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return stage


def swap_framework(root: Path, stage: Path) -> Path | None:
    current = checked_target(root, FRAMEWORK_ROOT)
    if current.is_symlink() or (current.exists() and not current.is_dir()):
        raise AdoptionError(".agent-workflow must be a regular non-symlink directory")
    backup: Path | None = None
    if current.exists():
        backup = Path(tempfile.mkdtemp(prefix=".agent-workflow-backup-", dir=root))
        backup.rmdir()
        os.replace(current, backup)
    try:
        os.replace(stage, current)
    except Exception:
        if backup is not None and backup.exists():
            os.replace(backup, current)
        raise
    return backup


def restore_framework(root: Path, backup: Path | None) -> None:
    current = checked_target(root, FRAMEWORK_ROOT)
    if current.exists() and current.is_dir() and not current.is_symlink():
        shutil.rmtree(current)
    if backup is not None and backup.exists():
        os.replace(backup, current)


def plan_reconciliation(
    root: Path,
    mappings: Sequence[tuple[PurePosixPath, PurePosixPath]],
    state: Mapping[str, object],
) -> tuple[
    dict[PurePosixPath, bytes],
    list[PurePosixPath],
    dict[str, dict[str, object]],
    dict[str, dict[str, object]],
    list[str],
]:
    previous_external = state["external_files"]
    previous_composites = state["composites"]
    assert isinstance(previous_external, dict)
    assert isinstance(previous_composites, dict)

    writes: dict[PurePosixPath, bytes] = {}
    removals: list[PurePosixPath] = []
    next_external: dict[str, dict[str, object]] = {}
    next_composites: dict[str, dict[str, object]] = {}
    actions: list[str] = []

    desired_external: set[str] = set()
    for source, target in mappings:
        if target == FRAMEWORK_ROOT or FRAMEWORK_ROOT in target.parents:
            continue
        data = source_bytes(source)
        key = target.as_posix()
        current = read_regular(root, target)
        if target in COMPOSITE_PATHS:
            previous = previous_composites.get(key)
            if current is None:
                project = b""
                created = True
            elif has_any_marker(current):
                _managed, project = parse_policy(current)
                created = bool(previous.get("created")) if isinstance(previous, dict) else False
            else:
                project = current
                created = False
            desired = compose_policy(data, project)
            if current != desired:
                writes[target] = desired
                actions.append(f"replace managed policy region in {target}")
            next_composites[key] = {"created": created}
            continue

        desired_external.add(key)
        previous = previous_external.get(key)
        if current is None:
            writes[target] = data
            created = True
            actions.append(f"create required external integration {target}")
        elif isinstance(previous, dict):
            created = bool(previous.get("created"))
            if current != data:
                writes[target] = data
                actions.append(f"replace managed external integration {target}")
        elif current == data:
            created = False
            actions.append(f"reuse exact pre-existing external integration {target}")
        else:
            raise AdoptionError(
                f"unknown external content blocks required framework target: {target}"
            )
        next_external[key] = {"created": created, "sha256": digest(data)}

    for key, details in previous_external.items():
        if key in desired_external or not isinstance(details, dict):
            continue
        relative = safe_relative(key)
        current = read_regular(root, relative)
        if current is None:
            continue
        if details.get("created") is True and digest(current) == details.get("sha256"):
            removals.append(relative)
            actions.append(f"remove retired unchanged external integration {relative}")
        else:
            actions.append(f"preserve retired external content without safe deletion proof {relative}")

    return writes, removals, next_external, next_composites, actions


def verify_reconciled(
    root: Path,
    mappings: Sequence[tuple[PurePosixPath, PurePosixPath]],
) -> None:
    for source, target in mappings:
        expected = source_bytes(source)
        current = read_regular(root, target)
        if target in COMPOSITE_PATHS:
            if current is None:
                raise AdoptionError(f"post-check missing composite policy: {target}")
            managed, _project = parse_policy(current)
            if managed != expected.rstrip(b"\n") + b"\n":
                raise AdoptionError(f"post-check found stale managed policy: {target}")
        elif current != expected:
            raise AdoptionError(f"post-check found stale framework target: {target}")


def reconcile(root: Path, dry_run: bool, revision: str, verb: str) -> None:
    version, mappings = load_distribution()
    state = load_install_state(root)
    writes, removals, external, composites, actions = plan_reconciliation(root, mappings, state)
    actions.append("replace reconstructable .agent-workflow with current desired files")
    if not checked_target(root, DURABLE_ROOT).exists():
        actions.append("create empty durable project-state directory .agent-workflow-state")

    if dry_run:
        print(f"{verb.upper()} PLAN {root}")
        for action in actions:
            print(f"- {action}")
        return

    manifest = install_manifest_bytes(version, revision, external, composites)
    stage = make_framework_stage(root, mappings, manifest)
    durable_created = False
    snapshots: dict[PurePosixPath, tuple[bytes, int] | None] = {}
    created_directories: list[Path] = []
    backup: Path | None = None
    framework_swapped = False
    try:
        durable_created = ensure_durable_state(root)
        snapshots, created_directories = apply_external_transaction(root, writes, removals)
        backup = swap_framework(root, stage)
        framework_swapped = True
        verify_reconciled(root, mappings)
    except Exception:
        if framework_swapped:
            try:
                restore_framework(root, backup)
            except OSError:
                pass
        rollback_external(root, snapshots, created_directories)
        rollback_created_durable_state(root, durable_created)
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
        raise
    if backup is not None:
        shutil.rmtree(backup, ignore_errors=True)
    print(f"OK: Agentic Workflow {verb} completed; current framework state reconciled.")
    print("OK: Durable project state preserved under .agent-workflow-state/.")


def status(root: Path) -> int:
    version, mappings = load_distribution()
    state = load_install_state(root)
    previous_external = state["external_files"]
    assert isinstance(previous_external, dict)
    problems: list[str] = []
    conflicts: list[str] = []

    framework = checked_target(root, FRAMEWORK_ROOT)
    if not framework.exists():
        problems.append("REPAIR: reconstructable .agent-workflow directory is absent")
    elif framework.is_symlink() or not framework.is_dir():
        conflicts.append("CONFLICT: .agent-workflow is not a regular directory")

    desired_internal: set[str] = {INSTALL_MANIFEST.as_posix()}
    for source, target in mappings:
        expected = source_bytes(source)
        if target == FRAMEWORK_ROOT or FRAMEWORK_ROOT in target.parents:
            desired_internal.add(target.as_posix())
        try:
            current = read_regular(root, target)
        except AdoptionError as exc:
            conflicts.append(f"CONFLICT: {exc}")
            continue
        if target in COMPOSITE_PATHS:
            if current is None:
                problems.append(f"REPAIR: missing composite policy {target}")
            elif has_any_marker(current):
                try:
                    managed, _project = parse_policy(current)
                except AdoptionError as exc:
                    conflicts.append(f"CONFLICT: malformed composite {target}: {exc}")
                else:
                    if managed != expected.rstrip(b"\n") + b"\n":
                        problems.append(f"REPAIR: stale managed policy region {target}")
            else:
                problems.append(f"REPAIR: unmarked project policy can be safely composed at {target}")
        elif current is None:
            problems.append(f"REPAIR: missing framework target {target}")
        elif current != expected:
            if target == FRAMEWORK_ROOT or FRAMEWORK_ROOT in target.parents or target.as_posix() in previous_external:
                problems.append(f"REPAIR: drifted managed framework target {target}")
            else:
                conflicts.append(f"CONFLICT: unknown external content at {target}")

    manifest_data = read_regular(root, INSTALL_MANIFEST)
    if manifest_data is None:
        problems.append("REPAIR: reconstructable install metadata is absent")
    else:
        try:
            manifest_raw = json.loads(manifest_data.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            manifest_raw = None
        if not isinstance(manifest_raw, dict) or manifest_raw.get("schema_version") != INSTALL_SCHEMA:
            problems.append("REPAIR: reconstructable install metadata is stale or malformed")
        elif manifest_raw.get("framework_version") != version:
            problems.append("REPAIR: installed framework version differs from current package")

    if framework.exists() and framework.is_dir() and not framework.is_symlink():
        for path in framework.rglob("*"):
            if path.is_file() and not path.is_symlink():
                relative = path.relative_to(root).as_posix()
                if relative not in desired_internal:
                    problems.append(f"REPAIR: obsolete reconstructable framework file {relative}")

    durable = checked_target(root, DURABLE_ROOT)
    if not durable.exists():
        problems.append("REPAIR: durable project-state directory is absent")
    elif durable.is_symlink() or not durable.is_dir():
        conflicts.append("CONFLICT: .agent-workflow-state is not a regular directory")

    print(f"STATUS {root}")
    print(f"Current package version: {version}")
    for message in problems + conflicts:
        print(message)
    if conflicts:
        print("Agentic Workflow: unsafe/conflict")
        return 2
    if problems:
        print("Agentic Workflow: repairable")
        return 1
    print("Agentic Workflow: healthy")
    print("OK: No lifecycle action is required.")
    return 0


def remove(root: Path, dry_run: bool) -> None:
    _version, mappings = load_distribution()
    state = load_install_state(root)
    external_state = state["external_files"]
    composite_state = state["composites"]
    assert isinstance(external_state, dict)
    assert isinstance(composite_state, dict)
    writes: dict[PurePosixPath, bytes] = {}
    removals: list[PurePosixPath] = []
    actions: list[str] = []

    composite_targets = {target for _source, target in mappings if target in COMPOSITE_PATHS}
    composite_targets |= {safe_relative(key) for key in composite_state}
    for relative in sorted(composite_targets, key=lambda item: item.as_posix()):
        current = read_regular(root, relative)
        if current is None or not has_any_marker(current):
            continue
        _managed, project = parse_policy(current)
        details = composite_state.get(relative.as_posix())
        created = isinstance(details, dict) and details.get("created") is True
        if created and not project:
            removals.append(relative)
            actions.append(f"remove framework-created composite policy {relative}")
        else:
            writes[relative] = project
            actions.append(f"remove managed policy region and preserve project bytes in {relative}")

    for key, details in external_state.items():
        if not isinstance(details, dict):
            continue
        relative = safe_relative(key)
        current = read_regular(root, relative)
        if current is None:
            continue
        if details.get("created") is True and digest(current) == details.get("sha256"):
            removals.append(relative)
            actions.append(f"remove unchanged framework-created external integration {relative}")
        else:
            actions.append(f"preserve pre-existing or changed external content {relative}")

    framework = checked_target(root, FRAMEWORK_ROOT)
    if framework.exists() or framework.is_symlink():
        if framework.is_symlink() or not framework.is_dir():
            raise AdoptionError(".agent-workflow must be a regular non-symlink directory")
        actions.append("remove reconstructable .agent-workflow directory")
    actions.append("preserve .agent-workflow-state and every file below it")

    if dry_run:
        print(f"REMOVE PLAN {root}")
        for action in actions:
            print(f"- {action}")
        return

    snapshots: dict[PurePosixPath, tuple[bytes, int] | None] = {}
    created_directories: list[Path] = []
    backup: Path | None = None
    try:
        snapshots, created_directories = apply_external_transaction(root, writes, removals)
        if framework.exists():
            backup = Path(tempfile.mkdtemp(prefix=".agent-workflow-remove-", dir=root))
            backup.rmdir()
            os.replace(framework, backup)
    except Exception:
        if backup is not None and backup.exists():
            os.replace(backup, framework)
        rollback_external(root, snapshots, created_directories)
        raise
    if backup is not None:
        shutil.rmtree(backup, ignore_errors=True)
    print("OK: Reconstructable Agentic Workflow files removed.")
    print("OK: Durable project state and uncertain external content preserved.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install", "update", "status", "remove"))
    parser.add_argument("target", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source-revision", default=LOCAL_REVISION)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    configure_console()
    try:
        require_supported_python()
        args = build_parser().parse_args(argv)
        root = validate_root(args.target)
        revision = validate_revision(args.source_revision)
        if args.command == "status":
            if args.dry_run:
                raise AdoptionError("status does not accept --dry-run")
            return status(root)
        if args.command == "remove":
            remove(root, args.dry_run)
        else:
            reconcile(root, args.dry_run, revision, args.command)
        return 0
    except AdoptionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: filesystem operation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
