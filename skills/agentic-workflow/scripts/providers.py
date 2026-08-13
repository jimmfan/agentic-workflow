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
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DECLARATION_PATH = PACKAGE_ROOT / "payload" / "ai-workflow" / "providers.json"
STATE_RELATIVE = PurePosixPath("ai-workflow/provider-state.json")
SKILLS_RELATIVE = PurePosixPath(".agents/skills")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
SHA = re.compile(r"[0-9a-f]{40}")
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class ProviderError(RuntimeError):
    """A provider declaration, dependency, or lifecycle invariant failed."""


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
    if set(raw) != {"schema_version", "capabilities", "provider"} or raw.get("schema_version") != 1:
        raise ProviderError("provider declaration has unknown fields or an unsupported schema")
    capabilities = raw.get("capabilities")
    provider = raw.get("provider")
    if not isinstance(capabilities, dict) or not capabilities:
        raise ProviderError("provider declaration needs a non-empty capabilities object")
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
        if not isinstance(item, dict) or set(item) != {"files", "name", "path", "tree_sha"}:
            raise ProviderError("each provider skill needs files, name, path, and tree_sha")
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
        if name in names or path in paths:
            raise ProviderError(f"duplicate provider skill name or path: {name}")
        names.add(name)
        paths.add(path)
        checked.append(item)
    for capability, skill_name in capabilities.items():
        if not isinstance(capability, str) or not capability or skill_name not in names:
            raise ProviderError(f"capability {capability!r} selects an unknown provider skill")
    return provider, checked


