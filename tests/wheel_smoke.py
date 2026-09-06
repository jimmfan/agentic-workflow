from __future__ import annotations

import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from _test_support import REPOSITORY_ROOT


class BuiltWheelSmokeTests(unittest.TestCase):
    def test_installed_cli_runs_local_archive_against_a_plain_project(self) -> None:
        def run(*command: object, cwd: Path | None = None) -> None:
            subprocess.run([str(item) for item in command], cwd=cwd, check=True)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            for name in ("LICENSE", "README.md", "pyproject.toml", "VERSION"):
                shutil.copy2(REPOSITORY_ROOT / name, source / name)
            package = source / "agent_workflow"
            shutil.copytree(
                REPOSITORY_ROOT / "agent_workflow",
                package,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            shutil.copytree(
                REPOSITORY_ROOT / "evals/token_forensics",
                source / "evals/token_forensics",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )

            wheelhouse = root / "wheelhouse"
            run("uv", "build", "--sdist", "--out-dir", wheelhouse, source)
            sdist = next(wheelhouse.glob("agent_workflow-*.tar.gz"))
            with tarfile.open(sdist, "r:gz") as built:
                versions = [
                    member for member in built if Path(member.name).name == "VERSION"
                ]
                self.assertEqual(len(versions), 1)
                self.assertEqual(len(Path(versions[0].name).parts), 2)
                with built.extractfile(versions[0]) as version:
                    self.assertEqual(version.read(), (source / "VERSION").read_bytes())
            run("uv", "build", "--wheel", "--out-dir", wheelhouse, sdist)
            wheel = next(wheelhouse.glob("agent_workflow-*.whl"))
            virtual_environment = root / "venv"
            run("uv", "venv", "--python", sys.executable, virtual_environment)
            python = virtual_environment / "bin/python"
            cli = virtual_environment / "bin/agent-workflow"
            run(
                "uv",
                "pip",
                "install",
                "--python",
                python,
                "--no-index",
                "--no-deps",
                wheel,
            )
            subprocess.run(
                [str(cli), "--help"],
                capture_output=True,
                text=True,
                check=True,
            )
            with zipfile.ZipFile(wheel) as built:
                package_files = {
                    name
                    for name in built.namelist()
                    if name.startswith("agent_workflow/")
                }
                self.assertEqual(
                    package_files,
                    {
                        "agent_workflow/__init__.py",
                        "agent_workflow/cli.py",
                        "agent_workflow/bootstrap.py",
                        "agent_workflow/lifecycle.py",
                        "agent_workflow/verify_package.py",
                        "agent_workflow/install/AGENTS.md.template",
                        "agent_workflow/install/CLAUDE.md.template",
                        "agent_workflow/install/manifest.json",
                    },
                )
                self.assertFalse(
                    any(
                        ".agents/" in name
                        or ".agent-workflow/" in name
                        or "token_forensics/" in name
                        or name.startswith("evals/")
                        for name in built.namelist()
                    )
                )
                metadata = built.read(
                    next(
                        name
                        for name in built.namelist()
                        if name.endswith(".dist-info/METADATA")
                    )
                ).decode()
                self.assertIn(
                    "Version: " + (source / "VERSION").read_text().strip(), metadata
                )
            archive = root / "repository-snapshot.tar.gz"
            with tarfile.open(archive, "w:gz") as built:
                built.add(REPOSITORY_ROOT / "VERSION", arcname="source/VERSION")
                for name in ("agent_workflow", ".agent-workflow", ".agents/skills"):
                    for path in sorted((REPOSITORY_ROOT / name).rglob("*")):
                        if path.is_file() and "__pycache__" not in path.parts:
                            built.add(
                                path,
                                arcname="source/"
                                + path.relative_to(REPOSITORY_ROOT).as_posix(),
                            )
            project = root / "project"
            project.mkdir()
            (project / "VERSION").write_bytes(b"project-owned version\n")
            context_bytes = b"# Project domain\r\n**Order**: A purchase.\r\n"
            (project / "CONTEXT.md").write_bytes(context_bytes)
            project_bytes = b"# Project instructions\r\nKeep these bytes.\r\n"
            for name in ("AGENTS.md", "CLAUDE.md"):
                (project / name).write_bytes(project_bytes)
            unrelated = project / ".agents/skills/project-local/SKILL.md"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_bytes(b"local skill\n")
            for action in ("install", "update", "status"):
                run(cli, action, project, "--archive-url", archive.as_uri())
                self.assertFalse((project / ".project-efforts").exists())
                self.assertEqual(
                    (project / "VERSION").read_bytes(), b"project-owned version\n"
                )
                self.assertEqual(unrelated.read_bytes(), b"local skill\n")
                self.assertEqual((project / "CONTEXT.md").read_bytes(), context_bytes)
                for name in (
                    "README.md",
                    "routing.md",
                    "terminology.md",
                    "contracts/wayfinder-state.md",
                ):
                    self.assertEqual(
                        (project / ".agent-workflow" / name).read_bytes(),
                        (REPOSITORY_ROOT / ".agent-workflow" / name).read_bytes(),
                    )
                self.assertEqual(
                    len(list((project / ".agents/skills").glob("*/SKILL.md"))), 16
                )
                for name in ("AGENTS.md", "CLAUDE.md"):
                    content = (project / name).read_bytes()
                    self.assertEqual(
                        content.count(b"<!-- agent-workflow:managed-begin -->"), 1
                    )
                    self.assertTrue(content.endswith(project_bytes))
            run(cli, "remove", project, "--archive-url", archive.as_uri())
            self.assertFalse((project / ".agent-workflow").exists())
            self.assertFalse((project / ".project-efforts").exists())
            self.assertEqual((project / "CONTEXT.md").read_bytes(), context_bytes)
            self.assertEqual(
                (project / "VERSION").read_bytes(), b"project-owned version\n"
            )
            self.assertEqual(
                list((project / ".agents/skills").iterdir()), [unrelated.parent]
            )
            for name in ("AGENTS.md", "CLAUDE.md"):
                self.assertEqual((project / name).read_bytes(), project_bytes)


if __name__ == "__main__":
    unittest.main()
