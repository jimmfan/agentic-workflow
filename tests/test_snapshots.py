"""Regression checks for the filesystem snapshots used by preservation tests."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from _test_support import tree_snapshot, workspace_snapshot


class WorkspaceSnapshotTests(unittest.TestCase):
    def test_git_metadata_is_excluded_before_traversal_or_reading(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            metadata = root / ".git"
            lock = metadata / "objects/maintenance.lock"
            lock.parent.mkdir(parents=True)
            lock.write_bytes(b"transient Git data")
            (root / "README.md").write_bytes(b"project bytes\r\n")
            scandir = os.scandir
            read_bytes = Path.read_bytes

            def scan(path):
                if Path(path).is_relative_to(metadata):
                    raise AssertionError("snapshot traversed Git metadata")
                return scandir(path)

            def read(path):
                if path.is_relative_to(metadata):
                    raise FileNotFoundError("transient Git metadata disappeared")
                return read_bytes(path)

            for git_entry in ("directory", "file"):
                with self.subTest(git_entry=git_entry):
                    with (
                        mock.patch("os.scandir", side_effect=scan),
                        mock.patch.object(Path, "read_bytes", read),
                    ):
                        self.assertEqual(
                            workspace_snapshot(root),
                            {"README.md": ("file", b"project bytes\r\n")},
                        )
                    self.assertIn(".git", tree_snapshot(root))
                if git_entry == "directory":
                    lock.unlink()
                    lock.parent.rmdir()
                    metadata.rmdir()
                    metadata.write_text("gitdir: /external/worktree/metadata\n")

    def test_project_bytes_directories_and_symlinks_remain_observable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            effort = root / ".project-efforts/effort"
            effort.mkdir(parents=True)
            (effort / "map.md").write_bytes(b"project state\r\n")
            (root / ".gitignore").write_bytes(b"ignored/\n")
            (root / "ignored").mkdir()
            (root / "link").symlink_to(".project-efforts", target_is_directory=True)
            (root / "dangling").symlink_to("missing")
            expected = {
                ".project-efforts": ("directory", b""),
                ".project-efforts/effort": ("directory", b""),
                ".project-efforts/effort/map.md": ("file", b"project state\r\n"),
                ".gitignore": ("file", b"ignored/\n"),
                "ignored": ("directory", b""),
                "link": ("symlink", ".project-efforts"),
                "dangling": ("symlink", "missing"),
            }
            self.assertEqual(workspace_snapshot(root), expected)
            self.assertEqual(tree_snapshot(root), expected)
            (effort / "map.md").write_bytes(b"changed state\n")
            self.assertNotEqual(workspace_snapshot(root), expected)

    def test_missing_project_file_during_read_still_fails_the_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "project.txt").write_bytes(b"must be preserved")
            with mock.patch.object(Path, "read_bytes", side_effect=FileNotFoundError):
                with self.assertRaises(FileNotFoundError):
                    workspace_snapshot(root)


if __name__ == "__main__":
    unittest.main()
