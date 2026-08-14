from __future__ import annotations

import base64
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
from typing import Mapping, Optional


PACKAGE = Path(__file__).resolve().parent.parent
ADOPT = PACKAGE / "scripts" / "adopt.py"
BOOTSTRAP = PACKAGE / "scripts" / "bootstrap.py"
LIFECYCLE = PACKAGE / "scripts" / "lifecycle.py"
PROVIDERS = PACKAGE / "scripts" / "providers.py"
VERIFY = PACKAGE / "scripts" / "verify_package.py"
REVISION = "1" * 40
FORMER_FRAMEWORK_DOCS = (
    "docs/architecture.md",
    "docs/decisions/0002-use-checksummed-copy-adoption.md",
    "docs/decisions/0003-use-internal-reference-inspired-workflows.md",
    "docs/decisions/0005-add-decomposition-and-independent-review.md",
    "docs/decisions/0006-use-inert-bootstrap-payload.md",
    "docs/routing.md",
    "docs/verification.md",
)
LEGACY_PROJECT_PROFILE = b"""# Project profile

## Purpose and success

Describe the project, its users, and observable success.

## Technology and architecture

List verified technologies, important components, and their relationships.

## Important paths

Map the few directories an agent usually needs. Name the project-owned durable
specification location and local ticket destination or accepted native tracker,
or state that each has not been established.

## Terminology

Define project-specific terms. Use `None` when there are none.

## Constraints and policy

Record security, organizational, compatibility, approval, and scope constraints.

## Delivery workflow

Describe how a change normally moves from development through release. State any
plan-approval policy, when proportional independent review is required, and who
may accept a review limitation. Review does not replace executable Verification.

## Commands

Copy a complete entry from `ai-workflow/contracts/project-profile.md` for each
real command or manual check. If none are configured, write:

`No project checks are configured. Report verification as blocked; do not invent commands.`

## Debugging model

Describe the project's request/data/control path and useful evidence at each
layer. Use `None` until verified.

## Decision considerations

List domain-specific tradeoffs and policies. Use `None` until verified.

## Profile maintenance

- Owner: Project maintainers
- Last reviewed: YYYY-MM-DD
- Becomes stale when: Architecture, toolchain, delivery, or policy changes.
- Conflict behavior: Verify against source and live evidence, report the conflict,
  and update this profile before relying on the disputed field.
"""


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load test module from {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


ADOPTER = load_script("agentic_workflow_adopt", ADOPT)
BOOTSTRAPPER = load_script("agentic_workflow_bootstrap", BOOTSTRAP)
LIFECYCLE_MANAGER = load_script("agentic_workflow_lifecycle", LIFECYCLE)
PROVIDER_MANAGER = load_script("agentic_workflow_providers", PROVIDERS)
VERIFIER = load_script("agentic_workflow_verify", VERIFY)
REAL_PROVIDER_LOAD_DECLARATION = PROVIDER_MANAGER.load_declaration


def run(
    *args: object,
    cwd: Optional[Path] = None,
    env: Optional[Mapping[str, str]] = None,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )


def git_repository(root: Path) -> Path:
    root.mkdir(parents=True)
    result = run("git", "init", "-q", str(root))
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return root


def adopt(script: Path, action: str, target: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return run(sys.executable, script, action, target, "--source-revision", REVISION, *extra)


def package_accepting_installed_fixture(base: Path, target: Path, label: str) -> Path:
    """Create a new-package fixture whose immutable manifest reviews this synthetic install."""
    copied = base / label
    shutil.copytree(PACKAGE, copied)
    installed = json.loads(
        (target / "ai-workflow/install-manifest.json").read_text(encoding="utf-8")
    )
    predecessor = {
        "framework_version": installed["framework_version"],
        "source_revisions": [installed["source_revision"]],
        "install_manifest_schemas": [installed["schema_version"]],
        "framework_files": {
            path: details["source_sha256"]
            for path, details in installed["framework_files"].items()
        },
    }
    manifest_path = copied / "payload/distribution/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["accepted_predecessors"].append(predecessor)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return copied / "scripts/adopt.py"


def fixture_provider_source_files(skill: Mapping[str, object]) -> Mapping[str, bytes]:
    """Return deterministic upstream-like bytes before GitHub metadata injection."""
    name = str(skill["name"])
    invocation = skill["invocation"]
    if not isinstance(invocation, Mapping):
        raise AssertionError(f"invalid fixture invocation declaration for {name}")
    disable_model_invocation = (
        "disable-model-invocation: true\n"
        if invocation["github-copilot"] == "user-only"
        else ""
    )
    allow_implicit_invocation = "true" if invocation["codex"] == "implicit" else "false"
    files: dict[str, bytes] = {}
    for relative_value in skill["files"]:
        relative = str(relative_value)
        if relative == "SKILL.md":
            content = (
                "---\n"
                f"description: Hermetic fixture for {name}.\n"
                + disable_model_invocation
                + f"name: {name}\n"
                "---\n"
                f"# {name}\n"
            )
        elif relative == "agents/openai.yaml":
            content = (
                "interface:\n"
                f"  display_name: \"{name}\"\n"
                f"  short_description: \"Hermetic fixture for {name}\"\n"
                "policy:\n"
                f"  allow_implicit_invocation: {allow_implicit_invocation}\n"
            )
        else:
            content = f"fixture: {name}/{relative}\n"
        files[relative] = content.encode("utf-8")
    return files


def fixture_provider_declaration() -> tuple[Mapping[str, object], list[Mapping[str, object]]]:
    """Mirror the packaged declaration while authenticating hermetic fixture bytes."""
    provider, skills = REAL_PROVIDER_LOAD_DECLARATION()
    cloned_provider = json.loads(json.dumps(provider))
    cloned_skills = cloned_provider["skills"]
    for skill in cloned_skills:
        skill["source_sha256"] = {
            relative: hashlib.sha256(content).hexdigest()
            for relative, content in fixture_provider_source_files(skill).items()
        }
    return cloned_provider, cloned_skills


def fixture_package(source: Path, destination: Path) -> Path:
    """Copy a package whose declaration and reviewed lock describe fixture bytes."""
    shutil.copytree(source, destination)
    declaration_path = destination / "payload/ai-workflow/providers.json"
    declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
    for skill in declaration["provider"]["skills"]:
        skill["source_sha256"] = {
            relative: hashlib.sha256(content).hexdigest()
            for relative, content in fixture_provider_source_files(skill).items()
        }
    declaration_path.write_text(
        json.dumps(declaration, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    provider = declaration["provider"]
    fixture_identity = {
        "repository": provider["repository"],
        "revision": provider["revision"],
        "version": provider["version"],
        "skills": [
            {
                key: skill.get(key)
                for key in ("name", "path", "tree_sha", "files", "source_sha256")
            }
            for skill in provider["skills"]
        ],
    }
    fixture_digest = hashlib.sha256(
        json.dumps(
            fixture_identity,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    verifier_path = destination / "scripts/verify_package.py"
    verifier_lines = verifier_path.read_text(encoding="utf-8").splitlines(keepends=True)
    lock_prefix = "AUDITED_PROVIDER_IDENTITY_SHA256 = "
    replacements = 0
    for index, line in enumerate(verifier_lines):
        if line.startswith(lock_prefix):
            # Fixture-only trust anchor: production refresh never rewrites this lock.
            verifier_lines[index] = f'{lock_prefix}"{fixture_digest}"\n'
            replacements += 1
    if replacements != 1:
        raise AssertionError("fixture package could not replace the provider identity lock")
    verifier_path.write_text("".join(verifier_lines), encoding="utf-8")
    refreshed = run(sys.executable, destination / "scripts/verify_package.py", "--refresh-manifest")
    if refreshed.returncode != 0:
        raise AssertionError(refreshed.stderr or refreshed.stdout)
    return destination


def write_provider_skill(
    root: Path,
    provider: Mapping[str, object],
    skill: Mapping[str, object],
    *,
    skills_root: Optional[Path] = None,
) -> Path:
    base = skills_root or root / ".agents/skills"
    destination = base / str(skill["name"])
    destination.mkdir(parents=True)
    metadata = (
        "metadata:\n"
        f"    github-path: {skill['path']}\n"
        f"    github-pinned: {provider['version']}\n"
        f"    github-ref: refs/tags/{provider['version']}\n"
        f"    github-repo: https://github.com/{provider['repository']}\n"
        f"    github-tree-sha: {skill['tree_sha']}\n"
    )
    for relative, source in fixture_provider_source_files(skill).items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if relative == "SKILL.md":
            marker = f"name: {skill['name']}\n".encode("utf-8")
            if source.count(marker) != 1:
                raise AssertionError(f"invalid fixture frontmatter for {skill['name']}")
            path.write_bytes(
                source.replace(marker, metadata.encode("utf-8") + marker, 1)
            )
        else:
            path.write_bytes(source)
    return destination


def fake_provider_install(
    _gh: Path,
    root: Path,
    provider: Mapping[str, object],
    skill: Mapping[str, object],
    *,
    directory: Optional[Path] = None,
) -> None:
    write_provider_skill(root, provider, skill, skills_root=directory)


def write_provider_state(
    root: Path,
    provider: Mapping[str, object],
    skills: list[Mapping[str, object]],
    *,
    origin: str = "preexisting-compatible",
) -> None:
    records = {}
    for skill in skills:
        name = str(skill["name"])
        directory = root / ".agents/skills" / name
        records[name] = {
            "files": {
                str(relative): PROVIDER_MANAGER.sha256(directory / str(relative))
                for relative in skill["files"]
            },
            "origin": origin,
            "path": skill["path"],
            "tree_sha": skill["tree_sha"],
        }
    state_path = root / "ai-workflow/provider-state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(PROVIDER_MANAGER.state_value(provider, records), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def provider_declaration_document(provider: Mapping[str, object]) -> Mapping[str, object]:
    declaration = json.loads(
        (PACKAGE / "payload/ai-workflow/providers.json").read_text(encoding="utf-8")
    )
    declaration["provider"] = json.loads(json.dumps(provider))
    return declaration


def write_authenticated_provider_predecessor(
    root: Path,
    declaration: Mapping[str, object],
    manifest_path: Path,
    *,
    framework_version: str = "0.6.9",
    source_revision: str = "2" * 40,
) -> None:
    """Write fixture-only payload evidence that authenticates an old provider declaration."""
    declaration_path = root / "ai-workflow/providers.json"
    declaration_path.parent.mkdir(parents=True, exist_ok=True)
    declaration_bytes = (
        json.dumps(declaration, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    declaration_path.write_bytes(declaration_bytes)
    digest = hashlib.sha256(declaration_bytes).hexdigest()
    install_manifest = {
        "framework_files": {
            "ai-workflow/providers.json": {
                "origin": "created",
                "sha256": digest,
                "source_sha256": digest,
            }
        },
        "framework_version": framework_version,
        "installed_at": "2026-08-14T00:00:00+00:00",
        "project_owned": [],
        "schema_version": 2,
        "source_revision": source_revision,
    }
    (root / "ai-workflow/install-manifest.json").write_text(
        json.dumps(install_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    source_manifest = {
        "accepted_predecessors": [
            {
                "framework_files": {"ai-workflow/providers.json": digest},
                "framework_version": framework_version,
                "install_manifest_schemas": [2],
                "source_revisions": [source_revision],
            }
        ],
        "schema_version": 3,
    }
    manifest_path.write_text(
        json.dumps(source_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


UPGRADED_PROVIDER_SUFFIX = b"Upstream fixture revision B.\n"


def provider_upgrade_fixture(
    provider: Mapping[str, object],
    changed_names: set[str],
    *,
    change_identity: bool = True,
) -> tuple[Mapping[str, object], list[Mapping[str, object]]]:
    upgraded = json.loads(json.dumps(provider))
    if change_identity:
        upgraded["version"] = "v1.2.4"
        upgraded["revision"] = "3" * 40
    upgraded_skills = upgraded["skills"]
    for skill in upgraded_skills:
        if skill["name"] not in changed_names:
            continue
        changed_source = fixture_provider_source_files(skill)["SKILL.md"] + UPGRADED_PROVIDER_SUFFIX
        skill["source_sha256"]["SKILL.md"] = hashlib.sha256(changed_source).hexdigest()
        skill["tree_sha"] = "4" * 40
    return upgraded, upgraded_skills


def fake_upgraded_provider_install(
    changed_names: set[str],
):
    def install(
        _gh: Path,
        root: Path,
        provider: Mapping[str, object],
        skill: Mapping[str, object],
        *,
        directory: Optional[Path] = None,
    ) -> None:
        installed = write_provider_skill(root, provider, skill, skills_root=directory)
        if skill["name"] in changed_names:
            path = installed / "SKILL.md"
            path.write_bytes(path.read_bytes() + UPGRADED_PROVIDER_SUFFIX)

    return install


class LifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="agentic-workflow-test-")
        self.base = Path(self.temporary.name)
        self.provider_declaration_patch = mock.patch.object(
            PROVIDER_MANAGER,
            "load_declaration",
            side_effect=fixture_provider_declaration,
        )
        self.provider_declaration_patch.start()

    def tearDown(self) -> None:
        self.provider_declaration_patch.stop()
        self.temporary.cleanup()

    def test_all_entry_points_require_supported_python(self) -> None:
        modules = (ADOPTER, BOOTSTRAPPER, LIFECYCLE_MANAGER, PROVIDER_MANAGER, VERIFIER)
        for module in modules:
            with self.subTest(module=module.__name__):
                self.assertEqual(module.MINIMUM_PYTHON, (3, 11))
                with mock.patch.object(module.sys, "version_info", (3, 10, 14)):
                    with self.assertRaisesRegex(RuntimeError, "Python 3.11 or newer is required"):
                        module.require_supported_python()

    def test_fresh_install_is_one_operation_and_verified(self) -> None:
        target = git_repository(self.base / "target")
        result = adopt(ADOPT, "install", target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("installed and verified", result.stdout)
        self.assertTrue((target / "AGENTS.md").is_file())
        self.assertIn(
            "[route: router → …]",
            (target / "AGENTS.md").read_text(encoding="utf-8"),
        )
        claude = (target / "CLAUDE.md").read_bytes()
        managed, project = ADOPTER.parse_composite_policy(claude)
        self.assertEqual(managed, b"@AGENTS.md\n")
        self.assertEqual(project, b"")
        self.assertTrue((target / ".agents/skills/workflow-discovery/SKILL.md").is_file())
        self.assertFalse((target / ".agents/skills/workflow-teach").exists())
        self.assertEqual(LIFECYCLE_MANAGER.profile_state(target), "uninitialized")
        self.assertTrue((target / "ai-workflow/state/active.md").is_file())
        self.assertFalse((target / "docs").exists())
        for relative in FORMER_FRAMEWORK_DOCS:
            self.assertFalse((target / relative).exists())
        manifest = json.loads(
            (target / "ai-workflow/install-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["framework_files"]["AGENTS.md"]["origin"], "composite-created")
        self.assertEqual(manifest["framework_files"]["CLAUDE.md"]["origin"], "composite-created")
        status = adopt(ADOPT, "status", target)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("Installation is clean", status.stdout)

    def test_non_git_install_update_status_and_remove(self) -> None:
        target = self.base / "ordinary-project"
        target.mkdir()
        self.assertFalse((target / ".git").exists())

        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        status = adopt(ADOPT, "status", target)
        self.assertEqual(status.returncode, 0, status.stderr)
        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())
        self.assertTrue((target / "ai-workflow/project-profile.md").is_file())

    def test_project_profile_seed_has_a_deterministic_uninitialized_state(self) -> None:
        target = self.base / "profile-seed"
        profile = target / "ai-workflow/project-profile.md"
        profile.parent.mkdir(parents=True)
        source = PACKAGE / "payload/ai-workflow/templates/project-profile.md"
        profile.write_bytes(source.read_bytes())

        text = profile.read_text(encoding="utf-8")
        nonblank = [line for line in text.splitlines() if line.strip()]
        self.assertEqual(nonblank[:2], ["# Project profile", "Initialization: uninitialized"])
        sections = text.split("\n## ")
        self.assertEqual(len(sections), len(LIFECYCLE_MANAGER.PROFILE_HEADINGS) + 1)
        for expected, section in zip(LIFECYCLE_MANAGER.PROFILE_HEADINGS, sections[1:]):
            heading, body = section.split("\n", 1)
            self.assertEqual(heading, expected)
            self.assertEqual(body.strip(), "None")
        self.assertEqual(LIFECYCLE_MANAGER.profile_state(target), "uninitialized")

        initialized = text.replace(
            "Initialization: uninitialized",
            "Initialization: initialized",
            1,
        ).replace(
            "## Purpose and success\n\nNone",
            "## Purpose and success\n\nVerified reusable project purpose.",
            1,
        )
        profile.write_text(initialized, encoding="utf-8")
        self.assertEqual(LIFECYCLE_MANAGER.profile_state(target), "initialized")

        misplaced = text.replace("Initialization: uninitialized\n\n", "", 1).replace(
            "## Purpose and success\n",
            "## Purpose and success\n\nInitialization: uninitialized\n",
            1,
        )
        profile.write_text(misplaced, encoding="utf-8")
        self.assertEqual(LIFECYCLE_MANAGER.profile_state(target), "invalid")

    def test_legacy_uninitialized_profile_is_recognized_and_never_rewritten(self) -> None:
        self.assertEqual(
            hashlib.sha256(LEGACY_PROJECT_PROFILE).hexdigest(),
            LIFECYCLE_MANAGER.LEGACY_UNINITIALIZED_PROFILE_SHA256,
        )
        target = self.base / "legacy-profile-project"
        profile = target / "ai-workflow/project-profile.md"
        profile.parent.mkdir(parents=True)
        profile.write_bytes(LEGACY_PROJECT_PROFILE)

        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(LIFECYCLE_MANAGER.profile_state(target), "legacy-uninitialized")
        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertEqual(profile.read_bytes(), LEGACY_PROJECT_PROFILE)
        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(profile.read_bytes(), LEGACY_PROJECT_PROFILE)

    def test_status_reports_readiness_warnings_separately_from_integrity(self) -> None:
        target = self.base / "readiness-project"
        profile = target / "ai-workflow/project-profile.md"
        profile.parent.mkdir(parents=True)
        profile.write_bytes(
            (PACKAGE / "payload/ai-workflow/templates/project-profile.md").read_bytes()
        )
        child_statuses = [
            subprocess.CompletedProcess([], 0),
            subprocess.CompletedProcess([], 0),
        ]
        output = io.StringIO()
        with mock.patch.object(
            LIFECYCLE_MANAGER.subprocess,
            "run",
            side_effect=child_statuses,
        ), redirect_stdout(output):
            result = LIFECYCLE_MANAGER.status(target, REVISION)

        self.assertEqual(result, 0)
        rendered = output.getvalue()
        self.assertIn("Framework integrity: healthy", rendered)
        self.assertIn("Provider integrity: healthy", rendered)
        self.assertIn("Project readiness (warnings do not affect integrity status):", rendered)
        self.assertIn("project profile: uninitialized", rendered)
        self.assertIn("issue tracker config: missing", rendered)
        self.assertIn("domain config: missing", rendered)
        self.assertIn("triage config: missing", rendered)
        self.assertIn(
            "Codex setup workflow: user invocation required (`$setup-matt-pocock-skills`)",
            rendered,
        )
        self.assertIn(
            "GitHub Copilot setup workflow: user invocation required (`/setup-matt-pocock-skills`)",
            rendered,
        )
        self.assertIn("Claude Code setup workflow: unavailable", rendered)
        self.assertIn(
            "initialize the profile once from verified repository evidence",
            rendered,
        )

        profile.write_text(
            profile.read_text(encoding="utf-8").replace(
                "Initialization: uninitialized",
                "Initialization: initialized",
                1,
            ),
            encoding="utf-8",
        )
        configuration, _host_invocation = LIFECYCLE_MANAGER.load_provider_status_contract()
        for _label, relative in configuration:
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("verified configuration\n", encoding="utf-8")
        self.assertEqual(
            LIFECYCLE_MANAGER.project_readiness(target, configuration),
            {
                "project profile": "initialized",
                "issue tracker config": "configured",
                "domain config": "configured",
                "triage config": "configured",
            },
        )

    def test_provider_install_is_pinned_complete_idempotent_and_removable(self) -> None:
        target = self.base / "provider-target"
        target.mkdir()
        preexisting_skills_parent = target / ".agents/skills"
        preexisting_skills_parent.mkdir(parents=True)
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ) as install:
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        provider, skills = PROVIDER_MANAGER.load_declaration()
        self.assertEqual(install.call_count, len(skills))
        self.assertEqual(provider["version"], "v1.2.3")
        self.assertEqual(
            provider["revision"],
            "6acc160e4e0cd062dbbbd7a1b26ae92855edf07e",
        )
        self.assertTrue(PROVIDER_MANAGER.command_status(target, verbose=False))
        state_path = target / "ai-workflow/provider-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(set(state["skills"]), {str(skill["name"]) for skill in skills})
        self.assertTrue(all(record["origin"] == "created" for record in state["skills"].values()))
        for skill in skills:
            directory = target / ".agents/skills" / str(skill["name"])
            actual = sorted(
                path.relative_to(directory).as_posix()
                for path in directory.rglob("*")
                if path.is_file()
            )
            self.assertEqual(actual, skill["files"])

        with mock.patch.object(PROVIDER_MANAGER, "find_gh") as unused:
            PROVIDER_MANAGER.command_install(target, dry_run=False)
        unused.assert_not_called()

        PROVIDER_MANAGER.command_remove(target, dry_run=False)
        self.assertFalse(state_path.exists())
        for skill in skills:
            self.assertFalse((target / ".agents/skills" / str(skill["name"])).exists())
        self.assertTrue(preexisting_skills_parent.is_dir())

    def test_provider_preserves_preexisting_compatible_and_changed_skills(self) -> None:
        target = self.base / "provider-preservation"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        preexisting = skills[0]
        write_provider_skill(target, provider, preexisting)
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        state_path = target / "ai-workflow/provider-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["skills"][preexisting["name"]]["origin"], "preexisting-compatible")
        changed_name = str(skills[1]["name"])
        changed = target / ".agents/skills" / changed_name / "SKILL.md"
        changed.write_text(changed.read_text(encoding="utf-8") + "local change\n", encoding="utf-8")

        PROVIDER_MANAGER.command_remove(target, dry_run=False)
        self.assertTrue((target / ".agents/skills" / str(preexisting["name"])).is_dir())
        self.assertTrue((target / ".agents/skills" / changed_name).is_dir())
        for skill in skills[2:]:
            self.assertFalse((target / ".agents/skills" / str(skill["name"])).exists())

    def test_forged_provider_state_checksum_cannot_hide_or_delete_altered_source(self) -> None:
        target = self.base / "provider-forged-checksum"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        _provider, skills = PROVIDER_MANAGER.load_declaration()
        changed_name = str(skills[0]["name"])
        changed_path = target / ".agents/skills" / changed_name / "SKILL.md"
        altered = changed_path.read_bytes() + b"project-owned alteration\n"
        changed_path.write_bytes(altered)
        state_path = target / "ai-workflow/provider-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["skills"][changed_name]["files"]["SKILL.md"] = PROVIDER_MANAGER.sha256(
            changed_path
        )
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        self.assertFalse(PROVIDER_MANAGER.command_status(target, verbose=False))
        PROVIDER_MANAGER.command_remove(target, dry_run=False)

        self.assertFalse(state_path.exists())
        self.assertEqual(changed_path.read_bytes(), altered)
        self.assertTrue(changed_path.parent.is_dir())

    def test_forged_provider_state_extra_file_inventory_cannot_authorize_deletion(self) -> None:
        target = self.base / "provider-forged-extra-file"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        _provider, skills = PROVIDER_MANAGER.load_declaration()
        changed_name = str(skills[0]["name"])
        extra = target / ".agents/skills" / changed_name / "PROJECT-NOTES.md"
        extra.write_text("project-owned evidence\n", encoding="utf-8")
        state_path = target / "ai-workflow/provider-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["skills"][changed_name]["files"]["PROJECT-NOTES.md"] = PROVIDER_MANAGER.sha256(
            extra
        )
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        self.assertFalse(PROVIDER_MANAGER.command_status(target, verbose=False))
        PROVIDER_MANAGER.command_remove(target, dry_run=False)

        self.assertFalse(state_path.exists())
        self.assertEqual(extra.read_text(encoding="utf-8"), "project-owned evidence\n")
        self.assertTrue(extra.parent.is_dir())

    def test_provider_remove_preserves_skill_with_unexpected_empty_directory(self) -> None:
        target = self.base / "provider-empty-directory"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        _provider, skills = PROVIDER_MANAGER.load_declaration()
        changed_name = str(skills[0]["name"])
        empty = target / ".agents/skills" / changed_name / "project-owned-empty"
        empty.mkdir()

        self.assertFalse(PROVIDER_MANAGER.command_status(target, verbose=False))
        PROVIDER_MANAGER.command_remove(target, dry_run=False)

        self.assertTrue(empty.is_dir())
        self.assertFalse((target / "ai-workflow/provider-state.json").exists())

    def test_provider_rejects_altered_preexisting_body_against_authenticated_staging(self) -> None:
        target = self.base / "provider-authenticated-preexisting"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        preexisting = skills[0]
        directory = write_provider_skill(target, provider, preexisting)
        skill_path = directory / "SKILL.md"
        altered = skill_path.read_text(encoding="utf-8") + "locally altered body\n"
        skill_path.write_text(altered, encoding="utf-8")

        with mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ) as install:
            with self.assertRaisesRegex(
                PROVIDER_MANAGER.ProviderError,
                "source content is incompatible",
            ):
                PROVIDER_MANAGER.command_install(target, dry_run=False)

        install.assert_not_called()
        self.assertEqual(skill_path.read_text(encoding="utf-8"), altered)
        self.assertFalse((target / "ai-workflow/provider-state.json").exists())
        for skill in skills[1:]:
            self.assertFalse((target / ".agents/skills" / str(skill["name"])).exists())
        self.assertFalse(list(target.glob(".ai-workflow-providers-*")))

    def test_provider_install_rolls_back_when_staging_cleanup_fails(self) -> None:
        target = self.base / "provider-install-staging-cleanup"
        target.mkdir()
        with mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "cleanup_provider_staging",
            side_effect=OSError("simulated staging cleanup failure"),
        ):
            with self.assertRaisesRegex(OSError, "simulated staging cleanup failure"):
                PROVIDER_MANAGER.command_install(target, dry_run=False)

        self.assertFalse((target / "ai-workflow/provider-state.json").exists())
        self.assertFalse((target / ".agents/skills").exists())
        self.assertFalse(list(target.glob(".ai-workflow-providers-*")))

    def test_provider_remove_rolls_back_quarantine_failure(self) -> None:
        target = self.base / "provider-remove-rollback"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        _provider, skills = PROVIDER_MANAGER.load_declaration()
        state_path = target / "ai-workflow/provider-state.json"
        state_before = state_path.read_bytes()
        failed = False

        def fail_state_quarantine_once(source: Path, destination: Path) -> None:
            nonlocal failed
            if source == state_path and not failed:
                failed = True
                raise OSError("simulated quarantine rename failure")
            source.replace(destination)

        with mock.patch.object(
            PROVIDER_MANAGER,
            "rename_quarantined_path",
            side_effect=fail_state_quarantine_once,
        ):
            with self.assertRaisesRegex(OSError, "simulated quarantine rename failure"):
                PROVIDER_MANAGER.command_remove(target, dry_run=False)

        self.assertEqual(state_path.read_bytes(), state_before)
        for skill in skills:
            self.assertTrue(
                (target / ".agents/skills" / str(skill["name"])).is_dir(),
                skill["name"],
            )
        self.assertFalse(list(target.glob(".ai-workflow-provider-remove-*")))
        self.assertTrue(PROVIDER_MANAGER.command_status(target, verbose=False))

    def test_provider_remove_retains_quarantine_after_committed_cleanup_failure(self) -> None:
        target = self.base / "provider-remove-cleanup-failure"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        _provider, skills = PROVIDER_MANAGER.load_declaration()
        state_path = target / "ai-workflow/provider-state.json"
        real_rmtree = PROVIDER_MANAGER.shutil.rmtree
        failed = False

        def fail_quarantine_cleanup_once(path: object, *args: object, **kwargs: object) -> None:
            nonlocal failed
            candidate = Path(path)
            if candidate.name.startswith(PROVIDER_MANAGER.REMOVAL_QUARANTINE_PREFIX) and not failed:
                failed = True
                raise OSError("simulated committed quarantine cleanup failure")
            real_rmtree(path, *args, **kwargs)

        diagnostics = io.StringIO()
        with mock.patch.object(
            PROVIDER_MANAGER.shutil,
            "rmtree",
            side_effect=fail_quarantine_cleanup_once,
        ), redirect_stderr(diagnostics):
            PROVIDER_MANAGER.command_remove(target, dry_run=False)

        quarantines = list(target.glob(f"{PROVIDER_MANAGER.REMOVAL_QUARANTINE_PREFIX}*"))
        self.assertEqual(len(quarantines), 1)
        self.assertIn("provider removal committed", diagnostics.getvalue())
        self.assertIn(str(quarantines[0]), diagnostics.getvalue())
        self.assertFalse(state_path.exists())
        for skill in skills:
            self.assertFalse((target / ".agents/skills" / str(skill["name"])).exists())
        with self.assertRaisesRegex(
            PROVIDER_MANAGER.ProviderError,
            "retained provider-removal quarantine blocks another removal",
        ):
            PROVIDER_MANAGER.quarantine_provider_removal(target, (), state_path)
        self.assertEqual(
            list(target.glob(f"{PROVIDER_MANAGER.REMOVAL_QUARANTINE_PREFIX}*")),
            quarantines,
        )

    def test_provider_incompatibility_fails_without_fallback_or_overwrite(self) -> None:
        target = self.base / "provider-conflict"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        conflict = write_provider_skill(target, provider, skills[0])
        skill_path = conflict / "SKILL.md"
        original = skill_path.read_text(encoding="utf-8").replace(
            "github-pinned: v1.2.3",
            "github-pinned: v9.9.9",
        )
        skill_path.write_text(original, encoding="utf-8")

        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ) as install:
            with self.assertRaisesRegex(
                PROVIDER_MANAGER.ProviderError,
                "incompatible or unexpected GitHub metadata",
            ):
                PROVIDER_MANAGER.command_install(target, dry_run=False)
        install.assert_not_called()
        self.assertEqual(skill_path.read_text(encoding="utf-8"), original)
        self.assertFalse((target / "ai-workflow/provider-state.json").exists())

    def test_provider_source_normalization_rejects_unexpected_injected_metadata(self) -> None:
        target = self.base / "provider-unexpected-metadata"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        skill = skills[0]
        directory = write_provider_skill(target, provider, skill)
        skill_path = directory / "SKILL.md"
        skill_path.write_text(
            skill_path.read_text(encoding="utf-8").replace(
                "    github-tree-sha:",
                "    unexpected-provider-field: value\n    github-tree-sha:",
                1,
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            PROVIDER_MANAGER.ProviderError,
            "incompatible or unexpected GitHub metadata",
        ):
            PROVIDER_MANAGER.verify_skill(target, provider, skill)

    def test_provider_rejects_noncanonical_quoted_provenance_value(self) -> None:
        target = self.base / "provider-quoted-metadata"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        skill = skills[0]
        directory = write_provider_skill(target, provider, skill)
        skill_path = directory / "SKILL.md"
        expected = f"    github-path: {skill['path']}"
        skill_path.write_text(
            skill_path.read_text(encoding="utf-8").replace(
                expected,
                f"    github-path: '{skill['path']}'",
                1,
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            PROVIDER_MANAGER.ProviderError,
            "incompatible or unexpected GitHub metadata",
        ):
            PROVIDER_MANAGER.verify_skill(target, provider, skill)

    def test_provider_rejects_copilot_invocation_metadata_mismatch(self) -> None:
        target = self.base / "provider-copilot-invocation-mismatch"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        skill = next(item for item in skills if item["name"] == "wayfinder")
        directory = write_provider_skill(target, provider, skill)
        skill_path = directory / "SKILL.md"
        skill_path.write_text(
            skill_path.read_text(encoding="utf-8").replace(
                "disable-model-invocation: true",
                "disable-model-invocation: false",
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            PROVIDER_MANAGER.ProviderError,
            "incompatible github-copilot invocation",
        ):
            PROVIDER_MANAGER.verify_skill(target, provider, skill)

    def test_provider_rejects_codex_invocation_metadata_mismatch(self) -> None:
        target = self.base / "provider-codex-invocation-mismatch"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        skill = next(item for item in skills if item["name"] == "wayfinder")
        directory = write_provider_skill(target, provider, skill)
        metadata_path = directory / "agents/openai.yaml"
        metadata_path.write_text(
            metadata_path.read_text(encoding="utf-8").replace(
                "allow_implicit_invocation: false",
                "allow_implicit_invocation: true",
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            PROVIDER_MANAGER.ProviderError,
            "incompatible codex invocation",
        ):
            PROVIDER_MANAGER.verify_skill(target, provider, skill)

    def test_provider_status_detects_missing_adjacent_resource(self) -> None:
        target = self.base / "provider-missing-resource"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)
        (target / ".agents/skills/tdd/mocking.md").unlink()

        self.assertFalse(PROVIDER_MANAGER.command_status(target, verbose=False))
        with self.assertRaisesRegex(PROVIDER_MANAGER.ProviderError, "locally changed or removed"):
            PROVIDER_MANAGER.command_update(target, dry_run=False)

    def test_clean_predecessor_provider_migrates_to_declared_revision(self) -> None:
        target = self.base / "provider-upgrade"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        old_provider, skills = PROVIDER_MANAGER.load_declaration()
        predecessor_manifest = self.base / "provider-upgrade-predecessors.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(old_provider),
            predecessor_manifest,
        )
        upgraded_provider, upgraded_skills = provider_upgrade_fixture(
            old_provider,
            {"code-review"},
        )

        state_path = target / "ai-workflow/provider-state.json"
        before_dry_run = {
            path.relative_to(target).as_posix(): path.read_bytes()
            for path in target.rglob("*")
            if path.is_file()
        }
        with mock.patch.object(
            PROVIDER_MANAGER,
            "load_declaration",
            return_value=(upgraded_provider, upgraded_skills),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_upgraded_provider_install({"code-review"}),
        ):
            PROVIDER_MANAGER.command_update(target, dry_run=True)
            self.assertEqual(
                {
                    path.relative_to(target).as_posix(): path.read_bytes()
                    for path in target.rglob("*")
                    if path.is_file()
                },
                before_dry_run,
            )
            PROVIDER_MANAGER.command_update(target, dry_run=False)

        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["provider"]["version"], "v1.2.4")
        self.assertEqual(state["provider"]["revision"], "3" * 40)
        self.assertTrue(
            (target / ".agents/skills/code-review/SKILL.md").read_bytes().endswith(
                UPGRADED_PROVIDER_SUFFIX
            )
        )
        self.assertTrue(all(record["origin"] == "created" for record in state["skills"].values()))
        self.assertFalse(list(target.glob(f"{PROVIDER_MANAGER.UPDATE_QUARANTINE_PREFIX}*")))

    def test_locally_modified_predecessor_provider_refuses_migration(self) -> None:
        target = self.base / "provider-upgrade-modified"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)
        old_provider, _skills = PROVIDER_MANAGER.load_declaration()
        predecessor_manifest = self.base / "modified-predecessor.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(old_provider),
            predecessor_manifest,
        )
        upgraded_provider, upgraded_skills = provider_upgrade_fixture(old_provider, {"code-review"})
        changed = target / ".agents/skills/code-review/SKILL.md"
        changed.write_bytes(changed.read_bytes() + b"local project change\n")
        before = {path: path.read_bytes() for path in target.rglob("*") if path.is_file()}

        with mock.patch.object(
            PROVIDER_MANAGER,
            "load_declaration",
            return_value=(upgraded_provider, upgraded_skills),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(PROVIDER_MANAGER, "find_gh") as find_gh:
            with self.assertRaises(PROVIDER_MANAGER.ProviderError) as raised:
                PROVIDER_MANAGER.command_update(target, dry_run=False)

        diagnostic = str(raised.exception)
        self.assertIn("code-review was installed by the authenticated predecessor", diagnostic)
        self.assertIn("Expected predecessor SHA-256", diagnostic)
        self.assertIn("Found SHA-256", diagnostic)
        find_gh.assert_not_called()
        self.assertEqual(
            {path: path.read_bytes() for path in target.rglob("*") if path.is_file()},
            before,
        )

    def test_preexisting_provider_refuses_predecessor_replacement(self) -> None:
        target = self.base / "provider-upgrade-preexisting"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        preexisting = next(skill for skill in skills if skill["name"] == "code-review")
        write_provider_skill(target, provider, preexisting)
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)
        predecessor_manifest = self.base / "preexisting-predecessor.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(provider),
            predecessor_manifest,
        )
        upgraded_provider, upgraded_skills = provider_upgrade_fixture(provider, {"code-review"})
        before = (target / ".agents/skills/code-review/SKILL.md").read_bytes()

        with mock.patch.object(
            PROVIDER_MANAGER,
            "load_declaration",
            return_value=(upgraded_provider, upgraded_skills),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(PROVIDER_MANAGER, "find_gh") as find_gh:
            with self.assertRaisesRegex(
                PROVIDER_MANAGER.ProviderError,
                "cannot be proven framework-managed.*pre-existing-compatible",
            ):
                PROVIDER_MANAGER.command_update(target, dry_run=False)

        find_gh.assert_not_called()
        self.assertEqual(
            (target / ".agents/skills/code-review/SKILL.md").read_bytes(),
            before,
        )

    def test_deleted_predecessor_provider_directory_is_installed_from_new_baseline(self) -> None:
        target = self.base / "provider-upgrade-deleted"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)
        old_provider, _skills = PROVIDER_MANAGER.load_declaration()
        predecessor_manifest = self.base / "deleted-predecessor.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(old_provider),
            predecessor_manifest,
        )
        shutil.rmtree(target / ".agents/skills/code-review")
        upgraded_provider, upgraded_skills = provider_upgrade_fixture(old_provider, {"code-review"})

        with mock.patch.object(
            PROVIDER_MANAGER,
            "load_declaration",
            return_value=(upgraded_provider, upgraded_skills),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_upgraded_provider_install({"code-review"}),
        ):
            PROVIDER_MANAGER.command_update(target, dry_run=False)

        self.assertTrue(
            (target / ".agents/skills/code-review/SKILL.md").read_bytes().endswith(
                UPGRADED_PROVIDER_SUFFIX
            )
        )
        state = json.loads((target / "ai-workflow/provider-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["skills"]["code-review"]["origin"], "created")

    def test_provider_transition_reports_all_modified_skills_before_staging(self) -> None:
        target = self.base / "provider-upgrade-multiple-conflicts"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)
        old_provider, _skills = PROVIDER_MANAGER.load_declaration()
        predecessor_manifest = self.base / "multiple-predecessor.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(old_provider),
            predecessor_manifest,
        )
        for name in ("code-review", "implement"):
            path = target / ".agents/skills" / name / "SKILL.md"
            path.write_bytes(path.read_bytes() + f"local {name} change\n".encode("utf-8"))
        upgraded_provider, upgraded_skills = provider_upgrade_fixture(
            old_provider,
            {"code-review", "implement"},
        )

        with mock.patch.object(
            PROVIDER_MANAGER,
            "load_declaration",
            return_value=(upgraded_provider, upgraded_skills),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(PROVIDER_MANAGER, "find_gh") as find_gh:
            with self.assertRaises(PROVIDER_MANAGER.ProviderError) as raised:
                PROVIDER_MANAGER.command_update(target, dry_run=False)

        diagnostic = str(raised.exception)
        self.assertIn("provider skill code-review", diagnostic)
        self.assertIn("provider skill implement", diagnostic)
        find_gh.assert_not_called()

    def test_malformed_predecessor_provider_state_fails_closed(self) -> None:
        target = self.base / "provider-upgrade-malformed-state"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)
        old_provider, _skills = PROVIDER_MANAGER.load_declaration()
        predecessor_manifest = self.base / "malformed-state-predecessor.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(old_provider),
            predecessor_manifest,
        )
        upgraded_provider, upgraded_skills = provider_upgrade_fixture(old_provider, {"code-review"})
        state_path = target / "ai-workflow/provider-state.json"
        state_path.write_text("not json\n", encoding="utf-8")
        provider_before = {
            path.relative_to(target).as_posix(): path.read_bytes()
            for path in (target / ".agents/skills").rglob("*")
            if path.is_file()
        }

        with mock.patch.object(
            PROVIDER_MANAGER,
            "load_declaration",
            return_value=(upgraded_provider, upgraded_skills),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(PROVIDER_MANAGER, "find_gh") as find_gh:
            with self.assertRaisesRegex(
                PROVIDER_MANAGER.ProviderError,
                "cannot read provider state",
            ):
                PROVIDER_MANAGER.command_update(target, dry_run=False)

        find_gh.assert_not_called()
        self.assertEqual(state_path.read_text(encoding="utf-8"), "not json\n")
        self.assertEqual(
            {
                path.relative_to(target).as_posix(): path.read_bytes()
                for path in (target / ".agents/skills").rglob("*")
                if path.is_file()
            },
            provider_before,
        )

    def test_provider_transition_retains_unchanged_skill_and_created_origin(self) -> None:
        target = self.base / "provider-upgrade-one-skill"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)
        old_provider, _skills = PROVIDER_MANAGER.load_declaration()
        predecessor_manifest = self.base / "one-skill-predecessor.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(old_provider),
            predecessor_manifest,
        )
        upgraded_provider, upgraded_skills = provider_upgrade_fixture(
            old_provider,
            {"code-review"},
            change_identity=False,
        )
        retained = target / ".agents/skills/wayfinder/SKILL.md"
        retained_before = retained.read_bytes()

        with mock.patch.object(
            PROVIDER_MANAGER,
            "load_declaration",
            return_value=(upgraded_provider, upgraded_skills),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_upgraded_provider_install({"code-review"}),
        ):
            PROVIDER_MANAGER.command_update(target, dry_run=False)

        self.assertEqual(retained.read_bytes(), retained_before)
        state = json.loads((target / "ai-workflow/provider-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["skills"]["wayfinder"]["origin"], "created")

    def test_provider_migration_callback_failure_restores_predecessor_exactly(self) -> None:
        target = self.base / "provider-upgrade-callback-rollback"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)
        old_provider, _skills = PROVIDER_MANAGER.load_declaration()
        predecessor_manifest = self.base / "callback-predecessor.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(old_provider),
            predecessor_manifest,
        )
        upgraded_provider, upgraded_skills = provider_upgrade_fixture(old_provider, {"code-review"})
        before = {
            path.relative_to(target).as_posix(): path.read_bytes()
            for path in target.rglob("*")
            if path.is_file()
        }

        with mock.patch.object(
            PROVIDER_MANAGER,
            "load_declaration",
            return_value=(upgraded_provider, upgraded_skills),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_upgraded_provider_install({"code-review"}),
        ):
            with self.assertRaisesRegex(RuntimeError, "simulated payload failure"):
                PROVIDER_MANAGER.command_update(
                    target,
                    dry_run=False,
                    commit_callback=lambda: (_ for _ in ()).throw(
                        RuntimeError("simulated payload failure")
                    ),
                )

        self.assertEqual(
            {
                path.relative_to(target).as_posix(): path.read_bytes()
                for path in target.rglob("*")
                if path.is_file()
            },
            before,
        )
        self.assertFalse(list(target.glob(f"{PROVIDER_MANAGER.UPDATE_QUARANTINE_PREFIX}*")))

    def test_dependency_set_update_preserves_clean_preexisting_skills_and_adds_triage(self) -> None:
        target = self.base / "provider-dependency-set-upgrade"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        old_skills = [skill for skill in skills if skill["name"] != "triage"]
        for skill in old_skills:
            write_provider_skill(target, provider, skill)
        write_provider_state(target, provider, old_skills, origin="created")
        old_provider = json.loads(json.dumps(provider))
        old_provider["skills"] = json.loads(json.dumps(old_skills))
        predecessor_manifest = self.base / "dependency-set-predecessors.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(old_provider),
            predecessor_manifest,
        )
        triage = target / ".agents/skills/triage"
        state_path = target / "ai-workflow/provider-state.json"
        retained_bytes = {
            path.relative_to(target / ".agents/skills").as_posix(): path.read_bytes()
            for skill in old_skills
            for path in (target / ".agents/skills" / str(skill["name"])).rglob("*")
            if path.is_file()
        }

        with mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_update(target, dry_run=False)

        updated = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(updated["skills"]["triage"]["origin"], "created")
        self.assertTrue(triage.is_dir())
        self.assertEqual(
            {
                path.relative_to(target / ".agents/skills").as_posix(): path.read_bytes()
                for skill in old_skills
                for path in (target / ".agents/skills" / str(skill["name"])).rglob("*")
                if path.is_file()
            },
            retained_bytes,
        )
        self.assertTrue(
            all(
                record["origin"] == "created"
                for name, record in updated["skills"].items()
                if name != "triage"
            )
        )
        self.assertTrue(PROVIDER_MANAGER.command_status(target, verbose=False))

    def test_dependency_set_update_rejects_canonized_altered_preexisting_body(self) -> None:
        target = self.base / "provider-dependency-authentication"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        for skill in skills:
            write_provider_skill(target, provider, skill)
        write_provider_state(target, provider, skills)
        with mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        triage = target / ".agents/skills/triage"
        shutil.rmtree(triage)
        state_path = target / "ai-workflow/provider-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        del state["skills"]["triage"]
        old_provider = json.loads(json.dumps(provider))
        old_provider["skills"] = [
            json.loads(json.dumps(skill)) for skill in skills if skill["name"] != "triage"
        ]
        predecessor_manifest = self.base / "dependency-auth-predecessors.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(old_provider),
            predecessor_manifest,
        )
        altered_name = str(skills[0]["name"])
        altered_path = target / ".agents/skills" / altered_name / "SKILL.md"
        altered = altered_path.read_text(encoding="utf-8") + "canonized local alteration\n"
        altered_path.write_text(altered, encoding="utf-8")
        state["skills"][altered_name]["files"]["SKILL.md"] = PROVIDER_MANAGER.sha256(
            altered_path
        )
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        state_before = state_path.read_bytes()

        with mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ) as install:
            with self.assertRaisesRegex(
                PROVIDER_MANAGER.ProviderError,
                "cannot be proven to match the authenticated predecessor",
            ):
                PROVIDER_MANAGER.command_update(target, dry_run=True)

        install.assert_not_called()
        self.assertEqual(state_path.read_bytes(), state_before)
        self.assertEqual(altered_path.read_text(encoding="utf-8"), altered)
        self.assertFalse(triage.exists())
        self.assertFalse(list(target.glob(f"{PROVIDER_MANAGER.UPDATE_QUARANTINE_PREFIX}*")))

    def test_dependency_set_update_preflights_new_skill_collision_before_gh(self) -> None:
        target = self.base / "provider-dependency-collision"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        for skill in skills:
            write_provider_skill(target, provider, skill)
        with mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        state_path = target / "ai-workflow/provider-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        del state["skills"]["triage"]
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        old_provider = json.loads(json.dumps(provider))
        old_provider["skills"] = [
            json.loads(json.dumps(skill)) for skill in skills if skill["name"] != "triage"
        ]
        predecessor_manifest = self.base / "dependency-collision-predecessors.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(old_provider),
            predecessor_manifest,
        )
        (target / ".agents/skills/triage/OUT-OF-SCOPE.md").unlink()

        with mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(PROVIDER_MANAGER, "find_gh") as find_gh:
            with self.assertRaisesRegex(
                PROVIDER_MANAGER.ProviderError,
                "cannot be proven framework-managed",
            ):
                PROVIDER_MANAGER.command_update(target, dry_run=True)
        find_gh.assert_not_called()

    def test_provider_remove_rejects_state_path_injection(self) -> None:
        target = self.base / "provider-state-injection"
        target.mkdir()
        protected = target / "protected"
        protected.mkdir()
        marker = protected / "keep.txt"
        marker.write_text("project owned\n", encoding="utf-8")
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        state_path = target / "ai-workflow/provider-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        first_name = next(iter(state["skills"]))
        state["skills"]["../../protected"] = state["skills"].pop(first_name)
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(PROVIDER_MANAGER.ProviderError, "invalid record"):
            PROVIDER_MANAGER.command_remove(target, dry_run=False)
        self.assertEqual(marker.read_text(encoding="utf-8"), "project owned\n")
        self.assertTrue(state_path.is_file())

    def test_provider_update_rejects_unknown_old_state_name_before_gh(self) -> None:
        target = self.base / "provider-state-extra-name"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        project_owned = target / ".agents/skills/project-owned"
        project_owned.mkdir()
        marker = project_owned / "keep.txt"
        marker.write_text("project-owned content\n", encoding="utf-8")
        state_path = target / "ai-workflow/provider-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["skills"]["project-owned"] = {
            "files": {"keep.txt": PROVIDER_MANAGER.sha256(marker)},
            "origin": "created",
            "path": "skills/project-owned",
            "tree_sha": "3" * 40,
        }
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        state_before = state_path.read_bytes()
        provider, _skills = PROVIDER_MANAGER.load_declaration()
        predecessor_manifest = self.base / "extra-state-predecessors.json"
        write_authenticated_provider_predecessor(
            target,
            provider_declaration_document(provider),
            predecessor_manifest,
        )

        with mock.patch.object(
            PROVIDER_MANAGER,
            "SOURCE_MANIFEST_PATH",
            predecessor_manifest,
        ), mock.patch.object(PROVIDER_MANAGER, "find_gh") as find_gh:
            with self.assertRaisesRegex(
                PROVIDER_MANAGER.ProviderError,
                "provider state skill set does not match the authenticated predecessor declaration",
            ):
                PROVIDER_MANAGER.command_update(target, dry_run=False)

        find_gh.assert_not_called()
        self.assertEqual(marker.read_text(encoding="utf-8"), "project-owned content\n")
        self.assertEqual(state_path.read_bytes(), state_before)

    def test_provider_requires_authenticated_gh_before_writes(self) -> None:
        provider, _ = PROVIDER_MANAGER.load_declaration()
        responses = [
            subprocess.CompletedProcess([], 0, "gh version 2.97.0 (2026-07-31)\n", ""),
            subprocess.CompletedProcess([], 0, "--pin\n--scope\n", ""),
            subprocess.CompletedProcess([], 1, "", "not logged in"),
        ]
        with mock.patch.object(PROVIDER_MANAGER.shutil, "which", return_value="/fixture/gh"), mock.patch.object(
            PROVIDER_MANAGER.subprocess,
            "run",
            side_effect=responses,
        ):
            with self.assertRaisesRegex(PROVIDER_MANAGER.ProviderError, "gh auth login"):
                PROVIDER_MANAGER.find_gh(provider)

    def test_provider_rejects_gh_before_security_baseline(self) -> None:
        provider, _ = PROVIDER_MANAGER.load_declaration()
        response = subprocess.CompletedProcess([], 0, "gh version 2.96.0 (2026-07-15)\n", "")
        with mock.patch.object(PROVIDER_MANAGER.shutil, "which", return_value="/fixture/gh"), mock.patch.object(
            PROVIDER_MANAGER.subprocess,
            "run",
            return_value=response,
        ):
            with self.assertRaisesRegex(PROVIDER_MANAGER.ProviderError, "2.97.0 or newer"):
                PROVIDER_MANAGER.find_gh(provider)

    def test_provider_declaration_maps_capabilities_without_router_prompt_copies(self) -> None:
        provider, skills = PROVIDER_MANAGER.load_declaration()
        declaration = json.loads(
            (PACKAGE / "payload/ai-workflow/providers.json").read_text(encoding="utf-8")
        )
        self.assertEqual(provider["repository"], "mattpocock/skills")
        self.assertEqual(
            set(declaration["capabilities"]),
            {
                "planning",
                "learning",
                "research",
                "specification",
                "tickets",
                "implementation",
                "test-driven-development",
                "code-review",
            },
        )
        names = {str(skill["name"]) for skill in skills}
        self.assertTrue({"grilling", "domain-modeling", "prototype", "codebase-design"} <= names)
        policy = (PACKAGE / "payload/root/AGENTS.md.template").read_text(encoding="utf-8")
        self.assertNotIn("## The Map", policy)
        self.assertNotIn("## Rules of the loop", policy)
        self.assertNotIn("## User Stories", policy)

    def test_provider_declaration_models_triage_configuration_without_routing_it(self) -> None:
        declaration = json.loads(
            (PACKAGE / "payload/ai-workflow/providers.json").read_text(encoding="utf-8")
        )
        _, skills = PROVIDER_MANAGER.load_declaration()
        by_name = {str(skill["name"]): skill for skill in skills}

        self.assertIn("triage", by_name)
        self.assertNotIn("triage", declaration["capabilities"].values())
        self.assertEqual(
            declaration["configuration"]["triage-labels"],
            {
                "enabled_by": "triage",
                "path": "docs/agents/triage-labels.md",
                "provisioned_by": "setup-matt-pocock-skills",
            },
        )
        for consumer in ("to-spec", "to-tickets", "triage"):
            self.assertEqual(
                by_name[consumer]["requires_configuration"],
                ["domain", "issue-tracker", "triage-labels"],
            )
        self.assertEqual(
            by_name["wayfinder"]["requires_configuration"],
            ["domain", "issue-tracker"],
        )
        self.assertEqual(
            by_name["code-review"]["requires_configuration"],
            ["issue-tracker"],
        )
        self.assertEqual(
            by_name["implement"]["requires_configuration"],
            ["issue-tracker"],
        )
        self.assertEqual(
            {
                name
                for name, skill in by_name.items()
                if skill["invocation"]["codex"] == "user-only"
            },
            {
                "implement",
                "setup-matt-pocock-skills",
                "teach",
                "to-spec",
                "to-tickets",
                "triage",
                "wayfinder",
            },
        )
        self.assertTrue(
            all(skill["invocation"]["claude-code"] == "unavailable" for skill in skills)
        )

    def test_coordinated_install_preflights_provider_before_payload_writes(self) -> None:
        target = self.base / "missing-gh-target"
        target.mkdir()
        environment = os.environ.copy()
        environment["PATH"] = str(self.base / "no-executables")

        result = run(
            sys.executable,
            LIFECYCLE,
            "install",
            target,
            "--source-revision",
            REVISION,
            env=environment,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("GitHub CLI 2.97.0 or newer", result.stderr)
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertFalse((target / "CLAUDE.md").exists())
        self.assertFalse((target / ".agents").exists())
        self.assertFalse(
            (target / "ai-workflow").exists(),
            sorted(path.relative_to(target).as_posix() for path in target.rglob("*")),
        )

    def test_coordinated_update_commits_payload_inside_provider_rollback_window(self) -> None:
        target = self.base / "coordinated-update"
        target.mkdir()
        events = []

        class FakeProviderManager:
            class ProviderError(RuntimeError):
                pass

            @staticmethod
            def command_update(root, dry_run, *, commit_callback=None):
                self.assertEqual(root, target)
                self.assertFalse(dry_run)
                self.assertIsNotNone(commit_callback)
                events.append("provider-transaction-open")
                commit_callback()
                events.append("provider-transaction-commit")

        def checked(script, action, root, dry_run, revision, *, quiet=False):
            self.assertEqual(script, LIFECYCLE_MANAGER.ADOPTER)
            self.assertEqual(action, "update")
            self.assertEqual(root, target)
            self.assertEqual(revision, REVISION)
            events.append("payload-preflight" if dry_run else "payload-commit")

        with mock.patch.object(
            LIFECYCLE_MANAGER,
            "run_checked",
            side_effect=checked,
        ), mock.patch.object(
            LIFECYCLE_MANAGER,
            "load_provider_manager",
            return_value=FakeProviderManager,
        ):
            LIFECYCLE_MANAGER.update(target, dry_run=False, revision=REVISION)

        self.assertEqual(
            events,
            [
                "payload-preflight",
                "provider-transaction-open",
                "payload-commit",
                "provider-transaction-commit",
            ],
        )

    def test_coordinated_rollback_derives_seed_targets_from_manifest(self) -> None:
        manifest = json.loads(
            LIFECYCLE_MANAGER.DISTRIBUTION_MANIFEST.read_text(encoding="utf-8")
        )
        manifest["project_seeds"].append(
            {
                "source": "ai-workflow/templates/future-seed.md",
                "target": "ai-workflow/future-seed.md",
            }
        )
        manifest_path = self.base / "future-distribution-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        with mock.patch.object(
            LIFECYCLE_MANAGER,
            "DISTRIBUTION_MANIFEST",
            manifest_path,
        ):
            cleanup_targets, seed_targets = LIFECYCLE_MANAGER.payload_targets()

        future = Path("ai-workflow/future-seed.md")
        self.assertIn(future, cleanup_targets)
        self.assertIn(future, seed_targets)

    def test_coordinated_install_rolls_back_new_payload_and_seeds_on_provider_failure(self) -> None:
        target = self.base / "provider-runtime-failure"
        target.mkdir()
        preexisting_seed_parent = target / "ai-workflow/state"
        preexisting_seed_parent.mkdir(parents=True)
        original_run_checked = LIFECYCLE_MANAGER.run_checked

        def controlled_run_checked(script, action, root, dry_run, revision, *, quiet=False):
            if script == LIFECYCLE_MANAGER.PROVIDERS:
                if dry_run:
                    return None
                raise LIFECYCLE_MANAGER.LifecycleError("simulated provider network failure")
            return original_run_checked(
                script,
                action,
                root,
                dry_run,
                revision,
                quiet=quiet,
            )

        with mock.patch.object(
            LIFECYCLE_MANAGER,
            "run_checked",
            side_effect=controlled_run_checked,
        ):
            with self.assertRaisesRegex(
                LIFECYCLE_MANAGER.LifecycleError,
                "simulated provider network failure",
            ):
                LIFECYCLE_MANAGER.install(target, dry_run=False, revision=REVISION)

        self.assertFalse((target / "AGENTS.md").exists())
        self.assertFalse((target / "CLAUDE.md").exists())
        self.assertFalse((target / ".agents").exists())
        self.assertTrue(preexisting_seed_parent.is_dir())
        self.assertEqual(list(preexisting_seed_parent.iterdir()), [])

    def test_target_project_docs_are_never_supplied_or_removed(self) -> None:
        target = self.base / "documented-project"
        project_decision = target / "docs/decisions/0001-project-architecture.md"
        project_decision.parent.mkdir(parents=True)
        project_decision.write_text("# Project-owned decision\n", encoding="utf-8")

        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(project_decision.read_text(encoding="utf-8"), "# Project-owned decision\n")
        for relative in FORMER_FRAMEWORK_DOCS:
            self.assertFalse((target / relative).exists())

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(project_decision.read_text(encoding="utf-8"), "# Project-owned decision\n")

    def test_default_target_is_current_directory(self) -> None:
        target = self.base / "current-project"
        target.mkdir()
        result = run(
            sys.executable,
            ADOPT,
            "install",
            "--source-revision",
            REVISION,
            cwd=target,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "ai-workflow/install-manifest.json").is_file())

    def test_explicit_target_is_used_from_another_directory(self) -> None:
        working = self.base / "working"
        target = self.base / "explicit-project"
        working.mkdir()
        target.mkdir()
        result = run(
            sys.executable,
            ADOPT,
            "install",
            target,
            "--source-revision",
            REVISION,
            cwd=working,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "ai-workflow/install-manifest.json").is_file())
        self.assertFalse((working / "ai-workflow").exists())

    def test_install_does_not_need_git_executable(self) -> None:
        target = self.base / "no-git-project"
        target.mkdir()
        environment = os.environ.copy()
        environment["PATH"] = str(self.base / "no-executables")
        result = run(
            sys.executable,
            ADOPT,
            "install",
            target,
            "--source-revision",
            REVISION,
            env=environment,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "ai-workflow/install-manifest.json").is_file())

    def test_filesystem_root_is_rejected(self) -> None:
        root = Path(Path.cwd().anchor)
        result = adopt(ADOPT, "install", root)
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to operate on a filesystem root", result.stderr)
        with self.assertRaisesRegex(BOOTSTRAPPER.BootstrapError, "filesystem root"):
            BOOTSTRAPPER.main(
                [
                    "install",
                    str(root),
                    "--archive-url",
                    (self.base / "unused.tar.gz").as_uri(),
                    "--ref",
                    REVISION,
                ]
            )

    def test_dry_run_is_optional_and_nonmutating(self) -> None:
        target = git_repository(self.base / "target")
        result = adopt(ADOPT, "install", target, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())

    def test_fresh_policy_allows_project_owned_customization(self) -> None:
        target = git_repository(self.base / "target")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)

        policy = target / "AGENTS.md"
        initial = policy.read_bytes()
        self.assertTrue(initial.startswith(ADOPTER.MANAGED_BEGIN))
        self.assertIn(ADOPTER.MANAGED_END + ADOPTER.PROJECT_BEGIN, initial)
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["framework_files"]["AGENTS.md"]["origin"], "composite-created")

        project = b"# Project instructions\n\nRun the repository test suite before completion.\n"
        policy.write_bytes(initial + project)

        status = adopt(ADOPT, "status", target)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("clean: AGENTS.md", status.stdout)

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertTrue(policy.read_bytes().endswith(project))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["framework_files"]["AGENTS.md"]["origin"], "composite-created")

        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(policy.read_bytes(), project)

    def test_exact_preexisting_agents_survives_source_update_and_restores_original(self) -> None:
        old_package = self.base / "older-policy-package"
        shutil.copytree(PACKAGE, old_package)
        (old_package / "VERSION").write_text("0.6.9\n", encoding="utf-8")
        refreshed = run(
            sys.executable,
            old_package / "scripts/verify_package.py",
            "--refresh-manifest",
        )
        self.assertEqual(refreshed.returncode, 0, refreshed.stderr)
        source_relative = "root/AGENTS.md.template"
        source_path = old_package / "payload" / source_relative
        original = b"# Exact pre-existing policy snapshot\n\n" + source_path.read_bytes()
        source_path.write_bytes(original)
        distribution_path = old_package / "payload/distribution/manifest.json"
        distribution = json.loads(distribution_path.read_text(encoding="utf-8"))
        distribution["checksums"][source_relative] = hashlib.sha256(original).hexdigest()
        distribution_path.write_text(
            json.dumps(distribution, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        target = git_repository(self.base / "exact-preexisting-agents-project")
        policy = target / "AGENTS.md"
        policy.write_bytes(original)
        installed = adopt(old_package / "scripts/adopt.py", "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        managed, project = ADOPTER.parse_composite_policy(policy.read_bytes())
        self.assertEqual((managed, project), (original, b""))

        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        record = manifest["framework_files"]["AGENTS.md"]
        self.assertEqual(manifest["schema_version"], ADOPTER.INSTALL_MANIFEST_SCHEMA)
        self.assertEqual(record["origin"], "composite-preexisting-identical")
        self.assertEqual(
            ADOPTER.restoration_bytes(record, ADOPTER.POLICY_PATH),
            original,
        )

        project = b"\n## Agent skills\n\nLegitimate project setup suffix.\n"
        policy.write_bytes(ADOPTER.compose_policy(managed, project))
        status = adopt(old_package / "scripts/adopt.py", "status", target)
        self.assertEqual(status.returncode, 0, status.stderr)

        trusted_adopt = package_accepting_installed_fixture(
            self.base,
            target,
            "newer-policy-package",
        )
        updated = adopt(trusted_adopt, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        current_source = (PACKAGE / "payload/root/AGENTS.md.template").read_bytes()
        self.assertEqual(
            ADOPTER.parse_composite_policy(policy.read_bytes()),
            (current_source, project),
        )
        self.assertEqual(adopt(trusted_adopt, "status", target).returncode, 0)

        removed = adopt(trusted_adopt, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(policy.read_bytes(), original + project)

    def test_update_migrates_legacy_exact_preexisting_agents_with_project_suffix(self) -> None:
        target = git_repository(self.base / "legacy-exact-preexisting-agents-project")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)

        policy = target / "AGENTS.md"
        source = (PACKAGE / "payload/root/AGENTS.md.template").read_bytes()
        project = b"\n## Agent skills\n\nLegacy setup-owned suffix.\n"
        policy.write_bytes(source + project)
        digest = hashlib.sha256(source).hexdigest()
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["schema_version"] = 1
        manifest["framework_files"]["AGENTS.md"] = {
            "origin": "preexisting-identical",
            "sha256": digest,
            "source_sha256": digest,
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertEqual(
            ADOPTER.parse_composite_policy(policy.read_bytes()),
            (source, project),
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], ADOPTER.INSTALL_MANIFEST_SCHEMA)
        record = manifest["framework_files"]["AGENTS.md"]
        self.assertEqual(record["origin"], "composite-preexisting-identical")
        self.assertEqual(
            ADOPTER.restoration_bytes(record, ADOPTER.POLICY_PATH),
            source,
        )

        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(policy.read_bytes(), source + project)

    def test_install_manifest_rejects_malformed_or_unexpected_restoration_data(self) -> None:
        target = git_repository(self.base / "invalid-restoration-project")
        source = (PACKAGE / "payload/root/AGENTS.md.template").read_bytes()
        (target / "AGENTS.md").write_bytes(source)
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)

        manifest_path = target / "ai-workflow/install-manifest.json"
        original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        cases = (
            ("malformed", {"preexisting_base64": "not base64!"}, "invalid preexisting_base64"),
            ("unexpected", {"origin": "composite-created"}, "restoration data is only valid"),
        )
        for label, changes, expected in cases:
            with self.subTest(label=label):
                manifest = json.loads(json.dumps(original_manifest))
                manifest["framework_files"]["AGENTS.md"].update(changes)
                manifest_path.write_text(
                    json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                status = adopt(ADOPT, "status", target)
                self.assertEqual(status.returncode, 2)
                self.assertIn(expected, status.stderr)

    def test_fresh_claude_policy_allows_setup_owned_customization(self) -> None:
        target = git_repository(self.base / "fresh-claude-project")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)

        policy = target / "CLAUDE.md"
        managed, project = ADOPTER.parse_composite_policy(policy.read_bytes())
        self.assertEqual(managed, ADOPTER.LEGACY_CREATED_CLAUDE_POLICY)
        self.assertEqual(project, b"")

        setup_content = b"## Agent skills\n\nProject-owned setup configuration.\n"
        policy.write_bytes(ADOPTER.compose_policy(managed, setup_content))

        status = adopt(ADOPT, "status", target)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("clean: CLAUDE.md", status.stdout)

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertEqual(ADOPTER.parse_composite_policy(policy.read_bytes()), (managed, setup_content))
        manifest = json.loads(
            (target / "ai-workflow/install-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["framework_files"]["CLAUDE.md"]["origin"], "composite-created")

        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(policy.read_bytes(), setup_content)

    def test_exact_preexisting_claude_policy_allows_setup_edit_and_is_restored(self) -> None:
        target = git_repository(self.base / "exact-preexisting-claude-project")
        policy = target / "CLAUDE.md"
        policy.write_bytes(ADOPTER.LEGACY_CREATED_CLAUDE_POLICY)

        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        managed, project = ADOPTER.parse_composite_policy(policy.read_bytes())
        self.assertEqual(managed, ADOPTER.LEGACY_CREATED_CLAUDE_POLICY)
        self.assertEqual(project, b"")
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["framework_files"]["CLAUDE.md"]["origin"],
            "composite-preexisting-identical",
        )
        manifest["schema_version"] = 1
        manifest["framework_files"]["CLAUDE.md"].pop("preexisting_base64")
        manifest["framework_files"]["CLAUDE.md"].pop("preexisting_sha256")
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        setup_content = b"\n## Agent skills\n\nExact pre-existing policy setup content.\n"
        policy.write_bytes(ADOPTER.compose_policy(managed, setup_content))
        self.assertEqual(adopt(ADOPT, "status", target).returncode, 0)
        self.assertEqual(adopt(ADOPT, "update", target).returncode, 0)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], ADOPTER.INSTALL_MANIFEST_SCHEMA)
        self.assertEqual(
            ADOPTER.restoration_bytes(
                manifest["framework_files"]["CLAUDE.md"],
                ADOPTER.CLAUDE_POLICY_PATH,
            ),
            ADOPTER.LEGACY_CREATED_CLAUDE_POLICY,
        )

        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(
            policy.read_bytes(),
            ADOPTER.LEGACY_CREATED_CLAUDE_POLICY + setup_content,
        )

    def test_update_migrates_setup_edited_legacy_created_claude_policy(self) -> None:
        target = git_repository(self.base / "legacy-created-claude-project")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)

        setup_content = b"\n## Agent skills\n\nPreserve this setup-owned content.\n"
        legacy_policy = ADOPTER.LEGACY_CREATED_CLAUDE_POLICY
        policy = target / "CLAUDE.md"
        policy.write_bytes(legacy_policy + setup_content)
        digest = hashlib.sha256(legacy_policy).hexdigest()
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["framework_files"]["CLAUDE.md"] = {
            "origin": "created",
            "sha256": digest,
            "source_sha256": digest,
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertEqual(
            ADOPTER.parse_composite_policy(policy.read_bytes()),
            (legacy_policy, setup_content),
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["framework_files"]["CLAUDE.md"]["origin"], "composite-created")
        self.assertEqual(adopt(ADOPT, "status", target).returncode, 0)

        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(policy.read_bytes(), setup_content)

    def test_update_migrates_setup_edited_legacy_preexisting_identical_claude_policy(self) -> None:
        target = git_repository(self.base / "legacy-preexisting-identical-claude-project")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)

        setup_content = b"\n## Agent skills\n\nPreserve pre-existing setup content.\n"
        legacy_policy = ADOPTER.LEGACY_CREATED_CLAUDE_POLICY
        policy = target / "CLAUDE.md"
        policy.write_bytes(legacy_policy + setup_content)
        digest = hashlib.sha256(legacy_policy).hexdigest()
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["framework_files"]["CLAUDE.md"] = {
            "origin": "preexisting-identical",
            "sha256": digest,
            "source_sha256": digest,
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertEqual(
            ADOPTER.parse_composite_policy(policy.read_bytes()),
            (legacy_policy, setup_content),
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["framework_files"]["CLAUDE.md"]["origin"],
            "composite-preexisting-identical",
        )
        self.assertEqual(adopt(ADOPT, "status", target).returncode, 0)

        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(policy.read_bytes(), legacy_policy + setup_content)

    def test_remove_deletes_untouched_framework_created_policy(self) -> None:
        target = git_repository(self.base / "target")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertTrue((target / "AGENTS.md").is_file())

        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse((target / "AGENTS.md").exists())

    def test_preexisting_empty_policy_is_preserved_on_remove(self) -> None:
        target = git_repository(self.base / "target")
        policy = target / "AGENTS.md"
        policy.write_bytes(b"")

        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertTrue(policy.is_file())
        self.assertEqual(policy.read_bytes(), b"")

    def test_update_migrates_clean_legacy_created_policy_to_composite(self) -> None:
        target = git_repository(self.base / "target")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)

        policy = target / "AGENTS.md"
        source = (PACKAGE / "payload/root/AGENTS.md.template").read_bytes()
        policy.write_bytes(source)
        digest = hashlib.sha256(source).hexdigest()
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["framework_files"]["AGENTS.md"] = {
            "origin": "created",
            "sha256": digest,
            "source_sha256": digest,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertTrue(policy.read_bytes().startswith(ADOPTER.MANAGED_BEGIN))
        self.assertIn(ADOPTER.MANAGED_END + ADOPTER.PROJECT_BEGIN, policy.read_bytes())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["framework_files"]["AGENTS.md"]["origin"], "composite-created")

    def test_existing_policy_is_preserved_through_install_and_remove(self) -> None:
        target = git_repository(self.base / "target")
        original = b"# Project policy\n\nKeep this exact content.\n"
        (target / "AGENTS.md").write_bytes(original)
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        composite = (target / "AGENTS.md").read_bytes()
        self.assertIn(original, composite)
        profile = target / "ai-workflow/project-profile.md"
        profile.write_text("project-owned customization\n", encoding="utf-8")
        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual((target / "AGENTS.md").read_bytes(), original)
        self.assertEqual(profile.read_text(encoding="utf-8"), "project-owned customization\n")
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())

    def test_existing_claude_policy_is_preserved_through_install_update_and_remove(self) -> None:
        target = git_repository(self.base / "target")
        original = b"# Claude-specific policy\n\nKeep this exact content.\n"
        (target / "CLAUDE.md").write_bytes(original)

        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        composite = (target / "CLAUDE.md").read_bytes()
        self.assertIn(b"@AGENTS.md\n", composite)
        self.assertIn(original, composite)

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertEqual((target / "CLAUDE.md").read_bytes(), composite)

        removed = adopt(ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual((target / "CLAUDE.md").read_bytes(), original)

    def test_update_adds_claude_import_to_an_older_installation(self) -> None:
        old_package = self.base / "pre-claude-package"
        shutil.copytree(PACKAGE, old_package)
        (old_package / "VERSION").write_text("0.4.1\n", encoding="utf-8")
        refreshed = run(sys.executable, old_package / "scripts/verify_package.py", "--refresh-manifest")
        self.assertEqual(refreshed.returncode, 0, refreshed.stderr)

        claude_source = "root/CLAUDE.md.template"
        (old_package / "payload" / claude_source).unlink()
        manifest_path = old_package / "payload/distribution/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["framework_owned"] = [
            item for item in manifest["framework_owned"] if item["source"] != claude_source
        ]
        del manifest["checksums"][claude_source]
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        target = git_repository(self.base / "target")
        original = b"# Existing Claude policy\n"
        (target / "CLAUDE.md").write_bytes(original)
        installed = adopt(old_package / "scripts/adopt.py", "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual((target / "CLAUDE.md").read_bytes(), original)

        trusted_adopt = package_accepting_installed_fixture(
            self.base,
            target,
            "post-claude-package",
        )
        updated = adopt(trusted_adopt, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        composite = (target / "CLAUDE.md").read_bytes()
        self.assertIn(b"@AGENTS.md\n", composite)
        self.assertIn(original, composite)

        removed = adopt(trusted_adopt, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual((target / "CLAUDE.md").read_bytes(), original)

    def test_conflict_fails_before_writes(self) -> None:
        target = git_repository(self.base / "target")
        conflict = target / ".agents/skills/workflow-discovery/SKILL.md"
        conflict.parent.mkdir(parents=True)
        conflict.write_text("project owned\n", encoding="utf-8")
        result = adopt(ADOPT, "install", target)
        self.assertEqual(result.returncode, 2)
        self.assertIn("would overwrite existing framework path", result.stderr)
        self.assertEqual(conflict.read_text(encoding="utf-8"), "project owned\n")
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())

    def test_reserved_composite_marker_fails_install_before_writes(self) -> None:
        target = git_repository(self.base / "reserved-policy-marker")
        policy = target / "AGENTS.md"
        original = b"# Project policy\n" + ADOPTER.MANAGED_END + ADOPTER.PROJECT_BEGIN
        policy.write_bytes(original)

        installed = adopt(ADOPT, "install", target)

        self.assertEqual(installed.returncode, 2)
        self.assertIn("reserved ai-workflow composite marker", installed.stderr)
        self.assertEqual(policy.read_bytes(), original)
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())
        self.assertFalse((target / ".agents").exists())

    def test_reserved_project_marker_is_unhealthy_and_blocks_update(self) -> None:
        target = git_repository(self.base / "reserved-project-marker")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        policy = target / "AGENTS.md"
        policy.write_bytes(policy.read_bytes() + ADOPTER.MANAGED_BEGIN)
        modified = policy.read_bytes()

        status = adopt(ADOPT, "status", target)
        update = adopt(ADOPT, "update", target)

        self.assertEqual(status.returncode, 1, status.stderr)
        self.assertIn("modified: AGENTS.md", status.stdout)
        self.assertEqual(update.returncode, 2)
        self.assertIn("reserved ai-workflow composite marker", update.stderr)
        self.assertEqual(policy.read_bytes(), modified)

    def test_payload_install_postcheck_failure_rolls_back_every_write(self) -> None:
        target = git_repository(self.base / "install-postcheck-rollback").resolve()
        policy = target / "AGENTS.md"
        original = b"# Existing project policy\n"
        policy.write_bytes(original)

        with mock.patch.object(ADOPTER, "command_status", return_value=False):
            with self.assertRaisesRegex(ADOPTER.AdoptionError, "post-install verification failed"):
                ADOPTER.command_install(target, False, REVISION)

        self.assertEqual(policy.read_bytes(), original)
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())
        self.assertFalse((target / ".agents").exists())

    def test_payload_write_failure_removes_only_transaction_created_parents(self) -> None:
        target = git_repository(self.base / "write-parent-rollback").resolve()
        destination = target / "created/by-transaction/file.txt"

        def fail_after_parent_creation(path: Path, _data: bytes, _mode: int) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            raise OSError("simulated atomic write failure")

        with mock.patch.object(ADOPTER, "atomic_write", side_effect=fail_after_parent_creation):
            with self.assertRaisesRegex(ADOPTER.AdoptionError, "changes were rolled back"):
                ADOPTER.apply_transaction(
                    target,
                    [("created/by-transaction/file.txt", b"content")],
                    (),
                )

        self.assertFalse(destination.exists())
        self.assertFalse((target / "created").exists())

    def test_payload_update_postcheck_failure_restores_manifest_and_files(self) -> None:
        target = git_repository(self.base / "update-postcheck-rollback").resolve()
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        manifest_path = target / "ai-workflow/install-manifest.json"
        policy = target / "AGENTS.md"
        before_manifest = manifest_path.read_bytes()
        before_policy = policy.read_bytes()
        missing = target / ".agents/skills/workflow-debugging/SKILL.md"
        missing.unlink()
        preexisting_empty_parent = missing.parent
        self.assertTrue(preexisting_empty_parent.is_dir())

        with mock.patch.object(ADOPTER, "command_status", return_value=False):
            with self.assertRaisesRegex(ADOPTER.AdoptionError, "post-update verification failed"):
                ADOPTER.command_update(target, False, REVISION)

        self.assertEqual(manifest_path.read_bytes(), before_manifest)
        self.assertEqual(policy.read_bytes(), before_policy)
        self.assertFalse(missing.exists())
        self.assertTrue(preexisting_empty_parent.is_dir())

    def test_remove_preserves_preexisting_empty_parent_directories(self) -> None:
        target = git_repository(self.base / "preexisting-empty-parent")
        preexisting = target / ".agents/skills/workflow-debugging"
        preexisting.mkdir(parents=True)

        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        removed = adopt(ADOPT, "remove", target)

        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertTrue(preexisting.is_dir())
        self.assertFalse((preexisting / "SKILL.md").exists())

    def test_reinstallation_is_idempotent(self) -> None:
        target = git_repository(self.base / "target")
        first = adopt(ADOPT, "install", target)
        self.assertEqual(first.returncode, 0, first.stderr)
        manifest = (target / "ai-workflow/install-manifest.json").read_bytes()
        second = adopt(ADOPT, "install", target)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("already installed and verified", second.stdout)
        self.assertEqual((target / "ai-workflow/install-manifest.json").read_bytes(), manifest)

    def test_accepted_predecessor_requires_immutable_git_revision(self) -> None:
        manifest = json.loads(ADOPTER.SOURCE_MANIFEST.read_text(encoding="utf-8"))
        manifest["accepted_predecessors"][0]["source_revisions"] = [
            ADOPTER.LOCAL_SOURCE_REVISION
        ]
        manifest_path = self.base / "sentinel-predecessor-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        with mock.patch.object(ADOPTER, "SOURCE_MANIFEST", manifest_path):
            with self.assertRaisesRegex(
                ADOPTER.AdoptionError,
                "accepted predecessor source_revisions are malformed",
            ):
                ADOPTER.load_source_manifest()

    def test_tamper_is_reported_and_blocks_update(self) -> None:
        target = git_repository(self.base / "target")
        self.assertEqual(adopt(ADOPT, "install", target).returncode, 0)
        skill = target / ".agents/skills/workflow-discovery/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nlocal change\n", encoding="utf-8")
        self.assertEqual(adopt(ADOPT, "status", target).returncode, 1)
        update = adopt(ADOPT, "update", target)
        self.assertEqual(update.returncode, 2)
        self.assertIn("locally changed framework file", update.stderr)

    def test_forged_current_source_identity_cannot_authorize_overwrite(self) -> None:
        target = git_repository(self.base / "forged-current-source")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        relative = ".agents/skills/workflow-discovery/SKILL.md"
        path = target / relative
        forged = b"project-authored bytes\n"
        path.write_bytes(forged)
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        digest = hashlib.sha256(forged).hexdigest()
        manifest["framework_files"][relative].update(
            {"sha256": digest, "source_sha256": digest, "origin": "created"}
        )
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        forged_manifest = manifest_path.read_bytes()

        updated = adopt(ADOPT, "update", target)

        self.assertEqual(updated.returncode, 2)
        self.assertIn("package-authenticated baseline", updated.stderr)
        self.assertEqual(path.read_bytes(), forged)
        self.assertEqual(manifest_path.read_bytes(), forged_manifest)

    def test_omitted_predecessor_record_blocks_dry_run_and_update_without_mutation(self) -> None:
        target = git_repository(self.base / "omitted-predecessor-record")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        manifest_path = target / "ai-workflow/install-manifest.json"
        policy = target / "AGENTS.md"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["framework_files"]["AGENTS.md"]
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        forged_manifest = manifest_path.read_bytes()
        original_policy = policy.read_bytes()

        for extra in (("--dry-run",), ()):
            with self.subTest(extra=extra):
                updated = adopt(ADOPT, "update", target, *extra)
                self.assertEqual(updated.returncode, 2)
                self.assertIn("package-authenticated baseline", updated.stderr)
                self.assertEqual(policy.read_bytes(), original_policy)
                self.assertEqual(manifest_path.read_bytes(), forged_manifest)

    def test_forged_retired_record_cannot_authorize_deletion(self) -> None:
        target = git_repository(self.base / "forged-retired-record")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        relative = "docs/routing.md"
        retired = target / relative
        retired.parent.mkdir(parents=True)
        retired.write_bytes(b"project routing\n")
        digest = hashlib.sha256(retired.read_bytes()).hexdigest()
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["framework_files"][relative] = {
            "origin": "created",
            "sha256": digest,
            "source_sha256": digest,
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        forged_manifest = manifest_path.read_bytes()

        updated = adopt(ADOPT, "update", target)

        self.assertEqual(updated.returncode, 2)
        self.assertIn("package-authenticated baseline", updated.stderr)
        self.assertEqual(retired.read_bytes(), b"project routing\n")
        self.assertEqual(manifest_path.read_bytes(), forged_manifest)

    def test_forged_policy_restoration_cannot_authorize_overwrite(self) -> None:
        target = git_repository(self.base / "forged-policy-restoration")
        source = (PACKAGE / "payload/root/AGENTS.md.template").read_bytes()
        policy = target / "AGENTS.md"
        policy.write_bytes(source)
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        forged = b"attacker-selected restoration\n"
        record = manifest["framework_files"]["AGENTS.md"]
        record["preexisting_base64"] = base64.b64encode(forged).decode("ascii")
        record["preexisting_sha256"] = hashlib.sha256(forged).hexdigest()
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        forged_manifest = manifest_path.read_bytes()
        composite = policy.read_bytes()

        for action in ("status", "update", "remove"):
            with self.subTest(action=action):
                result = adopt(ADOPT, action, target)
                self.assertEqual(result.returncode, 2)
                self.assertIn("restoration identity is not package-authenticated", result.stderr)
                self.assertEqual(policy.read_bytes(), composite)
                self.assertEqual(manifest_path.read_bytes(), forged_manifest)

    def test_installation_manifest_cannot_hide_file_tampering(self) -> None:
        target = git_repository(self.base / "target")
        self.assertEqual(adopt(ADOPT, "install", target).returncode, 0)
        relative = ".agents/skills/workflow-discovery/SKILL.md"
        skill = target / relative
        skill.write_text(skill.read_text(encoding="utf-8") + "\nlocal change\n", encoding="utf-8")
        digest = hashlib.sha256(skill.read_bytes()).hexdigest()
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["framework_files"][relative]["sha256"] = digest
        manifest["framework_files"][relative]["source_sha256"] = digest
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status = adopt(ADOPT, "status", target)
        self.assertEqual(status.returncode, 2)
        self.assertIn("source checksum was changed", status.stderr)

    def test_malformed_recorded_revision_cannot_fall_back_to_main(self) -> None:
        target = self.base / "malformed-revision"
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest_path.parent.mkdir(parents=True)
        for malformed in (None, "", "main", "1" * 39, "A" * 40):
            with self.subTest(malformed=malformed):
                manifest_path.write_text(
                    json.dumps({"source_revision": malformed}) + "\n",
                    encoding="utf-8",
                )
                with mock.patch.object(BOOTSTRAPPER, "resolve_revision") as fallback:
                    with self.assertRaisesRegex(
                        BOOTSTRAPPER.BootstrapError,
                        "installed source_revision is missing or invalid",
                    ):
                        BOOTSTRAPPER.select_source("status", target, "main", None)
                fallback.assert_not_called()

        manifest_path.write_text("not-json\n", encoding="utf-8")
        with self.assertRaisesRegex(BOOTSTRAPPER.BootstrapError, "cannot read installed source revision"):
            BOOTSTRAPPER.select_source("status", target, "main", None)

        manifest_path.write_text(
            json.dumps({"source_revision": BOOTSTRAPPER.LOCAL_SOURCE_REVISION}) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            BOOTSTRAPPER.BootstrapError,
            "records an unreleased local package",
        ):
            BOOTSTRAPPER.select_source("remove", target, "main", None)

    def test_repository_rename_preserves_installed_revision_lookup(self) -> None:
        target = self.base / "pre-rename-revision"
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest_path.parent.mkdir(parents=True)
        pre_rename_revision = "f1fda30e5d9e7740bf6ddcc32ab0c3df1262a037"
        manifest_path.write_text(
            json.dumps({"source_revision": pre_rename_revision}) + "\n",
            encoding="utf-8",
        )

        revision, archive_url = BOOTSTRAPPER.select_source(
            "status",
            target,
            "main",
            None,
        )

        self.assertEqual(revision, pre_rename_revision)
        self.assertEqual(
            archive_url,
            "https://codeload.github.com/jimmfan/agentic-workflow/tar.gz/"
            + pre_rename_revision,
        )

    def test_bootstrap_rejects_symlinked_revision_manifest_components(self) -> None:
        target = self.base / "bootstrap-symlink-target"
        target.mkdir()
        target = target.resolve()
        for linked_path in (
            target / "ai-workflow",
            target / "ai-workflow/install-manifest.json",
        ):
            with self.subTest(linked_path=linked_path), mock.patch.object(
                BOOTSTRAPPER.Path,
                "is_symlink",
                autospec=True,
                side_effect=lambda candidate, linked=linked_path: candidate == linked,
            ), mock.patch.object(BOOTSTRAPPER, "resolve_revision") as resolver, mock.patch.object(
                BOOTSTRAPPER,
                "request_bytes",
            ) as download:
                with self.assertRaisesRegex(
                    BOOTSTRAPPER.BootstrapError,
                    "refusing to follow target symlink",
                ):
                    BOOTSTRAPPER.main(["status", str(target)])
                resolver.assert_not_called()
                download.assert_not_called()

    def test_status_and_remove_bind_to_the_installed_source_revision(self) -> None:
        target = git_repository(self.base / "revision-binding")
        installed = adopt(ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        manifest_path = target / "ai-workflow/install-manifest.json"
        manifest_before = manifest_path.read_bytes()
        different_revision = "2" * 40

        for action in ("status", "remove"):
            with self.subTest(action=action):
                result = run(
                    sys.executable,
                    ADOPT,
                    action,
                    target,
                    "--source-revision",
                    different_revision,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("does not match installed", result.stderr)
                self.assertEqual(manifest_path.read_bytes(), manifest_before)

        valid_status = adopt(ADOPT, "status", target)
        self.assertEqual(valid_status.returncode, 0, valid_status.stderr)

        updated = run(
            sys.executable,
            ADOPT,
            "update",
            target,
            "--source-revision",
            different_revision,
        )
        self.assertEqual(updated.returncode, 0, updated.stderr)
        rebound = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(rebound["source_revision"], different_revision)
        rebound_status = run(
            sys.executable,
            ADOPT,
            "status",
            target,
            "--source-revision",
            different_revision,
        )
        self.assertEqual(rebound_status.returncode, 0, rebound_status.stderr)
        for action in ("status", "remove"):
            with self.subTest(stale_action=action):
                stale_package = adopt(ADOPT, action, target)
                self.assertEqual(stale_package.returncode, 2)
                self.assertIn("does not match installed", stale_package.stderr)
                self.assertTrue(manifest_path.exists())

        malformed = json.loads(manifest_path.read_text(encoding="utf-8"))
        malformed["source_revision"] = "main"
        manifest_path.write_text(json.dumps(malformed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        rejected = adopt(ADOPT, "remove", target)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("source_revision must be", rejected.stderr)
        self.assertTrue(manifest_path.exists())

    def test_unreleased_local_package_revision_supports_direct_lifecycle(self) -> None:
        target = git_repository(self.base / "local-revision")
        installed = run(sys.executable, ADOPT, "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        status = run(sys.executable, ADOPT, "status", target)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("source revision: unreleased-local-package", status.stdout)
        removed = run(sys.executable, ADOPT, "remove", target)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse((target / "ai-workflow/install-manifest.json").exists())

    def test_update_preserves_project_owned_content_and_removes_allowlisted_retirement(self) -> None:
        old_package = self.base / "old-package"
        shutil.copytree(PACKAGE, old_package)
        (old_package / "VERSION").write_text("0.3.0\n", encoding="utf-8")
        refreshed = run(sys.executable, old_package / "scripts/verify_package.py", "--refresh-manifest")
        self.assertEqual(refreshed.returncode, 0, refreshed.stderr)

        manifest_path = old_package / "payload/distribution/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        retired_source = manifest["retired_framework_owned"][-1]
        legacy = old_package / "payload" / retired_source
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text("legacy framework file\n", encoding="utf-8")
        manifest["retired_framework_owned"].remove(retired_source)
        manifest["framework_owned"].append({"source": retired_source, "target": retired_source})
        manifest["framework_owned"].sort(key=lambda item: item["source"])
        manifest["checksums"][retired_source] = hashlib.sha256(legacy.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        target = git_repository(self.base / "target")
        old_install = adopt(old_package / "scripts/adopt.py", "install", target)
        self.assertEqual(old_install.returncode, 0, old_install.stderr)
        profile = target / "ai-workflow/project-profile.md"
        profile.write_text("custom project profile\n", encoding="utf-8")
        trusted_adopt = package_accepting_installed_fixture(
            self.base,
            target,
            "retirement-new-package",
        )
        updated = adopt(trusted_adopt, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertEqual(profile.read_text(encoding="utf-8"), "custom project profile\n")
        self.assertFalse((target / retired_source).exists())

    def test_update_removes_all_unchanged_framework_docs_from_legacy_install(self) -> None:
        old_package = self.base / "legacy-docs-package"
        shutil.copytree(PACKAGE, old_package)
        (old_package / "VERSION").write_text("0.4.0\n", encoding="utf-8")
        refreshed = run(sys.executable, old_package / "scripts/verify_package.py", "--refresh-manifest")
        self.assertEqual(refreshed.returncode, 0, refreshed.stderr)

        manifest_path = old_package / "payload/distribution/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for relative in FORMER_FRAMEWORK_DOCS:
            destination = old_package / "payload" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(f"# Legacy framework documentation\n\n{relative}\n", encoding="utf-8")
            manifest["retired_framework_owned"].remove(relative)
            manifest["framework_owned"].append({"source": relative, "target": relative})
            manifest["checksums"][relative] = hashlib.sha256(destination.read_bytes()).hexdigest()
        manifest["framework_owned"].sort(key=lambda item: item["source"])
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        target = self.base / "legacy-target"
        target.mkdir()
        old_install = adopt(old_package / "scripts/adopt.py", "install", target)
        self.assertEqual(old_install.returncode, 0, old_install.stderr)
        for relative in FORMER_FRAMEWORK_DOCS:
            self.assertTrue((target / relative).is_file())

        trusted_adopt = package_accepting_installed_fixture(
            self.base,
            target,
            "legacy-docs-new-package",
        )
        updated = adopt(trusted_adopt, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertTrue((target / "docs").is_dir())
        for relative in FORMER_FRAMEWORK_DOCS:
            self.assertFalse((target / relative).exists())

    def test_update_retires_replaced_local_workflows_and_templates(self) -> None:
        old_package = self.base / "pre-provider-package"
        shutil.copytree(PACKAGE, old_package)
        (old_package / "VERSION").write_text("0.4.9\n", encoding="utf-8")
        refreshed = run(sys.executable, old_package / "scripts/verify_package.py", "--refresh-manifest")
        self.assertEqual(refreshed.returncode, 0, refreshed.stderr)

        legacy_mappings = (
            (
                "skills/workflow-decomposition/SKILL.md",
                ".agents/skills/workflow-decomposition/SKILL.md",
            ),
            ("skills/workflow-review/SKILL.md", ".agents/skills/workflow-review/SKILL.md"),
            ("skills/workflow-teach/SKILL.md", ".agents/skills/workflow-teach/SKILL.md"),
            ("ai-workflow/templates/learning-record.md", "ai-workflow/templates/learning-record.md"),
            ("ai-workflow/templates/ticket-record.md", "ai-workflow/templates/ticket-record.md"),
        )
        manifest_path = old_package / "payload/distribution/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for source, target_path in legacy_mappings:
            source_path = old_package / "payload" / source
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(f"legacy framework content for {target_path}\n", encoding="utf-8")
            manifest["retired_framework_owned"].remove(target_path)
            manifest["framework_owned"].append({"source": source, "target": target_path})
            manifest["checksums"][source] = hashlib.sha256(source_path.read_bytes()).hexdigest()
        manifest["framework_owned"].sort(key=lambda item: item["source"])
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        target = self.base / "pre-provider-target"
        target.mkdir()
        installed = adopt(old_package / "scripts/adopt.py", "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        for _source, target_path in legacy_mappings:
            self.assertTrue((target / target_path).is_file())

        trusted_adopt = package_accepting_installed_fixture(
            self.base,
            target,
            "pre-provider-new-package",
        )
        updated = adopt(trusted_adopt, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        for _source, target_path in legacy_mappings:
            self.assertFalse((target / target_path).exists())

    def test_package_version_and_checksum_drift_are_detected(self) -> None:
        copied = self.base / "package"
        shutil.copytree(PACKAGE, copied)
        (copied / "payload/VERSION").write_text("9.9.9\n", encoding="utf-8")
        mismatch = run(sys.executable, copied / "scripts/verify_package.py")
        self.assertEqual(mismatch.returncode, 1)
        self.assertIn("payload VERSION", mismatch.stderr)

        shutil.rmtree(copied)
        shutil.copytree(PACKAGE, copied)
        policy = copied / "payload/root/AGENTS.md.template"
        policy.write_text(policy.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
        checksum = run(sys.executable, copied / "scripts/verify_package.py")
        self.assertEqual(checksum.returncode, 1)
        self.assertIn("manifest/version/checksums drifted", checksum.stderr)

        shutil.rmtree(copied)
        shutil.copytree(PACKAGE, copied)
        declaration_path = copied / "payload/ai-workflow/providers.json"
        declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
        declaration["provider"]["skills"][0]["source_sha256"]["SKILL.md"] = "a" * 64
        declaration_path.write_text(
            json.dumps(declaration, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        refreshed = run(
            sys.executable,
            copied / "scripts/verify_package.py",
            "--refresh-manifest",
        )
        self.assertEqual(refreshed.returncode, 1)
        self.assertIn("reviewed pinned identity lock", refreshed.stderr)

    def test_documented_prerequisite_version_drift_is_detected(self) -> None:
        copied_root = self.base / "prerequisite-contract"
        copied_package = copied_root / "skills/agentic-workflow"
        copied_payload = copied_package / "payload"
        (copied_payload / "ai-workflow").mkdir(parents=True)
        (copied_root / "docs").mkdir()
        shutil.copy2(PACKAGE.parent.parent / "README.md", copied_root / "README.md")
        shutil.copy2(PACKAGE / "SKILL.md", copied_package / "SKILL.md")
        shutil.copy2(
            PACKAGE / "payload/ai-workflow/README.md",
            copied_payload / "ai-workflow/README.md",
        )
        shutil.copy2(
            PACKAGE / "payload/ai-workflow/providers.json",
            copied_payload / "ai-workflow/providers.json",
        )
        shutil.copy2(
            PACKAGE.parent.parent / "docs/verification.md",
            copied_root / "docs/verification.md",
        )

        readme = copied_root / "README.md"
        original = readme.read_text(encoding="utf-8")
        with mock.patch.multiple(
            VERIFIER,
            PACKAGE_ROOT=copied_package,
            PAYLOAD_ROOT=copied_payload,
            PROVIDERS_PATH=copied_payload / "ai-workflow/providers.json",
        ):
            readme.write_text(
                original.replace("Python 3.11+", "Python 3.10+", 1),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                VERIFIER.VerificationError,
                "documented Python minimum drifted",
            ):
                VERIFIER.check_prerequisite_documentation_contract()

            readme.write_text(
                original.replace("GitHub CLI 2.97.0", "GitHub CLI 2.96.0", 1),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                VERIFIER.VerificationError,
                "documented GitHub CLI minimum drifted",
            ):
                VERIFIER.check_prerequisite_documentation_contract()

    def test_route_observability_contract_is_centralized_and_compact(self) -> None:
        policy = (PACKAGE / "payload/root/AGENTS.md.template").read_text(encoding="utf-8")
        start = policy.index("Append `[route: router → …]`")
        route_instruction = policy[start : policy.index("\n\n", start)]
        compact_instruction = " ".join(route_instruction.split())
        self.assertLessEqual(len(route_instruction.encode("utf-8")), 300)
        self.assertLessEqual(len(compact_instruction.split()), 40)
        self.assertIn("router-visible execution", compact_instruction)
        self.assertIn("Explain routing only when requested", compact_instruction)
        self.assertIn("never reassess it", compact_instruction)
        self.assertIn("load skills, run workflows, or write state to produce", compact_instruction)
        for skill in (PACKAGE / "payload/skills").glob("*/SKILL.md"):
            self.assertNotIn("[route: router", skill.read_text(encoding="utf-8"))

        route_scenarios = json.loads(
            (PACKAGE / "tests/route-observability-scenarios.json").read_text(encoding="utf-8")
        )
        outputs = {item["id"]: item["expected_route_output"] for item in route_scenarios}
        self.assertEqual(outputs["direct"], "[route: router → direct]")
        self.assertEqual(
            outputs["wayfinder-handoff"],
            "[route: router → wayfinder-handoff]",
        )
        self.assertEqual(
            outputs["wayfinder-research-handoff"],
            "[route: router → wayfinder-handoff]",
        )
        self.assertEqual(
            outputs["wayfinder-research"],
            "[route: router → wayfinder → research]",
        )
        self.assertEqual(outputs["standalone-research"], "[route: router → research]")
        self.assertEqual(
            outputs["standalone-tdd"],
            "[route: router → tdd → verification]",
        )
        self.assertEqual(outputs["debugging"], "[route: router → debugging]")
        self.assertEqual(
            outputs["implementation-executed"],
            "[route: router → implement → verification]",
        )
        self.assertEqual(
            outputs["setup-handoff"],
            "[route: router → setup-matt-pocock-skills-handoff]",
        )
        self.assertEqual(
            outputs["limited-host-unavailable"],
            "[route: router → research-unavailable]",
        )
        self.assertEqual(
            outputs["provider-integrity-error"],
            "[route: router → wayfinder-blocked]",
        )
        self.assertEqual(
            outputs["active-state-conflict"],
            "[route: router → discovery-blocked]",
        )
        self.assertEqual(outputs["no-trigger"], "[route: router → direct]")

        decisions = json.loads(
            (PACKAGE / "tests/decision-contract-scenarios.json").read_text(encoding="utf-8")
        )
        by_category = {item["category"]: item for item in decisions}
        required_categories = {
            "direct-with-missing-setup",
            "wayfinder-handoff",
            "workflow-plus-capability",
            "standalone-research",
            "standalone-debugging",
            "standalone-teach-handoff",
            "setup-required-handoff",
            "implementation-handoff",
            "read-only-discovery",
            "scoped-external-read",
            "external-mutation-denied",
            "active-state-conflict",
            "canonical-artifact-ownership",
            "limited-host-local-unavailable",
        }
        self.assertLessEqual(required_categories, set(by_category))
        self.assertEqual(
            by_category["workflow-plus-capability"]["capabilities"],
            ["research"],
        )
        self.assertEqual(
            by_category["workflow-plus-capability"]["dominant_activity"],
            "wayfinder",
        )
        self.assertEqual(
            by_category["workflow-plus-capability"]["provider_invocations"],
            [
                {
                    "name": "wayfinder",
                    "policy": "user-only",
                    "invocation": "explicit",
                    "executed": True,
                },
                {
                    "name": "research",
                    "policy": "implicit",
                    "invocation": "implicit",
                    "executed": True,
                },
            ],
        )
        self.assertEqual(
            by_category["standalone-research"]["provider_invocations"],
            [
                {
                    "name": "research",
                    "policy": "implicit",
                    "invocation": "explicit",
                    "executed": True,
                }
            ],
        )
        for category in (
            "wayfinder-handoff",
            "standalone-teach-handoff",
            "setup-required-handoff",
            "implementation-handoff",
        ):
            self.assertEqual(by_category[category]["route_result"], "user-only-handoff")
            self.assertFalse(by_category[category]["executed"])
            self.assertEqual(by_category[category]["repository_state_effect"], "none")
        self.assertEqual(
            by_category["canonical-artifact-ownership"]["provider_invocations"][0]["invocation"],
            "explicit",
        )
        self.assertEqual(by_category["active-state-conflict"]["route_result"], "blocked")
        self.assertTrue(by_category["external-mutation-denied"]["executed"])
        self.assertEqual(
            by_category["external-mutation-denied"]["repository_state_effect"],
            "read-only",
        )
        self.assertEqual(
            by_category["limited-host-local-unavailable"]["host"],
            "claude-code",
        )
        self.assertEqual(
            by_category["limited-host-local-unavailable"]["route_result"],
            "unavailable",
        )
        self.assertFalse(by_category["limited-host-local-unavailable"]["executed"])

    def test_wayfinder_state_uses_native_identity_without_root_context_growth(self) -> None:
        VERIFIER.check_wayfinder_ownership_contract()
        policy = (PACKAGE / "payload/root/AGENTS.md.template").read_text(encoding="utf-8")
        self.assertNotIn("wayfinder:map", policy)
        self.assertNotIn("wayfinder:research", policy)
        self.assertLess(len(policy.encode("utf-8")), 5000)

    def test_package_is_path_independent(self) -> None:
        copied = self.base / "nested/location/agentic-workflow"
        shutil.copytree(PACKAGE, copied)
        verified = run(sys.executable, copied / "scripts/verify_package.py")
        self.assertEqual(verified.returncode, 0, verified.stderr)
        target = git_repository(self.base / "target")
        installed = adopt(copied / "scripts/adopt.py", "install", target)
        self.assertEqual(installed.returncode, 0, installed.stderr)

    def test_bootstrap_download_fixture_installs_in_one_invocation(self) -> None:
        packaged = fixture_package(PACKAGE, self.base / "fixture-package")
        archive = self.base / "package.tar.gz"
        with tarfile.open(archive, "w:gz") as opened:
            opened.add(packaged, arcname="source/skills/agentic-workflow")
        target = self.base / "target"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        for skill in skills:
            write_provider_skill(target, provider, skill)
        write_provider_state(target, provider, skills)
        loader = (
            "from urllib.request import urlopen; "
            f"exec(compile(urlopen({BOOTSTRAP.as_uri()!r}, timeout=30).read(), "
            "'agentic-workflow-bootstrap.py', 'exec'))"
        )
        environment = os.environ.copy()
        environment["PATH"] = str(self.base / "no-executables")
        result = run(
            sys.executable,
            "-c",
            loader,
            "install",
            target,
            "--archive-url",
            archive.as_uri(),
            "--ref",
            REVISION,
            env=environment,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("installed and verified", result.stdout)
        installed = json.loads((target / "ai-workflow/install-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(installed["source_revision"], REVISION)
        self.assertTrue((target / "ai-workflow/provider-state.json").is_file())

    def test_bootstrap_defaults_to_current_project_directory(self) -> None:
        packaged = fixture_package(PACKAGE, self.base / "fixture-package")
        archive = self.base / "package.tar.gz"
        with tarfile.open(archive, "w:gz") as opened:
            opened.add(packaged, arcname="source/skills/agentic-workflow")
        target = self.base / "current-bootstrap-project"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        for skill in skills:
            write_provider_skill(target, provider, skill)
        write_provider_state(target, provider, skills)
        loader = (
            "from urllib.request import urlopen; "
            f"exec(compile(urlopen({BOOTSTRAP.as_uri()!r}, timeout=30).read(), "
            "'agentic-workflow-bootstrap.py', 'exec'))"
        )
        result = run(
            sys.executable,
            "-c",
            loader,
            "install",
            "--archive-url",
            archive.as_uri(),
            "--ref",
            REVISION,
            cwd=target,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "ai-workflow/install-manifest.json").is_file())

    def test_windows_ordinary_modes_are_canonicalized(self) -> None:
        source = self.base / "downloaded.md"
        source.write_text("ordinary payload\n", encoding="utf-8")
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o666):
            mode = ADOPTER.reviewed_source_mode(
                source, "simulated Windows source", posix_modes_meaningful=False
            )
        self.assertEqual(mode, 0o644)
        with mock.patch.object(VERIFIER.stat, "S_IMODE", return_value=0o666):
            mode = VERIFIER.reviewed_filesystem_mode(
                source,
                expected=0o644,
                posix_modes_meaningful=False,
            )
        self.assertEqual(mode, 0o644)

    def test_windows_mode_validation_is_bounded(self) -> None:
        source = self.base / "downloaded.md"
        source.write_text("ordinary payload\n", encoding="utf-8")
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o600):
            with self.assertRaisesRegex(ADOPTER.AdoptionError, "ordinary Windows file mode"):
                ADOPTER.reviewed_source_mode(
                    source, "simulated Windows source", posix_modes_meaningful=False
                )

    def test_posix_modes_remain_strict_and_preserve_executable_intent(self) -> None:
        source = self.base / "source"
        source.write_text("payload\n", encoding="utf-8")
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o644):
            self.assertEqual(
                ADOPTER.reviewed_source_mode(source, "POSIX data", posix_modes_meaningful=True),
                0o644,
            )
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o755):
            self.assertEqual(
                ADOPTER.reviewed_source_mode(
                    source,
                    "POSIX script",
                    expected_mode=0o755,
                    posix_modes_meaningful=True,
                ),
                0o755,
            )
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o755):
            with self.assertRaisesRegex(ADOPTER.AdoptionError, "mode must be 0644"):
                ADOPTER.reviewed_source_mode(
                    source, "POSIX data", posix_modes_meaningful=True
                )
        with mock.patch.object(ADOPTER.stat, "S_IMODE", return_value=0o4755):
            with self.assertRaisesRegex(ADOPTER.AdoptionError, "mode must be 0644"):
                ADOPTER.reviewed_source_mode(source, "privileged POSIX source", posix_modes_meaningful=True)
        with mock.patch.object(VERIFIER.stat, "S_IMODE", return_value=0o4755):
            with self.assertRaisesRegex(VERIFIER.VerificationError, "mode must be 0644"):
                VERIFIER.reviewed_filesystem_mode(
                    source,
                    expected=0o644,
                    posix_modes_meaningful=True,
                )

    def test_archive_rejects_privileged_file_mode_before_extraction(self) -> None:
        archive = io.BytesIO()
        data = b"payload\n"
        with tarfile.open(fileobj=archive, mode="w:gz") as opened:
            member = tarfile.TarInfo("source/skills/agentic-workflow/payload/file.md")
            member.mode = 0o4644
            member.size = len(data)
            opened.addfile(member, io.BytesIO(data))
        (self.base / "extracted").mkdir()
        with self.assertRaisesRegex(BOOTSTRAPPER.BootstrapError, "archive package file mode"):
            BOOTSTRAPPER.extract_package(archive.getvalue(), self.base / "extracted")

    def test_archive_accepts_git_mode_variant_and_canonicalizes_it(self) -> None:
        archive = io.BytesIO()
        data = b"payload\n"
        with tarfile.open(fileobj=archive, mode="w:gz") as opened:
            member = tarfile.TarInfo("source/skills/agentic-workflow/payload/file.md")
            member.mode = 0o664
            member.size = len(data)
            opened.addfile(member, io.BytesIO(data))
        destination = self.base / "git-archive"
        destination.mkdir()
        package = BOOTSTRAPPER.extract_package(archive.getvalue(), destination)
        extracted = package / "payload/file.md"
        self.assertEqual(extracted.read_bytes(), data)
        self.assertEqual(ADOPTER.reviewed_source_mode(extracted, "extracted Git archive file"), 0o644)


if __name__ == "__main__":
    unittest.main()
