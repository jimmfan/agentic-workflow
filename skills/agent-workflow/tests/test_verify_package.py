from __future__ import annotations

import json
from pathlib import Path
import unittest

from _test_support import (
    PACKAGE_ROOT,
    REFRESH_PROVIDERS,
    ProjectTestCase,
    load_module,
    run_script,
)


class VerifyPackageTests(ProjectTestCase):
    def test_verifier_requires_the_source_only_project_language_glossary(self) -> None:
        package_copy = self.copy_package("missing-source-language")
        (package_copy.parents[1] / "CONTEXT.md").unlink()

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("source terminology glossary is missing", verify.stderr)

    def test_payload_content_edits_need_no_manifest_refresh(self) -> None:
        package_copy = self.copy_package("mapping-change")

        source = package_copy / "payload/agent-workflow/README.md"
        source.write_text(
            source.read_text(encoding="utf-8")
            + "\nCurrent package bytes are authoritative.\n",
            encoding="utf-8",
        )

        runtime = run_script(package_copy / "scripts/adopt.py", "install", self.project)
        self.assertEqual(runtime.returncode, 0, runtime.stdout + runtime.stderr)
        self.assertEqual(
            (self.project / ".agent-workflow/README.md").read_bytes(),
            source.read_bytes(),
        )

        verify = run_script(package_copy / "scripts/verify_package.py")
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_verifier_rejects_unmapped_payload_surfaces(self) -> None:
        package_copy = self.copy_package("unmapped-payload")
        unmapped = package_copy / "payload/agent-workflow/contracts/new-contract.md"
        unmapped.write_text("# Newly packaged contract\n", encoding="utf-8")
        for arguments in ((), ("--refresh-manifest",)):
            with self.subTest(arguments=arguments):
                result = run_script(
                    package_copy / "scripts/verify_package.py", *arguments
                )
                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "authored payload differs from the exact current package surface",
                    result.stderr,
                )

    def test_version_file_drives_verification_and_install_metadata(self) -> None:
        package_copy = self.copy_package("version-source")
        (package_copy / "VERSION").write_text("9.8.7\n", encoding="utf-8")

        verify = run_script(package_copy / "scripts/verify_package.py")
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

        install = run_script(
            package_copy / "scripts/adopt.py", "install", self.project
        )
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        installed = json.loads(
            (self.project / ".agent-workflow/install-manifest.json").read_text()
        )
        self.assertEqual(installed["framework_version"], "9.8.7")

    def test_verifier_rejects_duplicate_payload_version(self) -> None:
        duplicate = self.copy_package("duplicate-payload-version")
        (duplicate / "payload/VERSION").write_text("0.0.0\n", encoding="utf-8")
        verify = run_script(duplicate / "scripts/verify_package.py")
        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("payload/VERSION must remain absent", verify.stderr)

    def test_verifier_rejects_activation_sensitive_payload_paths(self) -> None:
        cases = (
            ("literal-root-policy", "payload/root/AGENTS.md"),
            ("literal-nested-policy", "payload/skills/example/CLAUDE.md"),
            ("host-customization-tree", "payload/.agents/skills/example/SKILL.md"),
        )
        for name, relative in cases:
            with self.subTest(relative=relative):
                package_copy = self.copy_package(name)
                path = package_copy / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("activation-sensitive fixture\n", encoding="utf-8")

                verify = run_script(package_copy / "scripts/verify_package.py")

                self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
                self.assertIn("activation-sensitive payload path", verify.stderr)

    def test_verifier_rejects_incomplete_provider_declarations(self) -> None:
        package_copy = self.copy_package("provider-declaration")
        declaration = package_copy / "payload/agent-workflow/providers.json"
        valid = json.loads(declaration.read_text(encoding="utf-8"))
        declared = {item["name"]: item for item in valid["provider"]["skills"]}
        self.assertEqual(declared["implement"]["requires_configuration"], [])
        self.assertEqual(declared["code-review"]["requires_configuration"], [])
        self.assertIn(
            "issue-tracker", declared["to-spec"]["requires_configuration"]
        )
        self.assertIn(
            "issue-tracker", declared["to-tickets"]["requires_configuration"]
        )

        cases = (
            ("empty skill name", "name", "", "invalid provider skill name"),
            ("missing skill path", "path", None, "needs a path"),
            (
                "incomplete invocation hosts",
                "invocation",
                {},
                "invocation hosts differ",
            ),
            (
                "unknown configuration requirement",
                "requires_configuration",
                ["not-declared"],
                "invalid configuration requirements",
            ),
            (
                "non-string configuration requirement",
                "requires_configuration",
                [{}],
                "invalid configuration requirements",
            ),
        )
        for label, field, value, expected in cases:
            with self.subTest(label=label):
                candidate = json.loads(json.dumps(valid))
                skill = candidate["provider"]["skills"][0]
                if value is None:
                    skill.pop(field)
                else:
                    skill[field] = value
                declaration.write_text(json.dumps(candidate), encoding="utf-8")
                verify = run_script(package_copy / "scripts/verify_package.py")
                self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
                self.assertIn(expected, verify.stderr)

    def test_verifier_requires_each_declared_projection_adapter(self) -> None:
        cases = (
            ("wayfinder", "Wayfinder must declare"),
            (
                "setup-matt-pocock-skills",
                "setup must declare the current-coordination adapter",
            ),
            ("implement", "implement must declare the implicit-invocation adapter"),
            ("grilling", "grilling must declare the discovery adapter"),
            ("research", "research must declare the chat-output adapter"),
        )
        for name, expected in cases:
            with self.subTest(skill=name):
                package_copy = self.copy_package(f"missing-{name}-adapter")
                declaration = package_copy / "payload/agent-workflow/providers.json"
                raw = json.loads(declaration.read_text(encoding="utf-8"))
                skill = next(
                    item for item in raw["provider"]["skills"] if item["name"] == name
                )
                skill.pop("agent_workflow_adapter")
                if name == "wayfinder":
                    skill["invocation"] = {
                        host: "user-only" for host in skill["invocation"]
                    }
                declaration.write_text(json.dumps(raw), encoding="utf-8")
                verify = run_script(package_copy / "scripts/verify_package.py")
                self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
                self.assertIn(expected, verify.stderr)

    def test_verifier_rejects_conflicting_owned_wayfinder_runtime_content(self) -> None:
        package_copy = self.copy_package("conflicting-wayfinder-runtime")
        projection = package_copy / "runtime-projections/wayfinder.md"
        projection.write_text(
            projection.read_text(encoding="utf-8")
            + "\nEach ticket is a **child issue** of the map.\n",
            encoding="utf-8",
        )

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn(
            "owned Wayfinder runtime contains incompatible tracker mechanics",
            verify.stderr,
        )

    def test_verifier_rejects_retired_owned_wayfinder_runtime_language(self) -> None:
        package_copy = self.copy_package("retired-wayfinder-language")
        projection = package_copy / "runtime-projections/wayfinder.md"
        projection.write_text(
            projection.read_text(encoding="utf-8")
            + "\nThe ready frontier is available.\n",
            encoding="utf-8",
        )

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn(
            "owned Wayfinder runtime retains retired canonical language",
            verify.stderr,
        )

    def test_verifier_allows_quoted_provider_frontier_language(self) -> None:
        package_copy = self.copy_package("quoted-provider-language")
        projection = package_copy / "runtime-projections/wayfinder.md"
        projection.write_text(
            projection.read_text(encoding="utf-8")
            + "\nThe pinned provider calls its tracker concept `frontier`.\n",
            encoding="utf-8",
        )

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_verifier_rejects_provider_snapshot_checksum_drift(self) -> None:
        package_copy = self.copy_package("provider-snapshot-integrity")
        snapshot = (
            package_copy
            / "provider-snapshots/matt-pocock-skills/skills/research/SKILL.md"
        )
        original = snapshot.read_bytes()
        snapshot.write_bytes(original + b"\ncorrupt\n")

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("snapshot checksum", verify.stderr)

    def test_verifier_rejects_provider_provenance_drift(self) -> None:
        package_copy = self.copy_package("provider-provenance")
        declaration = package_copy / "payload/agent-workflow/providers.json"
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        raw["provider"]["resolved_commit"] = "0" * 40
        declaration.write_text(json.dumps(raw), encoding="utf-8")

        verify = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("resolved_commit", verify.stderr)

    def test_verifier_rejects_source_and_installed_declaration_drift(self) -> None:
        parity_copy = self.copy_package("provider-declaration-parity")
        installed = parity_copy.parents[1] / ".agent-workflow/providers.json"
        installed.parent.mkdir()
        installed.write_text("{}\n", encoding="utf-8")
        verify = run_script(parity_copy / "scripts/verify_package.py")
        self.assertEqual(verify.returncode, 1, verify.stdout + verify.stderr)
        self.assertIn("source and packaged provider declarations differ", verify.stderr)

    def test_provider_snapshot_references_cannot_escape_the_skill(self) -> None:
        snapshot_module = load_module(
            "agent_workflow_provider_snapshot",
            PACKAGE_ROOT / "scripts/provider_snapshot.py",
        )
        skill = Path(self.temporary.name) / "referencing-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "Use [shared](../shared.md).\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(snapshot_module.SnapshotTreeError, "escape"):
            snapshot_module.validate_local_references(skill)

    def test_provider_refresh_refuses_to_write_inside_the_package(self) -> None:
        candidate = PACKAGE_ROOT / "candidate-provider-snapshot"
        self.assertFalse(candidate.exists())

        result = run_script(REFRESH_PROVIDERS, candidate)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("outside the Agent Workflow package", result.stderr)
        self.assertFalse(candidate.exists())

    def test_provider_refresh_accepts_exact_commit_tree_bytes(self) -> None:
        refresh, output = self.run_fake_provider_refresh("exact-provider-refresh")

        refresh.generate(output)

        self.assertTrue((output / "skills/demo/SKILL.md").is_file())

    def test_provider_refresh_rejects_drifted_commit_tree_bytes(self) -> None:
        for mutation in ("modified", "extra", "extra-directory"):
            with self.subTest(mutation=mutation):
                refresh, output = self.run_fake_provider_refresh(
                    f"{mutation}-provider-refresh",
                    mutation=mutation,
                )

                with self.assertRaisesRegex(refresh.RefreshError, "pinned commit tree"):
                    refresh.generate(output)

                self.assertFalse(output.exists())

    def test_verifier_ignores_existing_cache_and_does_not_add_cache_files(self) -> None:
        package_copy = self.copy_package("verifier-bytecode")
        cache = package_copy / "scripts/__pycache__"
        cache.mkdir(exist_ok=True)
        generated = cache / "local-test.cpython-311.pyc"
        generated.write_bytes(b"generated test cache\n")
        before = {
            path.name: path.read_bytes() for path in cache.iterdir() if path.is_file()
        }

        result = run_script(package_copy / "scripts/verify_package.py")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {
            path.name: path.read_bytes() for path in cache.iterdir() if path.is_file()
        }
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
