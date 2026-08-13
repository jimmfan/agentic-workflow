#!/usr/bin/env python3
"""Safely install, update, inspect, or remove the packaged workflow payload."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = PACKAGE_ROOT / "payload"
SOURCE_MANIFEST = SOURCE_ROOT / "distribution" / "manifest.json"
INSTALL_MANIFEST_PATH = PurePosixPath("ai-workflow/install-manifest.json")
POLICY_PATH = PurePosixPath("AGENTS.md")
CLAUDE_POLICY_PATH = PurePosixPath("CLAUDE.md")
COMPOSITE_POLICY_PATHS = {POLICY_PATH, CLAUDE_POLICY_PATH}
LEGACY_POLICY_PATH = PurePosixPath(".github/copilot-instructions.md")
MANAGED_BEGIN = b"<!-- ai-workflow:managed-begin -->\n"
MANAGED_END = b"<!-- ai-workflow:managed-end -->\n"
PROJECT_BEGIN = b"\n<!-- ai-workflow:project-instructions -->\n"
ENTRY_FIELDS = {"sha256", "source_sha256", "origin"}
ORIGINS = {"created", "preexisting-identical", "composite", "composite-created"}
COMPOSITE_ORIGINS = {"composite", "composite-created"}
DEFAULT_PROJECT_OWNED = (
    "ai-workflow/project-profile.md",
    "ai-workflow/state/active.md",
    "ai-workflow/state/records/",
    "ai-workflow/state/archive/",
)
REVIEWED_SOURCE_MODES = {0o644, 0o755}
WINDOWS_ORDINARY_SOURCE_MODES = {0o444, 0o555, 0o666, 0o777}
EXECUTABLE_PAYLOAD_PATHS = frozenset()
DEFAULT_CREATED_MODE = 0o644
OwnedMapping = Tuple[PurePosixPath, PurePosixPath]


class AdoptionError(RuntimeError):
    """A recoverable validation or safety failure."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def safe_relative(raw: str) -> PurePosixPath:
    if not isinstance(raw, str):
        raise AdoptionError(f"project-relative path must be a string: {raw!r}")
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or ".." in path.parts or "." in path.parts or "\\" in raw:
        raise AdoptionError(f"unsafe project-relative path in manifest: {raw!r}")
    return path


def target_path(root: Path, relative: PurePosixPath) -> Path:
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise AdoptionError(f"refusing to follow target symlink: {current}")
    try:
        current.parent.resolve().relative_to(root)
    except ValueError as exc:
        raise AdoptionError(f"target escapes project root: {relative}") from exc
    return current


