#!/usr/bin/env python3
"""Coordinate framework payload and curated upstream provider lifecycle."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Mapping, Optional, Sequence


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
ADOPTER = PACKAGE_ROOT / "scripts" / "adopt.py"
PROVIDERS = PACKAGE_ROOT / "scripts" / "providers.py"
STATE_DIRECTORY = Path(".ai-workflow")
DURABLE_STATE_DIRECTORY = Path(".ai-workflow-state")
LEGACY_STATE_DIRECTORY = Path("ai-workflow")
INSTALL_MANIFEST = STATE_DIRECTORY / "install-manifest.json"
PROVIDER_DECLARATION = PACKAGE_ROOT / "payload" / "ai-workflow" / "providers.json"
PROJECT_PROFILE = DURABLE_STATE_DIRECTORY / "project-profile.md"
ACTIVE_STATE = DURABLE_STATE_DIRECTORY / "active.md"
ENFORCEMENT_CAPABILITIES = STATE_DIRECTORY / "runtime" / "capabilities.json"
VSCODE_HOOK = Path(".github/hooks/agentic-workflow.json")
CONFIGURATION_LABELS = {
    "issue-tracker": "issue tracker config",
    "domain": "domain config",
    "triage-labels": "triage config",
}
ACTIVE_WORKFLOWS = {
    "debugging",
    "discovery",
    "implementation",
    "none",
    "provider",
    "verification",
}
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


def command(
    script: Path,
    action: str,
    root: Path,
    dry_run: bool,
    revision: str,
    extra: Sequence[str] = (),
) -> list[str]:
    value = [sys.executable, str(script), action, str(root)]
    if script == ADOPTER:
        value.extend(("--source-revision", revision))
    if dry_run:
        value.append("--dry-run")
    value.extend(extra)
    return value


def run_checked(
    script: Path,
    action: str,
    root: Path,
    dry_run: bool,
    revision: str,
    *,
    quiet: bool = False,
    extra: Sequence[str] = (),
) -> None:
    result = subprocess.run(
        command(script, action, root, dry_run, revision, extra),
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


def load_adopter_manager() -> object:
    """Load the adopter to reuse its managed-install validation boundary."""
    spec = importlib.util.spec_from_file_location("agentic_workflow_legacy_validator", ADOPTER)
    if spec is None or spec.loader is None:
        raise LifecycleError(f"cannot load legacy installation validator: {ADOPTER}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError) as error:
        raise LifecycleError(f"cannot load legacy installation validator: {error}") from error
    return module


def state_layout(root: Path) -> str:
    canonical = root / STATE_DIRECTORY
    legacy = root / LEGACY_STATE_DIRECTORY
    canonical_exists = canonical.exists() or canonical.is_symlink()
    legacy_exists = legacy.exists() or legacy.is_symlink()
    if canonical_exists and legacy_exists:
        raise LifecycleError(
            "conflicting Agentic Workflow state directories exist: "
            "ai-workflow/ and .ai-workflow/; refusing to merge or overwrite either directory"
        )
    if canonical_exists:
        if canonical.is_symlink() or not canonical.is_dir():
            raise LifecycleError(f"canonical state path must be a regular directory: {canonical}")
        return "canonical"
    if legacy_exists:
        if legacy.is_symlink() or not legacy.is_dir():
            raise LifecycleError(f"legacy state path must be a regular directory: {legacy}")
        return "legacy"
    return "absent"


def validate_legacy_update(root: Path) -> str:
    adopter = load_adopter_manager()
    try:
        return adopter.validate_legacy_installation(root)  # type: ignore[attr-defined,no-any-return]
    except adopter.AdoptionError as error:  # type: ignore[attr-defined]
        raise LifecycleError(
            "ai-workflow/ is not a recognizable managed legacy installation; "
            f"refusing to rename it: {error}"
        ) from error


def relocate_legacy_state(root: Path) -> None:
    legacy = root / LEGACY_STATE_DIRECTORY
    canonical = root / STATE_DIRECTORY
    print("Migrating Agentic Workflow state:")
    print("  ai-workflow/ -> .ai-workflow/")
    try:
        os.replace(legacy, canonical)
    except OSError as error:
        raise LifecycleError(f"could not migrate legacy project state: {error}") from error
    print("OK: migrated legacy project state")


def restore_legacy_state_name(root: Path) -> None:
    canonical = root / STATE_DIRECTORY
    legacy = root / LEGACY_STATE_DIRECTORY
    if legacy.exists() or legacy.is_symlink():
        raise LifecycleError(
            "update failed after migration and the legacy state path reappeared; "
            "cannot restore the original directory name safely"
        )
    try:
        os.replace(canonical, legacy)
    except OSError as error:
        raise LifecycleError(
            f"update failed after migration and the legacy directory name could not be restored: {error}"
        ) from error


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
        return "unsafe"
    if not path.exists() and not path.is_symlink():
        return "missing"
    if path.is_symlink() or not path.is_file():
        return "unsafe"
    try:
        data = path.read_bytes()
    except OSError:
        return "unreadable"
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return "unreadable"
    if not text.strip():
        return "empty"
    return "present"


def active_state(root: Path) -> str:
    path = readiness_path(root, ACTIVE_STATE)
    if path is None:
        return "unsafe"
    if not path.exists() and not path.is_symlink():
        return "none"
    if path.is_symlink() or not path.is_file():
        return "unsafe"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "unreadable"
    matches = re.findall(r"^- Active workflow: ([a-z-]+)$", text, flags=re.MULTILINE)
    if len(matches) != 1 or matches[0] not in ACTIVE_WORKFLOWS:
        return "invalid"
    return matches[0]


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
    states = {
        "project profile": profile_state(root),
        "active workflow": active_state(root),
    }
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
        or declaration.get("schema_version") != 4
    ):
        raise LifecycleError("provider host declaration must use schema version 4")
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
    try:
        configuration, host_invocation = load_provider_status_contract()
    except LifecycleError as error:
        configuration = []
        host_invocation = []
        print(
            "Optional provider readiness metadata is unavailable; "
            f"host-native fallback remains available: {error}"
        )
    readiness = project_readiness(root, configuration)
    capability = setup_capability(host_invocation)
    if detailed:
        print(
            "Project readiness (optional durable state; missing profile and active state are normal):"
        )
        for label, state in readiness.items():
            print(f"  {label}: {state}")
        print("Host capability (setup workflow):")
        for host, state in capability.items():
            print(f"  {host} setup workflow: {state}")
        return
    print(
        "Project readiness (optional durable state; absence is normal and does not affect integrity): "
        + "; ".join(f"{label}={state}" for label, state in readiness.items())
    )
    print("Host/setup capability: " + "; ".join(f"{host}={state}" for host, state in capability.items()))


def enforcement_status(root: Path) -> Mapping[str, str]:
    capabilities_path = readiness_path(root, ENFORCEMENT_CAPABILITIES)
    hook_path = readiness_path(root, VSCODE_HOOK)
    if capabilities_path is None or not capabilities_path.is_file() or capabilities_path.is_symlink():
        return {
            "GitHub Copilot in VS Code": "unavailable (capability metadata missing or invalid)",
            "Codex": "instruction-only",
            "Claude Code": "instruction-only",
            "GitHub Copilot CLI/cloud": "instruction-only",
        }
    try:
        value = json.loads(capabilities_path.read_text(encoding="utf-8"))
        hosts = value["hosts"]
        if value.get("schema_version") != 1 or not isinstance(hosts, dict):
            raise ValueError("unsupported capability schema")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return {
            "GitHub Copilot in VS Code": "unavailable (capability metadata unreadable)",
            "Codex": "instruction-only",
            "Claude Code": "instruction-only",
            "GitHub Copilot CLI/cloud": "instruction-only",
        }
    vscode = "partial/Preview"
    if hook_path is None or not hook_path.is_file() or hook_path.is_symlink():
        vscode += " (active hook missing; instruction fallback)"
    else:
        vscode += " (active adapter installed)"
    return {
        "GitHub Copilot in VS Code": vscode,
        "Codex": "partial optional adapter; instruction fallback by default",
        "Claude Code": "partial optional adapter; provider skills unavailable",
        "GitHub Copilot CLI/cloud": "shared file unvalidated; instruction fallback",
    }


def print_enforcement_status(root: Path) -> None:
    print("Host enforcement (capability, not installation integrity):")
    for host, state in enforcement_status(root).items():
        print(f"  {host}: {state}")


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
    print(f"Optional provider capability: {integrity_state(providers)}")
    print_enforcement_status(root)
    print_readiness(root, detailed=True)
    return 0 if payload == 0 else 1


def install(root: Path, dry_run: bool, revision: str) -> None:
    root = root.resolve()
    adopter = load_adopter_manager()
    reinstall = adopter.is_reinstall(root)  # type: ignore[attr-defined]
    provider_extra = ("--reinstall",) if reinstall else ()
    if dry_run:
        run_checked(ADOPTER, "install", root, True, revision)
        try:
            run_checked(
                PROVIDERS,
                "install",
                root,
                True,
                revision,
                extra=provider_extra,
            )
        except LifecycleError as error:
            print(f"Optional provider preflight unavailable: {error}")
        return
    run_checked(ADOPTER, "install", root, True, revision, quiet=True)
    run_checked(ADOPTER, "install", root, False, revision)
    try:
        run_checked(
            PROVIDERS,
            "install",
            root,
            False,
            revision,
            extra=provider_extra,
        )
    except LifecycleError as error:
        print(
            "WARNING: Agentic Workflow was installed, but optional providers were not installed: "
            f"{error}. Host-native workflows remain available.",
            file=sys.stderr,
        )
    print("✓ Agentic Workflow framework is installed.")
    print_enforcement_status(root)
    print_readiness(root, detailed=False)


def update(root: Path, dry_run: bool, revision: str) -> None:
    layout = state_layout(root)
    migrated = False
    if layout == "legacy":
        version = validate_legacy_update(root)
        if dry_run:
            print(f"UPDATE DRY RUN for {root}")
            print("  - migrate recognized managed Agentic Workflow state ai-workflow/ -> .ai-workflow/")
            print(f"  - continue the normal update from recognized legacy version {version}")
            print("No files changed. Re-run without --dry-run to apply this operation.")
            return
        relocate_legacy_state(root)
        migrated = True
    elif layout == "absent":
        raise LifecycleError(
            "no Agentic Workflow installation exists at .ai-workflow/install-manifest.json"
        )
    try:
        run_checked(ADOPTER, "update", root, True, revision, quiet=True)
        if dry_run:
            run_checked(ADOPTER, "update", root, True, revision)
        else:
            run_checked(ADOPTER, "update", root, False, revision)
    except BaseException as error:
        if migrated:
            restore_legacy_state_name(root)
        raise
    provider_state = root / STATE_DIRECTORY / "provider-state.json"
    if provider_state.exists() or provider_state.is_symlink():
        try:
            run_checked(PROVIDERS, "update", root, dry_run, revision)
        except LifecycleError as error:
            print(
                "WARNING: framework update succeeded, but the optional provider update did not: "
                f"{error}. Existing provider files were preserved; host-native fallback remains available.",
                file=sys.stderr,
            )
    elif dry_run:
        print("Optional providers are not installed; update will not create provider state.")
    if dry_run:
        return
    print("✓ Agentic Workflow framework is updated and verified.")
    print_enforcement_status(root)
    print_readiness(root, detailed=False)


def remove(root: Path, dry_run: bool, revision: str) -> None:
    run_checked(ADOPTER, "remove", root, True, revision, quiet=not dry_run)
    try:
        run_checked(PROVIDERS, "remove", root, dry_run, revision)
    except LifecycleError as error:
        print(
            "WARNING: optional provider cleanup was skipped: "
            f"{error}. Provider files and ownership state were preserved.",
            file=sys.stderr,
        )
    if dry_run:
        return
    run_checked(ADOPTER, "remove", root, False, revision)
    print("✓ Agentic Workflow framework was removed; unchanged managed providers were removed when safe.")


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
    layout = state_layout(root)
    if layout == "legacy" and args.action != "update":
        raise LifecycleError(
            "legacy Agentic Workflow state exists at ai-workflow/; run update to validate and "
            "migrate it to .ai-workflow/ before using this lifecycle operation"
        )
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
