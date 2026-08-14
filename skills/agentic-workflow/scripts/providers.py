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
SOURCE_MANIFEST_PATH = PACKAGE_ROOT / "payload" / "distribution" / "manifest.json"
STATE_RELATIVE = PurePosixPath("ai-workflow/provider-state.json")
INSTALL_MANIFEST_RELATIVE = PurePosixPath("ai-workflow/install-manifest.json")
INSTALLED_DECLARATION_RELATIVE = PurePosixPath("ai-workflow/providers.json")
SKILLS_RELATIVE = PurePosixPath(".agents/skills")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
SHA = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"[0-9a-f]{64}")
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
    ) != 2:
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
        "revision",
        "skills",
        "version",
    }:
        raise ProviderError("provider declaration has invalid provider fields")
    for field in ("minimum_gh_version", "name", "repository", "revision", "version"):
        if not isinstance(provider.get(field), str) or not provider[field]:
            raise ProviderError(f"provider {field} must be a non-empty string")
    parse_version(str(provider["minimum_gh_version"]), "minimum_gh_version")
    parse_version(str(provider["version"]), "provider version")
    if SHA.fullmatch(str(provider["revision"])) is None:
        raise ProviderError("provider revision must be a full Git commit SHA")
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
            "files",
            "invocation",
            "name",
            "path",
            "requires_configuration",
            "source_sha256",
            "tree_sha",
        }:
            raise ProviderError(
                "each provider skill needs files, invocation, name, path, requirements, "
                "source_sha256, and tree_sha"
            )
        name = item.get("name")
        if not isinstance(name, str) or SKILL_NAME.fullmatch(name) is None:
            raise ProviderError(f"invalid provider skill name: {name!r}")
        path = safe_relative(item.get("path"), f"provider path for {name}").as_posix()
        tree_sha = item.get("tree_sha")
        if not isinstance(tree_sha, str) or SHA.fullmatch(tree_sha) is None:
            raise ProviderError(f"invalid tree SHA for provider skill {name}")
        files = item.get("files")
        if not isinstance(files, list) or "SKILL.md" not in files:
            raise ProviderError(f"provider skill {name} needs a files array containing SKILL.md")
        checked_files = [safe_relative(value, f"file in provider skill {name}").as_posix() for value in files]
        if checked_files != sorted(set(checked_files)):
            raise ProviderError(f"provider skill {name} files must be unique and sorted")
        source_sha256 = item.get("source_sha256")
        if not isinstance(source_sha256, dict) or set(source_sha256) != set(checked_files):
            raise ProviderError(
                f"provider skill {name} source_sha256 must cover its exact file inventory"
            )
        if any(
            not isinstance(relative, str)
            or not isinstance(digest, str)
            or SHA256.fullmatch(digest) is None
            for relative, digest in source_sha256.items()
        ):
            raise ProviderError(f"provider skill {name} has an invalid source SHA-256")
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
            source_path = str(HOSTS[host]["invocation_source"]).split(":", 1)[0]
            if availability == "available" and source_path not in checked_files:
                raise ProviderError(f"provider skill {name} lacks {host} invocation metadata at {source_path}")
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
            metadata[key.strip()] = value.strip()
    return top, metadata


def normalized_skill_source(
    path: Path,
    expected_metadata: Mapping[str, str],
) -> bytes:
    """Remove only the GitHub CLI metadata block from a provider SKILL.md.

    The pinned upstream source has no ``metadata`` field. GitHub CLI injects one
    when it installs a skill, so source identity is the exact upstream bytes
    after removing that one authenticated block. All other frontmatter ordering,
    quoting, whitespace, line endings, and body bytes remain significant.
    """
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ProviderError(f"cannot read installed skill source at {path}: {exc}") from exc
    lines = text.splitlines(keepends=True)
    if not lines or lines[0] != "---\n":
        raise ProviderError(f"installed skill lacks valid frontmatter: {path}")
    try:
        closing = lines.index("---\n", 1)
    except ValueError as exc:
        raise ProviderError(f"installed skill lacks valid frontmatter: {path}") from exc

    starts = [
        index
        for index, line in enumerate(lines[1:closing], start=1)
        if re.fullmatch(r"metadata:[ ]*(?:\n)?", line) is not None
    ]
    if len(starts) != 1:
        raise ProviderError(
            f"installed skill must contain exactly one GitHub metadata block: {path}"
        )
    start = starts[0]
    end = start + 1
    parsed: Dict[str, str] = {}
    while end < closing and lines[end].startswith((" ", "\t")):
        line = lines[end]
        indentation = line[: len(line) - len(line.lstrip())]
        if "\t" in indentation or ":" not in line:
            raise ProviderError(f"installed skill has malformed GitHub metadata: {path}")
        key, value = line.split(":", 1)
        key = key.strip()
        if not key or key in parsed:
            raise ProviderError(f"installed skill has malformed GitHub metadata: {path}")
        parsed[key] = value.strip()
        end += 1
    if parsed != dict(expected_metadata):
        raise ProviderError(
            f"installed skill has incompatible or unexpected GitHub metadata: {path}"
        )
    return "".join(lines[:start] + lines[end:]).encode("utf-8")


