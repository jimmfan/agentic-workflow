#!/usr/bin/env python3
"""Validate the self-contained Agentic Workflow distribution package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Dict, Iterable, List, Mapping, Sequence


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PAYLOAD_ROOT = PACKAGE_ROOT / "payload"
MANIFEST_PATH = PAYLOAD_ROOT / "distribution" / "manifest.json"
SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
SKILLS = (
    "workflow-debugging",
    "workflow-decomposition",
    "workflow-discovery",
    "workflow-implementation",
    "workflow-review",
    "workflow-teach",
    "workflow-verification",
)
SEEDS = (
    {"source": "ai-workflow/templates/project-profile.md", "target": "ai-workflow/project-profile.md"},
    {"source": "ai-workflow/templates/active-state.md", "target": "ai-workflow/state/active.md"},
)
RETIRED = (
    ".agents/skills/hermes-delegation/SKILL.md",
    "adapters/hermes/profile-config.yaml",
    "adapters/hermes/request.schema.json",
    "adapters/hermes/result.schema.json",
    "adapters/hermes/smoke-request.json",
    "docs/integrations/hermes.md",
    "scripts/hermes_adapter.py",
)


class VerificationError(RuntimeError):
    """A package invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_relative(raw: str) -> PurePosixPath:
    require(isinstance(raw, str), f"manifest path must be a string: {raw!r}")
    path = PurePosixPath(raw)
    require(bool(raw) and not path.is_absolute() and ".." not in path.parts and "." not in path.parts and "\\" not in raw, f"unsafe manifest path: {raw!r}")
    return path


def payload_files() -> List[str]:
    excluded = {"VERSION", "distribution/manifest.json"}
    return sorted(
        path.relative_to(PAYLOAD_ROOT).as_posix()
        for path in PAYLOAD_ROOT.rglob("*")
        if path.is_file() and not path.is_symlink() and path.relative_to(PAYLOAD_ROOT).as_posix() not in excluded
    )


def target_for(source: str) -> str:
    if source == "root/AGENTS.md.template":
        return "AGENTS.md"
    match = re.fullmatch(r"skills/([^/]+)/(.*)", source)
    if match:
        return f".agents/skills/{match.group(1)}/{match.group(2)}"
    return source


def version() -> str:
    package_version = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(SEMVER.fullmatch(package_version) is not None, f"invalid package VERSION: {package_version!r}")
    return package_version


def generated_manifest() -> Mapping[str, object]:
    sources = payload_files()
    owned = [{"source": source, "target": target_for(source)} for source in sources]
    checksum_paths = set(sources)
    checksum_paths.update(seed["source"] for seed in SEEDS)
    return {
        "schema_version": 2,
        "framework_version": version(),
        "framework_owned": owned,
        "project_seeds": list(SEEDS),
        "checksums": {relative: sha256(PAYLOAD_ROOT / relative) for relative in sorted(checksum_paths)},
        "retired_framework_owned": list(RETIRED),
    }


