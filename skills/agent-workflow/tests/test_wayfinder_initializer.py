from __future__ import annotations

from pathlib import Path
import re
import resource
import signal
import subprocess
import sys
import tempfile

from _test_support import LIFECYCLE, ProjectTestCase, run_script, tree_snapshot


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
SCHEMA = PACKAGE_ROOT / "payload/agent-workflow/schemas/wayfinder/map.md"
HELPER = PACKAGE_ROOT / "payload/agent-workflow/tools/wayfinder.py"
INSTALLED_SCHEMA = REPOSITORY_ROOT / ".agent-workflow/schemas/wayfinder/map.md"
INSTALLED_HELPER = REPOSITORY_ROOT / ".agent-workflow/tools/wayfinder.py"

CANONICAL_SCHEMA = """# {{WAYFINDER_EFFORT_NAME}}

## Objective

{{REQUIRED_OBJECTIVE}}

## Scope

{{REQUIRED_SCOPE}}

## Ready work

None.

## Current state

{{REQUIRED_CURRENT_STATE}}

## Dependencies

None.

## Blockers

None.

## Ownership

None.

## Key references

None.
"""


class WayfinderInitializerTests(ProjectTestCase):
    def install(self) -> Path:
        result = run_script(LIFECYCLE, "install", self.project)
        self.assert_ok(result)
        return self.project / ".agent-workflow/tools/wayfinder.py"

    def init_effort(
        self,
        helper: Path,
        effort: str = "platform-migration",
        name: str = "Platform migration",
    ):
        return run_script(
            helper,
            "init-effort",
            "--effort",
            effort,
            "--name",
            name,
            cwd=self.project,
        )

    def test_schema_and_helper_are_packaged_and_installed(self) -> None:
        self.assertEqual(SCHEMA.read_text(encoding="utf-8"), CANONICAL_SCHEMA)
        self.assertTrue(HELPER.is_file())

        self.install()

        installed_schema = self.project / ".agent-workflow/schemas/wayfinder/map.md"
        installed_helper = self.project / ".agent-workflow/tools/wayfinder.py"
        self.assertEqual(installed_schema.read_bytes(), SCHEMA.read_bytes())
        self.assertEqual(installed_helper.read_bytes(), HELPER.read_bytes())

    def test_init_effort_creates_only_the_canonical_map_in_a_non_git_project(
        self,
    ) -> None:
        helper = self.install()

        result = self.init_effort(helper)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            "CREATED .agent-wayfinder/platform-migration/map.md\n",
        )
        self.assertEqual(result.stderr, "")
        effort = self.project / ".agent-wayfinder/platform-migration"
        self.assertEqual(
            [path.name for path in effort.iterdir()],
            ["map.md"],
        )
        self.assertFalse((self.project / ".git").exists())

        generated = (effort / "map.md").read_text(encoding="utf-8")
        self.assertEqual(
            generated,
            CANONICAL_SCHEMA.replace("{{WAYFINDER_EFFORT_NAME}}", "Platform migration"),
        )
        self.assertEqual(
            re.findall(r"^## (.+)$", generated, re.MULTILINE),
            [
                "Objective",
                "Scope",
                "Ready work",
                "Current state",
                "Dependencies",
                "Blockers",
                "Ownership",
                "Key references",
            ],
        )
        for placeholder in (
            "{{REQUIRED_OBJECTIVE}}",
            "{{REQUIRED_SCOPE}}",
            "{{REQUIRED_CURRENT_STATE}}",
        ):
            self.assertEqual(generated.count(placeholder), 1)
        for empty_heading in (
            "Ready work",
            "Dependencies",
            "Blockers",
            "Ownership",
            "Key references",
        ):
            section = generated.split(f"## {empty_heading}\n\n", 1)[1]
            section = section.split("\n\n## ", 1)[0]
            self.assertEqual(section.rstrip("\n"), "None.")

    def test_existing_effort_targets_are_never_overwritten_or_repurposed(self) -> None:
        helper = self.install()
        effort = self.project / ".agent-wayfinder/existing-effort"
        effort.mkdir(parents=True)
        existing_map = effort / "map.md"
        existing_map.write_bytes(b"# Existing\n\nProject-owned bytes.\n")
        before = tree_snapshot(self.project / ".agent-wayfinder")

        result = self.init_effort(helper, "existing-effort", "Replacement")

        self.assertEqual(result.returncode, 2)
        self.assertIn("effort already exists", result.stderr)
        self.assertEqual(tree_snapshot(self.project / ".agent-wayfinder"), before)

        mapless = self.project / ".agent-wayfinder/mapless-effort"
        mapless.mkdir()
        note = mapless / "project-note.txt"
        note.write_bytes(b"keep exactly\n")
        before = tree_snapshot(self.project / ".agent-wayfinder")

        result = self.init_effort(helper, "mapless-effort", "Mapless")

        self.assertEqual(result.returncode, 2)
        self.assertIn("effort already exists", result.stderr)
        self.assertEqual(tree_snapshot(self.project / ".agent-wayfinder"), before)

    def test_unsafe_effort_keys_fail_before_creating_wayfinder_state(self) -> None:
        helper = self.install()

        for effort in (
            "",
            ".",
            "..",
            "../escape",
            "two/parts",
            "Uppercase",
            "leading-",
            "under_score",
        ):
            with self.subTest(effort=effort):
                result = self.init_effort(helper, effort, "Unsafe")
                self.assertEqual(result.returncode, 2)
                self.assertIn("unsafe effort storage key", result.stderr)
                self.assertFalse((self.project / ".agent-wayfinder").exists())

    def test_unsafe_effort_names_fail_before_creating_wayfinder_state(self) -> None:
        helper = self.install()

        for name in ("", " surrounding whitespace ", "multiple\nlines", "delete\x7f"):
            with self.subTest(name=name):
                result = self.init_effort(helper, name=name)
                self.assertEqual(result.returncode, 2)
                self.assertIn("effort name must be", result.stderr)
                self.assertFalse((self.project / ".agent-wayfinder").exists())

    def test_unreadable_schema_fails_before_creating_wayfinder_state(self) -> None:
        helper = self.install()
        schema = self.project / ".agent-workflow/schemas/wayfinder/map.md"
        schema.write_bytes(b"\xff")

        result = self.init_effort(helper)

        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot read Wayfinder map schema", result.stderr)
        self.assertFalse((self.project / ".agent-wayfinder").exists())

    def test_failed_map_write_cleans_only_newly_created_state(self) -> None:
        helper = self.install()
        root = self.project / ".agent-wayfinder"
        root.mkdir()
        sentinel = root / "project-owned.txt"
        sentinel.write_bytes(b"preserve exactly\n")
        before = tree_snapshot(root)

        def limit_file_size() -> None:
            signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
            resource.setrlimit(resource.RLIMIT_FSIZE, (1, 1))

        result = subprocess.run(
            [
                sys.executable,
                str(helper),
                "init-effort",
                "--effort",
                "failed-write",
                "--name",
                "Failed write",
            ],
            text=True,
            capture_output=True,
            cwd=self.project,
            check=False,
            preexec_fn=limit_file_size,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot create Wayfinder map", result.stderr)
        self.assertEqual(tree_snapshot(root), before)

    def test_wayfinder_symlink_boundaries_fail_without_mutating_targets(self) -> None:
        helper = self.install()
        with tempfile.TemporaryDirectory() as temporary:
            outside = Path(temporary) / "outside"
            outside.mkdir()
            sentinel = outside / "sentinel.txt"
            sentinel.write_bytes(b"outside bytes\n")
            root = self.project / ".agent-wayfinder"
            root.symlink_to(outside, target_is_directory=True)

            result = self.init_effort(helper)

            self.assertEqual(result.returncode, 2)
            self.assertIn("symlink", result.stderr)
            self.assertEqual(sentinel.read_bytes(), b"outside bytes\n")
            self.assertFalse((outside / "platform-migration").exists())

            root.unlink()
            root.mkdir()
            (root / "platform-migration").symlink_to(outside, target_is_directory=True)
            before = tree_snapshot(root)

            result = self.init_effort(helper)

            self.assertEqual(result.returncode, 2)
            self.assertIn("effort already exists", result.stderr)
            self.assertEqual(tree_snapshot(root), before)
            self.assertEqual(sentinel.read_bytes(), b"outside bytes\n")

    def test_lifecycle_update_leaves_initialized_state_opaque(self) -> None:
        helper = self.install()
        self.assert_ok(self.init_effort(helper, "opaque-state", "Opaque state"))
        map_path = self.project / ".agent-wayfinder/opaque-state/map.md"
        map_path.write_bytes(
            b"# Existing shape\n\n## Destination\n\nPreserve these bytes.\n"
        )
        before = tree_snapshot(self.project / ".agent-wayfinder")

        result = run_script(LIFECYCLE, "update", self.project)

        self.assert_ok(result)
        self.assertEqual(tree_snapshot(self.project / ".agent-wayfinder"), before)

    def test_checked_in_schema_and_helper_match_the_authored_payload(self) -> None:
        self.assertEqual(INSTALLED_SCHEMA.read_bytes(), SCHEMA.read_bytes())
        self.assertEqual(INSTALLED_HELPER.read_bytes(), HELPER.read_bytes())


if __name__ == "__main__":
    import unittest

    unittest.main()
