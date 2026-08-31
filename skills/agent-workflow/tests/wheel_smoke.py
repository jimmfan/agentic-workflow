from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from _test_support import REPOSITORY_ROOT, initialize_repository, run_git


class BuiltWheelSmokeTests(unittest.TestCase):
    def test_installed_cli_runs_against_a_clean_git_project(self) -> None:
        def run(*command: object, cwd: Path | None = None) -> None:
            subprocess.run([str(item) for item in command], cwd=cwd, check=True)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            for name in ("LICENSE", "README.md", "pyproject.toml"):
                shutil.copy2(REPOSITORY_ROOT / name, source / name)
            package = source / "skills/agent-workflow"
            package.parent.mkdir()
            shutil.copytree(
                REPOSITORY_ROOT / "skills/agent-workflow",
                package,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )

            wheelhouse = root / "wheelhouse"
            environment = os.environ.copy()
            environment["PIP_CACHE_DIR"] = str(root / "pip-cache")
            command = [
                sys.executable, "-m", "pip", "wheel", "--no-deps",
                "--wheel-dir", str(wheelhouse), str(source),
            ]
            subprocess.run(command, cwd=source, env=environment, check=True)
            wheel = next(wheelhouse.glob("agent_workflow-*.whl"))
            virtual_environment = root / "venv"
            run(sys.executable, "-m", "venv", virtual_environment)
            python = virtual_environment / "bin/python"
            cli = virtual_environment / "bin/agent-workflow"
            run(python, "-m", "pip", "install", "--no-index", "--no-deps", wheel)
            extracted = root / "extracted"
            with zipfile.ZipFile(wheel) as built:
                built.extractall(extracted)
            archive = root / "wheel-package.tar.gz"
            with tarfile.open(archive, "w:gz") as built:
                built.add(extracted / "agent_workflow",
                          arcname="source/skills/agent-workflow")
            project = root / "project"
            project.mkdir()
            initialize_repository(project)
            self.assertEqual(run_git(project, "status", "--porcelain").stdout, "")
            run(cli, "install", project, "--archive-url", archive.as_uri())
            self.assertTrue((project / ".agent-workflow/routing.md").is_file())
            self.assertTrue((project / ".agents/skills/research/SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
