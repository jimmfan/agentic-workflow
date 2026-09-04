from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest

from _test_support import ProjectTestCase, run_script


class VerifyPackageTests(ProjectTestCase):
    def verify(
        self, package: Path, *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        return run_script(package / "scripts/verify_package.py", *arguments)

    def assert_verify_failure(
        self, package: Path, expected: str, *arguments: str
    ) -> None:
        result = self.verify(package, *arguments)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected, result.stderr)

    def replace_once(
        self, package: Path, relative: str, original: str, replacement: str
    ) -> None:
        path = package / relative
        text = path.read_text(encoding="utf-8")
        self.assertEqual(
            text.count(original), 1, f"unexpected fixture text in {relative}"
        )
        path.write_text(text.replace(original, replacement), encoding="utf-8")

    def sync_projection(
        self, package: Path, source_relative: str, target_relative: str
    ) -> None:
        source = package / "payload" / source_relative
        target = package.parents[1] / target_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())

    def test_verifier_accepts_the_current_direct_distribution(self) -> None:
        package = self.copy_package("current-direct-distribution")

        result = self.verify(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_distribution_manifest_is_only_the_current_source_target_map(self) -> None:
        package = self.copy_package("current-map-only")
        manifest = json.loads(
            (package / "payload/distribution/manifest.json").read_text(encoding="utf-8")
        )

        self.assertEqual(set(manifest), {"schema_version", "framework_owned"})
        self.assertTrue(manifest["framework_owned"])
        self.assertTrue(
            all(
                set(mapping) == {"source", "target"}
                for mapping in manifest["framework_owned"]
            )
        )

        manifest["install_history"] = []
        (package / "payload/distribution/manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.assert_verify_failure(
            package, "distribution manifest contains installation history"
        )

    def test_payload_content_edits_need_no_manifest_refresh(self) -> None:
        package = self.copy_package("content-change")
        manifest = package / "payload/distribution/manifest.json"
        manifest_before = manifest.read_bytes()
        source = package / "payload/agent-workflow/README.md"
        source.write_text(
            source.read_text(encoding="utf-8")
            + "\nCurrent package bytes are authoritative.\n",
            encoding="utf-8",
        )
        self.sync_projection(
            package,
            "agent-workflow/README.md",
            ".agent-workflow/README.md",
        )

        result = self.verify(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(manifest.read_bytes(), manifest_before)

    def test_verifier_rejects_unmapped_payload_surfaces(self) -> None:
        package = self.copy_package("unmapped-payload")
        unmapped = package / "payload/agent-workflow/contracts/new-contract.md"
        unmapped.write_text("# Newly packaged contract\n", encoding="utf-8")

        self.assert_verify_failure(
            package,
            "authored payload differs from the exact current package surface",
        )

    def test_package_version_is_the_only_version_source(self) -> None:
        package = self.copy_package("version-source")
        (package / "VERSION").write_text("9.8.7\n", encoding="utf-8")

        result = self.verify(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        (package / "payload/VERSION").write_text("9.8.7\n", encoding="utf-8")
        self.assert_verify_failure(package, "payload/VERSION must remain absent")

    def test_verifier_rejects_activation_sensitive_payload_paths(self) -> None:
        cases = (
            ("literal-root-policy", "payload/root/AGENTS.md"),
            ("literal-nested-policy", "payload/skills/example/CLAUDE.md"),
            ("host-customization-tree", "payload/.agents/skills/example/SKILL.md"),
        )
        for name, relative in cases:
            with self.subTest(relative=relative):
                package = self.copy_package(name)
                path = package / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("activation-sensitive fixture\n", encoding="utf-8")

                self.assert_verify_failure(package, "activation-sensitive payload path")

    def test_verifier_requires_complete_curated_skill_directories(self) -> None:
        missing = self.copy_package("missing-skill-file")
        (missing / "payload/skills/tdd/tests.md").unlink()
        self.assert_verify_failure(missing, "curated skill tdd is incomplete")

        extra = self.copy_package("extra-skill-file")
        (extra / "payload/skills/research/notes.md").write_text(
            "unexpected\n", encoding="utf-8"
        )
        self.assert_verify_failure(
            extra, "curated skill research is incomplete or contains unexpected files"
        )

        wrong_name = self.copy_package("wrong-skill-name")
        self.replace_once(
            wrong_name,
            "payload/skills/research/SKILL.md",
            "name: research",
            "name: not-research",
        )
        self.assert_verify_failure(
            wrong_name, "curated skill name differs from its directory"
        )

    def test_domain_modeling_has_no_generic_adr_support_surface(self) -> None:
        package = self.copy_package("domain-modeling-without-adr-support")
        domain_root = package / "payload/skills/domain-modeling"
        manifest = json.loads(
            (package / "payload/distribution/manifest.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            {path.name for path in domain_root.iterdir() if path.is_file()},
            {"CONTEXT-FORMAT.md", "SKILL.md"},
        )
        self.assertFalse(
            (
                package.parents[1] / ".agents/skills/domain-modeling/ADR-FORMAT.md"
            ).exists()
        )
        self.assertNotIn(
            "skills/domain-modeling/ADR-FORMAT.md",
            {item["source"] for item in manifest["framework_owned"]},
        )

        result = self.verify(package)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verifier_does_not_lock_skill_descriptions(self) -> None:
        package = self.copy_package("description-copy")
        self.replace_once(
            package,
            "payload/skills/research/SKILL.md",
            "description: Investigate substantive questions against high-trust primary sources and return cited findings in chat. Create a repository artifact only when the user explicitly requests durable research output.",
            "description: Research substantive questions and return cited findings.",
        )
        self.sync_projection(
            package,
            "skills/research/SKILL.md",
            ".agents/skills/research/SKILL.md",
        )

        result = self.verify(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verifier_does_not_apply_a_broad_prose_blacklist(self) -> None:
        package = self.copy_package("historical-prose")
        readme = package.parents[1] / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8")
            + "\nHistorical note: the former provider-native design was replaced.\n",
            encoding="utf-8",
        )

        result = self.verify(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verifier_rejects_missing_and_escaping_skill_links(self) -> None:
        cases = (
            (
                "missing-link",
                "[Missing support](missing-support.md)",
                "curated skill link target is missing",
            ),
            (
                "escaping-link",
                "[Another skill](../wayfinder/SKILL.md)",
                "curated skill link escapes its skill root",
            ),
        )
        for name, link, expected in cases:
            with self.subTest(name=name):
                package = self.copy_package(name)
                path = package / "payload/skills/research/SKILL.md"
                path.write_text(
                    path.read_text(encoding="utf-8") + f"\n{link}\n",
                    encoding="utf-8",
                )
                self.assert_verify_failure(package, expected)

    def test_verifier_requires_complete_third_party_attribution(self) -> None:
        cases = (
            (
                "current-skill",
                "`code-review`, ",
                "",
                "third-party notice omits attributed skill",
            ),
            (
                "upstream-repository",
                "https://github.com/mattpocock/skills",
                "https://example.invalid/upstream",
                "third-party attribution lacks",
            ),
            (
                "upstream-release",
                "release `v1.2.3`",
                "an upstream release",
                "third-party attribution lacks",
            ),
            (
                "copyright",
                "Copyright (c) 2026 Matt Pocock",
                "Copyright omitted",
                "third-party attribution lacks",
            ),
            (
                "license",
                "Permission is hereby granted, free of charge",
                "Permission is granted",
                "canonical MIT permission terms",
            ),
            (
                "disclaimer",
                'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR',
                "THE SOFTWARE HAS NO WARRANTY",
                "canonical MIT warranty disclaimer",
            ),
        )
        for name, original, replacement, expected in cases:
            with self.subTest(name=name):
                package = self.copy_package(f"attribution-{name}")
                self.replace_once(
                    package,
                    "payload/agent-workflow/README.md",
                    original,
                    replacement,
                )
                self.assert_verify_failure(package, expected)

    def test_verifier_enforces_only_load_bearing_semantic_contracts(self) -> None:
        cases = (
            (
                "research-write-authorization",
                "payload/skills/research/SKILL.md",
                "writes have action authorization",
                "writes are convenient",
                "Research lacks load-bearing contract",
            ),
            (
                "research-does-not-choose",
                "payload/skills/research/SKILL.md",
                "does not select the project's preferred alternative",
                "selects the project's preferred alternative",
                "Research lacks load-bearing contract",
            ),
            (
                "discovery-owns-bounded-architecture-choice",
                "payload/skills/workflow-discovery/SKILL.md",
                "An architectural decision is one possible kind of consequential project choice",
                "An architectural decision belongs to Domain Modeling",
                "Discovery lacks load-bearing contract",
            ),
            (
                "discovery-does-not-store-architecture-decisions",
                "payload/skills/workflow-discovery/SKILL.md",
                "Discovery does not maintain architecture decision records or durable coordination state.",
                "Discovery maintains architecture decision records.",
                "Discovery lacks load-bearing contract",
            ),
            (
                "wayfinder-sole-coordinator",
                "payload/skills/wayfinder/SKILL.md",
                "sole durable coordination layer",
                "a durable coordination layer",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "wayfinder-objective-alone-is-insufficient",
                "payload/skills/wayfinder/SKILL.md",
                "An objective alone does not select Wayfinder.",
                "An objective selects Wayfinder.",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "wayfinder-scope-refinement-keeps-effort",
                "payload/skills/wayfinder/SKILL.md",
                "clarified, narrowed, or elaborated",
                "frozen after creation",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "wayfinder-references-lasting-results",
                "payload/skills/wayfinder/SKILL.md",
                "Reference the artifacts that maintain",
                "Copy the artifacts that maintain",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "to-spec-destination-and-authorization",
                "payload/skills/to-spec/SKILL.md",
                "destination named by the user",
                "available publication destination",
                "to-spec lacks load-bearing contract",
            ),
            (
                "to-tickets-destination-and-authorization",
                "payload/skills/to-tickets/SKILL.md",
                "Publish only when",
                "Publish whenever a destination is available",
                "to-tickets lacks load-bearing contract",
            ),
            (
                "implement-commit-authorization",
                "payload/skills/implement/SKILL.md",
                "Commit only when the current user request",
                "Commit whenever the current user request",
                "Implement lacks load-bearing contract",
            ),
            (
                "root-route-marker",
                "payload/root/AGENTS.md.template",
                "Report only what executed",
                "Report what was selected",
                "Root routing lacks load-bearing contract",
            ),
            (
                "detailed-route-marker",
                "payload/agent-workflow/routing.md",
                "include it in the route marker only when its method actually ran",
                "include it in the route marker when selected",
                "Routing lacks load-bearing contract",
            ),
        )
        for name, relative, original, replacement, expected in cases:
            with self.subTest(name=name):
                package = self.copy_package(name)
                self.replace_once(package, relative, original, replacement)
                self.assert_verify_failure(package, expected)

        for skill in ("to-spec", "to-tickets"):
            with self.subTest(name=f"{skill}-hard-coded-label"):
                package = self.copy_package(f"{skill}-hard-coded-label")
                path = package / f"payload/skills/{skill}/SKILL.md"
                path.write_text(
                    path.read_text(encoding="utf-8")
                    + "\nApply the ready-for-agent label.\n",
                    encoding="utf-8",
                )
                self.assert_verify_failure(
                    package, f"{skill} hard-codes the ready-for-agent label"
                )

        domain_adr = self.copy_package("domain-modeling-generic-adr")
        domain_path = domain_adr / "payload/skills/domain-modeling/SKILL.md"
        domain_path.write_text(
            domain_path.read_text(encoding="utf-8")
            + "\nRecord an architectural decision in docs/adr/.\n",
            encoding="utf-8",
        )
        self.assert_verify_failure(
            domain_adr, "Domain Modeling retains generic ADR responsibility"
        )

    def test_verifier_rejects_checked_in_projection_drift_and_history(self) -> None:
        drift = self.copy_package("checked-projection-drift")
        installed = drift.parents[1] / ".agents/skills/research/SKILL.md"
        installed.write_text(
            installed.read_text(encoding="utf-8") + "\nlocal drift\n",
            encoding="utf-8",
        )
        self.assert_verify_failure(
            drift, "checked-in projection differs from direct payload"
        )

        history = self.copy_package("checked-history")
        (history.parents[1] / ".agent-workflow/install-manifest.json").write_text(
            "{}\n", encoding="utf-8"
        )
        self.assert_verify_failure(
            history, "checked-in projection must not contain an install manifest"
        )

        malformed_composite = self.copy_package("checked-composite-markers")
        agents = malformed_composite.parents[1] / "AGENTS.md"
        agents.write_bytes(
            agents.read_bytes().replace(
                b"<!-- agent-workflow:managed-end -->\n",
                b"\n",
                1,
            )
        )
        self.assert_verify_failure(
            malformed_composite, "checked-in composite has invalid managed markers"
        )

        extra_prefix = self.copy_package("checked-composite-extra-prefix")
        agents = extra_prefix.parents[1] / "AGENTS.md"
        agents.write_bytes(
            agents.read_bytes() + b"\n<!-- agent-workflow:partial-marker"
        )
        self.assert_verify_failure(
            extra_prefix, "checked-in composite has invalid managed markers"
        )

    def test_verifier_ignores_unrelated_project_skill_projection(self) -> None:
        package = self.copy_package("unrelated-projected-skill")
        unrelated = package.parents[1] / ".agents/skills/project-local"
        unrelated.mkdir(parents=True)
        (unrelated / "SKILL.md").write_text(
            "---\nname: project-local\ndescription: Project-owned skill.\n---\n",
            encoding="utf-8",
        )

        result = self.verify(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verifier_ignores_existing_cache_and_does_not_add_cache_files(self) -> None:
        package = self.copy_package("verifier-bytecode")
        cache = package / "scripts/__pycache__"
        cache.mkdir(exist_ok=True)
        generated = cache / "local-test.cpython-311.pyc"
        generated.write_bytes(b"generated test cache\n")
        before = {
            path.name: path.read_bytes() for path in cache.iterdir() if path.is_file()
        }

        result = self.verify(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {
            path.name: path.read_bytes() for path in cache.iterdir() if path.is_file()
        }
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
