from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from evals import routing_smoke as smoke
from evals import wording_micro as micro


SKILLS = {
    "implement": ("Build it, then review.", "Body: return to Verify the result.\n"),
    "workflow-implementation": ("Deliver one scope.", "Body: run Verification.\n"),
}

CASE = {
    "schema_version": 1,
    "id": "fixture",
    "request": "Use implement to add a filter.",
    "skills": ["implement", "workflow-implementation"],
    "variants": {
        "control": {"control": True, "descriptions": {"implement": ""}},
        "current": {"baseline": True, "descriptions": {}},
        "candidate": {"descriptions": {"implement": "Use when named."}},
    },
    "answer_schema": {
        "type": "object",
        "properties": {"verifies": {"type": "boolean"}},
        "required": ["verifies"],
        "additionalProperties": False,
    },
    "predicates": [
        {"id": "reads", "kind": "resource_requested", "resource": "implement"},
        {"id": "verifies", "kind": "answer_equals", "field": "verifies", "value": True},
    ],
}


def budget(limit: float = 1.0) -> smoke.CostBudget:
    return smoke.CostBudget(limit, 1.0, 0.1, 1.0)


class FakeModel:
    """Reads the body only for chosen variants, keyed on the rendered catalog."""

    def __init__(self, reads_when: dict[str, bool], tokens: int = 10):
        self.reads_when = reads_when
        self.tokens = tokens
        self.prompts: list[str] = []

    def __call__(self, prompt: str):
        self.prompts.append(prompt)
        usage = {"input_tokens": self.tokens, "output_tokens": self.tokens}
        variant = next(
            name
            for marker, name in (
                ("- implement: Use when named.", "candidate"),
                ("- implement: Build it, then review.", "current"),
                ("- implement\n", "control"),
            )
            if marker in prompt
        )
        loaded = '<skill name="implement">' in prompt
        if self.reads_when[variant] and not loaded:
            return (
                {
                    "status": "request_resources",
                    "requested_skills": ["implement"],
                    "answer": {"verifies": False},
                },
                usage,
            )
        return (
            {
                "status": "complete",
                "requested_skills": [],
                "answer": {"verifies": loaded},
            },
            usage,
        )