def require_plain_file(path: Path, label: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise AdoptionError(f"{label} must be a regular non-symlink file: {path}")


def reviewed_source_mode(
    path: Path,
    label: str,
    *,
    expected_mode: int = DEFAULT_CREATED_MODE,
    posix_modes_meaningful: Optional[bool] = None,
) -> int:
    require_plain_file(path, label)
    if expected_mode not in REVIEWED_SOURCE_MODES:
        raise AdoptionError(f"internal expected source mode is invalid: {expected_mode!r}")
    mode = stat.S_IMODE(path.stat().st_mode)
    if posix_modes_meaningful is None:
        posix_modes_meaningful = os.name != "nt"
    if posix_modes_meaningful:
        if mode != expected_mode:
            raise AdoptionError(
                f"{label} mode must be {expected_mode:04o}, found {mode:04o}: {path}"
            )
        return mode
    if mode not in WINDOWS_ORDINARY_SOURCE_MODES:
        allowed = ", ".join(f"{item:04o}" for item in sorted(WINDOWS_ORDINARY_SOURCE_MODES))
        raise AdoptionError(
            f"{label} mode must be an ordinary Windows file mode ({allowed}), found {mode:04o}: {path}"
        )
    return expected_mode


def expected_source_mode(relative: PurePosixPath) -> int:
    return 0o755 if relative.as_posix() in EXECUTABLE_PAYLOAD_PATHS else DEFAULT_CREATED_MODE


def load_json(path: Path, label: str) -> MutableMapping[str, object]:
    try:
        require_plain_file(path, label)
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AdoptionError(f"missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AdoptionError(f"malformed {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AdoptionError(f"{label} must be a JSON object: {path}")
    return value


def parse_version(raw: str) -> Tuple[int, int, int]:
    match = re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", raw)
    if match is None:
        raise AdoptionError(f"framework version must be numeric MAJOR.MINOR.PATCH: {raw!r}")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def load_source_manifest() -> Tuple[
    str,
    List[Tuple[PurePosixPath, PurePosixPath]],
    List[Tuple[PurePosixPath, PurePosixPath]],
    set[PurePosixPath],
]:
    raw = load_json(SOURCE_MANIFEST, "source distribution manifest")
    required = {
        "schema_version",
        "framework_version",
        "framework_owned",
        "project_seeds",
        "checksums",
        "retired_framework_owned",
    }
    if set(raw) != required or raw.get("schema_version") != 2:
        raise AdoptionError("source manifest has unknown fields or an unsupported schema")
    version = raw.get("framework_version")
    owned_raw = raw.get("framework_owned")
    seeds_raw = raw.get("project_seeds")
    checksums_raw = raw.get("checksums")
    retired_raw = raw.get("retired_framework_owned")
    if not isinstance(version, str):
        raise AdoptionError("source manifest needs a string framework_version")
    parse_version(version)
    if not isinstance(owned_raw, list) or not isinstance(seeds_raw, list):
        raise AdoptionError("source manifest needs framework_owned and project_seeds arrays")
    if not isinstance(checksums_raw, dict) or not isinstance(retired_raw, list):
        raise AdoptionError("source manifest needs checksums object and retired_framework_owned array")

    owned: List[Tuple[PurePosixPath, PurePosixPath]] = []
    for item in owned_raw:
        if not isinstance(item, dict) or set(item) != {"source", "target"}:
            raise AdoptionError("each framework-owned entry needs exactly source and target fields")
        owned.append((safe_relative(item["source"]), safe_relative(item["target"])))
    owned_sources = [source for source, _ in owned]
    owned_targets = [target for _, target in owned]
    if len(set(owned_sources)) != len(owned_sources) or len(set(owned_targets)) != len(owned_targets):
        raise AdoptionError("framework-owned source and target paths must be unique")
    seeds: List[Tuple[PurePosixPath, PurePosixPath]] = []
    for item in seeds_raw:
        if not isinstance(item, dict) or set(item) != {"source", "target"}:
            raise AdoptionError("each project seed needs exactly source and target fields")
        seeds.append((safe_relative(item["source"]), safe_relative(item["target"])))
    seed_sources = [source for source, _ in seeds]
    seed_targets = [target for _, target in seeds]
    if len(set(seed_sources)) != len(seed_sources) or len(set(seed_targets)) != len(seed_targets):
        raise AdoptionError("project seed source and target paths must be unique")
    if set(owned_targets) & set(seed_targets):
        raise AdoptionError("framework-owned paths and project seed targets must be disjoint")

    retired = {safe_relative(item) for item in retired_raw}
    if len(retired) != len(retired_raw) or retired & set(owned_targets):
        raise AdoptionError("retired framework paths must be unique and disjoint from current paths")

    for version_path, label in (
        (PACKAGE_ROOT / "VERSION", "package VERSION"),
        (SOURCE_ROOT / "VERSION", "payload VERSION"),
    ):
        require_plain_file(version_path, label)
        version_file = version_path.read_text(encoding="utf-8").strip()
        if version_file != version:
            raise AdoptionError(f"{label} {version_file!r} does not match manifest {version!r}")

    expected_checksum_paths = {path.as_posix() for path in owned_sources}
    expected_checksum_paths.update(source.as_posix() for source, _ in seeds)
    if set(checksums_raw) != expected_checksum_paths:
        raise AdoptionError("source manifest checksums do not exactly cover owned files and seed sources")
    for source_relative, target_relative in owned:
        path = SOURCE_ROOT.joinpath(*source_relative.parts)
        reviewed_source_mode(
            path,
            f"framework source {source_relative} for {target_relative}",
            expected_mode=expected_source_mode(source_relative),
        )
        if checksums_raw.get(source_relative.as_posix()) != sha256_file(path):
            raise AdoptionError(f"payload checksum mismatch for {source_relative}")
    for source_relative, _ in seeds:
        path = SOURCE_ROOT.joinpath(*source_relative.parts)
        reviewed_source_mode(
            path,
            f"seed source {source_relative}",
            expected_mode=expected_source_mode(source_relative),
        )
        if checksums_raw.get(source_relative.as_posix()) != sha256_file(path):
            raise AdoptionError(f"payload checksum mismatch for seed {source_relative}")
    return version, owned, seeds, retired


def load_installed(root: Path) -> MutableMapping[str, object]:
    path = target_path(root, INSTALL_MANIFEST_PATH)
    raw = load_json(path, "installation manifest")
    required = {"schema_version", "framework_version", "source_revision", "installed_at", "framework_files", "project_owned"}
    if set(raw) != required or raw.get("schema_version") != 1:
        raise AdoptionError(f"installation manifest has unknown fields or an unsupported schema: {path}")
    version = raw.get("framework_version")
    if not isinstance(version, str):
        raise AdoptionError("installation manifest needs framework_version")
    parse_version(version)
    files = raw.get("framework_files")
    if not isinstance(files, dict) or not files:
        raise AdoptionError("installation manifest needs a nonempty framework_files object")
    for relative, details in files.items():
        path_key = safe_relative(relative)
        if not isinstance(details, dict) or set(details) != ENTRY_FIELDS:
            raise AdoptionError(f"invalid checksum/provenance entry for {path_key}")
        if details.get("origin") not in ORIGINS:
            raise AdoptionError(f"invalid origin for {path_key}: {details.get('origin')!r}")
        for field in ("sha256", "source_sha256"):
            value = details.get(field)
            if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
                raise AdoptionError(f"invalid {field} for {path_key}")
        if details["origin"] in {"created", "preexisting-identical"} and details["sha256"] != details["source_sha256"]:
            raise AdoptionError(f"non-composite checksums disagree for {path_key}")
        if details["origin"] in COMPOSITE_ORIGINS and path_key not in COMPOSITE_POLICY_PATHS:
            legacy_allowed = path_key == LEGACY_POLICY_PATH and parse_version(version) < (0, 2, 0)
            if not legacy_allowed:
                allowed = ", ".join(str(path) for path in sorted(COMPOSITE_POLICY_PATHS))
                raise AdoptionError(f"only shared instruction files may be composite: {allowed}")
    if not isinstance(raw.get("source_revision"), str) or not isinstance(raw.get("installed_at"), str):
        raise AdoptionError("installation manifest revision and timestamp must be strings")
    project_owned = raw.get("project_owned")
    if not isinstance(project_owned, list) or not all(isinstance(item, str) for item in project_owned):
        raise AdoptionError("installation manifest project_owned must be an array")
    project_paths = [safe_relative(item) for item in project_owned]
    if len(project_paths) != len(set(project_paths)):
        raise AdoptionError("installation manifest project_owned contains duplicates")
    overlap = set(project_paths) & {safe_relative(item) for item in files}
    if overlap:
        raise AdoptionError(
            "installation manifest records paths as both framework-owned and project-owned: "
            + ", ".join(str(path) for path in sorted(overlap))
        )
    return raw


def compose_policy(source: bytes, project: bytes) -> bytes:
    return MANAGED_BEGIN + source + MANAGED_END + PROJECT_BEGIN + project


def parse_composite_policy(data: bytes) -> Tuple[bytes, bytes]:
    if not data.startswith(MANAGED_BEGIN):
        raise AdoptionError("composite policy is missing its managed-begin marker")
    delimiter = MANAGED_END + PROJECT_BEGIN
    if data.count(delimiter) != 1:
        raise AdoptionError("composite policy has missing or duplicate managed markers")
    managed, project = data[len(MANAGED_BEGIN) :].split(delimiter, 1)
    return managed, project


def render_seed(source_relative: PurePosixPath, destination_relative: PurePosixPath) -> bytes:
    data = SOURCE_ROOT.joinpath(*source_relative.parts).read_bytes()
    if destination_relative == PurePosixPath("ai-workflow/state/active.md"):
        today = dt.datetime.now(dt.timezone.utc).date().isoformat().encode("ascii")
        data = data.replace(b"YYYY-MM-DD", today)
    return data


def entry(data: bytes, source: bytes, origin: str) -> Dict[str, str]:
    return {"sha256": sha256_bytes(data), "source_sha256": sha256_bytes(source), "origin": origin}


def installed_payload(
    version: str,
    files: Mapping[str, Mapping[str, str]],
    owned: Sequence[OwnedMapping],
    seeds: Sequence[Tuple[PurePosixPath, PurePosixPath]],
    revision: str,
    project_owned: Sequence[PurePosixPath] = (),
) -> bytes:
    project_paths = {PurePosixPath(item) for item in DEFAULT_PROJECT_OWNED}
    project_paths.update(project_owned)
    project_paths.difference_update(target for _, target in owned)
    payload = {
        "schema_version": 1,
        "framework_version": version,
        "source_revision": revision,
        "installed_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "framework_files": {path: dict(details) for path, details in sorted(files.items())},
        "project_owned": [path.as_posix() for path in sorted(project_paths)],
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def existing_regular(path: Path, label: str) -> Optional[bytes]:
    if not path.exists() and not path.is_symlink():
        return None
    require_plain_file(path, label)
    return path.read_bytes()


def plan_new_owned(
    root: Path, relative: PurePosixPath, source_data: bytes
) -> Tuple[str, Optional[bytes], Dict[str, str]]:
    destination = target_path(root, relative)
    current = existing_regular(destination, f"existing target {relative}")
    if current is None:
        if relative == POLICY_PATH:
            combined = compose_policy(source_data, b"")
            return (
                f"create framework policy with editable project section in {relative}",
                combined,
                entry(combined, source_data, "composite-created"),
            )
        return f"create framework file {relative}", source_data, entry(source_data, source_data, "created")
    if current == source_data:
        return f"adopt identical framework file {relative} but preserve it on removal", None, entry(current, source_data, "preexisting-identical")
    if relative in COMPOSITE_POLICY_PATHS:
        combined = compose_policy(source_data, current)
        return f"merge framework guidance with existing project instructions in {relative}", combined, entry(combined, source_data, "composite")
    raise AdoptionError(
        f"install would overwrite existing framework path {relative}; rename the colliding project skill or reconcile it explicitly"
    )


def plan_seeds(
    root: Path,
    seeds: Sequence[Tuple[PurePosixPath, PurePosixPath]],
    excluded: Iterable[PurePosixPath] = (),
) -> Tuple[List[str], Dict[str, bytes]]:
    actions: List[str] = []
    writes: Dict[str, bytes] = {}
    excluded_set = set(excluded)
    for source_relative, destination_relative in seeds:
        if destination_relative in excluded_set:
            continue
        destination = target_path(root, destination_relative)
        current = existing_regular(destination, f"project-owned seed target {destination_relative}")
        key = destination_relative.as_posix()
        if current is None:
            actions.append(f"seed project-owned file {key}")
            writes[key] = render_seed(source_relative, destination_relative)
        else:
            actions.append(f"preserve existing project-owned file {key}")
    return actions, writes


def plan_install(root: Path) -> Tuple[List[str], Dict[str, bytes], Dict[str, Dict[str, str]], str, List[OwnedMapping], List[Tuple[PurePosixPath, PurePosixPath]]]:
    version, owned, seeds, _ = load_source_manifest()
    manifest_path = target_path(root, INSTALL_MANIFEST_PATH)
    if manifest_path.exists() or manifest_path.is_symlink():
        raise AdoptionError("installation manifest already exists; use update")
    actions: List[str] = []
    writes: Dict[str, bytes] = {}
    entries: Dict[str, Dict[str, str]] = {}
    for source_relative, target_relative in owned:
        source_data = SOURCE_ROOT.joinpath(*source_relative.parts).read_bytes()
        action, data, details = plan_new_owned(root, target_relative, source_data)
        actions.append(action)
        if data is not None:
            writes[target_relative.as_posix()] = data
        entries[target_relative.as_posix()] = details
    seed_actions, seed_writes = plan_seeds(root, seeds)
    actions.extend(seed_actions)
    writes.update(seed_writes)
    actions.append(f"create installation manifest {INSTALL_MANIFEST_PATH}")
    return actions, writes, entries, version, owned, seeds


def plan_existing_owned(
    root: Path,
    relative: PurePosixPath,
    source_data: bytes,
    old: Mapping[str, str],
) -> Tuple[str, Optional[bytes], Dict[str, str]]:
    destination = target_path(root, relative)
    current = existing_regular(destination, f"installed framework target {relative}")
    origin = old["origin"]
    if current is None:
        if origin == "preexisting-identical":
            raise AdoptionError(f"preexisting framework file was removed; refusing to recreate it as framework-owned: {relative}")
        if origin in COMPOSITE_ORIGINS or (relative == POLICY_PATH and origin == "created"):
            restored = compose_policy(source_data, b"")
            return (
                f"restore missing composite policy {relative}",
                restored,
                entry(restored, source_data, "composite-created"),
            )
        return f"restore missing framework file {relative}", source_data, entry(source_data, source_data, "created")
    if origin in COMPOSITE_ORIGINS:
        managed, project = parse_composite_policy(current)
        if sha256_bytes(managed) != old["source_sha256"]:
            raise AdoptionError(f"managed policy block was locally changed: {relative}")
        updated = compose_policy(source_data, project)
        if updated == current:
            return f"keep current composite policy {relative}", None, entry(current, source_data, origin)
        return f"update managed policy block and preserve project instructions in {relative}", updated, entry(updated, source_data, origin)
    current_digest = sha256_bytes(current)
    if relative == POLICY_PATH and origin == "created":
        if current_digest != old["sha256"]:
            raise AdoptionError(f"locally changed framework file: {relative}")
        migrated = compose_policy(source_data, b"")
        return (
            f"migrate framework-created policy to an editable composite in {relative}",
            migrated,
            entry(migrated, source_data, "composite-created"),
        )
    if current == source_data:
        return f"keep current framework file {relative}", None, entry(current, source_data, origin)
    if current_digest != old["sha256"]:
        raise AdoptionError(f"locally changed framework file: {relative}")
    if origin == "preexisting-identical":
        raise AdoptionError(
            f"framework update would replace a file that predated installation: {relative}; reconcile it explicitly first"
        )
    return f"update framework file {relative}", source_data, entry(source_data, source_data, "created")


def plan_update(root: Path) -> Tuple[List[str], Dict[str, bytes], List[str], Dict[str, Dict[str, str]], str, List[OwnedMapping], List[Tuple[PurePosixPath, PurePosixPath]], List[PurePosixPath]]:
    installed = load_installed(root)
    version, owned, seeds, retired = load_source_manifest()
    installed_version = installed["framework_version"]
    if parse_version(version) < parse_version(installed_version):
        raise AdoptionError(f"refusing downgrade from {installed_version} to {version}; use the installed version's source or reinstall deliberately")
    old_files = installed["framework_files"]
    new_keys = {target.as_posix() for _, target in owned}
    seed_targets = {target for _, target in seeds}
    actions: List[str] = []
    writes: Dict[str, bytes] = {}
    removals: List[str] = []
    entries: Dict[str, Dict[str, str]] = {}

    for source_relative, target_relative in owned:
        key = target_relative.as_posix()
        source_data = SOURCE_ROOT.joinpath(*source_relative.parts).read_bytes()
        old = old_files.get(key)
        if old is None:
            action, data, details = plan_new_owned(root, target_relative, source_data)
        else:
            action, data, details = plan_existing_owned(root, target_relative, source_data, old)
        actions.append(action)
        if data is not None:
            writes[key] = data
        entries[key] = details

    reclassified = [safe_relative(item) for item in installed["project_owned"]]
    retired_seed_targets: List[PurePosixPath] = []
    for key in old_files:
        if key in new_keys:
            continue
        relative = safe_relative(key)
        destination = target_path(root, relative)
        current = existing_regular(destination, f"retired framework target {relative}")
        if current is None:
            actions.append(f"retired framework file already absent {relative}")
            continue
        details = old_files[key]
        if relative in retired and details["origin"] == "created" and sha256_bytes(current) == details["sha256"]:
            actions.append(f"remove explicitly retired unchanged framework file {relative}")
            removals.append(key)
            continue
        reclassified.append(relative)
        suffix = " seed" if relative in seed_targets else ""
        if relative in seed_targets:
            retired_seed_targets.append(relative)
        actions.append(
            f"preserve retired framework file as project-owned{suffix} {relative}; review and remove it separately if obsolete"
        )

    seed_actions, seed_writes = plan_seeds(root, seeds, excluded=retired_seed_targets)
    actions.extend(seed_actions)
    writes.update(seed_writes)
    actions.append(f"refresh installation manifest {INSTALL_MANIFEST_PATH}")
    return actions, writes, removals, entries, version, owned, seeds, sorted(set(reclassified))


def preflight_parent(root: Path, path: Path) -> None:
    current = root
    relative_parent = path.parent.relative_to(root)
    for part in relative_parent.parts:
        current = current / part
        if current.is_symlink():
            raise AdoptionError(f"refusing to follow target symlink: {current}")
        if current.exists() and not current.is_dir():
            raise AdoptionError(f"target parent is not a directory: {current}")


def atomic_write(path: Path, data: bytes, mode: int = DEFAULT_CREATED_MODE) -> None:
    if not isinstance(mode, int) or not 0 <= mode <= 0o7777:
        raise AdoptionError(f"invalid file mode for atomic write: {mode!r}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            if hasattr(os, "fchmod"):
                os.fchmod(handle.fileno(), mode)
            else:  # pragma: no cover - fchmod is available on supported POSIX hosts.
                os.chmod(temporary, mode)
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def remove_empty_parents(path: Path, root: Path) -> None:
    parent = path.parent
    while parent != root:
        try:
            parent.rmdir()
        except OSError:
            return
        parent = parent.parent


def source_target_modes(
    owned: Sequence[OwnedMapping], seeds: Sequence[Tuple[PurePosixPath, PurePosixPath]]
) -> Dict[str, int]:
    modes = {
        target_relative.as_posix(): reviewed_source_mode(
            SOURCE_ROOT.joinpath(*source_relative.parts),
            f"framework source {source_relative}",
            expected_mode=expected_source_mode(source_relative),
        )
        for source_relative, target_relative in owned
    }
    for source_relative, target_relative in seeds:
        modes[target_relative.as_posix()] = reviewed_source_mode(
            SOURCE_ROOT.joinpath(*source_relative.parts),
            f"seed source {source_relative}",
            expected_mode=expected_source_mode(source_relative),
        )
    modes[INSTALL_MANIFEST_PATH.as_posix()] = DEFAULT_CREATED_MODE
    return modes


def apply_transaction(
    root: Path,
    writes: Sequence[Tuple[str, bytes]],
    removals: Sequence[str],
    new_file_modes: Optional[Mapping[str, int]] = None,
) -> None:
    requested_modes = new_file_modes or {}
    keys = [key for key, _ in writes] + list(removals)
    if len(keys) != len(set(keys)):
        raise AdoptionError("internal transaction contains duplicate write/removal targets")
    for key, mode in requested_modes.items():
        if mode not in REVIEWED_SOURCE_MODES:
            raise AdoptionError(f"internal transaction has unreviewed new-file mode {mode:04o} for {key}")
    snapshots: Dict[str, Optional[Tuple[bytes, int]]] = {}
    paths: Dict[str, Path] = {}
    for key in keys:
        relative = safe_relative(key)
        path = target_path(root, relative)
        preflight_parent(root, path)
        paths[key] = path
        current = existing_regular(path, f"transaction target {relative}")
        snapshots[key] = None if current is None else (current, stat.S_IMODE(path.stat().st_mode))

    changed: List[str] = []
    try:
        for key, data in writes:
            snapshot = snapshots[key]
            mode = snapshot[1] if snapshot is not None else requested_modes.get(key, DEFAULT_CREATED_MODE)
            changed.append(key)
            atomic_write(paths[key], data, mode)
        for key in removals:
            path = paths[key]
            changed.append(key)
            if path.exists():
                path.unlink()
                remove_empty_parents(path, root)
    except BaseException as error:
        rollback_errors: List[str] = []
        for key in reversed(changed):
            path = paths[key]
            try:
                original = snapshots[key]
                if original is None:
                    if path.exists() or path.is_symlink():
                        path.unlink()
                        remove_empty_parents(path, root)
                else:
                    original_data, original_mode = original
                    atomic_write(path, original_data, original_mode)
            except BaseException as rollback_error:
                rollback_errors.append(f"{key}: {rollback_error}")
        detail = f"transaction failed and changes were rolled back: {error}"
        if rollback_errors:
            detail += "; rollback also failed for " + ", ".join(rollback_errors)
            raise AdoptionError(detail) from error
        if isinstance(error, OSError):
            raise AdoptionError(detail) from error
        raise


def command_install(root: Path, dry_run: bool, revision: str) -> None:
    manifest_path = target_path(root, INSTALL_MANIFEST_PATH)
    if manifest_path.exists() or manifest_path.is_symlink():
        installed = load_installed(root)
        version, _, _, _ = load_source_manifest()
        if installed["framework_version"] == version and command_status(root, verbose=False):
            print(f"✓ Agentic workflow {version} is already installed and verified.")
            return
        raise AdoptionError("an installation already exists but is different; run update or status")
    actions, writes, entries, version, owned, seeds = plan_install(root)
    if dry_run:
        print_plan("INSTALL", root, actions)
        return
    manifest = installed_payload(version, entries, owned, seeds, revision)
    ordered = sorted(writes.items()) + [(INSTALL_MANIFEST_PATH.as_posix(), manifest)]
    source_modes = source_target_modes(owned, seeds)
    apply_transaction(root, ordered, (), {key: source_modes[key] for key, _ in ordered})
    if not command_status(root, verbose=False):
        raise AdoptionError("post-install verification failed")
    print(f"✓ Agentic workflow {version} installed and verified.")


def command_update(root: Path, dry_run: bool, revision: str) -> None:
    actions, writes, removals, entries, version, owned, seeds, project_owned = plan_update(root)
    if dry_run:
        print_plan("UPDATE", root, actions)
        return
    manifest = installed_payload(version, entries, owned, seeds, revision, project_owned)
    ordered = sorted(writes.items()) + [(INSTALL_MANIFEST_PATH.as_posix(), manifest)]
    source_modes = source_target_modes(owned, seeds)
    apply_transaction(root, ordered, removals, {key: source_modes[key] for key, _ in ordered})
    if not command_status(root, verbose=False):
        raise AdoptionError("post-update verification failed")
    print(f"✓ Agentic workflow updated to {version} and verified.")


def command_status(root: Path, verbose: bool = True) -> bool:
    installed = load_installed(root)
    source_version, owned, _, _ = load_source_manifest()
    if installed["framework_version"] != source_version:
        raise AdoptionError(
            f"status source version {source_version} does not match installed {installed['framework_version']}"
        )
    expected_keys = {target.as_posix() for _, target in owned}
    installed_keys = set(installed["framework_files"])
    if installed_keys != expected_keys:
        raise AdoptionError("installation ownership does not match the exact source package")
    for source_relative, target_relative in owned:
        source_digest = sha256_file(SOURCE_ROOT.joinpath(*source_relative.parts))
        if installed["framework_files"][target_relative.as_posix()]["source_sha256"] != source_digest:
            raise AdoptionError(f"installation manifest source checksum was changed for {target_relative}")
    if verbose:
        print(f"STATUS {root}")
        print(f"version: {installed['framework_version']}")
        print(f"source revision: {installed['source_revision']}")
    states: List[str] = []
    for key, details in sorted(installed["framework_files"].items()):
        path = target_path(root, safe_relative(key))
        current = existing_regular(path, f"installed framework target {key}")
        if current is None:
            state = "missing"
        elif details["origin"] in COMPOSITE_ORIGINS:
            try:
                managed, _ = parse_composite_policy(current)
            except AdoptionError:
                state = "modified"
            else:
                state = "clean" if sha256_bytes(managed) == details["source_sha256"] else "modified"
        else:
            state = "clean" if sha256_bytes(current) == details["sha256"] else "modified"
        states.append(state)
        if verbose:
            print(f"{state}: {key}")
    clean = all(state == "clean" for state in states)
    if verbose:
        print("✓ Installation is clean." if clean else "Installation differs from its recorded framework files.")
    return clean


def command_remove(root: Path, dry_run: bool) -> None:
    installed = load_installed(root)
    version, owned, seeds, _ = load_source_manifest()
    if installed["framework_version"] != version:
        raise AdoptionError(
            f"removal source version {version} does not match installed {installed['framework_version']}; use the recorded version's source"
        )
    source_keys = {target.as_posix() for _, target in owned}
    installed_keys = set(installed["framework_files"])
    if installed_keys != source_keys:
        unexpected = sorted(installed_keys - source_keys)
        missing = sorted(source_keys - installed_keys)
        raise AdoptionError(
            "installation ownership does not match this source; refusing deletion"
            + (f"; unexpected: {', '.join(unexpected)}" if unexpected else "")
            + (f"; missing: {', '.join(missing)}" if missing else "")
        )

    actions: List[str] = []
    writes: List[Tuple[str, bytes]] = []
    removals: List[str] = []
    for source_relative, relative in owned:
        key = relative.as_posix()
        details = installed["framework_files"][key]
        source_data = SOURCE_ROOT.joinpath(*source_relative.parts).read_bytes()
        if details["source_sha256"] != sha256_bytes(source_data):
            raise AdoptionError(f"installed ownership checksum does not match this source for {relative}")
        path = target_path(root, relative)
        current = existing_regular(path, f"installed framework target {relative}")
        if current is None:
            actions.append(f"already absent {relative}")
        elif details["origin"] == "preexisting-identical":
            actions.append(f"preserve file that predated installation {relative}")
        elif details["origin"] in COMPOSITE_ORIGINS:
            try:
                managed, project = parse_composite_policy(current)
            except AdoptionError:
                actions.append(f"preserve locally changed composite policy {relative}")
            else:
                if sha256_bytes(managed) == details["source_sha256"]:
                    if details["origin"] == "composite-created" and not project:
                        actions.append(f"remove empty framework-created policy {relative}")
                        removals.append(key)
                    else:
                        actions.append(f"remove managed block and restore project instructions in {relative}")
                        writes.append((key, project))
                else:
                    actions.append(f"preserve locally changed composite policy {relative}")
        elif sha256_bytes(current) == details["sha256"]:
            actions.append(f"remove unchanged framework file {relative}")
            removals.append(key)
        else:
            actions.append(f"preserve locally changed framework file {relative}")
    actions.append("preserve all project-owned profile and state files")
    actions.append(f"remove installation manifest {INSTALL_MANIFEST_PATH}")
    if dry_run:
        print_plan("REMOVE", root, actions)
        return
    removals.append(INSTALL_MANIFEST_PATH.as_posix())
    apply_transaction(root, writes, removals)
    print("✓ Agentic workflow removed; project-owned profile, state, and instructions were preserved.")


def print_plan(action: str, root: Path, actions: Sequence[str]) -> None:
    print(f"{action} DRY RUN for {root}")
    for item in actions:
        print(f"  - {item}")
    print("No files changed. Re-run without --dry-run to apply this operation.")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "update", "status", "remove"))
    parser.add_argument(
        "target",
        nargs="?",
        default=Path.cwd(),
        type=Path,
        help="project root (default: current directory)",
    )
    parser.add_argument("--dry-run", action="store_true", help="show a safe plan without changing files")
    parser.add_argument(
        "--source-revision",
        default="unreleased-local-package",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.action == "status" and args.dry_run:
        raise AdoptionError("--dry-run is not valid for status")
    root = args.target.expanduser().resolve()
    if not root.is_dir():
        raise AdoptionError(f"target project directory does not exist: {root}")
    if root == Path(root.anchor):
        raise AdoptionError("refusing to operate on a filesystem root")
    if args.action == "install":
        command_install(root, args.dry_run, args.source_revision)
    elif args.action == "update":
        command_update(root, args.dry_run, args.source_revision)
    elif args.action == "status":
        return 0 if command_status(root) else 1
    else:
        command_remove(root, args.dry_run)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AdoptionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
    except OSError as error:
        print(f"ERROR: filesystem operation failed before changes were applied: {error}", file=sys.stderr)
        raise SystemExit(2)
