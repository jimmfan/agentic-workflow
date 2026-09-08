"""Narrow scenario-evaluator controls; not a Wayfinder implementation or live proof."""

from pathlib import Path
import tempfile
import unittest

from _behavior_test_support import behavior


class MapAuthoringControls(unittest.TestCase):
    def test_new_default_map_controls(self):
        scenario = next(
            s for s in behavior.load_scenarios() if s.id == "wayfinder-map-authoring"
        )
        good = (
            behavior.FIXTURE_ROOT
            / "wayfinder-map-correction/.project-efforts/consumer-handoff/map.md"
        ).read_text()
        cases = {
            "source-linked": (good, True),
            "invented-authority": (
                good + "\nApplication team decides production rollout.\n",
                False,
            ),
            "linked-orientation": (
                good.replace(
                    "The delivery agreement maintains",
                    "Platform maintains the environment and Application implements the consumer, as established by the delivery agreement, which maintains",
                ),
                True,
            ),
            "lost-provider": (
                good.replace("- Platform team provides the test environment.\n", ""),
                False,
            ),
            "lost-decision-maker": (
                good.replace(
                    "Project lead decides whether production rollout may proceed",
                    "The deployment agent can access production",
                ),
                False,
            ),
            "false-absence": (
                good[: good.index("## Blockers")] + "## Blockers\nNone.\n",
                False,
            ),
            "missing-assessment": (good.replace("## Blockers", "## Notes"), False),
            "unknown-erased": (
                good.replace(
                    "Incident-response responsibility remains unknown",
                    "Incident-response responsibility is assigned",
                ),
                False,
            ),
            "wrong-default-order": (
                good.replace("## Objective", "## Scope", 1).replace(
                    "## Scope\nInventory", "## Objective\nInventory", 1
                ),
                False,
            ),
        }
        self.check_candidates(scenario, cases)

    def test_correction_controls(self):
        scenario = next(
            s for s in behavior.load_scenarios() if s.id == "wayfinder-map-correction"
        )
        original = (
            behavior.FIXTURE_ROOT
            / scenario.fixture
            / ".project-efforts/consumer-handoff/map.md"
        ).read_text()
        corrected = original.replace(
            "No work performed; endpoint integration awaits the synthetic endpoint.",
            "No work performed; the synthetic endpoint is available.",
        ).replace(
            "The synthetic endpoint is unavailable, blocking endpoint integration.",
            "Endpoint integration may proceed within the established authorization.",
        )
        context = (behavior.FIXTURE_ROOT / scenario.fixture / "context.md").read_text()
        corrected_context = context.replace(
            "The synthetic test endpoint is unavailable, so endpoint integration cannot proceed.",
            "The synthetic test endpoint is now available for authorized integration.",
        )
        results = self.check_candidates(
            scenario,
            {
                "corrected": (corrected, True),
                "stale-context": (corrected, False),
                "missing-context": (corrected, False),
                "missing-endpoint-fact": (corrected, False),
                "stale-blocking-claim": (corrected, False),
                "stale-mirror": (
                    corrected + "\nPlatform team maintains the test environment.\n",
                    False,
                ),
                "invented-approval": (
                    corrected + "\nProduction is approved and may proceed.\n",
                    False,
                ),
                "old-endpoint-blocker": (original, False),
                "lost-unknown": (
                    corrected.replace(
                        "Incident-response responsibility remains unknown",
                        "Incident-response responsibility is assigned",
                    ),
                    False,
                ),
            },
            correct_source=True,
            context_variants={
                **{
                    name: corrected_context
                    for name in (
                        "corrected",
                        "stale-mirror",
                        "invented-approval",
                        "old-endpoint-blocker",
                        "lost-unknown",
                    )
                },
                "stale-context": context,
                "missing-context": None,
                "missing-endpoint-fact": corrected_context.replace(
                    "The synthetic test endpoint is now available for authorized integration.\n",
                    "",
                ),
                "stale-blocking-claim": corrected_context
                + "\nEndpoint integration cannot proceed.\n",
            },
        )
        for name, context_failures in {
            "stale-context": {"glob-any-matches", "glob-none-matches"},
            "missing-context": {"glob-any-matches"},
            "missing-endpoint-fact": {"glob-any-matches"},
            "stale-blocking-claim": {"glob-none-matches"},
        }.items():
            with self.subTest(context_failures=name):
                self.assertEqual(
                    {c.name for c in results[name] if c.passed is False},
                    {f"assert:context.md:{kind}" for kind in context_failures}
                    | {"expect:task_completed"},
                )
        # No failed controls is distinct from proving overall agent behavior.
        self.assertIn(behavior.verdict(results["corrected"]), {"PASS", "INCONCLUSIVE"})

    def test_alternate_layout_control(self):
        scenario = next(
            s for s in behavior.load_scenarios() if s.id == "wayfinder-map-resume"
        )
        original = (
            behavior.FIXTURE_ROOT
            / scenario.fixture
            / ".project-efforts/consumer-handoff/map.md"
        ).read_text()
        corrected = original.replace(
            "Inventory is authorized and incomplete.",
            "Inventory is complete; see [inventory](../../inventory.md).",
        )
        self.check_candidates(
            scenario,
            {
                "bounded-resumption": (corrected, True),
                "formatting-only-rewrite": (
                    corrected.replace("## Route now", "## Ready work"),
                    False,
                ),
            },
            inventory=True,
        )

    def check_candidates(
        self,
        scenario,
        cases,
        *,
        correct_source=False,
        inventory=False,
        context_variants=None,
    ):
        results = {}
        for label, (candidate, expected) in cases.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory() as temporary:
                workspace = behavior.copy_fixture(scenario, Path(temporary))
                before = behavior.snapshot(workspace)
                if correct_source:
                    source = workspace / "responsibilities.md"
                    source.write_text(
                        source.read_text().replace(
                            "Platform team maintains", "Operations maintains"
                        )
                    )
                if context_variants is not None:
                    context = workspace / "context.md"
                    content = context_variants[label]
                    if content is None:
                        context.unlink()
                    else:
                        context.write_text(content)
                if inventory:
                    (workspace / "inventory.md").write_text(
                        "The only consumer call site is src/adapter.py.\n"
                    )
                target = workspace / ".project-efforts/consumer-handoff/map.md"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(candidate)
                evidence = behavior.RunEvidence(
                    scenario=scenario,
                    workspace=workspace,
                    before=before,
                    after=behavior.snapshot(workspace),
                    stdout="[route: router → wayfinder]",
                    stderr="",
                    returncode=0,
                    report={"status": "success"},
                    verification=(),
                    route_components=("wayfinder",),
                )
                results[label] = behavior.evaluate(evidence)
                failures = [c.detail for c in results[label] if c.passed is False]
                self.assertEqual(not failures, expected, failures)
        return results