class WordingMicroTests(unittest.TestCase):
    def test_case_validation_requires_one_control_and_known_names(self):
        micro.validate_case(CASE)
        broken = copy.deepcopy(CASE)
        broken["variants"]["current"]["control"] = True
        with self.assertRaisesRegex(smoke.SmokeError, "exactly one control"):
            micro.validate_case(broken)
        broken = copy.deepcopy(CASE)
        broken["variants"]["candidate"]["descriptions"] = {"missing": "x"}
        with self.assertRaisesRegex(smoke.SmokeError, "unknown skills"):
            micro.validate_case(broken)
        broken = copy.deepcopy(CASE)
        broken["predicates"][0]["resource"] = "missing"
        with self.assertRaisesRegex(smoke.SmokeError, "unknown skill"):
            micro.validate_case(broken)

    def test_repository_cases_are_valid_and_reference_real_skills(self):
        for path in sorted(micro.CASES_ROOT.glob("*.json")):
            with self.subTest(case=path.stem):
                case = micro.load_case(path.stem)
                texts = micro.skill_texts(case["skills"])
                for name, (description, body) in texts.items():
                    self.assertTrue(description, name)
                    self.assertNotIn("\ndescription:", body)

    def test_prompt_shows_variant_descriptions_and_hides_bodies_until_requested(self):
        prompt = micro.build_prompt(
            CASE, "control", policy="POLICY", skills=SKILLS, loaded=[], history=[]
        )
        self.assertIn("- implement\n", prompt)
        self.assertIn("- workflow-implementation: Deliver one scope.", prompt)
        self.assertNotIn("Body: return", prompt)
        loaded = micro.build_prompt(
            CASE,
            "candidate",
            policy="POLICY",
            skills=SKILLS,
            loaded=["implement"],
            history=[],
        )
        self.assertIn("- implement: Use when named.", loaded)
        self.assertIn("Body: return to Verify the result.", loaded)

    def test_run_scores_each_variant_and_reports_spread(self):
        model = FakeModel({"control": False, "current": False, "candidate": True})
        report = micro.run(
            CASE, model, budget(), reps=5, policy="POLICY", skills=SKILLS
        )
        variants = report["summary"]["variants"]
        self.assertEqual(variants["candidate"]["passes"], {"reads": 5, "verifies": 5})
        self.assertEqual(variants["current"]["passes"], {"reads": 0, "verifies": 0})
        self.assertEqual(variants["current"]["distinct_outcome_patterns"], 1)
        self.assertTrue(report["summary"]["baseline_failure_observed"])
        self.assertEqual(len(report["samples"]), 15)
        self.assertEqual(
            [sample["variant"] for sample in report["samples"][:3]],
            ["control", "current", "candidate"],
        )

    def test_a_passing_baseline_supports_no_change(self):
        model = FakeModel({"control": True, "current": True, "candidate": True})
        report = micro.run(
            CASE, model, budget(), reps=5, policy="POLICY", skills=SKILLS
        )
        self.assertFalse(report["summary"]["baseline_failure_observed"])
        self.assertIn("supports no wording change", report["summary"]["interpretation"])

    def test_fewer_than_five_reps_is_rejected(self):
        with self.assertRaisesRegex(smoke.SmokeError, "at least 5"):
            micro.run(
                CASE, FakeModel({}), budget(), reps=4, policy="POLICY", skills=SKILLS
            )

    def test_budget_stops_the_run_and_keeps_completed_samples(self):
        model = FakeModel(
            {"control": False, "current": False, "candidate": False}, tokens=100_000
        )
        report = micro.run(
            CASE, model, budget(limit=0.5), reps=5, policy="POLICY", skills=SKILLS
        )
        self.assertIn("limit", report["stopped"])
        self.assertEqual(len(report["samples"]), 3)
        self.assertEqual(len(model.prompts), 3)

    def test_reports_must_be_written_outside_the_repository(self):
        with self.assertRaises(smoke.SmokeError):
            smoke.validated_output_path(smoke.REPOSITORY_ROOT / "report.json")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "report.json"
            smoke.write_json(path, {"ok": True})
            self.assertEqual(json.loads(path.read_text()), {"ok": True})

    def test_run_command_rejects_a_budget_above_the_hard_limit(self):
        with tempfile.TemporaryDirectory() as temporary:
            code = micro.main(
                [
                    "run",
                    "--case",
                    "implement-named-handoff",
                    "--model",
                    "m",
                    "--executable",
                    "/nonexistent",
                    "--max-estimated-cost-usd",
                    "9",
                    "--input-price-per-million",
                    "1",
                    "--cached-input-price-per-million",
                    "0.1",
                    "--output-price-per-million",
                    "1",
                    "--output",
                    str(Path(temporary) / "r.json"),
                ]
            )
        self.assertEqual(code, 2)

    def run_args(self, directory, *extra):
        return [
            "run",
            "--case",
            "implement-named-handoff",
            "--model",
            "m",
            "--executable",
            "/nonexistent",
            "--max-estimated-cost-usd",
            "1",
            "--input-price-per-million",
            "1",
            "--cached-input-price-per-million",
            "0.1",
            "--output-price-per-million",
            "1",
            "--output",
            str(Path(directory) / "r.json"),
            *extra,
        ]

    def test_run_command_passes_codex_effort_and_records_it(self):
        for extra, expected in (((), "low"), (("--effort", "medium"), "medium")):
            with (
                self.subTest(effort=expected),
                tempfile.TemporaryDirectory() as temporary,
                patch.object(smoke, "codex_invoke") as factory,
                patch.object(micro, "run", return_value={"summary": {}}),
            ):
                code = micro.main(self.run_args(temporary, *extra))
                report = json.loads((Path(temporary) / "r.json").read_text())
            self.assertEqual(code, 0)
            self.assertEqual(factory.call_args.kwargs["effort"], expected)
            self.assertEqual(report["conditions"]["effort"], expected)

    def test_run_command_rejects_effort_for_the_claude_adapter(self):
        with tempfile.TemporaryDirectory() as temporary:
            code = micro.main(
                self.run_args(temporary, "--adapter", "claude", "--effort", "medium")
            )
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
