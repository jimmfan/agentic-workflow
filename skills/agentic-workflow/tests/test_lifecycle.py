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

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
ADOPT = PACKAGE_ROOT / "scripts" / "adopt.py"
BOOTSTRAP = PACKAGE_ROOT / "scripts" / "bootstrap.py"
LIFECYCLE = PACKAGE_ROOT / "scripts" / "lifecycle.py"
PROVIDERS = PACKAGE_ROOT / "scripts" / "providers.py"
REFRESH_PROVIDERS = PACKAGE_ROOT / "scripts" / "refresh_provider_snapshot.py"
VERIFIER = PACKAGE_ROOT / "scripts" / "verify_package.py"
MANAGED_BEGIN = b"<!-- agent-workflow:managed-begin -->\n"
MANAGED_END = b"<!-- agent-workflow:managed-end -->\n"
PROJECT_BEGIN = b"\n<!-- agent-workflow:project-instructions -->\n"
WAYFINDER_ADAPTER_BEGIN = "<!-- agentic-workflow:wayfinder-local-state-v1:begin -->\n"
WAYFINDER_ADAPTER_END = "<!-- agentic-workflow:wayfinder-local-state-v1:end -->\n\n"
IMPLICIT_INVOCATION_SKILLS = ("to-spec", "to-tickets", "implement")
USER_ONLY_SKILLS = ("setup-matt-pocock-skills", "teach", "triage")


def run_script(
    script: Path,
    *arguments: object,
    env: dict[str, str] | None = None,
    encoding: str = "utf-8",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *(str(item) for item in arguments)],
        text=True,
        capture_output=True,
        encoding=encoding,
        errors="strict",
        env=env,
    )


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def tree_snapshot(root: Path) -> dict[str, tuple[str, bytes | str]]:
    result: dict[str, tuple[str, bytes | str]] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("symlink", os.readlink(path))
        elif path.is_dir():
            result[relative] = ("directory", b"")
        else:
            result[relative] = ("file", path.read_bytes())
    return result


class LifecycleAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name) / "project"
        self.project.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def adopt(self, command: str, *extra: object) -> subprocess.CompletedProcess[str]:
        return run_script(ADOPT, command, self.project, *extra)

    def assert_ok(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def copy_package(self, name: str) -> Path:
        package_copy = Path(self.temporary.name) / name / "agentic-workflow"
        shutil.copytree(PACKAGE_ROOT, package_copy)
        return package_copy

    def run_fake_provider_refresh(
        self,
        name: str,
        *,
        mutation: str | None = None,
    ) -> tuple[object, Path]:
        package_copy = self.copy_package(name)
        declaration = package_copy / "payload/agent-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        provider = raw["provider"]
        skill_name = "demo"
        skill_path = "skills/engineering/demo"
        skill_tree = "1" * 40
        provider["skills"] = [{"name": skill_name, "path": skill_path}]
        declaration.write_text(json.dumps(raw), encoding="utf-8")

        upstream_skill = b"---\ndescription: Demo skill.\nname: demo\n---\n\nDemo body.\n"
        upstream_openai = b'interface:\n  display_name: "Demo"\n'
        metadata = (
            "metadata:\n"
            f"    github-path: {skill_path}\n"
            f"    github-pinned: {provider['version']}\n"
            f"    github-ref: refs/tags/{provider['version']}\n"
            f"    github-repo: https://github.com/{provider['repository']}\n"
            f"    github-tree-sha: {skill_tree}\n"
        ).encode("utf-8")
        installed_skill = upstream_skill.replace(b"name: demo\n", metadata + b"name: demo\n")

        def git_blob_sha(content: bytes) -> str:
            header = f"blob {len(content)}\0".encode("ascii")
            return hashlib.sha1(header + content).hexdigest()

        tree_entries = [
            {"path": skill_path, "mode": "040000", "type": "tree", "sha": skill_tree},
            {
                "path": f"{skill_path}/SKILL.md",
                "mode": "100644",
                "type": "blob",
                "sha": git_blob_sha(upstream_skill),
            },
            {
                "path": f"{skill_path}/agents",
                "mode": "040000",
                "type": "tree",
                "sha": "2" * 40,
            },
            {
                "path": f"{skill_path}/agents/openai.yaml",
                "mode": "100644",
                "type": "blob",
                "sha": git_blob_sha(upstream_openai),
            },
        ]

        scripts = package_copy / "scripts"
        sys.path.insert(0, str(scripts))
        try:
            refresh = load_module(
                f"agentic_workflow_refresh_{name}",
                scripts / "refresh_provider_snapshot.py",
            )
        finally:
            sys.path.pop(0)
        refresh.shutil.which = lambda _command: "/fake/gh"

        def fake_run_gh(_gh: str, arguments: list[str]) -> str:
            if arguments[0] == "api":
                endpoint = arguments[1]
                responses = {
                    f"repos/{provider['repository']}/git/ref/tags/{provider['version']}": {
                        "object": {"type": "tag", "sha": provider["tag_object"]}
                    },
                    f"repos/{provider['repository']}/git/tags/{provider['tag_object']}": {
                        "object": {"type": "commit", "sha": provider["resolved_commit"]}
                    },
                    f"repos/{provider['repository']}/git/commits/{provider['resolved_commit']}": {
                        "tree": {"sha": provider["upstream_tree"]}
                    },
                    f"repos/{provider['repository']}/git/trees/{provider['upstream_tree']}?recursive=1": {
                        "tree": tree_entries,
                        "truncated": False,
                    },
                    f"repos/{provider['repository']}/contents/LICENSE?ref={provider['resolved_commit']}": {
                        "content": base64.b64encode(b"MIT License\n").decode("ascii")
                    },
                }
                return json.dumps(responses[endpoint])
            self.assertEqual(arguments[:2], ["skill", "install"])
            target = Path(arguments[arguments.index("--dir") + 1]) / skill_name
            (target / "agents").mkdir(parents=True)
            (target / "SKILL.md").write_bytes(installed_skill)
            installed_openai = upstream_openai
            if mutation == "modified":
                installed_openai += b"changed: true\n"
            (target / "agents/openai.yaml").write_bytes(installed_openai)
            if mutation == "extra":
                (target / "extra.md").write_text("unexpected\n", encoding="utf-8")
            if mutation == "extra-directory":
                (target / "empty").mkdir()
            return ""

        refresh.run_gh = fake_run_gh
        output = Path(self.temporary.name) / f"{name}-candidate"
        return refresh, output

    def declared_provider_names(self, package_root: Path = PACKAGE_ROOT) -> set[str]:
        declaration = package_root / "payload/agent-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        return {item["name"] for item in raw["provider"]["skills"]}

    def test_install_creates_only_current_framework_and_empty_state_root(self) -> None:
        self.assert_ok(self.adopt("install"))
        self.assertTrue((self.project / ".agent-workflow/routing.md").is_file())
        self.assertTrue((self.project / ".agent-workflow-state").is_dir())
        self.assertEqual(list((self.project / ".agent-workflow-state").iterdir()), [])
        self.assertFalse((self.project / ".agent-workflow/templates/active-state.md").exists())
        self.assertFalse((self.project / ".agent-workflow/state/README.md").exists())
        manifest = json.loads((self.project / ".agent-workflow/install-manifest.json").read_text())
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(
            set(manifest),
            {"schema_version", "framework_version", "source_revision", "external_files", "composites"},
        )
        self.assertNotIn("framework_files", manifest)
        self.assertNotIn("project_owned", manifest)

    def test_update_replaces_missing_modified_and_obsolete_reconstructable_files(self) -> None:
        self.assert_ok(self.adopt("install"))
        routing = self.project / ".agent-workflow/routing.md"
        expected = routing.read_bytes()
        routing.write_bytes(b"locally drifted framework bytes\n")
        (self.project / ".agent-workflow/README.md").unlink()
        obsolete = self.project / ".agent-workflow/state/README.md"
        obsolete.parent.mkdir()
        obsolete.write_text("historical framework file\n")
        self.assert_ok(self.adopt("update"))
        self.assertEqual(routing.read_bytes(), expected)
        self.assertTrue((self.project / ".agent-workflow/README.md").is_file())
        self.assertFalse(obsolete.exists())

    def test_deleted_framework_directory_is_rebuilt_conservatively(self) -> None:
        self.assert_ok(self.adopt("install"))
        state = self.project / ".agent-workflow-state/custom.txt"
        state.write_text("durable project bytes\n")
        shutil.rmtree(self.project / ".agent-workflow")
        self.assert_ok(self.adopt("update"))
        self.assertTrue((self.project / ".agent-workflow/routing.md").is_file())
        self.assertEqual(state.read_text(), "durable project bytes\n")
        manifest = json.loads((self.project / ".agent-workflow/install-manifest.json").read_text())
        self.assertTrue(all(not details["created"] for details in manifest["external_files"].values()))

    def test_historical_absence_is_not_a_blocker_or_recreated(self) -> None:
        self.assert_ok(self.adopt("install"))
        manifest_path = self.project / ".agent-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        retired = self.project / ".agents/skills/retired-workflow/SKILL.md"
        retired.parent.mkdir(parents=True)
        retired.write_bytes(b"old managed bytes\n")
        manifest["external_files"][".agents/skills/retired-workflow/SKILL.md"] = {
            "created": True,
            "sha256": hashlib.sha256(retired.read_bytes()).hexdigest(),
        }
        manifest_path.write_text(json.dumps(manifest))
        retired.unlink()
        self.assert_ok(self.adopt("update"))
        self.assertFalse(retired.exists())
        self.assertFalse((self.project / ".agent-workflow/state/README.md").exists())

    def test_arbitrary_durable_state_survives_update_remove_and_reinstall(self) -> None:
        state = self.project / ".agent-workflow-state"
        (state / "records/nested").mkdir(parents=True)
        (state / "records/nested/data.bin").write_bytes(b"\x00project\xffstate")
        (state / "custom.json").write_text('{"owner":"project"}\n')
        try:
            (state / "record-link").symlink_to("records/nested/data.bin")
        except OSError:
            pass
        original = tree_snapshot(state)

        self.assert_ok(self.adopt("install"))
        self.assertEqual(tree_snapshot(state), original)
        self.assert_ok(self.adopt("update"))
        self.assertEqual(tree_snapshot(state), original)
        self.assert_ok(self.adopt("remove"))
        self.assertEqual(tree_snapshot(state), original)
        self.assert_ok(self.adopt("install"))
        self.assertEqual(tree_snapshot(state), original)

    def test_human_edited_wayfinder_state_is_opaque_to_lifecycle(self) -> None:
        effort = self.project / ".agent-workflow-state/wayfinder/custom-effort"
        (effort / "unknowns").mkdir(parents=True)
        (effort / "map.md").write_text(
            "# Personal layout\n\nNo standard headings; keep exactly.\n",
            encoding="utf-8",
        )
        (effort / "unknowns/U9-free-form.md").write_text(
            "A human can structure this however they find useful.\n",
            encoding="utf-8",
        )
        original = tree_snapshot(effort)

        for command in ("install", "update", "remove", "install"):
            with self.subTest(command=command):
                self.assert_ok(self.adopt(command))
                self.assertEqual(tree_snapshot(effort), original)

    def test_composite_policy_preserves_project_region_through_update_and_remove(self) -> None:
        project_policy = b"# Project policy\n\nKeep this byte-for-byte.\n"
        (self.project / "AGENTS.md").write_bytes(project_policy)
        self.assert_ok(self.adopt("install"))
        installed = (self.project / "AGENTS.md").read_bytes()
        self.assertTrue(installed.startswith(MANAGED_BEGIN))
        self.assertTrue(installed.endswith(project_policy))

        managed_end = installed.index(MANAGED_END)
        drifted = MANAGED_BEGIN + b"drifted managed text\n" + installed[managed_end:]
        (self.project / "AGENTS.md").write_bytes(drifted)
        self.assert_ok(self.adopt("update"))
        repaired = (self.project / "AGENTS.md").read_bytes()
        self.assertNotIn(b"drifted managed text", repaired)
        self.assertTrue(repaired.endswith(project_policy))

        self.assert_ok(self.adopt("remove"))
        self.assertEqual((self.project / "AGENTS.md").read_bytes(), project_policy)
        self.assertFalse((self.project / "CLAUDE.md").exists())

    def test_malformed_composite_boundary_stops_without_partial_mutation(self) -> None:
        self.assert_ok(self.adopt("install"))
        policy = self.project / "AGENTS.md"
        policy.write_bytes(MANAGED_BEGIN + b"missing the other boundaries\n")
        routing = self.project / ".agent-workflow/routing.md"
        routing.write_bytes(b"drift that must remain after failed preflight\n")
        before = tree_snapshot(self.project)
        result = self.adopt("update")
        self.assertEqual(result.returncode, 2)
        self.assertIn("markers", result.stderr)
        self.assertEqual(tree_snapshot(self.project), before)

    def test_unknown_external_collision_is_never_overwritten(self) -> None:
        collision = self.project / ".agents/skills/workflow-debugging/SKILL.md"
        collision.parent.mkdir(parents=True)
        collision.write_text("project-owned skill\n")
        result = self.adopt("install")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown external content", result.stderr)
        self.assertEqual(collision.read_text(), "project-owned skill\n")
        self.assertFalse((self.project / ".agent-workflow").exists())
        self.assertFalse((self.project / ".agent-workflow-state").exists())

    def test_preexisting_exact_external_file_is_preserved_on_remove(self) -> None:
        source = PACKAGE_ROOT / "payload/skills/workflow-debugging/SKILL.md"
        target = self.project / ".agents/skills/workflow-debugging/SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(source.read_bytes())
        self.assert_ok(self.adopt("install"))
        self.assert_ok(self.adopt("remove"))
        self.assertEqual(target.read_bytes(), source.read_bytes())

    def test_locally_changed_created_external_file_is_preserved_on_remove(self) -> None:
        self.assert_ok(self.adopt("install"))
        target = self.project / ".agents/skills/workflow-debugging/SKILL.md"
        target.write_text("project changed this managed integration\n")
        self.assert_ok(self.adopt("remove"))
        self.assertEqual(target.read_text(), "project changed this managed integration\n")

    def test_framework_and_state_root_symlinks_are_rejected(self) -> None:
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (outside / "sentinel").write_text("safe\n")
        (self.project / ".agent-workflow").symlink_to(outside, target_is_directory=True)
        result = self.adopt("update")
        self.assertEqual(result.returncode, 2)
        self.assertEqual((outside / "sentinel").read_text(), "safe\n")

        (self.project / ".agent-workflow").unlink()
        (self.project / ".agent-workflow-state").symlink_to(outside, target_is_directory=True)
        result = self.adopt("install")
        self.assertEqual(result.returncode, 2)
        self.assertEqual((outside / "sentinel").read_text(), "safe\n")

    def test_filesystem_root_target_is_rejected(self) -> None:
        result = run_script(ADOPT, "status", Path(Path.cwd().anchor))
        self.assertEqual(result.returncode, 2)
        self.assertIn("filesystem root", result.stderr)

    def test_status_treats_optional_files_as_normal_and_drift_as_repairable(self) -> None:
        self.assert_ok(self.adopt("install"))
        result = self.adopt("status")
        self.assert_ok(result)
        self.assertIn("Agentic Workflow: healthy", result.stdout)
        self.assertFalse((self.project / ".agent-workflow-state/project-profile.md").exists())
        self.assertFalse((self.project / ".agent-workflow-state/active.md").exists())
        (self.project / ".agent-workflow/routing.md").unlink()
        result = self.adopt("status")
        self.assertEqual(result.returncode, 1)
        self.assertIn("repairable", result.stdout)

    def test_optional_provider_failure_does_not_fail_core_install(self) -> None:
        package_copy = self.copy_package("corrupt-provider-snapshot")
        snapshot = package_copy / "provider-snapshots/matt-pocock-skills/skills/research/SKILL.md"
        snapshot.write_text("corrupt bundled provider\n", encoding="utf-8")

        result = run_script(package_copy / "scripts/lifecycle.py", "install", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.project / ".agent-workflow/routing.md").is_file())
        self.assertIn("Optional provider setup did not complete", result.stderr)

    def test_optional_provider_failure_during_remove_reports_truthfully(self) -> None:
        self.assert_ok(self.adopt("install"))
        provider_file = self.project / ".agents/skills/wayfinder/personal.txt"
        provider_file.parent.mkdir(parents=True)
        provider_file.write_text("preserve provider bytes\n")

        package_copy = self.copy_package("remove-provider-failure")
        declaration = package_copy / "payload/agent-workflow/providers.json"
        declaration.write_text("{}\n", encoding="utf-8")
        result = run_script(package_copy / "scripts/lifecycle.py", "remove", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Core removal will continue; inspect the provider error", result.stderr)
        self.assertNotIn("core router and local workflows remain usable", result.stderr)
        self.assertFalse((self.project / ".agent-workflow").exists())
        self.assertEqual(provider_file.read_text(), "preserve provider bytes\n")

    def test_damaged_declared_wayfinder_content_is_safely_replaced(self) -> None:
        directory = self.project / ".agents/skills/wayfinder"
        directory.mkdir(parents=True)
        (directory / "personal.txt").write_text("do not touch\n")
        result = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((directory / "personal.txt").exists())
        self.assertIn("disable-model-invocation: false", (directory / "SKILL.md").read_text())
        self.assertIn(
            "framework-owned runtime projection",
            (directory / "SKILL.md").read_text(),
        )
        for name in self.declared_provider_names():
            self.assertTrue((self.project / ".agents/skills" / name / "SKILL.md").is_file())

    def test_fresh_lifecycle_projects_every_declared_provider_skill(self) -> None:
        empty_bin = Path(self.temporary.name) / "empty-bin"
        empty_bin.mkdir()
        env = os.environ.copy()
        env["PATH"] = str(empty_bin)

        result = run_script(LIFECYCLE, "install", self.project, env=env)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in self.declared_provider_names():
            with self.subTest(skill=name):
                self.assertTrue((self.project / ".agents/skills" / name / "SKILL.md").is_file())

    def test_update_completes_an_existing_partial_provider_projection(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        retained = {"setup-matt-pocock-skills", "wayfinder", "teach", "research"}
        before = {
            name: tree_snapshot(self.project / ".agents/skills" / name)
            for name in retained
        }
        for name in self.declared_provider_names() - retained:
            shutil.rmtree(self.project / ".agents/skills" / name)

        result = run_script(LIFECYCLE, "update", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in self.declared_provider_names():
            with self.subTest(skill=name):
                self.assertTrue((self.project / ".agents/skills" / name / "SKILL.md").is_file())
        for name, snapshot in before.items():
            self.assertEqual(tree_snapshot(self.project / ".agents/skills" / name), snapshot)

    def test_modified_and_missing_provider_skills_are_repaired_together(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        conflict = self.project / ".agents/skills/wayfinder/personal.txt"
        conflict.write_text("project-owned addition\n", encoding="utf-8")
        missing = self.project / ".agents/skills/research"
        shutil.rmtree(missing)

        result = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("reconciled optional provider skill wayfinder", result.stdout)
        self.assertIn("reconciled optional provider skill research", result.stdout)
        self.assertFalse(conflict.exists())
        self.assertTrue((missing / "SKILL.md").is_file())

    def test_unsafe_declared_provider_path_blocks_all_projection_changes(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        shutil.rmtree(self.project / ".agents/skills/research")
        shutil.rmtree(self.project / ".agents/skills/wayfinder")
        (self.project / ".agents/skills/wayfinder").write_text("unsafe\n", encoding="utf-8")

        result = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("blocked unsafe optional provider skill wayfinder", result.stderr)
        self.assertFalse((self.project / ".agents/skills/research").exists())

    def test_projection_failure_rolls_back_the_complete_changed_set(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        (self.project / ".agents/skills/wayfinder/personal.txt").write_text("old bytes\n")
        shutil.rmtree(self.project / ".agents/skills/research")
        before = tree_snapshot(self.project / ".agents/skills")

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_rollback_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)
        provider = module.load_provider()
        with tempfile.TemporaryDirectory(dir=self.project) as temporary:
            staged = module.prepare_staged_projection(Path(temporary), provider)
            original_move = module.move_path
            calls = 0

            def fail_third_move(source: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise OSError("injected projection failure")
                original_move(source, destination)

            module.move_path = fail_third_move
            with self.assertRaisesRegex(module.ProviderError, "prior projection restored"):
                module.replace_projection(self.project, staged, list(provider.skills))

        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before)

    def test_projection_revalidates_every_declared_destination_before_mutation(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        shutil.rmtree(self.project / ".agents/skills/research")

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_full_preflight_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)
        original_state = module.projection_state
        calls = 0

        def make_ready_destination_unsafe(
            root: Path, staged: Path, skill: object
        ) -> str:
            nonlocal calls
            state = original_state(root, staged, skill)
            calls += 1
            if calls == 14:
                shutil.rmtree(self.project / ".agents/skills/wayfinder")
                (self.project / ".agents/skills/wayfinder").write_text("unsafe\n")
            return state

        module.projection_state = make_ready_destination_unsafe
        with self.assertRaisesRegex(module.ProviderError, "wayfinder"):
            module.install(self.project, False)

        self.assertFalse((self.project / ".agents/skills/research").exists())
        self.assertEqual((self.project / ".agents/skills/wayfinder").read_text(), "unsafe\n")

    def test_replacement_cleanup_failure_reports_success_with_recovery_path(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        marker = self.project / ".agents/skills/wayfinder/personal.txt"
        marker.write_text("replace me\n")

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_replace_cleanup_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)
        provider = module.load_provider()
        original_rmtree = module.shutil.rmtree
        warning = io.StringIO()
        try:
            with tempfile.TemporaryDirectory(dir=self.project) as temporary:
                staged = module.prepare_staged_projection(Path(temporary), provider)

                def fail_recovery_cleanup(path: object, *args: object, **kwargs: object) -> None:
                    if Path(path).name.startswith(".agent-workflow-provider-rollback-"):
                        raise PermissionError("injected cleanup failure")
                    original_rmtree(path, *args, **kwargs)

                module.shutil.rmtree = fail_recovery_cleanup
                with redirect_stderr(warning):
                    changed = module.replace_projection(
                        self.project, staged, list(provider.skills)
                    )
        finally:
            module.shutil.rmtree = original_rmtree

        self.assertEqual([skill.name for skill in changed], ["wayfinder"])
        self.assertFalse(marker.exists())
        recovery = list(self.project.glob(".agent-workflow-provider-rollback-*"))
        self.assertEqual(len(recovery), 1)
        self.assertIn("replacement committed", warning.getvalue())
        original_rmtree(recovery[0])

    def test_removal_failure_rolls_back_every_moved_provider(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        before = tree_snapshot(self.project / ".agents/skills")

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_remove_rollback_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)
        provider = module.load_provider()
        original_move = module.move_path
        calls = 0

        def fail_second_move(source: Path, destination: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected removal failure")
            original_move(source, destination)

        module.move_path = fail_second_move
        with self.assertRaisesRegex(module.ProviderError, "prior projection restored"):
            module.remove_projection(self.project, list(provider.skills))

        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before)

    def test_removal_cleanup_failure_reports_success_with_recovery_path(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_remove_cleanup_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)
        provider = module.load_provider()
        original_rmtree = module.shutil.rmtree
        warning = io.StringIO()
        try:
            def fail_recovery_cleanup(path: object, *args: object, **kwargs: object) -> None:
                if Path(path).name.startswith(".agent-workflow-provider-remove-"):
                    raise PermissionError("injected cleanup failure")
                original_rmtree(path, *args, **kwargs)

            module.shutil.rmtree = fail_recovery_cleanup
            with redirect_stderr(warning):
                removed = module.remove_projection(self.project, list(provider.skills))
        finally:
            module.shutil.rmtree = original_rmtree

        self.assertEqual({skill.name for skill in removed}, self.declared_provider_names())
        for name in self.declared_provider_names():
            self.assertFalse((self.project / ".agents/skills" / name).exists())
        recovery = list(self.project.glob(".agent-workflow-provider-remove-*"))
        self.assertEqual(len(recovery), 1)
        self.assertIn("removal committed", warning.getvalue())
        original_rmtree(recovery[0])

    def test_remove_does_not_announce_success_before_transaction(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_remove_output_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)

        def fail_remove(*_args: object, **_kwargs: object) -> None:
            raise module.ProviderError("injected remove failure")

        module.remove_projection = fail_remove
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaisesRegex(
            module.ProviderError, "injected remove failure"
        ):
            module.remove(self.project, False)
        self.assertNotIn("removed declared optional provider directories", output.getvalue())

    def test_runtime_projection_does_not_enforce_release_snapshot_checksum(self) -> None:
        package_copy = self.copy_package("runtime-provider-checksum")
        snapshot = package_copy / "provider-snapshots/matt-pocock-skills/skills/codebase-design/SKILL.md"
        snapshot.write_text(
            snapshot.read_text(encoding="utf-8") + "\nrelease-content-drift\n",
            encoding="utf-8",
        )

        result = run_script(package_copy / "scripts/providers.py", "install", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK: Optional provider skills match the bundled projection.", result.stdout)
        projected = self.project / ".agents/skills/codebase-design/SKILL.md"
        self.assertTrue(
            projected.read_text(encoding="utf-8").endswith("\nrelease-content-drift\n")
        )

    def test_implicit_invocation_adapters_apply_from_bundle_and_are_idempotent(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        before_second = tree_snapshot(self.project / ".agents/skills")
        second = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before_second)
        for name in IMPLICIT_INVOCATION_SKILLS:
            with self.subTest(skill=name):
                skill_text = (self.project / ".agents/skills" / name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                openai_text = (
                    self.project / ".agents/skills" / name / "agents/openai.yaml"
                ).read_text(encoding="utf-8")
                self.assertIn("disable-model-invocation: false", skill_text)
                self.assertNotIn("disable-model-invocation: true", skill_text)
                self.assertIn("allow_implicit_invocation: true", openai_text)
                self.assertNotIn("allow_implicit_invocation: false", openai_text)
        for name in USER_ONLY_SKILLS:
            with self.subTest(skill=name):
                skill_text = (self.project / ".agents/skills" / name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                openai_text = (
                    self.project / ".agents/skills" / name / "agents/openai.yaml"
                ).read_text(encoding="utf-8")
                self.assertIn("disable-model-invocation: true", skill_text)
                self.assertIn("allow_implicit_invocation: false", openai_text)

    def test_provider_status_is_nonzero_while_declared_projection_is_incomplete(self) -> None:
        result = run_script(PROVIDERS, "status", self.project)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("0 ready, 14 repairable, 0 blocked", result.stdout)

    def test_lifecycle_status_reports_incomplete_provider_projection_without_failing_core(self) -> None:
        self.assert_ok(self.adopt("install"))

        result = run_script(LIFECYCLE, "status", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Agentic Workflow: healthy", result.stdout)
        self.assertIn("Optional provider projection is incomplete", result.stderr)

    def test_wayfinder_owned_runtime_projects_from_recognized_upstream_input(self) -> None:
        result = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        skill_text = (self.project / ".agents/skills/wayfinder/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn(WAYFINDER_ADAPTER_BEGIN, skill_text)
        self.assertNotIn(WAYFINDER_ADAPTER_END, skill_text)
        self.assertIn("framework-owned runtime projection", skill_text)
        self.assertIn("Effort naming, selection, and stable paths", skill_text)
        self.assertIn("The map H1 is the durable human-readable effort name", skill_text)
        self.assertIn("reread the effort-directory listing", skill_text)
        normalized_skill = " ".join(skill_text.split())
        self.assertIn("derived from Matt Pocock's Wayfinder methodology", normalized_skill)
        self.assertIn("never force U# -> E# -> F# -> D# as ceremony", normalized_skill)
        self.assertIn("never renumber a current record", normalized_skill)
        self.assertIn("Status: current | completed | abandoned | superseded", normalized_skill)
        self.assertIn("When a U# resolves", normalized_skill)
        self.assertIn("U/E/F/D files are current knowledge roles", normalized_skill)
        self.assertIn("After removal its number is no longer reserved", normalized_skill)
        self.assertIn(".wayfinder-mutation-lock/", normalized_skill)
        self.assertIn("Exact current contents need not already exist in Git", normalized_skill)
        self.assertIn("Wayfinder does not create implementation work items", normalized_skill)
        self.assertIn("`map.md` alone is valid", normalized_skill)
        self.assertIn("Keep the map self-contained", normalized_skill)
        for incompatible in (
            "shared map on the repo's issue tracker",
            "labelled `wayfinder:map`",
            "Each ticket is a **child issue**",
            "Each ticket carries a `wayfinder:<type>` label",
            "A session **claims** a ticket by assigning it",
            "tracker's **native** dependency relationship",
            "run `/setup-matt-pocock-skills`",
            "default to the local-markdown tracker",
            "post the answer as a **resolution comment**",
            "**close** the issue",
        ):
            self.assertNotIn(incompatible, skill_text)
        self.assertIn(
            "disable-model-invocation: false",
            (self.project / ".agents/skills/wayfinder/SKILL.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "description: Keep a lightweight structured map",
            (self.project / ".agents/skills/wayfinder/SKILL.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "allow_implicit_invocation: true",
            (self.project / ".agents/skills/wayfinder/agents/openai.yaml").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "short_description: \"Keep a lightweight map of complicated work\"",
            (self.project / ".agents/skills/wayfinder/agents/openai.yaml").read_text(encoding="utf-8"),
        )

    def test_unadapted_upstream_wayfinder_is_repaired_for_model_invocation(self) -> None:
        source = PACKAGE_ROOT / "provider-snapshots/matt-pocock-skills/skills/wayfinder"
        destination = self.project / ".agents/skills/wayfinder"
        destination.parent.mkdir(parents=True)
        shutil.copytree(source, destination)

        result = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("reconciled optional provider skill wayfinder", result.stdout)
        self.assertIn(
            "disable-model-invocation: false",
            (destination / "SKILL.md").read_text(encoding="utf-8"),
        )
        self.assertTrue((self.project / ".agents/skills/research/SKILL.md").is_file())

    def test_legacy_prepend_wayfinder_projection_is_repaired_to_owned_runtime(self) -> None:
        source = PACKAGE_ROOT / "provider-snapshots/matt-pocock-skills/skills/wayfinder"
        destination = self.project / ".agents/skills/wayfinder"
        destination.parent.mkdir(parents=True)
        shutil.copytree(source, destination)
        skill_path = destination / "SKILL.md"
        upstream = skill_path.read_text(encoding="utf-8")
        frontmatter, body = upstream.split("\n---\n", 1)
        legacy = (
            frontmatter.replace(
                "disable-model-invocation: true",
                "disable-model-invocation: false",
            )
            + "\n---\n"
            + WAYFINDER_ADAPTER_BEGIN
            + "## Agentic Workflow local mode (authoritative)\n\nLegacy overlay.\n\n"
            + WAYFINDER_ADAPTER_END
            + body
        )
        skill_path.write_text(legacy, encoding="utf-8")
        openai = destination / "agents/openai.yaml"
        openai.write_text(
            openai.read_text(encoding="utf-8").replace(
                "allow_implicit_invocation: false",
                "allow_implicit_invocation: true",
            ),
            encoding="utf-8",
        )

        result = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        repaired = skill_path.read_text(encoding="utf-8")
        self.assertIn("framework-owned runtime projection", repaired)
        self.assertNotIn(WAYFINDER_ADAPTER_BEGIN, repaired)
        self.assertNotIn("shared map on the repo's issue tracker", repaired)

    def test_stale_owned_wayfinder_projection_is_repaired_to_current_runtime(self) -> None:
        install = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        skill_path = self.project / ".agents/skills/wayfinder/SKILL.md"
        frontmatter, _ = skill_path.read_text(encoding="utf-8").split("\n---\n", 1)
        skill_path.write_text(
            frontmatter
            + "\n---\n# Wayfinder\n\nAgentic Workflow's stale owned runtime projection.\n",
            encoding="utf-8",
        )

        result = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("reconciled optional provider skill wayfinder", result.stdout)
        repaired = skill_path.read_text(encoding="utf-8")
        self.assertIn("## Effort naming, selection, and stable paths", repaired)
        self.assertNotIn("stale owned runtime projection", repaired)

    def test_malformed_owned_runtime_source_fails_before_projection_mutation(self) -> None:
        install = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        before = tree_snapshot(self.project / ".agents/skills")
        package_copy = self.copy_package("malformed-wayfinder-runtime")
        projection = package_copy / "runtime-projections/wayfinder.md"
        projection.write_text("not a Wayfinder runtime\n", encoding="utf-8")

        result = run_script(package_copy / "scripts/providers.py", "install", self.project)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("runtime projection is malformed", result.stderr)
        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before)

    def test_exact_existing_projection_is_reused_without_writing(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        before = tree_snapshot(self.project / ".agents/skills")

        second = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("reuse exact optional provider skill wayfinder", second.stdout)
        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before)

    def test_modified_provider_metadata_is_restored_from_bundle(self) -> None:
        install = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        openai = self.project / ".agents/skills/wayfinder/agents/openai.yaml"
        openai.write_text("policy:\n  allow_implicit_invocation: ask\n", encoding="utf-8")

        result = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("reconciled optional provider skill wayfinder", result.stdout)
        self.assertIn("allow_implicit_invocation: true", openai.read_text(encoding="utf-8"))

    def test_provider_status_reports_modified_content_without_writing(self) -> None:
        install = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        changed = self.project / ".agents/skills/wayfinder/personal.txt"
        changed.write_text("user change\n", encoding="utf-8")
        before = tree_snapshot(self.project / ".agents/skills")

        result = run_script(PROVIDERS, "status", self.project)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("13 ready, 1 repairable, 0 blocked", result.stdout)
        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before)

    def test_provider_remove_deletes_only_declared_provider_directories(self) -> None:
        install = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        unrelated = self.project / ".agents/skills/my-local-skill/SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("local\n", encoding="utf-8")

        result = run_script(PROVIDERS, "remove", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("removed declared optional provider directories", result.stdout)
        for name in self.declared_provider_names():
            self.assertFalse((self.project / ".agents/skills" / name).exists())
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "local\n")

    def test_cp1252_console_escapes_unrepresentable_project_path(self) -> None:
        project = Path(self.temporary.name) / "project-snow-\u96ea"
        project.mkdir()
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"
        install = run_script(ADOPT, "install", project, env=env, encoding="cp1252")
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        status = run_script(ADOPT, "status", project, env=env, encoding="cp1252")
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertIn("\\u96ea", status.stdout)

    def test_payload_content_edits_need_no_manifest_refresh_but_mapping_changes_do(self) -> None:
        package_copy = self.copy_package("mapping-change")

        source = package_copy / "payload/agent-workflow/README.md"
        source.write_text(
            source.read_text(encoding="utf-8") + "\nCurrent package bytes are authoritative.\n",
            encoding="utf-8",
        )

        runtime = run_script(package_copy / "scripts/adopt.py", "install", self.project)
        self.assertEqual(runtime.returncode, 0, runtime.stdout + runtime.stderr)
        self.assertEqual(
            (self.project / ".agent-workflow/README.md").read_bytes(),
            source.read_bytes(),
        )

        verify = run_script(package_copy / "scripts/verify_package.py")
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

        unmapped = package_copy / "payload/agent-workflow/contracts/new-contract.md"
        unmapped.write_text("# Newly packaged contract\n", encoding="utf-8")
        verify = run_script(package_copy / "scripts/verify_package.py")
        self.assertEqual(verify.returncode, 1)
        self.assertIn("manifest is stale", verify.stderr)

    def test_verifier_rejects_incomplete_provider_declarations(self) -> None:
        package_copy = self.copy_package("provider-declaration")
        declaration = package_copy / "payload/agent-workflow/providers.json"
        valid = json.loads(declaration.read_text(encoding="utf-8"))

        cases = (
            ("empty skill name", "name", "", "invalid provider skill name"),
            ("missing skill path", "path", None, "needs a path"),
            ("incomplete invocation hosts", "invocation", {}, "invocation hosts differ"),
            (
                "unknown configuration requirement",
                "requires_configuration",
                ["not-declared"],
                "invalid configuration requirements",
            ),
            (
                "non-string configuration requirement",
                "requires_configuration",
                [{}],
                "invalid configuration requirements",
            ),
        )
        for label, field, value, expected in cases:
            with self.subTest(label=label):
                candidate = json.loads(json.dumps(valid))
                skill = candidate["provider"]["skills"][0]
                if value is None:
                    skill.pop(field)
                else:
                    skill[field] = value
                declaration.write_text(json.dumps(candidate), encoding="utf-8")
                verify = run_script(package_copy / "scripts/verify_package.py")
                self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
                self.assertIn(expected, verify.stderr)

    def test_provider_cli_rejects_non_string_configuration_requirements(self) -> None:
        package_copy = self.copy_package("provider-requirement-type")
        declaration = package_copy / "payload/agent-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        raw["provider"]["skills"][0]["requires_configuration"] = [{}]
        declaration.write_text(json.dumps(raw), encoding="utf-8")

        result = run_script(package_copy / "scripts/providers.py", "status", self.project)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("invalid configuration requirements", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_verifier_requires_the_wayfinder_local_state_adapter(self) -> None:
        package_copy = self.copy_package("wayfinder-adapter-declaration")
        declaration = package_copy / "payload/agent-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        wayfinder = next(item for item in raw["provider"]["skills"] if item["name"] == "wayfinder")
        wayfinder.pop("agentic_workflow_adapter")
        wayfinder["invocation"]["codex"] = "user-only"
        wayfinder["invocation"]["github-copilot"] = "user-only"
        declaration.write_text(json.dumps(raw), encoding="utf-8")

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("Wayfinder must declare", verify.stderr)

    def test_verifier_rejects_conflicting_owned_wayfinder_runtime_content(self) -> None:
        package_copy = self.copy_package("conflicting-wayfinder-runtime")
        projection = package_copy / "runtime-projections/wayfinder.md"
        projection.write_text(
            projection.read_text(encoding="utf-8")
            + "\nEach ticket is a **child issue** of the map.\n",
            encoding="utf-8",
        )

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("owned Wayfinder runtime contains incompatible tracker mechanics", verify.stderr)

    def test_verifier_requires_implicit_invocation_adapters(self) -> None:
        package_copy = self.copy_package("implicit-invocation-adapter-declaration")
        declaration = package_copy / "payload/agent-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        implement = next(item for item in raw["provider"]["skills"] if item["name"] == "implement")
        implement.pop("agentic_workflow_adapter")
        declaration.write_text(json.dumps(raw), encoding="utf-8")

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("implement must declare the implicit-invocation adapter", verify.stderr)

    def test_verifier_rejects_corrupt_provider_snapshot_and_provenance(self) -> None:
        package_copy = self.copy_package("provider-snapshot-integrity")
        snapshot = package_copy / "provider-snapshots/matt-pocock-skills/skills/research/SKILL.md"
        original = snapshot.read_bytes()
        snapshot.write_bytes(original + b"\ncorrupt\n")

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("snapshot checksum", verify.stderr)

        snapshot.write_bytes(original)
        declaration = package_copy / "payload/agent-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        raw["provider"]["resolved_commit"] = "0" * 40
        declaration.write_text(json.dumps(raw), encoding="utf-8")

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("resolved_commit", verify.stderr)

    def test_verifier_rejects_source_package_provider_declaration_drift(self) -> None:
        package_copy = self.copy_package("provider-declaration-parity")
        installed = package_copy.parents[1] / ".agent-workflow/providers.json"
        installed.parent.mkdir()
        installed.write_text("{}\n", encoding="utf-8")

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("source and packaged provider declarations differ", verify.stderr)

    def test_provider_refresh_refuses_to_write_inside_the_package(self) -> None:
        candidate = PACKAGE_ROOT / "candidate-provider-snapshot"
        self.assertFalse(candidate.exists())

        result = run_script(REFRESH_PROVIDERS, candidate)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("outside the Agentic Workflow package", result.stderr)
        self.assertFalse(candidate.exists())

    def test_provider_refresh_verifies_every_installed_byte_against_the_commit_tree(self) -> None:
        refresh, output = self.run_fake_provider_refresh("exact-provider-refresh")

        refresh.generate(output)

        self.assertTrue((output / "skills/demo/SKILL.md").is_file())

    def test_provider_refresh_rejects_modified_or_extra_installed_files(self) -> None:
        for mutation in ("modified", "extra", "extra-directory"):
            with self.subTest(mutation=mutation):
                refresh, output = self.run_fake_provider_refresh(
                    f"{mutation}-provider-refresh",
                    mutation=mutation,
                )

                with self.assertRaisesRegex(refresh.RefreshError, "pinned commit tree"):
                    refresh.generate(output)

                self.assertFalse(output.exists())

    def test_provider_refresh_console_escapes_unrepresentable_output_path(self) -> None:
        package_copy = self.copy_package("refresh-console")
        driver = Path(self.temporary.name) / "refresh-console-driver.py"
        driver.write_text(
            "import importlib.util\n"
            "import sys\n"
            f"path = {str(package_copy / 'scripts/refresh_provider_snapshot.py')!r}\n"
            "sys.path.insert(0, str(__import__('pathlib').Path(path).parent))\n"
            "spec = importlib.util.spec_from_file_location('refresh_console', path)\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "module.generate = lambda output: print(f'Generated {output}')\n"
            "raise SystemExit(module.main(['/tmp/provider-snow-\\u96ea']))\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"

        result = run_script(driver, env=env, encoding="cp1252")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("\\u96ea", result.stdout)

    def test_verifier_ignores_existing_cache_and_does_not_add_cache_files(self) -> None:
        package_copy = self.copy_package("verifier-bytecode")
        cache = package_copy / "scripts/__pycache__"
        cache.mkdir(exist_ok=True)
        generated = cache / "local-test.cpython-311.pyc"
        generated.write_bytes(b"generated test cache\n")
        before = {path.name: path.read_bytes() for path in cache.iterdir() if path.is_file()}

        result = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {path.name: path.read_bytes() for path in cache.iterdir() if path.is_file()}
        self.assertEqual(after, before)

    def test_provider_reference_validation_rejects_external_resources(self) -> None:
        snapshot_module = load_module(
            "agentic_workflow_provider_snapshot",
            PACKAGE_ROOT / "scripts/provider_snapshot.py",
        )
        skill = Path(self.temporary.name) / "referencing-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("Use [shared](../shared.md).\n", encoding="utf-8")

        with self.assertRaisesRegex(snapshot_module.SnapshotTreeError, "escape"):
            snapshot_module.validate_local_references(skill)

    def test_verifier_rejects_removed_subsystem_recreated_as_a_file(self) -> None:
        package_copy = self.copy_package("removed-runtime")
        removed_path = package_copy / "payload/hosts"
        if removed_path.exists():
            removed_path.rmdir()
        removed_path.write_text("retired runtime payload\n", encoding="utf-8")

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("deferred v0 subsystem remains packaged", verify.stderr)

    def test_verifier_distinguishes_json_catalogs_from_toml_scenarios(self) -> None:
        package_copy = self.copy_package("scenario-layers")
        acceptance_path = package_copy / "tests/acceptance-scenarios.json"
        acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
        acceptance[0].pop("operation")
        acceptance_path.write_text(json.dumps(acceptance), encoding="utf-8")

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("acceptance-scenarios.json case needs a non-empty operation", verify.stderr)

        acceptance_path.write_bytes((PACKAGE_ROOT / "tests/acceptance-scenarios.json").read_bytes())
        scenario_path = package_copy / "tests/scenarios/simple-bounded-task.toml"
        scenario_path.write_text(
            'unknown_contract_field = "unexpected"\n' + scenario_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("behavioral scenario validation failed", verify.stderr)


class BootstrapSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bootstrap = load_module("agentic_workflow_bootstrap", PACKAGE_ROOT / "scripts/bootstrap.py")

    def archive(self, entries: list[tuple[str, bytes, str]]) -> bytes:
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w:gz") as archive:
            for name, data, kind in entries:
                member = tarfile.TarInfo(name)
                member.mode = 0o644
                if kind == "symlink":
                    member.type = tarfile.SYMTYPE
                    member.linkname = "elsewhere"
                    archive.addfile(member)
                elif kind == "special":
                    member.type = tarfile.FIFOTYPE
                    archive.addfile(member)
                else:
                    member.size = len(data)
                    archive.addfile(member, io.BytesIO(data))
        return output.getvalue()

    def package_archive(self, unrelated_entries: int = 0) -> bytes:
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w:gz") as archive:
            for index in range(unrelated_entries):
                data = b"{}"
                member = tarfile.TarInfo(f"source/evaluations/case-{index}.json")
                member.mode = 0o644
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
            for path in sorted(PACKAGE_ROOT.rglob("*")):
                if not path.is_file() or path.is_symlink() or "__pycache__" in path.parts:
                    continue
                relative = path.relative_to(PACKAGE_ROOT).as_posix()
                data = path.read_bytes()
                member = tarfile.TarInfo(f"source/skills/agentic-workflow/{relative}")
                member.mode = 0o644
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
        return output.getvalue()

    def test_corrupt_archive_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(self.bootstrap.BootstrapError):
                self.bootstrap.extract_package(b"not a tar archive", Path(temporary))

    def test_traversal_and_link_entries_are_rejected(self) -> None:
        cases = [
            [("root/skills/agentic-workflow/../escape", b"bad", "file")],
            [("root/skills/agentic-workflow/scripts/lifecycle.py", b"", "symlink")],
            [("root/skills/agentic-workflow/scripts/lifecycle.py", b"", "special")],
        ]
        for entries in cases:
            with self.subTest(entries=entries), tempfile.TemporaryDirectory() as temporary:
                with self.assertRaises(self.bootstrap.BootstrapError):
                    self.bootstrap.extract_package(self.archive(entries), Path(temporary))

    def test_unrelated_repository_entries_do_not_exhaust_package_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            archive = root / "repository.tar.gz"
            archive.write_bytes(
                self.package_archive(self.bootstrap.MAX_PACKAGE_MEMBERS + 1)
            )
            result = run_script(
                BOOTSTRAP,
                "install",
                project,
                "--archive-url",
                archive.as_uri(),
                "--dry-run",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((project / ".agent-workflow").exists())

    def test_excessive_package_entries_are_rejected(self) -> None:
        entries = [
            (f"root/skills/agentic-workflow/data/item-{index}.txt", b"x", "file")
            for index in range(self.bootstrap.MAX_PACKAGE_MEMBERS + 1)
        ]

        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                self.bootstrap.BootstrapError,
                f"package contains more than {self.bootstrap.MAX_PACKAGE_MEMBERS} entries",
            ):
                self.bootstrap.extract_package(self.archive(entries), Path(temporary))

    def test_whole_archive_parsing_ceiling_is_retained(self) -> None:
        entries = [
            (f"root/unrelated/item-{index}.txt", b"", "file")
            for index in range(self.bootstrap.MAX_ARCHIVE_MEMBERS + 1)
        ]

        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                self.bootstrap.BootstrapError,
                f"source archive contains more than {self.bootstrap.MAX_ARCHIVE_MEMBERS} entries",
            ):
                self.bootstrap.extract_package(self.archive(entries), Path(temporary))

    def test_bootstrap_rejects_a_symlink_project_root_before_download(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            link = root / "project-link"
            link.symlink_to(project, target_is_directory=True)
            with self.assertRaises(self.bootstrap.BootstrapError):
                self.bootstrap.main(["status", str(link), "--archive-url", "unused"])

    def test_local_archive_bootstrap_installs_core_and_providers_without_external_tools(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            archive = root / "package.tar.gz"
            archive.write_bytes(self.package_archive())
            empty_bin = root / "bin"
            empty_bin.mkdir()
            env = os.environ.copy()
            env["PATH"] = str(empty_bin)
            result = run_script(
                BOOTSTRAP,
                "install",
                project,
                "--archive-url",
                archive.as_uri(),
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / ".agent-workflow/routing.md").is_file())
            self.assertTrue((project / ".agent-workflow-state").is_dir())
            declaration = json.loads(
                (PACKAGE_ROOT / "payload/agent-workflow/providers.json").read_text(encoding="utf-8")
            )
            names = {item["name"] for item in declaration["provider"]["skills"]}
            for name in names:
                with self.subTest(skill=name):
                    self.assertTrue((project / ".agents/skills" / name / "SKILL.md").is_file())
            self.assertNotIn("GitHub CLI", result.stderr)

    def test_minimum_runtime_files_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "agentic-workflow"
            package.mkdir()
            with self.assertRaises(self.bootstrap.BootstrapError):
                self.bootstrap.validate_runtime_package(package)


if __name__ == "__main__":
    unittest.main()
