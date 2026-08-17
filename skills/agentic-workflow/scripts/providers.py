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

from provider_snapshot import SnapshotTreeError, tree_digest, validate_local_references


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DECLARATION = PACKAGE_ROOT / "payload" / "ai-workflow" / "providers.json"
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


@dataclass(frozen=True)
class Provider:
    repository: str
    version: str
    resolved_commit: str
    snapshot_root: Path
    snapshot_sha256: str
    license_path: Path
    license_sha256: str
    skills: tuple[ProviderSkill, ...]


WAYFINDER_ADAPTER = "wayfinder-local-state-v1"
IMPLICIT_INVOCATION_ADAPTER = "implicit-invocation-v1"
WAYFINDER_ADAPTER_BEGIN = b"<!-- agentic-workflow:wayfinder-local-state-v1:begin -->\n"
WAYFINDER_ADAPTER_END = b"<!-- agentic-workflow:wayfinder-local-state-v1:end -->\n\n"
WAYFINDER_LOCAL_MODE = WAYFINDER_ADAPTER_BEGIN + b"""## Agentic Workflow local mode (authoritative)

Use this section when `.ai-workflow/contracts/wayfinder-state.md` exists. Read
that contract when Wayfinder is selected. Before an authorized durable-state
write, also read `.ai-workflow/contracts/durable-state.md`. These rules override
incompatible tracker-specific mechanics below. If the local contract is absent,
ignore this section and use the unchanged upstream method normally.

- Agentic Workflow decides when local Wayfinder is selected. Explicit use is
  still allowed; an explicit opt-out prevents automatic selection. Bounded
  debugging, one isolated unknown, and unrelated work keep their normal route.
- The only canonical local representation is
  `.ai-workflow-state/wayfinder/<effort>/`: `map.md`, `unknowns/U#`,
  `decisions/D#`, and `tickets/T#`. Never create `.scratch/`, an external issue
  tracker copy, or `.ai-workflow-state/active.md`; do not run setup to provision
  a tracker for this mode.
- Preserve the upstream reasoning method: orient around a destination, keep the
  map low resolution, represent fog honestly, resolve consequential uncertainty
  incrementally, progressively load detail, and derive the frontier from current
  status and dependencies.
- Map a sharp decision, investigation, research, prototype, grilling, or human
  clarification question to U#. Update that U# with evidence and resolution.
  Create or update D# only when the answer is a durable project decision. Create
  T# only for concrete executable work when decomposition adds value. An
  upstream `task` ticket becomes T# only when it is truly executable work, often
  linked to the U# it unblocks. Never force U# -> D# -> T# as ceremony.
- Wayfinder owns durable coordination, not every action. Debugging, Research,
  Prototype, Grilling, Domain Modeling, human clarification, and Implementation
  may resolve or consume an item while the map remains canonical. Mid-task
  escalation does not erase a useful specialized workflow, and charting does
  not require stopping when authorized, bounded work can safely continue.
- Use Grilling and Domain Modeling when destination or domain ambiguity actually
  needs live human clarification or a sharper domain model. Do not invoke them
  ceremonially for a clear mid-task escalation or resume. Grilling is human in
  the loop; never invent the human side of it.
- Read-only analysis, audit, diagnosis, or review may use Wayfinder reasoning
  but must not create or update state. On resume, load the relevant `map.md`
  first and only the needed U/D/T children. Live/source evidence wins over stale
  state; preserve history and reconcile affected files explicitly.
- Tracker labels, assignment/claiming, issue comments/closing, and tracker-native
  blocking below do not apply in local mode. Before a write, reread the target
  and map, allocate the next unused per-type ID, and never overwrite a concurrent
  file or silently merge conflicting evidence.

""" + WAYFINDER_ADAPTER_END
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
    if not isinstance(raw, dict) or raw.get("schema_version") != 6:
        raise ProviderError("unsupported provider declaration")
    if not isinstance(provider, dict):
        raise ProviderError("provider declaration needs a provider object")
    repository = provider.get("repository")
    version = provider.get("version")
    resolved_commit = provider.get("resolved_commit")
    tag_object = provider.get("tag_object")
    upstream_tree = provider.get("upstream_tree")
    snapshot = provider.get("snapshot")
    license_info = provider.get("license")
    skills = provider.get("skills")
    if not isinstance(repository, str) or repository.count("/") != 1:
        raise ProviderError("provider repository must use owner/name form")
    if not isinstance(version, str) or not version:
        raise ProviderError("provider version must be a non-empty pinned tag")
    if not is_sha(resolved_commit, 40):
        raise ProviderError("provider resolved commit must be a 40-character Git object ID")
    if not is_sha(tag_object, 40) or not is_sha(upstream_tree, 40):
        raise ProviderError("provider tag and tree provenance must use 40-character Git object IDs")
    if not isinstance(snapshot, dict) or set(snapshot) != {"path", "sha256"}:
        raise ProviderError("provider snapshot declaration is incomplete")
    snapshot_root = package_path(snapshot.get("path"), "provider snapshot path")
    snapshot_sha256 = snapshot.get("sha256")
    if not is_sha(snapshot_sha256, 64):
        raise ProviderError("provider snapshot checksum must be a SHA-256 digest")
    if not isinstance(license_info, dict) or set(license_info) != {"name", "path", "sha256"}:
        raise ProviderError("provider license declaration is incomplete")
    if license_info.get("name") != "MIT":
        raise ProviderError("provider snapshot must declare its MIT license")
    license_path = package_path(license_info.get("path"), "provider license path")
    license_sha256 = license_info.get("sha256")
    if not is_sha(license_sha256, 64):
        raise ProviderError("provider license checksum must be a SHA-256 digest")
    if not isinstance(skills, list):
        raise ProviderError("provider skills must be an array")
    hosts = raw.get("hosts")
    if not isinstance(hosts, dict) or not hosts:
        raise ProviderError("provider declaration needs hosts")
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
        adapter = item.get("agentic_workflow_adapter")
        adapter_name: str | None = None
        upstream_body_sha256: str | None = None
        if adapter is not None:
            if not isinstance(adapter, dict):
                raise ProviderError(f"provider skill {name} has an invalid Agentic Workflow adapter")
            adapter_name = adapter.get("name")
            if adapter_name == WAYFINDER_ADAPTER:
                upstream_body_sha256 = adapter.get("upstream_body_sha256")
                valid = (
                    set(adapter) == {"name", "upstream_body_sha256"}
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
                raise ProviderError(f"provider skill {name} has an unsupported Agentic Workflow adapter")
        if adapter_name and (
            invocation.get("codex") != "implicit"
            or invocation.get("github-copilot") != "implicit"
            or invocation.get("claude-code") != "unavailable"
        ):
            raise ProviderError(
                f"provider skill {name} adapter does not match supported host policies"
            )
        result.append(ProviderSkill(name, path, invocation, adapter_name, upstream_body_sha256))
    if len({skill.name for skill in result}) != len(result):
        raise ProviderError("provider skill names must be unique")
    return Provider(
        repository,
        version,
        resolved_commit,
        snapshot_root,
        snapshot_sha256,
        license_path,
        license_sha256,
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
    """Return validated rewrites for a declared Agentic Workflow adapter."""
    if not skill.adapter:
        return []
    if skill.adapter == IMPLICIT_INVOCATION_ADAPTER:
        return implicit_invocation_adapter_plan(root, skill, repository, version)
    if skill.adapter != WAYFINDER_ADAPTER or skill.upstream_body_sha256 is None:
        raise ProviderError(f"provider skill {skill.name} has an unsupported Agentic Workflow adapter")
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
    if WAYFINDER_ADAPTER_BEGIN in upstream_body or WAYFINDER_ADAPTER_END in upstream_body:
        raise ProviderError(f"provider skill {skill.name} has unexpected local-mode adapter markers")
    if sha256(upstream_body).hexdigest() != skill.upstream_body_sha256:
        raise ProviderError(f"provider skill {skill.name} has an unexpected pinned method body")

    desired_skill = original_skill[:body_start] + WAYFINDER_LOCAL_MODE + upstream_body
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
        raise ProviderError(f"cannot apply Agentic Workflow adapter for {skill.name}: {exc}") from exc
    return True


def validate_snapshot(provider: Provider) -> None:
    if provider.license_path.is_symlink() or not provider.license_path.is_file():
        raise ProviderError("bundled provider license is missing or unsafe")
    license_bytes = provider.license_path.read_bytes()
    if sha256(license_bytes).hexdigest() != provider.license_sha256 or b"MIT License" not in license_bytes:
        raise ProviderError("bundled provider license differs from the declaration")
    expected = {skill.name for skill in provider.skills}
    if provider.snapshot_root.is_symlink() or not provider.snapshot_root.is_dir():
        raise ProviderError("bundled provider snapshot is missing or unsafe")
    actual = {path.name for path in provider.snapshot_root.iterdir()}
    if actual != expected:
        raise ProviderError("bundled provider inventory differs from the declaration")
    try:
        digest = tree_digest(provider.snapshot_root)
        for skill in provider.skills:
            validate_local_references(provider.snapshot_root / skill.name)
    except SnapshotTreeError as exc:
        raise ProviderError(str(exc)) from exc
    if digest != provider.snapshot_sha256:
        raise ProviderError("bundled provider snapshot checksum differs from the declaration")


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
    state = destination_state(root, skill.name)
    if state == "missing":
        return "missing"
    if state != "present":
        return "conflict"
    try:
        matches = tree_digest(root / ".agents" / "skills" / skill.name) == tree_digest(
            staged_skills / skill.name
        )
    except (OSError, SnapshotTreeError):
        return "conflict"
    return "ready" if matches else "conflict"


def project_missing(root: Path, staged_skills: Path, missing: list[ProviderSkill]) -> None:
    destinations = root / ".agents" / "skills"
    if destinations.is_symlink() or (destinations.exists() and not destinations.is_dir()):
        raise ProviderError("optional provider destination became unsafe during staging")
    for skill in missing:
        if destination_state(root, skill.name) != "missing":
            raise ProviderError(f"provider destination appeared during staging: {skill.name}")
    destinations.mkdir(parents=True, exist_ok=True)

    moved: list[tuple[Path, Path]] = []
    try:
        for skill in missing:
            source = staged_skills / skill.name
            destination = destinations / skill.name
            source.replace(destination)
            moved.append((source, destination))
    except OSError as exc:
        rollback_errors: list[str] = []
        for source, destination in reversed(moved):
            try:
                destination.replace(source)
            except OSError as rollback_exc:
                rollback_errors.append(f"{destination}: {rollback_exc}")
        detail = f"; rollback failed for {', '.join(rollback_errors)}" if rollback_errors else ""
        raise ProviderError(f"cannot project bundled provider skills: {exc}{detail}") from exc


def status(root: Path) -> int:
    provider = load_provider()
    with tempfile.TemporaryDirectory(prefix="ai-workflow-provider-status-") as temporary:
        staged_skills = prepare_staged_projection(Path(temporary), provider)
        states = {
            skill.name: projection_state(root, staged_skills, skill)
            for skill in provider.skills
        }
    ready = sum(state == "ready" for state in states.values())
    missing = sum(state == "missing" for state in states.values())
    conflicts = sum(state == "conflict" for state in states.values())
    print(
        f"Optional provider: {provider.repository}@{provider.version} "
        f"({provider.resolved_commit})"
    )
    print(f"Optional provider skills: {ready} ready, {missing} missing, {conflicts} conflicts")
    if missing:
        print("INFO: Rerun install or update to project missing skills from the bundled snapshot.")
    if conflicts:
        names = ", ".join(name for name, state in states.items() if state == "conflict")
        print(f"WARNING: Differing same-named provider content was preserved: {names}")
    return 1 if missing or conflicts else 0


def install(root: Path, dry_run: bool) -> int:
    provider = load_provider()
    temporary_arguments = {"prefix": ".ai-workflow-providers-"}
    if not dry_run:
        temporary_arguments["dir"] = root
    with tempfile.TemporaryDirectory(**temporary_arguments) as temporary:
        staged_skills = prepare_staged_projection(Path(temporary), provider)
        states = {
            skill.name: projection_state(root, staged_skills, skill)
            for skill in provider.skills
        }
        conflicts = [skill for skill in provider.skills if states[skill.name] == "conflict"]
        missing = [skill for skill in provider.skills if states[skill.name] == "missing"]
        ready = [skill for skill in provider.skills if states[skill.name] == "ready"]

        for skill in ready:
            print(f"reuse exact optional provider skill {skill.name}")
        for skill in conflicts:
            print(f"preserve differing optional provider skill {skill.name}: conflict", file=sys.stderr)
        if conflicts:
            if missing:
                print(
                    "WARNING: No bundled provider skills were installed because the declared set "
                    "contains conflicts.",
                    file=sys.stderr,
                )
            return 1
        if dry_run:
            for skill in missing:
                print(f"would install bundled optional provider skill {skill.name}")
            return 0

        project_missing(root, staged_skills, missing)
        for skill in missing:
            print(
                f"installed optional provider skill {skill.name} from bundled "
                f"{provider.repository}@{provider.version} ({provider.resolved_commit})"
            )

    print("OK: Optional provider skills match the bundled projection.")
    return 0


def remove(root: Path, dry_run: bool) -> int:
    provider = load_provider()
    present: list[str] = []
    for skill in provider.skills:
        state = destination_state(root, skill.name)
        if state == "missing":
            continue
        present.append(f"{skill.name} ({state})")
    prefix = "would preserve" if dry_run else "preserved"
    if present:
        print(f"{prefix} optional provider directories: {', '.join(present)}")
    print("INFO: Provider removal is intentionally manual because v0 keeps no ownership database.")
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
        print("ERROR: Agentic Workflow requires Python 3.11 or newer", file=sys.stderr)
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
