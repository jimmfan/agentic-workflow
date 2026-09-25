from __future__ import annotations

import unittest
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from _behavior_test_support import behavior
from evals import persistence


class ObjectiveScopeRoutingTests(unittest.TestCase):
    def test_authorized_documentation_edits_preserve_the_fixed_checker_boundary(self):
        cases = {case.id: case for case in behavior.load_scenarios()}
        for identifier in (
            "imdsv2-rollout-implementation",
            "imdsv2-local-implementation",
            "imdsv2-rollout-plan",
        ):
            with (
                self.subTest(identifier=identifier),
                tempfile.TemporaryDirectory() as temporary,
            ):
                case = cases[identifier]
                workspace = behavior.copy_fixture(case, Path(temporary))
                before = behavior.snapshot(workspace)

                def preservation_passes():
                    checks = behavior.evaluate(
                        behavior.RunEvidence(
                            scenario=case,
                            workspace=workspace,
                            before=before,
                            after=behavior.snapshot(workspace),
                            stdout="",
                            stderr="",
                            returncode=0,
                            report={},
                            verification=(),
                            route_components=(),
                        )
                    )
                    return next(
                        check.passed
                        for check in checks
                        if check.name == "expect:project_state_preserved"
                    )

                for relative in ("README.md", "docs/rollout.md"):
                    path = workspace / relative
                    path.write_text(
                        path.read_text() + "\nPilot evidence remains pending.\n"
                    )
                self.assertEqual(
                    preservation_passes(), identifier != "imdsv2-rollout-plan"
                )
                checker = workspace / "verify.py"
                checker.write_text(checker.read_text() + "\n# Modified checker\n")
                self.assertFalse(preservation_passes())

    def test_structural_controls_reject_missing_empty_and_unnecessary_maps(self):
        cases = {case.id: case for case in behavior.load_scenarios()}
        positive = cases["imdsv2-rollout-implementation"]
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(positive, Path(temporary))
            before = behavior.snapshot(workspace)
            map_path = workspace / ".project-efforts/metadata/map.md"
            map_path.parent.mkdir(parents=True)

            def checks(case):
                return behavior.evaluate(
                    behavior.RunEvidence(
                        scenario=case,
                        workspace=workspace,
                        before=before,
                        after=behavior.snapshot(workspace),
                        stdout="Live acceptance remains pending. [route: router → wayfinder]",
                        stderr="",
                        returncode=0,
                        report={"status": "blocked"},
                        verification=(),
                        route_components=("wayfinder",),
                    )
                )

            self.assertTrue(
                any(
                    c.passed is False
                    for c in checks(positive)
                    if c.name.startswith("assert:")
                )
            )
            map_path.write_text("\n")
            self.assertTrue(
                any(
                    c.passed is False
                    for c in checks(positive)
                    if c.name.startswith("assert:")
                )
            )
            controls = json.loads(
                (
                    behavior.REPOSITORY_ROOT
                    / "evals/objective-scope-routing/controls.json"
                ).read_text()
            )
            for control in controls[:2]:
                map_path.write_text(control["map"])
                self.assertTrue(
                    all(
                        c.passed
                        for c in checks(positive)
                        if c.name.startswith("assert:")
                    )
                )
                # Both controls must reject this unnecessary state regardless of prose.
                for identifier in (
                    "imdsv2-local-implementation",
                    "imdsv2-rollout-plan",
                ):
                    result = {c.name: c.passed for c in checks(cases[identifier])}
                    self.assertFalse(result["must-not:unnecessary_planning_artifacts"])

    def test_semantic_controls_need_bound_review_not_keyword_inference(self):
        controls = json.loads(
            (
                behavior.REPOSITORY_ROOT / "evals/objective-scope-routing/controls.json"
            ).read_text()
        )
        for control in controls:
            with self.subTest(control=control["id"]):
                dimension = control["dimension"]
                packet = {
                    "files": {
                        "map.md": control["map"],
                        "events": "\n".join(control["events"]),
                    },
                    "response": control["response"],
                    "diff": "Synthetic control: " + control["id"],
                    "dimensions": {dimension: "INCONCLUSIVE"},
                }
                review = {"packet_sha256": persistence.fingerprint(packet)}
                self.assertEqual(
                    persistence.adjudicate(packet, review)[dimension], "INCONCLUSIVE"
                )
                review["dimensions"] = {
                    dimension: {
                        "verdict": control["expected"],
                        "rationale": control["reason"],
                        "evidence": [{"path": "@diff", "quote": packet["diff"]}],
                    }
                }
                self.assertEqual(
                    persistence.adjudicate(packet, review)[dimension],
                    control["expected"],
                )
                # A stale review must not promote different evidence to a pass.
                packet["response"] += " changed"
                with self.assertRaises(ValueError):
                    persistence.adjudicate(packet, review)

    def test_configuration_alone_does_not_satisfy_updated_test_coverage(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "consumer"
            shutil.copytree(behavior.FIXTURE_ROOT / "imdsv2-local", workspace)
            config_path = workspace / "main.tf.json"
            config = json.loads(config_path.read_text())
            options = config["resource"]["aws_launch_template"]["application"][
                "metadata_options"
            ]
            options["http_tokens"] = "required"
            config_path.write_text(json.dumps(config))
            result = subprocess.run(
                [sys.executable, "verify.py"], cwd=workspace, capture_output=True
            )
            self.assertNotEqual(
                result.returncode, 0, "missing token regression must fail"
            )
            tests = workspace / "test_configuration.py"
            tests.write_text(
                tests.read_text().replace(
                    'self.assertEqual(template["metadata_options"]["http_endpoint"], "enabled")',
                    'self.assertEqual(template["metadata_options"]["http_endpoint"], "enabled")\n'
                    '        self.assertEqual(template["metadata_options"]["http_tokens"], "required")',
                )
            )
            result = subprocess.run(
                [sys.executable, "verify.py"], cwd=workspace, capture_output=True
            )
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            options["http_endpoint"] = "disabled"
            config_path.write_text(json.dumps(config))
            result = subprocess.run(
                [sys.executable, "verify.py"], cwd=workspace, capture_output=True
            )
            self.assertNotEqual(result.returncode, 0)

    def test_matched_cases_are_blind_and_start_without_coordination(self):
        cases = {case.id: case for case in behavior.load_scenarios()}
        for identifier in (
            "imdsv2-rollout-implementation",
            "imdsv2-local-implementation",
            "imdsv2-rollout-plan",
        ):
            with self.subTest(identifier=identifier):
                case = cases[identifier]
                self.assertTrue(case.blind_grading)
                fixture = behavior.FIXTURE_ROOT / case.fixture
                self.assertFalse((fixture / ".project-efforts").exists())
                prompt = behavior.build_prompt(case)
                self.assertNotIn("Wayfinder", prompt)
                self.assertNotIn("rubric", prompt)


if __name__ == "__main__":
    unittest.main()
