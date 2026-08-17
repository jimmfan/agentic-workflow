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


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
ADOPT = PACKAGE_ROOT / "scripts" / "adopt.py"
BOOTSTRAP = PACKAGE_ROOT / "scripts" / "bootstrap.py"
LIFECYCLE = PACKAGE_ROOT / "scripts" / "lifecycle.py"
PROVIDERS = PACKAGE_ROOT / "scripts" / "providers.py"
VERIFIER = PACKAGE_ROOT / "scripts" / "verify_package.py"
MANAGED_BEGIN = b"<!-- ai-workflow:managed-begin -->\n"
MANAGED_END = b"<!-- ai-workflow:managed-end -->\n"
PROJECT_BEGIN = b"\n<!-- ai-workflow:project-instructions -->\n"
WAYFINDER_ADAPTER_BEGIN = "<!-- agentic-workflow:wayfinder-local-state-v1:begin -->\n"
WAYFINDER_ADAPTER_END = "<!-- agentic-workflow:wayfinder-local-state-v1:end -->\n\n"


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

    def keep_only_wayfinder_provider(self, package_copy: Path) -> None:
        declaration = package_copy / "payload/ai-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        raw["provider"]["skills"] = [
            item for item in raw["provider"]["skills"] if item["name"] == "wayfinder"
        ]
        raw["capabilities"] = {"planning": "wayfinder"}
        declaration.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")

    def declared_provider_names(self, package_root: Path = PACKAGE_ROOT) -> set[str]:
        declaration = package_root / "payload/ai-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        return {item["name"] for item in raw["provider"]["skills"]}

    def upstream_wayfinder_files(self) -> tuple[str, str]:
        directory = REPOSITORY_ROOT / ".agents/skills/wayfinder"
        skill_text = (directory / "SKILL.md").read_text(encoding="utf-8")
        if WAYFINDER_ADAPTER_BEGIN in skill_text:
            begin = skill_text.index(WAYFINDER_ADAPTER_BEGIN)
            end = skill_text.index(WAYFINDER_ADAPTER_END, begin) + len(WAYFINDER_ADAPTER_END)
            skill_text = skill_text[:begin] + skill_text[end:]
        skill_text = skill_text.replace(
            "description: Keep a lightweight structured map when important unknowns, decisions, "
            "dependencies, blockers, or conflicting facts are becoming unreliable to hold in "
            "ordinary context.\n",
            "description: Plan a huge chunk of work — more than one agent session can hold — "
            "as a shared map of decision tickets on your issue tracker, and resolve them one at "
            "a time until the way to the destination is clear.\n",
            1,
        ).replace("disable-model-invocation: false\n", "disable-model-invocation: true\n", 1)
        openai_text = (directory / "agents/openai.yaml").read_text(encoding="utf-8")
        openai_text = openai_text.replace(
            '  short_description: "Keep a lightweight map of complicated work"\n',
            '  short_description: "Map a large effort as decision tickets"\n',
            1,
        ).replace("  allow_implicit_invocation: true\n", "  allow_implicit_invocation: false\n", 1)
        return skill_text, openai_text

    def write_fake_provider_skill(self, project: Path, name: str) -> None:
        if name == "wayfinder":
            self.write_upstream_wayfinder_metadata(project)
            return
        directory = project / ".agents/skills" / name
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text(
            "---\n"
            f"description: Fake {name} provider skill.\n"
            f"name: {name}\n"
            "---\n"
            "\n"
            "Fake provider method.\n",
            encoding="utf-8",
        )

    def fake_gh_provider_installer(
        self,
        name: str,
        *,
        fail_skill: str | None = None,
        omit_skill: str | None = None,
        missing_copilot_policy_skill: str | None = None,
        missing_codex_policy_skill: str | None = None,
    ) -> Path:
        wayfinder_skill, wayfinder_openai = self.upstream_wayfinder_files()
        fake_bin = Path(self.temporary.name) / name
        fake_bin.mkdir()
        gh = fake_bin / "gh"
        gh.write_text(
            f"#!{sys.executable}\n"
            "from pathlib import Path\n"
            "import sys\n"
            f"fail_skill = {fail_skill!r}\n"
            f"omit_skill = {omit_skill!r}\n"
            f"missing_copilot_policy_skill = {missing_copilot_policy_skill!r}\n"
            f"missing_codex_policy_skill = {missing_codex_policy_skill!r}\n"
            f"wayfinder_skill = {wayfinder_skill!r}\n"
            f"wayfinder_openai = {wayfinder_openai!r}\n"
            "skill_path = sys.argv[4]\n"
            "skill_name = Path(skill_path).name\n"
            "if skill_name == fail_skill:\n"
            "    print(f'failed {skill_name}', file=sys.stderr)\n"
            "    raise SystemExit(23)\n"
            "if '--dir' not in sys.argv:\n"
            "    print('missing staged --dir', file=sys.stderr)\n"
            "    raise SystemExit(24)\n"
            "if skill_name == omit_skill:\n"
            "    raise SystemExit(0)\n"
            "destination = Path(sys.argv[sys.argv.index('--dir') + 1]) / skill_name\n"
            "(destination / 'agents').mkdir(parents=True)\n"
            "repository = sys.argv[3]\n"
            "version = sys.argv[sys.argv.index('--pin') + 1]\n"
            "source_metadata = f\"metadata:\\n    github-path: {skill_path}\\n    github-pinned: {version}\\n    github-ref: refs/tags/{version}\\n    github-repo: https://github.com/{repository}\\n\"\n"
            "if skill_name == 'wayfinder':\n"
            "    skill_text = wayfinder_skill\n"
            "    openai_text = wayfinder_openai\n"
            "else:\n"
            "    user_only = skill_name in {'setup-matt-pocock-skills', 'teach', 'to-spec', 'to-tickets', 'implement', 'triage'}\n"
            "    disable = \"disable-model-invocation: true\\n\" if user_only and skill_name != missing_copilot_policy_skill else \"\"\n"
            "    skill_text = f\"---\\ndescription: Fake {skill_name} provider skill.\\n{disable}\" + source_metadata + f\"name: {skill_name}\\n---\\n\\nFake provider method.\\n\"\n"
            "    policy = \"policy:\\n  allow_implicit_invocation: false\\n\" if user_only and skill_name != missing_codex_policy_skill else \"\"\n"
            "    openai_text = f\"interface:\\n  display_name: \\\"{skill_name}\\\"\\n{policy}\"\n"
            "(destination / 'SKILL.md').write_text(skill_text, encoding='utf-8')\n"
            "(destination / 'agents/openai.yaml').write_text(openai_text, encoding='utf-8')\n",
            encoding="utf-8",
        )
        gh.chmod(0o755)
        return fake_bin

    def assert_provider_staging_rejected(self, fake_bin: Path, expected: str) -> None:
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"

        result = run_script(PROVIDERS, "install", self.project, env=env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected, result.stderr)
        for name in self.declared_provider_names():
            self.assertFalse((self.project / ".agents/skills" / name).exists())

    def write_upstream_wayfinder_metadata(self, project: Path) -> None:
        directory = project / ".agents/skills/wayfinder"
        (directory / "agents").mkdir(parents=True)
        skill_text, openai_text = self.upstream_wayfinder_files()
        (directory / "SKILL.md").write_text(skill_text, encoding="utf-8")
        (directory / "agents/openai.yaml").write_text(openai_text, encoding="utf-8")

    def test_install_creates_only_current_framework_and_empty_state_root(self) -> None:
        self.assert_ok(self.adopt("install"))
        self.assertTrue((self.project / ".ai-workflow/routing.md").is_file())
        self.assertTrue((self.project / ".ai-workflow-state").is_dir())
        self.assertEqual(list((self.project / ".ai-workflow-state").iterdir()), [])
        self.assertFalse((self.project / ".ai-workflow/templates/active-state.md").exists())
        self.assertFalse((self.project / ".ai-workflow/state/README.md").exists())
        manifest = json.loads((self.project / ".ai-workflow/install-manifest.json").read_text())
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(
            set(manifest),
            {"schema_version", "framework_version", "source_revision", "external_files", "composites"},
        )
        self.assertNotIn("framework_files", manifest)
        self.assertNotIn("project_owned", manifest)

    def test_update_replaces_missing_modified_and_obsolete_reconstructable_files(self) -> None:
        self.assert_ok(self.adopt("install"))
        routing = self.project / ".ai-workflow/routing.md"
        expected = routing.read_bytes()
        routing.write_bytes(b"locally drifted framework bytes\n")
        (self.project / ".ai-workflow/README.md").unlink()
        obsolete = self.project / ".ai-workflow/state/README.md"
        obsolete.parent.mkdir()
        obsolete.write_text("historical framework file\n")
        self.assert_ok(self.adopt("update"))
        self.assertEqual(routing.read_bytes(), expected)
        self.assertTrue((self.project / ".ai-workflow/README.md").is_file())
        self.assertFalse(obsolete.exists())

    def test_deleted_framework_directory_is_rebuilt_conservatively(self) -> None:
        self.assert_ok(self.adopt("install"))
        state = self.project / ".ai-workflow-state/custom.txt"
        state.write_text("durable project bytes\n")
        shutil.rmtree(self.project / ".ai-workflow")
        self.assert_ok(self.adopt("update"))
        self.assertTrue((self.project / ".ai-workflow/routing.md").is_file())
        self.assertEqual(state.read_text(), "durable project bytes\n")
        manifest = json.loads((self.project / ".ai-workflow/install-manifest.json").read_text())
        self.assertTrue(all(not details["created"] for details in manifest["external_files"].values()))

    def test_historical_absence_is_not_a_blocker_or_recreated(self) -> None:
        self.assert_ok(self.adopt("install"))
        manifest_path = self.project / ".ai-workflow/install-manifest.json"
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
        self.assertFalse((self.project / ".ai-workflow/state/README.md").exists())

    def test_arbitrary_durable_state_survives_update_remove_and_reinstall(self) -> None:
        state = self.project / ".ai-workflow-state"
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
        effort = self.project / ".ai-workflow-state/wayfinder/custom-effort"
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

    def test_legacy_active_index_is_preserved_as_inert_history(self) -> None:
        retired = self.project / ".ai-workflow-state/active.md"
        retired.parent.mkdir(parents=True)
        retired_bytes = b"# Existing project-owned file\n\nPreserve but never consult.\n"
        retired.write_bytes(retired_bytes)
        legacy = self.project / ".ai-workflow/state/active.md"
        legacy.parent.mkdir(parents=True)
        original = b"# Historical active pointer\n\nUnique user context.\n"
        legacy.write_bytes(original)

        self.assert_ok(self.adopt("install"))

        self.assertFalse(legacy.exists())
        self.assertEqual(retired.read_bytes(), retired_bytes)
        preserved = self.project / ".ai-workflow-state/legacy-active.md"
        self.assertEqual(preserved.read_bytes(), original)

        for command in ("update", "remove", "install"):
            with self.subTest(command=command):
                self.assert_ok(self.adopt(command))
                self.assertEqual(retired.read_bytes(), retired_bytes)
                self.assertEqual(preserved.read_bytes(), original)

    def test_known_legacy_state_moves_and_conflict_preserves_both(self) -> None:
        self.assert_ok(self.adopt("install"))
        legacy = self.project / ".ai-workflow/project-profile.md"
        legacy.write_text("legacy profile\n")
        result = self.adopt("update")
        self.assert_ok(result)
        self.assertEqual((self.project / ".ai-workflow-state/project-profile.md").read_text(), "legacy profile\n")
        self.assertFalse(legacy.exists())

        legacy.write_text("legacy profile\n")
        self.assert_ok(self.adopt("update"))
        self.assertFalse(legacy.exists())
        self.assertEqual((self.project / ".ai-workflow-state/project-profile.md").read_text(), "legacy profile\n")

        legacy = self.project / ".ai-workflow/project-profile.md"
        legacy.write_text("different legacy bytes\n")
        before_framework = tree_snapshot(self.project / ".ai-workflow")
        result = self.adopt("update")
        self.assertEqual(result.returncode, 2)
        self.assertIn("conflicting legacy and canonical", result.stderr)
        self.assertEqual(legacy.read_text(), "different legacy bytes\n")
        self.assertEqual(
            (self.project / ".ai-workflow-state/project-profile.md").read_text(),
            "legacy profile\n",
        )
        self.assertEqual(tree_snapshot(self.project / ".ai-workflow"), before_framework)

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
        routing = self.project / ".ai-workflow/routing.md"
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
        self.assertFalse((self.project / ".ai-workflow").exists())
        self.assertFalse((self.project / ".ai-workflow-state").exists())

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
        (self.project / ".ai-workflow").symlink_to(outside, target_is_directory=True)
        result = self.adopt("update")
        self.assertEqual(result.returncode, 2)
        self.assertEqual((outside / "sentinel").read_text(), "safe\n")

        (self.project / ".ai-workflow").unlink()
        (self.project / ".ai-workflow-state").symlink_to(outside, target_is_directory=True)
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
        self.assertFalse((self.project / ".ai-workflow-state/project-profile.md").exists())
        self.assertFalse((self.project / ".ai-workflow-state/active.md").exists())
        (self.project / ".ai-workflow/routing.md").unlink()
        result = self.adopt("status")
        self.assertEqual(result.returncode, 1)
        self.assertIn("repairable", result.stdout)

    def test_optional_provider_failure_does_not_fail_core_install(self) -> None:
        fake_bin = Path(self.temporary.name) / "bin"
        fake_bin.mkdir()
        gh = fake_bin / "gh"
        gh.write_text("#!/bin/sh\nexit 23\n")
        gh.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = str(fake_bin)
        result = run_script(LIFECYCLE, "install", self.project, env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.project / ".ai-workflow/routing.md").is_file())
        self.assertIn("Optional provider setup did not complete", result.stderr)

    def test_optional_provider_failure_during_remove_reports_truthfully(self) -> None:
        self.assert_ok(self.adopt("install"))
        provider_file = self.project / ".agents/skills/wayfinder/personal.txt"
        provider_file.parent.mkdir(parents=True)
        provider_file.write_text("preserve provider bytes\n")

        package_copy = self.copy_package("remove-provider-failure")
        declaration = package_copy / "payload/ai-workflow/providers.json"
        declaration.write_text("{}\n", encoding="utf-8")
        result = run_script(package_copy / "scripts/lifecycle.py", "remove", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Core removal will continue; provider directories remain preserved", result.stderr)
        self.assertNotIn("core router and local workflows remain usable", result.stderr)
        self.assertFalse((self.project / ".ai-workflow").exists())
        self.assertEqual(provider_file.read_text(), "preserve provider bytes\n")

    def test_existing_provider_content_is_preserved(self) -> None:
        directory = self.project / ".agents/skills/wayfinder"
        directory.mkdir(parents=True)
        (directory / "personal.txt").write_text("do not touch\n")
        fake_bin = Path(self.temporary.name) / "bin"
        fake_bin.mkdir()
        gh = fake_bin / "gh"
        gh.write_text("#!/bin/sh\nexit 1\n")
        gh.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = str(fake_bin)
        result = run_script(PROVIDERS, "install", self.project, env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((directory / "personal.txt").read_text(), "do not touch\n")

    def test_fresh_lifecycle_projects_every_declared_provider_skill(self) -> None:
        fake_bin = self.fake_gh_provider_installer("complete-provider-bin")
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"

        result = run_script(LIFECYCLE, "install", self.project, env=env)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in self.declared_provider_names():
            with self.subTest(skill=name):
                self.assertTrue((self.project / ".agents/skills" / name / "SKILL.md").is_file())

    def test_update_completes_an_existing_partial_provider_projection(self) -> None:
        for name in {"setup-matt-pocock-skills", "wayfinder", "teach", "research"}:
            self.write_fake_provider_skill(self.project, name)
        fake_bin = self.fake_gh_provider_installer("partial-update-bin")
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"

        result = run_script(LIFECYCLE, "update", self.project, env=env)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in self.declared_provider_names():
            with self.subTest(skill=name):
                self.assertTrue((self.project / ".agents/skills" / name / "SKILL.md").is_file())

    def test_failed_provider_staging_does_not_commit_a_partial_prefix(self) -> None:
        fake_bin = self.fake_gh_provider_installer("failed-stage-bin", fail_skill="grilling")
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"

        result = run_script(PROVIDERS, "install", self.project, env=env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for name in self.declared_provider_names():
            self.assertFalse((self.project / ".agents/skills" / name).exists())

    def test_provider_staging_rejects_a_successful_command_that_omits_a_declared_skill(self) -> None:
        fake_bin = self.fake_gh_provider_installer("omitted-skill-bin", omit_skill="codebase-design")
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"

        result = run_script(PROVIDERS, "install", self.project, env=env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("codebase-design", result.stderr)
        for name in self.declared_provider_names():
            self.assertFalse((self.project / ".agents/skills" / name).exists())

    def test_provider_staging_rejects_missing_copilot_user_only_metadata(self) -> None:
        fake_bin = self.fake_gh_provider_installer(
            "missing-copilot-policy-bin",
            missing_copilot_policy_skill="teach",
        )
        self.assert_provider_staging_rejected(
            fake_bin,
            "teach lacks GitHub Copilot user-only metadata",
        )

    def test_provider_staging_rejects_missing_codex_user_only_metadata(self) -> None:
        fake_bin = self.fake_gh_provider_installer(
            "missing-codex-policy-bin",
            missing_codex_policy_skill="teach",
        )
        self.assert_provider_staging_rejected(
            fake_bin,
            "teach lacks Codex user-only metadata",
        )

    def test_provider_status_is_nonzero_while_declared_projection_is_incomplete(self) -> None:
        result = run_script(PROVIDERS, "status", self.project)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("14 missing", result.stdout)

    def test_lifecycle_status_reports_incomplete_provider_projection_without_failing_core(self) -> None:
        self.assert_ok(self.adopt("install"))

        result = run_script(LIFECYCLE, "status", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Agentic Workflow: healthy", result.stdout)
        self.assertIn("Optional provider projection is incomplete", result.stderr)

    def test_wayfinder_adapter_applies_after_fresh_provider_install(self) -> None:
        package_copy = self.copy_package("fresh-wayfinder-adapter")
        self.keep_only_wayfinder_provider(package_copy)
        fake_bin = self.fake_gh_provider_installer("fresh-provider-bin")
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"

        result = run_script(package_copy / "scripts/providers.py", "install", self.project, env=env)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("verified Agentic Workflow adapter for wayfinder", result.stdout)
        skill_text = (self.project / ".agents/skills/wayfinder/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(skill_text.count(WAYFINDER_ADAPTER_BEGIN), 1)
        self.assertEqual(skill_text.count(WAYFINDER_ADAPTER_END), 1)
        self.assertIn("The only canonical local representation", skill_text)
        self.assertIn("Never force U# -> D# -> T# as ceremony", skill_text)
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

    def test_wayfinder_adapter_updates_existing_provider_idempotently_and_preserves_other_bytes(self) -> None:
        package_copy = self.copy_package("existing-wayfinder-adapter")
        self.keep_only_wayfinder_provider(package_copy)
        self.write_upstream_wayfinder_metadata(self.project)
        personal = self.project / ".agents/skills/wayfinder/personal.txt"
        personal.write_text("preserve this project file\n", encoding="utf-8")

        first = run_script(package_copy / "scripts/providers.py", "install", self.project)
        second = run_script(package_copy / "scripts/providers.py", "install", self.project)

        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("applied Agentic Workflow adapter for wayfinder", first.stdout)
        self.assertIn("verified Agentic Workflow adapter for wayfinder", second.stdout)
        self.assertEqual(personal.read_text(encoding="utf-8"), "preserve this project file\n")
        adapted = (self.project / ".agents/skills/wayfinder/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(adapted.count(WAYFINDER_ADAPTER_BEGIN), 1)
        self.assertEqual(adapted.count(WAYFINDER_ADAPTER_END), 1)

    def test_wayfinder_adapter_upgrades_the_recognized_read_only_loading_rule(self) -> None:
        package_copy = self.copy_package("wayfinder-adapter-loading-upgrade")
        self.keep_only_wayfinder_provider(package_copy)
        self.write_upstream_wayfinder_metadata(self.project)
        first = run_script(package_copy / "scripts/providers.py", "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

        skill = self.project / ".agents/skills/wayfinder/SKILL.md"
        current = (
            "that contract when Wayfinder is selected. Before an authorized durable-state\n"
            "write, also read `.ai-workflow/contracts/durable-state.md`. These rules override\n"
            "incompatible tracker-specific mechanics below. If the local contract is absent,\n"
            "ignore this section and use the unchanged upstream method normally.\n"
        )
        legacy = (
            "that contract and `.ai-workflow/contracts/durable-state.md` before local state\n"
            "work. These rules override incompatible tracker-specific mechanics below. If\n"
            "the local contract is absent, ignore this section and use the unchanged\n"
            "upstream method normally.\n"
        )
        skill.write_text(skill.read_text(encoding="utf-8").replace(current, legacy, 1), encoding="utf-8")

        status = run_script(package_copy / "scripts/providers.py", "status", self.project)
        upgrade = run_script(package_copy / "scripts/providers.py", "install", self.project)

        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("0 ready, 1 pending, 0 incompatible", status.stdout)
        self.assertEqual(upgrade.returncode, 0, upgrade.stdout + upgrade.stderr)
        self.assertIn("applied Agentic Workflow adapter for wayfinder", upgrade.stdout)
        upgraded = skill.read_text(encoding="utf-8")
        self.assertIn(current, upgraded)
        self.assertNotIn(legacy, upgraded)

    def test_wayfinder_adapter_rejects_unexpected_metadata_without_partial_write(self) -> None:
        package_copy = self.copy_package("incompatible-wayfinder-adapter")
        self.keep_only_wayfinder_provider(package_copy)
        self.write_upstream_wayfinder_metadata(self.project)
        skill = self.project / ".agents/skills/wayfinder/SKILL.md"
        openai = self.project / ".agents/skills/wayfinder/agents/openai.yaml"
        openai.write_text("policy:\n  allow_implicit_invocation: ask\n", encoding="utf-8")
        before_skill = skill.read_bytes()
        before_openai = openai.read_bytes()

        result = run_script(package_copy / "scripts/providers.py", "install", self.project)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unexpected invocation metadata", result.stderr)
        self.assertEqual(skill.read_bytes(), before_skill)
        self.assertEqual(openai.read_bytes(), before_openai)

    def test_wayfinder_adapter_rejects_a_modified_method_body_without_partial_write(self) -> None:
        package_copy = self.copy_package("modified-wayfinder-method")
        self.keep_only_wayfinder_provider(package_copy)
        self.write_upstream_wayfinder_metadata(self.project)
        skill = self.project / ".agents/skills/wayfinder/SKILL.md"
        openai = self.project / ".agents/skills/wayfinder/agents/openai.yaml"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace("A loose idea has arrived", "A changed idea has arrived", 1),
            encoding="utf-8",
        )
        before_skill = skill.read_bytes()
        before_openai = openai.read_bytes()

        result = run_script(package_copy / "scripts/providers.py", "install", self.project)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unexpected pinned method body", result.stderr)
        self.assertEqual(skill.read_bytes(), before_skill)
        self.assertEqual(openai.read_bytes(), before_openai)

    def test_provider_status_reports_pending_wayfinder_adapter_without_writing(self) -> None:
        package_copy = self.copy_package("pending-wayfinder-adapter")
        self.keep_only_wayfinder_provider(package_copy)
        self.write_upstream_wayfinder_metadata(self.project)
        before = tree_snapshot(self.project / ".agents/skills/wayfinder")

        result = run_script(package_copy / "scripts/providers.py", "status", self.project)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("0 ready, 1 pending, 0 incompatible", result.stdout)
        self.assertEqual(tree_snapshot(self.project / ".agents/skills/wayfinder"), before)

    def test_provider_remove_distinguishes_and_preserves_adapted_wayfinder(self) -> None:
        package_copy = self.copy_package("remove-wayfinder-adapter")
        self.keep_only_wayfinder_provider(package_copy)
        self.write_upstream_wayfinder_metadata(self.project)
        install = run_script(package_copy / "scripts/providers.py", "install", self.project)
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        before = tree_snapshot(self.project / ".agents/skills/wayfinder")

        result = run_script(package_copy / "scripts/providers.py", "remove", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("wayfinder (ready)", result.stdout)
        self.assertEqual(tree_snapshot(self.project / ".agents/skills/wayfinder"), before)

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

        source = package_copy / "payload/ai-workflow/README.md"
        source.write_text(
            source.read_text(encoding="utf-8") + "\nCurrent package bytes are authoritative.\n",
            encoding="utf-8",
        )

        runtime = run_script(package_copy / "scripts/adopt.py", "install", self.project)
        self.assertEqual(runtime.returncode, 0, runtime.stdout + runtime.stderr)
        self.assertEqual(
            (self.project / ".ai-workflow/README.md").read_bytes(),
            source.read_bytes(),
        )

        verify = run_script(package_copy / "scripts/verify_package.py")
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

        unmapped = package_copy / "payload/ai-workflow/contracts/new-contract.md"
        unmapped.write_text("# Newly packaged contract\n", encoding="utf-8")
        verify = run_script(package_copy / "scripts/verify_package.py")
        self.assertEqual(verify.returncode, 1)
        self.assertIn("manifest is stale", verify.stderr)

    def test_verifier_rejects_incomplete_provider_declarations(self) -> None:
        package_copy = self.copy_package("provider-declaration")
        declaration = package_copy / "payload/ai-workflow/providers.json"
        valid = json.loads(declaration.read_text(encoding="utf-8"))

        cases = (
            ("empty skill name", "name", "", "invalid provider skill name"),
            ("missing skill path", "path", None, "needs a path"),
            ("incomplete invocation hosts", "invocation", {}, "invocation hosts differ"),
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

    def test_verifier_requires_the_wayfinder_local_state_adapter(self) -> None:
        package_copy = self.copy_package("wayfinder-adapter-declaration")
        declaration = package_copy / "payload/ai-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        wayfinder = next(item for item in raw["provider"]["skills"] if item["name"] == "wayfinder")
        wayfinder.pop("agentic_workflow_adapter")
        wayfinder["invocation"]["codex"] = "user-only"
        wayfinder["invocation"]["github-copilot"] = "user-only"
        declaration.write_text(json.dumps(raw), encoding="utf-8")

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("Wayfinder must declare", verify.stderr)

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

    def package_archive(self) -> bytes:
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w:gz") as archive:
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

    def test_bootstrap_rejects_a_symlink_project_root_before_download(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            link = root / "project-link"
            link.symlink_to(project, target_is_directory=True)
            with self.assertRaises(self.bootstrap.BootstrapError):
                self.bootstrap.main(["status", str(link), "--archive-url", "unused"])

    def test_local_archive_bootstrap_installs_core_when_provider_is_unavailable(self) -> None:
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
            self.assertTrue((project / ".ai-workflow/routing.md").is_file())
            self.assertTrue((project / ".ai-workflow-state").is_dir())

    def test_minimum_runtime_files_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "agentic-workflow"
            package.mkdir()
            with self.assertRaises(self.bootstrap.BootstrapError):
                self.bootstrap.validate_runtime_package(package)


if __name__ == "__main__":
    unittest.main()
