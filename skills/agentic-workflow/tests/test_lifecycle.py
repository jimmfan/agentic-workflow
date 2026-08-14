from __future__ import annotations

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
    for relative in skill["files"]:
        path = destination / str(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        if relative == "SKILL.md":
            path.write_text(
                "---\n"
                f"description: Hermetic fixture for {skill['name']}.\n"
                + metadata
                + f"name: {skill['name']}\n"
                "---\n"
                f"# {skill['name']}\n",
                encoding="utf-8",
            )
        else:
            path.write_text(f"fixture: {skill['name']}/{relative}\n", encoding="utf-8")
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


class LifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="agentic-workflow-test-")
        self.base = Path(self.temporary.name)

    def tearDown(self) -> None:
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
        self.assertEqual((target / "CLAUDE.md").read_text(encoding="utf-8"), "@AGENTS.md\n")
        self.assertTrue((target / ".agents/skills/workflow-discovery/SKILL.md").is_file())
        self.assertFalse((target / ".agents/skills/workflow-teach").exists())
        self.assertTrue((target / "ai-workflow/project-profile.md").is_file())
        self.assertTrue((target / "ai-workflow/state/active.md").is_file())
        self.assertFalse((target / "docs").exists())
        for relative in FORMER_FRAMEWORK_DOCS:
            self.assertFalse((target / relative).exists())
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

    def test_provider_install_is_pinned_complete_idempotent_and_removable(self) -> None:
        target = self.base / "provider-target"
        target.mkdir()
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
            with self.assertRaisesRegex(PROVIDER_MANAGER.ProviderError, "incompatible github-pinned"):
                PROVIDER_MANAGER.command_install(target, dry_run=False)
        install.assert_not_called()
        self.assertEqual(skill_path.read_text(encoding="utf-8"), original)
        self.assertFalse((target / "ai-workflow/provider-state.json").exists())

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

    def test_provider_upgrade_stages_and_records_new_declared_pin(self) -> None:
        target = self.base / "provider-upgrade"
        target.mkdir()
        with mock.patch.object(PROVIDER_MANAGER, "find_gh", return_value=Path("gh")), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ):
            PROVIDER_MANAGER.command_install(target, dry_run=False)

        old_provider, skills = PROVIDER_MANAGER.load_declaration()
        upgraded_provider = dict(old_provider)
        upgraded_provider["version"] = "v1.2.4"
        upgraded_provider["revision"] = "2" * 40
        with mock.patch.object(
            PROVIDER_MANAGER,
            "load_declaration",
            return_value=(upgraded_provider, skills),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "find_gh",
            return_value=Path("gh"),
        ), mock.patch.object(
            PROVIDER_MANAGER,
            "run_gh_install",
            side_effect=fake_provider_install,
        ) as install:
            PROVIDER_MANAGER.command_update(target, dry_run=False)
            self.assertTrue(PROVIDER_MANAGER.command_status(target, verbose=False))

        self.assertEqual(install.call_count, len(skills))
        state = json.loads(
            (target / "ai-workflow/provider-state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(state["provider"]["version"], "v1.2.4")
        self.assertEqual(state["provider"]["revision"], "2" * 40)
        self.assertTrue(
            all(record["origin"] == "created" for record in state["skills"].values())
        )
        _, metadata = PROVIDER_MANAGER.frontmatter(
            target / ".agents/skills/implement/SKILL.md"
        )
        self.assertEqual(metadata["github-pinned"], "v1.2.4")
        self.assertEqual(metadata["github-ref"], "refs/tags/v1.2.4")

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

    def test_coordinated_install_rolls_back_new_payload_and_seeds_on_provider_failure(self) -> None:
        target = self.base / "provider-runtime-failure"
        target.mkdir()
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
        self.assertFalse(
            (target / "ai-workflow").exists(),
            sorted(path.relative_to(target).as_posix() for path in target.rglob("*")),
        )

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

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        composite = (target / "CLAUDE.md").read_bytes()
        self.assertIn(b"@AGENTS.md\n", composite)
        self.assertIn(original, composite)

        removed = adopt(ADOPT, "remove", target)
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

    def test_reinstallation_is_idempotent(self) -> None:
        target = git_repository(self.base / "target")
        first = adopt(ADOPT, "install", target)
        self.assertEqual(first.returncode, 0, first.stderr)
        manifest = (target / "ai-workflow/install-manifest.json").read_bytes()
        second = adopt(ADOPT, "install", target)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("already installed and verified", second.stdout)
        self.assertEqual((target / "ai-workflow/install-manifest.json").read_bytes(), manifest)

    def test_tamper_is_reported_and_blocks_update(self) -> None:
        target = git_repository(self.base / "target")
        self.assertEqual(adopt(ADOPT, "install", target).returncode, 0)
        skill = target / ".agents/skills/workflow-discovery/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nlocal change\n", encoding="utf-8")
        self.assertEqual(adopt(ADOPT, "status", target).returncode, 1)
        update = adopt(ADOPT, "update", target)
        self.assertEqual(update.returncode, 2)
        self.assertIn("locally changed framework file", update.stderr)

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
        updated = adopt(ADOPT, "update", target)
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

        updated = adopt(ADOPT, "update", target)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertFalse((target / "docs").exists())
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

        updated = adopt(ADOPT, "update", target)
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

    def test_route_observability_contract_is_centralized_and_compact(self) -> None:
        policy = (PACKAGE / "payload/root/AGENTS.md.template").read_text(encoding="utf-8")
        start = policy.index("Append `[route: router → …]`")
        route_instruction = policy[start : policy.index("\n\n", start)]
        compact_instruction = " ".join(route_instruction.split())
        self.assertLessEqual(len(route_instruction.encode("utf-8")), 300)
        self.assertLessEqual(len(compact_instruction.split()), 40)
        self.assertIn("effective workflow stages already used", compact_instruction)
        self.assertIn("Explain routing only when requested", compact_instruction)
        self.assertIn("never reassess it", compact_instruction)
        self.assertIn("load skills, run workflows, or write state to produce", compact_instruction)
        for skill in (PACKAGE / "payload/skills").glob("*/SKILL.md"):
            self.assertNotIn("[route: router", skill.read_text(encoding="utf-8"))

        scenarios = json.loads(
            (PACKAGE / "tests/route-observability-scenarios.json").read_text(encoding="utf-8")
        )
        outputs = {item["id"]: item["expected_route_output"] for item in scenarios}
        self.assertEqual(outputs["wayfinder"], "[route: router → wayfinder]")
        self.assertEqual(
            outputs["implementation"],
            "[route: router → implement → verification]",
        )
        self.assertEqual(
            outputs["multi-stage"],
            "[route: router → discovery → to-spec → implement → verification]",
        )
        self.assertEqual(outputs["effective-only"], "[route: router → teach]")
        self.assertEqual(outputs["no-trigger"], "[route: router → direct]")

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
        archive = self.base / "package.tar.gz"
        with tarfile.open(archive, "w:gz") as opened:
            opened.add(PACKAGE, arcname="source/skills/agentic-workflow")
        target = self.base / "target"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        for skill in skills:
            write_provider_skill(target, provider, skill)
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
        archive = self.base / "package.tar.gz"
        with tarfile.open(archive, "w:gz") as opened:
            opened.add(PACKAGE, arcname="source/skills/agentic-workflow")
        target = self.base / "current-bootstrap-project"
        target.mkdir()
        provider, skills = PROVIDER_MANAGER.load_declaration()
        for skill in skills:
            write_provider_skill(target, provider, skill)
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
