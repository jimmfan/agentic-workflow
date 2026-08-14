#!/usr/bin/env python3
"""Install and verify curated upstream skills through GitHub CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DECLARATION_PATH = PACKAGE_ROOT / "payload" / "ai-workflow" / "providers.json"
STATE_RELATIVE = PurePosixPath(".ai-workflow/provider-state.json")
SKILLS_RELATIVE = PurePosixPath(".agents/skills")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
SHA = re.compile(r"[0-9a-f]{40}")
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MINIMUM_PYTHON = (3, 11)
REMOVAL_QUARANTINE_PREFIX = ".ai-workflow-provider-remove-"
UPDATE_QUARANTINE_PREFIX = ".ai-workflow-provider-update-"
INVOCATION_MODES = {"implicit", "unavailable", "user-only"}
HOSTS = {
    "claude-code": {
        "availability": "unavailable",
        "discovery": ".claude/skills",
        "explicit_prefix": "/",
        "invocation_source": "SKILL.md:disable-model-invocation",
    },
    "codex": {
        "availability": "available",
        "discovery": ".agents/skills",
        "explicit_prefix": "$",
        "invocation_source": "agents/openai.yaml:policy.allow_implicit_invocation",
    },
    "github-copilot": {
        "availability": "available",
        "discovery": ".agents/skills",
        "explicit_prefix": "/",
        "invocation_source": "SKILL.md:disable-model-invocation",
    },
}


class ProviderError(RuntimeError):
    """A provider declaration, dependency, or lifecycle invariant failed."""


def require_supported_python() -> None:
    if sys.version_info < MINIMUM_PYTHON:
        found = ".".join(str(part) for part in sys.version_info[:3])
        raise ProviderError(f"Python 3.11 or newer is required; found Python {found}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_relative(raw: object, label: str) -> PurePosixPath:
    if not isinstance(raw, str):
        raise ProviderError(f"{label} must be a string")
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or ".." in path.parts or "." in path.parts or "\\" in raw:
        raise ProviderError(f"unsafe {label}: {raw!r}")
    return path


def target_path(root: Path, relative: PurePosixPath) -> Path:
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ProviderError(f"refusing to follow target symlink: {current}")
    try:
        current.parent.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ProviderError(f"target escapes project root: {relative}") from exc
    return current


def parse_version(raw: str, label: str) -> Tuple[int, int, int]:
    match = VERSION.fullmatch(raw.removeprefix("v"))
    if match is None:
        raise ProviderError(f"{label} must be a semantic version: {raw!r}")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def load_json(path: Path, label: str) -> MutableMapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProviderError(f"missing {label}: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderError(f"cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProviderError(f"{label} must be a JSON object: {path}")
    return value


def load_declaration() -> Tuple[Mapping[str, object], List[Mapping[str, object]]]:
    raw = load_json(DECLARATION_PATH, "provider declaration")
    if set(raw) != {"schema_version", "capabilities", "configuration", "hosts", "provider"} or raw.get(
        "schema_version"
    ) != 4:
        raise ProviderError("provider declaration has unknown fields or an unsupported schema")
    capabilities = raw.get("capabilities")
    configuration = raw.get("configuration")
    hosts = raw.get("hosts")
    provider = raw.get("provider")
    if not isinstance(capabilities, dict) or not capabilities:
        raise ProviderError("provider declaration needs a non-empty capabilities object")
    if hosts != HOSTS:
        raise ProviderError("provider declaration has incompatible host discovery or invocation metadata")
    if not isinstance(configuration, dict) or not configuration:
        raise ProviderError("provider declaration needs a non-empty configuration object")
    configuration_paths = set()
    configuration_references = []
    for name, item in configuration.items():
        if not isinstance(name, str) or SKILL_NAME.fullmatch(name) is None:
            raise ProviderError(f"invalid provider configuration name: {name!r}")
        if not isinstance(item, dict) or set(item) not in (
            {"path", "provisioned_by"},
            {"enabled_by", "path", "provisioned_by"},
        ):
            raise ProviderError(f"provider configuration {name} has invalid fields")
        path = safe_relative(item.get("path"), f"path for provider configuration {name}").as_posix()
        if path in configuration_paths:
            raise ProviderError(f"duplicate provider configuration path: {path}")
        configuration_paths.add(path)
        provisioned_by = item.get("provisioned_by")
        if not isinstance(provisioned_by, str) or SKILL_NAME.fullmatch(provisioned_by) is None:
            raise ProviderError(f"provider configuration {name} has invalid provisioned_by")
        enabled_by = item.get("enabled_by")
        if enabled_by is not None and (
            not isinstance(enabled_by, str) or SKILL_NAME.fullmatch(enabled_by) is None
        ):
            raise ProviderError(f"provider configuration {name} has invalid enabled_by")
        configuration_references.append((name, provisioned_by, enabled_by))
    if not isinstance(provider, dict) or set(provider) != {
        "minimum_gh_version",
        "name",
        "repository",
        "skills",
        "version",
    }:
        raise ProviderError("provider declaration has invalid provider fields")
    for field in ("minimum_gh_version", "name", "repository", "version"):
        if not isinstance(provider.get(field), str) or not provider[field]:
            raise ProviderError(f"provider {field} must be a non-empty string")
    parse_version(str(provider["minimum_gh_version"]), "minimum_gh_version")
    parse_version(str(provider["version"]), "provider version")
    repository = str(provider["repository"])
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None:
        raise ProviderError(f"invalid GitHub repository: {repository!r}")
    skills = provider.get("skills")
    if not isinstance(skills, list) or not skills:
        raise ProviderError("provider skills must be a non-empty array")
    checked: List[Mapping[str, object]] = []
    names = set()
    paths = set()
    for item in skills:
        if not isinstance(item, dict) or set(item) != {
            "invocation",
            "name",
            "path",
            "requires_configuration",
        }:
            raise ProviderError(
                "each provider skill needs invocation, name, path, and requirements"
            )
        name = item.get("name")
        if not isinstance(name, str) or SKILL_NAME.fullmatch(name) is None:
            raise ProviderError(f"invalid provider skill name: {name!r}")
        path = safe_relative(item.get("path"), f"provider path for {name}").as_posix()
        invocation = item.get("invocation")
        if not isinstance(invocation, dict) or set(invocation) != set(HOSTS):
            raise ProviderError(f"provider skill {name} invocation must cover every declared host")
        for host, mode in invocation.items():
            if mode not in INVOCATION_MODES:
                raise ProviderError(f"provider skill {name} has invalid {host} invocation mode: {mode!r}")
            availability = HOSTS[host]["availability"]
            if availability == "unavailable" and mode != "unavailable":
                raise ProviderError(f"provider skill {name} must be unavailable on {host}")
            if availability == "available" and mode == "unavailable":
                raise ProviderError(f"provider skill {name} cannot be unavailable on {host}")
        requirements = item.get("requires_configuration")
        if not isinstance(requirements, list) or any(not isinstance(value, str) for value in requirements):
            raise ProviderError(f"provider skill {name} requires_configuration must be an array of names")
        if requirements != sorted(set(requirements)):
            raise ProviderError(f"provider skill {name} configuration requirements must be unique and sorted")
        unknown_requirements = sorted(set(requirements) - set(configuration))
        if unknown_requirements:
            raise ProviderError(
                f"provider skill {name} requires unknown configuration: {', '.join(unknown_requirements)}"
            )
        if name in names or path in paths:
            raise ProviderError(f"duplicate provider skill name or path: {name}")
        names.add(name)
        paths.add(path)
        checked.append(item)
    for configuration_name, provisioned_by, enabled_by in configuration_references:
        if provisioned_by not in names:
            raise ProviderError(
                f"provider configuration {configuration_name} is provisioned by unknown skill {provisioned_by}"
            )
        if enabled_by is not None and enabled_by not in names:
            raise ProviderError(
                f"provider configuration {configuration_name} is enabled by unknown skill {enabled_by}"
            )
    for capability, skill_name in capabilities.items():
        if not isinstance(capability, str) or not capability or skill_name not in names:
            raise ProviderError(f"capability {capability!r} selects an unknown provider skill")
    return provider, checked


def frontmatter(path: Path) -> Tuple[Mapping[str, str], Mapping[str, str]]:
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ProviderError(f"cannot read installed skill metadata at {path}: {exc}") from exc
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ProviderError(f"installed skill lacks valid frontmatter: {path}")
    block = text[4 : text.index("\n---\n", 4)]
    top: Dict[str, str] = {}
    metadata: Dict[str, str] = {}
    in_metadata = False
    for line in block.splitlines():
        if not line.startswith((" ", "\t")):
            in_metadata = line.strip() == "metadata:"
            if ":" in line and not in_metadata:
                key, value = line.split(":", 1)
                top[key.strip()] = value.strip().strip("\"'")
        elif in_metadata and ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip("\"'")
    return top, metadata


def metadata_boolean(value: Optional[str], label: str, *, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized not in {"false", "true"}:
        raise ProviderError(f"{label} must be true or false, found {value!r}")
    return normalized == "true"


def openai_allows_implicit_invocation(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ProviderError(f"cannot read installed Codex invocation metadata at {path}: {exc}") from exc
    parent = re.compile(r"^policy:\s*(?:#.*)?$")
    field = re.compile(r"^\s+allow_implicit_invocation:\s*(true|false)\s*(?:#.*)?$", re.IGNORECASE)
    malformed_field = re.compile(r"^\s+allow_implicit_invocation\s*:")
    values: List[str] = []
    in_policy = False
    for line in text.splitlines():
        indentation = line[: len(line) - len(line.lstrip())]
        if "\t" in indentation:
            raise ProviderError(f"installed Codex invocation metadata uses unsupported tab indentation: {path}")
        if line and not indentation:
            in_policy = parent.fullmatch(line) is not None
            continue
        if not in_policy or not line.strip() or line.lstrip().startswith("#"):
            continue
        match = field.fullmatch(line)
        if match is not None:
            values.append(match.group(1))
        elif malformed_field.match(line) is not None:
            raise ProviderError(
                f"policy.allow_implicit_invocation must be true or false in installed metadata: {path}"
            )
    if len(values) > 1:
        raise ProviderError(f"installed Codex invocation metadata repeats policy.allow_implicit_invocation: {path}")
    return metadata_boolean(
        values[0] if values else None,
        "policy.allow_implicit_invocation",
        default=True,
    )


def verify_invocation_metadata(
    directory: Path,
    skill: Mapping[str, object],
    frontmatter_values: Mapping[str, str],
) -> None:
    name = str(skill["name"])
    declared = skill["invocation"]
    if not isinstance(declared, Mapping):
        raise ProviderError(f"provider skill {name} has invalid invocation declaration")
    for host, host_contract in HOSTS.items():
        expected = declared.get(host)
        if host_contract["availability"] == "unavailable":
            actual = "unavailable"
        elif host == "codex":
            actual = (
                "implicit"
                if openai_allows_implicit_invocation(directory / "agents/openai.yaml")
                else "user-only"
            )
        elif host == "github-copilot":
            disabled = metadata_boolean(
                frontmatter_values.get("disable-model-invocation"),
                "disable-model-invocation",
                default=False,
            )
            actual = "user-only" if disabled else "implicit"
        else:  # The declaration is validated against HOSTS before installed skills are inspected.
            raise ProviderError(f"unsupported provider host: {host}")
        if actual != expected:
            raise ProviderError(
                f"provider skill {name} has incompatible {host} invocation: "
                f"expected {expected!r}, found {actual!r} from {host_contract['invocation_source']}"
            )


def skill_directory(root: Path, name: str) -> Path:
    return target_path(root, SKILLS_RELATIVE / name)


def directory_inventory(directory: Path) -> Tuple[List[str], List[str]]:
    if directory.is_symlink() or not directory.is_dir():
        raise ProviderError(f"provider skill must be a regular directory: {directory}")
    files = []
    directories = []
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ProviderError(f"provider skill contains a symlink: {path}")
        if path.is_dir():
            directories.append(path.relative_to(directory).as_posix())
            continue
        if not path.is_file():
            raise ProviderError(f"provider skill contains a special entry: {path}")
        files.append(path.relative_to(directory).as_posix())
    return sorted(files), sorted(directories)


def directory_files(directory: Path) -> List[str]:
    files, _directories = directory_inventory(directory)
    return files


def implied_directories(files: Iterable[str]) -> List[str]:
    directories = set()
    for relative in files:
        parent = PurePosixPath(relative).parent
        while parent.parts:
            directories.add(parent.as_posix())
            parent = parent.parent
    return sorted(directories)


def verify_skill(
    root: Path,
    provider: Mapping[str, object],
    skill: Mapping[str, object],
) -> Mapping[str, str]:
    name = str(skill["name"])
    directory = skill_directory(root, name)
    actual_files, actual_directories = directory_inventory(directory)
    if "SKILL.md" not in actual_files:
        raise ProviderError(f"provider skill {name} lacks SKILL.md")
    if actual_directories != implied_directories(actual_files):
        raise ProviderError(f"provider skill {name} contains empty or unexpected directories")
    top, metadata = frontmatter(directory / "SKILL.md")
    expected_metadata = {
        "github-path": str(skill["path"]),
        "github-pinned": str(provider["version"]),
        "github-ref": f"refs/tags/{provider['version']}",
        "github-repo": f"https://github.com/{provider['repository']}",
    }
    if top.get("name") != name:
        raise ProviderError(f"provider skill name does not match its directory: {name}")
    if any(metadata.get(key) != value for key, value in expected_metadata.items()):
        raise ProviderError(
            f"provider skill {name} has incompatible GitHub source metadata"
        )
    verify_invocation_metadata(directory, skill, top)
    return {relative: sha256(directory / relative) for relative in actual_files}


def find_gh(provider: Mapping[str, object]) -> Path:
    minimum_text = str(provider["minimum_gh_version"])
    command = shutil.which("gh")
    if command is None:
        raise ProviderError(
            f"GitHub CLI {minimum_text} or newer with `gh skill` is required; install or update gh, "
            "verify with `gh --version` and `gh skill --help`, then rerun this command"
        )
    executable = Path(command).resolve()
    result = subprocess.run([str(executable), "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        raise ProviderError(f"cannot run GitHub CLI at {executable}: {result.stderr.strip()}")
    match = re.search(r"gh version ([0-9]+\.[0-9]+\.[0-9]+)", result.stdout)
    if match is None:
        raise ProviderError(f"cannot determine GitHub CLI version from: {result.stdout.strip()!r}")
    minimum = parse_version(minimum_text, "minimum_gh_version")
    if parse_version(match.group(1), "GitHub CLI version") < minimum:
        raise ProviderError(
            f"GitHub CLI {provider['minimum_gh_version']} or newer is required; found {match.group(1)} at {command}"
        )
    help_result = subprocess.run(
        [str(executable), "skill", "install", "--help"], capture_output=True, text=True
    )
    if help_result.returncode != 0 or "--pin" not in help_result.stdout or "--scope" not in help_result.stdout:
        raise ProviderError(
            f"GitHub CLI at {executable} does not provide the required gh skill install interface"
        )
    auth_result = subprocess.run(
        [str(executable), "auth", "status", "--hostname", "github.com"],
        capture_output=True,
        text=True,
    )
    if auth_result.returncode != 0:
        raise ProviderError(
            "an authenticated GitHub CLI session is required to install the curated provider set reliably; "
            "run `gh auth login --hostname github.com --web`, verify with "
            "`gh auth status --hostname github.com`, then rerun this command (automation may set GH_TOKEN)"
        )
    return executable


def run_gh_install(
    gh: Path,
    root: Path,
    provider: Mapping[str, object],
    skill: Mapping[str, object],
    *,
    directory: Optional[Path] = None,
) -> None:
    command = [
        str(gh),
        "skill",
        "install",
        str(provider["repository"]),
        str(skill["path"]),
        "--pin",
        str(provider["version"]),
    ]
    if directory is None:
        command.extend(("--scope", "project", "--agent", "codex"))
    else:
        command.extend(("--dir", str(directory)))
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        detail = "\n".join(value.strip() for value in (result.stdout, result.stderr) if value.strip())
        raise ProviderError(f"gh skill install failed for {skill['name']}: {detail}")
    print(f"installed pinned upstream skill {skill['name']} from {provider['repository']}@{provider['version']}")


def atomic_json(path: Path, value: Mapping[str, object]) -> None:
    parent = path.parent
    if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
        raise ProviderError(f"provider state parent must be a regular directory: {parent}")
    parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as opened:
            json.dump(value, opened, indent=2, sort_keys=True)
            opened.write("\n")
            opened.flush()
            os.fsync(opened.fileno())
        temporary_path.chmod(0o644)
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def state_value(
    provider: Mapping[str, object],
    records: Mapping[str, Mapping[str, object]],
) -> Mapping[str, object]:
    return {
        "provider": {
            "name": provider["name"],
            "repository": provider["repository"],
            "version": provider["version"],
        },
        "schema_version": 2,
        "skills": dict(sorted(records.items())),
    }


def load_state(root: Path) -> MutableMapping[str, object]:
    path = target_path(root, STATE_RELATIVE)
    state = load_json(path, "provider state")
    schema = state.get("schema_version")
    if set(state) != {"provider", "schema_version", "skills"} or schema not in {1, 2}:
        raise ProviderError("provider state has unknown fields or an unsupported schema")
    provider = state.get("provider")
    skills = state.get("skills")
    expected_provider_fields = (
        {"name", "repository", "revision", "version"}
        if schema == 1
        else {"name", "repository", "version"}
    )
    if not isinstance(provider, dict) or set(provider) != expected_provider_fields:
        raise ProviderError("provider state has invalid provider fields")
    if (
        not isinstance(provider.get("name"), str)
        or not isinstance(provider.get("repository"), str)
        or re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", str(provider.get("repository"))) is None
        or not isinstance(provider.get("version"), str)
        or (
            schema == 1
            and (
                not isinstance(provider.get("revision"), str)
                or SHA.fullmatch(str(provider.get("revision"))) is None
            )
        )
    ):
        raise ProviderError("provider state has invalid provider identity")
    parse_version(str(provider["version"]), "provider state version")
    if not isinstance(skills, dict):
        raise ProviderError("provider state skills must be an object")
    for name, record in skills.items():
        if (
            not isinstance(name, str)
            or SKILL_NAME.fullmatch(name) is None
            or not isinstance(record, dict)
            or set(record)
            != ({"files", "origin", "path", "tree_sha"} if schema == 1 else {"files", "origin", "path"})
        ):
            raise ProviderError(f"provider state has invalid record for {name}")
        if record.get("origin") not in {
            "created",
            "preexisting-compatible",
            "reconstructed",
        }:
            raise ProviderError(f"provider state has invalid origin for {name}")
        safe_relative(record.get("path"), f"provider state path for {name}")
        if schema == 1 and (
            not isinstance(record.get("tree_sha"), str)
            or SHA.fullmatch(str(record.get("tree_sha"))) is None
        ):
            raise ProviderError(f"provider state has invalid tree SHA for {name}")
        if not isinstance(record.get("files"), dict) or not all(
            isinstance(key, str)
            and safe_relative(key, f"provider state file for {name}")
            and isinstance(value, str)
            and re.fullmatch(r"[0-9a-f]{64}", value)
            for key, value in record["files"].items()
        ):
            raise ProviderError(f"provider state has invalid file checksums for {name}")
    return state


def recorded_checksum_conflicts(
    root: Path,
    name: str,
    record: Mapping[str, object],
) -> List[str]:
    """Return paths that differ from the bytes recorded when the provider was installed."""
    directory = skill_directory(root, name)
    expected = record.get("files")
    if not isinstance(expected, dict):
        return [f"provider state for {name} lacks recorded file checksums"]
    try:
        actual_files, actual_directories = directory_inventory(directory)
    except ProviderError as error:
        return [str(error)]
    conflicts: List[str] = []
    expected_files = sorted(expected)
    expected_directories = implied_directories(expected_files)
    for relative in sorted(set(expected_files) - set(actual_files)):
        conflicts.append(f"  .agents/skills/{name}/{relative} (missing)")
    for relative in sorted(set(actual_files) - set(expected_files)):
        conflicts.append(f"  .agents/skills/{name}/{relative} (unexpected)")
    for relative in sorted(set(actual_files) & set(expected_files)):
        actual = sha256(directory / relative)
        if actual != expected[relative]:
            conflicts.append(f"  .agents/skills/{name}/{relative}")
    for relative in sorted(set(expected_directories) - set(actual_directories)):
        conflicts.append(f"  .agents/skills/{name}/{relative}/ (expected directory is missing)")
    for relative in sorted(set(actual_directories) - set(expected_directories)):
        conflicts.append(f"  .agents/skills/{name}/{relative}/ (unexpected directory)")
    return conflicts


def existing_parent_directories(root: Path, paths: Sequence[Path]) -> set[Path]:
    existing = {root}
    for path in paths:
        current = path.parent
        while current != root:
            if current.exists() or current.is_symlink():
                existing.add(current)
            current = current.parent
    return existing


def remove_created_empty_parents(
    path: Path,
    root: Path,
    preexisting_directories: set[Path],
) -> None:
    current = path.parent
    while current != root and current != root.parent:
        if current in preexisting_directories:
            return
        try:
            current.rmdir()
        except OSError:
            return
        current = current.parent


def remove_tree(directory: Path, root: Path) -> None:
    if directory.is_symlink() or not directory.is_dir():
        raise ProviderError(f"refusing to remove non-directory provider path: {directory}")
    directory.resolve().relative_to(root.resolve())
    shutil.rmtree(directory)


def verify_quarantined_removal(moved: Sequence[Tuple[Path, Path]]) -> None:
    """Confirm every removal target moved wholly into its reversible quarantine."""
    for original, quarantined in moved:
        if original.exists() or original.is_symlink():
            raise ProviderError(f"provider removal target remained active after quarantine: {original}")
        if not quarantined.exists() and not quarantined.is_symlink():
            raise ProviderError(f"provider removal quarantine is missing staged target: {quarantined}")


def rename_quarantined_path(source: Path, destination: Path) -> None:
    source.replace(destination)


def quarantine_provider_removal(root: Path, removals: Sequence[Path], state_path: Path) -> None:
    """Remove provider paths through same-filesystem renames with transactional rollback."""
    retained = sorted(root.glob(f"{REMOVAL_QUARANTINE_PREFIX}*"))
    if retained:
        raise ProviderError(
            "a retained provider-removal quarantine blocks another removal; inspect and remove "
            + ", ".join(str(path) for path in retained)
        )
    transaction = Path(tempfile.mkdtemp(prefix=REMOVAL_QUARANTINE_PREFIX, dir=root))
    quarantine = transaction / "skills"
    quarantine.mkdir()
    planned = [(directory, quarantine / directory.name) for directory in removals]
    planned.append((state_path, transaction / state_path.name))
    moved: List[Tuple[Path, Path]] = []
    try:
        transaction_device = transaction.stat().st_dev
        for original, _quarantined in planned:
            if original.stat().st_dev != transaction_device:
                raise ProviderError(
                    f"provider removal target is not on the project quarantine filesystem: {original}"
                )
        for original, quarantined in planned:
            rename_quarantined_path(original, quarantined)
            moved.append((original, quarantined))
        verify_quarantined_removal(moved)
    except BaseException as error:
        rollback_errors = []
        for original, quarantined in reversed(moved):
            try:
                if original.exists() or original.is_symlink():
                    raise ProviderError(f"rollback target already exists: {original}")
                if not quarantined.exists() and not quarantined.is_symlink():
                    raise ProviderError(f"rollback source is missing: {quarantined}")
                rename_quarantined_path(quarantined, original)
            except BaseException as rollback_error:
                rollback_errors.append(f"{original}: {rollback_error}")
        if not rollback_errors:
            try:
                shutil.rmtree(transaction)
            except BaseException as cleanup_error:
                rollback_errors.append(f"quarantine cleanup: {cleanup_error}")
        if rollback_errors:
            raise ProviderError(
                f"provider removal failed and rollback also failed; quarantine retained at "
                f"{transaction}: {error}; "
                + "; ".join(rollback_errors)
            ) from error
        raise

    try:
        shutil.rmtree(transaction)
    except OSError as error:
        print(
            "WARNING: provider removal committed, but quarantine cleanup failed; "
            f"inspect and remove {transaction} before a future provider removal: {error}",
            file=sys.stderr,
        )

def checksums_match(root: Path, name: str, record: Mapping[str, object]) -> bool:
    directory = skill_directory(root, name)
    try:
        actual_files, actual_directories = directory_inventory(directory)
    except ProviderError:
        return False
    expected = record["files"]
    if (
        not isinstance(expected, dict)
        or actual_files != sorted(expected)
        or actual_directories != implied_directories(actual_files)
    ):
        return False
    return all(sha256(directory / relative) == expected[relative] for relative in actual_files)


def cleanup_provider_staging(transaction: Path) -> None:
    """Remove validated staging before committing target ownership state."""
    shutil.rmtree(transaction)


def command_install(
    root: Path,
    dry_run: bool,
    *,
    commit_callback: Optional[Callable[[], None]] = None,
    reinstall: bool = False,
) -> None:
    provider, skills = load_declaration()
    state_path = target_path(root, STATE_RELATIVE)
    if state_path.exists() or state_path.is_symlink():
        if command_status(root, verbose=False):
            if commit_callback is not None:
                commit_callback()
            print(f"✓ Upstream provider {provider['repository']}@{provider['version']} is already compatible.")
            return
        raise ProviderError("provider state already exists but dependencies differ; run status or update")

    collisions = []
    for skill in skills:
        name = str(skill["name"])
        destination = skill_directory(root, name)
        if destination.exists() or destination.is_symlink():
            collisions.append(name)
    if collisions:
        if not reinstall:
            raise ProviderError(
                "provider install preflight found unowned directories; no provider files were changed:\n"
                + "\n".join(
                    f".agents/skills/{name} already exists and is not known to be managed "
                    "by Agentic Workflow. Refusing to overwrite it."
                    for name in collisions
                )
            )
        expected_names = {str(skill["name"]) for skill in skills}
        if set(collisions) != expected_names:
            raise ProviderError(
                "framework reinstall found only part of the declared provider skill set; "
                "restore or reconcile .agents/skills before retrying"
            )
        recovered_records: Dict[str, Mapping[str, object]] = {}
        for skill in skills:
            name = str(skill["name"])
            try:
                files = verify_skill(root, provider, skill)
            except ProviderError as error:
                raise ProviderError(
                    f"framework reinstall cannot validate existing provider skill {name}: {error}"
                ) from error
            recovered_records[name] = {
                "files": files,
                "origin": "reconstructed",
                "path": skill["path"],
            }
        if dry_run:
            print(f"PROVIDERS REINSTALL DRY RUN for {root}")
            print(
                f"  - reconstruct provider ownership state for {len(skills)} compatible skills"
            )
            print("  - preserve reconstructed skills on later removal")
            print("No provider files changed.")
            return
        try:
            atomic_json(state_path, state_value(provider, recovered_records))
            if not command_status(root, verbose=False):
                raise ProviderError("post-reinstall provider verification failed")
            if commit_callback is not None:
                commit_callback()
        except BaseException:
            state_path.unlink(missing_ok=True)
            raise
        print(
            "✓ Provider ownership state reconstructed from compatible skills; "
            "the skills will be preserved on removal."
        )
        return
    new_destinations = [skill_directory(root, str(skill["name"])) for skill in skills]
    rollback_paths = new_destinations + [state_path]
    preexisting_directories = existing_parent_directories(root, rollback_paths)
    gh = find_gh(provider)
    with tempfile.TemporaryDirectory(prefix=".ai-workflow-providers-", dir=root) as temporary:
        transaction = Path(temporary)
        staged = transaction / ".agents" / "skills"
        staged.mkdir(parents=True)
        for skill in skills:
            run_gh_install(gh, root, provider, skill, directory=staged)
            verify_skill(transaction, provider, skill)

        if dry_run:
            print(f"PROVIDERS INSTALL DRY RUN for {root}")
            print(f"  - validated and staged {len(skills)} pinned skills with {gh}")
            for skill in skills:
                print(f"  - install managed provider skill {skill['name']}@{provider['version']}")
            print("No provider files changed.")
            return

        moved_new: List[Path] = []
        records: Dict[str, Mapping[str, object]] = {}
        try:
            for skill in skills:
                name = str(skill["name"])
                destination = skill_directory(root, name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                (staged / name).replace(destination)
                moved_new.append(destination)
                files = verify_skill(root, provider, skill)
                records[name] = {
                    "files": files,
                    "origin": "created",
                    "path": skill["path"],
                }
            cleanup_provider_staging(transaction)
            atomic_json(state_path, state_value(provider, records))
            if not command_status(root, verbose=False):
                raise ProviderError("post-install provider verification failed")
            if commit_callback is not None:
                commit_callback()
        except BaseException as error:
            rollback_errors = []
            try:
                state_path.unlink(missing_ok=True)
            except BaseException as rollback_error:
                rollback_errors.append(f"provider state: {rollback_error}")
            for directory in reversed(moved_new):
                try:
                    if directory.exists() and not directory.is_symlink():
                        remove_tree(directory, root)
                except BaseException as rollback_error:
                    rollback_errors.append(f"{directory}: {rollback_error}")
            for path in reversed(rollback_paths):
                try:
                    remove_created_empty_parents(
                        path,
                        root,
                        preexisting_directories,
                    )
                except BaseException as rollback_error:
                    rollback_errors.append(f"{path.parent}: {rollback_error}")
            if rollback_errors:
                raise ProviderError(
                    f"provider install failed and rollback also failed: {error}; "
                    + "; ".join(rollback_errors)
                ) from error
            raise
    print(f"✓ Curated upstream skills from {provider['repository']}@{provider['version']} are installed and verified.")


def state_matches_declaration(
    state: Mapping[str, object],
    provider: Mapping[str, object],
    skills: Sequence[Mapping[str, object]],
) -> bool:
    installed_provider = state.get("provider")
    if (
        not isinstance(installed_provider, dict)
        or installed_provider.get("name") != provider["name"]
        or installed_provider.get("repository") != provider["repository"]
        or installed_provider.get("version") != provider["version"]
    ):
        return False
    records = state.get("skills")
    if not isinstance(records, dict) or set(records) != {str(skill["name"]) for skill in skills}:
        return False
    return all(
        isinstance(records[str(skill["name"])], dict)
        and records[str(skill["name"])].get("path") == skill["path"]
        for skill in skills
    )


def command_status(root: Path, verbose: bool = True) -> bool:
    provider, skills = load_declaration()
    state_path = target_path(root, STATE_RELATIVE)
    if not state_path.exists() and not state_path.is_symlink():
        if verbose:
            print(f"PROVIDERS STATUS {root}")
            print("optional provider set: not installed; host-native fallback remains available")
        return True
    state = load_state(root)
    records = state["skills"]
    installed_provider = state["provider"]
    if not isinstance(records, dict) or not isinstance(installed_provider, dict):
        raise ProviderError("provider state is malformed")
    current_by_name = {str(skill["name"]): skill for skill in skills}
    same_release = (
        installed_provider.get("name") == provider["name"]
        and installed_provider.get("repository") == provider["repository"]
        and installed_provider.get("version") == provider["version"]
    )
    if verbose:
        print(f"PROVIDERS STATUS {root}")
        print(f"recorded source: {installed_provider['repository']}@{installed_provider['version']}")
        if not same_release:
            print(f"preferred source: {provider['repository']}@{provider['version']}")
    clean = True
    for name, record in sorted(records.items()):
        state_name = (
            "clean"
            if isinstance(record, dict) and checksums_match(root, name, record)
            else "modified"
        )
        skill = current_by_name.get(name)
        if (
            state_name == "clean"
            and same_release
            and skill is not None
            and record.get("path") == skill["path"]
        ):
            try:
                verify_skill(root, provider, skill)
            except ProviderError:
                state_name = "incompatible"
        clean = clean and state_name == "clean"
        if verbose:
            qualifier = " (not in preferred set)" if skill is None else ""
            print(f"{state_name}: .agents/skills/{name}{qualifier}")
    for name in sorted(set(current_by_name) - set(records)):
        clean = False
        if verbose:
            print(f"not-installed: .agents/skills/{name}")
    if verbose:
        if clean and same_release:
            print("✓ Optional upstream providers are clean.")
        elif clean:
            print("Optional upstream providers are locally clean; an update is available.")
        else:
            print(
                "Optional upstream providers are incomplete or locally changed; "
                "host-native fallback remains available."
            )
    return clean


def command_update(
    root: Path,
    dry_run: bool,
    *,
    commit_callback: Optional[Callable[[], None]] = None,
) -> None:
    provider, skills = load_declaration()
    state_path = target_path(root, STATE_RELATIVE)
    if not state_path.exists() and not state_path.is_symlink():
        command_install(root, dry_run, commit_callback=commit_callback)
        return
    state = load_state(root)
    old_provider = state.get("provider")
    old_records = state.get("skills")
    if not isinstance(old_provider, dict) or not isinstance(old_records, dict):
        raise ProviderError("provider state is malformed")
    new_by_name = {str(item["name"]): item for item in skills}
    if (
        old_provider.get("name") != provider["name"]
        or old_provider.get("repository") != provider["repository"]
    ):
        raise ProviderError(
            "installed provider belongs to a different provider source; "
            "refusing to overwrite its files"
        )

    actions: Dict[str, str] = {}
    transition_errors: List[str] = []
    for name, skill in sorted(new_by_name.items()):
        record = old_records.get(name)
        destination = skill_directory(root, name)
        if record is None:
            if not destination.exists() and not destination.is_symlink():
                actions[name] = "add"
            else:
                transition_errors.append(
                    f".agents/skills/{name} already exists without Agentic Workflow ownership; "
                    "refusing to overwrite it."
                )
            continue
        if not isinstance(record, dict):
            transition_errors.append(f"provider state has an invalid record for {name}")
            continue
        if not destination.exists() and not destination.is_symlink():
            actions[name] = "install-missing"
            continue
        conflicts = recorded_checksum_conflicts(root, name, record)
        if conflicts:
            transition_errors.append(
                f"{name} has local modifications. Refusing to overwrite:\n"
                + "\n".join(conflicts)
            )
            continue
        compatible = (
            old_provider.get("version") == provider["version"]
            and record.get("path") == skill["path"]
        )
        if compatible:
            try:
                verify_skill(root, provider, skill)
            except ProviderError:
                compatible = False
        if compatible:
            actions[name] = "retain"
        elif record.get("origin") in {"created", "reconstructed"}:
            actions[name] = "replace"
        else:
            transition_errors.append(
                f"existing provider skill {name} predates framework ownership; "
                "refusing to replace it."
            )
    if transition_errors:
        raise ProviderError(
            "provider update found ownership conflicts; no provider files were changed:\n\n"
            + "\n\n".join(transition_errors)
        )

    if all(action == "retain" for action in actions.values()) and state.get("schema_version") == 2:
        if commit_callback is not None:
            commit_callback()
        print(f"✓ Optional upstream provider baseline remains {provider['repository']}@{provider['version']}.")
        return

    retained_transactions = sorted(root.glob(f"{UPDATE_QUARANTINE_PREFIX}*"))
    if retained_transactions:
        raise ProviderError(
            "a retained provider-update quarantine blocks another update; inspect and remove "
            + ", ".join(str(path) for path in retained_transactions)
        )

    new_destinations = [
        skill_directory(root, name)
        for name, action in actions.items()
        if action in {"add", "install-missing"}
    ]
    preexisting_directories = existing_parent_directories(root, new_destinations)
    gh = find_gh(provider)
    transaction = Path(tempfile.mkdtemp(prefix=UPDATE_QUARANTINE_PREFIX, dir=root))
    staging_root = transaction / "new"
    staged = staging_root / ".agents" / "skills"
    backups = transaction / "previous"
    state_backup = transaction / STATE_RELATIVE.name
    staged.mkdir(parents=True)
    backups.mkdir()
    committed = False
    cleanup_transaction = True
    try:
        for skill in skills:
            if actions[str(skill["name"])] == "retain":
                continue
            run_gh_install(gh, root, provider, skill, directory=staged)
            verify_skill(staging_root, provider, skill)

        staging_conflicts: List[str] = []
        try:
            if load_state(root) != state:
                staging_conflicts.append("provider ownership state changed during staging")
        except ProviderError as error:
            staging_conflicts.append(f"provider ownership state changed during staging: {error}")
        for skill in skills:
            name = str(skill["name"])
            if actions[name] == "retain":
                conflicts = recorded_checksum_conflicts(root, name, old_records[name])
                if conflicts:
                    staging_conflicts.append(
                        f"provider skill {name} changed during staging:\n"
                        + "\n".join(conflicts)
                    )
                    continue
            elif actions[name] == "replace":
                conflicts = recorded_checksum_conflicts(root, name, old_records[name])
                if conflicts:
                    staging_conflicts.append(
                        f"provider skill {name} changed during staging:\n"
                        + "\n".join(conflicts)
                    )
                    continue
            elif actions[name] in {"add", "install-missing"}:
                destination = skill_directory(root, name)
                if destination.exists() or destination.is_symlink():
                    staging_conflicts.append(
                        f"provider path appeared during pinned staging; refusing to replace it: "
                        f".agents/skills/{name}"
                    )
        if staging_conflicts:
            raise ProviderError(
                "provider staging found conflicts; no provider files were changed:\n\n"
                + "\n\n".join(staging_conflicts)
            )

        if dry_run:
            print(f"PROVIDERS UPDATE DRY RUN for {root}")
            for name, action in sorted(actions.items()):
                print(f"  - {action.replace('-', ' ')} provider skill {name}")
            print(f"  - record preferred baseline {provider['repository']}@{provider['version']}")
            print("No provider files changed.")
            return

        activated: List[Tuple[Path, Optional[Path]]] = []
        state_backed_up = False
        new_records: Dict[str, Mapping[str, object]] = {
            name: {
                "files": record["files"],
                "origin": record["origin"],
                "path": record["path"],
            }
            for name, record in old_records.items()
            if name not in new_by_name and isinstance(record, dict)
        }
        try:
            for skill in skills:
                name = str(skill["name"])
                destination = skill_directory(root, name)
                action = actions[name]
                if action in {"replace", "add", "install-missing"}:
                    backup: Optional[Path] = None
                    if action == "replace":
                        backup = backups / name
                        destination.replace(backup)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    (staged / name).replace(destination)
                    activated.append((destination, backup))
                if name in old_records and (
                    action == "retain"
                    or old_records[name].get("origin") == "reconstructed"
                ):
                    origin = str(old_records[name]["origin"])
                else:
                    origin = "created"
                files = verify_skill(root, provider, skill)
                new_records[name] = {
                    "files": files,
                    "origin": origin,
                    "path": skill["path"],
                }
            state_path.replace(state_backup)
            state_backed_up = True
            atomic_json(state_path, state_value(provider, new_records))
            if not command_status(root, verbose=False):
                raise ProviderError("post-update provider verification failed")
            if commit_callback is not None:
                commit_callback()
        except BaseException as error:
            rollback_errors = []
            if state_backed_up:
                try:
                    if state_path.is_symlink() or (state_path.exists() and not state_path.is_file()):
                        raise ProviderError(f"rollback state target is not a regular file: {state_path}")
                    state_path.unlink(missing_ok=True)
                    state_backup.replace(state_path)
                except BaseException as rollback_error:
                    rollback_errors.append(f"provider state: {rollback_error}")
            for destination, backup in reversed(activated):
                try:
                    if destination.exists() and not destination.is_symlink():
                        remove_tree(destination, root)
                    elif destination.is_symlink():
                        raise ProviderError(f"rollback target became a symlink: {destination}")
                    if backup is not None:
                        backup.replace(destination)
                except BaseException as rollback_error:
                    rollback_errors.append(f"{destination}: {rollback_error}")
            for path in reversed(new_destinations):
                try:
                    remove_created_empty_parents(
                        path,
                        root,
                        preexisting_directories,
                    )
                except BaseException as rollback_error:
                    rollback_errors.append(f"{path.parent}: {rollback_error}")
            if rollback_errors:
                cleanup_transaction = False
                raise ProviderError(
                    f"provider update failed and rollback also failed: {error}; "
                    + "; ".join(rollback_errors)
                    + f"; rollback quarantine retained at {transaction}"
                ) from error
            raise
        committed = True
    finally:
        if cleanup_transaction:
            try:
                shutil.rmtree(transaction)
            except OSError as error:
                if committed:
                    print(
                        "WARNING: provider update committed, but backup cleanup failed; "
                        f"inspect and remove {transaction}: {error}",
                        file=sys.stderr,
                    )
                else:
                    print(
                        "WARNING: provider update did not commit, and staging cleanup failed; "
                        f"inspect and remove {transaction}: {error}",
                        file=sys.stderr,
                    )

    print(f"✓ Optional upstream providers updated to {provider['repository']}@{provider['version']}.")


def command_remove(root: Path, dry_run: bool) -> None:
    state_path = target_path(root, STATE_RELATIVE)
    if not state_path.exists() and not state_path.is_symlink():
        print("✓ No optional provider ownership state is installed; no provider files changed.")
        return
    state = load_state(root)
    records = state["skills"]
    if not isinstance(records, dict):
        raise ProviderError("provider state skills must be an object")
    actions = []
    removals = []
    for name, record in sorted(records.items()):
        if not isinstance(record, dict):
            raise ProviderError(f"invalid provider record for {name}")
        if record.get("origin") in {"preexisting-compatible", "reconstructed"}:
            actions.append(
                f"preserve provider skill without framework-created removal proof {name}"
            )
            continue
        if checksums_match(root, name, record):
            actions.append(f"remove unchanged framework-installed provider skill {name}")
            removals.append(skill_directory(root, name))
        else:
            actions.append(f"preserve locally changed provider skill {name}")
    actions.append(f"remove provider ownership state {STATE_RELATIVE}")
    if dry_run:
        print(f"PROVIDERS REMOVE DRY RUN for {root}")
        for action in actions:
            print(f"  - {action}")
        print("No provider files changed.")
        return
    quarantine_provider_removal(root, removals, state_path)
    print("✓ Upstream provider lifecycle state removed; pre-existing or changed skills were preserved.")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "update", "status", "remove"))
    parser.add_argument("target", nargs="?", default=Path.cwd(), type=Path)
    parser.add_argument("--dry-run", action="store_true", help="show the provider operation without changing files")
    parser.add_argument("--reinstall", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    require_supported_python()
    args = parse_args(argv or sys.argv[1:])
    if args.action == "status" and args.dry_run:
        raise ProviderError("--dry-run is not valid for status")
    if args.reinstall and args.action != "install":
        raise ProviderError("--reinstall is valid only for provider install")
    root = args.target.expanduser().resolve()
    if not root.is_dir():
        raise ProviderError(f"target project directory does not exist: {root}")
    if root == Path(root.anchor):
        raise ProviderError("refusing to operate on a filesystem root")
    if args.action == "install":
        command_install(root, args.dry_run, reinstall=args.reinstall)
    elif args.action == "update":
        command_update(root, args.dry_run)
    elif args.action == "status":
        return 0 if command_status(root) else 1
    else:
        command_remove(root, args.dry_run)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProviderError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
    except OSError as error:
        print(f"ERROR: filesystem operation failed: {error}", file=sys.stderr)
        raise SystemExit(2)
