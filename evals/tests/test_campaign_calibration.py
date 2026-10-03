"""Calibration protocol controls; constructed reviews are not live grading evidence."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from evals.campaign.calibration import assess, make_packet
from evals.campaign.core import fingerprint
from evals.campaign.schema import validate_scenario


SOURCE = Path(__file__).resolve().parents[1] / "campaign/examples/calibration.json"


def _signature(evidence):
    return fingerprint(evidence)


def constructed_review(source, packet):
    """Supply authored labels only to test transport, matching, and rejection.

    A real reviewer sees the packet without this answer-key lookup.
    """
    corpus = json.loads(source.read_text())
    cases = {_signature(case["evidence"]): case for case in corpus["cases"]}
    items = []
    for item in packet["items"]:
        evidence = item["evidence"]
        case = cases[
            _signature(
                {
                    "request": item["request"],
                    "files": {
                        key: value
                        for key, value in evidence.items()
                        if not key.startswith("@")
                    },
                    "response": evidence["@response"],
                    "observations": json.loads(evidence["@observations"]),
                }
            )
        ]
        items.append(
            {
                "id": item["id"],
                "checks": {
                    expected["id"]: {
                        "verdict": expected["verdict"],
                        "rationale": expected["rationale"],
                        "evidence": [
                            {
                                "path": "docs/visit.md",
                                "quote": evidence["docs/visit.md"],
                            },
                            {
                                "path": "@observations",
                                "quote": evidence["@observations"],
                            },
                        ],
                    }
                    for expected in case["expected"]
                },
            }
        )
    return {
        "packet_sha256": fingerprint(packet),
        "reviewer": "synthetic unit-test reviewer; not a model evaluation",
        "items": items,
    }


class CalibrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.source = Path(self.temporary.name) / "calibration.json"
        self.source.write_bytes(SOURCE.read_bytes())
        self.packet = make_packet(self.source)
        self.review = constructed_review(self.source, self.packet)

    def update_source(self, operation):
        corpus = json.loads(self.source.read_text())
        operation(corpus)
        self.source.write_text(json.dumps(corpus))

    def test_blind_packet_has_deterministic_opaque_ids_without_answer_key(self):
        corpus = json.loads(self.source.read_text())
        self.assertEqual(self.packet, make_packet(self.source))
        encoded = json.dumps(self.packet)
        for case in corpus["cases"]:
            self.assertNotIn(case["id"], encoded)
        self.assertNotIn('"expected"', encoded)
        self.assertNotIn('"expected_rationale"', encoded)
        self.assertNotIn(corpus["purpose"], encoded)
        ids = [item["id"] for item in self.packet["items"]]
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for key in ids:
            self.assertRegex(key, r"^case-[0-9a-f]{24}$")

    def test_complete_constructed_agreement_is_separate_calibration_pass(self):
        before, review = self.source.read_bytes(), deepcopy(self.review)
        result = assess(self.source, self.review)
        self.assertTrue(result["calibration_passed"])
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["totals"]["cases"], 8)
        self.assertEqual(result["totals"]["expected_checks"], 48)
        self.assertEqual(result["totals"]["matching_checks"], 48)
        self.assertEqual(result["totals"]["missing_checks"], 0)
        self.assertEqual(result["kind"], "semantic-grader-calibration")
        self.assertNotIn("subject_invocations", result)
        self.assertNotIn("launched_turns", result)
        self.assertEqual(before, self.source.read_bytes())
        self.assertEqual(review, self.review)

    def test_accept_everything_review_misses_all_six_seeded_defects(self):
        for item in self.review["items"]:
            for judgment in item["checks"].values():
                judgment["verdict"] = "PASS"
        result = assess(self.source, self.review)
        self.assertFalse(result["calibration_passed"])
        self.assertEqual(result["verdict"], "FAIL")
        self.assertEqual(result["totals"]["mismatched_checks"], 6)
        self.assertEqual(result["totals"]["missing_checks"], 0)

    def test_reject_everything_review_rejects_valid_paraphrases_and_valid_dimensions(
        self,
    ):
        for item in self.review["items"]:
            for judgment in item["checks"].values():
                judgment["verdict"] = "FAIL"
        result = assess(self.source, self.review)
        self.assertEqual(result["verdict"], "FAIL")
        self.assertEqual(result["totals"]["mismatched_checks"], 42)
        valid = [
            case
            for case in result["cases"]
            if case["source_case_id"].startswith("valid-")
        ]
        self.assertEqual(len(valid), 2)
        self.assertTrue(
            all(
                check["verdict"] == "FAIL" for case in valid for check in case["checks"]
            )
        )

    def test_missing_criterion_is_inconclusive_and_cannot_pass_calibration(self):
        item = self.review["items"][0]
        omitted = next(iter(item["checks"]))
        del item["checks"][omitted]
        result = assess(self.source, self.review)
        self.assertFalse(result["calibration_passed"])
        self.assertEqual(result["verdict"], "INCONCLUSIVE")
        self.assertEqual(result["totals"]["missing_checks"], 1)
        case = next(case for case in result["cases"] if case["id"] == item["id"])
        check = next(check for check in case["checks"] if check["id"] == omitted)
        self.assertEqual(check["actual"], "INCONCLUSIVE")
        self.assertFalse(check["present"])
        self.assertFalse(check["agreement"])

    def test_missing_case_and_empty_review_retain_complete_denominators(self):
        self.review["items"].pop()
        result = assess(self.source, self.review)
        self.assertEqual(result["totals"]["missing_checks"], 6)
        self.assertEqual(result["totals"]["expected_checks"], 48)
        self.review["items"] = []
        result = assess(self.source, self.review)
        self.assertEqual(result["totals"]["missing_checks"], 48)
        self.assertEqual(result["verdict"], "INCONCLUSIVE")
        self.assertFalse(result["calibration_passed"])

    def test_explicit_inconclusive_is_not_missing_and_is_not_a_matched_pass(self):
        judgment = next(iter(self.review["items"][0]["checks"].values()))
        judgment["verdict"] = "INCONCLUSIVE"
        result = assess(self.source, self.review)
        self.assertEqual(result["totals"]["missing_checks"], 0)
        self.assertEqual(result["totals"]["mismatched_checks"], 1)
        self.assertEqual(result["totals"]["inconclusive_checks"], 1)
        self.assertEqual(result["verdict"], "INCONCLUSIVE")

    def test_observed_disagreement_dominates_other_missing_checks(self):
        item = self.review["items"][0]
        judgments = list(item["checks"])
        verdict = item["checks"][judgments[0]]["verdict"]
        item["checks"][judgments[0]]["verdict"] = (
            "FAIL" if verdict == "PASS" else "PASS"
        )
        del item["checks"][judgments[1]]
        self.assertEqual(assess(self.source, self.review)["verdict"], "FAIL")

    def test_packet_binding_detects_evidence_and_hidden_answer_key_amendments(self):
        operations = [
            lambda corpus: corpus["cases"][0]["evidence"]["files"].update(
                {"docs/visit.md": "Amended artifact"}
            ),
            lambda corpus: corpus["cases"][0]["expected"][0].update(
                {"rationale": "Amended answer key"}
            ),
        ]
        original = self.source.read_bytes()
        for operation in operations:
            with self.subTest(operation=operation):
                self.source.write_bytes(original)
                self.update_source(operation)
                with self.assertRaisesRegex(ValueError, "evidence packet"):
                    assess(self.source, self.review)

    def test_saved_state_pass_requires_saved_artifact_not_request_or_response_claim(
        self,
    ):
        for virtual in ("@request", "@response", "@observations"):
            review = deepcopy(self.review)
            item = review["items"][0]
            evidence = next(p for p in self.packet["items"] if p["id"] == item["id"])[
                "evidence"
            ]
            judgment = item["checks"]["committed-choice"]
            judgment["verdict"] = "PASS"
            judgment["evidence"] = [{"path": virtual, "quote": evidence[virtual]}]
            with (
                self.subTest(path=virtual),
                self.assertRaisesRegex(ValueError, "Saved-state PASS"),
            ):
                assess(self.source, review)

    def test_unknown_duplicate_and_fabricated_review_evidence_are_rejected(self):
        mutations = {
            "stale-hash": lambda r: r.update(packet_sha256="stale"),
            "unknown-case": lambda r: r["items"][0].update(id="case-unknown"),
            "duplicate-case": lambda r: r["items"].append(deepcopy(r["items"][0])),
            "unknown-check": lambda r: r["items"][0]["checks"].update(
                {"invented": deepcopy(next(iter(r["items"][0]["checks"].values())))}
            ),
            "fabricated-quote": lambda r: next(iter(r["items"][0]["checks"].values()))[
                "evidence"
            ][0].update(quote="This quote is absent from every artifact."),
            "empty-quote": lambda r: next(iter(r["items"][0]["checks"].values()))[
                "evidence"
            ][0].update(quote=""),
            "no-citations": lambda r: next(
                iter(r["items"][0]["checks"].values())
            ).update(evidence=[]),
            "missing-rationale": lambda r: next(
                iter(r["items"][0]["checks"].values())
            ).update(rationale=""),
            "nontext-rationale": lambda r: next(
                iter(r["items"][0]["checks"].values())
            ).update(rationale=1),
            "missing-reviewer": lambda r: r.pop("reviewer"),
            "malformed-judgment": lambda r: r["items"][0]["checks"].update(
                {"committed-choice": "PASS"}
            ),
        }
        for name, operation in mutations.items():
            review = deepcopy(self.review)
            operation(review)
            with self.subTest(mutation=name), self.assertRaises(ValueError):
                assess(self.source, review)

    def test_invalid_corpus_cannot_drop_criteria_or_impersonate_saved_files(self):
        operations = {
            "missing-key": lambda c: c["cases"][0]["expected"].pop(),
            "duplicate-key": lambda c: c["cases"][0]["expected"].append(
                deepcopy(c["cases"][0]["expected"][0])
            ),
            "duplicate-case": lambda c: c["cases"].append(deepcopy(c["cases"][0])),
            "duplicate-rubric": lambda c: c["rubric"].append(deepcopy(c["rubric"][0])),
            "unknown-verdict": lambda c: c["cases"][0]["expected"][0].update(
                verdict="OK"
            ),
            "virtual-file": lambda c: c["cases"][0]["evidence"]["files"].update(
                {"@response": "not a saved artifact"}
            ),
            "unsafe-file": lambda c: c["cases"][0]["evidence"]["files"].update(
                {"../outside": "out of scope"}
            ),
            "empty-corpus": lambda c: c.update(cases=[]),
        }
        original = self.source.read_bytes()
        for name, operation in operations.items():
            self.source.write_bytes(original)
            self.update_source(operation)
            with self.subTest(mutation=name), self.assertRaises(ValueError):
                make_packet(self.source)

    def test_saved_requirement_annotations_preserve_matched_core_turns(self):
        root = SOURCE.parents[1] / "scenarios"
        for family in ("guidance-continuity", "objective-acceptance"):
            short = validate_scenario(
                json.loads((root / f"{family}-short.json").read_text())
            )
            accumulated = validate_scenario(
                json.loads((root / f"{family}-accumulated.json").read_text())
            )
            self.assertEqual(
                short["turns"],
                [turn for turn in accumulated["turns"] if turn["id"].startswith("T")],
            )
            declared = {
                check["id"]: check
                for turn in short["turns"]
                for check in turn["checks"]
            }
            required = (
                ("guidance-choice-saved", "evidence-saved")
                if family == "guidance-continuity"
                else ("full-objective-saved", "correction-retained")
            )
            for key in required:
                self.assertEqual(declared[key]["evidence_scope"], "saved")
            reader = (
                "fresh-reader-reconstruction"
                if family == "guidance-continuity"
                else "fresh-reader-objective"
            )
            self.assertEqual(declared[reader]["evidence_scope"], "response")


if __name__ == "__main__":
    unittest.main()
