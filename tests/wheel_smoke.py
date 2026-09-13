from __future__ import annotations

import shutil
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from _test_support import REPOSITORY_ROOT, curated_skill_names


def copy_source_snapshot(repository: Path, destination: Path) -> None:
    """Copy current tracked and unignored source bytes, including pending dot-files."""
    paths = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=repository,
        capture_output=True,
        check=True,
    ).stdout.split(b"\0")
    destination.mkdir()
    for raw in sorted(set(paths)):
        if not raw:
            continue
        relative = Path(os.fsdecode(raw))
        if any(
            part in {".git", ".venv", "__pycache__", "build", "dist", ".ruff_cache"}
            or part.endswith((".egg-info", ".pyc"))
            for part in relative.parts
        ):
            continue
        source = repository / relative
        if not source.exists() and not source.is_symlink():
            continue  # A pending deletion is part of the source under test.
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            target.symlink_to(os.readlink(source))
        else:
            shutil.copy2(source, target)


class BuiltWheelSmokeTests(unittest.TestCase):
    def test_locked_run_rejects_pending_dependency_drift_without_rewriting_lock(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            copy_source_snapshot(REPOSITORY_ROOT, source)
            project = source / "pyproject.toml"
            lock = source / "uv.lock"
            before = lock.read_bytes()
            command = [
                "uv",
                "run",
                "--locked",
                "--cache-dir",
                str(Path(temporary) / "cache"),
                "--python",
                sys.executable,
            ]
            probe = ["python", "-c", "print('locked command ran')"]
            # Prepare our own cache, including build metadata, rather than relying
            # on the host cache. The unchanged lock must permit real execution.
            baseline = subprocess.run(
                [*command, *probe], cwd=source, capture_output=True, text=True
            )
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            self.assertEqual(baseline.stdout.strip(), "locked command ran")
            self.assertEqual(lock.read_bytes(), before)
            # Removing a dependency changes the lock without requiring uncached
            # registry metadata for a new requirement during the offline check.
            project.write_text(project.read_text().replace('    "ruff>=0.16.4",\n', ""))
            result = subprocess.run(
                [*command, "--offline", *probe],
                cwd=source,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("lockfile", result.stderr.lower())
            self.assertIn("--locked", result.stderr)
            self.assertNotIn("locked command ran", result.stdout)
            self.assertEqual(lock.read_bytes(), before)

    def test_installed_cli_runs_local_archive_against_a_plain_project(self) -> None:
        def run(*command: object, cwd: Path | None = None) -> None:
            subprocess.run([str(item) for item in command], cwd=cwd, check=True)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            copy_source_snapshot(REPOSITORY_ROOT, source)
            for relative in (
                ".agent-workflow/routing.md",
                ".agents/skills/wayfinder/SKILL.md",
                "tests/test_bootstrap.py",
                "evals/routing_smoke.py",
            ):
                self.assertEqual(
                    (source / relative).read_bytes(),
                    (REPOSITORY_ROOT / relative).read_bytes(),
                )
            wheelhouse = root / "wheelhouse"
            run(
                "uv",
                "build",
                "--sdist",
                "--python",
                sys.executable,
                "--out-dir",
                wheelhouse,
                source,
                cwd=root,
            )
            sdist = next(wheelhouse.glob("agent_workflow-*.tar.gz"))
            with tarfile.open(sdist, "r:gz") as built:
                versions = [
                    member for member in built if Path(member.name).name == "VERSION"
                ]
                self.assertEqual(len(versions), 1)
                self.assertEqual(len(Path(versions[0].name).parts), 2)
                with built.extractfile(versions[0]) as version:
                    self.assertEqual(version.read(), (source / "VERSION").read_bytes())
                archive_root = Path(versions[0].name).parent
                for relative in ("pyproject.toml", "README.md", "LICENSE"):
                    with built.extractfile(
                        (archive_root / relative).as_posix()
                    ) as member:
                        self.assertEqual(
                            member.read(), (source / relative).read_bytes()
                        )
            run(
                "uv",
                "build",
                "--wheel",
                "--python",
                sys.executable,
                "--out-dir",
                wheelhouse,
                sdist,
                cwd=root,
            )
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
            run(
                python,
                "-I",
                "-c",
                "import agent_workflow; from pathlib import Path; assert Path(agent_workflow.__file__).resolve().is_relative_to(Path("
                + repr(str(virtual_environment))
                + ").resolve())",
                cwd=root,
            )
            subprocess.run(
                [str(cli), "--help"],
                cwd=root,
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
                        or name.startswith(("evals/", "tests/", ".project-efforts/"))
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
                license_files = [
                    name
                    for name in built.namelist()
                    if ".dist-info/" in name and Path(name).name == "LICENSE"
                ]
                self.assertEqual(len(license_files), 1)
                self.assertEqual(
                    built.read(license_files[0]), (source / "LICENSE").read_bytes()
                )
            archive = root / "repository-snapshot.tar.gz"
            with tarfile.open(archive, "w:gz") as built:
                built.add(source / "VERSION", arcname="source/VERSION")
                for name in ("agent_workflow", ".agent-workflow", ".agents/skills"):
                    for path in sorted((source / name).rglob("*")):
                        if path.is_file() and "__pycache__" not in path.parts:
                            built.add(
                                path,
                                arcname="source/" + path.relative_to(source).as_posix(),
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
            durable = project / ".project-efforts/user/map.md"
            for action in ("install", "update", "status"):
                if action == "update":
                    durable.parent.mkdir(parents=True)
                    durable.write_bytes(b"# Consumer-owned effort\r\n")
                run(cli, action, project, "--archive-url", archive.as_uri(), cwd=root)
                if action == "install":
                    self.assertFalse((project / ".project-efforts").exists())
                else:
                    self.assertEqual(
                        durable.read_bytes(), b"# Consumer-owned effort\r\n"
                    )
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
                    curated_skill_names(project),
                    curated_skill_names() | {"project-local"},
                )
                for name in ("AGENTS.md", "CLAUDE.md"):
                    content = (project / name).read_bytes()
                    self.assertEqual(
                        content.count(b"<!-- agent-workflow:managed-begin -->"), 1
                    )
                    self.assertTrue(content.endswith(project_bytes))
            run(cli, "remove", project, "--archive-url", archive.as_uri(), cwd=root)
            self.assertFalse((project / ".agent-workflow").exists())
            self.assertEqual(durable.read_bytes(), b"# Consumer-owned effort\r\n")
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
