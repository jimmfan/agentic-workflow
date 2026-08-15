#!/usr/bin/env python3
"""Strict development, CI, and release verification for Agentic Workflow."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
from typing import Iterable, Mapping


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = PACKAGE_ROOT.parent.parent
PAYLOAD_ROOT = PACKAGE_ROOT / "payload"
MANIFEST = PAYLOAD_ROOT / "distribution" / "manifest.json"
MINIMUM_PYTHON = (3, 11)
MANIFEST_SCHEMA = 6
SEMVER = re.compile(r"\d+\.\d+\.\d+")
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")
REQUIRED_PACKAGE_FILES = (
    "SKILL.md",
    "VERSION",
    "scripts/adopt.py",
    "scripts/bootstrap.py",
    "scripts/lifecycle.py",
    "scripts/providers.py",
    "scripts/verify_package.py",
    "tests/behavior.py",
    "payload/VERSION",
    "payload/distribution/manifest.json",
    "payload/root/AGENTS.md.template",
    "payload/root/CLAUDE.md.template",
    "payload/ai-workflow/routing.md",
    "payload/ai-workflow/providers.json",
    "payload/ai-workflow/contracts/durable-state.md",
    "payload/ai-workflow/contracts/project-profile.md",
    "payload/ai-workflow/contracts/wayfinder-state.md",
)
REMOVED_RUNTIME_PATHS = (
    PAYLOAD_ROOT / "ai-workflow" / "runtime",
    PAYLOAD_ROOT / "ai-workflow" / "observability",
    PAYLOAD_ROOT / "hosts",
)


class VerificationError(RuntimeError):
    pass


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except (AttributeError, OSError, ValueError):
                pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def safe_relative(value: str) -> PurePosixPath:
    require(bool(value) and "\\" not in value, f"unsafe manifest path: {value!r}")
    path = PurePosixPath(value)
    require(
        not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts),
        f"unsafe manifest path: {value!r}",
    )
    return path


def version() -> str:
    package_version = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    payload_version = (PAYLOAD_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(SEMVER.fullmatch(package_version) is not None, "VERSION must use x.y.z")
    require(package_version == payload_version, "package and payload VERSION files differ")
    return package_version


def expected_mappings() -> list[dict[str, str]]:
    mappings = [
        {"source": "root/AGENTS.md.template", "target": "AGENTS.md"},
        {"source": "root/CLAUDE.md.template", "target": "CLAUDE.md"},
    ]
    skills_root = PAYLOAD_ROOT / "skills"
    for skill in sorted(skills_root.glob("*/SKILL.md")):
        mappings.append(
            {
                "source": skill.relative_to(PAYLOAD_ROOT).as_posix(),
                "target": f".agents/skills/{skill.parent.name}/SKILL.md",
            }
        )
    workflow_root = PAYLOAD_ROOT / "ai-workflow"
    for path in sorted(workflow_root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(PAYLOAD_ROOT).as_posix()
            target = ".ai-workflow/" + path.relative_to(workflow_root).as_posix()
            mappings.append({"source": relative, "target": target})
    return sorted(mappings, key=lambda item: item["target"])


def generated_manifest() -> Mapping[str, object]:
    return {
        "schema_version": MANIFEST_SCHEMA,
        "framework_version": version(),
        "framework_owned": expected_mappings(),
    }


def refresh_manifest() -> None:
    MANIFEST.write_text(
        json.dumps(generated_manifest(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Refreshed {MANIFEST.relative_to(PACKAGE_ROOT)}")


def check_structure() -> None:
    for relative in REQUIRED_PACKAGE_FILES:
        path = PACKAGE_ROOT / relative
        require(path.is_file() and not path.is_symlink(), f"missing or unsafe package file: {relative}")
    for path in REMOVED_RUNTIME_PATHS:
        require(
            not path.is_symlink()
            and (
                not path.exists()
                or not any(child.is_file() or child.is_symlink() for child in path.rglob("*"))
            ),
            f"deferred v0 subsystem remains packaged: {path}",
        )
    require(
        not (PAYLOAD_ROOT / "ai-workflow/templates/active-state.md").exists(),
        "retired active-index template remains packaged",
    )
    require(not (REPOSITORY_ROOT / "docs" / "enforcement.md").exists(), "obsolete controller documentation remains")
    require(not (REPOSITORY_ROOT / "docs" / "observability.md").exists(), "obsolete observability documentation remains")


def check_manifest() -> None:
    try:
        actual = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read distribution manifest: {exc}") from exc
    require(actual == generated_manifest(), "distribution manifest is stale; run verify_package.py --refresh-manifest")
    mappings = actual["framework_owned"]
    sources: list[str] = []
    targets: list[str] = []
    for item in mappings:
        require(isinstance(item, dict) and set(item) == {"source", "target"}, "invalid manifest mapping")
        source = safe_relative(item["source"])
        target = safe_relative(item["target"])
        require(target.parts[0] != ".ai-workflow-state", "manifest must not own durable project state")
        require(".ai-workflow/state" not in target.as_posix(), "manifest must not recreate obsolete workflow state")
        sources.append(source.as_posix())
        targets.append(target.as_posix())
    require(len(sources) == len(set(sources)), "manifest source paths are duplicated")
    require(len(targets) == len(set(targets)), "manifest target paths are duplicated")


def check_filesystem() -> None:
    for path in PACKAGE_ROOT.rglob("*"):
        require(not path.is_symlink(), f"package contains a symlink: {path.relative_to(PACKAGE_ROOT)}")
        require(
            "__pycache__" not in path.parts and path.suffix != ".pyc",
            f"package contains generated Python cache data: {path.relative_to(PACKAGE_ROOT)}",
        )
        if path.is_file():
            mode = stat.S_IMODE(path.stat().st_mode)
            if os.name != "nt":
                require(mode == 0o644, f"package file mode must be 0644: {path.relative_to(PACKAGE_ROOT)}")
    for script in PACKAGE_ROOT.rglob("*.py"):
        compile(script.read_text(encoding="utf-8"), str(script), "exec")


def check_router_contract() -> None:
    agents = (PAYLOAD_ROOT / "root" / "AGENTS.md.template").read_text(encoding="utf-8")
    routing = (PAYLOAD_ROOT / "ai-workflow" / "routing.md").read_text(encoding="utf-8")
    durable = (PAYLOAD_ROOT / "ai-workflow" / "contracts" / "durable-state.md").read_text(encoding="utf-8")
    wayfinder = (PAYLOAD_ROOT / "ai-workflow" / "contracts" / "wayfinder-state.md").read_text(encoding="utf-8")
    require("Every request MUST be evaluated" in agents, "root policy lacks mandatory routing")
    require("`direct`" in agents and "minimum useful process" in routing, "router lacks the minimum/direct contract")
    require("MUST NOT" in agents and "authority" in agents, "root policy lacks the authorization boundary")
    require(".ai-workflow-state/" in durable, "durable-state contract lacks the canonical state root")
    require("no global active-workflow index" in durable, "durable-state contract retains a global active index")
    require("legacy-active.md" in durable, "durable-state contract lacks legacy active-index preservation")
    require(
        "Multiple unrelated active or interrupted records may coexist" in durable,
        "durable-state contract lacks independent record continuity",
    )
    require(
        ".ai-workflow-state/wayfinder/" in agents and "unrelated map" in agents,
        "root policy lacks minimal Wayfinder progressive-loading guidance",
    )
    for required in (
        "unknowns/",
        "decisions/",
        "tickets/",
        "Do not read every child file",
        "Do not create or update `.ai-workflow-state/active.md`",
    ):
        require(required in wayfinder, f"Wayfinder state contract lacks required boundary: {required}")
    combined = agents + routing + durable + wayfinder
    require(
        "runtime/README.md" not in combined and ".ai-workflow/runtime" not in combined,
        "router still depends on the removed controller payload",
    )


def check_provider_declaration() -> None:
    path = PAYLOAD_ROOT / "ai-workflow" / "providers.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(raw, dict) and raw.get("schema_version") == 4, "unsupported provider declaration")
    provider = raw.get("provider")
    capabilities = raw.get("capabilities")
    require(isinstance(provider, dict) and isinstance(capabilities, dict), "provider declaration is incomplete")
    require(re.fullmatch(r"[^/]+/[^/]+", str(provider.get("repository"))) is not None, "invalid provider repository")
    require(re.fullmatch(r"v\d+\.\d+\.\d+", str(provider.get("version"))) is not None, "provider version must be pinned")
    skills = provider.get("skills")
    require(isinstance(skills, list) and skills, "provider skills must be a non-empty array")
    names: set[str] = set()
    for item in skills:
        require(isinstance(item, dict), "provider skill entries must be objects")
        name = item.get("name")
        require(isinstance(name, str) and PurePosixPath(name).name == name, "invalid provider skill name")
        require(name not in names, f"duplicate provider skill: {name}")
        names.add(name)
        safe_relative(str(item.get("path")))
        invocation = item.get("invocation")
        require(isinstance(invocation, dict), f"provider skill {name} lacks invocation policy")
        require(set(invocation.values()) <= {"implicit", "user-only", "unavailable"}, f"invalid invocation policy for {name}")
    require(set(capabilities.values()) <= names, "capability points to an undeclared provider skill")


def check_scenarios() -> None:
    tests = PACKAGE_ROOT / "tests"
    for name in ("acceptance-scenarios.json", "decision-contract-scenarios.json"):
        raw = json.loads((tests / name).read_text(encoding="utf-8"))
        require(isinstance(raw, list) and raw, f"{name} must contain scenarios")
        ids = []
        for item in raw:
            require(isinstance(item, dict) and isinstance(item.get("id"), str), f"invalid scenario in {name}")
            ids.append(item["id"])
        require(len(ids) == len(set(ids)), f"duplicate scenario id in {name}")
    behavior = subprocess.run(
        [sys.executable, str(tests / "behavior.py"), "validate"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        errors="backslashreplace",
    )
    require(
        behavior.returncode == 0,
        "behavioral scenario validation failed: "
        + (behavior.stderr.strip() or behavior.stdout.strip()),
    )


def check_markdown_links() -> None:
    roots = [REPOSITORY_ROOT / "README.md", REPOSITORY_ROOT / "docs", PACKAGE_ROOT / "SKILL.md", PAYLOAD_ROOT / "ai-workflow"]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(path for path in root.rglob("*.md") if path.is_file())
    for path in files:
        text = path.read_text(encoding="utf-8")
        for destination in MARKDOWN_LINK.findall(text):
            destination = destination.split("#", 1)[0]
            if not destination or "://" in destination or destination.startswith("mailto:"):
                continue
            candidate = (path.parent / destination).resolve()
            require(candidate.exists(), f"broken local Markdown link in {path.relative_to(REPOSITORY_ROOT)}: {destination}")


def run_tests() -> None:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(PACKAGE_ROOT / "tests"), "-p", "test_*.py", "-v"],
        cwd=REPOSITORY_ROOT,
        env=environment,
    )
    require(result.returncode == 0, "test suite failed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-manifest", action="store_true")
    parser.add_argument("--tests", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    configure_console()
    if sys.version_info < MINIMUM_PYTHON:
        print("ERROR: Agentic Workflow requires Python 3.11 or newer", file=sys.stderr)
        return 2
    args = build_parser().parse_args(argv)
    try:
        if args.refresh_manifest:
            refresh_manifest()
        for check in (
            check_structure,
            check_manifest,
            check_filesystem,
            check_router_contract,
            check_provider_declaration,
            check_scenarios,
            check_markdown_links,
        ):
            check()
        if args.tests:
            run_tests()
        print("OK: Agentic Workflow package verification passed.")
        return 0
    except (VerificationError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
