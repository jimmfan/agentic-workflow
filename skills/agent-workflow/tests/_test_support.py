from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
CLI = PACKAGE_ROOT / "cli.py"
ADOPT = PACKAGE_ROOT / "scripts" / "adopt.py"
BOOTSTRAP = PACKAGE_ROOT / "scripts" / "bootstrap.py"
LIFECYCLE = PACKAGE_ROOT / "scripts" / "lifecycle.py"
MANAGED_BEGIN = b"<!-- agent-workflow:managed-begin -->\n"
MANAGED_END = b"<!-- agent-workflow:managed-end -->\n"


def run_script(
    script: Path,
    *arguments: object,
    env: dict[str, str] | None = None,
    encoding: str = "utf-8",
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *(str(item) for item in arguments)],
        text=True,
        capture_output=True,
        encoding=encoding,
        errors="strict",
        env=env,
        cwd=cwd,
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


class ProjectTestCase(unittest.TestCase):
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
        repository_copy = Path(self.temporary.name) / name
        package_copy = repository_copy / "skills" / "agent-workflow"
        package_copy.parent.mkdir(parents=True)
        shutil.copytree(PACKAGE_ROOT, package_copy)
        for source_name in (
            ".agent-workflow",
            ".agents",
            "architecture-decisions",
            "docs",
            "AGENTS.md",
            "CLAUDE.md",
            "CONTEXT.md",
            "LICENSE",
            "README.md",
        ):
            source = REPOSITORY_ROOT / source_name
            target = repository_copy / source_name
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        # Durable state is deliberately not copied, but a healthy installed
        # repository has the framework-independent durable root available.
        (repository_copy / ".agent-wayfinder").mkdir()
        return package_copy
