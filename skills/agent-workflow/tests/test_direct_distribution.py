from __future__ import annotations

import unittest
from pathlib import Path

from _test_support import (
    LIFECYCLE,
    PACKAGE_ROOT,
    ProjectTestCase,
    commit_all,
    initialize_repository,
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
OBSOLETE_SKILLS = {"setup-matt-pocock-skills", "teach", "triage"}
# These independent literals verify the externally visible clean-break contract.
LEGACY_INSTRUCTION = (
    "Remove the legacy .agent-workflow/ directory and obsolete skill directories "
    ".agents/skills/setup-matt-pocock-skills, .agents/skills/teach, and "
    ".agents/skills/triage in a separate Git-tracked cleanup, commit that cleanup, "
    "then run the new agent-workflow install."
)


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

    def assert_current_payload_installed(self) -> None:
        framework = self.project / ".agent-workflow"
        self.assertEqual(
            file_snapshot(framework),
            file_snapshot(PACKAGE_ROOT / "payload/agent-workflow"),
        )
        self.assertFalse((framework / "install-manifest.json").exists())

        installed = self.project / ".agents/skills"
        self.assertEqual(
            {path.name for path in installed.iterdir() if path.is_dir()},
            RETAINED_SKILLS | {"project-local"},
        )
        for name in RETAINED_SKILLS:
            with self.subTest(skill=name):
                self.assertEqual(
                    tree_snapshot(installed / name),
                    tree_snapshot(PACKAGE_ROOT / "payload/skills" / name),
                )
        for name in OBSOLETE_SKILLS:
            self.assertFalse((installed / name).exists())

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
        self.assertNotIn("reserved curated skill directory", status.stdout)

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
        self.assertNotIn("reserved curated skill directory", status.stdout)

        self.assert_ok(self.lifecycle("update"))
        self.assert_current_payload_installed()
        self.assert_wayfinder_untouched()

    def test_fresh_adoption_rejects_preexisting_framework_directory(
        self,
    ) -> None:
        project = Path(self.temporary.name) / "framework-collision"
        project.mkdir()

        framework_note = project / ".agent-workflow/project-note.txt"
        framework_note.parent.mkdir(parents=True)
        framework_note.write_bytes(b"project-owned pre-existing content\n")

        initialize_repository(project)
        before = workspace_snapshot(project)

        status = run_script(LIFECYCLE, "status", project)
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn(
            "existing .agent-workflow directory blocks adoption",
            status.stdout,
        )
        self.assertIn("Agent Workflow: unsafe/conflict", status.stdout)
        self.assertNotIn("REPAIR:", status.stdout)
        self.assertEqual(workspace_snapshot(project), before)

        for command in ("install", "update", "remove"):
            with self.subTest(command=command):
                result = run_script(LIFECYCLE, command, project)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(
                    "existing .agent-workflow directory blocks adoption",
                    result.stderr,
                )
                self.assertEqual(workspace_snapshot(project), before)

    def test_fresh_adoption_rejects_a_reserved_skill_despite_framework_directory(
        self,
    ) -> None:
        project = Path(self.temporary.name) / "reserved-name"
        project.mkdir()
        framework_note = project / ".agent-workflow/project-note.txt"
        framework_note.parent.mkdir(parents=True)
        framework_note.write_bytes(b"project-owned framework-shaped directory\n")
        collision = project / ".agents/skills/research/SKILL.md"
        collision.parent.mkdir(parents=True)
        collision.write_bytes(b"project-owned research skill\n")
        initialize_repository(project)
        before = workspace_snapshot(project)

        status = run_script(LIFECYCLE, "status", project)
        self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
        self.assertIn("reserved curated skill directory blocks adoption", status.stdout)

        for command in ("install", "update", "remove"):
            with self.subTest(command=command):
                result = run_script(LIFECYCLE, command, project)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(
                    "move or rename the project-owned skill before installation",
                    result.stderr,
                )
                self.assertEqual(workspace_snapshot(project), before)

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

    def test_legacy_provider_surfaces_require_one_manual_clean_break(self) -> None:
        cases = ["providers.json", *sorted(OBSOLETE_SKILLS)]
        for name in cases:
            with self.subTest(name=name):
                project = Path(self.temporary.name) / name.replace(".", "-")
                project.mkdir()
                initialize_repository(project)
                if name == "providers.json":
                    legacy = project / ".agent-workflow/providers.json"
                else:
                    legacy = project / ".agents/skills" / name / "SKILL.md"
                legacy.parent.mkdir(parents=True, exist_ok=True)
                legacy.write_bytes(b"legacy bytes are deliberately not inspected\n")
                commit_all(project, "add legacy installation surface")
                before = workspace_snapshot(project)

                status = run_script(LIFECYCLE, "status", project)
                self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
                self.assertIn("legacy clean break required", status.stdout)
                self.assertEqual(status.stdout.count(LEGACY_INSTRUCTION), 1)

                install = run_script(LIFECYCLE, "install", project)
                self.assertEqual(install.returncode, 2, install.stdout + install.stderr)
                self.assertEqual(install.stderr.count(LEGACY_INSTRUCTION), 1)
                self.assertEqual(workspace_snapshot(project), before)


if __name__ == "__main__":
    unittest.main()
