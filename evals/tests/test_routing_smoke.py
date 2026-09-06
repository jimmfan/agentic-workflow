from __future__ import annotations

from contextlib import redirect_stdout
import io
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import subprocess
import sys

from evals import routing_smoke


class RoutingSmokeTests(unittest.TestCase):
    def test_policy_is_the_disposable_consumer_policy_not_maintainer_instructions(self):
        case = routing_smoke.load_cases()["direct"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = root / "consumer"
            consumer.mkdir()
            subprocess.run(
                [
                    sys.executable,
                    str(routing_smoke.REPOSITORY_ROOT / "agent_workflow/lifecycle.py"),
                    "install",
                    str(consumer),
                ],
                check=True,
                capture_output=True,
            )
            prompt = routing_smoke.build_prompt(case, loaded={}, decisions=[])
            self.assertEqual(
                routing_smoke.consumer_policy(), (consumer / "AGENTS.md").read_text()
            )
            self.assertIn((consumer / "AGENTS.md").read_text().strip(), prompt)
            self.assertNotIn("# Agent Workflow source repository", prompt)
            source = root / "source"
            shutil.copytree(
                routing_smoke.REPOSITORY_ROOT / "agent_workflow/install",
                source / "agent_workflow/install",
            )
            (source / "AGENTS.md").write_text("MAINTAINER ONLY EDIT")
            with patch.object(routing_smoke, "REPOSITORY_ROOT", source):
                self.assertEqual(
                    prompt, routing_smoke.build_prompt(case, loaded={}, decisions=[])
                )

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
                "selected_cases": ["direct", "evolving"],
                "execution_status": "completed",
                "incomplete_cases": 0,
                "provenance": {key: "fixed" for key in routing_smoke.COMPARISON_FIELDS}
                | {"model": model, "adapter": {"identity": "fake", "version": "1"}},
                "host": "fake",
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

        comparison = routing_smoke.compare_reports(
            [report("codex"), report("claude")], variables=["model"]
        )

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

        report = routing_smoke.run_case(
            routing_smoke.load_cases()["direct"],
            host="codex",
            model="fake-codex",
            invoke=invoke,
            max_prompt_bytes=1,
        )
        self.assertEqual(report["verdict"], "INCONCLUSIVE")
        self.assertIn("prompt budget", report["error"])
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
            budget.check()

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


class RoutingReportEvidenceTests(unittest.TestCase):
    @staticmethod
    def decision(resource=None, route="direct"):
        return {
            "status": "request_resources" if resource else "complete",
            "requested_resources": [resource] if resource else [],
            "initial_route": "direct",
            "current_route": route,
            "wayfinder_assessment": route == "wayfinder",
            "wayfinder_selected": route == "wayfinder",
            "summary": "Fixture decision.",
        }

    def test_success_then_timeout_persists_both_cases_and_current_prompt(self):
        responses = iter(
            [
                (self.decision("note.txt"), {}),
                (self.decision(), {}),
                subprocess.TimeoutExpired("fake", 1, output="partial"),
            ]
        )

        def invoke(prompt):
            result = next(responses)
            if isinstance(result, Exception):
                raise result
            return result

        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(routing_smoke, "codex_invoke", return_value=invoke),
        ):
            output = Path(temporary) / "report.json"
            code = routing_smoke.main(
                [
                    "run",
                    "--adapter",
                    "codex",
                    "--model",
                    "fake",
                    "--executable",
                    "unavailable-fake",
                    "--max-estimated-cost-usd",
                    "1",
                    "--input-price-per-million",
                    "1",
                    "--cached-input-price-per-million",
                    "1",
                    "--output-price-per-million",
                    "1",
                    "--output",
                    str(output),
                ]
            )
            report = json.loads(output.read_text())
        self.assertEqual(code, 2)
        self.assertEqual(report["cases"][0]["verdict"], "PASS")
        self.assertEqual(report["cases"][1]["verdict"], "INCONCLUSIVE")
        self.assertEqual(report["incomplete_cases"], 1)
        self.assertEqual(report["observed_failures"], 0)
        self.assertEqual(report["cases"][1]["rounds"][0]["partial_stdout"], "partial")
        self.assertIn("prompt", report["cases"][1]["rounds"][0])

    def test_received_response_crossing_cost_limit_is_retained(self):
        budget = routing_smoke.CostBudget(0.01, 1, 1, 1)
        report = routing_smoke.run_case(
            routing_smoke.load_cases()["direct"],
            host="fake",
            model="fake",
            invoke=lambda prompt: (
                self.decision("note.txt"),
                {"input_tokens": 20_000, "output_tokens": 0},
            ),
            cost_budget=budget,
        )
        self.assertEqual(len(report["rounds"]), 1)
        self.assertEqual(report["rounds"][0]["decision"], self.decision("note.txt"))
        self.assertEqual(report["transmission"]["estimated_cost_usd"], 0.02)
        self.assertEqual(report["execution_status"], "interrupted")
        self.assertEqual(report["verdict"], "INCONCLUSIVE")

    def test_observed_failure_survives_a_later_adapter_exception(self):
        responses = iter(
            [(self.decision(".agent-workflow/routing.md"), {}), OSError("offline")]
        )

        def invoke(prompt):
            result = next(responses)
            if isinstance(result, Exception):
                raise result
            return result

        report = routing_smoke.run_case(
            routing_smoke.load_cases()["direct"],
            host="fake",
            model="fake",
            invoke=invoke,
        )
        self.assertEqual(report["verdict"], "FAIL")
        self.assertFalse(report["complete"])

    def test_premature_wayfinder_selection_survives_a_later_timeout(self):
        responses = iter(
            [
                (self.decision("task.md", route="wayfinder"), {}),
                subprocess.TimeoutExpired("fake", 1),
            ]
        )

        def invoke(prompt):
            result = next(responses)
            if isinstance(result, Exception):
                raise result
            return result

        report = routing_smoke.run_case(
            routing_smoke.load_cases()["evolving"],
            host="fake",
            model="fake",
            invoke=invoke,
        )
        self.assertEqual(report["verdict"], "FAIL")
        self.assertFalse(report["complete"])
        self.assertEqual(report["execution_status"], "interrupted")

    def test_codex_timeout_preserves_received_response_and_usage(self):
        decision = self.decision("task.md", route="wayfinder")
        usage = {"input_tokens": 20, "output_tokens": 5}

        def timeout(command, **kwargs):
            output = Path(command[command.index("--output-last-message") + 1])
            output.write_text(json.dumps(decision))
            raise subprocess.TimeoutExpired(
                command,
                1,
                output=json.dumps({"type": "turn.completed", "usage": usage}).encode(),
                stderr=b"partial diagnostics",
            )

        with tempfile.TemporaryDirectory() as temporary:
            Path(temporary, "auth.json").write_text("{}")
            with (
                patch.dict("os.environ", {"CODEX_HOME": temporary}),
                patch.object(routing_smoke, "executable_path", return_value="fake"),
                patch.object(routing_smoke.subprocess, "run", side_effect=timeout),
            ):
                invoke = routing_smoke.codex_invoke(
                    model="fake",
                    executable="fake",
                    timeout_seconds=1,
                )
                report = routing_smoke.run_case(
                    routing_smoke.load_cases()["evolving"],
                    host="codex",
                    model="fake",
                    invoke=invoke,
                    cost_budget=routing_smoke.CostBudget(1, 1, 1, 1),
                )
        self.assertEqual(report["rounds"][0]["decision"], decision)
        self.assertEqual(report["rounds"][0]["usage"], usage)
        self.assertEqual(
            report["rounds"][0]["adapter_evidence"]["stderr"], "partial diagnostics"
        )
        self.assertEqual(report["transmission"]["model_usage"], usage)
        self.assertEqual(report["transmission"]["estimated_cost_usd"], 0.000025)
        self.assertEqual(report["execution_status"], "interrupted")
        self.assertFalse(report["complete"])
        self.assertEqual(report["verdict"], "FAIL")

    def test_invalid_received_response_and_adapter_output_are_retained(self):
        report = routing_smoke.run_case(
            routing_smoke.load_cases()["direct"],
            host="fake",
            model="fake",
            invoke=lambda prompt: ({"invalid": True}, {}),
        )
        self.assertEqual(report["rounds"][0]["decision"], {"invalid": True})
        self.assertEqual(report["verdict"], "INCONCLUSIVE")

        def fail(prompt):
            raise routing_smoke.SmokeError(
                "bad envelope",
                evidence={"stdout": "received response", "usage": {"input_tokens": 5}},
            )

        report = routing_smoke.run_case(
            routing_smoke.load_cases()["direct"], host="fake", model="fake", invoke=fail
        )
        self.assertEqual(
            report["rounds"][0]["adapter_evidence"]["stdout"], "received response"
        )

        def invalid_response(prompt):
            raise routing_smoke.SmokeError(
                "timeout with invalid structured response",
                evidence={"response": '{"invalid": true}', "usage": {}},
            )

        report = routing_smoke.run_case(
            routing_smoke.load_cases()["direct"],
            host="fake",
            model="fake",
            invoke=invalid_response,
        )
        self.assertEqual(report["rounds"][0]["decision"], {"invalid": True})
        self.assertIn("evidence_error", report["rounds"][0])
        self.assertEqual(report["execution_status"], "interrupted")
        self.assertEqual(report["verdict"], "INCONCLUSIVE")

    def test_comparison_requires_provenance_and_declared_variables(self):
        provenance = {key: "fixed" for key in routing_smoke.COMPARISON_FIELDS} | {
            "adapter": {"identity": "fake", "version": "1"}
        }
        report = {"provenance": provenance, "cases": [], "selected_cases": ["direct"]}
        for field in routing_smoke.COMPARISON_FIELDS:
            changed = deepcopy(report)
            changed["provenance"][field] = (
                {"identity": "fake", "version": "2"}
                if field == "adapter"
                else "different"
            )
            comparison = routing_smoke.compare_reports([report, changed])
            self.assertFalse(comparison["comparable"], field)
            self.assertIsNone(comparison["interpretation_agreement"])
            self.assertIn(field, comparison["mismatches"])
            if field in routing_smoke.VARIABLE_FIELDS:
                self.assertTrue(
                    routing_smoke.compare_reports([report, changed], variables=[field])[
                        "comparable"
                    ]
                )
        legacy = routing_smoke.compare_reports([{"cases": []}, {"cases": []}])
        self.assertTrue(legacy["unavailable"])
        self.assertIsNone(legacy["interpretation_agreement"])

    def test_fingerprints_cover_pending_policy_case_and_harness_inputs(self):
        args = routing_smoke.build_parser().parse_args(
            [
                "run",
                "--adapter",
                "codex",
                "--model",
                "fake",
                "--executable",
                "unavailable-fake",
                "--max-estimated-cost-usd",
                "1",
                "--input-price-per-million",
                "1",
                "--cached-input-price-per-million",
                "1",
                "--output-price-per-million",
                "1",
            ]
        )
        inputs = routing_smoke.capture_inputs(routing_smoke.load_cases())
        original = routing_smoke.provenance(args, inputs)
        modified = deepcopy(inputs)
        modified["policy"] += "Pending change"
        self.assertNotEqual(
            original["policy_sha256"],
            routing_smoke.provenance(args, modified)["policy_sha256"],
        )
        modified = deepcopy(inputs)
        modified["resources"]["direct"][".agent-workflow/routing.md"] += " pending"
        self.assertNotEqual(
            original["policy_sha256"],
            routing_smoke.provenance(args, modified)["policy_sha256"],
        )
        modified = deepcopy(inputs)
        modified["resources"]["direct"]["note.txt"] += " pending"
        self.assertNotEqual(
            original["cases_sha256"],
            routing_smoke.provenance(args, modified)["cases_sha256"],
        )
        self.assertIsNone(original["adapter"]["version"])


if __name__ == "__main__":
    unittest.main()