def verify_source_content(
    directory: Path,
    skill: Mapping[str, object],
    expected_metadata: Mapping[str, str],
) -> None:
    name = str(skill["name"])
    declared = skill.get("source_sha256")
    if not isinstance(declared, Mapping):
        raise ProviderError(f"provider skill {name} has invalid source SHA-256 declarations")
    for relative in skill["files"]:  # type: ignore[union-attr]
        relative_text = str(relative)
        path = directory / relative_text
        if relative_text == "SKILL.md":
            content = normalized_skill_source(path, expected_metadata)
            actual = hashlib.sha256(content).hexdigest()
        else:
            actual = sha256(path)
        expected = declared.get(relative_text)
        if actual != expected:
            raise ProviderError(
                f"provider skill {name} source content is incompatible at {relative_text}: "
                f"expected SHA-256 {expected}, found {actual}"
            )


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
    expected_files = list(skill["files"])  # type: ignore[arg-type]
    expected_directories = implied_directories(expected_files)
    if actual_files != expected_files or actual_directories != expected_directories:
        missing = sorted(set(expected_files) - set(actual_files))
        extra = sorted(set(actual_files) - set(expected_files))
        missing_directories = sorted(set(expected_directories) - set(actual_directories))
        extra_directories = sorted(set(actual_directories) - set(expected_directories))
        detail = (f"; missing: {', '.join(missing)}" if missing else "") + (
            f"; unexpected: {', '.join(extra)}" if extra else ""
        ) + (
            f"; missing directories: {', '.join(missing_directories)}"
            if missing_directories
            else ""
        ) + (
            f"; unexpected directories: {', '.join(extra_directories)}"
            if extra_directories
            else ""
        )
        raise ProviderError(f"provider skill {name} directory contents are incompatible{detail}")
    top, metadata = frontmatter(directory / "SKILL.md")
    expected_metadata = {
        "github-path": str(skill["path"]),
        "github-pinned": str(provider["version"]),
        "github-ref": f"refs/tags/{provider['version']}",
        "github-repo": f"https://github.com/{provider['repository']}",
        "github-tree-sha": str(skill["tree_sha"]),
    }
    if top.get("name") != name:
        raise ProviderError(f"provider skill name does not match its directory: {name}")
    if metadata != expected_metadata:
        raise ProviderError(
            f"provider skill {name} has incompatible or unexpected GitHub metadata"
        )
    verify_invocation_metadata(directory, skill, top)
    verify_source_content(directory, skill, expected_metadata)
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
            "revision": provider["revision"],
            "version": provider["version"],
        },
        "schema_version": 1,
        "skills": dict(sorted(records.items())),
    }


def load_state(root: Path) -> MutableMapping[str, object]:
    path = target_path(root, STATE_RELATIVE)
    state = load_json(path, "provider state")
    if set(state) != {"provider", "schema_version", "skills"} or state.get("schema_version") != 1:
        raise ProviderError("provider state has unknown fields or an unsupported schema")
    provider = state.get("provider")
    skills = state.get("skills")
    if not isinstance(provider, dict) or set(provider) != {"name", "repository", "revision", "version"}:
        raise ProviderError("provider state has invalid provider fields")
    if (
        not isinstance(provider.get("name"), str)
        or not isinstance(provider.get("repository"), str)
        or re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", str(provider.get("repository"))) is None
        or not isinstance(provider.get("revision"), str)
        or SHA.fullmatch(str(provider.get("revision"))) is None
        or not isinstance(provider.get("version"), str)
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
            or set(record) != {"files", "origin", "path", "tree_sha"}
        ):
            raise ProviderError(f"provider state has invalid record for {name}")
        if record.get("origin") not in {"created", "preexisting-compatible"}:
            raise ProviderError(f"provider state has invalid origin for {name}")
        safe_relative(record.get("path"), f"provider state path for {name}")
        if not isinstance(record.get("tree_sha"), str) or SHA.fullmatch(str(record.get("tree_sha"))) is None:
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


