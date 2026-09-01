from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from _test_support import (
    LIFECYCLE,
    PACKAGE_ROOT,
    ProjectTestCase,
    commit_all,
    initialize_repository,
    load_module,
    run_git,
    run_script,
    tree_snapshot,
    workspace_snapshot,
)

RETAINED_SKILLS = {
    "code-review",
    "codebase-design",
    "domain-modeling",
    "grilling",
    "implement",
    "prototype",
    "research",
    "tdd",
    "to-spec",
    "to-tickets",
    "wayfinder",
    "workflow-debugging",
    "workflow-discovery",
    "workflow-implementation",
    "workflow-verification",
}


class InteractiveInput(io.StringIO):
    def isatty(self) -> bool:
        return True


def file_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


class DirectDistributionTests(ProjectTestCase):
    def setUp(self) -> None:
        super().setUp()
        state = self.project / ".agent-wayfinder/custom-effort"
        state.mkdir(parents=True)
        (state / "map.md").write_bytes(b"# Project-owned map\n\x00\xff")
        unrelated = self.project / ".agents/skills/project-local/SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_bytes(b"project-owned skill\n")
        initialize_repository(self.project)
        self.state_before = tree_snapshot(self.project / ".agent-wayfinder")

    def lifecycle(self, command: str, *extra: object):
        return run_script(LIFECYCLE, command, self.project, *extra)

    def lifecycle_in_process(
        self,
        command: str,
        *,
        project: Path | None = None,
        stdin: io.StringIO | None = None,
    ) -> tuple[int, str, str]:
        lifecycle = load_module(
            f"interactive_lifecycle_{id(stdin)}_{command}",
            LIFECYCLE,
        )
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch.object(lifecycle.sys, "stdin", stdin or io.StringIO()),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            result = lifecycle.main([command, str(project or self.project)])
        return result, stdout.getvalue(), stderr.getvalue()

    def add_project_skill(self, name: str, content: bytes = b"project-owned\n") -> Path:
        path = self.project / ".agents/skills" / name / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(content)
        return path

    def assert_current_payload_installed(
        self, additional_skills: set[str] | None = None
    ) -> None:
        framework = self.project / ".agent-workflow"
        self.assertEqual(
            file_snapshot(framework),
            file_snapshot(PACKAGE_ROOT / "payload/agent-workflow"),
        )
        self.assertFalse((framework / "install-manifest.json").exists())

        installed = self.project / ".agents/skills"
        self.assertEqual(
            {path.name for path in installed.iterdir() if path.is_dir()},
            RETAINED_SKILLS | {"project-local"} | (additional_skills or set()),
        )
        for name in RETAINED_SKILLS:
            with self.subTest(skill=name):
                self.assertEqual(
                    tree_snapshot(installed / name),
                    tree_snapshot(PACKAGE_ROOT / "payload/skills" / name),
                )

    def assert_wayfinder_untouched(self) -> None:
        self.assertEqual(
            tree_snapshot(self.project / ".agent-wayfinder"),
            self.state_before,
        )

    def test_fresh_install_distributes_fifteen_skills_without_install_state(
        self,
    ) -> None:
        self.assert_ok(self.lifecycle("install"))

        self.assert_current_payload_installed()
        self.assert_wayfinder_untouched()
        commit_all(self.project, "install current agent workflow")
        status = self.lifecycle("status")
        self.assert_ok(status)
        self.assertIn("Agent Workflow: healthy", status.stdout)
        self.assertNotIn(".agent-wayfinder", status.stdout)

    def test_fresh_install_without_reserved_collision_does_not_prompt(self) -> None:
        result, stdout, stderr = self.lifecycle_in_process(
            "install",
            stdin=InteractiveInput("no\n"),
        )

        self.assertEqual(result, 0, stdout + stderr)
        self.assertNotIn("Continue and replace", stdout)

    def test_fresh_install_replaces_reserved_collision_without_prompt(self) -> None:
        self.add_project_skill("research")

        result, stdout, stderr = self.lifecycle_in_process(
            "install",
            stdin=InteractiveInput("no\n"),
        )

        self.assertEqual(result, 0, stdout + stderr)
        self.assertNotIn("Continue and replace", stdout)
        self.assertEqual(
            tree_snapshot(self.project / ".agents/skills/research"),
            tree_snapshot(PACKAGE_ROOT / "payload/skills/research"),
        )

    def test_noninteractive_first_install_replaces_reserved_collision(self) -> None:
        self.add_project_skill("research")

        result, stdout, stderr = self.lifecycle_in_process(
            "install",
            stdin=io.StringIO(),
        )

        self.assertEqual(result, 0, stdout + stderr)
        self.assertNotIn("Continue and replace", stdout)
        self.assertEqual(
            tree_snapshot(self.project / ".agents/skills/research"),
            tree_snapshot(PACKAGE_ROOT / "payload/skills/research"),
        )

    def test_multiple_reserved_collisions_replace_without_interaction(self) -> None:
        self.add_project_skill("research")
        self.add_project_skill("tdd")

        result, stdout, stderr = self.lifecycle_in_process(
            "install",
            stdin=io.StringIO(),
        )

        self.assertEqual(result, 0, stdout + stderr)
        self.assertNotIn("Continue and replace", stdout)
        for name in ("research", "tdd"):
            with self.subTest(name=name):
                self.assertEqual(
                    tree_snapshot(self.project / ".agents/skills" / name),
                    tree_snapshot(PACKAGE_ROOT / "payload/skills" / name),
                )
        self.assert_wayfinder_untouched()

    def test_unrecognized_remove_preserves_curated_name_collision(self) -> None:
        self.add_project_skill("research")
        before = workspace_snapshot(self.project)

        result, stdout, stderr = self.lifecycle_in_process("remove")

        self.assertEqual(result, 2, stdout + stderr)
        self.assertIn(".agents/skills/research/", stderr)
        self.assertIn("no recognizable Agent Workflow installation", stderr)
        self.assertEqual(workspace_snapshot(self.project), before)

    def test_ambiguous_composite_fails_before_mutation(self) -> None:
        self.add_project_skill("research")
        (self.project / "AGENTS.md").write_bytes(
            b"<!-- agent-workflow:managed-begin -->\nambiguous\n"
        )
        before = workspace_snapshot(self.project)

        result, stdout, stderr = self.lifecycle_in_process(
            "install",
            stdin=io.StringIO(),
        )

        self.assertEqual(result, 2, stdout + stderr)
        self.assertIn("AGENTS.md: managed policy markers", stderr)
        self.assertEqual(workspace_snapshot(self.project), before)

    def test_update_replaces_modified_reserved_skill_without_prompt(self) -> None:
        self.assert_ok(self.lifecycle("install"))
        research = self.project / ".agents/skills/research"
        (research / "SKILL.md").write_bytes(b"modified current skill\n")

        result, stdout, stderr = self.lifecycle_in_process(
            "update",
            stdin=InteractiveInput("no\n"),
        )

        self.assertEqual(result, 0, stdout + stderr)
        self.assertNotIn("Continue and replace", stdout)
        self.assertEqual(
            tree_snapshot(research),
            tree_snapshot(PACKAGE_ROOT / "payload/skills/research"),
        )

    def test_update_completely_replaces_managed_directories_only(self) -> None:
        self.assert_ok(self.lifecycle("install"))
        commit_all(self.project, "install agent workflow")

        routing = self.project / ".agent-workflow/routing.md"
        routing.write_bytes(b"committed framework drift\n")
        (self.project / ".agent-workflow/obsolete.txt").write_bytes(b"delete me\n")
        research = self.project / ".agents/skills/research"
        (research / "SKILL.md").write_bytes(b"committed skill drift\n")
        (research / "project-extra.txt").write_bytes(b"reserved directory extra\n")
        unrelated = self.project / ".agents/skills/project-local/SKILL.md"
        unrelated.write_bytes(b"updated unrelated skill\n")
        commit_all(self.project, "commit managed drift")

        self.assert_ok(self.lifecycle("update"))

        self.assert_current_payload_installed()
        self.assertEqual(unrelated.read_bytes(), b"updated unrelated skill\n")
        self.assert_wayfinder_untouched()
        self.assertFalse((research / "project-extra.txt").exists())

    def test_status_reports_committed_drift_as_repairable(self) -> None:
        self.assert_ok(self.lifecycle("install"))
        commit_all(self.project, "install agent workflow")
        self.assert_ok(self.lifecycle("status"))

        (self.project / ".agents/skills/research/SKILL.md").write_bytes(b"drift\n")
        commit_all(self.project, "commit drift")
        status = self.lifecycle("status")
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("repairable", status.stdout)
        self.assertIn("research", status.stdout)
        self.assertNotIn("mutation blocked", status.stdout)

    def test_update_recovers_a_committed_missing_framework_directory(self) -> None:
        self.assert_ok(self.lifecycle("install"))
        commit_all(self.project, "install agent workflow")
        run_git(self.project, "rm", "-r", ".agent-workflow")
        commit_all(self.project, "commit missing framework directory")

        status = self.lifecycle("status")
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("Agent Workflow: repairable", status.stdout)

        self.assert_ok(self.lifecycle("update"))
        self.assert_current_payload_installed()
        self.assert_wayfinder_untouched()

    def test_update_recovers_missing_composites_and_a_drifted_skill(self) -> None:
        self.assert_ok(self.lifecycle("install"))
        commit_all(self.project, "install agent workflow")
        run_git(self.project, "rm", "AGENTS.md", "CLAUDE.md")
        (self.project / ".agents/skills/research/SKILL.md").write_text(
            "committed project drift\n", encoding="utf-8"
        )
        commit_all(self.project, "commit missing composites and skill drift")

        status = self.lifecycle("status")
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("Agent Workflow: repairable", status.stdout)

        self.assert_ok(self.lifecycle("update"))
        self.assert_current_payload_installed()
        self.assert_wayfinder_untouched()

    def test_install_replaces_existing_framework_and_curated_skill_surfaces(
        self,
    ) -> None:
        project = Path(self.temporary.name) / "existing-surfaces"
        project.mkdir()

        framework_note = project / ".agent-workflow/project-note.txt"
        framework_note.parent.mkdir(parents=True)
        framework_note.write_bytes(b"stale pre-v1 framework content\n")
        curated = project / ".agents/skills/research/SKILL.md"
        curated.parent.mkdir(parents=True)
        curated.write_bytes(b"stale curated skill content\n")
        unrelated = project / ".agents/skills/legacy-local/SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_bytes(b"project-owned unrelated skill\n")
        durable = project / ".agent-wayfinder/effort/map.md"
        durable.parent.mkdir(parents=True)
        durable.write_bytes(b"project-owned durable state\n")
        (project / ".gitignore").write_text(
            ".agent-workflow/\n.agents/\n",
            encoding="utf-8",
        )
        initialize_repository(project)

        status = run_script(LIFECYCLE, "status", project)
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("Agent Workflow: repairable", status.stdout)

        result, stdout, stderr = self.lifecycle_in_process(
            "install",
            project=project,
            stdin=io.StringIO(),
        )
        self.assertEqual(result, 0, stdout + stderr)
        self.assertNotIn("Continue and replace", stdout)
        self.assertFalse(framework_note.exists())
        self.assertEqual(
            tree_snapshot(project / ".agents/skills/research"),
            tree_snapshot(PACKAGE_ROOT / "payload/skills/research"),
        )
        self.assertEqual(unrelated.read_bytes(), b"project-owned unrelated skill\n")
        self.assertEqual(durable.read_bytes(), b"project-owned durable state\n")

        (project / ".agent-workflow/providers.json").write_bytes(b"obsolete\n")
        (project / ".agents/skills/research/local.txt").write_bytes(b"obsolete\n")
        self.assert_ok(run_script(LIFECYCLE, "update", project))
        self.assertFalse((project / ".agent-workflow/providers.json").exists())
        self.assertFalse((project / ".agents/skills/research/local.txt").exists())
        self.assertEqual(unrelated.read_bytes(), b"project-owned unrelated skill\n")
        self.assertEqual(durable.read_bytes(), b"project-owned durable state\n")

    def test_remove_and_reinstall_touch_only_current_managed_surfaces(self) -> None:
        project_policy = b"# Local agent policy\n"
        (self.project / "AGENTS.md").write_bytes(project_policy)
        commit_all(self.project, "add project policy")
        self.assert_ok(self.lifecycle("install"))
        commit_all(self.project, "install agent workflow")

        self.assert_ok(self.lifecycle("remove"))
        self.assertFalse((self.project / ".agent-workflow").exists())
        for name in RETAINED_SKILLS:
            self.assertFalse((self.project / ".agents/skills" / name).exists())
        self.assertEqual(
            (self.project / ".agents/skills/project-local/SKILL.md").read_bytes(),
            b"project-owned skill\n",
        )
        self.assertEqual((self.project / "AGENTS.md").read_bytes(), project_policy)
        self.assertFalse((self.project / "CLAUDE.md").exists())
        self.assert_wayfinder_untouched()

        commit_all(self.project, "remove agent workflow")
        self.assert_ok(self.lifecycle("install"))
        self.assert_current_payload_installed()
        self.assert_wayfinder_untouched()

    def test_update_replaces_framework_desired_state_and_preserves_unmanaged_skills(
        self,
    ) -> None:
        self.assert_ok(self.lifecycle("install"))
        commit_all(self.project, "install agent workflow")

        providers = self.project / ".agent-workflow/providers.json"
        providers.write_bytes(b"obsolete framework bytes\n")
        notices = self.project / ".agent-workflow/THIRD_PARTY_NOTICES.md"
        notices.write_bytes(b"former standalone notice\n")
        preserved: dict[Path, bytes] = {}
        for name in ("setup-matt-pocock-skills", "teach", "triage"):
            path = self.project / ".agents/skills" / name / "SKILL.md"
            path.parent.mkdir(parents=True)
            content = f"project-owned {name}\n".encode()
            path.write_bytes(content)
            preserved[path] = content
        commit_all(self.project, "add prior provider-era surfaces")

        status = self.lifecycle("status")
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("Agent Workflow: repairable", status.stdout)
        self.assertNotIn("clean break", status.stdout)

        self.assert_ok(self.lifecycle("update"))

        self.assert_current_payload_installed({path.parent.name for path in preserved})
        self.assertFalse(providers.exists())
        self.assertFalse(notices.exists())
        for path, content in preserved.items():
            with self.subTest(path=path):
                self.assertEqual(path.read_bytes(), content)
        self.assert_wayfinder_untouched()

        commit_all(self.project, "converge prior provider-era surfaces")
        providers.write_bytes(b"another obsolete framework file\n")
        notices.write_bytes(b"another former standalone notice\n")
        commit_all(self.project, "restore obsolete framework files")

        self.assert_ok(self.lifecycle("install"))
        self.assertFalse(providers.exists())
        self.assertFalse(notices.exists())
        for path, content in preserved.items():
            with self.subTest(repeated_install=path):
                self.assertEqual(path.read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
