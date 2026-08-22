#!/usr/bin/env python3
"""Offline projection and inspection of bundled optional provider skills."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
from typing import Iterable

from provider_snapshot import (
    SnapshotTreeError,
    tree_digest,
    validate_local_references,
    validate_tree_shape,
)


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DECLARATION = PACKAGE_ROOT / "payload" / "agent-workflow" / "providers.json"
MINIMUM_PYTHON = (3, 11)


class ProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderSkill:
    name: str
    path: str
    invocation: dict[str, str]
    adapter: str | None
    upstream_body_sha256: str | None
    projection_source: Path | None


@dataclass(frozen=True)
class Provider:
    repository: str
    version: str
    resolved_commit: str
    snapshot_root: Path
    skills: tuple[ProviderSkill, ...]


WAYFINDER_ADAPTER = "wayfinder-runtime-projection-v1"
IMPLICIT_INVOCATION_ADAPTER = "implicit-invocation-v1"
def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except (AttributeError, OSError, ValueError):
                pass


def safe_component(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or PurePosixPath(value).name != value:
        raise ProviderError(f"invalid {label}: {value!r}")
    return value


def package_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ProviderError(f"invalid {label}: {value!r}")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ProviderError(f"invalid {label}: {value!r}")
    return PACKAGE_ROOT.joinpath(*relative.parts)


def is_sha(value: object, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and not any(character not in "0123456789abcdef" for character in value)
    )


def load_provider() -> Provider:
    if DECLARATION.is_symlink() or not DECLARATION.is_file():
        raise ProviderError("provider declaration is missing or unsafe")
    try:
        raw = json.loads(DECLARATION.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProviderError(f"cannot read provider declaration: {exc}") from exc
    provider = raw.get("provider") if isinstance(raw, dict) else None
    if not isinstance(raw, dict) or raw.get("schema_version") != 7:
        raise ProviderError("unsupported provider declaration")
    if not isinstance(provider, dict):
        raise ProviderError("provider declaration needs a provider object")
    repository = provider.get("repository")
    version = provider.get("version")
    resolved_commit = provider.get("resolved_commit")
    snapshot = provider.get("snapshot")
    skills = provider.get("skills")
    if not isinstance(repository, str) or repository.count("/") != 1:
        raise ProviderError("provider repository must use owner/name form")
    if not isinstance(version, str) or not version:
        raise ProviderError("provider version must be a non-empty pinned tag")
    if not is_sha(resolved_commit, 40):
        raise ProviderError("provider resolved commit must be a 40-character Git object ID")
    if not isinstance(snapshot, dict):
        raise ProviderError("provider snapshot declaration is incomplete")
    snapshot_root = package_path(snapshot.get("path"), "provider snapshot path")
    if not isinstance(skills, list):
        raise ProviderError("provider skills must be an array")
    hosts = raw.get("hosts")
    if not isinstance(hosts, dict) or not hosts:
        raise ProviderError("provider declaration needs hosts")
    configuration = raw.get("configuration")
    if not isinstance(configuration, dict):
        raise ProviderError("provider declaration needs configuration definitions")
    configuration_names = set(configuration)
    result: list[ProviderSkill] = []
    for item in skills:
        if not isinstance(item, dict):
            raise ProviderError("provider skill entries must be objects")
        name = safe_component(item.get("name"), "provider skill name")
        path = item.get("path")
        if not isinstance(path, str):
            raise ProviderError(f"provider skill {name} needs a path")
        relative = PurePosixPath(path)
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise ProviderError(f"provider skill {name} has an unsafe path")
        invocation = item.get("invocation")
        if not isinstance(invocation, dict) or set(invocation) != set(hosts):
            raise ProviderError(f"provider skill {name} invocation hosts differ from declaration")
        if not all(
            isinstance(policy, str) and policy in {"implicit", "user-only", "unavailable"}
            for policy in invocation.values()
        ):
            raise ProviderError(f"provider skill {name} has an invalid invocation policy")
        requirements = item.get("requires_configuration")
        if (
            not isinstance(requirements, list)
            or not all(isinstance(requirement, str) for requirement in requirements)
            or len(requirements) != len(set(requirements))
            or not all(requirement in configuration_names for requirement in requirements)
        ):
            raise ProviderError(f"provider skill {name} has invalid configuration requirements")
        adapter = item.get("agentic_workflow_adapter")
        adapter_name: str | None = None
        upstream_body_sha256: str | None = None
        projection_source: Path | None = None
        if adapter is not None:
            if not isinstance(adapter, dict):
                raise ProviderError(f"provider skill {name} has an invalid Agent Workflow adapter")
            adapter_name = adapter.get("name")
            if adapter_name == WAYFINDER_ADAPTER:
                upstream_body_sha256 = adapter.get("upstream_body_sha256")
                projection_source = package_path(
                    adapter.get("projection_source"),
                    f"provider skill {name} projection source",
                )
                valid = (
                    set(adapter) == {"name", "projection_source", "upstream_body_sha256"}
                    and name == "wayfinder"
                    and isinstance(upstream_body_sha256, str)
                    and len(upstream_body_sha256) == 64
                    and not any(
                        character not in "0123456789abcdef"
                        for character in upstream_body_sha256
                    )
                )
            else:
                valid = (
                    adapter_name == IMPLICIT_INVOCATION_ADAPTER
                    and set(adapter) == {"name"}
                )
            if not valid:
                raise ProviderError(f"provider skill {name} has an unsupported Agent Workflow adapter")
        if adapter_name and (
            invocation.get("codex") != "implicit"
            or invocation.get("github-copilot") != "implicit"
            or invocation.get("claude-code") != "unavailable"
        ):
            raise ProviderError(
                f"provider skill {name} adapter does not match supported host policies"
            )
        result.append(
            ProviderSkill(
                name,
                path,
                invocation,
                adapter_name,
                upstream_body_sha256,
                projection_source,
            )
        )
    if len({skill.name for skill in result}) != len(result):
        raise ProviderError("provider skill names must be unique")
    return Provider(
        repository,
        version,
        resolved_commit,
        snapshot_root,
        tuple(result),
    )


def validate_root(raw: Path) -> Path:
    if not raw.exists() or raw.is_symlink() or not raw.is_dir():
        raise ProviderError(f"target must be an existing regular directory: {raw}")
    root = raw.resolve()
    if root.parent == root:
        raise ProviderError("refusing to use a filesystem root as the project target")
    for relative in (Path(".agents"), Path(".agents/skills")):
        path = root / relative
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise ProviderError(f"optional provider destination is unsafe: {relative}")
    return root


def destination_state(root: Path, name: str) -> str:
    directory = root / ".agents" / "skills" / name
    if not directory.exists() and not directory.is_symlink():
        return "missing"
    if directory.is_symlink() or not directory.is_dir():
        return "incompatible"
    skill = directory / "SKILL.md"
    if skill.is_symlink() or not skill.is_file():
        return "incompatible"
    return "present"


def validate_staged_skill(
    root: Path,
    skill: ProviderSkill,
    repository: str,
    version: str,
) -> None:
    if destination_state(root, skill.name) != "present":
        raise ProviderError(f"staged provider skill {skill.name} is missing or unusable")
    directory = root / ".agents" / "skills" / skill.name
    skill_file = directory / "SKILL.md"
    try:
        text = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ProviderError(f"cannot read staged provider skill {skill.name}: {exc}") from exc
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ProviderError(f"staged provider skill {skill.name} lacks valid frontmatter")
    frontmatter = text[4 : text.index("\n---\n", 4)]
    required = (
        f"name: {skill.name}",
        f"    github-path: {skill.path}",
        f"    github-pinned: {version}",
        f"    github-repo: https://github.com/{repository}",
    )
    if any(line not in frontmatter.splitlines() for line in required):
        raise ProviderError(f"staged provider skill {skill.name} has incompatible source metadata")

    openai = directory / "agents" / "openai.yaml"
    if openai.is_symlink() or not openai.is_file():
        raise ProviderError(f"staged provider skill {skill.name} lacks Codex metadata")
    try:
        openai_text = openai.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ProviderError(f"cannot read Codex metadata for {skill.name}: {exc}") from exc

    github_policy = skill.invocation["github-copilot"]
    if github_policy == "user-only" and "disable-model-invocation: true" not in frontmatter:
        raise ProviderError(f"staged provider skill {skill.name} lacks GitHub Copilot user-only metadata")
    if github_policy == "implicit" and "disable-model-invocation: true" in frontmatter:
        raise ProviderError(f"staged provider skill {skill.name} blocks GitHub Copilot implicit invocation")

    codex_policy = skill.invocation["codex"]
    if codex_policy == "user-only" and "allow_implicit_invocation: false" not in openai_text:
        raise ProviderError(f"staged provider skill {skill.name} lacks Codex user-only metadata")
    if codex_policy == "implicit" and "allow_implicit_invocation: false" in openai_text:
        raise ProviderError(f"staged provider skill {skill.name} blocks Codex implicit invocation")


def adapter_plan(
    root: Path,
    skill: ProviderSkill,
    repository: str,
    version: str,
) -> list[tuple[Path, bytes, bytes]]:
    """Return validated rewrites for a declared Agent Workflow adapter."""
    if not skill.adapter:
        return []
    if skill.adapter == IMPLICIT_INVOCATION_ADAPTER:
        return implicit_invocation_adapter_plan(root, skill, repository, version)
    if (
        skill.adapter != WAYFINDER_ADAPTER
        or skill.upstream_body_sha256 is None
        or skill.projection_source is None
    ):
        raise ProviderError(f"provider skill {skill.name} has an unsupported Agent Workflow adapter")
    if destination_state(root, skill.name) != "present":
        raise ProviderError(f"provider skill {skill.name} is not safe to adapt")

    directory = root / ".agents" / "skills" / skill.name
    skill_path = directory / "SKILL.md"
    if skill_path.is_symlink() or not skill_path.is_file():
        raise ProviderError(f"provider skill {skill.name} instructions are missing or unsafe")
    original_skill = skill_path.read_bytes()
    if not original_skill.startswith(b"---\n"):
        raise ProviderError(f"provider skill {skill.name} lacks valid frontmatter")
    separator = original_skill.find(b"\n---\n", 4)
    if separator < 0:
        raise ProviderError(f"provider skill {skill.name} lacks valid frontmatter")
    body_start = separator + len(b"\n---\n")
    frontmatter = original_skill[4:separator]
    required_source = (
        f"    github-path: {skill.path}\n".encode("utf-8"),
        f"    github-pinned: {version}\n".encode("utf-8"),
        f"    github-repo: https://github.com/{repository}\n".encode("utf-8"),
    )
    if any(frontmatter.count(line) != 1 for line in required_source):
        raise ProviderError(f"provider skill {skill.name} has incompatible source metadata")

    upstream_body = original_skill[body_start:]
    if b"<!-- agent-workflow:wayfinder-" in upstream_body:
        raise ProviderError(f"provider skill {skill.name} has unexpected projection markers")
    if sha256(upstream_body).hexdigest() != skill.upstream_body_sha256:
        raise ProviderError(f"provider skill {skill.name} has an unexpected pinned method body")

    if skill.projection_source.is_symlink() or not skill.projection_source.is_file():
        raise ProviderError(f"provider skill {skill.name} runtime projection is missing or unsafe")
    try:
        projection_body = skill.projection_source.read_bytes()
        projection_body.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise ProviderError(
            f"cannot read runtime projection for provider skill {skill.name}: {exc}"
        ) from exc
    if (
        not projection_body.startswith(b"# Wayfinder\n")
        or not projection_body.endswith(b"\n")
        or b"\n---\n" in projection_body
    ):
        raise ProviderError(f"provider skill {skill.name} runtime projection is malformed")

    desired_skill = original_skill[:body_start] + projection_body
    replacements = (
        (
            skill_path,
            (
                (
                    (
                        "description: Plan a huge chunk of work — more than one agent session can hold — "
                        "as a shared map of decision tickets on your issue tracker, and resolve them one at "
                        "a time until the way to the destination is clear.\n"
                    ).encode("utf-8"),
                    (
                        "description: Keep a lightweight structured map when important unknowns, decisions, "
                        "dependencies, blockers, or conflicting facts are becoming unreliable to hold in "
                        "ordinary context.\n"
                    ).encode("utf-8"),
                ),
                (
                    b"disable-model-invocation: true\n",
                    b"disable-model-invocation: false\n",
                ),
            ),
        ),
        (
            directory / "agents" / "openai.yaml",
            (
                (
                    b"  short_description: \"Map a large effort as decision tickets\"\n",
                    b"  short_description: \"Keep a lightweight map of complicated work\"\n",
                ),
                (
                    b"  allow_implicit_invocation: false\n",
                    b"  allow_implicit_invocation: true\n",
                ),
            ),
        ),
    )
    plan: list[tuple[Path, bytes, bytes]] = []
    for path, rules in replacements:
        if path.is_symlink() or not path.is_file():
            raise ProviderError(
                f"provider skill {skill.name} invocation metadata is missing or unsafe: "
                f"{path.relative_to(directory)}"
            )
        original = path.read_bytes()
        desired = desired_skill if path == skill_path else original
        for upstream_line, adapted_line in rules:
            if desired.count(upstream_line) != 1 or adapted_line in desired:
                raise ProviderError(
                    f"provider skill {skill.name} has unexpected invocation metadata in "
                    f"{path.relative_to(directory)}"
                )
            desired = desired.replace(upstream_line, adapted_line, 1)
        plan.append((path, original, desired))
    return plan


def implicit_invocation_adapter_plan(
    root: Path,
    skill: ProviderSkill,
    repository: str,
    version: str,
) -> list[tuple[Path, bytes, bytes]]:
    """Make a pinned user-only provider skill model-invocable on supported hosts."""
    if destination_state(root, skill.name) != "present":
        raise ProviderError(f"provider skill {skill.name} is not safe to adapt")

    directory = root / ".agents" / "skills" / skill.name
    skill_path = directory / "SKILL.md"
    openai_path = directory / "agents" / "openai.yaml"
    if skill_path.is_symlink() or not skill_path.is_file():
        raise ProviderError(f"provider skill {skill.name} instructions are missing or unsafe")
    if openai_path.is_symlink() or not openai_path.is_file():
        raise ProviderError(f"provider skill {skill.name} Codex metadata is missing or unsafe")

    original_skill = skill_path.read_bytes()
    if not original_skill.startswith(b"---\n"):
        raise ProviderError(f"provider skill {skill.name} lacks valid frontmatter")
    separator = original_skill.find(b"\n---\n", 4)
    if separator < 0:
        raise ProviderError(f"provider skill {skill.name} lacks valid frontmatter")
    frontmatter = original_skill[4:separator]
    required_source = (
        f"    github-path: {skill.path}\n".encode("utf-8"),
        f"    github-pinned: {version}\n".encode("utf-8"),
        f"    github-repo: https://github.com/{repository}\n".encode("utf-8"),
    )
    if any(frontmatter.count(line) != 1 for line in required_source):
        raise ProviderError(f"provider skill {skill.name} has incompatible source metadata")

    plan: list[tuple[Path, bytes, bytes]] = []
    replacements = (
        (
            skill_path,
            b"disable-model-invocation: true\n",
            b"disable-model-invocation: false\n",
        ),
        (
            openai_path,
            b"  allow_implicit_invocation: false\n",
            b"  allow_implicit_invocation: true\n",
        ),
    )
    for path, upstream_line, adapted_line in replacements:
        original = path.read_bytes()
        if original.count(upstream_line) != 1 or adapted_line in original:
            raise ProviderError(
                f"provider skill {skill.name} has unexpected invocation metadata in "
                f"{path.relative_to(directory)}"
            )
        desired = original.replace(upstream_line, adapted_line, 1)
        plan.append((path, original, desired))
    return plan


def apply_adapter(
    root: Path,
    skill: ProviderSkill,
    repository: str,
    version: str,
) -> bool:
    plan = adapter_plan(root, skill, repository, version)
    changed = [(path, original, desired) for path, original, desired in plan if original != desired]
    if not changed:
        return False
    try:
        for path, _original, desired in changed:
            path.write_bytes(desired)
    except OSError as exc:
        raise ProviderError(f"cannot apply Agent Workflow adapter for {skill.name}: {exc}") from exc
    return True


def validate_snapshot(provider: Provider) -> None:
    expected = {skill.name for skill in provider.skills}
    if provider.snapshot_root.is_symlink() or not provider.snapshot_root.is_dir():
        raise ProviderError("bundled provider snapshot is missing or unsafe")
    actual = {path.name for path in provider.snapshot_root.iterdir()}
    if actual != expected:
        raise ProviderError("bundled provider inventory differs from the declaration")
    try:
        validate_tree_shape(provider.snapshot_root)
        for skill in provider.skills:
            validate_local_references(provider.snapshot_root / skill.name)
    except SnapshotTreeError as exc:
        raise ProviderError(str(exc)) from exc


def prepare_staged_projection(staging_root: Path, provider: Provider) -> Path:
    validate_snapshot(provider)
    staged_skills = staging_root / ".agents" / "skills"
    staged_skills.mkdir(parents=True)
    for skill in provider.skills:
        shutil.copytree(provider.snapshot_root / skill.name, staged_skills / skill.name)
    for skill in provider.skills:
        if skill.adapter:
            apply_adapter(
                staging_root,
                skill,
                provider.repository,
                provider.version,
            )
        validate_staged_skill(
            staging_root,
            skill,
            provider.repository,
            provider.version,
        )
    return staged_skills


def projection_state(root: Path, staged_skills: Path, skill: ProviderSkill) -> str:
    directory = root / ".agents" / "skills" / skill.name
    if not directory.exists() and not directory.is_symlink():
        return "repairable"
    if directory.is_symlink() or not directory.is_dir():
        return "blocked"
    try:
        matches = tree_digest(directory) == tree_digest(staged_skills / skill.name)
    except (OSError, SnapshotTreeError):
        return "blocked"
    return "ready" if matches else "repairable"


def move_path(source: Path, destination: Path) -> None:
    """Rename one path; kept separate so rollback behavior can be fault-tested."""
    source.replace(destination)


def rollback_moves(moves: list[tuple[Path, Path]]) -> list[str]:
    """Restore `(current, original)` paths in reverse transaction order."""
    errors: list[str] = []
    for current, original in reversed(moves):
        if original.exists() or original.is_symlink():
            errors.append(f"{original}: rollback destination is occupied")
            continue
        try:
            move_path(current, original)
        except OSError as exc:
            errors.append(f"{original}: {exc}")
    return errors


def cleanup_recovery_directory(path: Path) -> str | None:
    try:
        shutil.rmtree(path)
    except OSError as exc:
        return f"recovery cleanup failed at {path}: {exc}"
    return None


def replace_projection(
    root: Path,
    staged_skills: Path,
    skills: list[ProviderSkill],
) -> list[ProviderSkill]:
    destinations = root / ".agents" / "skills"
    if destinations.is_symlink() or (destinations.exists() and not destinations.is_dir()):
        raise ProviderError("optional provider destination became unsafe during staging")
    states = {skill.name: projection_state(root, staged_skills, skill) for skill in skills}
    blocked = [skill.name for skill in skills if states[skill.name] == "blocked"]
    if blocked:
        raise ProviderError(
            "provider destinations became unsafe during staging: " + ", ".join(blocked)
        )
    changed = [skill for skill in skills if states[skill.name] == "repairable"]
    if not changed:
        return []
    destinations.mkdir(parents=True, exist_ok=True)

    rollback_root = Path(
        tempfile.mkdtemp(prefix=".agent-workflow-provider-rollback-", dir=root)
    )
    backed_up: list[tuple[Path, Path]] = []
    installed: list[tuple[Path, Path]] = []
    try:
        for skill in changed:
            destination = destinations / skill.name
            if destination.exists():
                backup = rollback_root / skill.name
                move_path(destination, backup)
                backed_up.append((backup, destination))
        for skill in changed:
            source = staged_skills / skill.name
            destination = destinations / skill.name
            move_path(source, destination)
            installed.append((destination, source))
    except OSError as exc:
        rollback_errors = rollback_moves(installed)
        rollback_errors.extend(rollback_moves(backed_up))
        if rollback_errors:
            detail = f"; rollback incomplete; preserved recovery data at {rollback_root}: " + ", ".join(
                rollback_errors
            )
        else:
            detail = "; prior projection restored"
            cleanup_error = cleanup_recovery_directory(rollback_root)
            if cleanup_error:
                detail += f"; {cleanup_error}"
        raise ProviderError(f"cannot replace bundled provider skills: {exc}{detail}") from exc
    cleanup_error = cleanup_recovery_directory(rollback_root)
    if cleanup_error:
        print(
            f"WARNING: Provider replacement committed; {cleanup_error}",
            file=sys.stderr,
        )
    return changed


def remove_projection(root: Path, skills: list[ProviderSkill]) -> list[ProviderSkill]:
    destinations = root / ".agents" / "skills"
    if destinations.is_symlink() or (destinations.exists() and not destinations.is_dir()):
        raise ProviderError("optional provider destination is unsafe")
    present: list[ProviderSkill] = []
    for skill in skills:
        destination = destinations / skill.name
        if not destination.exists() and not destination.is_symlink():
            continue
        if destination.is_symlink() or not destination.is_dir():
            raise ProviderError(f"provider destination is unsafe: {skill.name}")
        present.append(skill)
    if not present:
        return []

    removal_root = Path(tempfile.mkdtemp(prefix=".agent-workflow-provider-remove-", dir=root))
    moved: list[tuple[Path, Path]] = []
    try:
        for skill in present:
            source = destinations / skill.name
            backup = removal_root / skill.name
            move_path(source, backup)
            moved.append((backup, source))
    except OSError as exc:
        rollback_errors = rollback_moves(moved)
        if rollback_errors:
            detail = f"; rollback incomplete; preserved recovery data at {removal_root}: " + ", ".join(
                rollback_errors
            )
        else:
            detail = "; prior projection restored"
            cleanup_error = cleanup_recovery_directory(removal_root)
            if cleanup_error:
                detail += f"; {cleanup_error}"
        raise ProviderError(f"cannot remove bundled provider skills: {exc}{detail}") from exc
    cleanup_error = cleanup_recovery_directory(removal_root)
    if cleanup_error:
        print(f"WARNING: Provider removal committed; {cleanup_error}", file=sys.stderr)
    return present


def status(root: Path) -> int:
    provider = load_provider()
    with tempfile.TemporaryDirectory(prefix="agent-workflow-provider-status-") as temporary:
        staged_skills = prepare_staged_projection(Path(temporary), provider)
        states = {
            skill.name: projection_state(root, staged_skills, skill)
            for skill in provider.skills
        }
    ready = sum(state == "ready" for state in states.values())
    repairable = sum(state == "repairable" for state in states.values())
    blocked = sum(state == "blocked" for state in states.values())
    print(
        f"Optional provider: {provider.repository}@{provider.version} "
        f"({provider.resolved_commit})"
    )
    print(
        f"Optional provider skills: {ready} ready, {repairable} repairable, {blocked} blocked"
    )
    if repairable:
        print("INFO: Rerun install or update to restore the complete bundled projection.")
    if blocked:
        names = ", ".join(name for name, state in states.items() if state == "blocked")
        print(f"WARNING: Unsafe provider destinations block lifecycle changes: {names}")
    return 1 if repairable or blocked else 0


def install(root: Path, dry_run: bool) -> int:
    provider = load_provider()
    temporary_arguments = {"prefix": ".agent-workflow-providers-"}
    if not dry_run:
        temporary_arguments["dir"] = root
    with tempfile.TemporaryDirectory(**temporary_arguments) as temporary:
        staged_skills = prepare_staged_projection(Path(temporary), provider)
        states = {
            skill.name: projection_state(root, staged_skills, skill)
            for skill in provider.skills
        }
        blocked = [skill for skill in provider.skills if states[skill.name] == "blocked"]
        repairable = [skill for skill in provider.skills if states[skill.name] == "repairable"]
        ready = [skill for skill in provider.skills if states[skill.name] == "ready"]

        for skill in blocked:
            print(f"blocked unsafe optional provider skill {skill.name}", file=sys.stderr)
        if blocked:
            print("WARNING: No provider changes were made because the projection is blocked.", file=sys.stderr)
            return 1
        if dry_run:
            for skill in repairable:
                print(f"would reconcile bundled optional provider skill {skill.name}")
            for skill in ready:
                print(f"would reuse exact optional provider skill {skill.name}")
            return 0

        changed = replace_projection(root, staged_skills, list(provider.skills))
        changed_names = {skill.name for skill in changed}
        for skill in provider.skills:
            if skill.name not in changed_names:
                print(f"reuse exact optional provider skill {skill.name}")
                continue
            print(
                f"reconciled optional provider skill {skill.name} from bundled "
                f"{provider.repository}@{provider.version} ({provider.resolved_commit})"
            )

    print("OK: Optional provider skills match the bundled projection.")
    return 0


def remove(root: Path, dry_run: bool) -> int:
    provider = load_provider()
    if dry_run:
        present: list[ProviderSkill] = []
        for skill in provider.skills:
            destination = root / ".agents" / "skills" / skill.name
            if not destination.exists() and not destination.is_symlink():
                continue
            if destination.is_symlink() or not destination.is_dir():
                raise ProviderError(f"provider destination is unsafe: {skill.name}")
            present.append(skill)
        if present:
            print(
                "would remove declared optional provider directories: "
                + ", ".join(skill.name for skill in present)
            )
    else:
        removed = remove_projection(root, list(provider.skills))
        if removed:
            print(
                "removed declared optional provider directories: "
                + ", ".join(skill.name for skill in removed)
            )
    print("OK: Unrelated .agents/skills directories were preserved.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install", "status", "remove"))
    parser.add_argument("target", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    configure_console()
    if sys.version_info < MINIMUM_PYTHON:
        print("ERROR: Agent Workflow requires Python 3.11 or newer", file=sys.stderr)
        return 2
    try:
        args = build_parser().parse_args(argv)
        root = validate_root(args.target)
        if args.command == "status":
            if args.dry_run:
                raise ProviderError("status does not accept --dry-run")
            return status(root)
        if args.command == "remove":
            return remove(root, args.dry_run)
        return install(root, args.dry_run)
    except ProviderError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
