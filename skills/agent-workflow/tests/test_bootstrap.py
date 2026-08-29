from __future__ import annotations

import io
import json
import os
from pathlib import Path
import tempfile
import tarfile
import unittest

from _test_support import BOOTSTRAP, CLI, PACKAGE_ROOT, load_module, run_script


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
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(self.bootstrap.BootstrapError):
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
            ):
                with self.assertRaises(self.bootstrap.BootstrapError):
                    self.bootstrap.extract_package(
                        self.archive(entries), Path(temporary)
                    )

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
            (f"root/skills/agent-workflow/data/item-{index}.txt", b"x", "file")
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

    def test_local_archive_bootstrap_installs_core_and_providers_without_external_tools(
        self,
    ) -> None:
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
            self.assertTrue((project / ".agent-wayfinder").is_dir())
            declaration = json.loads(
                (PACKAGE_ROOT / "payload/agent-workflow/providers.json").read_text(
                    encoding="utf-8"
                )
            )
            names = {item["name"] for item in declaration["provider"]["skills"]}
            for name in names:
                with self.subTest(skill=name):
                    self.assertTrue(
                        (project / ".agents/skills" / name / "SKILL.md").is_file()
                    )
            self.assertNotIn("GitHub CLI", result.stderr)

    def test_cli_exposes_help_and_delegates_every_lifecycle_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
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

            for command in ("update", "status"):
                with self.subTest(command=command):
                    result = run_script(
                        CLI, command, project, "--archive-url", archive_url
                    )
                    self.assertEqual(
                        result.returncode, 0, result.stdout + result.stderr
                    )

            state = project / ".agent-wayfinder"
            sentinel = state / "keep.txt"
            sentinel.write_text("project-owned\n", encoding="utf-8")
            result = run_script(CLI, "remove", project, "--archive-url", archive_url)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "project-owned\n")
            self.assertFalse((project / ".agent-workflow").exists())

    def test_minimum_runtime_files_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "agent-workflow"
            package.mkdir()
            with self.assertRaises(self.bootstrap.BootstrapError):
                self.bootstrap.validate_runtime_package(package)


if __name__ == "__main__":
    unittest.main()
