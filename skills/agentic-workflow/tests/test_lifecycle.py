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
ADOPT = PACKAGE_ROOT / "scripts" / "adopt.py"
BOOTSTRAP = PACKAGE_ROOT / "scripts" / "bootstrap.py"
LIFECYCLE = PACKAGE_ROOT / "scripts" / "lifecycle.py"
PROVIDERS = PACKAGE_ROOT / "scripts" / "providers.py"
VERIFIER = PACKAGE_ROOT / "scripts" / "verify_package.py"
MANAGED_BEGIN = b"<!-- ai-workflow:managed-begin -->\n"
MANAGED_END = b"<!-- ai-workflow:managed-end -->\n"
PROJECT_BEGIN = b"\n<!-- ai-workflow:project-instructions -->\n"


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

    def test_install_creates_only_current_framework_and_empty_state_root(self) -> None:
        self.assert_ok(self.adopt("install"))
        self.assertTrue((self.project / ".ai-workflow/routing.md").is_file())
        self.assertTrue((self.project / ".ai-workflow-state").is_dir())
        self.assertEqual(list((self.project / ".ai-workflow-state").iterdir()), [])
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

    def test_stale_release_checksum_fails_verifier_but_not_runtime(self) -> None:
        package_copy = Path(self.temporary.name) / "copy" / "agentic-workflow"
        shutil.copytree(PACKAGE_ROOT, package_copy)
        manifest_path = package_copy / "payload/distribution/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        first_source = next(iter(manifest["checksums"]))
        manifest["checksums"][first_source] = "0" * 64
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        runtime = run_script(package_copy / "scripts/adopt.py", "install", self.project)
        self.assertEqual(runtime.returncode, 0, runtime.stdout + runtime.stderr)
        verify = run_script(package_copy / "scripts/verify_package.py")
        self.assertEqual(verify.returncode, 1)
        self.assertIn("manifest is stale", verify.stderr)


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
