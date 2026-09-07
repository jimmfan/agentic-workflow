"""Deterministic snapshot tests; actual isolated builds run in wheel_smoke.py."""

from pathlib import Path
import subprocess
import tempfile
import unittest

from wheel_smoke import copy_source_snapshot


class WheelSnapshotTests(unittest.TestCase):
    def test_snapshot_includes_pending_dot_sources_and_excludes_build_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "repository"
            repository.mkdir()
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            for name in (
                ".agent-workflow/routing.md",
                ".agents/skills/wayfinder/SKILL.md",
                "deleted.txt",
            ):
                path = repository / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("baseline")
            subprocess.run(["git", "-C", str(repository), "add", "."], check=True)
            (repository / ".agent-workflow/routing.md").write_bytes(
                b"pending policy\r\n"
            )
            (repository / "deleted.txt").unlink()
            (repository / "pending.py").write_bytes(b"pending new source\n")
            (repository / ".gitignore").write_text(".venv/\ndist/\n")
            for name in (".venv", "dist"):
                (repository / name).mkdir()
                (repository / name / "noise").write_text("excluded")
            snapshot = root / "snapshot"
            copy_source_snapshot(repository, snapshot)
            self.assertEqual(
                (snapshot / ".agent-workflow/routing.md").read_bytes(),
                b"pending policy\r\n",
            )
            self.assertEqual(
                (snapshot / ".agents/skills/wayfinder/SKILL.md").read_text(), "baseline"
            )
            self.assertEqual(
                (snapshot / "pending.py").read_text(), "pending new source\n"
            )
            for name in ("deleted.txt", ".venv", "dist", ".git"):
                self.assertFalse((snapshot / name).exists())
