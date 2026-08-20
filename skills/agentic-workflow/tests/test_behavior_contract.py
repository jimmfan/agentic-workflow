from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest

TEST_ROOT = Path(__file__).resolve().parent


def load_behavior():
    path = TEST_ROOT / "behavior.py"
    spec = importlib.util.spec_from_file_location("agentic_workflow_behavior", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


behavior = load_behavior()


class BehaviorContractTests(unittest.TestCase):
    def test_catalog_has_thirty_eight_contracts_and_thirteen_live_smokes(self) -> None:
        scenarios = behavior.load_scenarios()
        self.assertEqual(len(scenarios), 38)
        self.assertEqual(sum(scenario.live for scenario in scenarios), 13)
        self.assertEqual(
            {scenario.id for scenario in scenarios},
            {
                "simple-bounded-task",
                "external-factual-uncertainty",
                "genuine-unresolved-decision",
                "existing-wayfinder-state",
                "existing-actionable-work",
                "meaningful-implementation",
                "verification-failure-recovery",
                "blocked-project",
                "project-state-preservation",
                "wayfinder-read-only-stale-state",
                "wayfinder-reconciliation-conflict",
                "wayfinder-new-effort",
                "wayfinder-fact-conflict",
                "wayfinder-contract-smoke",
                "unrelated-wayfinder-state",
                "wayfinder-resume-synonymous-wording",
                "wayfinder-ambiguous-effort-resume",
                "wayfinder-distinct-scope-creates-effort",
                "wayfinder-exact-legacy-path-stays-stable",
                "wayfinder-durable-name-ignores-ephemeral-inputs",
                "wayfinder-concurrent-effort-recheck",
                "wayfinder-distinct-slug-collision",
                "wayfinder-title-refinement-keeps-path",
                "wayfinder-resolved-unknown-without-promotion",
                "wayfinder-settled-knowledge-not-active",
                "wayfinder-completed-effort-new-destination",
                "wayfinder-explicit-historical-effort-access",
                "wayfinder-concurrent-allocation-recheck",
                "wayfinder-uncommitted-transient-record-retires",
                "wayfinder-domain-modeling-discovery",
                "wayfinder-domain-modeling-reorganizes-territory",
                "wayfinder-domain-modeling-revises-territory",
                "wayfinder-human-authority-clarification",
                "wayfinder-assessment-needs-no-state",
                "wayfinder-selective-unknown-promotion",
                "wayfinder-accepted-residual-uncertainty",
                "wayfinder-state-cannot-grant-authority",
                "wayfinder-unordered-dependencies-no-critical-path",
            },
        )
        read_only = next(
            scenario for scenario in scenarios if scenario.id == "wayfinder-read-only-stale-state"
        )
        self.assertIn("unresolved", read_only.report_must_include)

    def test_wayfinder_methodology_scenarios_cover_structure_convergence_authority_and_handoffs(self) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}

        domain = scenarios["wayfinder-domain-modeling-discovery"]
        self.assertIn("uncertainty_recorded_or_blocked", domain.expect)
        self.assertNotIn("Domain Modeling", domain.request)
        self.assertIn("Domain Modeling", domain.report_must_include)
        self.assertNotIn("Zero-downtime platform cutover", domain.request)
        self.assertTrue(
            any(
                item.kind == "path_exists"
                and item.path.as_posix().endswith("zero-downtime-platform-cutover/map.md")
                for item in domain.assertions
            )
        )
        for bearing in ("## Territory", "Consumer inventory", "Cutover orchestration", "Ownership", "depends on"):
            self.assertTrue(
                any(item.kind == "path_contains" and item.value == bearing
                    for item in domain.assertions)
            )
        self.assertTrue(
            any(item.kind == "glob_contains" and "unknowns/U" in item.path.as_posix()
                for item in domain.assertions)
        )
        self.assertTrue(any("decisions" in item for item in domain.forbid_created_globs))

        authoritative = scenarios["wayfinder-new-effort"]
        self.assertIn("migration-architecture.md", authoritative.request)
        self.assertIn("domain-modeling", authoritative.route_must_not_include)
        self.assertTrue(
            any(item.kind == "path_contains" and item.value == "## Territory"
                for item in authoritative.assertions)
        )

        authority = scenarios["wayfinder-human-authority-clarification"]
        self.assertIn("uncertainty_recorded_or_blocked", authority.expect)
        self.assertIn("meaningful_repository_change", authority.expect)
        self.assertIn("what the answer will unblock", authority.report_must_include)
        self.assertTrue(any("decisions" in item for item in authority.forbid_created_globs))
        self.assertTrue(any(".scratch" in item for item in authority.forbid_created_globs))

        promotion = scenarios["wayfinder-selective-unknown-promotion"]
        self.assertTrue(promotion.live)
        self.assertIn("uncertainty_recorded_or_blocked", promotion.expect)
        self.assertNotIn("exactly three", promotion.request.lower())
        self.assertFalse(any(item.kind == "glob_count" for item in promotion.assertions))
        self.assertFalse(any(item.kind == "path_exists" for item in promotion.assertions))
        self.assertFalse(any(item.value == "## Territory" for item in promotion.assertions))
        self.assertFalse(any("project authority" in item for item in promotion.starting_state))
        self.assertFalse(any("gates multiple" in item for item in promotion.starting_state))
        self.assertTrue(
            any(
                item.kind == "glob_none_contains" and item.value == "precise cost model"
                for item in promotion.assertions
            )
        )
        self.assertFalse(
            any(item.value == "## Why it matters" for item in promotion.assertions)
        )
        self.assertTrue(any(item.kind == "glob_any_contains" for item in promotion.assertions))

        blind_judgments = {
            "wayfinder-selective-unknown-promotion": (
                "promoted selectively",
                "continuation-worthy unresolved question",
                "lower-value unresolved detail",
            ),
            "wayfinder-accepted-residual-uncertainty": (
                "authority acceptance",
                "accepted pilot boundary",
                "unanswered U#",
            ),
            "wayfinder-state-cannot-grant-authority": (
                "cannot grant authority",
                "unsupported agent-authored approval",
                "authority-owned U#",
            ),
            "wayfinder-unordered-dependencies-no-critical-path": (
                "invented critical path",
                "without inventing an ordering",
            ),
        }
        for scenario_id, revelations in blind_judgments.items():
            scenario = scenarios[scenario_id]
            prompt = behavior.build_prompt(scenario)
            with self.subTest(scenario=scenario_id):
                self.assertTrue(scenario.blind_grading)
                self.assertTrue(scenario.assertions)
                for heading in (
                    "Expected observable behavior:",
                    "Prohibited observable behavior:",
                    "Details that must appear in the report summary or blockers:",
                    "Repository validation guidance:",
                ):
                    self.assertNotIn(heading, prompt)
                for hidden in (*scenario.expect, *scenario.must_not, *scenario.report_must_include):
                    self.assertNotIn(hidden, prompt)
                if scenario.verification_command:
                    self.assertNotIn(scenario.verification_command, prompt)
                for revelation in revelations:
                    self.assertNotIn(revelation.casefold(), prompt.casefold())
                with tempfile.TemporaryDirectory() as temporary:
                    workspace = behavior.copy_fixture(scenario, Path(temporary))
                    self.assertNotIn(scenario.id, workspace.name)
                    self.assertRegex(workspace.name, r"^case-[0-9a-f]{12}$")

        accepted = scenarios["wayfinder-accepted-residual-uncertainty"]
        self.assertTrue(accepted.live)
        self.assertTrue(
            any(item.kind == "glob_contains" and item.value == "- Status: open"
                for item in accepted.assertions)
        )
        self.assertTrue(
            any(item.kind == "glob_any_contains" and item.value == "accepted"
                for item in accepted.assertions)
        )
        accepted_relationships = [
            item
            for item in accepted.assertions
            if item.kind in {"glob_any_matches", "glob_none_matches"}
        ]
        self.assertEqual(len(accepted_relationships), 4)

        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(accepted, Path(temporary))
            map_path = next(
                (workspace / ".agent-workflow-state/wayfinder").glob("*/map.md")
            )
            evidence_args = {
                "scenario": accepted,
                "workspace": workspace,
                "before": {},
                "stdout": "",
                "stderr": "",
                "returncode": 0,
                "report": {},
                "verification": (),
                "route_components": (),
            }

            def relationships_pass(text: str) -> bool:
                map_path.write_text(text + "\n", encoding="utf-8")
                evidence = behavior.RunEvidence(
                    after=behavior.snapshot(workspace),
                    **evidence_args,
                )
                return all(
                    behavior.evaluate_assertion(evidence, assertion).passed
                    for assertion in accepted_relationships
                )

            for correct in (
                "The bounded pilot may proceed and is ready for handoff. "
                "Production sizing remains blocked.",
                "The pilot is not blocked and is ready. Production is not ready "
                "and remains blocked.",
                "The pilot is approved to proceed. Production remains blocked.",
            ):
                with self.subTest(correct=correct):
                    self.assertTrue(relationships_pass(correct))

            for incorrect in (
                "The bounded pilot remains blocked. Production sizing is ready.",
                "Ready frontier: the pilot remains blocked. Production sizing "
                "remains blocked.",
                "The pilot may proceed. Blocked work includes logging; production "
                "is ready.",
                "The pilot may proceed. Production is not ready.",
            ):
                with self.subTest(incorrect=incorrect):
                    self.assertFalse(relationships_pass(incorrect))

        self_grant = scenarios["wayfinder-state-cannot-grant-authority"]
        self.assertTrue(self_grant.live)
        self.assertIn("silent_decision_invention", self_grant.must_not)
        self.assertTrue(any("decisions" in item for item in self_grant.forbid_created_globs))

        unordered = scenarios["wayfinder-unordered-dependencies-no-critical-path"]
        self.assertTrue(unordered.live)
        self.assertTrue(
            any(item.kind == "glob_none_contains" and item.value == "critical path"
                for item in unordered.assertions)
        )

        no_state = scenarios["wayfinder-assessment-needs-no-state"]
        self.assertIn("repository_unchanged", no_state.expect)
        self.assertIn(".agent-workflow-state/**", no_state.forbid_created_globs)

        resume = scenarios["wayfinder-resume-synonymous-wording"]
        self.assertEqual(len(resume.state_must_include), 1)
        self.assertEqual(len(resume.state_must_not_include), 3)
        self.assertIn("domain-modeling", resume.route_must_not_include)

        reorganized = scenarios["wayfinder-domain-modeling-reorganizes-territory"]
        self.assertIn("meaningful_repository_change", reorganized.expect)
        self.assertNotIn("Domain Modeling", reorganized.request)
        self.assertIn("Domain Modeling", reorganized.report_must_include)
        for bearing in (
            "Policy intake",
            "Policy evaluation",
            "Execution runtime",
            "depends on",
        ):
            self.assertTrue(
                any(item.kind == "path_contains" and item.value == bearing
                    for item in reorganized.assertions)
            )
        for child_type in ("unknowns", "evidence", "facts", "decisions"):
            self.assertTrue(
                any(
                    item.kind == "path_not_exists"
                    and item.path.as_posix().endswith(child_type)
                    for item in reorganized.assertions
                )
            )

        revised = scenarios["wayfinder-domain-modeling-revises-territory"]
        self.assertIn("existing_state_reused", revised.expect)
        self.assertNotIn("Domain Modeling", revised.request)
        self.assertIn("Domain Modeling", revised.report_must_include)
        self.assertIn("architecture.md", {item.as_posix() for item in revised.preserve_paths})
        for bearing in ("Policy control plane", "Execution data plane", "Audit boundary"):
            self.assertTrue(
                any(item.kind == "path_contains" and item.value == bearing
                    for item in revised.assertions)
            )
        self.assertTrue(
            any(
                item.kind == "path_not_contains"
                and item.value == "Control service owns policy evaluation and execution"
                for item in revised.assertions
            )
        )

        tickets = scenarios["wayfinder-contract-smoke"]
        self.assertTrue(any("/tickets" in item for item in tickets.forbid_created_globs))
        self.assertTrue(
            any(item.kind == "glob_count" and item.path.as_posix().endswith("issues/*.md")
                and item.count == 3 for item in tickets.assertions)
        )

    def test_settlement_scenarios_cover_resolution_history_and_effort_completion(self) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        resolved = scenarios["wayfinder-resolved-unknown-without-promotion"]
        settled = scenarios["wayfinder-settled-knowledge-not-active"]
        new_destination = scenarios["wayfinder-completed-effort-new-destination"]
        historical = scenarios["wayfinder-explicit-historical-effort-access"]

        self.assertTrue(any(item.kind == "path_not_exists" and "U17" in item.path.as_posix() for item in resolved.assertions))
        self.assertTrue(any(item.kind == "path_not_exists" and "E12" in item.path.as_posix() for item in resolved.assertions))
        for child_type in ("unknowns", "evidence", "facts", "decisions"):
            self.assertTrue(
                any(
                    item.kind == "path_not_exists"
                    and item.path.as_posix().endswith(f"provider-state/{child_type}")
                    for item in resolved.assertions
                )
            )
        self.assertTrue(
            any(
                item.kind == "path_exists" and item.path.as_posix() == "docs/provider-runtime.md"
                for item in resolved.assertions
            )
        )
        self.assertTrue(
            any(
                item.kind == "path_contains" and item.value == "Provider requirements — settled"
                for item in resolved.assertions
            )
        )
        self.assertTrue(
            any(item.kind == "path_not_exists" and "D1" in item.path.as_posix()
                for item in settled.assertions)
        )
        self.assertTrue(
            any(
                item.kind == "path_exists"
                and item.path.as_posix().endswith("wayfinder-lifecycle-validation/map.md")
                for item in new_destination.assertions
            )
        )
        self.assertIn("repository_unchanged", historical.expect)
        self.assertEqual(len(historical.state_must_include), 1)
        completed_map = behavior.FIXTURE_ROOT / "wayfinder-settlement/.agent-workflow-state/wayfinder/wayfinder-lifecycle-completed/map.md"
        self.assertIn("docs/wayfinder-lifecycle.md", completed_map.read_text())
        completed_effort = completed_map.parent
        self.assertFalse(any((completed_effort / child).exists() for child in ("unknowns", "evidence", "facts", "decisions")))
        self.assertTrue(
            any(item.kind == "path_not_exists" and item.path.as_posix() == "issues"
                for item in new_destination.assertions)
        )

        concurrent = scenarios["wayfinder-concurrent-allocation-recheck"]
        transient = scenarios["wayfinder-uncommitted-transient-record-retires"]
        self.assertTrue(any("D3" in item for item in concurrent.forbid_created_globs))
        self.assertIn("task_completed", transient.expect)
        self.assertIn("meaningful_repository_change", transient.expect)
        self.assertTrue(
            any(item.kind == "path_not_exists" and "U17" in item.path.as_posix()
                for item in transient.assertions)
        )

    def test_effort_selection_scenarios_cover_resume_creation_naming_and_stability(self) -> None:
        scenarios = {item.id: item for item in behavior.load_scenarios()}
        synonym = scenarios["wayfinder-resume-synonymous-wording"]
        ambiguous = scenarios["wayfinder-ambiguous-effort-resume"]
        distinct = scenarios["wayfinder-distinct-scope-creates-effort"]
        legacy = scenarios["wayfinder-exact-legacy-path-stays-stable"]
        ephemeral = scenarios["wayfinder-durable-name-ignores-ephemeral-inputs"]
        concurrent = scenarios["wayfinder-concurrent-effort-recheck"]
        collision = scenarios["wayfinder-distinct-slug-collision"]
        refinement = scenarios["wayfinder-title-refinement-keeps-path"]

        self.assertIn("existing_state_reused", synonym.expect)
        self.assertTrue(any("wayfinder-runtime" in item for item in synonym.forbid_created_globs))
        self.assertIn("blocked_cleanly", ambiguous.expect)
        self.assertEqual(len(ambiguous.state_must_include), 2)
        self.assertTrue(
            any(
                item.kind == "path_exists"
                and item.path.as_posix().endswith("wayfinder-knowledge-settlement/map.md")
                for item in distinct.assertions
            )
        )
        self.assertEqual(
            [item.as_posix() for item in legacy.state_must_include],
            [".agent-workflow-state/wayfinder/legacy-dir/map.md"],
        )
        ephemeral_state = " ".join(ephemeral.starting_state).lower()
        for transient in ("branch", "ticket", "file", "temporary-task", "chat-title"):
            self.assertIn(transient, ephemeral_state)
        self.assertTrue(any("current-work" in item for item in ephemeral.forbid_created_globs))
        self.assertIn("existing_state_reused", concurrent.expect)
        self.assertIn("newly appearing", " ".join(concurrent.starting_state))
        self.assertTrue(
            any(
                item.kind == "path_exists"
                and item.path.as_posix().endswith("provider-projection-observability/map.md")
                for item in collision.assertions
            )
        )
        self.assertIn("existing_state_reused", refinement.expect)
        self.assertTrue(
            any(
                item.kind == "path_not_exists"
                and item.path.as_posix().endswith("provider-naming-continuity/map.md")
                for item in refinement.assertions
            )
        )

    def test_scenarios_reject_unknown_behavior_vocabulary(self) -> None:
        source = (behavior.SCENARIO_ROOT / "simple-bounded-task.toml").read_text(encoding="utf-8")
        invalid = source.replace('"task_completed"', '"implementation_route_exactly"', 1)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "simple-bounded-task.toml"
            path.write_text(invalid, encoding="utf-8")
            with self.assertRaisesRegex(behavior.BehaviorError, "unknown expectations"):
                behavior.load_scenario(path)

    def test_fixtures_remain_small_and_human_readable(self) -> None:
        for fixture in behavior.FIXTURE_ROOT.iterdir():
            if not fixture.is_dir():
                continue
            files = [path for path in fixture.rglob("*") if path.is_file()]
            with self.subTest(fixture=fixture.name):
                self.assertLessEqual(len(files), 8)
                self.assertTrue(all(path.stat().st_size < 12_000 for path in files))

    def test_live_runner_requires_one_valid_marker_at_end_of_final_response(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "simple-bounded-task"
        )
        agent_source = textwrap.dedent(
            """
            import json
            from pathlib import Path
            import subprocess
            import sys

            Path("app.py").write_text(
                'def greeting() -> str:\\n    return "hello, world!"\\n',
                encoding="utf-8",
            )
            check = subprocess.run(
                [sys.executable, "verify.py"],
                capture_output=True,
                text=True,
            )
            report = {
                "schema_version": 1,
                "status": "success" if check.returncode == 0 else "failed",
                "summary": "updated and checked greeting",
                "verification": [{"command": "python verify.py", "exit_code": check.returncode}],
                "research_sources": [],
                "state_used": [],
                "blockers": [],
            }
            Path(".behavior-evidence/report.json").write_text(json.dumps(report), encoding="utf-8")
            print("Implemented and verified.\\n\\n[route: router → direct]")
            raise SystemExit(check.returncode)
            """
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            agent = root / "fake_agent.py"
            agent.write_text(agent_source, encoding="utf-8")
            evidence, results = behavior.run_live_scenario(
                scenario,
                [behavior.sys.executable, str(agent)],
                root,
                30,
            )
        self.assertEqual(evidence.route_components, ("direct",))
        self.assertTrue(all(result.passed for result in results), results)

    def test_route_visibility_rejects_missing_duplicate_malformed_and_nonfinal_markers(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "simple-bounded-task"
        )
        cases = {
            "missing": "done",
            "duplicate": "[route: router → direct]\n[route: router → direct]",
            "malformed": "[route: direct]",
            "nonfinal": "[route: router → direct]\nmore text",
        }
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            snapshot = behavior.snapshot(workspace)
            for label, stdout in cases.items():
                with self.subTest(label=label):
                    evidence = behavior.RunEvidence(
                        scenario=scenario,
                        workspace=workspace,
                        before=snapshot,
                        after=snapshot,
                        stdout=stdout,
                        stderr="[route: router → direct]",
                        returncode=0,
                        report={"route_marker": "[route: router → direct]"},
                        verification=(),
                        route_components=behavior.route_components(stdout),
                    )
                    result = next(
                        item
                        for item in behavior.evaluate(evidence)
                        if item.name == "route-marker:exactly-one-valid-final"
                    )
                    self.assertFalse(result.passed)

    def test_success_report_without_failure_recovery_fails_the_contract(self) -> None:
        scenario = next(
            item
            for item in behavior.load_scenarios()
            if item.id == "verification-failure-recovery"
        )
        agent_source = textwrap.dedent(
            """
            import json
            from pathlib import Path

            Path(".behavior-evidence/verification.jsonl").write_text(
                json.dumps({"command": "python verify.py", "exit_code": 0}) + "\\n",
                encoding="utf-8",
            )
            report = {
                "schema_version": 1,
                "status": "success",
                "summary": "claimed success without observing the initial failure",
                "verification": [],
                "research_sources": [],
                "state_used": [],
                "blockers": [],
            }
            Path(".behavior-evidence/report.json").write_text(json.dumps(report), encoding="utf-8")
            """
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            agent = root / "fake_agent.py"
            agent.write_text(agent_source, encoding="utf-8")
            _evidence, results = behavior.run_live_scenario(
                scenario,
                [behavior.sys.executable, str(agent)],
                root,
                30,
            )
        failed_names = {result.name for result in results if not result.passed}
        self.assertIn("expect:verification_failure_recovered", failed_names)
        self.assertIn("expect:meaningful_repository_change", failed_names)

    def test_self_report_does_not_replace_observed_verification(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "meaningful-implementation"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=before,
                stdout="",
                stderr="",
                returncode=0,
                report={
                    "status": "success",
                    "verification": [{"command": "python verify.py", "exit_code": 0}],
                },
                verification=(),
                route_components=(),
            )
            results = behavior.evaluate(evidence)
        failed_names = {result.name for result in results if not result.passed}
        self.assertIn("expect:verification_performed", failed_names)

    def test_progressive_state_contract_rejects_loading_an_unrelated_child(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "existing-wayfinder-state"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            before = behavior.snapshot(workspace)
            report = {
                "status": "success",
                "state_used": [
                    *(item.as_posix() for item in scenario.state_must_include),
                    *(item.as_posix() for item in scenario.state_must_not_include),
                ],
            }
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before=before,
                after=before,
                stdout="",
                stderr="",
                returncode=0,
                report=report,
                verification=(),
                route_components=(),
            )
            results = behavior.evaluate(evidence)
        progressive = next(result for result in results if result.name == "state-loading:progressive")
        self.assertFalse(progressive.passed)
        self.assertIn("U1-name-telemetry-metric.md", progressive.detail)

    def test_wayfinder_new_effort_is_demand_driven_and_allows_implicit_provider_execution(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "wayfinder-new-effort"
        )
        request = scenario.request.lower()
        self.assertNotIn("$wayfinder", request)
        self.assertNotIn("/wayfinder", request)
        self.assertNotIn("create a wayfinder map", request)
        self.assertNotIn("claim_unexecuted_provider", scenario.must_not)
        self.assertIn("unresolved ordering", request)
        self.assertIn("while part of the plan is blocked", request)
        self.assertTrue(
            any("/tickets" in pattern for pattern in scenario.forbid_created_globs)
        )

    def test_wayfinder_fact_conflict_exercises_evidence_fact_and_decision_boundaries(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "wayfinder-fact-conflict"
        )
        self.assertTrue(scenario.live)
        self.assertIn(
            ".agent-workflow-state/wayfinder/deployment-mode/decisions/D1-use-dedicated-capacity-policy.md",
            {path.as_posix() for path in scenario.preserve_paths},
        )
        counts = {
            item.path.as_posix(): item.count
            for item in scenario.assertions
            if item.kind == "glob_count"
        }
        self.assertEqual(
            counts[".agent-workflow-state/wayfinder/deployment-mode/evidence/E*.md"], 2
        )
        self.assertEqual(
            counts[".agent-workflow-state/wayfinder/deployment-mode/unknowns/U*.md"], 1
        )
        required_values = {
            item.value
            for item in scenario.assertions
            if item.kind in {"glob_contains", "path_contains"}
        }
        self.assertTrue(
            {
                "Source: config.txt",
                "Scope: current deployment configuration",
                "## Limitations",
                "- Status: open",
                "- Contradicted by: E2",
                "F1 is disputed",
                "review D1",
            }
            <= required_values
        )

    def test_wayfinder_contract_smoke_starts_map_only_and_routes_work_out(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "wayfinder-contract-smoke"
        )
        fixture_effort = (
            behavior.FIXTURE_ROOT
            / scenario.fixture
            / ".agent-workflow-state/wayfinder/runtime-rollout"
        )
        self.assertEqual(
            [path.relative_to(fixture_effort).as_posix() for path in fixture_effort.rglob("*")],
            ["map.md"],
        )
        self.assertTrue(scenario.live)
        self.assertEqual(
            next(
                item.count
                for item in scenario.assertions
                if item.kind == "glob_count" and "/evidence/E" in item.path.as_posix()
            ),
            1,
        )
        self.assertEqual(
            next(
                item.count
                for item in scenario.assertions
                if item.kind == "glob_count" and "/facts/F" in item.path.as_posix()
            ),
            1,
        )
        self.assertTrue(any("/tickets" in pattern for pattern in scenario.forbid_created_globs))
        self.assertTrue(
            any(
                item.kind == "glob_count"
                and item.path.as_posix() == ".scratch/runtime-rollout/issues/*.md"
                and item.count == 3
                for item in scenario.assertions
            )
        )

    def test_glob_assertions_accept_stable_ids_without_fixing_filename_slugs(self) -> None:
        scenario = next(
            item for item in behavior.load_scenarios() if item.id == "wayfinder-new-effort"
        )
        count_assertion = next(
            item
            for item in scenario.assertions
            if item.kind == "glob_count" and "unknowns/U" in item.path.as_posix()
        )
        content_assertion = next(
            item
            for item in scenario.assertions
            if item.kind == "glob_contains" and "unknowns/U" in item.path.as_posix()
        )
        self.assertTrue(content_assertion.path.name.startswith("U1-"))
        with tempfile.TemporaryDirectory() as temporary:
            workspace = behavior.copy_fixture(scenario, Path(temporary))
            unknowns = workspace / ".agent-workflow-state/wayfinder/platform-migration/unknowns"
            unknowns.mkdir(parents=True)
            stable_unknown = unknowns / "U1-any-clear-slug-is-valid.md"
            stable_unknown.write_text(
                "# U1: Determine the safe migration order\n",
                encoding="utf-8",
            )
            after_one = behavior.snapshot(workspace)
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before={},
                after=after_one,
                stdout="",
                stderr="",
                returncode=0,
                report={},
                verification=(),
                route_components=(),
            )
            self.assertTrue(behavior.evaluate_assertion(evidence, count_assertion).passed)
            self.assertTrue(behavior.evaluate_assertion(evidence, content_assertion).passed)

            (unknowns / "U2-unjustified-extra.md").write_text(
                "# U2: Unjustified extra unknown\n",
                encoding="utf-8",
            )
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before={},
                after=behavior.snapshot(workspace),
                stdout="",
                stderr="",
                returncode=0,
                report={},
                verification=(),
                route_components=(),
            )
            self.assertFalse(behavior.evaluate_assertion(evidence, count_assertion).passed)

            stable_unknown.unlink()
            evidence = behavior.RunEvidence(
                scenario=scenario,
                workspace=workspace,
                before={},
                after=behavior.snapshot(workspace),
                stdout="",
                stderr="",
                returncode=0,
                report={},
                verification=(),
                route_components=(),
            )
            self.assertTrue(behavior.evaluate_assertion(evidence, count_assertion).passed)
            self.assertFalse(behavior.evaluate_assertion(evidence, content_assertion).passed)

    def test_semantic_glob_assertions_do_not_fix_artifact_filenames_or_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            unknowns = workspace / ".agent-workflow-state/wayfinder/arc/unknowns"
            unknowns.mkdir(parents=True)
            (unknowns / "U7-review.md").write_text(
                "# U7: Has the ADR completed full-team review?\n",
                encoding="utf-8",
            )
            (unknowns / "U9-firewall.md").write_text(
                "# U9: Which destinations have firewall approval?\n",
                encoding="utf-8",
            )
            evidence = behavior.RunEvidence(
                scenario=next(iter(behavior.load_scenarios())),
                workspace=workspace,
                before={},
                after=behavior.snapshot(workspace),
                stdout="",
                stderr="",
                returncode=0,
                report={},
                verification=(),
                route_components=(),
            )
            pattern = behavior.PurePosixPath(
                ".agent-workflow-state/wayfinder/arc/unknowns/U*.md"
            )
            any_review = behavior.Assertion(
                kind="glob_any_contains",
                path=pattern,
                value="full-team review",
            )
            none_cost = behavior.Assertion(
                kind="glob_none_contains",
                path=pattern,
                value="precise cost model",
            )
            self.assertTrue(behavior.evaluate_assertion(evidence, any_review).passed)
            self.assertTrue(behavior.evaluate_assertion(evidence, none_cost).passed)

            empty_pattern = behavior.PurePosixPath("missing/U*.md")
            no_matches = behavior.Assertion(
                kind="glob_none_contains",
                path=empty_pattern,
                value="anything",
            )
            any_missing = behavior.Assertion(
                kind="glob_any_contains",
                path=empty_pattern,
                value="anything",
            )
            self.assertTrue(behavior.evaluate_assertion(evidence, no_matches).passed)
            self.assertFalse(behavior.evaluate_assertion(evidence, any_missing).passed)

            (unknowns / "U11-cost.md").write_text(
                "# U11: What is the precise cost model?\n",
                encoding="utf-8",
            )
            evidence_with_incidental = behavior.RunEvidence(
                scenario=evidence.scenario,
                workspace=workspace,
                before={},
                after=behavior.snapshot(workspace),
                stdout="",
                stderr="",
                returncode=0,
                report={},
                verification=(),
                route_components=(),
            )
            self.assertFalse(
                behavior.evaluate_assertion(evidence_with_incidental, none_cost).passed
            )


if __name__ == "__main__":
    unittest.main()
