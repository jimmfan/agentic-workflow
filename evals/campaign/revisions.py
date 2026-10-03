"""Prepare frozen historical consumers without checking out or editing source."""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile


def _git(repo: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"Git preparation could not run: {exc}") from exc
    if result.returncode:
        raise ValueError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def resolve_revision(repo: Path, ref: str) -> str:
    if not isinstance(ref, str) or not ref or ref.startswith("-") or "\x00" in ref:
        raise ValueError("revision must be a nonempty Git commit or ref")
    return (
        _git(repo, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")
        .decode()
        .strip()
    )


def snapshot_files(root: Path) -> dict:
    """Record content, file/directory modes, and internal symlinks, including root."""
    root = root.resolve()
    files = {".": {"kind": "directory", "mode": stat.S_IMODE(root.lstat().st_mode)}}
    for parent, directories, names in os.walk(root, followlinks=False):
        for name in sorted(directories + names):
            path = Path(parent) / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                try:
                    target = path.resolve(strict=True)
                except (OSError, RuntimeError) as exc:
                    raise ValueError(f"invalid installed symlink: {relative}") from exc
                if (
                    not target.is_relative_to(root)
                    or Path(os.readlink(path)).is_absolute()
                ):
                    raise ValueError(f"installed symlink escapes consumer: {relative}")
                files[relative] = {"kind": "symlink", "target": os.readlink(path)}
            elif path.is_file():
                files[relative] = {
                    "kind": "file",
                    "mode": stat.S_IMODE(path.lstat().st_mode),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            elif path.is_dir():
                files[relative] = {
                    "kind": "directory",
                    "mode": stat.S_IMODE(path.lstat().st_mode),
                }
            else:
                raise ValueError(f"unsupported installed file type: {relative}")
    return dict(sorted(files.items()))


def verify_files(root: Path, expected: dict) -> None:
    actual = snapshot_files(root)
    changed = sorted(
        name
        for name in actual.keys() | expected.keys()
        if actual.get(name) != expected.get(name)
    )
    if changed:
        raise ValueError("installed payload drift: " + ", ".join(changed[:20]))


def _fingerprint(files: dict) -> str:
    return hashlib.sha256(
        json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _export(repo: Path, commit: str, source: Path) -> tuple[str, Path, Path]:
    names = set(
        _git(repo, "ls-tree", "-r", "--name-only", commit).decode().splitlines()
    )
    modern = "agent_workflow/lifecycle.py"
    legacy = "skills/agent-workflow/scripts/lifecycle.py"
    if modern in names:
        layout, script = "canonical-source", modern
        selections = ["agent_workflow", ".agent-workflow", ".agents/skills"]
        if "VERSION" in names:
            selections.append("VERSION")
        manifest = "agent_workflow/install/manifest.json"
    elif legacy in names:
        layout, script = "legacy-payload", legacy
        selections = ["skills/agent-workflow"]
        manifest = "skills/agent-workflow/payload/distribution/manifest.json"
    else:
        raise ValueError(f"unsupported historical installer layout at {commit}")
    archive = _git(repo, "archive", "--format=tar", commit, *selections)
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for entry in bundle:
            relative = PurePosixPath(entry.name)
            if relative.is_absolute() or ".." in relative.parts or not relative.parts:
                raise ValueError(f"unsafe Git archive path: {entry.name}")
            target = source.joinpath(*relative.parts)
            if entry.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif entry.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.extractfile(entry) as stream:
                    target.write_bytes(stream.read())
                target.chmod(entry.mode & 0o777)
            else:
                raise ValueError(f"unsupported Git archive entry: {entry.name}")
    return layout, source / script, source / manifest


def _run_installer(command: list[str], source: Path) -> dict:
    try:
        result = subprocess.run(
            command,
            cwd=source,
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"historical installer could not run: {exc}") from exc
    log = {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if result.returncode:
        raise RuntimeError("historical installer failed: " + json.dumps(log))
    return log


def _install(repo: Path, ref: str, commit: str, consumer: Path, source: Path) -> dict:
    layout, script, manifest_path = _export(repo, commit, source)
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError) as exc:
        raise ValueError(
            f"historical distribution manifest unavailable at {commit}"
        ) from exc
    if not isinstance(manifest, dict):
        raise ValueError(
            f"historical distribution manifest is not an object at {commit}"
        )
    consumer.mkdir()
    provider = script.with_name("providers.py")
    source_argument = ["--source-revision", commit] if provider.is_file() else []
    logs = [
        _run_installer(
            [sys.executable, str(script), "install", str(consumer), *source_argument],
            source,
        )
    ]
    if layout == "legacy-payload" and provider.is_file():
        # Legacy lifecycle success only guarantees core, not optional projections.
        logs.append(
            _run_installer(
                [sys.executable, str(provider), "status", str(consumer)], source
            )
        )
    logs.append(
        _run_installer(
            [sys.executable, str(script), "status", str(consumer), *source_argument],
            source,
        )
    )
    version_paths = (
        source / "VERSION",
        source / "agent_workflow/VERSION",
        source / "skills/agent-workflow/VERSION",
    )
    version = next(
        (path.read_text().strip() for path in version_paths if path.is_file()), None
    )
    warnings = []
    declared = manifest.get("framework_version")
    if declared is not None and declared != version:
        warnings.append(
            f"Package VERSION {version!r} differs from distribution framework_version {declared!r}; commit SHA defines this treatment."
        )
    files = snapshot_files(consumer)
    if "AGENTS.md" not in files or not any(
        name.endswith("/SKILL.md") for name in files
    ):
        raise RuntimeError(
            f"historical installation omitted policy or skills at {commit}"
        )
    return {
        "ref": ref,
        "commit": commit,
        "version": version,
        "distribution_version": declared,
        "layout": layout,
        "files": files,
        "payload_sha256": _fingerprint(files),
        "warnings": warnings,
        "overlays": [],
        "installer": logs,
    }


def _missing_dependencies(consumer: Path, donor: Path, skill: str) -> list[str]:
    """Check literal framework references and resolvable Markdown links only."""
    missing = set()
    directory = consumer / ".agents/skills" / skill
    for file in directory.rglob("*.md"):
        text = file.read_text()
        references = set(
            re.findall(
                r"(?:\.agent-workflow|\.agents/skills)/[\w./-]+\.(?:md|json|ya?ml)\b",
                text,
            )
        )
        donor_file = donor / file.relative_to(consumer)
        for link in re.findall(r"\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", text):
            link = link.split("#", 1)[0].strip("<>")
            if (
                not link
                or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", link)
                or link.startswith("/")
            ):
                continue
            target = (donor_file.parent / link).resolve()
            sibling = len(PurePosixPath(link).parts) == 1 and target.suffix == ".md"
            if target.is_relative_to(donor) and (target.exists() or sibling):
                references.add(target.relative_to(donor).as_posix())
        for reference in references:
            target = (consumer / reference).resolve()
            if not target.is_relative_to(consumer) or not target.exists():
                missing.add(reference)
    return sorted(missing)


def prepare_revision(
    repo: Path, ref: str, destination: Path, *, overlays: list[dict] | None = None
) -> dict:
    """Install a revision and explicit whole-skill replacements into a new directory.

    Source and donor revisions are immutable Git commits. Overlay validation catches
    missing literal local dependencies, not semantic compatibility between policies.
    """
    repo = repo.resolve()
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError("destination must not exist")
    if not destination.parent.is_dir():
        raise ValueError("destination parent must be an existing directory")
    destination = destination.parent.resolve() / destination.name
    if repo.is_relative_to(destination) or (
        destination.is_relative_to(repo)
        and not destination.is_relative_to(repo / "evals/artifacts")
    ):
        raise ValueError(
            "destination overlaps source; use evals/artifacts or an external disposable directory"
        )
    overlays = [] if overlays is None else overlays
    if not isinstance(overlays, list):
        raise ValueError("overlays must be a list")
    prepared = []
    seen = set()
    commit = resolve_revision(repo, ref)
    for item in overlays:
        if not isinstance(item, dict) or set(item) != {"skill", "ref"}:
            raise ValueError("overlay requires only skill and ref")
        skill = item["skill"]
        if (
            not isinstance(skill, str)
            or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill) is None
            or skill in seen
        ):
            raise ValueError("overlay skill must be a unique simple skill name")
        seen.add(skill)
        prepared.append((skill, item["ref"], resolve_revision(repo, item["ref"])))
    with tempfile.TemporaryDirectory(
        prefix="campaign-revision-", dir=destination.parent
    ) as temporary:
        work = Path(temporary)
        consumer = work / "consumer"
        metadata = _install(repo, ref, commit, consumer, work / "source")
        for index, (skill, donor_ref, donor_commit) in enumerate(prepared):
            donor = work / f"donor-{index}"
            donor_meta = _install(
                repo, donor_ref, donor_commit, donor, work / f"donor-source-{index}"
            )
            target, origin = (
                consumer / ".agents/skills" / skill,
                donor / ".agents/skills" / skill,
            )
            if any(
                path.is_symlink() or not (path / "SKILL.md").is_file()
                for path in (target, origin)
            ):
                raise ValueError(
                    f"overlay requires an existing installed skill in base and donor: {skill}"
                )
            before = snapshot_files(target)
            shutil.rmtree(target)
            shutil.copytree(origin, target, symlinks=True)
            metadata["overlays"].append(
                {
                    "skill": skill,
                    "ref": donor_ref,
                    "base_commit": commit,
                    "donor_commit": donor_commit,
                    "donor_version": donor_meta["version"],
                    "donor_payload_sha256": donor_meta["payload_sha256"],
                    "before_files": before,
                    "files": snapshot_files(target),
                    "compatibility": "literal-local-dependencies-only",
                    "warnings": donor_meta["warnings"],
                }
            )
        for index, (skill, _, _) in enumerate(prepared):
            missing = _missing_dependencies(consumer, work / f"donor-{index}", skill)
            if missing:
                raise ValueError(
                    f"incompatible skill overlay {skill}; missing local dependencies: {', '.join(missing)}"
                )
        if prepared:
            metadata["warnings"].append(
                "Skill overlays are experimental; local reference checks do not establish semantic compatibility."
            )
        metadata["files"] = snapshot_files(consumer)
        metadata["payload_sha256"] = _fingerprint(metadata["files"])
        if destination.exists() or destination.is_symlink():
            raise ValueError("destination appeared during preparation")
        consumer.rename(destination)
    return metadata
