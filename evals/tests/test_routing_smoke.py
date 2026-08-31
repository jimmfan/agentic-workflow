from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from evals import routing_smoke


class RoutingSmokeTests(unittest.TestCase):
    def _install_wayfinder(
        self,
        root: Path,
        *,
        skill_metadata: str = "disable-model-invocation: false\n",
        skill_body: str = "# Wayfinder\n",
        openai_metadata: str = 'interface:\n  display_name: "Wayfinder"\n',
    ) -> None:
        skill = root / ".agents/skills/wayfinder"
        (skill / "agents").mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: wayfinder\n{skill_metadata}---\n{skill_body}",
            encoding="utf-8",
        )
        (skill / "agents/openai.yaml").write_text(
            openai_metadata,
            encoding="utf-8",
        )

    def test_model_visible_catalog_exposes_only_names_and_byte_sizes(self) -> None:
        case = routing_smoke.load_cases()["direct"]
        catalog = routing_smoke.resource_catalog(case)
        prompt = routing_smoke.build_prompt(
            case,
            host="codex",
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
        self.assertIn("Deterministic host fixture", prompt)
        self.assertIn('"live_host_discovery": "unverified"', prompt)
        self.assertIn("MUST request its instructions and declared invocation metadata", prompt)

    def test_installed_surface_uses_invocation_default_from_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._install_wayfinder(root)

            environment = routing_smoke.derive_skill_environment(
                routing_smoke.load_cases()["evolving"],
                host="codex",
                repository_root=root,
            )

        self.assertTrue(environment["installed"])
        self.assertEqual(environment["invocation"], "implicit")
        self.assertEqual(environment["invocation_metadata"]["source"], "default")
        self.assertEqual(environment["expected_skill_outcomes"], ["available"])
        self.assertEqual(environment["live_host_discovery"], "unverified")

    def test_installed_surface_respects_explicit_invocation_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._install_wayfinder(
                root,
                openai_metadata=(
                    "interface:\n"
                    '  display_name: "Wayfinder"\n'
                    "policy:\n"
                    "  allow_implicit_invocation: false\n"
                ),
            )

            environment = routing_smoke.derive_skill_environment(
                routing_smoke.load_cases()["evolving"],
                host="codex",
                repository_root=root,
            )

        self.assertEqual(environment["invocation"], "explicit")
        self.assertEqual(environment["invocation_metadata"]["source"], "metadata")
        self.assertEqual(
            environment["expected_skill_outcomes"],
            ["explicit_invocation_required", "host_native_fallback"],
        )

    def test_skill_invocation_metadata_is_read_only_from_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._install_wayfinder(
                root,
                skill_body=(
                    "# Wayfinder\n"
                    "## Example that is not metadata\n"
                    "disable-model-invocation: true\n"
                ),
            )

            environment = routing_smoke.derive_skill_environment(
                routing_smoke.load_cases()["evolving"],
                host="claude",
                repository_root=root,
            )

        self.assertEqual(environment["invocation"], "implicit")
        self.assertEqual(environment["invocation_metadata"]["value"], False)

    def test_missing_installed_surface_is_unavailable_without_live_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            environment = routing_smoke.derive_skill_environment(
                routing_smoke.load_cases()["evolving"],
                host="claude",
                repository_root=Path(temporary),
            )

        self.assertFalse(environment["installed"])
        self.assertEqual(environment["invocation"], "not_checked")
        self.assertEqual(
            environment["expected_skill_outcomes"],
            ["unavailable", "host_native_fallback"],
        )
        self.assertEqual(environment["live_host_discovery"], "unverified")

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
                    "skill_outcome": "not_checked",
                    "summary": "The bounded read needs only its target.",
                },
                {
                    "status": "complete",
                    "requested_resources": [],
                    "initial_route": "direct",
                    "current_route": "direct",
                    "wayfinder_assessment": False,
                    "wayfinder_selected": False,
                    "skill_outcome": "not_checked",
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
        self.assertEqual(report["skill_environment"]["live_host_discovery"], "unverified")
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
                    "skill_outcome": "not_checked",
                    "summary": "Inspect the bounded target before classifying further.",
                },
                {
                    "status": "request_resources",
                    "requested_resources": [
                        ".agents/skills/wayfinder/SKILL.md",
                        ".agents/skills/wayfinder/agents/openai.yaml",
                        ".agent-workflow/contracts/wayfinder-state.md",
                    ],
                    "initial_route": "direct",
                    "current_route": "wayfinder",
                    "wayfinder_assessment": True,
                    "wayfinder_selected": True,
                    "skill_outcome": "not_checked",
                    "summary": "Accumulated evidence contains several hard Wayfinder signals.",
                },
                {
                    "status": "complete",
                    "requested_resources": [],
                    "initial_route": "direct",
                    "current_route": "wayfinder",
                    "wayfinder_assessment": True,
                    "wayfinder_selected": True,
                    "skill_outcome": "available",
                    "summary": "Wayfinder is installed and implicitly invocable in the fixture.",
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
        self.assertEqual(report["skill_environment"]["invocation"], "implicit")

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
                    "skill_outcome": "not_checked",
                    "summary": "Loaded the detailed router unnecessarily.",
                },
                {
                    "status": "complete",
                    "requested_resources": [],
                    "initial_route": "direct",
                    "current_route": "direct",
                    "wayfinder_assessment": False,
                    "wayfinder_selected": False,
                    "skill_outcome": "direct",
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

    def test_comparison_separates_route_agreement_from_skill_outcomes(self) -> None:
        def report(model: str, skill_outcome: str) -> dict[str, object]:
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
                            "skill_outcome": "not_checked",
                        },
                    },
                    {
                        "case": "evolving",
                        "passed": True,
                        "final_decision": {
                            "initial_route": "direct",
                            "current_route": "wayfinder",
                            "skill_outcome": skill_outcome,
                        },
                    },
                ],
            }

        comparison = routing_smoke.compare_reports(
            [report("codex", "available"), report("claude", "host_native_fallback")]
        )

        self.assertTrue(comparison["interpretation_agreement"])
        self.assertFalse(comparison["skill_outcome_agreement"])

    def test_route_labels_and_transition_are_unchanged(self) -> None:
        self.assertEqual(
            routing_smoke.ROUTES,
            ["direct", "discovery", "debugging", "wayfinder", "other"],
        )
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
                        "skill_outcome": "direct",
                    },
                }
            ],
        }
        comparison = routing_smoke.compare_reports([failed, failed])
        self.assertFalse(comparison["interpretation_agreement"])


if __name__ == "__main__":
    unittest.main()