def frontmatter(path: Path) -> Tuple[Mapping[str, str], Mapping[str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
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


def skill_directory(root: Path, name: str) -> Path:
    return target_path(root, SKILLS_RELATIVE / name)


def directory_files(directory: Path) -> List[str]:
    if directory.is_symlink() or not directory.is_dir():
        raise ProviderError(f"provider skill must be a regular directory: {directory}")
    files = []
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ProviderError(f"provider skill contains a symlink: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ProviderError(f"provider skill contains a special entry: {path}")
        files.append(path.relative_to(directory).as_posix())
    return sorted(files)


def verify_skill(
    root: Path,
    provider: Mapping[str, object],
    skill: Mapping[str, object],
) -> Mapping[str, str]:
    name = str(skill["name"])
    directory = skill_directory(root, name)
    actual_files = directory_files(directory)
    expected_files = list(skill["files"])  # type: ignore[arg-type]
    if actual_files != expected_files:
        missing = sorted(set(expected_files) - set(actual_files))
        extra = sorted(set(actual_files) - set(expected_files))
        detail = (f"; missing: {', '.join(missing)}" if missing else "") + (
            f"; unexpected: {', '.join(extra)}" if extra else ""
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
    for key, expected in expected_metadata.items():
        if metadata.get(key) != expected:
            raise ProviderError(
                f"provider skill {name} has incompatible {key}: "
                f"expected {expected!r}, found {metadata.get(key)!r}"
            )
    return {relative: sha256(directory / relative) for relative in actual_files}


def find_gh(provider: Mapping[str, object]) -> Path:
    command = shutil.which("gh")
    if command is None:
        raise ProviderError(
            "GitHub CLI 2.90.0 or newer with `gh skill` is required; install or update gh, "
            "verify with `gh --version` and `gh skill --help`, then rerun this command"
        )
    result = subprocess.run([command, "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        raise ProviderError(f"cannot run GitHub CLI at {command}: {result.stderr.strip()}")
    match = re.search(r"gh version ([0-9]+\.[0-9]+\.[0-9]+)", result.stdout)
    if match is None:
        raise ProviderError(f"cannot determine GitHub CLI version from: {result.stdout.strip()!r}")
    minimum = parse_version(str(provider["minimum_gh_version"]), "minimum_gh_version")
    if parse_version(match.group(1), "GitHub CLI version") < minimum:
        raise ProviderError(
            f"GitHub CLI {provider['minimum_gh_version']} or newer is required; found {match.group(1)} at {command}"
        )
    help_result = subprocess.run([command, "skill", "install", "--help"], capture_output=True, text=True)
    if help_result.returncode != 0 or "--pin" not in help_result.stdout or "--scope" not in help_result.stdout:
        raise ProviderError(f"GitHub CLI at {command} does not provide the required gh skill install interface")
    auth_result = subprocess.run(
        [command, "auth", "status", "--hostname", "github.com"],
        capture_output=True,
        text=True,
    )
    if auth_result.returncode != 0:
        raise ProviderError(
            "an authenticated GitHub CLI session is required to install the curated provider set reliably; "
            "run `gh auth login --hostname github.com --web`, verify with "
            "`gh auth status --hostname github.com`, then rerun this command (automation may set GH_TOKEN)"
        )
    return Path(command)


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


def remove_tree(directory: Path, root: Path) -> None:
    if directory.is_symlink() or not directory.is_dir():
        raise ProviderError(f"refusing to remove non-directory provider path: {directory}")
    directory.resolve().relative_to(root.resolve())
    shutil.rmtree(directory)
    current = directory.parent
    while current != root and current != root.parent:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def checksums_match(root: Path, name: str, record: Mapping[str, object]) -> bool:
    directory = skill_directory(root, name)
    try:
        actual_files = directory_files(directory)
    except ProviderError:
        return False
    expected = record["files"]
    if not isinstance(expected, dict) or actual_files != sorted(expected):
        return False
    return all(sha256(directory / relative) == expected[relative] for relative in actual_files)


def command_install(root: Path, dry_run: bool) -> None:
    provider, skills = load_declaration()
    state_path = target_path(root, STATE_RELATIVE)
    if state_path.exists() or state_path.is_symlink():
        if command_status(root, verbose=False):
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
    gh = find_gh(provider) if "created" in origins.values() else None
    if dry_run:
        print(f"PROVIDERS INSTALL DRY RUN for {root}")
        if gh is not None:
            print(f"  - use GitHub CLI at {gh}")
        for skill in skills:
            print(f"  - {origins[str(skill['name'])]}: {skill['name']}@{provider['version']}")
        print("No provider files changed.")
        return

    attempted: List[Path] = []
    records: Dict[str, Mapping[str, object]] = {}
    try:
        for skill in skills:
            name = str(skill["name"])
            if origins[name] == "created":
                if gh is None:
                    raise ProviderError("internal provider install is missing GitHub CLI")
                attempted.append(skill_directory(root, name))
                run_gh_install(gh, root, provider, skill)
            files = verify_skill(root, provider, skill)
            records[name] = {
                "files": files,
                "origin": origins[name],
                "path": skill["path"],
                "tree_sha": skill["tree_sha"],
            }
        atomic_json(state_path, state_value(provider, records))
    except BaseException:
        for directory in reversed(attempted):
            if directory.exists() and not directory.is_symlink():
                remove_tree(directory, root)
        state_path.unlink(missing_ok=True)
        raise
    if not command_status(root, verbose=False):
        raise ProviderError("post-install provider verification failed")
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


def command_update(root: Path, dry_run: bool) -> None:
    provider, skills = load_declaration()
    state_path = target_path(root, STATE_RELATIVE)
    if not state_path.exists():
        command_install(root, dry_run)
        return
    state = load_state(root)
    if state_matches_declaration(state, provider, skills):
        if not command_status(root, verbose=False):
            raise ProviderError("provider dependencies were locally changed or removed; refusing to overwrite them")
        print(f"✓ Upstream provider baseline remains {provider['repository']}@{provider['version']}.")
        return

    gh = find_gh(provider)
    old_records = state["skills"]
    if not isinstance(old_records, dict):
        raise ProviderError("provider state skills must be an object")
    for name, record in old_records.items():
        if not isinstance(record, dict):
            raise ProviderError(f"invalid old provider record for {name}")
        if record.get("origin") == "created" and not checksums_match(root, name, record):
            raise ProviderError(f"locally changed provider skill blocks upgrade: .agents/skills/{name}")
        if record.get("origin") == "preexisting-compatible" and name in {str(item["name"]) for item in skills}:
            raise ProviderError(
                f"pre-existing provider skill {name} is not framework-owned; reinstall it at {provider['version']} explicitly, then rerun update"
            )
    if dry_run:
        print(f"PROVIDERS UPDATE DRY RUN for {root}")
        print(f"  - stage {len(skills)} pinned skills with {gh}")
        print(f"  - replace only checksum-clean framework-created provider directories")
        print(f"  - record compatible baseline {provider['repository']}@{provider['version']}")
        print("No provider files changed.")
        return

    with tempfile.TemporaryDirectory(prefix=".ai-workflow-providers-", dir=root) as temporary:
        transaction = Path(temporary)
        staged = transaction / ".agents" / "skills"
        backups = transaction / "backups"
        staged.mkdir(parents=True)
        backups.mkdir()
        for skill in skills:
            run_gh_install(gh, root, provider, skill, directory=staged)
            verify_skill(transaction, provider, skill)

        new_records: Dict[str, Mapping[str, object]] = {}
        moved_new: List[Path] = []
        backed_up: List[Tuple[Path, Path]] = []
        try:
            for name, record in old_records.items():
                if not isinstance(record, dict) or record.get("origin") != "created":
                    continue
                destination = skill_directory(root, name)
                backup = backups / name
                destination.replace(backup)
                backed_up.append((destination, backup))
            for skill in skills:
                name = str(skill["name"])
                destination = skill_directory(root, name)
                if destination.exists() or destination.is_symlink():
                    verify_skill(root, provider, skill)
                    origin = "preexisting-compatible"
                    files = verify_skill(root, provider, skill)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    (staged / name).replace(destination)
                    moved_new.append(destination)
                    origin = "created"
                    files = verify_skill(root, provider, skill)
                new_records[name] = {
                    "files": files,
                    "origin": origin,
                    "path": skill["path"],
                    "tree_sha": skill["tree_sha"],
                }
            atomic_json(state_path, state_value(provider, new_records))
        except BaseException:
            for destination in reversed(moved_new):
                if destination.exists() and not destination.is_symlink():
                    remove_tree(destination, root)
            for destination, backup in reversed(backed_up):
                if not destination.exists() and backup.exists():
                    backup.replace(destination)
            raise
    if not command_status(root, verbose=False):
        raise ProviderError("post-update provider verification failed")
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
    for name, record in sorted(records.items()):
        if not isinstance(record, dict):
            raise ProviderError(f"invalid provider record for {name}")
        if record.get("origin") == "preexisting-compatible":
            actions.append(f"preserve pre-existing compatible provider skill {name}")
        elif checksums_match(root, name, record):
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
    for directory in removals:
        remove_tree(directory, root)
    state_path.unlink()
    print("✓ Upstream provider lifecycle state removed; pre-existing or changed skills were preserved.")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "update", "status", "remove"))
    parser.add_argument("target", nargs="?", default=Path.cwd(), type=Path)
    parser.add_argument("--dry-run", action="store_true", help="show the provider operation without changing files")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
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
