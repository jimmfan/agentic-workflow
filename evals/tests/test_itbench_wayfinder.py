from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "itbench-wayfinder" / "harness.py"
SPEC = importlib.util.spec_from_file_location("itbench_wayfinder_harness", MODULE_PATH)
assert SPEC and SPEC.loader
harness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(harness)


class OrderingTests(unittest.TestCase):
    def test_order_contains_every_cell_once(self) -> None:
        order = harness.execution_order(3)
        cells = {
            (item["scenario"], item["condition"], item["repetition"])
            for item in order
        }
        self.assertEqual(len(order), 54)
        self.assertEqual(len(cells), 54)

    def test_first_repetition_uses_each_condition_permutation_once(self) -> None:
        order = harness.execution_order(1)
        by_scenario: dict[int, list[str]] = {}
        for item in order:
            by_scenario.setdefault(item["scenario"], []).append(item["condition"])
        self.assertEqual(len({tuple(value) for value in by_scenario.values()}), 6)


class PromptTests(unittest.TestCase):
    def test_a_and_b_are_identical_and_c_only_adds_wayfinder_prefix(self) -> None:
        snapshot = Path("/snapshot")
        output = Path("/workspace/diagnosis.json")
        prompt_a = harness.prompt_for("A", snapshot, output)
        prompt_b = harness.prompt_for("B", snapshot, output)
        prompt_c = harness.prompt_for("C", snapshot, output)
        self.assertEqual(prompt_a, prompt_b)
        self.assertEqual(prompt_c, "$wayfinder\n\n" + prompt_a)
        self.assertNotIn("domain-modeling", prompt_c.lower())


class MatcherTests(unittest.TestCase):
    def parse(self, text: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ground_truth.yaml"
            path.write_text(text, encoding="utf-8")
            return harness.parse_matcher_ground_truth(path)

    def test_parser_supports_id_first_and_filter_first_groups(self) -> None:
        parsed = self.parse(
            """groups:
  - id: pod-root
    kind: Pod
    filter:
      - root-.*
    namespace: demo
    root_cause: true
  - filter:
      - root\\b
    id: service-alias
    kind: Service
    namespace: demo
aliases:
  - - pod-root
    - service-alias
"""
        )
        self.assertEqual(parsed["roots"][0]["root_group_id"], "pod-root")
        self.assertEqual(
            parsed["roots"][0]["accepted_group_ids"],
            ["pod-root", "service-alias"],
        )

    def test_native_score_is_precision_only_at_full_recall(self) -> None:
        matcher = {
            "roots": [
                {
                    "root_group_id": "root",
                    "accepted_groups": [
                        {"id": "root", "kind": "Deployment", "filter": ["checkout\\b"], "namespace": "demo"}
                    ],
                }
            ]
        }
        correct = {"kind": "Deployment", "name": "checkout", "namespace": "demo"}
        false_positive = {"kind": "Service", "name": "kafka", "namespace": "demo"}
        grade = harness.native_grade({"root_causes": [correct, false_positive]}, matcher)
        self.assertTrue(grade["full_recall"])
        self.assertEqual(grade["native_score"], 0.5)
        self.assertEqual(grade["false_positive_predictions"], 1)

        missed = harness.native_grade({"root_causes": [false_positive]}, matcher)
        self.assertFalse(missed["full_recall"])
        self.assertEqual(missed["native_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
