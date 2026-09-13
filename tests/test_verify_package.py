from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest

from _test_support import ProjectTestCase, load_module, run_script


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

    def test_verifier_requires_valid_curated_skill_directories(self) -> None:
        missing = self.copy_source("missing-skill-file")
        (missing / ".agents/skills/tdd/tests.md").unlink()
        self.assert_verify_failure(missing, "curated skill link target is missing")

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

    def test_verifier_discovers_new_skills_and_support_files_from_canonical_source(
        self,
    ) -> None:
        source = self.copy_source("discovered-canonical-skill")
        skill = source / ".agents/skills/example"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: example\ndescription: Exercise canonical discovery.\n---\n\n"
            "Read [support](support.md).\n",
            encoding="utf-8",
        )
        (skill / "support.md").write_text("# Support\n", encoding="utf-8")

        result = self.verify(source, "--refresh-manifest")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads(
            (source / "agent_workflow/install/manifest.json").read_text(
                encoding="utf-8"
            )
        )
        sources = {item["source"] for item in manifest["framework_owned"]}
        self.assertIn(".agents/skills/example/SKILL.md", sources)
        self.assertIn(".agents/skills/example/support.md", sources)

    def test_domain_modeling_distributes_context_support(self) -> None:
        source = self.copy_source("domain-modeling-context-support")
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
        self.assertIn(
            ".agents/skills/domain-modeling/CONTEXT-FORMAT.md",
            {item["source"] for item in manifest["framework_owned"]},
        )

        result = self.verify(source)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_wayfinder_effort_is_a_thin_distributed_wayfinder_entry_point(
        self,
    ) -> None:
        skill_root = (
            Path(__file__).resolve().parents[1] / ".agents/skills/wayfinder-effort"
        )
        self.assertEqual(
            {path.name for path in skill_root.iterdir()},
            {"SKILL.md"},
        )
        text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        for required in (
            "name: wayfinder-effort",
            "objective, plan, or referenced material",
            "Invoke the installed `wayfinder` skill",
            "`.agent-workflow/contracts/wayfinder-state.md`",
            "Do not implement product changes",
            "rather than emulate",
            "what Wayfinder state was created or updated",
            "what remains uncertain",
            "recommended next prompt",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)

        manifest = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "agent_workflow/install/manifest.json"
            ).read_text(encoding="utf-8")
        )
        self.assertIn(
            {
                "source": ".agents/skills/wayfinder-effort/SKILL.md",
                "target": ".agents/skills/wayfinder-effort/SKILL.md",
            },
            manifest["framework_owned"],
        )

    def test_verifier_does_not_lock_skill_descriptions(self) -> None:
        source = self.copy_source("description-copy")
        skill = source / ".agents/skills/research/SKILL.md"
        skill.write_text(
            "\n".join(
                "description: Research substantive questions and return cited findings."
                if line.startswith("description:")
                else line
                for line in skill.read_text(encoding="utf-8").splitlines()
            )
            + "\n",
            encoding="utf-8",
        )

        result = self.verify(source)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verifier_accepts_equivalent_skill_instruction_wording(self) -> None:
        source = self.copy_source("reworded-instructions")
        skill = source / ".agents/skills/implement/SKILL.md"
        frontmatter, delimiter, _ = skill.read_text(encoding="utf-8").partition(
            "\n---\n"
        )
        skill.write_text(
            frontmatter
            + delimiter
            + """Carry out the scope defined by the user or calling workflow.

Apply `tdd` at agreed seams when feasible.
Check types and focused tests regularly, then run the full suite at the end.
Finish by using `code-review` to review the implementation.

Make a commit only with authorization from the current user request or accepted project policy.
If neither authorizes a commit, keep the changes uncommitted and report that status.
""",
            encoding="utf-8",
        )

        result = self.verify(source)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verifier_does_not_apply_a_broad_prose_blacklist(self) -> None:
        cases = (
            (
                "README.md",
                "Historical note: the former provider-native design was replaced.",
            ),
            (
                ".agents/skills/domain-modeling/SKILL.md",
                "Do not record an architectural decision.",
            ),
            (
                ".agents/skills/wayfinder/SKILL.md",
                "Earlier terminology used 'coordination boundary' and 'bounded current scope'.",
            ),
            (
                ".agents/skills/to-spec/SKILL.md",
                "Use a label such as ready-for-agent only when the user names it.",
            ),
            (
                ".agents/skills/to-tickets/SKILL.md",
                "Use a label such as ready-for-agent only when the user names it.",
            ),
        )
        for index, (relative, addition) in enumerate(cases):
            with self.subTest(relative=relative):
                source = self.copy_source(f"permitted-prose-{index}")
                path = source / relative
                path.write_text(
                    path.read_text(encoding="utf-8") + f"\n{addition}\n",
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
                "v1.2.3",
                "unspecified-upstream",
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

    def test_attribution_boundary_covers_only_derived_skills(self) -> None:
        source = self.copy_source("attribution-boundary")
        verifier = load_module(
            "attribution_boundary_verifier",
            source / "agent_workflow/verify_package.py",
        )

        self.assertEqual(
            verifier.ATTRIBUTED_SKILLS,
            {
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
            },
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
