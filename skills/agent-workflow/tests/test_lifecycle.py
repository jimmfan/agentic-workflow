from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import unittest

from _test_support import (
    ADOPT,
    MANAGED_BEGIN,
    MANAGED_END,
    PACKAGE_ROOT,
    ProjectTestCase,
    run_script,
    tree_snapshot,
)


class LifecycleTests(ProjectTestCase):
    def test_install_creates_only_current_framework_and_empty_state_root(self) -> None:
        self.assert_ok(self.adopt("install"))
        self.assertTrue((self.project / ".agent-workflow/routing.md").is_file())
        self.assertTrue((self.project / ".agent-wayfinder").is_dir())
        self.assertEqual(list((self.project / ".agent-wayfinder").iterdir()), [])
        self.assertEqual(
            {
                path.relative_to(self.project / ".agent-workflow").as_posix()
                for path in (self.project / ".agent-workflow").rglob("*")
                if path.is_file()
            },
            {
                "README.md",
                "THIRD_PARTY_NOTICES.md",
                "contracts/wayfinder-state.md",
                "install-manifest.json",
                "routing.md",
            },
        )
        manifest = json.loads(
            (self.project / ".agent-workflow/install-manifest.json").read_text()
        )
        self.assertEqual(manifest["schema_version"], 2)
        self.assertEqual(
            set(manifest),
            {
                "schema_version",
                "framework_version",
                "source_revision",
                "external_files",
                "composites",
                "integrity_sha256",
            },
        )
        self.assertRegex(manifest["integrity_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn("framework_files", manifest)
        self.assertNotIn("project_owned", manifest)

    def test_update_repairs_reconstructable_state_and_missing_framework_fails_closed(
        self,
    ) -> None:
        self.assert_ok(self.adopt("install"))
        routing = self.project / ".agent-workflow/routing.md"
        expected = routing.read_bytes()
        routing.write_bytes(b"locally drifted framework bytes\n")
        (self.project / ".agent-workflow/README.md").unlink()
        obsolete = self.project / ".agent-workflow/obsolete-runtime-note.md"
        obsolete.write_text("historical framework file\n")
        self.assert_ok(self.adopt("update"))
        self.assertEqual(routing.read_bytes(), expected)
        self.assertTrue((self.project / ".agent-workflow/README.md").is_file())
        self.assertFalse(obsolete.exists())

        manifest_path = self.project / ".agent-workflow/install-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        absent = self.project / ".agents/skills/removed-local-skill/SKILL.md"
        absent.parent.mkdir(parents=True)
        absent.write_bytes(b"previously recorded managed bytes\n")
        manifest["external_files"][".agents/skills/removed-local-skill/SKILL.md"] = {
            "created": True,
            "sha256": hashlib.sha256(absent.read_bytes()).hexdigest(),
        }
        lifecycle_fields = {
            key: manifest[key]
            for key in (
                "schema_version",
                "framework_version",
                "source_revision",
                "external_files",
                "composites",
            )
        }
        manifest["integrity_sha256"] = hashlib.sha256(
            json.dumps(
                lifecycle_fields,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        absent.unlink()
        self.assert_ok(self.adopt("update"))
        self.assertFalse(absent.exists())

        state = self.project / ".agent-wayfinder/custom.txt"
        state.write_text("durable project bytes\n")
        shutil.rmtree(self.project / ".agent-workflow")
        before = tree_snapshot(self.project)
        result = self.adopt("update")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("manifest is absent", result.stderr)
        self.assertEqual(tree_snapshot(self.project), before)
        self.assertEqual(state.read_text(), "durable project bytes\n")

    def test_arbitrary_and_human_edited_state_survives_every_lifecycle_operation(
        self,
    ) -> None:
        state = self.project / ".agent-wayfinder"
        unknown = state / "unrecognized-project-data"
        (unknown / "nested").mkdir(parents=True)
        (unknown / "note.txt").write_bytes(b"project-owned note\n")
        (unknown / "nested/data.bin").write_bytes(b"\x00project\xffstate")
        (unknown / "metadata.json").write_bytes(b'{"owner":"project"}\n')
        try:
            (unknown / "data-link").symlink_to("nested/data.bin")
        except OSError:
            pass
        effort = self.project / ".agent-wayfinder/custom-effort"
        (effort / "unknowns").mkdir(parents=True)
        (effort / "unrecognized-project-data").mkdir()
        (effort / "map.md").write_text(
            "# Personal layout\n\nNo standard headings; keep exactly.\n",
            encoding="utf-8",
        )
        (effort / "facts.md").write_text(
            "# Facts\n\n## F1 — Ledger fact\n\n- Source: source.md\n\nKeep exactly.\n",
            encoding="utf-8",
        )
        (effort / "unrecognized-project-data/note.txt").write_text(
            "Human-owned content outside the current state shape.\n",
            encoding="utf-8",
        )
        (effort / "decisions.md").write_text(
            "# Decisions\n\n## D1 — Ledger decision\n\n"
            "- Authority: User\n\nKeep exactly.\n",
            encoding="utf-8",
        )
        (effort / "unknowns/U9-free-form.md").write_text(
            "A human can structure this however they find useful.\n",
            encoding="utf-8",
        )
        original = tree_snapshot(state)

        for command in ("install", "status", "update", "remove", "install"):
            with self.subTest(command=command):
                self.assert_ok(self.adopt(command))
                self.assertEqual(tree_snapshot(state), original)

    def test_composite_policy_preserves_project_region_through_update_and_remove(
        self,
    ) -> None:
        project_policy = b"# Project policy\n\nKeep this byte-for-byte.\n"
        (self.project / "AGENTS.md").write_bytes(project_policy)
        self.assert_ok(self.adopt("install"))
        installed = (self.project / "AGENTS.md").read_bytes()
        self.assertTrue(installed.startswith(MANAGED_BEGIN))
        self.assertIn(
            b"Do not manufacture cross-artifact conflicts or parallel representations",
            installed,
        )
        self.assertTrue(installed.endswith(project_policy))

        managed_end = installed.index(MANAGED_END)
        drifted = MANAGED_BEGIN + b"drifted managed text\n" + installed[managed_end:]
        (self.project / "AGENTS.md").write_bytes(drifted)
        self.assert_ok(self.adopt("update"))
        repaired = (self.project / "AGENTS.md").read_bytes()
        self.assertNotIn(b"drifted managed text", repaired)
        self.assertTrue(repaired.endswith(project_policy))

        self.assert_ok(self.adopt("remove"))
        self.assertEqual((self.project / "AGENTS.md").read_bytes(), project_policy)
        self.assertFalse((self.project / "CLAUDE.md").exists())

    def test_malformed_composite_boundary_stops_without_partial_mutation(self) -> None:
        self.assert_ok(self.adopt("install"))
        policy = self.project / "AGENTS.md"
        policy.write_bytes(MANAGED_BEGIN + b"missing the other boundaries\n")
        routing = self.project / ".agent-workflow/routing.md"
        routing.write_bytes(b"drift that must remain after failed preflight\n")
        before = tree_snapshot(self.project)
        result = self.adopt("update")
        self.assertEqual(result.returncode, 2)
        self.assertIn("markers", result.stderr)
        self.assertEqual(tree_snapshot(self.project), before)

    def test_unknown_external_collision_is_never_overwritten(self) -> None:
        collision = self.project / ".agents/skills/workflow-debugging/SKILL.md"
        collision.parent.mkdir(parents=True)
        collision.write_text("project-owned skill\n")
        result = self.adopt("install")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown external content", result.stderr)
        self.assertEqual(collision.read_text(), "project-owned skill\n")
        self.assertFalse((self.project / ".agent-workflow").exists())
        self.assertFalse((self.project / ".agent-wayfinder").exists())

    def test_remove_preserves_external_files_not_owned_at_removal(self) -> None:
        source = PACKAGE_ROOT / "payload/skills/workflow-debugging/SKILL.md"
        for case in ("preexisting-exact", "locally-modified"):
            with self.subTest(case=case):
                project = Path(self.temporary.name) / case
                project.mkdir()
                target = project / ".agents/skills/workflow-debugging/SKILL.md"
                if case == "preexisting-exact":
                    target.parent.mkdir(parents=True)
                    expected = source.read_bytes()
                    target.write_bytes(expected)
                    self.assert_ok(run_script(ADOPT, "install", project))
                else:
                    self.assert_ok(run_script(ADOPT, "install", project))
                    expected = b"project changed this managed integration\n"
                    target.write_bytes(expected)
                self.assert_ok(run_script(ADOPT, "remove", project))
                self.assertEqual(target.read_bytes(), expected)

    def test_unsafe_project_and_framework_roots_are_rejected(self) -> None:
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (outside / "sentinel").write_text("safe\n")
        (self.project / ".agent-workflow").symlink_to(outside, target_is_directory=True)
        result = self.adopt("update")
        self.assertEqual(result.returncode, 2)
        self.assertEqual((outside / "sentinel").read_text(), "safe\n")

        (self.project / ".agent-workflow").unlink()
        (self.project / ".agent-wayfinder").symlink_to(
            outside, target_is_directory=True
        )
        result = self.adopt("install")
        self.assertEqual(result.returncode, 2)
        self.assertEqual((outside / "sentinel").read_text(), "safe\n")

    def test_filesystem_root_target_is_rejected(self) -> None:
        result = run_script(ADOPT, "status", Path(Path.cwd().anchor))
        self.assertEqual(result.returncode, 2)
        self.assertIn("filesystem root", result.stderr)

    def test_status_treats_optional_files_as_normal_and_drift_as_repairable(
        self,
    ) -> None:
        self.assert_ok(self.adopt("install"))
        result = self.adopt("status")
        self.assert_ok(result)
        self.assertIn("Agent Workflow: healthy", result.stdout)
        self.assertEqual(list((self.project / ".agent-wayfinder").iterdir()), [])
        (self.project / ".agent-workflow/routing.md").unlink()
        result = self.adopt("status")
        self.assertEqual(result.returncode, 1)
        self.assertIn("repairable", result.stdout)

    def test_cp1252_console_escapes_unrepresentable_project_path(self) -> None:
        project = Path(self.temporary.name) / "project-snow-\u96ea"
        project.mkdir()
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"
        install = run_script(ADOPT, "install", project, env=env, encoding="cp1252")
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        status = run_script(ADOPT, "status", project, env=env, encoding="cp1252")
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertIn("\\u96ea", status.stdout)


if __name__ == "__main__":
    unittest.main()
