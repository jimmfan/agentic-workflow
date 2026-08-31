#!/usr/bin/env python3
"""Reconcile the small local Agent Workflow payload with a project."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from enum import Enum
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

from legacy_transition import (
    FORMER_FRAMEWORK_VERSION,
    FORMER_PROVIDERS_SHA256,
    LEGACY_PROVIDER_PROOF,
    LEGACY_PROVIDER_SKILLS,
    LEGACY_WORKFLOW_DIGESTS,
    PINNED_MAIN_COMMIT,
)


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PAYLOAD_ROOT = PACKAGE_ROOT / "payload"
DISTRIBUTION_MANIFEST = PAYLOAD_ROOT / "distribution" / "manifest.json"
VERSION_FILE = PACKAGE_ROOT / "VERSION"
FRAMEWORK_ROOT = PurePosixPath(".agent-workflow")
DURABLE_ROOT = PurePosixPath(".agent-wayfinder")
INSTALL_MANIFEST = FRAMEWORK_ROOT / "install-manifest.json"
COMPOSITE_PATHS = {PurePosixPath("AGENTS.md"), PurePosixPath("CLAUDE.md")}
MANAGED_BEGIN = b"<!-- agent-workflow:managed-begin -->\n"
MANAGED_END = b"<!-- agent-workflow:managed-end -->\n"
PROJECT_BEGIN = b"\n<!-- agent-workflow:project-instructions -->\n"
MINIMUM_PYTHON = (3, 11)
DISTRIBUTION_SCHEMA = 7
INSTALL_SCHEMA = 2
FORMER_INSTALL_SCHEMA = 1
LOCAL_REVISION = "unreleased-local-package"
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}")
REMOVED_LEGACY_SKILLS = frozenset(
    {"setup-matt-pocock-skills", "teach", "triage"}
)
RETAINED_LEGACY_SKILLS = LEGACY_PROVIDER_SKILLS - REMOVED_LEGACY_SKILLS


class AdoptionError(RuntimeError):
    """A safe, user-actionable lifecycle failure."""


class DuplicateKeyError(ValueError):
    """Raised when JSON contains a duplicate object key."""


class InstallStateKind(Enum):
    ABSENT = "absent"
    VALID = "valid"
    INVALID = "invalid"


@dataclass(frozen=True)
class InstallState:
    kind: InstallStateKind
    external_files: Mapping[str, Mapping[str, object]]
    composites: Mapping[str, Mapping[str, object]]
    framework_version: str | None = None
    source_revision: str | None = None
    legacy: bool = False
    manifest_sha256: str | None = None
    error: str | None = None


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
        raise AdoptionError("Agent Workflow requires Python 3.11 or newer")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise AdoptionError(f"unsafe relative path: {value!r}")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise AdoptionError(f"unsafe relative path: {value!r}") from exc
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or path.as_posix() != value
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise AdoptionError(f"unsafe relative path: {value!r}")
    return path


def validate_revision(value: str) -> str:
    if value != LOCAL_REVISION and REVISION_PATTERN.fullmatch(value) is None:
        raise AdoptionError(
            "source revision must be a 40-character lowercase Git commit or unreleased-local-package"
        )
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


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json_bytes(data: bytes, label: str) -> MutableMapping[str, object]:
    try:
        value = json.loads(
            data.decode("utf-8"), object_pairs_hook=reject_duplicate_keys
        )
    except (UnicodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        raise AdoptionError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise AdoptionError(f"{label} must contain a JSON object")
    return value


def load_json(path: Path, label: str) -> MutableMapping[str, object]:
    if path.is_symlink() or not path.is_file():
        raise AdoptionError(f"{label} must be a regular non-symlink file: {path}")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise AdoptionError(f"cannot read {label}: {exc}") from exc
    return parse_json_bytes(data, label)


def package_version() -> str:
    if VERSION_FILE.is_symlink() or not VERSION_FILE.is_file():
        raise AdoptionError(
            f"package VERSION must be a regular non-symlink file: {VERSION_FILE}"
        )
    try:
        version = VERSION_FILE.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as exc:
        raise AdoptionError(f"cannot read package VERSION: {exc}") from exc
    if re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        raise AdoptionError("package VERSION must use x.y.z")
    return version


def load_distribution() -> tuple[str, list[tuple[PurePosixPath, PurePosixPath]]]:
    raw = load_json(DISTRIBUTION_MANIFEST, "distribution manifest")
    if raw.get("schema_version") != DISTRIBUTION_SCHEMA:
        raise AdoptionError("unsupported distribution manifest schema")
    version = package_version()
    mappings = raw.get("framework_owned")
    if not isinstance(mappings, list):
        raise AdoptionError("distribution manifest needs a framework_owned array")

    result: list[tuple[PurePosixPath, PurePosixPath]] = []
    for item in mappings:
        if not isinstance(item, dict) or set(item) != {"source", "target"}:
            raise AdoptionError("distribution mappings require only source and target")
        source = safe_relative(item["source"])
        target = safe_relative(item["target"])
        if (
            target == INSTALL_MANIFEST
            or target == DURABLE_ROOT
            or DURABLE_ROOT in target.parents
        ):
            raise AdoptionError(f"distribution must not own lifecycle state: {target}")
        source_path = PAYLOAD_ROOT.joinpath(*source.parts)
        if source_path.is_symlink() or not source_path.is_file():
            raise AdoptionError(
                f"required current payload source is missing or unsafe: {source}"
            )
        result.append((source, target))

    sources = [source for source, _target in result]
    targets = [target for _source, target in result]
    if len(sources) != len(set(sources)) or len(targets) != len(set(targets)):
        raise AdoptionError(
            "distribution mappings must have unique sources and targets"
        )
    return version, result


def empty_install_state() -> InstallState:
    return InstallState(InstallStateKind.ABSENT, {}, {})


def invalid_install_state(message: str) -> InstallState:
    return InstallState(InstallStateKind.INVALID, {}, {}, error=message)


def canonical_integrity_value(
    schema_version: int,
    framework_version: str,
    source_revision: str,
    external: Mapping[str, Mapping[str, object]],
    composites: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    return {
        "schema_version": schema_version,
        "framework_version": framework_version,
        "source_revision": source_revision,
        "external_files": dict(sorted(external.items())),
        "composites": dict(sorted(composites.items())),
    }


def install_state_integrity(
    schema_version: int,
    framework_version: str,
    source_revision: str,
    external: Mapping[str, Mapping[str, object]],
    composites: Mapping[str, Mapping[str, object]],
) -> str:
    encoded = json.dumps(
        canonical_integrity_value(
            schema_version,
            framework_version,
            source_revision,
            external,
            composites,
        ),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return digest(encoded)


def validate_external_state(value: object) -> dict[str, dict[str, object]]:
    if not isinstance(value, dict):
        raise AdoptionError("external_files must be an object")
    external: dict[str, dict[str, object]] = {}
    for key, details in value.items():
        relative = safe_relative(key)
        if (
            relative == FRAMEWORK_ROOT
            or FRAMEWORK_ROOT in relative.parents
            or relative == DURABLE_ROOT
            or DURABLE_ROOT in relative.parents
            or relative in COMPOSITE_PATHS
        ):
            raise AdoptionError(
                f"external install state must not own internal or composite target: {relative}"
            )
        if not isinstance(details, dict) or set(details) != {"created", "sha256"}:
            raise AdoptionError(f"invalid external state entry: {key}")
        created = details["created"]
        checksum = details["sha256"]
        if (
            not isinstance(created, bool)
            or not isinstance(checksum, str)
            or SHA256_PATTERN.fullmatch(checksum) is None
        ):
            raise AdoptionError(f"invalid external state entry: {key}")
        external[relative.as_posix()] = {"created": created, "sha256": checksum}
    return external


def validate_composite_state(value: object) -> dict[str, dict[str, object]]:
    if not isinstance(value, dict):
        raise AdoptionError("composites must be an object")
    composites: dict[str, dict[str, object]] = {}
    for key, details in value.items():
        relative = safe_relative(key)
        if (
            relative not in COMPOSITE_PATHS
            or not isinstance(details, dict)
            or set(details) != {"created"}
            or not isinstance(details["created"], bool)
        ):
            raise AdoptionError(f"invalid composite state entry: {key}")
        composites[relative.as_posix()] = {"created": details["created"]}
    return composites


def inspect_legacy_tree(
    root: Path,
    relative: PurePosixPath,
    captured: Path | None = None,
) -> dict[str, tuple[str, str | None]]:
    result: dict[str, tuple[str, str | None]] = {}
    start = checked_target(root, relative) if captured is None else captured
    try:
        start_stat = os.lstat(start)
    except FileNotFoundError:
        return result
    except OSError as exc:
        raise AdoptionError(f"cannot inspect former skill root {relative}: {exc}") from exc

    def visit(path: Path, child: PurePosixPath, details: os.stat_result) -> None:
        if stat.S_ISLNK(details.st_mode):
            raise AdoptionError(f"former skill tree contains a symlink: {child}")
        if stat.S_ISDIR(details.st_mode):
            result[child.as_posix()] = ("directory", None)
            try:
                with os.scandir(path) as iterator:
                    entries = sorted(iterator, key=lambda item: item.name)
            except OSError as exc:
                raise AdoptionError(f"cannot inspect former skill tree {child}: {exc}") from exc
            for entry in entries:
                descendant = child / entry.name
                try:
                    entry_stat = entry.stat(follow_symlinks=False)
                except OSError as exc:
                    raise AdoptionError(
                        f"cannot inspect former skill entry {descendant}: {exc}"
                    ) from exc
                visit(Path(entry.path), descendant, entry_stat)
            return
        if stat.S_ISREG(details.st_mode):
            try:
                content = path.read_bytes()
            except OSError as exc:
                raise AdoptionError(f"cannot read former skill file {child}: {exc}") from exc
            result[child.as_posix()] = ("file", digest(content))
            return
        raise AdoptionError(f"former skill tree contains a special entry: {child}")

    visit(start, relative, start_stat)
    return result


def prove_legacy_provider_installation(root: Path) -> None:
    declaration = read_regular(root, FRAMEWORK_ROOT / "providers.json")
    if declaration is None or digest(declaration) != FORMER_PROVIDERS_SHA256:
        raise AdoptionError("former provider declaration does not match pinned main")

    actual: dict[str, tuple[str, str | None]] = {}
    for name in sorted(LEGACY_PROVIDER_SKILLS):
        relative = PurePosixPath(".agents/skills") / name
        actual.update(inspect_legacy_tree(root, relative))
    expected = dict(LEGACY_PROVIDER_PROOF)
    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    if missing or unexpected:
        raise AdoptionError(
            "former skill inventory differs from pinned main: "
            f"missing={missing!r}, unexpected={unexpected!r}"
        )
    for path, expected_entry in expected.items():
        if actual[path] != expected_entry:
            raise AdoptionError(f"former skill proof mismatch at {path}")


def parse_current_install_state(raw: Mapping[str, object]) -> InstallState:
    if set(raw) != {
        "schema_version",
        "framework_version",
        "source_revision",
        "external_files",
        "composites",
        "integrity_sha256",
    }:
        raise AdoptionError("current install manifest fields are incomplete or unexpected")
    if type(raw["schema_version"]) is not int or raw["schema_version"] != INSTALL_SCHEMA:
        raise AdoptionError("current install manifest schema is invalid")
    framework_version = raw["framework_version"]
    source_revision = raw["source_revision"]
    integrity = raw["integrity_sha256"]
    if not isinstance(framework_version, str) or re.fullmatch(
        r"\d+\.\d+\.\d+", framework_version
    ) is None:
        raise AdoptionError("invalid installed framework version")
    if not isinstance(source_revision, str):
        raise AdoptionError("invalid installed source revision")
    validate_revision(source_revision)
    if not isinstance(integrity, str) or SHA256_PATTERN.fullmatch(integrity) is None:
        raise AdoptionError("invalid install-state integrity digest")
    external = validate_external_state(raw["external_files"])
    composites = validate_composite_state(raw["composites"])
    expected = install_state_integrity(
        INSTALL_SCHEMA,
        framework_version,
        source_revision,
        external,
        composites,
    )
    if integrity != expected:
        raise AdoptionError("install-state integrity digest mismatch")
    return InstallState(
        InstallStateKind.VALID,
        external,
        composites,
        framework_version,
        source_revision,
    )


def parse_legacy_install_state(root: Path, raw: Mapping[str, object]) -> InstallState:
    if set(raw) != {
        "schema_version",
        "framework_version",
        "source_revision",
        "external_files",
        "composites",
    }:
        raise AdoptionError("former install manifest fields differ from pinned main")
    if (
        type(raw["schema_version"]) is not int
        or raw["schema_version"] != FORMER_INSTALL_SCHEMA
    ):
        raise AdoptionError("former install manifest schema differs from pinned main")
    if raw["framework_version"] != FORMER_FRAMEWORK_VERSION:
        raise AdoptionError("former framework version differs from pinned main")
    source_revision = raw["source_revision"]
    if not isinstance(source_revision, str):
        raise AdoptionError("invalid former source revision")
    validate_revision(source_revision)
    if source_revision not in {LOCAL_REVISION, PINNED_MAIN_COMMIT}:
        raise AdoptionError("former source revision differs from pinned main")
    external = validate_external_state(raw["external_files"])
    composites = validate_composite_state(raw["composites"])
    if set(external) != set(LEGACY_WORKFLOW_DIGESTS):
        raise AdoptionError("former external install state differs from pinned main")
    for path, checksum in LEGACY_WORKFLOW_DIGESTS.items():
        if external[path]["sha256"] != checksum:
            raise AdoptionError(f"former external digest differs at {path}")
    if set(composites) != {path.as_posix() for path in COMPOSITE_PATHS}:
        raise AdoptionError("former composite install state differs from pinned main")
    prove_legacy_provider_installation(root)
    return InstallState(
        InstallStateKind.VALID,
        external,
        composites,
        FORMER_FRAMEWORK_VERSION,
        source_revision,
        legacy=True,
    )


def managed_install_evidence(root: Path) -> bool:
    framework = checked_target(root, FRAMEWORK_ROOT)
    if os.path.lexists(framework):
        return True
    for relative in COMPOSITE_PATHS:
        path = checked_target(root, relative)
        if not os.path.lexists(path):
            continue
        if path.is_symlink() or not path.is_file():
            return True
        try:
            if has_any_marker(path.read_bytes()):
                return True
        except OSError:
            return True
    return False


def load_install_state(root: Path) -> InstallState:
    """Classify install state without converting corruption into an empty state."""
    try:
        data = read_regular(root, INSTALL_MANIFEST)
    except AdoptionError as exc:
        return invalid_install_state(str(exc))
    if data is None:
        try:
            evidence = managed_install_evidence(root)
        except AdoptionError as exc:
            return invalid_install_state(str(exc))
        if evidence:
            return invalid_install_state(
                "install manifest is absent while managed-install evidence remains"
            )
        return empty_install_state()
    try:
        raw = parse_json_bytes(data, "install manifest")
        schema_version = raw.get("schema_version")
        if type(schema_version) is not int:
            raise AdoptionError("install manifest schema must be an integer")
        if schema_version == INSTALL_SCHEMA:
            return replace(
                parse_current_install_state(raw), manifest_sha256=digest(data)
            )
        if schema_version == FORMER_INSTALL_SCHEMA:
            return replace(
                parse_legacy_install_state(root, raw), manifest_sha256=digest(data)
            )
        raise AdoptionError("unsupported install manifest schema")
    except AdoptionError as exc:
        return invalid_install_state(str(exc))


def require_usable_state(state: InstallState) -> None:
    if state.kind is InstallStateKind.INVALID:
        raise AdoptionError(f"invalid install state: {state.error}; no changes made")


def compose_policy(managed: bytes, project: bytes) -> bytes:
    managed_body = managed.rstrip(b"\n") + b"\n"
    return MANAGED_BEGIN + managed_body + MANAGED_END + PROJECT_BEGIN + project


def has_any_marker(data: bytes) -> bool:
    return any(marker in data for marker in (MANAGED_BEGIN, MANAGED_END, PROJECT_BEGIN))


def parse_policy(data: bytes) -> tuple[bytes, bytes]:
    if (
        data.count(MANAGED_BEGIN) != 1
        or data.count(MANAGED_END) != 1
        or data.count(PROJECT_BEGIN) != 1
    ):
        raise AdoptionError(
            "managed policy markers are missing, duplicated, or ambiguous"
        )
    if not data.startswith(MANAGED_BEGIN):
        raise AdoptionError("managed policy must start with its managed marker")
    managed_end = data.find(MANAGED_END, len(MANAGED_BEGIN))
    project_begin = data.find(PROJECT_BEGIN, managed_end + len(MANAGED_END))
    if managed_end < 0 or project_begin != managed_end + len(MANAGED_END):
        raise AdoptionError("managed policy markers are out of order")
    managed = data[len(MANAGED_BEGIN) : managed_end]
    project = data[project_begin + len(PROJECT_BEGIN) :]
    return managed, project


def source_bytes(source: PurePosixPath) -> bytes:
    try:
        return PAYLOAD_ROOT.joinpath(*source.parts).read_bytes()
    except OSError as exc:
        raise AdoptionError(
            f"cannot read current payload source {source}: {exc}"
        ) from exc


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


def atomic_write(
    path: Path, data: bytes, mode: int, root: Path, created: list[Path]
) -> None:
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


@dataclass
class ExternalTransaction:
    snapshots: dict[PurePosixPath, tuple[bytes, int] | None]
    created_directories: list[Path]
    moved_files: dict[PurePosixPath, Path]
    moved_roots: dict[PurePosixPath, Path]
    written_files: dict[PurePosixPath, bytes]
    backup_root: Path


def exclusive_write(
    path: Path,
    data: bytes,
    mode: int,
    root: Path,
    created: list[Path],
) -> None:
    ensure_parent(path, root, created)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, mode)
    except FileExistsError as exc:
        raise AdoptionError(
            "external target changed at lifecycle mutation boundary: "
            f"{path.relative_to(root)}"
        ) from exc
    except OSError as exc:
        raise AdoptionError(f"cannot create external target {path}: {exc}") from exc
    created_identity: tuple[int, int] | None = None
    try:
        created_stat = os.fstat(descriptor)
        created_identity = (created_stat.st_dev, created_stat.st_ino)
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            current_stat = os.lstat(path)
            if created_identity == (current_stat.st_dev, current_stat.st_ino):
                path.unlink()
        except OSError:
            pass
        raise


def expected_legacy_tree(
    relative: PurePosixPath,
) -> dict[str, tuple[str, str | None]]:
    prefix = relative.as_posix()
    return {
        path: details
        for path, details in LEGACY_PROVIDER_PROOF.items()
        if path == prefix or path.startswith(prefix + "/")
    }


def apply_external_transaction(
    root: Path,
    writes: Mapping[PurePosixPath, bytes],
    removals: Sequence[PurePosixPath],
    removed_roots: Sequence[PurePosixPath] = (),
    expected: Mapping[PurePosixPath, bytes | None] | None = None,
    prove_legacy: bool = False,
) -> ExternalTransaction:
    affected = sorted(set(writes) | set(removals), key=lambda item: item.as_posix())
    expected = {} if expected is None else expected
    if set(expected) != set(affected):
        raise AdoptionError("transaction observations do not match affected targets")
    snapshots: dict[PurePosixPath, tuple[bytes, int] | None] = {}
    created_directories: list[Path] = []
    backup_root = Path(tempfile.mkdtemp(prefix=".agent-workflow-transaction-", dir=root))
    moved_files: dict[PurePosixPath, Path] = {}
    moved_roots: dict[PurePosixPath, Path] = {}
    written_files: dict[PurePosixPath, bytes] = {}
    transaction = ExternalTransaction(
        snapshots,
        created_directories,
        moved_files,
        moved_roots,
        written_files,
        backup_root,
    )
    try:
        for index, relative in enumerate(removed_roots):
            path = checked_target(root, relative)
            backup = backup_root / f"former-skill-{index}"
            try:
                os.replace(path, backup)
            except OSError as exc:
                raise AdoptionError(
                    f"former skill root changed at lifecycle mutation boundary: {relative}"
                ) from exc
            moved_roots[relative] = backup
            if prove_legacy:
                actual = inspect_legacy_tree(root, relative, captured=backup)
                if actual != expected_legacy_tree(relative):
                    raise AdoptionError(
                        f"former skill root changed at lifecycle mutation boundary: {relative}"
                    )

        for index, relative in enumerate(affected):
            path = checked_target(root, relative)
            expected_bytes = expected[relative]
            if expected_bytes is None:
                snapshots[relative] = None
            else:
                backup = backup_root / f"external-{index}"
                try:
                    os.replace(path, backup)
                except OSError as exc:
                    raise AdoptionError(
                        f"external target changed at lifecycle mutation boundary: {relative}"
                    ) from exc
                moved_files[relative] = backup
                snapshots[relative] = None
                details = os.lstat(backup)
                if not stat.S_ISREG(details.st_mode):
                    raise AdoptionError(
                        f"external target changed type at lifecycle mutation boundary: {relative}"
                    )
                try:
                    captured = backup.read_bytes()
                except OSError as exc:
                    raise AdoptionError(
                        f"cannot read captured external target {relative}: {exc}"
                    ) from exc
                mode = stat.S_IMODE(details.st_mode)
                snapshots[relative] = (captured, mode)
                if captured != expected_bytes:
                    raise AdoptionError(
                        f"external target changed at lifecycle mutation boundary: {relative}"
                    )

            if relative in writes:
                prior = snapshots[relative]
                mode = prior[1] if prior is not None else 0o644
                data = writes[relative]
                exclusive_write(path, data, mode, root, created_directories)
                written_files[relative] = data
    except Exception:
        rollback_external(root, transaction)
        raise
    return transaction


def rollback_external(
    root: Path,
    transaction: ExternalTransaction,
) -> None:
    errors: list[str] = []
    for relative, snapshot in reversed(list(transaction.snapshots.items())):
        path = checked_target(root, relative)
        try:
            if path.exists() or path.is_symlink():
                written = transaction.written_files.get(relative)
                late_change = written is None
                if not late_change:
                    try:
                        late_change = read_regular(root, relative) != written
                    except AdoptionError:
                        late_change = True
                if late_change:
                    backup = transaction.moved_files.pop(relative, None)
                    if backup is not None:
                        backup.unlink()
                    continue
                path.unlink()
            backup = transaction.moved_files.get(relative)
            if backup is not None:
                if path.exists() or path.is_symlink():
                    raise AdoptionError(f"rollback target is occupied: {relative}")
                ensure_parent(path, root, transaction.created_directories)
                os.replace(backup, path)
            elif snapshot is not None:
                raise AdoptionError(f"rollback lacks captured bytes for {relative}")
        except (AdoptionError, OSError) as exc:
            errors.append(f"{relative}: {exc}")
    for relative, backup in reversed(list(transaction.moved_roots.items())):
        path = checked_target(root, relative)
        try:
            if path.exists() or path.is_symlink():
                raise AdoptionError(
                    f"rollback target for former skill is occupied: {relative}"
                )
            ensure_parent(path, root, transaction.created_directories)
            os.replace(backup, path)
        except (AdoptionError, OSError) as exc:
            errors.append(f"{relative}: {exc}")
    for directory in reversed(transaction.created_directories):
        try:
            directory.rmdir()
        except OSError as exc:
            if directory.exists():
                errors.append(f"{directory}: {exc}")
    try:
        transaction.backup_root.rmdir()
    except OSError as exc:
        if transaction.backup_root.exists():
            errors.append(f"{transaction.backup_root}: {exc}")
    if errors:
        raise AdoptionError("rollback could not restore transaction: " + "; ".join(errors))


def cleanup_external_transaction(transaction: ExternalTransaction) -> None:
    try:
        if os.environ.get("AGENT_WORKFLOW_TEST_FAIL_AT") == "cleanup-external":
            raise OSError("injected transaction-backup cleanup failure")
        shutil.rmtree(transaction.backup_root)
    except OSError as exc:
        print(
            "WARNING: committed lifecycle changes but could not remove transaction "
            f"backup {transaction.backup_root}: {exc}",
            file=sys.stderr,
        )


def ensure_durable_state(root: Path) -> bool:
    durable_root = checked_target(root, DURABLE_ROOT)
    if not durable_root.exists():
        durable_root.mkdir(mode=0o755)
        return True
    if durable_root.is_symlink() or not durable_root.is_dir():
        raise AdoptionError(".agent-wayfinder must be a regular non-symlink directory")
    return False


def preflight_durable_state(root: Path) -> None:
    durable_root = checked_target(root, DURABLE_ROOT)
    if durable_root.exists() or durable_root.is_symlink():
        if durable_root.is_symlink() or not durable_root.is_dir():
            raise AdoptionError(
                ".agent-wayfinder must be a regular non-symlink directory"
            )


def preflight_framework_state(root: Path) -> None:
    """Reject unsafe framework entries before any lifecycle mutation."""
    framework = checked_target(root, FRAMEWORK_ROOT)
    try:
        framework_stat = os.lstat(framework)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise AdoptionError(f"cannot inspect .agent-workflow: {exc}") from exc
    if stat.S_ISLNK(framework_stat.st_mode) or not stat.S_ISDIR(
        framework_stat.st_mode
    ):
        raise AdoptionError(".agent-workflow must be a regular non-symlink directory")

    def visit(directory: Path, relative: PurePosixPath) -> None:
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda item: item.name)
        except OSError as exc:
            raise AdoptionError(f"cannot inspect framework directory {relative}: {exc}") from exc
        for entry in entries:
            child = relative / entry.name
            try:
                details = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise AdoptionError(f"cannot inspect framework entry {child}: {exc}") from exc
            if stat.S_ISLNK(details.st_mode):
                raise AdoptionError(f"framework contains a symlink: {child}")
            if stat.S_ISDIR(details.st_mode):
                visit(Path(entry.path), child)
            elif not stat.S_ISREG(details.st_mode):
                raise AdoptionError(f"framework contains a special entry: {child}")

    visit(framework, FRAMEWORK_ROOT)


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
    value = canonical_integrity_value(
        INSTALL_SCHEMA, version, revision, external, composites
    )
    value["integrity_sha256"] = install_state_integrity(
        INSTALL_SCHEMA, version, revision, external, composites
    )
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def make_framework_stage(
    root: Path,
    mappings: Sequence[tuple[PurePosixPath, PurePosixPath]],
    manifest: bytes,
) -> Path:
    stage = Path(tempfile.mkdtemp(prefix=".agent-workflow-stage-", dir=root))
    os.chmod(stage, 0o755)
    try:
        for source, target in mappings:
            if target != FRAMEWORK_ROOT and FRAMEWORK_ROOT in target.parents:
                relative = target.relative_to(FRAMEWORK_ROOT)
                destination = stage.joinpath(*relative.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.chmod(destination.parent, 0o755)
                destination.write_bytes(source_bytes(source))
                os.chmod(destination, 0o644)
        (stage / INSTALL_MANIFEST.name).write_bytes(manifest)
        os.chmod(stage / INSTALL_MANIFEST.name, 0o644)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return stage


def validate_captured_legacy_framework(
    backup: Path,
    manifest_sha256: str,
) -> None:
    expected = {
        "providers.json": FORMER_PROVIDERS_SHA256,
        INSTALL_MANIFEST.name: manifest_sha256,
    }
    for name, expected_digest in expected.items():
        path = backup / name
        try:
            details = os.lstat(path)
        except OSError as exc:
            raise AdoptionError(
                f"former framework proof changed at lifecycle mutation boundary: {name}"
            ) from exc
        if not stat.S_ISREG(details.st_mode):
            raise AdoptionError(
                f"former framework proof changed type at lifecycle mutation boundary: {name}"
            )
        try:
            current = path.read_bytes()
        except OSError as exc:
            raise AdoptionError(
                f"cannot read captured former framework proof {name}: {exc}"
            ) from exc
        if digest(current) != expected_digest:
            raise AdoptionError(
                f"former framework proof changed at lifecycle mutation boundary: {name}"
            )


def validate_captured_framework_tree(backup: Path) -> None:
    try:
        root_stat = os.lstat(backup)
    except OSError as exc:
        raise AdoptionError(
            ".agent-workflow changed at lifecycle mutation boundary"
        ) from exc
    if not stat.S_ISDIR(root_stat.st_mode):
        raise AdoptionError(
            ".agent-workflow changed type at lifecycle mutation boundary"
        )

    def visit(directory: Path, relative: PurePosixPath) -> None:
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda item: item.name)
        except OSError as exc:
            raise AdoptionError(
                f"captured framework changed at lifecycle mutation boundary: {relative}"
            ) from exc
        for entry in entries:
            child = relative / entry.name
            try:
                details = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise AdoptionError(
                    f"captured framework changed at lifecycle mutation boundary: {child}"
                ) from exc
            if stat.S_ISLNK(details.st_mode):
                raise AdoptionError(
                    f"captured framework contains a symlink: {child}"
                )
            if stat.S_ISDIR(details.st_mode):
                visit(Path(entry.path), child)
            elif not stat.S_ISREG(details.st_mode):
                raise AdoptionError(
                    f"captured framework contains a special entry: {child}"
                )

    visit(backup, FRAMEWORK_ROOT)


def capture_framework(
    root: Path,
    backup_prefix: str,
    legacy_manifest_sha256: str | None = None,
) -> Path | None:
    current = checked_target(root, FRAMEWORK_ROOT)
    if current.is_symlink() or (current.exists() and not current.is_dir()):
        raise AdoptionError(".agent-workflow must be a regular non-symlink directory")
    if not current.exists():
        return None
    backup = Path(tempfile.mkdtemp(prefix=backup_prefix, dir=root))
    backup.rmdir()
    os.replace(current, backup)
    try:
        validate_captured_framework_tree(backup)
        if legacy_manifest_sha256 is not None:
            validate_captured_legacy_framework(backup, legacy_manifest_sha256)
    except Exception as original:
        if current.exists() or current.is_symlink():
            raise AdoptionError(
                f"{original}; captured framework remains at {backup} because "
                ".agent-workflow was occupied during rollback"
            ) from original
        os.replace(backup, current)
        raise
    return backup


def swap_framework(
    root: Path,
    stage: Path,
    legacy_manifest_sha256: str | None = None,
) -> Path | None:
    current = checked_target(root, FRAMEWORK_ROOT)
    backup = capture_framework(
        root,
        ".agent-workflow-backup-",
        legacy_manifest_sha256,
    )
    try:
        if current.exists() or current.is_symlink():
            raise AdoptionError(
                ".agent-workflow changed at lifecycle mutation boundary"
            )
        os.replace(stage, current)
    except Exception as original:
        if backup is not None and backup.exists():
            if current.exists() or current.is_symlink():
                raise AdoptionError(
                    f"{original}; captured framework remains at {backup} because "
                    ".agent-workflow was occupied during rollback"
                ) from original
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
    state: InstallState,
) -> tuple[
    dict[PurePosixPath, bytes],
    list[PurePosixPath],
    list[PurePosixPath],
    dict[PurePosixPath, bytes | None],
    dict[str, dict[str, object]],
    dict[str, dict[str, object]],
    list[str],
]:
    require_usable_state(state)
    if state.legacy:
        prove_legacy_provider_installation(root)
    previous_external = state.external_files
    previous_composites = state.composites

    writes: dict[PurePosixPath, bytes] = {}
    removals: list[PurePosixPath] = []
    removed_roots: list[PurePosixPath] = []
    observations: dict[PurePosixPath, bytes | None] = {}
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
            previous_created = (
                bool(previous.get("created"))
                if isinstance(previous, Mapping)
                else None
            )
            if current is None:
                project = b""
                created = previous_created if previous_created is not None else True
            elif has_any_marker(current):
                _managed, project = parse_policy(current)
                created = previous_created if previous_created is not None else False
            else:
                project = current
                created = previous_created if previous_created is not None else False
            desired = compose_policy(data, project)
            if current != desired:
                writes[target] = desired
                observations[target] = current
                actions.append(f"replace managed policy region in {target}")
            next_composites[key] = {"created": created}
            continue

        desired_external.add(key)
        previous = previous_external.get(key)
        legacy_skill = (
            target.parts[0:2] == (".agents", "skills")
            and len(target.parts) >= 3
            and target.parts[2] in RETAINED_LEGACY_SKILLS
        )
        if current is None:
            writes[target] = data
            observations[target] = current
            if isinstance(previous, Mapping):
                created = bool(previous.get("created"))
            else:
                created = True
            actions.append(f"create required external integration {target}")
        elif isinstance(previous, dict):
            created = bool(previous.get("created"))
            if current != data:
                writes[target] = data
                observations[target] = current
                actions.append(f"replace managed external integration {target}")
        elif state.legacy and legacy_skill:
            created = True
            if current != data:
                writes[target] = data
                observations[target] = current
                actions.append(f"replace proven former skill file {target}")
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
            observations[relative] = current
            actions.append(f"remove retired unchanged external integration {relative}")
        else:
            raise AdoptionError(
                "retired external content lacks safe deletion proof: "
                f"{relative}"
            )

    if state.legacy:
        removed_roots = [
            PurePosixPath(".agents/skills") / name
            for name in sorted(REMOVED_LEGACY_SKILLS)
        ]
        actions.extend(f"remove proven former skill {root}" for root in removed_roots)

    return (
        writes,
        removals,
        removed_roots,
        observations,
        next_external,
        next_composites,
        actions,
    )


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
    manifest = read_regular(root, INSTALL_MANIFEST)
    if manifest is None:
        raise AdoptionError("post-check found missing install manifest")
    parsed = parse_json_bytes(manifest, "post-check install manifest")
    parse_current_install_state(parsed)


def inject_test_failure(point: str) -> None:
    if os.environ.get("AGENT_WORKFLOW_TEST_FAIL_AT") == point:
        raise AdoptionError(f"injected lifecycle failure at {point}")


def reconcile(root: Path, dry_run: bool, revision: str, verb: str) -> None:
    version, mappings = load_distribution()
    state = load_install_state(root)
    require_usable_state(state)
    preflight_framework_state(root)
    (
        writes,
        removals,
        removed_roots,
        observations,
        external,
        composites,
        actions,
    ) = plan_reconciliation(root, mappings, state)
    preflight_durable_state(root)
    actions.append("replace reconstructable .agent-workflow with current desired files")
    if not checked_target(root, DURABLE_ROOT).exists():
        actions.append("create empty durable project-state directory .agent-wayfinder")

    if dry_run:
        print(f"{verb.upper()} PLAN {root}")
        for action in actions:
            print(f"- {action}")
        return

    legacy_manifest_sha256 = state.manifest_sha256 if state.legacy else None
    if state.legacy and legacy_manifest_sha256 is None:
        raise AdoptionError("former install manifest observation is missing")
    manifest = install_manifest_bytes(version, revision, external, composites)
    stage = make_framework_stage(root, mappings, manifest)
    durable_created = False
    transaction: ExternalTransaction | None = None
    backup: Path | None = None
    framework_swapped = False
    try:
        transaction = apply_external_transaction(
            root,
            writes,
            removals,
            removed_roots,
            observations,
            state.legacy,
        )
        durable_created = ensure_durable_state(root)
        inject_test_failure("after-external")
        backup = swap_framework(root, stage, legacy_manifest_sha256)
        framework_swapped = True
        inject_test_failure("after-framework")
        verify_reconciled(root, mappings)
        if backup is not None and legacy_manifest_sha256 is not None:
            validate_captured_legacy_framework(backup, legacy_manifest_sha256)
    except Exception as original:
        rollback_errors: list[str] = []
        if framework_swapped:
            try:
                restore_framework(root, backup)
            except (AdoptionError, OSError) as exc:
                rollback_errors.append(f"framework: {exc}")
        if transaction is not None:
            try:
                rollback_external(root, transaction)
            except AdoptionError as exc:
                rollback_errors.append(f"external: {exc}")
        rollback_created_durable_state(root, durable_created)
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
        if rollback_errors:
            raise AdoptionError(
                f"{original}; rollback incomplete: {'; '.join(rollback_errors)}"
            ) from original
        raise
    if backup is not None:
        try:
            shutil.rmtree(backup)
        except OSError as exc:
            print(
                "WARNING: committed lifecycle changes but could not remove framework "
                f"backup {backup}: {exc}",
                file=sys.stderr,
            )
    if transaction is not None:
        cleanup_external_transaction(transaction)
    print(f"OK: Agent Workflow {verb} completed; current framework state reconciled.")
    print("OK: Durable project state preserved under .agent-wayfinder/.")


def status(root: Path, revision: str) -> int:
    version, mappings = load_distribution()
    state = load_install_state(root)
    problems: list[str] = []
    conflicts: list[str] = []

    if state.kind is InstallStateKind.INVALID:
        conflicts.append(f"CONFLICT: invalid install state: {state.error}")
    else:
        try:
            preflight_framework_state(root)
            writes, removals, removed_roots, _observations, external, composites, _actions = (
                plan_reconciliation(root, mappings, state)
            )
        except AdoptionError as exc:
            conflicts.append(f"CONFLICT: {exc}")
        else:
            problems.extend(
                f"REPAIR: lifecycle target requires reconciliation: {target}"
                for target in sorted(writes, key=lambda item: item.as_posix())
            )
            problems.extend(
                f"REPAIR: retired external target is safely removable: {target}"
                for target in removals
            )
            problems.extend(
                f"REPAIR: exact former skill is ready for transition: {target}"
                for target in removed_roots
            )
            if (
                state.kind is InstallStateKind.VALID
                and not state.legacy
                and (
                    dict(state.external_files) != external
                    or dict(state.composites) != composites
                )
            ):
                problems.append("REPAIR: install manifest evidence requires reconciliation")

    framework = checked_target(root, FRAMEWORK_ROOT)
    desired_internal = {INSTALL_MANIFEST.as_posix()}
    desired_internal.update(
        target.as_posix()
        for _source, target in mappings
        if target != FRAMEWORK_ROOT and FRAMEWORK_ROOT in target.parents
    )
    desired_directories = {FRAMEWORK_ROOT.as_posix()}
    for value in desired_internal:
        path = PurePosixPath(value)
        for parent in path.parents:
            if parent == FRAMEWORK_ROOT or FRAMEWORK_ROOT in parent.parents:
                desired_directories.add(parent.as_posix())
    if not framework.exists() and not framework.is_symlink():
        if state.kind is InstallStateKind.ABSENT:
            problems.append("REPAIR: Agent Workflow is not installed")
        elif state.kind is not InstallStateKind.INVALID:
            conflicts.append("CONFLICT: managed framework directory is absent")
    elif framework.is_symlink() or not framework.is_dir():
        conflicts.append("CONFLICT: .agent-workflow is not a regular directory")
    else:
        for source, target in mappings:
            if target == FRAMEWORK_ROOT or FRAMEWORK_ROOT not in target.parents:
                continue
            try:
                current = read_regular(root, target)
            except AdoptionError as exc:
                conflicts.append(f"CONFLICT: {exc}")
                continue
            if current != source_bytes(source):
                problems.append(f"REPAIR: stale framework target {target}")
        for path in framework.rglob("*"):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                conflicts.append(f"CONFLICT: framework contains a symlink: {relative}")
            elif not path.is_file() and not path.is_dir():
                conflicts.append(
                    f"CONFLICT: framework contains a special entry: {relative}"
                )
            elif path.is_file() and relative not in desired_internal:
                problems.append(
                    f"REPAIR: obsolete reconstructable framework file {relative}"
                )
            elif path.is_dir() and relative not in desired_directories:
                problems.append(
                    f"REPAIR: obsolete reconstructable framework directory {relative}"
                )

    if state.kind is InstallStateKind.VALID and not state.legacy:
        if state.framework_version != version:
            problems.append(
                "REPAIR: installed framework version differs from current package"
            )
        if state.source_revision != revision:
            problems.append(
                "REPAIR: installed source revision differs from requested source"
            )
    elif state.legacy:
        problems.append("REPAIR: exact pinned-main installation requires transition")

    durable = checked_target(root, DURABLE_ROOT)
    if not durable.exists() and not durable.is_symlink():
        problems.append("REPAIR: durable project-state directory is absent")
    elif durable.is_symlink() or not durable.is_dir():
        conflicts.append("CONFLICT: .agent-wayfinder is not a regular directory")

    print(f"STATUS {root}")
    print(f"Current package version: {version}")
    for message in dict.fromkeys(problems + conflicts):
        print(message)
    if conflicts:
        print("Agent Workflow: unsafe/conflict")
        return 2
    if problems:
        print("Agent Workflow: repairable")
        return 1
    print("Agent Workflow: healthy")
    print("OK: No lifecycle action is required.")
    return 0


def remove(root: Path, dry_run: bool) -> None:
    _version, mappings = load_distribution()
    state = load_install_state(root)
    require_usable_state(state)
    preflight_framework_state(root)
    preflight_durable_state(root)
    external_state = state.external_files
    composite_state = state.composites
    writes: dict[PurePosixPath, bytes] = {}
    removals: list[PurePosixPath] = []
    observations: dict[PurePosixPath, bytes | None] = {}
    actions: list[str] = []
    removed_roots: list[PurePosixPath] = []

    composite_targets = {
        target for _source, target in mappings if target in COMPOSITE_PATHS
    }
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
            observations[relative] = current
            actions.append(f"remove framework-created composite policy {relative}")
        else:
            writes[relative] = project
            observations[relative] = current
            actions.append(
                f"remove managed policy region and preserve project bytes in {relative}"
            )

    for key, details in external_state.items():
        if not isinstance(details, dict):
            continue
        relative = safe_relative(key)
        current = read_regular(root, relative)
        if current is None:
            continue
        if details.get("created") is True and digest(current) == details.get("sha256"):
            removals.append(relative)
            observations[relative] = current
            actions.append(
                f"remove unchanged framework-created external integration {relative}"
            )
        else:
            actions.append(
                f"preserve pre-existing or changed external content {relative}"
            )

    if state.legacy:
        prove_legacy_provider_installation(root)
        removed_roots = [
            PurePosixPath(".agents/skills") / name
            for name in sorted(LEGACY_PROVIDER_SKILLS)
        ]
        actions.extend(f"remove proven former skill {path}" for path in removed_roots)

    framework = checked_target(root, FRAMEWORK_ROOT)
    if framework.exists() or framework.is_symlink():
        if framework.is_symlink() or not framework.is_dir():
            raise AdoptionError(
                ".agent-workflow must be a regular non-symlink directory"
            )
        actions.append("remove reconstructable .agent-workflow directory")
    actions.append("preserve .agent-wayfinder and every file below it")

    if dry_run:
        print(f"REMOVE PLAN {root}")
        for action in actions:
            print(f"- {action}")
        return

    legacy_manifest_sha256 = state.manifest_sha256 if state.legacy else None
    if state.legacy and legacy_manifest_sha256 is None:
        raise AdoptionError("former install manifest observation is missing")
    transaction: ExternalTransaction | None = None
    backup: Path | None = None
    try:
        transaction = apply_external_transaction(
            root,
            writes,
            removals,
            removed_roots,
            observations,
            state.legacy,
        )
        backup = capture_framework(
            root,
            ".agent-workflow-remove-",
            legacy_manifest_sha256,
        )
        if backup is not None and legacy_manifest_sha256 is not None:
            validate_captured_legacy_framework(backup, legacy_manifest_sha256)
    except Exception as original:
        rollback_errors: list[str] = []
        if backup is not None and backup.exists():
            if framework.exists() or framework.is_symlink():
                rollback_errors.append(
                    "framework: rollback target is occupied; captured framework "
                    f"remains at {backup}"
                )
            else:
                try:
                    os.replace(backup, framework)
                except OSError as exc:
                    rollback_errors.append(f"framework: {exc}")
        if transaction is not None:
            try:
                rollback_external(root, transaction)
            except AdoptionError as exc:
                rollback_errors.append(f"external: {exc}")
        if rollback_errors:
            raise AdoptionError(
                f"{original}; rollback incomplete: {'; '.join(rollback_errors)}"
            ) from original
        raise
    if backup is not None:
        try:
            shutil.rmtree(backup)
        except OSError as exc:
            print(
                "WARNING: removal completed but framework backup cleanup failed at "
                f"{backup}: {exc}",
                file=sys.stderr,
            )
    if transaction is not None:
        cleanup_external_transaction(transaction)
    print("OK: Reconstructable Agent Workflow files removed.")
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
            return status(root, revision)
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
