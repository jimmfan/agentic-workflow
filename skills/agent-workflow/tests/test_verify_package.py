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

    def reconcile_projection(self, package: Path) -> None:
        result = run_script(
            package / "scripts/lifecycle.py",
            "update",
            package.parents[1],
            "--source-revision",
            "unreleased-local-package",
        )
        self.assert_ok(result)

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

    def test_verifier_accepts_the_complete_direct_distribution(self) -> None:
        package = self.copy_package("complete-direct-distribution")

        result = self.verify(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verifier_requires_the_source_only_project_language_glossary(self) -> None:
        package = self.copy_package("missing-source-language")
        (package.parents[1] / "CONTEXT.md").unlink()

        self.assert_verify_failure(
            package, "source terminology glossary is missing"
        )

    def test_payload_content_edits_need_no_distribution_manifest_refresh(self) -> None:
        package = self.copy_package("mapping-content-change")
        source = package / "payload/agent-workflow/README.md"
        source.write_text(
            source.read_text(encoding="utf-8")
            + "\nCurrent package bytes are authoritative.\n",
            encoding="utf-8",
        )
        self.reconcile_projection(package)

        runtime = run_script(package / "scripts/adopt.py", "install", self.project)
        self.assert_ok(runtime)
        self.assertEqual(
            (self.project / ".agent-workflow/README.md").read_bytes(),
            source.read_bytes(),
        )
        verify = self.verify(package)
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_verifier_rejects_unmapped_payload_surfaces(self) -> None:
        package = self.copy_package("unmapped-payload")
        unmapped = package / "payload/agent-workflow/contracts/new-contract.md"
        unmapped.write_text("# Newly packaged contract\n", encoding="utf-8")

        for arguments in ((), ("--refresh-manifest",)):
            with self.subTest(arguments=arguments):
                self.assert_verify_failure(
                    package,
                    "authored payload differs from the exact current package surface",
                    *arguments,
                )

    def test_version_file_drives_verification_and_install_metadata(self) -> None:
        package = self.copy_package("version-source")
        (package / "VERSION").write_text("9.8.7\n", encoding="utf-8")
        self.reconcile_projection(package)

        verify = self.verify(package)
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
        install = run_script(package / "scripts/adopt.py", "install", self.project)
        self.assert_ok(install)
        installed = json.loads(
            (self.project / ".agent-workflow/install-manifest.json").read_text()
        )
        self.assertEqual(installed["framework_version"], "9.8.7")

    def test_verifier_rejects_duplicate_payload_version(self) -> None:
        package = self.copy_package("duplicate-payload-version")
        (package / "payload/VERSION").write_text("0.0.0\n", encoding="utf-8")

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

    def test_verifier_enforces_the_exact_fifteen_skill_thirty_four_file_inventory(
        self,
    ) -> None:
        package = self.copy_package("direct-inventory")
        skills = package / "payload/skills"
        self.assertEqual(
            len([path for path in skills.iterdir() if path.is_dir()]),
            15,
        )
        self.assertEqual(
            len([path for path in skills.rglob("*") if path.is_file()]),
            34,
        )
        extra = skills / "unexpected/SKILL.md"
        extra.parent.mkdir()
        extra.write_text(
            "---\ndescription: Unexpected.\nname: unexpected\n---\n",
            encoding="utf-8",
        )

        self.assert_verify_failure(
            package, "authored payload differs from the exact current package surface"
        )

    def test_verifier_rejects_invalid_direct_skill_frontmatter_and_metadata(self) -> None:
        cases = (
            (
                "wrong-name",
                "payload/skills/research/SKILL.md",
                "name: research",
                "name: not-research",
                "curated skill name differs from its directory",
            ),
            (
                "obsolete-provenance",
                "payload/skills/research/SKILL.md",
                "name: research",
                "github-ref: refs/tags/v1.2.3\nname: research",
                "retains obsolete provenance metadata",
            ),
            (
                "lost-implicit-invocation",
                "payload/skills/implement/SKILL.md",
                "disable-model-invocation: false\n",
                "",
                "lost its effective implicit invocation behavior",
            ),
            (
                "redundant-default",
                "payload/skills/implement/agents/openai.yaml",
                "interface:\n",
                "interface:\n  allow_implicit_invocation: true\n",
                "adds redundant default-true invocation metadata",
            ),
            (
                "implicit-opt-out",
                "payload/skills/research/agents/openai.yaml",
                "interface:\n",
                "interface:\npolicy:\n  allow_implicit_invocation: false\n",
                "Codex metadata differs from the accepted effective version",
            ),
            (
                "frontmatter-opt-out",
                "payload/skills/research/SKILL.md",
                "name: research\n",
                "disable-model-invocation: true\nname: research\n",
                "behavior-bearing frontmatter differs from the accepted effective version",
            ),
            (
                "frontmatter-description",
                "payload/skills/research/SKILL.md",
                "description: Investigate substantive questions",
                "description: Look into questions",
                "behavior-bearing frontmatter differs from the accepted effective version",
            ),
            (
                "metadata-description",
                "payload/skills/research/agents/openai.yaml",
                'short_description: "Research from high-trust sources"',
                'short_description: "Research anything"',
                "Codex metadata differs from the accepted effective version",
            ),
        )
        for name, relative, original, replacement, expected in cases:
            with self.subTest(name=name):
                package = self.copy_package(name)
                self.replace_once(package, relative, original, replacement)
                self.assert_verify_failure(package, expected)

    def test_verifier_rejects_missing_and_escaping_direct_skill_links(self) -> None:
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

    def test_verifier_rejects_frozen_fixture_content_and_proof_drift(self) -> None:
        content = self.copy_package("fixture-content-drift")
        fixture_skill = (
            content
            / "tests/fixtures/pinned-main-installation/project/.agents/skills/code-review/SKILL.md"
        )
        fixture_skill.write_text(
            fixture_skill.read_text(encoding="utf-8") + "\ncorrupt\n",
            encoding="utf-8",
        )
        self.assert_verify_failure(
            content, "frozen fixture bytes or filesystem shape differ from proof"
        )

        proof = self.copy_package("fixture-proof-drift")
        proof_path = proof / "tests/fixtures/pinned-main-installation/proof.json"
        proof_path.write_bytes(proof_path.read_bytes() + b"\n")
        self.assert_verify_failure(
            proof, "frozen fixture proof-file SHA-256 differs from the accepted digest"
        )

    def test_verifier_rejects_production_transition_proof_drift(self) -> None:
        package = self.copy_package("production-proof-drift")
        self.replace_once(
            package,
            "scripts/legacy_transition.py",
            "0587a7a2df76a02adfa69fec1a4eb98f3cc7a99baa5301e6e7f050938183504a",
            "0" * 64,
        )

        self.assert_verify_failure(
            package, "frozen fixture legacy trees differ from immutable production proof"
        )

    def test_verifier_requires_complete_third_party_attribution(self) -> None:
        cases = (
            (
                "retained-skill",
                "`code-review`, ",
                "",
                "third-party notice omits retained derived skill",
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
                "license-clause",
                "Permission is hereby granted, free of charge",
                "Permission is granted",
                "canonical MIT permission terms",
            ),
            (
                "license-interior-clause",
                "and to permit persons to whom the Software is\nfurnished to do so",
                "and to share the Software",
                "canonical MIT permission terms",
            ),
            (
                "warranty-disclaimer",
                'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR',
                "THE SOFTWARE HAS NO WARRANTY",
                "canonical MIT warranty disclaimer",
            ),
            (
                "warranty-interior-clause",
                "INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.",
                "INCLUDING GENERAL WARRANTIES.",
                "canonical MIT warranty disclaimer",
            ),
            (
                "historical-scope",
                "those three skills are not part of the current runtime payload",
                "those skills are historical",
                "third-party attribution lacks",
            ),
        )
        for name, original, replacement, expected in cases:
            with self.subTest(name=name):
                package = self.copy_package(f"attribution-{name}")
                self.replace_once(
                    package,
                    "payload/agent-workflow/THIRD_PARTY_NOTICES.md",
                    original,
                    replacement,
                )
                self.assert_verify_failure(package, expected)

    def test_verifier_enforces_research_wayfinder_review_and_implement_contracts(
        self,
    ) -> None:
        cases = (
            (
                "research-chat-default",
                "payload/skills/research/SKILL.md",
                "Return sourced research findings",
                "Return research findings",
                "Research lacks load-bearing contract",
            ),
            (
                "research-no-unrequested-write",
                "payload/skills/research/SKILL.md",
                "Do not create a standalone research file unless",
                "Create a standalone research file unless",
                "Research lacks load-bearing contract",
            ),
            (
                "wayfinder-route-before-state",
                "payload/skills/wayfinder/SKILL.md",
                "Route before inspecting state",
                "Inspect state before routing",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "wayfinder-fail-closed-state",
                "payload/skills/wayfinder/SKILL.md",
                "If the state contract is unavailable",
                "If the state contract is delayed",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "wayfinder-artifact-reference",
                "payload/skills/wayfinder/SKILL.md",
                "create the artifact designated to maintain the result",
                "create a separate report for the result",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "wayfinder-authority",
                "payload/skills/wayfinder/SKILL.md",
                "Host permission",
                "Runtime permission",
                "Wayfinder lacks load-bearing contract",
            ),
            (
                "review-optional-tracker",
                "payload/skills/code-review/SKILL.md",
                "Tracker access is optional source lookup",
                "Tracker access is required source lookup",
                "Code Review lacks load-bearing contract",
            ),
            (
                "review-chat-default",
                "payload/skills/code-review/SKILL.md",
                "Return the review in chat by default.",
                "Return the review in a file by default.",
                "Code Review lacks load-bearing contract",
            ),
            (
                "review-publication-authorization",
                "payload/skills/code-review/SKILL.md",
                "only when that action is separately authorized",
                "whenever a review destination is available",
                "Code Review lacks load-bearing contract",
            ),
            (
                "implement-commit-authorization",
                "payload/skills/implement/SKILL.md",
                "Commit only when the current user request",
                "Commit when the current user request",
                "Implement lacks load-bearing contract",
            ),
            (
                "implement-inner-loop-boundary",
                "payload/skills/implement/SKILL.md",
                "owns the inner build, test, and review loop",
                "owns implementation work",
                "Implement lacks load-bearing contract",
            ),
        )
        for name, relative, original, replacement, expected in cases:
            with self.subTest(name=name):
                package = self.copy_package(name)
                self.replace_once(package, relative, original, replacement)
                self.assert_verify_failure(package, expected)

        host_prefix = self.copy_package("implement-host-prefix")
        implement = host_prefix / "payload/skills/implement/SKILL.md"
        implement.write_text(
            implement.read_text(encoding="utf-8") + "\nUse /tdd for this work.\n",
            encoding="utf-8",
        )
        self.assert_verify_failure(
            host_prefix, "Implement retains a host-specific skill prefix"
        )

    def test_verifier_rejects_retired_or_incompatible_wayfinder_language(self) -> None:
        cases = (
            (
                "retired-frontier",
                "The ready frontier is available.",
                "Wayfinder retains retired canonical language",
            ),
            (
                "tracker-parent",
                "The map is the parent issue.",
                "Wayfinder contains incompatible tracker mechanics",
            ),
        )
        for name, addition, expected in cases:
            with self.subTest(name=name):
                package = self.copy_package(name)
                path = package / "payload/skills/wayfinder/SKILL.md"
                path.write_text(
                    path.read_text(encoding="utf-8") + f"\n{addition}\n",
                    encoding="utf-8",
                )
                self.assert_verify_failure(package, expected)

    def test_verifier_enforces_tracker_destination_and_mutation_contracts(self) -> None:
        destination = self.copy_package("tracker-destination-order")
        self.replace_once(
            destination,
            "payload/skills/to-spec/SKILL.md",
            "1. the current user request;\n2. project instructions;",
            "1. project instructions;\n2. the current user request;",
        )
        self.assert_verify_failure(
            destination, "To Spec destination precedence is missing or reordered"
        )

        authorization = self.copy_package("tracker-mutation-authorization")
        self.replace_once(
            authorization,
            "payload/skills/to-tickets/SKILL.md",
            "blocking-link creation, status changes, and labels require authorization",
            "blocking links may be created when useful",
        )
        self.assert_verify_failure(
            authorization, "To Tickets lacks load-bearing contract"
        )

        publication = self.copy_package("tracker-publication-authorization")
        self.replace_once(
            publication,
            "payload/skills/to-spec/SKILL.md",
            "A known destination does not authorize publication.",
            "A known destination authorizes publication.",
        )
        self.assert_verify_failure(publication, "To Spec lacks load-bearing contract")

        labels = self.copy_package("tracker-label-semantics")
        self.replace_once(
            labels,
            "payload/skills/to-spec/SKILL.md",
            "Apply labels only when the project defines their semantics.",
            "Apply labels when they appear useful.",
        )
        self.assert_verify_failure(labels, "To Spec lacks load-bearing contract")

    def test_verifier_enforces_workflow_and_result_artifact_contracts(self) -> None:
        cases = (
            (
                "implementation-single-invocation",
                "payload/skills/workflow-implementation/SKILL.md",
                "Invoke the installed `implement` skill once",
                "Invoke the installed `implement` skill twice",
                "Implementation integration lacks load-bearing contract",
            ),
            (
                "verification-return-path",
                "payload/skills/workflow-verification/SKILL.md",
                "Return implementation defects to",
                "Report implementation defects to",
                "Verification integration lacks load-bearing contract",
            ),
            (
                "implementation-designated-result-artifact",
                "payload/skills/workflow-implementation/SKILL.md",
                "the artifact designated to maintain the result",
                "the selected artifacts",
                "Implementation integration lacks load-bearing contract",
            ),
            (
                "verification-designated-result-artifact",
                "payload/skills/workflow-verification/SKILL.md",
                "the artifact designated to maintain the result",
                "the selected artifacts",
                "Verification integration lacks load-bearing contract",
            ),
            (
                "designated-result-artifacts",
                "payload/agent-workflow/routing.md",
                "The artifact designated to maintain the result remains authoritative",
                "Project or external artifacts designated to maintain their results remain authoritative",
                "Routing lacks load-bearing contract",
            ),
            (
                "routing-transition",
                "payload/agent-workflow/routing.md",
                "Meaningful Implementation runs Verification once.",
                "Meaningful Implementation may skip Verification.",
                "Routing lacks load-bearing contract",
            ),
            (
                "routing-label",
                "payload/agent-workflow/routing.md",
                "`<skill>-blocked`",
                "`<skill>-stopped`",
                "Routing lacks load-bearing contract",
            ),
        )
        for name, relative, original, replacement, expected in cases:
            with self.subTest(name=name):
                package = self.copy_package(name)
                self.replace_once(package, relative, original, replacement)
                self.assert_verify_failure(package, expected)

    def test_verifier_rejects_retired_architecture_on_current_surfaces(self) -> None:
        current = self.copy_package("retired-current-language")
        readme = current.parents[1] / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8")
            + "\nThe provider-native runtime remains current.\n",
            encoding="utf-8",
        )
        self.assert_verify_failure(
            current, "current surface retains retired runtime architecture"
        )

        tree = self.copy_package("retired-runtime-tree")
        retired = tree / "provider-snapshots"
        retired.mkdir()
        (retired / "README.md").write_text("retired\n", encoding="utf-8")
        self.assert_verify_failure(tree, "retired runtime architecture remains")

    def test_retired_architecture_scan_excludes_notices_tests_and_history(self) -> None:
        package = self.copy_package("retired-scan-exclusions")
        notice = package / "payload/agent-workflow/THIRD_PARTY_NOTICES.md"
        notice.write_text(
            notice.read_text(encoding="utf-8")
            + "\nHistorical terms: .agent-workflow/providers.json, provider-native, "
            ".scratch/, skill-owned artifact, skill lifecycle, /tdd, /code-review, "
            "and setup, tdd, and code review.\n",
            encoding="utf-8",
        )
        test_source = package / "tests/test_verify_package.py"
        test_source.write_text(
            test_source.read_text(encoding="utf-8")
            + "\n# Negative assertion: provider-snapshots/ and provider-native.\n",
            encoding="utf-8",
        )
        self.reconcile_projection(package)

        result = self.verify(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verifier_rejects_retired_conventions_in_active_scenario_semantics(self) -> None:
        package = self.copy_package("retired-active-scenario")
        scenario = package / "tests/scenarios/wayfinder-new-effort.toml"
        scenario.write_text(
            scenario.read_text(encoding="utf-8").replace(
                "parallel tracker ticket copy",
                "parallel provider-native ticket copy",
            ),
            encoding="utf-8",
        )

        self.assert_verify_failure(
            package, "active behavioral scenario retains retired runtime architecture"
        )

    def test_verifier_rejects_checked_in_projection_drift(self) -> None:
        package = self.copy_package("checked-projection-drift")
        installed = package.parents[1] / ".agents/skills/research/SKILL.md"
        installed.write_text(
            installed.read_text(encoding="utf-8") + "\nlocal drift\n",
            encoding="utf-8",
        )

        self.assert_verify_failure(
            package, "checked-in projection differs from direct payload"
        )

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
