from __future__ import annotations

import unittest

from evals import routing_smoke


class RoutingSmokeTests(unittest.TestCase):
    def test_model_visible_catalog_does_not_reveal_fixture_word_count(self) -> None:
        prompt = routing_smoke.build_prompt(
            routing_smoke.load_cases()["direct"],
            host="codex",
            loaded={},
            decisions=[],
        )
        self.assertNotIn('"words": 5', prompt)
        self.assertIn("MUST request provider metadata before completing", prompt)

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
                    "provider_outcome": "not_checked",
                    "summary": "The bounded read needs only its target.",
                },
                {
                    "status": "complete",
                    "requested_resources": [],
                    "initial_route": "direct",
                    "current_route": "direct",
                    "wayfinder_assessment": False,
                    "wayfinder_selected": False,
                    "provider_outcome": "not_checked",
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
                    "provider_outcome": "not_checked",
                    "summary": "Inspect the bounded target before classifying further.",
                },
                {
                    "status": "request_resources",
                    "requested_resources": [
                        ".agent-workflow/providers.json",
                        ".agents/skills/wayfinder/SKILL.md",
                        ".agent-workflow/contracts/wayfinder-state.md",
                    ],
                    "initial_route": "direct",
                    "current_route": "wayfinder",
                    "wayfinder_assessment": True,
                    "wayfinder_selected": True,
                    "provider_outcome": "not_checked",
                    "summary": "Accumulated evidence contains several hard Wayfinder signals.",
                },
                {
                    "status": "complete",
                    "requested_resources": [],
                    "initial_route": "direct",
                    "current_route": "wayfinder",
                    "wayfinder_assessment": True,
                    "wayfinder_selected": True,
                    "provider_outcome": "available",
                    "summary": "Wayfinder is available, but read-only scope prevents durable writes.",
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
        self.assertEqual(report["resources_loaded"][0], "task.md")
        self.assertEqual(report["final_decision"]["current_route"], "wayfinder")
        self.assertTrue(report["final_decision"]["wayfinder_selected"])

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
                    "provider_outcome": "not_checked",
                    "summary": "Loaded the detailed router unnecessarily.",
                },
                {
                    "status": "complete",
                    "requested_resources": [],
                    "initial_route": "direct",
                    "current_route": "direct",
                    "wayfinder_assessment": False,
                    "wayfinder_selected": False,
                    "provider_outcome": "direct",
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

    def test_comparison_separates_route_agreement_from_provider_outcomes(self) -> None:
        def report(model: str, provider_outcome: str) -> dict[str, object]:
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
                            "provider_outcome": provider_outcome,
                        },
                    },
                ],
            }

        comparison = routing_smoke.compare_reports(
            [report("codex", "available"), report("claude", "host_native_fallback")]
        )

        self.assertTrue(comparison["interpretation_agreement"])
        self.assertFalse(comparison["provider_outcome_agreement"])

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

    def test_cost_budget_stops_before_two_dollars(self) -> None:
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

    def test_comparison_fails_when_matching_models_both_miss_the_contract(self) -> None:
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
                        "provider_outcome": "direct",
                    },
                }
            ],
        }
        comparison = routing_smoke.compare_reports([failed, failed])
        self.assertFalse(comparison["interpretation_agreement"])


if __name__ == "__main__":
    unittest.main()