def refresh_manifest() -> None:
    payload_version = version() + "\n"
    (PAYLOAD_ROOT / "VERSION").write_text(payload_version, encoding="utf-8")
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(generated_manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_manifest() -> Mapping[str, object]:
    try:
        value = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read package manifest: {exc}") from exc
    require(isinstance(value, dict), "package manifest must be a JSON object")
    return value


def parse_frontmatter(path: Path) -> Mapping[str, str]:
    text = path.read_text(encoding="utf-8")
    require(text.startswith("---\n"), f"missing YAML frontmatter: {path}")
    parts = text.split("---\n", 2)
    require(len(parts) == 3, f"unterminated YAML frontmatter: {path}")
    block = parts[1]
    fields: Dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def check_structure() -> None:
    required = [
        PACKAGE_ROOT / "SKILL.md",
        PACKAGE_ROOT / "VERSION",
        PACKAGE_ROOT / "scripts" / "adopt.py",
        PACKAGE_ROOT / "scripts" / "bootstrap.py",
        PACKAGE_ROOT / "scripts" / "verify_package.py",
        PAYLOAD_ROOT / "root" / "AGENTS.md.template",
        PAYLOAD_ROOT / "VERSION",
        MANIFEST_PATH,
        PAYLOAD_ROOT / "ai-workflow" / "README.md",
    ]
    required.extend(PAYLOAD_ROOT / "skills" / name / "SKILL.md" for name in SKILLS)
    for path in required:
        require(path.is_file() and not path.is_symlink(), f"missing regular package file: {path.relative_to(PACKAGE_ROOT)}")
    package_fields = parse_frontmatter(PACKAGE_ROOT / "SKILL.md")
    require(package_fields.get("name") == "agentic-workflow", "bootstrap skill name must be agentic-workflow")
    for name in SKILLS:
        path = PAYLOAD_ROOT / "skills" / name / "SKILL.md"
        fields = parse_frontmatter(path)
        require(fields.get("name") == name, f"skill name does not match directory: {name}")
        require(bool(fields.get("description")), f"skill lacks description: {name}")


def check_manifest() -> None:
    payload_version = (PAYLOAD_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(payload_version == version(), "payload VERSION must equal package VERSION")
    actual = load_manifest()
    expected = generated_manifest()
    require(actual == expected, "manifest/version/checksums drifted; run verify_package.py --refresh-manifest")
    mappings = actual["framework_owned"]  # type: ignore[index]
    require(isinstance(mappings, list), "framework_owned must be an array")
    targets = []
    for item in mappings:
        require(isinstance(item, dict) and set(item) == {"source", "target"}, "framework_owned entries need source and target")
        source = safe_relative(item["source"])
        target = safe_relative(item["target"])
        require((PAYLOAD_ROOT / source).is_file(), f"manifest-owned source is missing: {source}")
        targets.append(target)
    require(len(targets) == len(set(targets)), "framework_owned target paths must be unique")


def check_inert_payload() -> None:
    allowed_package_entries = {"SKILL.md", "VERSION", "examples", "payload", "scripts", "tests"}
    require({path.name for path in PACKAGE_ROOT.iterdir()} <= allowed_package_entries, "package root contains an unexpected entry")
    allowed_payload_entries = {"VERSION", "ai-workflow", "distribution", "docs", "root", "skills"}
    require({path.name for path in PAYLOAD_ROOT.iterdir()} == allowed_payload_entries, "payload top-level entries drifted")
    require(not (PAYLOAD_ROOT / "AGENTS.md").exists(), "payload must not contain an active root AGENTS.md")
    require(not (PAYLOAD_ROOT / ".agents").exists(), "payload must not contain an active .agents tree")
    require(not (PAYLOAD_ROOT / ".github").exists(), "payload must not contain an active .github customization tree")
    nested_agents = [path for path in PAYLOAD_ROOT.rglob("AGENTS.md")]
    require(not nested_agents, "payload contains an active AGENTS.md instead of an inert template")
    symlinks = [path.relative_to(PACKAGE_ROOT).as_posix() for path in PACKAGE_ROOT.rglob("*") if path.is_symlink()]
    require(not symlinks, "package must not contain symlinks: " + ", ".join(symlinks))


def check_workflow_contract() -> None:
    policy = (PAYLOAD_ROOT / "root" / "AGENTS.md.template").read_text(encoding="utf-8")
    require(len(policy.encode("utf-8")) < 5000, "installed root policy exceeds the compact v0 budget")
    for name in SKILLS:
        require(name in policy, f"root policy does not route to {name}")
    catalog_path = PACKAGE_ROOT / "tests" / "acceptance-scenarios.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read acceptance catalog: {exc}") from exc
    require(isinstance(catalog, list) and len(catalog) == 32, "acceptance catalog must contain 32 core scenarios")
    require([item.get("id") for item in catalog if isinstance(item, dict)] == list(range(1, 33)), "acceptance scenario IDs must be sequential")
    required = {"id", "requirement", "prompt", "setup", "expected_route", "expected_behavior", "evidence"}
    for item in catalog:
        require(isinstance(item, dict) and set(item) == required, "acceptance scenario fields drifted")
        require(all(str(item[field]).strip() for field in required - {"id"}), f"acceptance scenario {item.get('id')} has an empty field")
    routes = " ".join(str(item["expected_route"]) for item in catalog)
    for route in ("normal", "teach", "discovery", "debugging", "decomposition", "implementation", "verification", "review"):
        require(route in routes, f"acceptance catalog lacks the {route} route")


def check_no_external_runtime() -> None:
    forbidden_paths = []
    forbidden_text = []
    allowed_metadata = {Path(__file__).resolve(), MANIFEST_PATH.resolve()}
    for path in PACKAGE_ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(PACKAGE_ROOT).as_posix()
        if "hermes" in relative.lower():
            forbidden_paths.append(relative)
        if path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8")
            if "hermes" in text.lower() and path.resolve() not in allowed_metadata:
                forbidden_text.append(relative)
    require(not forbidden_paths, "forbidden external-runtime paths packaged: " + ", ".join(forbidden_paths))
    require(not forbidden_text, "forbidden external-runtime references packaged: " + ", ".join(forbidden_text))


def check_markdown_links() -> None:
    pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    failures = []
    for path in PACKAGE_ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for raw in pattern.findall(text):
            target = raw.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:") or target.startswith("/"):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(PACKAGE_ROOT.resolve())
            except ValueError:
                failures.append(f"{path.relative_to(PACKAGE_ROOT)} -> {raw} (escapes package)")
                continue
            if not resolved.exists():
                failures.append(f"{path.relative_to(PACKAGE_ROOT)} -> {raw}")
    require(not failures, "broken package Markdown links: " + "; ".join(failures))


def run_tests() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(PACKAGE_ROOT / "tests"), "-p", "test_*.py", "-v"],
        cwd=PACKAGE_ROOT,
    )
    require(result.returncode == 0, "package lifecycle tests failed")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-manifest", action="store_true", help="derive payload metadata from package VERSION and files")
    parser.add_argument("--tests", action="store_true", help="also run lifecycle integration tests")
    return parser.parse_args(argv)


def main(argv: Iterable[str] = ()) -> int:
    args = parse_args(list(argv))
    if args.refresh_manifest:
        refresh_manifest()
    checks = (
        check_structure,
        check_manifest,
        check_inert_payload,
        check_workflow_contract,
        check_no_external_runtime,
        check_markdown_links,
    )
    for check in checks:
        check()
        print(f"OK: {check.__name__}")
    if args.tests:
        run_tests()
        print("OK: lifecycle integration tests")
    print("OK: distributable package is internally consistent.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except VerificationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
