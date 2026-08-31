from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from _test_support import (
    LIFECYCLE,
    MANAGED_BEGIN,
    MANAGED_END,
    ProjectTestCase,
    commit_all,
    initialize_repository,
    load_module,
    run_git,
    run_script,
    workspace_snapshot,
)

FORMER_PROJECT_MARKER = b"<!-- agent-workflow:project-instructions -->"


class LifecycleTests(ProjectTestCase):
    def setUp(self) -> None:
        super().setUp()
        initialize_repository(self.project)

    def lifecycle(self, command: str, *extra: object):
        return run_script(LIFECYCLE, command, self.project, *extra)

    def test_mutation_requires_exact_git_root_with_valid_head(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            non_repository = Path(temporary) / "plain"
            non_repository.mkdir()
            result = run_script(LIFECYCLE, "install", non_repository)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Git worktree root", result.stderr)

            unborn = Path(temporary) / "unborn"
            unborn.mkdir()
            run_git(unborn, "init", "-q")
            result = run_script(LIFECYCLE, "install", unborn)
            self.assertEqual(result.returncode, 2)
            self.assertIn("valid HEAD", result.stderr)

        child = self.project / "nested"
        child.mkdir()
        (child / ".gitkeep").write_bytes(b"")
        commit_all(self.project, "add nested directory")
        result = run_script(LIFECYCLE, "install", child)
        self.assertEqual(result.returncode, 2)
        self.assertIn("exact Git worktree root", result.stderr)

    def test_mutation_requires_a_completely_clean_worktree(self) -> None:
        tracked = self.project / "README.md"
        tracked.write_text("changed\n", encoding="utf-8")
        result = self.lifecycle("install")
        self.assertEqual(result.returncode, 2)
        self.assertIn("worktree and index must be completely clean", result.stderr)
        self.assertFalse((self.project / ".agent-workflow").exists())

        run_git(self.project, "restore", "README.md")
        (self.project / "untracked.txt").write_text("untracked\n", encoding="utf-8")
        result = self.lifecycle("install")
        self.assertEqual(result.returncode, 2)
        self.assertIn("untracked", result.stderr)
        self.assertFalse((self.project / ".agent-workflow").exists())

    def test_untracked_or_ignored_managed_content_is_rejected(self) -> None:
        managed_untracked = self.project / ".agents/skills/research/local.txt"
        managed_untracked.parent.mkdir(parents=True)
        managed_untracked.write_text("cannot be recovered by Git\n", encoding="utf-8")
        result = self.lifecycle("install")
        self.assertEqual(result.returncode, 2)
        self.assertIn("untracked file under a managed surface", result.stderr)

        managed_untracked.unlink()
        managed_untracked.parent.rmdir()
        (self.project / ".gitignore").write_text(".agents/\n", encoding="utf-8")
        commit_all(self.project, "ignore agents directory")
        result = self.lifecycle("install")
        self.assertEqual(result.returncode, 2)
        self.assertIn("managed destination is ignored", result.stderr)
        self.assertFalse((self.project / ".agent-workflow").exists())

    def test_symlink_in_a_managed_parent_is_rejected_without_escape(self) -> None:
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        sentinel = outside / "sentinel.txt"
        sentinel.write_text("outside\n", encoding="utf-8")
        (self.project / ".agents").symlink_to(outside, target_is_directory=True)
        commit_all(self.project, "track managed-parent symlink")

        before = workspace_snapshot(self.project)
        result = self.lifecycle("install")
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlink", result.stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "outside\n")
        self.assertEqual(workspace_snapshot(self.project), before)

    def test_special_entry_in_a_managed_tree_is_rejected(self) -> None:
        framework = self.project / ".agent-workflow"
        framework.mkdir()
        fifo = framework / "unsupported"
        try:
            fifo_path = os.fspath(fifo)
            os.mkfifo(fifo_path)
        except (AttributeError, OSError) as exc:
            self.skipTest(f"FIFO creation is unavailable: {exc}")

        result = self.lifecycle("install")

        self.assertEqual(result.returncode, 2)
        self.assertIn("special entry", result.stderr)
        self.assertTrue(fifo.exists())

    def test_composite_project_bytes_survive_install_update_and_remove(self) -> None:
        project_policy = b"# Project policy\n\nKeep this byte-for-byte.\n"
        policy = self.project / "AGENTS.md"
        policy.write_bytes(project_policy)
        commit_all(self.project, "add project policy")

        self.assert_ok(self.lifecycle("install"))
        installed = policy.read_bytes()
        self.assertTrue(installed.startswith(MANAGED_BEGIN))
        self.assertTrue(installed.endswith(project_policy))
        self.assertFalse((self.project / ".agent-wayfinder").exists())
        commit_all(self.project, "install agent workflow")

        managed_end = installed.index(MANAGED_END)
        policy.write_bytes(
            MANAGED_BEGIN + b"\ncommitted managed drift\n" + installed[managed_end:]
        )
        commit_all(self.project, "commit managed drift")
        self.assert_ok(self.lifecycle("update"))
        repaired = policy.read_bytes()
        self.assertNotIn(b"committed managed drift", repaired)
        self.assertTrue(repaired.endswith(project_policy))
        commit_all(self.project, "repair managed drift")

        self.assert_ok(self.lifecycle("remove"))
        self.assertEqual(policy.read_bytes(), project_policy)
        self.assertFalse((self.project / "CLAUDE.md").exists())
        self.assertFalse((self.project / ".agent-wayfinder").exists())

    def test_repeated_install_and_update_are_composite_idempotent(self) -> None:
        project_bytes = {
            "AGENTS.md": b"# Project agents\r\n\r\nKeep \x00\xff bytes.\r\n",
            "CLAUDE.md": b"# Project Claude\n\nKeep this exact suffix.\n",
        }
        for name, content in project_bytes.items():
            (self.project / name).write_bytes(content)
        commit_all(self.project, "add unmarked project policies")

        self.assert_ok(self.lifecycle("install"))
        installed = {name: (self.project / name).read_bytes() for name in project_bytes}
        commit_all(self.project, "install agent workflow")

        for command in ("install", "update", "install", "update"):
            with self.subTest(command=command):
                self.assert_ok(self.lifecycle(command))
                for name, project in project_bytes.items():
                    data = (self.project / name).read_bytes()
                    self.assertEqual(data, installed[name])
                    self.assertTrue(data.endswith(project))
                    self.assertEqual(data.count(MANAGED_BEGIN), 1)
                    self.assertEqual(data.count(MANAGED_END), 1)
                    if name == "AGENTS.md":
                        self.assertNotIn(FORMER_PROJECT_MARKER, data)
                    else:
                        self.assertEqual(data.count(FORMER_PROJECT_MARKER), 1)
                self.assertEqual(
                    run_git(self.project, "status", "--porcelain").stdout,
                    "",
                )

    def test_malformed_duplicated_partial_and_reordered_markers_fail_preflight(
        self,
    ) -> None:
        cases = {
            "partial": MANAGED_BEGIN + b"\nmissing other markers\n",
            "unknown-duplicate": MANAGED_BEGIN
            + b"\nfirst managed\n"
            + MANAGED_END
            + b"\n"
            + MANAGED_BEGIN
            + b"\nsecond managed\n"
            + MANAGED_END
            + b"\nproject bytes\n",
            "reordered": MANAGED_END + b"\n" + MANAGED_BEGIN + b"\n",
            "interleaved": MANAGED_BEGIN
            + b"\n"
            + MANAGED_BEGIN
            + b"\n"
            + MANAGED_END
            + b"\n"
            + MANAGED_END
            + b"\n",
            "partial-token": b"<!-- agent-workflow:managed-beg",
        }
        for composite in ("AGENTS.md", "CLAUDE.md"):
            for name, content in cases.items():
                with self.subTest(composite=composite, name=name):
                    project = Path(self.temporary.name) / f"{composite}-{name}"
                    project.mkdir()
                    initialize_repository(project)
                    (project / composite).write_bytes(content)
                    commit_all(project, f"add {name} markers")
                    before = workspace_snapshot(project)

                    result = run_script(LIFECYCLE, "install", project)

                    self.assertEqual(result.returncode, 2)
                    self.assertIn(f"{composite}: managed policy markers", result.stderr)
                    self.assertIn("managed-begin=", result.stderr)
                    self.assertIn("managed-end=", result.stderr)
                    self.assertEqual(workspace_snapshot(project), before)

    def test_logical_marker_lines_accept_crlf_and_replace_in_place(self) -> None:
        project_prefix = b"# Prefix\r\n\r\n"
        project_suffix = b"# Suffix\r\nKeep exactly.\r\n"
        policy = self.project / "AGENTS.md"
        policy.write_bytes(
            project_prefix
            + MANAGED_BEGIN
            + b"\r\nstale managed bytes\r\n"
            + MANAGED_END
            + b"\r\n"
            + project_suffix
        )
        commit_all(self.project, "add CRLF managed region")

        self.assert_ok(self.lifecycle("update"))

        updated = policy.read_bytes()
        self.assertTrue(updated.startswith(project_prefix + MANAGED_BEGIN + b"\n"))
        self.assertTrue(updated.endswith(project_suffix))
        self.assertNotIn(b"stale managed bytes", updated)
        self.assertEqual(updated.count(MANAGED_BEGIN), 1)
        self.assertEqual(updated.count(MANAGED_END), 1)

        commit_all(self.project, "normalize CRLF managed region")
        self.assert_ok(self.lifecycle("remove"))
        self.assertEqual(policy.read_bytes(), project_prefix + project_suffix)

    def test_former_standard_agents_layout_converges_without_project_loss(self) -> None:
        project_bytes = b"# Original project policy\nKeep exactly.\n"
        policy = self.project / "AGENTS.md"
        policy.write_bytes(
            MANAGED_BEGIN
            + b"\nstale managed bytes\n"
            + MANAGED_END
            + b"\n\n"
            + FORMER_PROJECT_MARKER
            + b"\n"
            + project_bytes
        )
        commit_all(self.project, "add former standard composite")

        self.assert_ok(self.lifecycle("update"))

        updated = policy.read_bytes()
        self.assertEqual(updated.count(MANAGED_BEGIN), 1)
        self.assertEqual(updated.count(MANAGED_END), 1)
        self.assertNotIn(FORMER_PROJECT_MARKER, updated)
        self.assertNotIn(b"stale managed bytes", updated)
        self.assertTrue(updated.endswith(project_bytes))

    def test_known_nested_crlf_duplicate_is_normalized_without_project_loss(
        self,
    ) -> None:
        project_bytes = b"# Original project policy\r\nKeep \x00\xff exactly.\r\n"
        policy = self.project / "AGENTS.md"
        policy.write_bytes(
            MANAGED_BEGIN
            + b"\nouter managed bytes\n"
            + MANAGED_END
            + b"\n\n"
            + FORMER_PROJECT_MARKER
            + b"\n"
            + MANAGED_BEGIN
            + b"\r\ninner managed bytes\r\n"
            + MANAGED_END
            + b"\r\n\r\n"
            + FORMER_PROJECT_MARKER
            + b"\r\n"
            + project_bytes
        )
        commit_all(self.project, "add historical nested duplicate")

        self.assert_ok(self.lifecycle("install"))

        updated = policy.read_bytes()
        self.assertEqual(updated.count(MANAGED_BEGIN), 1)
        self.assertEqual(updated.count(MANAGED_END), 1)
        self.assertNotIn(FORMER_PROJECT_MARKER, updated)
        self.assertNotIn(b"outer managed bytes", updated)
        self.assertNotIn(b"inner managed bytes", updated)
        self.assertTrue(updated.endswith(project_bytes))

    def test_nested_duplicate_recovery_requires_the_evidenced_newline_shape(
        self,
    ) -> None:
        layouts = {
            "all-lf": (b"\n", b"\n"),
            "reversed": (b"\r\n", b"\n"),
        }
        for name, (outer_newline, inner_newline) in layouts.items():
            with self.subTest(name=name):
                project = Path(self.temporary.name) / f"nested-{name}"
                project.mkdir()
                initialize_repository(project)
                policy = project / "AGENTS.md"
                policy.write_bytes(
                    MANAGED_BEGIN
                    + outer_newline
                    + b"outer managed"
                    + outer_newline
                    + MANAGED_END
                    + outer_newline
                    + outer_newline
                    + FORMER_PROJECT_MARKER
                    + outer_newline
                    + MANAGED_BEGIN
                    + inner_newline
                    + b"inner managed"
                    + inner_newline
                    + MANAGED_END
                    + inner_newline
                    + inner_newline
                    + FORMER_PROJECT_MARKER
                    + inner_newline
                    + b"project bytes\n"
                )
                commit_all(project, "add unsupported nested marker layout")
                before = workspace_snapshot(project)

                result = run_script(LIFECYCLE, "update", project)

                self.assertEqual(result.returncode, 2)
                self.assertIn("AGENTS.md: managed policy markers", result.stderr)
                self.assertEqual(workspace_snapshot(project), before)

    def test_dry_run_is_immutable(self) -> None:
        before = workspace_snapshot(self.project)
        result = self.lifecycle("install", "--dry-run")
        self.assert_ok(result)
        self.assertIn("INSTALL PLAN", result.stdout)
        self.assertEqual(workspace_snapshot(self.project), before)

    def test_status_reports_repair_and_git_safety_without_requiring_cleanliness(
        self,
    ) -> None:
        status = self.lifecycle("status")
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("repairable", status.stdout)

        self.assert_ok(self.lifecycle("install"))
        commit_all(self.project, "install agent workflow")

        untracked = self.project / "untracked.txt"
        untracked.write_text("work in progress\n", encoding="utf-8")
        status = self.lifecycle("status")
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("Git safety boundary would block mutation", status.stdout)
        self.assertIn("untracked", status.stdout)
        self.assertIn("Agent Workflow: blocked by Git safety boundary", status.stdout)
        self.assertNotIn("Agent Workflow: repairable", status.stdout)
        self.assertEqual(untracked.read_text(encoding="utf-8"), "work in progress\n")

    def test_mid_operation_write_failure_reports_truthful_partial_state(self) -> None:
        lifecycle = load_module("partial_failure_lifecycle", LIFECYCLE)
        real_replace = lifecycle.os.replace
        replacements = 0

        def fail_second_replace(source: object, target: object) -> None:
            nonlocal replacements
            replacements += 1
            if replacements == 2:
                raise OSError("injected ordinary replace failure")
            real_replace(source, target)

        stderr = io.StringIO()
        with (
            mock.patch.object(lifecycle.os, "replace", side_effect=fail_second_replace),
            redirect_stderr(stderr),
        ):
            result = lifecycle.main(["install", str(self.project)])

        self.assertEqual(result, 2)
        self.assertIn("partial changes may exist", stderr.getvalue())
        self.assertIn("inspect git status", stderr.getvalue().lower())
        self.assertTrue((self.project / ".agent-workflow").is_dir())
        self.assertLess(len(list((self.project / ".agent-workflow").rglob("*"))), 6)
        self.assertNotEqual(run_git(self.project, "status", "--porcelain").stdout, "")


if __name__ == "__main__":
    unittest.main()
