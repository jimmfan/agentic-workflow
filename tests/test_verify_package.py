from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest

from _test_support import ProjectTestCase, run_script


class VerifyPackageTests(ProjectTestCase):
    def verify(self, source: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return run_script(source / "agent_workflow/verify_package.py", *arguments)

    def assert_verify_failure(
        self, source: Path, expected: str, *arguments: str
    ) -> None:
        result = self.verify(source, *arguments)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected, result.stderr)

    def replace_once(
        self, source: Path, relative: str, original: str, replacement: str
    ) -> None:
        path = source / relative
        text = path.read_text(encoding="utf-8")
        self.assertEqual(
            text.count(original), 1, f"unexpected fixture text in {relative}"
        )
        path.write_text(text.replace(original, replacement), encoding="utf-8")

    def test_verifier_accepts_the_current_direct_distribution(self) -> None:
        source = self.copy_source("current-direct-distribution")

        result = self.verify(source)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_distribution_manifest_is_only_the_current_source_target_map(self) -> None:
        source = self.copy_source("current-map-only")
        manifest = json.loads(
            (source / "agent_workflow/install/manifest.json").read_text(
                encoding="utf-8"
            )
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
        (source / "agent_workflow/install/manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.assert_verify_failure(
            source, "distribution manifest contains installation history"
        )

    def test_canonical_content_edits_need_no_manifest_refresh(self) -> None:
        source = self.copy_source("content-change")
        manifest = source / "agent_workflow/install/manifest.json"
        manifest_before = manifest.read_bytes()
        readme = source / ".agent-workflow/README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8")
            + "\nCurrent source bytes are authoritative.\n",
            encoding="utf-8",
        )

        result = self.verify(source)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(manifest.read_bytes(), manifest_before)

    def test_verifier_rejects_unmapped_canonical_surfaces(self) -> None:
        source = self.copy_source("unmapped-source")
        unmapped = source / ".agent-workflow/contracts/new-contract.md"
        unmapped.write_text("# Newly packaged contract\n", encoding="utf-8")

        self.assert_verify_failure(
            source,
            "canonical source inventory differs",
        )

    def test_root_version_is_the_only_version_source(self) -> None:
        source = self.copy_source("version-source")
        (source / "VERSION").write_text("9.8.7\n", encoding="utf-8")

        result = self.verify(source)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        (source / ".agent-workflow/VERSION").write_text("9.8.7\n", encoding="utf-8")
        self.assert_verify_failure(source, "canonical source inventory differs")

    def test_framework_terminology_is_required_and_mapped_to_its_canonical_path(
        self,
    ) -> None:
        missing = self.copy_source("missing-terminology")
        (missing / ".agent-workflow/terminology.md").unlink()
        self.assert_verify_failure(missing, "canonical source inventory differs")

        unmapped = self.copy_source("unmapped-terminology")
        path = unmapped / "agent_workflow/install/manifest.json"
        manifest = json.loads(path.read_text())
        manifest["framework_owned"] = [
            mapping
            for mapping in manifest["framework_owned"]
            if mapping["source"] != ".agent-workflow/terminology.md"
        ]
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assert_verify_failure(unmapped, "distribution manifest is stale")

    def test_verifier_rejects_the_old_root_terminology_source(self) -> None:
        source = self.copy_source("duplicate-terminology")
        (source / "CONTEXT.md").write_bytes(
            (source / ".agent-workflow/terminology.md").read_bytes()
        )
        self.assert_verify_failure(
            source, "obsolete source layout must remain absent: CONTEXT.md"
        )

    def test_verifier_requires_the_domain_modeling_terminology_boundary(self) -> None:
        source = self.copy_source("domain-modeling-terminology-ownership")
        self.replace_once(
            source,
            ".agents/skills/domain-modeling/SKILL.md",
            "In consuming projects, Domain Modeling does not own or modify the framework-owned `.agent-workflow/terminology.md`.",
            "Domain Modeling may modify framework terminology in consuming projects.",
        )
        self.assert_verify_failure(
            source, "Domain Modeling lacks load-bearing contract"
        )

    def test_verifier_rejects_a_second_version_inside_the_python_package(self) -> None:
        source = self.copy_source("duplicate-version")
        (source / "agent_workflow/VERSION").write_text("9.8.7\n", encoding="utf-8")
        self.assert_verify_failure(
            source, "root VERSION is the single authored version"
        )

    def test_root_version_must_be_a_regular_semantic_version_file(self) -> None:
        for kind in ("missing", "symlink", "directory", "malformed"):
            with self.subTest(kind=kind):
                source = self.copy_source(f"version-{kind}")
                version = source / "VERSION"
                version.unlink()
                if kind == "symlink":
                    version.symlink_to(source / "README.md")
                elif kind == "directory":
                    version.mkdir()
                elif kind == "malformed":
                    version.write_text("0.30.0-rc.1\n", encoding="utf-8")
                expected = (
                    "VERSION must use x.y.z"
                    if kind == "malformed"
                    else "missing or unsafe root VERSION"
                )
                self.assert_verify_failure(source, expected)

    def test_verifier_requires_non_active_root_policy_templates(self) -> None:
        cases = (
            ("literal-root-policy", "agent_workflow/install/AGENTS.md"),
            ("literal-nested-policy", ".agents/skills/example/CLAUDE.md"),
            ("literal-framework-policy", ".agent-workflow/AGENTS.md"),
        )
        for name, relative in cases:
            with self.subTest(relative=relative):
                source = self.copy_source(name)
                path = source / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("activation-sensitive fixture\n", encoding="utf-8")

                self.assert_verify_failure(
                    source, "distributed root policy must use an install template"
                )

    def test_verifier_requires_complete_curated_skill_directories(self) -> None:
        missing = self.copy_source("missing-skill-file")
        (missing / ".agents/skills/tdd/tests.md").unlink()
        self.assert_verify_failure(missing, "curated skill tdd is incomplete")

        extra = self.copy_source("extra-skill-file")
        (extra / ".agents/skills/research/notes.md").write_text(
            "unexpected\n", encoding="utf-8"
        )
        self.assert_verify_failure(
            extra, "curated skill research is incomplete or contains unexpected files"
        )

        wrong_name = self.copy_source("wrong-skill-name")
        self.replace_once(
            wrong_name,
            ".agents/skills/research/SKILL.md",
            "name: research",
            "name: not-research",
        )
        self.assert_verify_failure(
            wrong_name, "curated skill name differs from its directory"
        )

    def test_domain_modeling_has_no_generic_adr_support_surface(self) -> None:
        source = self.copy_source("domain-modeling-without-adr-support")
        domain_root = source / ".agents/skills/domain-modeling"
        manifest = json.loads(
            (source / "agent_workflow/install/manifest.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            {path.name for path in domain_root.iterdir() if path.is_file()},
            {"CONTEXT-FORMAT.md", "SKILL.md"},
        )
        self.assertFalse(
            (source / ".agents/skills/domain-modeling/ADR-FORMAT.md").exists()
        )
        self.assertNotIn(
            ".agents/skills/domain-modeling/ADR-FORMAT.md",
            {item["source"] for item in manifest["framework_owned"]},
        )

        result = self.verify(source)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verifier_does_not_lock_skill_descriptions(self) -> None:
        source = self.copy_source("description-copy")
        self.replace_once(
            source,
            ".agents/skills/research/SKILL.md",
            "description: Investigate substantive questions against high-trust primary sources and return cited findings in chat. Create a repository artifact only when the user explicitly requests durable research output.",
            "description: Research substantive questions and return cited findings.",
        )

        result = self.verify(source)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verifier_does_not_apply_a_broad_prose_blacklist(self) -> None:
        source = self.copy_source("historical-prose")
        readme = source / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8")
            + "\nHistorical note: the former provider-native design was replaced.\n",
            encoding="utf-8",
        )

        result = self.verify(source)

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
                source = self.copy_source(name)
                path = source / ".agents/skills/research/SKILL.md"
                path.write_text(
                    path.read_text(encoding="utf-8") + f"\n{link}\n",
                    encoding="utf-8",
                )
                self.assert_verify_failure(source, expected)

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
                source = self.copy_source(f"attribution-{name}")
                self.replace_once(
                    source,
                    ".agent-workflow/README.md",
                    original,
                    replacement,
                )
                self.assert_verify_failure(source, expected)

    def test_verifier_enforces_only_load_bearing_semantic_contracts(self) -> None:
        cases = (
            (
                "research-write-authorization",
                ".agents/skills/research/SKILL.md",
                "writes have action authorization",
                "writes are convenient",
                "Research lacks load-bearing contract",
            ),
            (
                "research-does-not-choose",
                ".agents/skills/research/SKILL.md",
                "does not select the project's preferred alternative",
                "selects the project's preferred alternative",
                "Research lacks load-bearing contract",
            ),
            (
                "discovery-owns-bounded-architecture-choice",
                ".agents/skills/workflow-discovery/SKILL.md",
                "An architectural decision is one possible kind of consequential project choice",
                "An architectural decision belongs to Domain Modeling",
                "Discovery lacks load-bearing contract",
            ),
            (
                "discovery-does-not-store-architecture-decisions",
                ".agents/skills/workflow-discovery/SKILL.md",
                "Discovery does not maintain architecture decision records or durable coordination state.",
                "Discovery maintains architecture decision records.",
                "Discovery lacks load-bearing contract",
            ),
            (
                "wayfinder-sole-coordinator",
                ".agents/skills/wayfinder/SKILL.md",
                "sole durable coordination layer",
                "a durable coordination layer",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "wayfinder-objective-alone-is-insufficient",
                ".agents/skills/wayfinder/SKILL.md",
                "An objective alone does not select Wayfinder.",
                "An objective selects Wayfinder.",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "wayfinder-scope-refinement-keeps-effort",
                ".agents/skills/wayfinder/SKILL.md",
                "clarified, narrowed, or elaborated",
                "frozen after creation",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "wayfinder-references-lasting-results",
                ".agents/skills/wayfinder/SKILL.md",
                "Reference the artifacts that maintain",
                "Copy the artifacts that maintain",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "to-spec-destination-and-authorization",
                ".agents/skills/to-spec/SKILL.md",
                "destination named by the user",
                "available publication destination",
                "to-spec lacks load-bearing contract",
            ),
            (
                "to-tickets-destination-and-authorization",
                ".agents/skills/to-tickets/SKILL.md",
                "Publish only when",
                "Publish whenever a destination is available",
                "to-tickets lacks load-bearing contract",
            ),
            (
                "implement-commit-authorization",
                ".agents/skills/implement/SKILL.md",
                "Commit only when the current user request",
                "Commit whenever the current user request",
                "Implement lacks load-bearing contract",
            ),
            (
                "root-route-marker",
                "agent_workflow/install/AGENTS.md.template",
                "Report only what executed",
                "Report what was selected",
                "Root routing lacks load-bearing contract",
            ),
            (
                "detailed-route-marker",
                ".agent-workflow/routing.md",
                "include it in the route marker only when its method actually ran",
                "include it in the route marker when selected",
                "Routing lacks load-bearing contract",
            ),
        )
        for name, relative, original, replacement, expected in cases:
            with self.subTest(name=name):
                source = self.copy_source(name)
                self.replace_once(source, relative, original, replacement)
                self.assert_verify_failure(source, expected)

        for skill in ("to-spec", "to-tickets"):
            with self.subTest(name=f"{skill}-hard-coded-label"):
                source = self.copy_source(f"{skill}-hard-coded-label")
                path = source / f".agents/skills/{skill}/SKILL.md"
                path.write_text(
                    path.read_text(encoding="utf-8")
                    + "\nApply the ready-for-agent label.\n",
                    encoding="utf-8",
                )
                self.assert_verify_failure(
                    source, f"{skill} hard-codes the ready-for-agent label"
                )

        domain_adr = self.copy_source("domain-modeling-generic-adr")
        domain_path = domain_adr / ".agents/skills/domain-modeling/SKILL.md"
        domain_path.write_text(
            domain_path.read_text(encoding="utf-8")
            + "\nRecord an architectural decision in docs/adr/.\n",
            encoding="utf-8",
        )
        self.assert_verify_failure(
            domain_adr, "Domain Modeling retains generic ADR responsibility"
        )

    def test_verifier_rejects_install_history_and_invalid_composite_markers(
        self,
    ) -> None:
        history = self.copy_source("checked-history")
        (history / ".agent-workflow/install-manifest.json").write_text(
            "{}\n", encoding="utf-8"
        )
        self.assert_verify_failure(history, "canonical source inventory differs")

        malformed_composite = self.copy_source("checked-composite-markers")
        agents = malformed_composite / "AGENTS.md"
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

        extra_prefix = self.copy_source("checked-composite-extra-prefix")
        agents = extra_prefix / "AGENTS.md"
        agents.write_bytes(
            agents.read_bytes() + b"\n<!-- agent-workflow:partial-marker"
        )
        self.assert_verify_failure(
            extra_prefix, "checked-in composite has invalid managed markers"
        )

    def test_verifier_rejects_changes_to_the_canonical_skill_inventory(self) -> None:
        source = self.copy_source("unexpected-source-skill")
        unrelated = source / ".agents/skills/project-local"
        unrelated.mkdir(parents=True)
        (unrelated / "SKILL.md").write_text(
            "---\nname: project-local\ndescription: Project-owned skill.\n---\n",
            encoding="utf-8",
        )

        self.assert_verify_failure(source, "curated skill inventory differs")

    def test_verifier_ignores_existing_cache_and_does_not_add_cache_files(self) -> None:
        source = self.copy_source("verifier-bytecode")
        cache = source / "agent_workflow/__pycache__"
        cache.mkdir(exist_ok=True)
        generated = cache / "local-test.cpython-311.pyc"
        generated.write_bytes(b"generated test cache\n")
        before = {
            path.name: path.read_bytes() for path in cache.iterdir() if path.is_file()
        }

        result = self.verify(source)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {
            path.name: path.read_bytes() for path in cache.iterdir() if path.is_file()
        }
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
