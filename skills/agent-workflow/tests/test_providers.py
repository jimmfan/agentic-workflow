from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from _test_support import (
    IMPLICIT_INVOCATION_SKILLS,
    LIFECYCLE,
    PACKAGE_ROOT,
    PROVIDERS,
    USER_ONLY_SKILLS,
    ProjectTestCase,
    load_module,
    run_script,
    tree_snapshot,
)

class ProviderTests(ProjectTestCase):
    def test_install_reconciles_safe_projection_drift_as_one_declared_set(self) -> None:
        declared = self.declared_provider_names()
        for case in ("damaged", "partial", "mixed"):
            with self.subTest(case=case):
                project = Path(self.temporary.name) / case
                project.mkdir()
                skills = project / ".agents/skills"
                if case == "damaged":
                    wayfinder = skills / "wayfinder"
                    wayfinder.mkdir(parents=True)
                    marker = wayfinder / "personal.txt"
                    marker.write_text("replace this declared projection\n")
                    command = PROVIDERS
                else:
                    self.assert_ok(run_script(PROVIDERS, "install", project))
                    if case == "partial":
                        retained = {
                            "setup-matt-pocock-skills",
                            "wayfinder",
                            "teach",
                            "research",
                        }
                        retained_bytes = {
                            name: tree_snapshot(skills / name) for name in retained
                        }
                        for name in declared - retained:
                            shutil.rmtree(skills / name)
                        command = LIFECYCLE
                    else:
                        marker = skills / "wayfinder/personal.txt"
                        marker.write_text("replace this declared projection\n")
                        shutil.rmtree(skills / "research")
                        command = PROVIDERS

                result = run_script(command, "update" if command == LIFECYCLE else "install", project)
                self.assert_ok(result)
                for name in declared:
                    self.assertTrue((skills / name / "SKILL.md").is_file(), name)
                if case in {"damaged", "mixed"}:
                    self.assertFalse(marker.exists())
                if case == "partial":
                    for name, snapshot in retained_bytes.items():
                        self.assertEqual(tree_snapshot(skills / name), snapshot)

    def test_unsafe_declared_provider_path_blocks_all_projection_changes(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        shutil.rmtree(self.project / ".agents/skills/research")
        shutil.rmtree(self.project / ".agents/skills/wayfinder")
        (self.project / ".agents/skills/wayfinder").write_text(
            "unsafe\n", encoding="utf-8"
        )

        result = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("blocked unsafe optional provider skill wayfinder", result.stderr)
        self.assertFalse((self.project / ".agents/skills/research").exists())

    def test_projection_failure_rolls_back_the_complete_changed_set(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        (self.project / ".agents/skills/wayfinder/personal.txt").write_text(
            "old bytes\n"
        )
        shutil.rmtree(self.project / ".agents/skills/research")
        before = tree_snapshot(self.project / ".agents/skills")

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_rollback_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)
        provider = module.load_provider()
        with tempfile.TemporaryDirectory(dir=self.project) as temporary:
            staged = module.prepare_staged_projection(Path(temporary), provider)
            original_move = module.move_path
            calls = 0

            def fail_third_move(source: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise OSError("injected projection failure")
                original_move(source, destination)

            module.move_path = fail_third_move
            with self.assertRaisesRegex(
                module.ProviderError, "prior projection restored"
            ):
                module.replace_projection(self.project, staged, list(provider.skills))

        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before)

    def test_projection_revalidates_every_declared_destination_before_mutation(
        self,
    ) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        shutil.rmtree(self.project / ".agents/skills/research")

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_full_preflight_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)
        original_state = module.projection_state
        declared_count = len(module.load_provider().skills)
        calls = 0

        def make_ready_destination_unsafe(
            root: Path, staged: Path, skill: object
        ) -> str:
            nonlocal calls
            state = original_state(root, staged, skill)
            calls += 1
            if calls == declared_count:
                shutil.rmtree(self.project / ".agents/skills/wayfinder")
                (self.project / ".agents/skills/wayfinder").write_text("unsafe\n")
            return state

        module.projection_state = make_ready_destination_unsafe
        with self.assertRaisesRegex(module.ProviderError, "wayfinder"):
            module.install(self.project, False)

        self.assertFalse((self.project / ".agents/skills/research").exists())
        self.assertEqual(
            (self.project / ".agents/skills/wayfinder").read_text(), "unsafe\n"
        )

    def test_replacement_cleanup_failure_reports_success_with_recovery_path(
        self,
    ) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        marker = self.project / ".agents/skills/wayfinder/personal.txt"
        marker.write_text("replace me\n")

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_replace_cleanup_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)
        provider = module.load_provider()
        original_rmtree = module.shutil.rmtree
        warning = io.StringIO()
        try:
            with tempfile.TemporaryDirectory(dir=self.project) as temporary:
                staged = module.prepare_staged_projection(Path(temporary), provider)

                def fail_recovery_cleanup(
                    path: object, *args: object, **kwargs: object
                ) -> None:
                    if Path(path).name.startswith(".agent-workflow-provider-rollback-"):
                        raise PermissionError("injected cleanup failure")
                    original_rmtree(path, *args, **kwargs)

                module.shutil.rmtree = fail_recovery_cleanup
                with redirect_stderr(warning):
                    changed = module.replace_projection(
                        self.project, staged, list(provider.skills)
                    )
        finally:
            module.shutil.rmtree = original_rmtree

        self.assertEqual([skill.name for skill in changed], ["wayfinder"])
        self.assertFalse(marker.exists())
        recovery = list(self.project.glob(".agent-workflow-provider-rollback-*"))
        self.assertEqual(len(recovery), 1)
        self.assertIn("replacement committed", warning.getvalue())
        original_rmtree(recovery[0])

    def test_removal_failure_rolls_back_every_moved_provider(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        before = tree_snapshot(self.project / ".agents/skills")

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_remove_rollback_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)
        original_move = module.move_path
        calls = 0

        def fail_second_move(source: Path, destination: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected removal failure")
            original_move(source, destination)

        module.move_path = fail_second_move
        output = io.StringIO()
        with (
            redirect_stdout(output),
            self.assertRaisesRegex(module.ProviderError, "prior projection restored"),
        ):
            module.remove(self.project, False)

        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before)
        self.assertNotIn(
            "removed declared optional provider directories", output.getvalue()
        )

    def test_removal_cleanup_failure_reports_success_with_recovery_path(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

        scripts_path = str(PROVIDERS.parent)
        sys.path.insert(0, scripts_path)
        try:
            module = load_module("providers_remove_cleanup_test", PROVIDERS)
        finally:
            sys.path.remove(scripts_path)
        provider = module.load_provider()
        original_rmtree = module.shutil.rmtree
        warning = io.StringIO()
        try:

            def fail_recovery_cleanup(
                path: object, *args: object, **kwargs: object
            ) -> None:
                if Path(path).name.startswith(".agent-workflow-provider-remove-"):
                    raise PermissionError("injected cleanup failure")
                original_rmtree(path, *args, **kwargs)

            module.shutil.rmtree = fail_recovery_cleanup
            with redirect_stderr(warning):
                removed = module.remove_projection(self.project, list(provider.skills))
        finally:
            module.shutil.rmtree = original_rmtree

        self.assertEqual(
            {skill.name for skill in removed}, self.declared_provider_names()
        )
        for name in self.declared_provider_names():
            self.assertFalse((self.project / ".agents/skills" / name).exists())
        recovery = list(self.project.glob(".agent-workflow-provider-remove-*"))
        self.assertEqual(len(recovery), 1)
        self.assertIn("removal committed", warning.getvalue())
        original_rmtree(recovery[0])

    def test_runtime_projection_does_not_enforce_release_snapshot_checksum(
        self,
    ) -> None:
        package_copy = self.copy_package("runtime-provider-checksum")
        snapshot = (
            package_copy
            / "provider-snapshots/matt-pocock-skills/skills/codebase-design/SKILL.md"
        )
        snapshot.write_text(
            snapshot.read_text(encoding="utf-8") + "\nrelease-content-drift\n",
            encoding="utf-8",
        )

        result = run_script(
            package_copy / "scripts/providers.py", "install", self.project
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "OK: Optional provider skills match the bundled projection.", result.stdout
        )
        projected = self.project / ".agents/skills/codebase-design/SKILL.md"
        self.assertTrue(
            projected.read_text(encoding="utf-8").endswith("\nrelease-content-drift\n")
        )

    def test_projection_adapters_apply_from_bundle_and_are_idempotent(
        self,
    ) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        before_second = tree_snapshot(self.project / ".agents/skills")
        second = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before_second)
        for name in IMPLICIT_INVOCATION_SKILLS:
            with self.subTest(skill=name):
                skill_text = (
                    self.project / ".agents/skills" / name / "SKILL.md"
                ).read_text(encoding="utf-8")
                openai_text = (
                    self.project / ".agents/skills" / name / "agents/openai.yaml"
                ).read_text(encoding="utf-8")
                self.assertIn("disable-model-invocation: false", skill_text)
                self.assertNotIn("disable-model-invocation: true", skill_text)
                self.assertIn("allow_implicit_invocation: true", openai_text)
                self.assertNotIn("allow_implicit_invocation: false", openai_text)
        for name in USER_ONLY_SKILLS:
            with self.subTest(skill=name):
                skill_text = (
                    self.project / ".agents/skills" / name / "SKILL.md"
                ).read_text(encoding="utf-8")
                openai_text = (
                    self.project / ".agents/skills" / name / "agents/openai.yaml"
                ).read_text(encoding="utf-8")
                self.assertIn("disable-model-invocation: true", skill_text)
                self.assertIn("allow_implicit_invocation: false", openai_text)

        skill_text = (self.project / ".agents/skills/grilling/SKILL.md").read_text(
            encoding="utf-8"
        )
        openai_text = (
            self.project / ".agents/skills/grilling/agents/openai.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "Grill the user through interdependent human/project-owned decisions whose answers "
            "materially shape downstream choices.",
            skill_text,
        )
        self.assertIn("explicitly asks to be grilled or stress-test", skill_text)
        self.assertIn(
            'short_description: "Resolve interdependent decisions through structured questions"',
            openai_text,
        )

        for name in (
            "issue-tracker-local.md",
            "issue-tracker-github.md",
            "issue-tracker-gitlab.md",
        ):
            with self.subTest(adapter="setup", file=name):
                projected = (
                    self.project / ".agents/skills/setup-matt-pocock-skills" / name
                ).read_text(encoding="utf-8")
                self.assertIn("## When a skill says", projected)
                self.assertNotIn("## Wayfinding operations", projected)

        research = " ".join(
            (self.project / ".agents/skills/research/SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )
        self.assertIn("Return sourced research findings in chat by default.", research)
        self.assertIn(
            "Do not create a standalone research file unless the user explicitly requests",
            research,
        )
        self.assertNotIn("Write the findings to a single Markdown file", research)

    def test_provider_status_reports_incomplete_and_modified_projections_read_only(
        self,
    ) -> None:
        result = run_script(PROVIDERS, "status", self.project)
        declaration = json.loads(
            (PACKAGE_ROOT / "payload/agent-workflow/providers.json").read_text(
                encoding="utf-8"
            )
        )
        declared_count = len(declaration["provider"]["skills"])

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            f"0 ready, {declared_count} repairable, 0 blocked",
            result.stdout,
        )

        self.assert_ok(run_script(PROVIDERS, "install", self.project))
        changed = self.project / ".agents/skills/wayfinder/personal.txt"
        changed.write_text("user change\n", encoding="utf-8")
        before = tree_snapshot(self.project / ".agents/skills")
        result = run_script(PROVIDERS, "status", self.project)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            f"{declared_count - 1} ready, 1 repairable, 0 blocked",
            result.stdout,
        )
        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before)

    def test_wayfinder_owned_runtime_projects_from_recognized_upstream_input(
        self,
    ) -> None:
        result = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        skill_path = self.project / ".agents/skills/wayfinder/SKILL.md"
        skill_text = skill_path.read_text(encoding="utf-8")
        frontmatter, body = skill_text[4:].split("\n---\n", 1)
        self.assertEqual(
            body,
            (PACKAGE_ROOT / "runtime-projections/wayfinder.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertIn(
            "disable-model-invocation: false",
            frontmatter,
        )
        self.assertIn(
            "description: Keep a lightweight structured map when important unresolved questions, choices,",
            frontmatter,
        )
        self.assertIn(
            "dependencies, blockers, or conflicting conclusions",
            frontmatter,
        )
        self.assertNotIn("important unknowns, decisions", frontmatter)
        openai_text = (
            self.project / ".agents/skills/wayfinder/agents/openai.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "allow_implicit_invocation: true",
            openai_text,
        )
        self.assertIn(
            'short_description: "Keep a lightweight map of complicated work"',
            openai_text,
        )

    def test_wayfinder_projection_repairs_raw_stale_and_metadata_drift(
        self,
    ) -> None:
        source = PACKAGE_ROOT / "provider-snapshots/matt-pocock-skills/skills/wayfinder"
        for case in ("raw-upstream", "stale-runtime", "metadata"):
            with self.subTest(case=case):
                project = Path(self.temporary.name) / case
                project.mkdir()
                state = project / ".agent-wayfinder/unrecognized-project-data"
                state.mkdir(parents=True)
                (state / "note.txt").write_bytes(b"preserve project state\n")
                original_state = tree_snapshot(project / ".agent-wayfinder")
                destination = project / ".agents/skills/wayfinder"
                if case == "raw-upstream":
                    destination.parent.mkdir(parents=True)
                    shutil.copytree(source, destination)
                else:
                    self.assert_ok(run_script(PROVIDERS, "install", project))
                    if case == "stale-runtime":
                        skill_path = destination / "SKILL.md"
                        frontmatter, _ = skill_path.read_text(encoding="utf-8").split(
                            "\n---\n", 1
                        )
                        skill_path.write_text(
                            frontmatter + "\n---\n# Wayfinder\n\nstale runtime\n",
                            encoding="utf-8",
                        )
                    else:
                        (destination / "agents/openai.yaml").write_text(
                            "policy:\n  allow_implicit_invocation: ask\n",
                            encoding="utf-8",
                        )

                result = run_script(PROVIDERS, "install", project)
                self.assert_ok(result)
                self.assertIn("reconciled optional provider skill wayfinder", result.stdout)
                repaired = (destination / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("disable-model-invocation: false", repaired)
                self.assertIn("## Operating rules", repaired)
                self.assertNotIn("stale runtime", repaired)
                self.assertIn(
                    "allow_implicit_invocation: true",
                    (destination / "agents/openai.yaml").read_text(encoding="utf-8"),
                )
                self.assertEqual(
                    tree_snapshot(project / ".agent-wayfinder"), original_state
                )

    def test_malformed_owned_runtime_source_fails_before_projection_mutation(
        self,
    ) -> None:
        install = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        before = tree_snapshot(self.project / ".agents/skills")
        package_copy = self.copy_package("malformed-wayfinder-runtime")
        projection = package_copy / "runtime-projections/wayfinder.md"
        projection.write_text("not a Wayfinder runtime\n", encoding="utf-8")

        result = run_script(
            package_copy / "scripts/providers.py", "install", self.project
        )

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("runtime projection is malformed", result.stderr)
        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before)

    def test_exact_existing_projection_is_reused_without_writing(self) -> None:
        first = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        before = tree_snapshot(self.project / ".agents/skills")

        second = run_script(PROVIDERS, "install", self.project)

        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("reuse exact optional provider skill wayfinder", second.stdout)
        self.assertEqual(tree_snapshot(self.project / ".agents/skills"), before)

    def test_provider_remove_deletes_only_declared_provider_directories(self) -> None:
        install = run_script(PROVIDERS, "install", self.project)
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        unrelated = self.project / ".agents/skills/my-local-skill/SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("local\n", encoding="utf-8")

        result = run_script(PROVIDERS, "remove", self.project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("removed declared optional provider directories", result.stdout)
        for name in self.declared_provider_names():
            self.assertFalse((self.project / ".agents/skills" / name).exists())
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "local\n")

    def test_provider_cli_rejects_non_string_configuration_requirements(self) -> None:
        package_copy = self.copy_package("provider-requirement-type")
        declaration = package_copy / "payload/agent-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        raw["provider"]["skills"][0]["requires_configuration"] = [{}]
        declaration.write_text(json.dumps(raw), encoding="utf-8")

        result = run_script(
            package_copy / "scripts/providers.py", "status", self.project
        )

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("invalid configuration requirements", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
