from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import unittest

from evals import routing_smoke


class RoutingSmokeTests(unittest.TestCase):
    def test_model_visible_catalog_exposes_only_names_and_byte_sizes(self) -> None:
        case = routing_smoke.load_cases()["direct"]
        catalog = routing_smoke.resource_catalog(case)
        prompt = routing_smoke.build_prompt(
            case,
            loaded={},
            decisions=[],
        )

        self.assertTrue(catalog)
        self.assertTrue(all(set(entry) == {"name", "bytes"} for entry in catalog))
        for resource_name in case["available_resources"]:
            resource_text = routing_smoke.resource_path(case, resource_name).read_text(
                encoding="utf-8"
            )
            self.assertNotIn(resource_text.strip(), prompt)
        for removed_simulation in (
            "host fixture",
            "current-session observation",
            "live host discovery",
            "live_host_discovery",
            "selected_skill",
            "skill_exposed",
            "explicit_user_invocation_required",
            "skill_outcome",
            "invocation metadata",
        ):
            with self.subTest(removed_simulation=removed_simulation):
                self.assertNotIn(removed_simulation, prompt.lower())

    def test_payload_describes_only_routing_inputs_and_limits(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = routing_smoke.main(["payload"])

        self.assertEqual(result, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(set(payload), {"always_loaded", "cases", "limits"})

    def test_direct_case_requests_only_target_then_completes_direct(self) -> None:
        responses = iter(
            [
                {
                    "status": "request_resources",
                    "requested_resources": ["note.txt"],
                    "initial_route": "direct",
                    "current_route": "direct",
                    "wayfinder_assessment": False,
                    "wayfinder_selected": False,
                    "summary": "The bounded read needs only its target.",
                },
                {
                    "status": "complete",
                    "requested_resources": [],
                    "initial_route": "direct",
                    "current_route": "direct",
                    "wayfinder_assessment": False,
                    "wayfinder_selected": False,
                    "summary": "Report the five-word result directly.",
                },
            ]
        )

        report = routing_smoke.run_case(
            routing_smoke.load_cases()["direct"],
            host="codex",
            model="fake-codex",
            invoke=lambda _prompt: (next(responses), {}),
        )

        self.assertTrue(report["passed"], report["checks"])
        self.assertEqual(report["resources_loaded"], ["note.txt"])
        self.assertNotIn(".agent-workflow/routing.md", report["resources_loaded"])
        self.assertEqual(report["final_decision"]["current_route"], "direct")
        self.assertNotIn("skill_environment", report)
        self.assertEqual(len(report["rounds"]), 2)

    def test_evolving_case_reconnoiters_before_wayfinder_escalation(self) -> None:
        responses = iter(
            [
                {
                    "status": "request_resources",
                    "requested_resources": ["task.md"],
                    "initial_route": "direct",
                    "current_route": "direct",
                    "wayfinder_assessment": False,
                    "wayfinder_selected": False,
                    "summary": "Inspect the bounded target before classifying further.",
                },
                {
                    "status": "complete",
                    "requested_resources": [],
                    "initial_route": "direct",
                    "current_route": "wayfinder",
                    "wayfinder_assessment": True,
                    "wayfinder_selected": True,
                    "summary": "The inspected evidence contains hard Wayfinder signals.",
                },
            ]
        )

        report = routing_smoke.run_case(
            routing_smoke.load_cases()["evolving"],
            host="codex",
            model="fake-codex",
            invoke=lambda _prompt: (next(responses), {}),
        )

        self.assertTrue(report["passed"], report["checks"])
        self.assertEqual(report["resources_loaded"], ["task.md"])
        self.assertEqual(report["final_decision"]["current_route"], "wayfinder")
        self.assertTrue(report["final_decision"]["wayfinder_selected"])
        self.assertEqual(len(report["rounds"]), 2)

    def test_direct_case_fails_when_detailed_router_is_loaded(self) -> None:
        responses = iter(
            [
                {
                    "status": "request_resources",
                    "requested_resources": ["note.txt", ".agent-workflow/routing.md"],
                    "initial_route": "direct",
                    "current_route": "direct",
                    "wayfinder_assessment": False,
                    "wayfinder_selected": False,
                    "summary": "Loaded the detailed router unnecessarily.",
                },
                {
                    "status": "complete",
                    "requested_resources": [],
                    "initial_route": "direct",
                    "current_route": "direct",
                    "wayfinder_assessment": False,
                    "wayfinder_selected": False,
                    "summary": "Completed directly after excess loading.",
                },
            ]
        )
        report = routing_smoke.run_case(
            routing_smoke.load_cases()["direct"],
            host="codex",
            model="overloaded",
            invoke=lambda _prompt: (next(responses), {}),
        )

        self.assertFalse(report["passed"])
        failed = {check["name"] for check in report["checks"] if not check["passed"]}
        self.assertEqual(failed, {"first-resources", "forbidden-resources"})

    def test_comparison_reports_routing_interpretation_agreement(self) -> None:
        def report(model: str) -> dict[str, object]:
            return {
                "model": model,
                "host": "claude" if model == "claude" else "codex",
                "cases": [
                    {
                        "case": "direct",
                        "passed": True,
                        "final_decision": {
                            "initial_route": "direct",
                            "current_route": "direct",
                        },
                    },
                    {
                        "case": "evolving",
                        "passed": True,
                        "final_decision": {
                            "initial_route": "direct",
                            "current_route": "wayfinder",
                        },
                    },
                ],
            }

        comparison = routing_smoke.compare_reports([report("codex"), report("claude")])

        self.assertTrue(comparison["interpretation_agreement"])
        self.assertNotIn("skill_outcome_agreement", comparison)

    def test_route_labels_and_transition_are_unchanged(self) -> None:
        self.assertEqual(
            routing_smoke.ROUTES,
            ["direct", "discovery", "debugging", "wayfinder", "other"],
        )
        self.assertNotIn("skill_outcome", routing_smoke.DECISION_SCHEMA["properties"])
        evolving = routing_smoke.load_cases()["evolving"]
        self.assertEqual(evolving["expected_initial_route"], "direct")
        self.assertEqual(evolving["expected_final_route"], "wayfinder")

    def test_prompt_budget_stops_before_contacting_adapter(self) -> None:
        contacted = False

        def invoke(_prompt: str):
            nonlocal contacted
            contacted = True
            raise AssertionError("adapter must not be called after budget failure")

        with self.assertRaisesRegex(routing_smoke.SmokeError, "prompt budget"):
            routing_smoke.run_case(
                routing_smoke.load_cases()["direct"],
                host="codex",
                model="fake-codex",
                invoke=invoke,
                max_prompt_bytes=1,
            )
        self.assertFalse(contacted)

    def test_reports_must_be_written_outside_the_repository(self) -> None:
        with self.assertRaisesRegex(routing_smoke.SmokeError, "outside the repository"):
            routing_smoke.write_json(
                routing_smoke.REPOSITORY_ROOT / "routing-smoke-report.json",
                {"schema_version": 1},
            )

    def test_cost_budget_reports_a_post_call_limit_overrun(self) -> None:
        budget = routing_smoke.CostBudget(
            max_usd=2.0,
            input_per_million=5.0,
            cached_input_per_million=0.5,
            output_per_million=30.0,
        )
        cost = budget.add(
            {
                "input_tokens": 30_000,
                "cached_input_tokens": 10_000,
                "output_tokens": 200,
            }
        )
        self.assertAlmostEqual(cost, 0.111)
        with self.assertRaisesRegex(
            routing_smoke.SmokeError, "reached the \\$2.00 limit"
        ):
            budget.add({"input_tokens": 400_000, "output_tokens": 0})

    def test_comparison_fails_when_matching_models_both_miss_contract(self) -> None:
        failed = {
            "model": "failed",
            "host": "codex",
            "cases": [
                {
                    "case": "direct",
                    "passed": False,
                    "final_decision": {
                        "initial_route": "direct",
                        "current_route": "direct",
                    },
                }
            ],
        }
        comparison = routing_smoke.compare_reports([failed, failed])
        self.assertFalse(comparison["interpretation_agreement"])


if __name__ == "__main__":
    unittest.main()