def load_predecessor_declaration(
    raw: Mapping[str, object],
) -> Tuple[Mapping[str, object], List[Mapping[str, object]]]:
    """Validate the provider identity embedded in an authenticated predecessor payload."""
    schema = raw.get("schema_version")
    if schema == 1:
        expected_top = {"schema_version", "capabilities", "provider"}
        expected_skill_fields = {"files", "name", "path", "tree_sha"}
    elif schema == 2:
        expected_top = {"schema_version", "capabilities", "configuration", "hosts", "provider"}
        expected_skill_fields = {
            "files",
            "invocation",
            "name",
            "path",
            "requires_configuration",
            "source_sha256",
            "tree_sha",
        }
    else:
        raise ProviderError("authenticated predecessor provider declaration has an unsupported schema")
    if set(raw) != expected_top:
        raise ProviderError("authenticated predecessor provider declaration has unknown fields")
    capabilities = raw.get("capabilities")
    provider = raw.get("provider")
    if not isinstance(capabilities, dict) or not capabilities:
        raise ProviderError("authenticated predecessor provider declaration needs capabilities")
    if not isinstance(provider, dict) or set(provider) != {
        "minimum_gh_version",
        "name",
        "repository",
        "revision",
        "skills",
        "version",
    }:
        raise ProviderError("authenticated predecessor provider identity is malformed")
    for field in ("minimum_gh_version", "name", "repository", "revision", "version"):
        if not isinstance(provider.get(field), str) or not provider[field]:
            raise ProviderError(f"authenticated predecessor provider {field} is malformed")
    parse_version(str(provider["minimum_gh_version"]), "predecessor minimum_gh_version")
    parse_version(str(provider["version"]), "predecessor provider version")
    if SHA.fullmatch(str(provider["revision"])) is None:
        raise ProviderError("authenticated predecessor provider revision is malformed")
    if re.fullmatch(
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", str(provider["repository"])
    ) is None:
        raise ProviderError("authenticated predecessor provider repository is malformed")

    skills = provider.get("skills")
    if not isinstance(skills, list) or not skills:
        raise ProviderError("authenticated predecessor provider skills are missing")
    checked: List[Mapping[str, object]] = []
    names = set()
    paths = set()
    for item in skills:
        if not isinstance(item, dict) or set(item) != expected_skill_fields:
            raise ProviderError("authenticated predecessor provider skill record is malformed")
        name = item.get("name")
        if not isinstance(name, str) or SKILL_NAME.fullmatch(name) is None:
            raise ProviderError(f"authenticated predecessor provider skill name is malformed: {name!r}")
        path = safe_relative(item.get("path"), f"predecessor provider path for {name}").as_posix()
        tree_sha = item.get("tree_sha")
        if not isinstance(tree_sha, str) or SHA.fullmatch(tree_sha) is None:
            raise ProviderError(f"authenticated predecessor tree SHA is malformed for {name}")
        files = item.get("files")
        if not isinstance(files, list) or "SKILL.md" not in files:
            raise ProviderError(f"authenticated predecessor file inventory is malformed for {name}")
        checked_files = [
            safe_relative(value, f"predecessor provider file for {name}").as_posix()
            for value in files
        ]
        if checked_files != sorted(set(checked_files)):
            raise ProviderError(f"authenticated predecessor file inventory is malformed for {name}")
        if schema == 2:
            source_sha256 = item.get("source_sha256")
            invocation = item.get("invocation")
            requirements = item.get("requires_configuration")
            if (
                not isinstance(source_sha256, dict)
                or set(source_sha256) != set(checked_files)
                or any(
                    not isinstance(digest, str) or SHA256.fullmatch(digest) is None
                    for digest in source_sha256.values()
                )
            ):
                raise ProviderError(f"authenticated predecessor source hashes are malformed for {name}")
            if not isinstance(invocation, dict) or set(invocation) != set(HOSTS) or any(
                value not in INVOCATION_MODES for value in invocation.values()
            ):
                raise ProviderError(f"authenticated predecessor invocation policy is malformed for {name}")
            if not isinstance(requirements, list) or any(
                not isinstance(value, str) for value in requirements
            ):
                raise ProviderError(f"authenticated predecessor requirements are malformed for {name}")
        if name in names or path in paths:
            raise ProviderError(f"duplicate authenticated predecessor provider skill: {name}")
        names.add(name)
        paths.add(path)
        checked.append(item)
    if any(
        not isinstance(capability, str)
        or not capability
        or not isinstance(skill_name, str)
        or skill_name not in names
        for capability, skill_name in capabilities.items()
    ):
        raise ProviderError("authenticated predecessor capability map is malformed")
    return provider, checked


