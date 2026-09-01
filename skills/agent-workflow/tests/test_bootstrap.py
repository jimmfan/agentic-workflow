from __future__ import annotations

import io
import os
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _test_support import (
    BOOTSTRAP,
    CLI,
    PACKAGE_ROOT,
    commit_all,
    initialize_repository,
    load_module,
    run_script,
)


class BootstrapSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bootstrap = load_module(
            "agent_workflow_bootstrap", PACKAGE_ROOT / "scripts/bootstrap.py"
        )

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
                if (
                    not path.is_file()
                    or path.is_symlink()
                    or "__pycache__" in path.parts
                ):
                    continue
                relative = path.relative_to(PACKAGE_ROOT).as_posix()
                data = path.read_bytes()
                member = tarfile.TarInfo(f"source/skills/agent-workflow/{relative}")
                member.mode = 0o644
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
        return output.getvalue()

    def test_corrupt_archive_is_rejected(self) -> None:
        with (
            tempfile.TemporaryDirectory() as temporary,
            self.assertRaises(self.bootstrap.BootstrapError),
        ):
            self.bootstrap.extract_package(b"not a tar archive", Path(temporary))

    def test_traversal_and_link_entries_are_rejected(self) -> None:
        cases = [
            [("root/skills/agent-workflow/../escape", b"bad", "file")],
            [("root/skills/agent-workflow/scripts/lifecycle.py", b"", "symlink")],
            [("root/skills/agent-workflow/scripts/lifecycle.py", b"", "special")],
        ]
        for entries in cases:
            with (
                self.subTest(entries=entries),
                tempfile.TemporaryDirectory() as temporary,
                self.assertRaises(self.bootstrap.BootstrapError),
            ):
                self.bootstrap.extract_package(self.archive(entries), Path(temporary))

    def test_unrelated_repository_entries_do_not_exhaust_package_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            initialize_repository(project)
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
            (f"root/skills/agent-workflow/data/item-{index}.txt", b"x", "file")
            for index in range(self.bootstrap.MAX_PACKAGE_MEMBERS + 1)
        ]

        with (
            tempfile.TemporaryDirectory() as temporary,
            self.assertRaisesRegex(
                self.bootstrap.BootstrapError,
                f"package contains more than {self.bootstrap.MAX_PACKAGE_MEMBERS} entries",
            ),
        ):
            self.bootstrap.extract_package(self.archive(entries), Path(temporary))

    def test_whole_archive_parsing_ceiling_is_retained(self) -> None:
        entries = [
            (f"root/unrelated/item-{index}.txt", b"", "file")
            for index in range(self.bootstrap.MAX_ARCHIVE_MEMBERS + 1)
        ]

        with (
            tempfile.TemporaryDirectory() as temporary,
            self.assertRaisesRegex(
                self.bootstrap.BootstrapError,
                f"source archive contains more than {self.bootstrap.MAX_ARCHIVE_MEMBERS} entries",
            ),
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

    def test_local_archive_bootstrap_installs_all_direct_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            state = project / ".agent-wayfinder/keep.txt"
            state.parent.mkdir()
            state.write_text("project-owned\n", encoding="utf-8")
            initialize_repository(project)
            archive = root / "package.tar.gz"
            archive.write_bytes(self.package_archive())
            result = run_script(
                BOOTSTRAP,
                "install",
                project,
                "--archive-url",
                archive.as_uri(),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / ".agent-workflow/routing.md").is_file())
            self.assertEqual(state.read_text(encoding="utf-8"), "project-owned\n")
            self.assertFalse(
                (project / ".agent-workflow/install-manifest.json").exists()
            )
            payload = PACKAGE_ROOT / "payload/skills"
            installed = project / ".agents/skills"
            self.assertEqual(
                {path.name for path in installed.iterdir() if path.is_dir()},
                {path.name for path in payload.iterdir() if path.is_dir()},
            )
            for source in payload.rglob("*"):
                if source.is_file():
                    target = installed / source.relative_to(payload)
                    with self.subTest(target=target):
                        self.assertEqual(target.read_bytes(), source.read_bytes())
            self.assertNotIn("GitHub CLI", result.stderr)

    def test_default_target_discovers_git_root_and_explicit_target_is_literal(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "package.tar.gz"
            archive.write_bytes(self.package_archive())
            archive_url = archive.as_uri()

            repository = root / "repository"
            nested = repository / "terraform/prod"
            nested.mkdir(parents=True)
            initialize_repository(repository)
            result = run_script(
                CLI,
                "install",
                "--archive-url",
                archive_url,
                cwd=nested,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((repository / ".agent-workflow/routing.md").is_file())
            self.assertFalse((nested / ".agent-workflow").exists())

            explicit_repository = root / "explicit-repository"
            explicit_nested = explicit_repository / "terraform/prod"
            explicit_nested.mkdir(parents=True)
            initialize_repository(explicit_repository)
            result = run_script(
                CLI,
                "update",
                explicit_nested,
                "--archive-url",
                archive_url,
                cwd=explicit_repository,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((explicit_nested / ".agent-workflow/routing.md").is_file())
            self.assertFalse((explicit_repository / ".agent-workflow").exists())

            plain = root / "plain"
            plain.mkdir()
            environment = os.environ.copy()
            environment["PATH"] = ""
            result = run_script(
                CLI,
                "install",
                "--archive-url",
                archive_url,
                cwd=plain,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((plain / ".agent-workflow/routing.md").is_file())

    def test_cli_exposes_help_and_delegates_every_lifecycle_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            state = project / ".agent-wayfinder/keep.txt"
            state.parent.mkdir()
            state.write_text("project-owned\n", encoding="utf-8")
            initialize_repository(project)
            archive = root / "package.tar.gz"
            archive.write_bytes(self.package_archive())
            archive_url = archive.as_uri()

            help_result = run_script(CLI, "--help")
            self.assertEqual(
                help_result.returncode, 0, help_result.stdout + help_result.stderr
            )
            self.assertIn("{install,update,status,remove}", help_result.stdout)

            install = run_script(
                CLI, "install", "--archive-url", archive_url, cwd=project
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            commit_all(project, "install agent workflow")

            for command in ("update", "status"):
                with self.subTest(command=command):
                    result = run_script(
                        CLI, command, project, "--archive-url", archive_url
                    )
                    self.assertEqual(
                        result.returncode, 0, result.stdout + result.stderr
                    )

            result = run_script(CLI, "remove", project, "--archive-url", archive_url)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(state.read_text(encoding="utf-8"), "project-owned\n")
            self.assertFalse((project / ".agent-workflow").exists())

    def test_runtime_package_requires_only_the_single_lifecycle_implementation(
        self,
    ) -> None:
        required = {
            path.as_posix()
            for path, _label in self.bootstrap.RUNTIME_PACKAGE_REQUIREMENTS
        }
        self.assertIn("scripts/lifecycle.py", required)
        self.assertNotIn("scripts/adopt.py", required)
        self.assertNotIn("scripts/legacy_transition.py", required)

    def test_default_download_uses_the_installed_package_release_tag(self) -> None:
        version = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        release_ref = f"v{version}"

        default_args = self.bootstrap.parse_args([])
        self.assertEqual(default_args.ref, release_ref)
        explicit_args = self.bootstrap.parse_args(["--ref", "main"])
        self.assertEqual(explicit_args.ref, "main")

        with mock.patch.object(
            self.bootstrap,
            "resolve_revision",
            return_value="a" * 40,
        ) as resolve_revision:
            self.bootstrap.select_source(default_args.ref, None)
            resolve_revision.assert_called_once_with(release_ref)

        with mock.patch.object(
            self.bootstrap,
            "resolve_revision",
            return_value="b" * 40,
        ) as resolve_revision:
            self.bootstrap.select_source(explicit_args.ref, None)
            resolve_revision.assert_called_once_with("main")

    def test_minimum_runtime_files_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "agent-workflow"
            package.mkdir()
            with self.assertRaises(self.bootstrap.BootstrapError):
                self.bootstrap.validate_runtime_package(package)


if __name__ == "__main__":
    unittest.main()
