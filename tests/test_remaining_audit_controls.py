"""Campaign controls over the existing evaluator; no model execution."""

from dataclasses import replace
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from _behavior_test_support import behavior


CASES = {s.id: s for s in behavior.load_scenarios() if s.id.startswith("audit-")}
EFFORT = ".project-efforts/receipt-consumer"


class RemainingAuditControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name) / "project"

    def prepare(self, name):
        scenario = CASES["audit-" + name]
        shutil.copytree(behavior.FIXTURE_ROOT / scenario.fixture, self.workspace)
        return scenario, behavior.snapshot(self.workspace)

    def evaluate(self, scenario, before, response="Complete.", route="direct"):
        return behavior.evaluate(
            behavior.RunEvidence(
                scenario=scenario,
                workspace=self.workspace,
                before=before,
                after=behavior.snapshot(self.workspace),
                stdout=response + f"\n[route: router → {route}]",
                stderr="",
                returncode=0,
                report={"status": "success", "summary": "Complete."},
                verification=(),
                route_components=(route,),
            )
        )

    def test_campaign_is_blind_and_contains_fourteen_distinct_cases(self):
        self.assertEqual(len(CASES), 14)
        for scenario in CASES.values():
            with self.subTest(scenario=scenario.id):
                self.assertTrue(scenario.blind_grading)
                prompt = behavior.build_prompt(scenario)
                self.assertNotIn(scenario.id, prompt)
                # Metamorphic control: changing the hidden rubric cannot change
                # the actual delivered request or prompt.
                altered = replace(
                    scenario,
                    assertions=(),
                    expect=("blocked_cleanly",),
                    route_must_include=("wayfinder",),
                    response_must_match=("secret-grading-sentinel",),
                )
                self.assertEqual(prompt, behavior.build_prompt(altered))
                for forbidden in ("Wayfinder", "Codebase Design", "Prototype", "TDD"):
                    self.assertNotIn(forbidden, scenario.request)

    def test_source_negative_rejects_state_even_with_direct_claim(self):
        scenario, before = self.prepare("source-answer")
        answer = (
            "protocol.md: v2 keys do not collide across accounts; retained 24 hours."
        )
        self.assertEqual(
            behavior.verdict(self.evaluate(scenario, before, answer)), "PASS"
        )
        path = self.workspace / ".project-efforts/unneeded/map.md"
        path.parent.mkdir(parents=True)
        path.write_text("# Unneeded coordination\n")
        self.assertEqual(
            behavior.verdict(self.evaluate(scenario, before, answer)), "FAIL"
        )

    def test_positive_rejects_missing_continuation(self):
        scenario, before = self.prepare("source-continuation")
        self.assertEqual(
            behavior.verdict(self.evaluate(scenario, before, route="wayfinder")),
            "FAIL",
        )

    def test_planning_control_rejects_file_mutation(self):
        scenario, before = self.prepare("plan")
        path = self.workspace / "part-03-arc-runners/values.yaml"
        path.write_text(path.read_text().replace("arc-runner-set", "build-runners"))
        self.assertEqual(behavior.verdict(self.evaluate(scenario, before)), "FAIL")

    def test_cache_fixture_exhibits_real_isolation_defect(self):
        self.prepare("causal-fix")
        baseline = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "-v"],
            cwd=self.workspace,
            capture_output=True,
            text=True,
        )
        self.assertEqual(baseline.returncode, 0, baseline.stderr)
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                "from service import Reports, Store; "
                "r=Reports(Store({'alpha':12,'beta':31})); "
                "print(r.total('alpha',0),r.total('beta',0))",
            ],
            cwd=self.workspace,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "12 12")

    def test_trivial_fixture_has_causal_one_value_repair(self):
        scenario, before = self.prepare("trivial-fix")
        command = [sys.executable, "-B", "check.py"]
        self.assertNotEqual(
            subprocess.run(command, cwd=self.workspace, capture_output=True).returncode,
            0,
        )
        (self.workspace / "settings.json").write_text(json.dumps({"port": 8080}))
        self.assertEqual(
            subprocess.run(command, cwd=self.workspace, capture_output=True).returncode,
            0,
        )
        self.assertEqual(behavior.verdict(self.evaluate(scenario, before)), "PASS")

    def test_diagnosis_cannot_claim_success_after_code_edit(self):
        scenario, before = self.prepare("diagnosis")
        (self.workspace / "service.py").write_text("# Unauthorized repair\n")
        self.assertEqual(behavior.verdict(self.evaluate(scenario, before)), "FAIL")

    def resolved_candidate(self):
        scenario, before = self.prepare("resolution")
        (self.workspace / "docs/retry-contract.md").write_text(
            "# Retry consumer contract\n\n"
            "For Parcel v2 batch POST, preserve the original request key for one logical operation.\n"
            "The [publisher reply](../evidence/publisher-reply.md) establishes account isolation, "
            "24 hours from first acceptance, and returning the original response for a changed payload.\n"
        )
        (self.workspace / EFFORT / "map.md").write_text(
            "# Receipt consumer\n\n"
            "Local implementation and independent inventory may proceed.\n"
            "The [contract](../../docs/retry-contract.md) maintains the v2 guarantee.\n"
            "Deployment still awaits [U8](unknowns/U8-window.md); it does not block local work.\n"
        )
        (self.workspace / EFFORT / "unknowns/U7-key-scope.md").unlink()
        return scenario, before

    def test_pruning_without_usable_result_is_rejected(self):
        scenario, before = self.resolved_candidate()
        (self.workspace / "docs/retry-contract.md").write_text("# Done\n")
        self.assertEqual(behavior.verdict(self.evaluate(scenario, before)), "FAIL")

    def test_unrelated_state_loss_is_rejected(self):
        scenario, before = self.resolved_candidate()
        (self.workspace / EFFORT / "unknowns/U8-window.md").unlink()
        self.assertEqual(behavior.verdict(self.evaluate(scenario, before)), "FAIL")

    def test_correct_snapshot_does_not_establish_temporal_compliance(self):
        scenario, before = self.resolved_candidate()
        checks = self.evaluate(scenario, before)
        self.assertEqual(behavior.verdict(checks), "PASS")
        # The existing snapshot evaluator cannot observe reads/order. This
        # predeclared manual dimension prevents promoting snapshot PASS to live
        # lifecycle PASS without trace evidence. It is not a trace evaluator.
        for observed, expected in ((None, "INCONCLUSIVE"), (False, "FAIL")):
            with self.subTest(observed=observed):
                temporal = behavior.CheckResult(
                    "manual:preserve-before-prune-and-saved-readback",
                    observed,
                    "Unavailable trace, or observed premature pruning/no readback.",
                )
                self.assertEqual(behavior.verdict((*checks, temporal)), expected)


if __name__ == "__main__":
    unittest.main()
