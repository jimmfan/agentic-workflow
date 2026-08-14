#!/usr/bin/env python3
"""Coordinate framework payload and curated upstream provider lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Iterable, Mapping, Optional, Sequence


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
ADOPTER = PACKAGE_ROOT / "scripts" / "adopt.py"
PROVIDERS = PACKAGE_ROOT / "scripts" / "providers.py"
INSTALL_MANIFEST = Path("ai-workflow/install-manifest.json")
PROVIDER_DECLARATION = PACKAGE_ROOT / "payload" / "ai-workflow" / "providers.json"
DISTRIBUTION_MANIFEST = PACKAGE_ROOT / "payload" / "distribution" / "manifest.json"
PROJECT_PROFILE = Path("ai-workflow/project-profile.md")
CONFIGURATION_LABELS = {
    "issue-tracker": "issue tracker config",
    "domain": "domain config",
    "triage-labels": "triage config",
}
PROFILE_HEADINGS = (
    "Purpose and success",
    "Technology and architecture",
    "Important paths",
    "Terminology",
    "Constraints and policy",
    "Delivery workflow",
    "Commands",
    "Debugging model",
    "Decision considerations",
    "Profile maintenance",
)
PROFILE_INITIALIZATION = {
    "Initialization: uninitialized": "uninitialized",
    "Initialization: initialized": "initialized",
}
LEGACY_UNINITIALIZED_PROFILE_SHA256 = (
    "a1ab827e351693fb700120877d2df4548cfa56d9662906cff8e85e85e17ff22a"
)
SETUP_SKILL = "setup-matt-pocock-skills"
HOST_FIELDS = {"availability", "discovery", "explicit_prefix", "invocation_source"}
INVOCATION_VALUES = {"implicit", "user-only", "unavailable"}
HOST_LABELS = {
    "codex": "Codex",
    "github-copilot": "GitHub Copilot",
    "claude-code": "Claude Code",
}
MINIMUM_PYTHON = (3, 11)


class LifecycleError(RuntimeError):
    """A coordinated lifecycle operation failed."""


def require_supported_python() -> None:
    if sys.version_info < MINIMUM_PYTHON:
        found = ".".join(str(part) for part in sys.version_info[:3])
        raise LifecycleError(f"Python 3.11 or newer is required; found Python {found}")


def command(script: Path, action: str, root: Path, dry_run: bool, revision: str) -> list[str]:
    value = [sys.executable, str(script), action, str(root)]
    if script == ADOPTER:
        value.extend(("--source-revision", revision))
    if dry_run:
        value.append("--dry-run")
    return value


def run_checked(
    script: Path,
    action: str,
    root: Path,
    dry_run: bool,
    revision: str,
    *,
    quiet: bool = False,
) -> None:
    result = subprocess.run(
        command(script, action, root, dry_run, revision),
        capture_output=quiet,
        text=True,
    )
    if result.returncode != 0:
        detail = ""
        if quiet:
            detail = "\n".join(
                part.strip() for part in (result.stdout, result.stderr) if part and part.strip()
            )
        raise LifecycleError(
            f"{script.name} {action} failed with exit code {result.returncode}"
            + (f": {detail}" if detail else "")
        )


def load_provider_manager() -> object:
    """Load the provider manager so its rollback window can include payload commit."""
    spec = importlib.util.spec_from_file_location("agentic_workflow_provider_transaction", PROVIDERS)
    if spec is None or spec.loader is None:
        raise LifecycleError(f"cannot load provider transaction manager: {PROVIDERS}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError) as error:
        raise LifecycleError(f"cannot load provider transaction manager: {error}") from error
    return module


def readiness_path(root: Path, relative: Path) -> Optional[Path]:
    current = root
    for index, part in enumerate(relative.parts):
        current = current / part
        try:
            if current.is_symlink():
                return None
            if index < len(relative.parts) - 1 and current.exists() and not current.is_dir():
                return None
        except OSError:
            return None
    return current


def profile_state(root: Path) -> str:
    path = readiness_path(root, PROJECT_PROFILE)
    if path is None:
        return "invalid"
    if not path.exists() and not path.is_symlink():
        return "missing"
    if path.is_symlink() or not path.is_file():
        return "invalid"
    try:
        data = path.read_bytes()
    except OSError:
        return "unreadable"
    if hashlib.sha256(data).hexdigest() == LEGACY_UNINITIALIZED_PROFILE_SHA256:
        return "legacy-uninitialized"
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return "invalid"
    lines = text.splitlines()
    nonblank = [index for index, line in enumerate(lines) if line.strip()]
    if (
        len(nonblank) < 2
        or lines[nonblank[0]].strip() != "# Project profile"
        or lines[nonblank[1]].strip() not in PROFILE_INITIALIZATION
    ):
        return "invalid"
    headings = [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]
    positions = []
    for heading in PROFILE_HEADINGS:
        if headings.count(heading) != 1:
            return "invalid"
        positions.append(headings.index(heading))
    if positions != sorted(positions):
        return "invalid"
    markers = [PROFILE_INITIALIZATION[line.strip()] for line in lines if line.strip() in PROFILE_INITIALIZATION]
    return markers[0] if len(markers) == 1 else "invalid"


def configuration_state(root: Path, relative: Path) -> str:
    path = readiness_path(root, relative)
    if path is None:
        return "invalid"
    if not path.exists() and not path.is_symlink():
        return "missing"
    if path.is_symlink() or not path.is_file():
        return "invalid"
    try:
        return "configured" if path.read_bytes().strip() else "empty"
    except OSError:
        return "unreadable"


def project_readiness(
    root: Path, configuration: Optional[Sequence[tuple[str, Path]]] = None
) -> Mapping[str, str]:
    if configuration is None:
        configuration, _capability = load_provider_status_contract()
    states = {"project profile": profile_state(root)}
    states.update(
        (label, configuration_state(root, relative))
        for label, relative in configuration
    )
    return states


def safe_configuration_path(raw: object, label: str) -> Path:
    if not isinstance(raw, str):
        raise LifecycleError(f"{label} must be a string")
    relative = PurePosixPath(raw)
    if not raw or relative.is_absolute() or ".." in relative.parts or "." in relative.parts or "\\" in raw:
        raise LifecycleError(f"unsafe {label}: {raw!r}")
    return Path(*relative.parts)


def load_provider_status_contract() -> tuple[
    list[tuple[str, Path]], list[tuple[str, Mapping[str, object], str]]
]:
    try:
        declaration = json.loads(PROVIDER_DECLARATION.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LifecycleError(f"cannot read provider host declaration: {error}") from error
    if (
        not isinstance(declaration, dict)
        or set(declaration) != {"schema_version", "capabilities", "configuration", "hosts", "provider"}
        or declaration.get("schema_version") != 3
    ):
        raise LifecycleError("provider host declaration must use schema version 3")
    hosts = declaration.get("hosts")
    configuration = declaration.get("configuration")
    provider = declaration.get("provider")
    if not isinstance(hosts, dict) or set(hosts) != set(HOST_LABELS):
        raise LifecycleError("provider host declaration must cover the supported host set")
    if not isinstance(configuration, dict) or set(configuration) != set(CONFIGURATION_LABELS):
        raise LifecycleError("provider declaration has invalid project configuration entries")
    if not isinstance(provider, dict) or not isinstance(provider.get("skills"), list):
        raise LifecycleError("provider host declaration needs a provider skills array")

    checked_configuration = []
    for config_id, label in CONFIGURATION_LABELS.items():
        record = configuration[config_id]
        required_fields = {"path", "provisioned_by"}
        if config_id == "triage-labels":
            required_fields.add("enabled_by")
        if not isinstance(record, dict) or set(record) != required_fields:
            raise LifecycleError(f"provider configuration {config_id!r} has invalid fields")
        if not isinstance(record.get("provisioned_by"), str) or not record["provisioned_by"]:
            raise LifecycleError(f"provider configuration {config_id!r} needs a provisioner")
        if config_id == "triage-labels" and (
            not isinstance(record.get("enabled_by"), str) or not record["enabled_by"]
        ):
            raise LifecycleError("triage-label configuration needs an enabling provider skill")
        checked_configuration.append(
            (label, safe_configuration_path(record.get("path"), f"path for {config_id}"))
        )

    checked_hosts: dict[str, Mapping[str, object]] = {}
    for host_id, record in hosts.items():
        if not isinstance(host_id, str) or not host_id:
            raise LifecycleError("provider host identifiers must be non-empty strings")
        if not isinstance(record, dict) or set(record) != HOST_FIELDS:
            raise LifecycleError(f"provider host {host_id!r} has invalid fields")
        if record.get("availability") not in {"available", "unavailable"}:
            raise LifecycleError(f"provider host {host_id!r} has invalid availability")
        for field in ("discovery", "explicit_prefix", "invocation_source"):
            value = record.get(field)
            if not isinstance(value, str) or not value:
                raise LifecycleError(f"provider host {host_id!r} {field} must be a non-empty string")
        checked_hosts[host_id] = record

    setup_matches = [
        skill
        for skill in provider["skills"]
        if isinstance(skill, dict) and skill.get("name") == SETUP_SKILL
    ]
    if len(setup_matches) != 1:
        raise LifecycleError(f"provider declaration must contain exactly one {SETUP_SKILL} skill")
    setup = setup_matches[0]
    invocation = setup.get("invocation")
    required_configuration = setup.get("requires_configuration")
    if not isinstance(invocation, dict) or set(invocation) != set(checked_hosts):
        raise LifecycleError(f"{SETUP_SKILL} invocation must cover every declared host")
    if not all(value in INVOCATION_VALUES for value in invocation.values()):
        raise LifecycleError(f"{SETUP_SKILL} invocation contains an unsupported policy")
    if not isinstance(required_configuration, list) or not all(
        isinstance(item, str) and item for item in required_configuration
    ):
        raise LifecycleError(f"{SETUP_SKILL} requires_configuration must be a string array")

    result = []
    for host_id, record in checked_hosts.items():
        policy = invocation[host_id]
        if record["availability"] == "unavailable" and policy != "unavailable":
            raise LifecycleError(f"unavailable host {host_id!r} cannot invoke {SETUP_SKILL}")
        if policy == "user-only" and not record.get("explicit_prefix"):
            raise LifecycleError(f"user-only host {host_id!r} needs an explicit invocation prefix")
        result.append((host_id, record, policy))
    return checked_configuration, result


def setup_capability(
    host_invocation: Optional[Sequence[tuple[str, Mapping[str, object], str]]] = None,
) -> Mapping[str, str]:
    if host_invocation is None:
        _configuration, host_invocation = load_provider_status_contract()
    capabilities = {}
    for host_id, record, policy in host_invocation:
        label = HOST_LABELS.get(host_id, host_id)
        if policy == "user-only":
            invocation = f"{record['explicit_prefix']}{SETUP_SKILL}"
            capabilities[label] = f"user invocation required (`{invocation}`)"
        elif policy == "implicit":
            capabilities[label] = "implicit invocation available"
        else:
            capabilities[label] = "unavailable"
    return capabilities


def print_readiness(root: Path, *, detailed: bool) -> None:
    configuration, host_invocation = load_provider_status_contract()
    readiness = project_readiness(root, configuration)
    capability = setup_capability(host_invocation)
    if detailed:
        print("Project readiness (warnings do not affect integrity status):")
        for label, state in readiness.items():
            print(f"  {label}: {state}")
        print("Host capability (setup workflow):")
        for host, state in capability.items():
            print(f"  {host} setup workflow: {state}")
        if readiness["project profile"] in {"uninitialized", "legacy-uninitialized"}:
            print(
                "Readiness guidance: initialize the profile once from verified repository evidence "
                "when writes are authorized; unrelated direct work remains available."
            )
        return
    print(
        "Project readiness (optional; does not affect installation integrity): "
        + "; ".join(f"{label}={state}" for label, state in readiness.items())
    )
    print("Host/setup capability: " + "; ".join(f"{host}={state}" for host, state in capability.items()))
    if readiness["project profile"] in {"uninitialized", "legacy-uninitialized"}:
        print(
            "Project initialization remains: initialize the profile once from verified repository "
            "evidence when writes are authorized; unrelated direct work is ready."
        )


def integrity_state(returncode: int) -> str:
    if returncode == 0:
        return "healthy"
    if returncode == 1:
        return "unhealthy"
    return "error"


def status(root: Path, revision: str) -> int:
    payload = subprocess.run(command(ADOPTER, "status", root, False, revision)).returncode
    providers = subprocess.run(command(PROVIDERS, "status", root, False, revision)).returncode
    print(f"Framework integrity: {integrity_state(payload)}")
    print(f"Provider integrity: {integrity_state(providers)}")
    print_readiness(root, detailed=True)
    if payload == 2 or providers == 2:
        return 2
    return 0 if payload == 0 and providers == 0 else 1


def payload_targets() -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    try:
        manifest = json.loads(DISTRIBUTION_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LifecycleError(f"cannot read payload distribution manifest: {error}") from error
    if not isinstance(manifest, dict):
        raise LifecycleError("payload distribution manifest must be an object")

    groups: list[tuple[Path, ...]] = []
    for field in ("framework_owned", "project_seeds"):
        mappings = manifest.get(field)
        if not isinstance(mappings, list):
            raise LifecycleError(f"payload distribution manifest needs {field} mappings")
        targets = []
        for item in mappings:
            if not isinstance(item, dict) or set(item) != {"source", "target"}:
                raise LifecycleError(
                    f"payload distribution manifest has malformed {field} mapping"
                )
            targets.append(safe_configuration_path(item["target"], f"{field} target"))
        groups.append(tuple(targets))
    framework_targets, seed_targets = groups
    return framework_targets + seed_targets, seed_targets


def existing_parent_directories(root: Path, targets: Iterable[Path]) -> set[Path]:
    existing = {root}
    for relative in targets:
        current = (root / relative).parent
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
            break
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def rollback_new_seeds(
    root: Path,
    created: Mapping[Path, bytes],
    cleanup_targets: Sequence[Path],
    preexisting_directories: set[Path],
) -> None:
    for relative, expected in created.items():
        destination = root / relative
        if (
            destination.is_file()
            and not destination.is_symlink()
            and destination.read_bytes() == expected
        ):
            destination.unlink()
    for relative in sorted(cleanup_targets, key=lambda item: len(item.parts), reverse=True):
        remove_created_empty_parents(
            root / relative,
            root,
            preexisting_directories,
        )


def install(root: Path, dry_run: bool, revision: str) -> None:
    if dry_run:
        run_checked(ADOPTER, "install", root, True, revision)
        run_checked(PROVIDERS, "install", root, True, revision)
        return
    existed = (root / INSTALL_MANIFEST).exists()
    cleanup_targets, seed_targets = payload_targets()
    preexisting_directories = existing_parent_directories(root, cleanup_targets)
    originally_absent = {
        target for target in seed_targets if not (root / target).exists()
    }
    run_checked(ADOPTER, "install", root, True, revision, quiet=True)
    run_checked(PROVIDERS, "install", root, True, revision, quiet=True)
    run_checked(ADOPTER, "install", root, False, revision)
    created_seed_snapshots = {
        relative: (root / relative).read_bytes()
        for relative in originally_absent
        if (root / relative).is_file() and not (root / relative).is_symlink()
    }
    try:
        run_checked(PROVIDERS, "install", root, False, revision)
    except LifecycleError as error:
        if not existed:
            rollback = subprocess.run(
                command(ADOPTER, "remove", root, False, revision),
                capture_output=True,
                text=True,
            )
            if rollback.returncode != 0:
                detail = "\n".join(
                    part.strip() for part in (rollback.stdout, rollback.stderr) if part and part.strip()
                )
                raise LifecycleError(
                    f"provider installation failed and payload rollback also failed: {error}; {detail}"
                ) from error
            rollback_new_seeds(
                root,
                created_seed_snapshots,
                cleanup_targets,
                preexisting_directories,
            )
        raise
    print("✓ Agentic Workflow framework is installed; payload and curated upstream providers are verified.")
    print_readiness(root, detailed=False)


def update(root: Path, dry_run: bool, revision: str) -> None:
    run_checked(ADOPTER, "update", root, True, revision, quiet=not dry_run)
    if dry_run:
        run_checked(PROVIDERS, "update", root, True, revision)
        return
    manager = load_provider_manager()
    try:
        manager.command_update(  # type: ignore[attr-defined]
            root,
            False,
            commit_callback=lambda: run_checked(ADOPTER, "update", root, False, revision),
        )
    except manager.ProviderError as error:  # type: ignore[attr-defined]
        raise LifecycleError(f"providers.py update failed: {error}") from error
    except OSError as error:
        raise LifecycleError(f"providers.py update failed: filesystem operation failed: {error}") from error
    print("✓ Agentic Workflow payload and curated upstream providers are updated and verified.")
    print_readiness(root, detailed=False)


def remove(root: Path, dry_run: bool, revision: str) -> None:
    run_checked(ADOPTER, "remove", root, True, revision, quiet=not dry_run)
    run_checked(PROVIDERS, "remove", root, dry_run, revision)
    if dry_run:
        return
    run_checked(ADOPTER, "remove", root, False, revision)
    print("✓ Agentic Workflow and its unchanged framework-installed providers were removed.")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "update", "status", "remove"))
    parser.add_argument("target", nargs="?", default=Path.cwd(), type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source-revision", default="unreleased-local-package", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    require_supported_python()
    args = parse_args(argv or sys.argv[1:])
    if args.action == "status" and args.dry_run:
        raise LifecycleError("--dry-run is not valid for status")
    root = args.target.expanduser().resolve()
    if not root.is_dir():
        raise LifecycleError(f"target project directory does not exist: {root}")
    if root == Path(root.anchor):
        raise LifecycleError("refusing to operate on a filesystem root")
    if args.action == "install":
        install(root, args.dry_run, args.source_revision)
    elif args.action == "update":
        update(root, args.dry_run, args.source_revision)
    elif args.action == "status":
        return status(root, args.source_revision)
    else:
        remove(root, args.dry_run, args.source_revision)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LifecycleError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