def authenticated_predecessor_declaration(
    root: Path,
) -> Tuple[Mapping[str, object], List[Mapping[str, object]], str]:
    """Bind old provider state to an exact predecessor audited by the new package."""
    installed_path = target_path(root, INSTALL_MANIFEST_RELATIVE)
    installed = load_json(installed_path, "installation manifest for provider migration")
    if set(installed) != {
        "schema_version",
        "framework_version",
        "source_revision",
        "installed_at",
        "framework_files",
        "project_owned",
    }:
        raise ProviderError("installation manifest cannot authenticate provider migration")
    installed_schema = installed.get("schema_version")
    installed_version = installed.get("framework_version")
    installed_revision = installed.get("source_revision")
    installed_files = installed.get("framework_files")
    if (
        type(installed_schema) is not int
        or not isinstance(installed_version, str)
        or not isinstance(installed_revision, str)
        or SHA.fullmatch(installed_revision) is None
        or not isinstance(installed_files, dict)
        or not installed_files
    ):
        raise ProviderError("installation manifest cannot authenticate provider migration")
    parse_version(installed_version, "installed framework version")
    installed_sources: Dict[str, str] = {}
    for relative, details in installed_files.items():
        safe_relative(relative, "installed framework path")
        if not isinstance(details, dict):
            raise ProviderError("installation manifest has malformed provider migration evidence")
        source_digest = details.get("source_sha256")
        installed_digest = details.get("sha256")
        if (
            not isinstance(source_digest, str)
            or SHA256.fullmatch(source_digest) is None
            or not isinstance(installed_digest, str)
            or SHA256.fullmatch(installed_digest) is None
        ):
            raise ProviderError("installation manifest has malformed provider migration checksums")
        installed_sources[str(relative)] = source_digest

    source_manifest = load_json(SOURCE_MANIFEST_PATH, "source distribution manifest")
    accepted = source_manifest.get("accepted_predecessors")
    if source_manifest.get("schema_version") != 3 or not isinstance(accepted, list):
        raise ProviderError("source package cannot authenticate provider predecessors")
    matches: List[Mapping[str, object]] = []
    for candidate in accepted:
        if not isinstance(candidate, dict) or set(candidate) != {
            "framework_version",
            "source_revisions",
            "install_manifest_schemas",
            "framework_files",
        }:
            raise ProviderError("source package has malformed accepted predecessor evidence")
        identities = candidate.get("framework_files")
        revisions = candidate.get("source_revisions")
        schemas = candidate.get("install_manifest_schemas")
        if (
            candidate.get("framework_version") == installed_version
            and isinstance(revisions, list)
            and installed_revision in revisions
            and isinstance(schemas, list)
            and installed_schema in schemas
            and isinstance(identities, dict)
            and installed_sources == identities
        ):
            matches.append(candidate)
    if len(matches) != 1:
        raise ProviderError(
            "provider migration requires an exact package-authenticated predecessor; "
            f"found {installed_version}, {installed_revision}, schema {installed_schema}"
        )

    declaration_key = INSTALLED_DECLARATION_RELATIVE.as_posix()
    authenticated_sources = matches[0]["framework_files"]
    if not isinstance(authenticated_sources, dict) or declaration_key not in authenticated_sources:
        raise ProviderError(
            "authenticated predecessor does not contain a provider declaration; refusing migration"
        )
    declaration_details = installed_files.get(declaration_key)
    declaration_path = target_path(root, INSTALLED_DECLARATION_RELATIVE)
    if not isinstance(declaration_details, dict):
        raise ProviderError("installation manifest lacks provider declaration ownership evidence")
    expected_source = authenticated_sources[declaration_key]
    try:
        declaration_bytes = declaration_path.read_bytes()
    except OSError as error:
        raise ProviderError(
            f"cannot read authenticated predecessor provider declaration: {error}"
        ) from error
    if (
        declaration_details.get("source_sha256") != expected_source
        or declaration_details.get("sha256") != expected_source
        or hashlib.sha256(declaration_bytes).hexdigest() != expected_source
    ):
        raise ProviderError(
            "installed predecessor provider declaration is modified or inconsistent; refusing migration"
        )
    try:
        raw_declaration = json.loads(declaration_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProviderError(
            f"authenticated predecessor provider declaration is malformed: {error}"
        ) from error
    if not isinstance(raw_declaration, dict):
        raise ProviderError("authenticated predecessor provider declaration must be an object")
    predecessor_provider, predecessor_skills = load_predecessor_declaration(raw_declaration)
    return predecessor_provider, predecessor_skills, installed_version


def validate_predecessor_state(
    state: Mapping[str, object],
    provider: Mapping[str, object],
    skills: Sequence[Mapping[str, object]],
) -> Mapping[str, Mapping[str, object]]:
    expected_provider = {
        "name": provider["name"],
        "repository": provider["repository"],
        "revision": provider["revision"],
        "version": provider["version"],
    }
    if state.get("provider") != expected_provider:
        raise ProviderError(
            "provider state identity does not match the authenticated predecessor declaration"
        )
    records = state.get("skills")
    by_name = {str(skill["name"]): skill for skill in skills}
    if not isinstance(records, dict) or set(records) != set(by_name):
        raise ProviderError(
            "provider state skill set does not match the authenticated predecessor declaration"
        )
    for name, skill in by_name.items():
        record = records.get(name)
        if (
            not isinstance(record, dict)
            or record.get("path") != skill["path"]
            or record.get("tree_sha") != skill["tree_sha"]
            or not isinstance(record.get("files"), dict)
            or set(record["files"]) != set(skill["files"])
        ):
            raise ProviderError(
                f"provider state for {name} is inconsistent with the authenticated predecessor"
            )
    return records  # type: ignore[return-value]


def verify_predecessor_skill(
    root: Path,
    provider: Mapping[str, object],
    skill: Mapping[str, object],
) -> None:
    """Verify package-authenticated predecessor metadata and its complete inventory."""
    name = str(skill["name"])
    directory = skill_directory(root, name)
    actual_files, actual_directories = directory_inventory(directory)
    expected_files = list(skill["files"])  # type: ignore[arg-type]
    if actual_files != expected_files or actual_directories != implied_directories(expected_files):
        raise ProviderError(f"predecessor provider skill {name} has an incompatible inventory")
    top, metadata = frontmatter(directory / "SKILL.md")
    expected_metadata = {
        "github-path": str(skill["path"]),
        "github-pinned": str(provider["version"]),
        "github-ref": f"refs/tags/{provider['version']}",
        "github-repo": f"https://github.com/{provider['repository']}",
        "github-tree-sha": str(skill["tree_sha"]),
    }
    if top.get("name") != name or metadata != expected_metadata:
        raise ProviderError(
            f"predecessor provider skill {name} does not match its authenticated source metadata"
        )
    if "source_sha256" in skill:
        verify_invocation_metadata(directory, skill, top)
        verify_source_content(directory, skill, expected_metadata)


def predecessor_checksum_conflicts(
    root: Path,
    name: str,
    record: Mapping[str, object],
) -> List[str]:
    """Return precise path/hash differences from the predecessor installation record."""
    directory = skill_directory(root, name)
    expected = record.get("files")
    if not isinstance(expected, dict):
        return [f"provider state for {name} lacks predecessor file checksums"]
    try:
        actual_files, actual_directories = directory_inventory(directory)
    except ProviderError as error:
        return [str(error)]
    conflicts: List[str] = []
    expected_files = sorted(expected)
    expected_directories = implied_directories(expected_files)
    for relative in sorted(set(expected_files) - set(actual_files)):
        conflicts.append(
            f"  .agents/skills/{name}/{relative}\n"
            f"    Expected predecessor SHA-256: {expected[relative]}\n"
            "    Found SHA-256: missing"
        )
    for relative in sorted(set(actual_files) - set(expected_files)):
        conflicts.append(
            f"  .agents/skills/{name}/{relative}\n"
            "    Expected predecessor SHA-256: absent\n"
            f"    Found SHA-256: {sha256(directory / relative)}"
        )
    for relative in sorted(set(actual_files) & set(expected_files)):
        actual = sha256(directory / relative)
        if actual != expected[relative]:
            conflicts.append(
                f"  .agents/skills/{name}/{relative}\n"
                f"    Expected predecessor SHA-256: {expected[relative]}\n"
                f"    Found SHA-256: {actual}"
            )
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


def verify_authenticated_match(actual: Path, staged: Path, name: str) -> None:
    """Require an existing provider directory to byte-match authenticated staging."""
    actual_files, actual_directories = directory_inventory(actual)
    staged_files, staged_directories = directory_inventory(staged)
    if actual_files != staged_files or actual_directories != staged_directories:
        missing = sorted(set(staged_files) - set(actual_files))
        extra = sorted(set(actual_files) - set(staged_files))
        missing_directories = sorted(set(staged_directories) - set(actual_directories))
        extra_directories = sorted(set(actual_directories) - set(staged_directories))
        detail = (f"; missing: {', '.join(missing)}" if missing else "") + (
            f"; unexpected: {', '.join(extra)}" if extra else ""
        ) + (
            f"; missing directories: {', '.join(missing_directories)}"
            if missing_directories
            else ""
        ) + (
            f"; unexpected directories: {', '.join(extra_directories)}"
            if extra_directories
            else ""
        )
        raise ProviderError(
            f"pre-existing provider skill {name} does not match authenticated pinned staging{detail}"
        )
    for relative in staged_files:
        if actual.joinpath(relative).read_bytes() != staged.joinpath(relative).read_bytes():
            raise ProviderError(
                f"pre-existing provider skill {name} does not byte-match authenticated pinned staging: "
                f"{relative}"
            )


def cleanup_provider_staging(transaction: Path) -> None:
    """Remove authenticated staging before committing target ownership state."""
    shutil.rmtree(transaction)


def command_install(
    root: Path,
    dry_run: bool,
    *,
    commit_callback: Optional[Callable[[], None]] = None,
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

    origins: Dict[str, str] = {}
    for skill in skills:
        name = str(skill["name"])
        destination = skill_directory(root, name)
        if destination.exists() or destination.is_symlink():
            verify_skill(root, provider, skill)
            origins[name] = "preexisting-compatible"
        else:
            origins[name] = "created"
    new_destinations = [
        skill_directory(root, str(skill["name"]))
        for skill in skills
        if origins[str(skill["name"])] == "created"
    ]
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
        for skill in skills:
            name = str(skill["name"])
            if origins[name] == "preexisting-compatible":
                verify_authenticated_match(
                    skill_directory(root, name),
                    staged / name,
                    name,
                )

        if dry_run:
            print(f"PROVIDERS INSTALL DRY RUN for {root}")
            print(f"  - authenticated and staged {len(skills)} pinned skills with {gh}")
            for skill in skills:
                print(f"  - {origins[str(skill['name'])]}: {skill['name']}@{provider['version']}")
            print("No provider files changed.")
            return

        moved_new: List[Path] = []
        records: Dict[str, Mapping[str, object]] = {}
        try:
            for skill in skills:
                name = str(skill["name"])
                destination = skill_directory(root, name)
                if origins[name] == "created":
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    (staged / name).replace(destination)
                    moved_new.append(destination)
                files = verify_skill(root, provider, skill)
                records[name] = {
                    "files": files,
                    "origin": origins[name],
                    "path": skill["path"],
                    "tree_sha": skill["tree_sha"],
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
    expected_provider = {
        "name": provider["name"],
        "repository": provider["repository"],
        "revision": provider["revision"],
        "version": provider["version"],
    }
    if state.get("provider") != expected_provider:
        return False
    records = state.get("skills")
    if not isinstance(records, dict) or set(records) != {str(skill["name"]) for skill in skills}:
        return False
    return all(
        isinstance(records[str(skill["name"])], dict)
        and records[str(skill["name"])].get("path") == skill["path"]
        and records[str(skill["name"])].get("tree_sha") == skill["tree_sha"]
        for skill in skills
    )


def command_status(root: Path, verbose: bool = True) -> bool:
    provider, skills = load_declaration()
    state = load_state(root)
    if not state_matches_declaration(state, provider, skills):
        raise ProviderError("installed provider baseline differs from this package; run update with the intended package")
    records = state["skills"]
    if not isinstance(records, dict):
        raise ProviderError("provider state skills must be an object")
    if verbose:
        print(f"PROVIDERS STATUS {root}")
        print(f"source: {provider['repository']}@{provider['version']}")
        print(f"revision: {provider['revision']}")
    clean = True
    for skill in skills:
        name = str(skill["name"])
        try:
            verify_skill(root, provider, skill)
            record = records[name]
            state_name = "clean" if isinstance(record, dict) and checksums_match(root, name, record) else "modified"
        except ProviderError:
            state_name = "missing-or-incompatible"
        clean = clean and state_name == "clean"
        if verbose:
            print(f"{state_name}: .agents/skills/{name}")
    if verbose:
        print("✓ Upstream provider dependencies are clean." if clean else "Upstream provider dependencies differ from their recorded installation.")
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
    if state_matches_declaration(state, provider, skills):
        if not command_status(root, verbose=False):
            raise ProviderError("provider dependencies were locally changed or removed; refusing to overwrite them")
        if commit_callback is not None:
            commit_callback()
        print(f"✓ Upstream provider baseline remains {provider['repository']}@{provider['version']}.")
        return

    old_provider, old_skills, predecessor_version = authenticated_predecessor_declaration(root)
    old_records = validate_predecessor_state(state, old_provider, old_skills)
    old_by_name = {str(item["name"]): item for item in old_skills}
    new_by_name = {str(item["name"]): item for item in skills}
    if (
        old_provider.get("name") != provider["name"]
        or old_provider.get("repository") != provider["repository"]
    ):
        raise ProviderError(
            "installed provider belongs to a different provider source; "
            "update with its exact framework package before changing providers"
        )
    unknown_old_names = sorted(set(old_by_name) - set(new_by_name))
    if unknown_old_names:
        raise ProviderError(
            "authenticated predecessor contains provider names outside this package declaration; "
            "automatic removal is not authorized: "
            + ", ".join(unknown_old_names)
        )

    actions: Dict[str, str] = {}
    transition_errors: List[str] = []
    for name, predecessor_skill in sorted(old_by_name.items()):
        record = old_records[name]
        destination = skill_directory(root, name)
        if not destination.exists() and not destination.is_symlink():
            actions[name] = "install-missing"
            continue
        conflicts = predecessor_checksum_conflicts(root, name, record)
        if conflicts:
            transition_errors.append(
                f"provider skill {name} was installed by the authenticated predecessor "
                "but has been modified locally.\nRefusing to replace:\n"
                + "\n".join(conflicts)
            )
            continue
        try:
            verify_predecessor_skill(root, old_provider, predecessor_skill)
        except ProviderError as error:
            transition_errors.append(
                f"existing provider skill {name} cannot be proven to match the authenticated "
                f"predecessor. Refusing to replace it: {error}"
            )
            continue
        try:
            verify_skill(root, provider, new_by_name[name])
            actions[name] = "retain"
        except ProviderError:
            if record.get("origin") == "created":
                actions[name] = "replace"
            else:
                transition_errors.append(
                    f"existing provider skill {name} cannot be proven framework-managed; "
                    "the authenticated predecessor records it as pre-existing-compatible. "
                    "Refusing to replace it."
                )
    for skill in skills:
        name = str(skill["name"])
        if name in old_records:
            continue
        destination = skill_directory(root, name)
        if not destination.exists() and not destination.is_symlink():
            actions[name] = "add"
            continue
        try:
            verify_skill(root, provider, skill)
            actions[name] = "preexisting-compatible"
        except ProviderError as error:
            transition_errors.append(
                f"existing provider skill {name} cannot be proven framework-managed. "
                f"Refusing to replace it: {error}"
            )
    if transition_errors:
        raise ProviderError(
            "provider transition preflight found conflicts; no provider files were changed:\n\n"
            + "\n\n".join(transition_errors)
        )

    retained_transactions = sorted(root.glob(f"{UPDATE_QUARANTINE_PREFIX}*"))
    if retained_transactions:
        raise ProviderError(
            "a retained provider-update quarantine blocks another migration; inspect and remove "
            + ", ".join(str(path) for path in retained_transactions)
        )

    new_destinations = [
        skill_directory(root, str(skill["name"]))
        for skill in skills
        if actions[str(skill["name"])] in {"add", "install-missing"}
    ]
    preexisting_directories = existing_parent_directories(root, new_destinations)
    gh = find_gh(provider)
    transaction = Path(tempfile.mkdtemp(prefix=UPDATE_QUARANTINE_PREFIX, dir=root))
    staging_root = transaction / "new"
    staged = staging_root / ".agents" / "skills"
    backups = transaction / "predecessor"
    state_backup = transaction / STATE_RELATIVE.name
    staged.mkdir(parents=True)
    backups.mkdir()
    committed = False
    cleanup_transaction = True
    try:
        for skill in skills:
            run_gh_install(gh, root, provider, skill, directory=staged)
            verify_skill(staging_root, provider, skill)

        staging_conflicts: List[str] = []
        try:
            refreshed_provider, refreshed_skills, refreshed_version = (
                authenticated_predecessor_declaration(root)
            )
            if (
                refreshed_provider != old_provider
                or refreshed_skills != old_skills
                or refreshed_version != predecessor_version
                or load_state(root) != state
            ):
                staging_conflicts.append(
                    "predecessor ownership evidence changed during authenticated staging"
                )
        except ProviderError as error:
            staging_conflicts.append(
                f"predecessor ownership evidence changed during authenticated staging: {error}"
            )
        for skill in skills:
            name = str(skill["name"])
            if actions[name] in {"retain", "preexisting-compatible"}:
                try:
                    verify_authenticated_match(
                        skill_directory(root, name),
                        staged / name,
                        name,
                    )
                except ProviderError as error:
                    staging_conflicts.append(str(error))
            elif actions[name] == "replace":
                conflicts = predecessor_checksum_conflicts(root, name, old_records[name])
                if conflicts:
                    staging_conflicts.append(
                        f"provider skill {name} changed during authenticated staging:\n"
                        + "\n".join(conflicts)
                    )
                    continue
                try:
                    verify_predecessor_skill(root, old_provider, old_by_name[name])
                except ProviderError as error:
                    staging_conflicts.append(
                        f"provider skill {name} changed during authenticated staging: {error}"
                    )
            elif actions[name] in {"add", "install-missing"}:
                destination = skill_directory(root, name)
                if destination.exists() or destination.is_symlink():
                    staging_conflicts.append(
                        f"provider path appeared during authenticated staging; refusing to replace it: "
                        f".agents/skills/{name}"
                    )
        if staging_conflicts:
            raise ProviderError(
                "authenticated staging found provider conflicts; no provider files were changed:\n\n"
                + "\n\n".join(staging_conflicts)
            )

        migrations = [name for name, action in sorted(actions.items()) if action == "replace"]
        if dry_run:
            print(f"PROVIDERS UPDATE DRY RUN for {root}")
            print(f"  - authenticated predecessor framework {predecessor_version}")
            print(f"  - authenticated and staged {len(skills)} pinned skills with {gh}")
            if migrations:
                print("  - provider migration:")
                for name in migrations:
                    print(
                        f"      {name}: predecessor-managed, checksum-clean; "
                        f"{old_provider['version']} -> {provider['version']}"
                    )
            for name, action in sorted(actions.items()):
                if action != "replace":
                    print(f"  - {action.replace('-', ' ')} provider skill {name}")
            print(f"  - record compatible baseline {provider['repository']}@{provider['version']}")
            print("No provider files changed.")
            return

        activated: List[Tuple[Path, Optional[Path]]] = []
        state_backed_up = False
        new_records: Dict[str, Mapping[str, object]] = {}
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
                if action == "preexisting-compatible":
                    origin = "preexisting-compatible"
                elif name in old_records and action == "retain":
                    origin = str(old_records[name]["origin"])
                else:
                    origin = "created"
                files = verify_skill(root, provider, skill)
                new_records[name] = {
                    "files": files,
                    "origin": origin,
                    "path": skill["path"],
                    "tree_sha": skill["tree_sha"],
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
                        "WARNING: provider update committed, but predecessor-backup cleanup failed; "
                        f"inspect and remove {transaction}: {error}",
                        file=sys.stderr,
                    )
                else:
                    print(
                        "WARNING: provider update did not commit, and staging cleanup failed; "
                        f"inspect and remove {transaction}: {error}",
                        file=sys.stderr,
                    )

    if migrations:
        print("Provider migration:")
        for name in migrations:
            print(
                f"  {name}: predecessor-managed, checksum-clean; "
                f"{old_provider['version']} -> {provider['version']}"
            )
            print(f"✓ Migrated provider skill {name}.")
    print(f"✓ Curated upstream skills updated intentionally to {provider['repository']}@{provider['version']}.")


def command_remove(root: Path, dry_run: bool) -> None:
    provider, skills = load_declaration()
    state_path = target_path(root, STATE_RELATIVE)
    state = load_state(root)
    if not state_matches_declaration(state, provider, skills):
        raise ProviderError(
            "installed provider baseline differs from this package; remove with the exact recorded framework package"
        )
    records = state["skills"]
    if not isinstance(records, dict):
        raise ProviderError("provider state skills must be an object")
    actions = []
    removals = []
    by_name = {str(skill["name"]): skill for skill in skills}
    for name, record in sorted(records.items()):
        if not isinstance(record, dict):
            raise ProviderError(f"invalid provider record for {name}")
        if record.get("origin") == "preexisting-compatible":
            actions.append(f"preserve pre-existing compatible provider skill {name}")
            continue
        try:
            verify_skill(root, provider, by_name[name])
        except ProviderError:
            actions.append(f"preserve incompatible or locally changed provider skill {name}")
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
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    require_supported_python()
    args = parse_args(argv or sys.argv[1:])
    if args.action == "status" and args.dry_run:
        raise ProviderError("--dry-run is not valid for status")
    root = args.target.expanduser().resolve()
    if not root.is_dir():
        raise ProviderError(f"target project directory does not exist: {root}")
    if root == Path(root.anchor):
        raise ProviderError("refusing to operate on a filesystem root")
    if args.action == "install":
        command_install(root, args.dry_run)
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
