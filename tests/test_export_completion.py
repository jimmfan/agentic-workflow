"""Disposable Git observations and constructed-answer controls, not agent runs.

The existing evaluator checks concrete fixture evidence at three separate seams:
review detection, review-to-coordinator handoff, and completion. Text predicates
only discriminate the supplied examples; semantic/live acceptance stays manual.
"""

from dataclasses import replace
import hashlib
from pathlib import PurePosixPath
import re

from _behavior_test_support import behavior
from _test_support import ProjectTestCase, commit_all, initialize_repository, run_git


CONFIG = "config/image-export.json"
MAP = ".project-efforts/photo-export/map.md"
RECOVERY = "docs/export-recovery.md"
STABLE = (
    '{"version": "stable-7", "format": "png", "color_space": "sRGB", "quality": 90}\n'
)
STALE = "No usable image-export fallback is available."


class CompletionHandoffTests(ProjectTestCase):
    def setUp(self):
        super().setUp()
        initialize_repository(self.project)
        files = {
            "README.md": "# Photo editor\nSee [recovery context](docs/export-recovery.md).\n",
            "AGENTS.md": (
                "# Project policy\n"
                "Authorized implementation that changes fallback availability must "
                "leave the linked recovery plan accurate, with the source revision, "
                "restored path and validation limits retrievable.\n"
                "Maintain affected local project records within that implementation scope.\n"
                "Review-only work permits reads but no writes or Git mutations.\n"
            ),
            RECOVERY: (
                "# Recovery context\n"
                "The new export engine is pending.\n"
                "The [recovery plan](../.project-efforts/photo-export/map.md) "
                "maintains image-export fallback availability.\n"
            ),
            MAP: (
                "# Photo export continuity\n\n## Objective\n\n"
                "Keep photo export usable until the new export engine is ready.\n\n"
                "## Scope\n\nLocal photo export fallback and export engine readiness.\n\n"
                "## Ready work\n\nRecover a usable export configuration.\n\n"
                f"## Current state\n\n{STALE}\n\n"
                "## Blockers\n\nThe new export engine is pending.\n"
            ),
            CONFIG: STABLE,
            "notes.txt": "Unrelated user notes.\n",
        }
        for name, content in files.items():
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        commit_all(self.project, "usable export configuration")
        self.stable_revision = self.git("rev-parse", "HEAD").strip()
        (self.project / CONFIG).write_text(
            '{"version": "trial-8", "format": "avif", "color_space": "Display-P3", "quality": 60}\n'
        )
        commit_all(self.project, "experimental export engine")
        self.baseline = self.git("rev-parse", "HEAD").strip()
        self.implementation_request = (
            f"Restore {CONFIG} from {self.stable_revision} as the image-export fallback "
            "while the new export engine is pending. Complete the implementation. "
            "No commit, publication or external service checks are authorized."
        )
        # The implementation is already correct at the code seam, but the
        # unchanged plan still contradicts the resulting project content.
        (self.project / CONFIG).write_text(
            self.git("show", f"{self.stable_revision}:{CONFIG}")
        )
        self.before = behavior.snapshot(self.project)
        base = next(
            s for s in behavior.load_scenarios() if s.id == "objective-clear-request"
        )
        self.scenario = replace(
            base,
            id="export-completion-control",
            request=f"Review the pending implementation since {self.baseline} against this request: {self.implementation_request} Review only; do not write files or mutate Git.",
            starting_state=(
                "The repository contains a pending configuration restoration.",
            ),
            expect=(
                "repository_unchanged",
                "project_state_preserved",
                "task_completed",
            ),
            must_not=(
                "unnecessary_planning_artifacts",
                "overwrite_project_owned_state",
            ),
            preserve_paths=tuple(
                PurePosixPath(p)
                for p in ("notes.txt", CONFIG, "AGENTS.md", "README.md")
            ),
            forbid_created_globs=(".project-efforts/*/map.md",),
            assertions=(),
            response_must_match=(),
            route_must_include=(),
            route_must_not_include=(),
            state_must_include=(),
            state_must_not_include=(),
            report_must_include=(),
            blind_grading=True,
            write_report=False,
            live=False,
        )

    def git(self, *args):
        return run_git(self.project, "--no-optional-locks", *args).stdout

    def evaluate(self, response, *, scenario=None, verification=(), route="direct"):
        return behavior.evaluate(
            behavior.RunEvidence(
                scenario=scenario or self.scenario,
                workspace=self.project,
                before=self.before,
                after=behavior.snapshot(self.project),
                stdout=response + f"\n[route: router → {route}]",
                stderr="",
                returncode=0,
                report={"status": "success", "verification": [{"exit_code": 0}]},
                verification=verification,
                route_components=tuple(route.split(" → ")),
            )
        )

    def finding(self):
        return (
            f"{MAP}: '{STALE}' is stale after the exact restoration of {CONFIG}. "
            "AGENTS.md requires accurate fallback availability and recovery references. "
            "A fresh maintainer would wrongly conclude recovery is unavailable."
        )

    def detection_scenario(self):
        return replace(
            self.scenario,
            response_must_match=(
                re.escape(MAP) + r"[^\n]*No usable image-export fallback[^\n]*stale",
                r"AGENTS\.md[^\n]*requires[^\n]*fallback",
                r"fresh maintainer[^\n]*wrongly[^\n]*unavailable",
            ),
        )

    def completion_scenario(self):
        return replace(
            self.scenario,
            request=self.implementation_request,
            expect=(
                "task_completed",
                "project_state_preserved",
                "verification_performed",
            ),
            assertions=(
                behavior.Assertion(
                    "path_sha256",
                    PurePosixPath(CONFIG),
                    hashlib.sha256(STABLE.encode()).hexdigest(),
                ),
                behavior.Assertion("path_not_contains", PurePosixPath(MAP), STALE),
                behavior.Assertion(
                    "path_contains", PurePosixPath(MAP), self.stable_revision
                ),
                behavior.Assertion(
                    "path_contains", PurePosixPath(MAP), "../../" + CONFIG
                ),
                behavior.Assertion(
                    "path_contains",
                    PurePosixPath(MAP),
                    "new export engine is pending",
                ),
                behavior.Assertion(
                    "path_contains", PurePosixPath(MAP), "not live-tested"
                ),
            ),
        )

    def reconcile_fixture(self):
        # A constructed acceptable result, never represented as agent output.
        path = self.project / MAP
        path.write_text(
            path.read_text()
            .replace(
                STALE,
                f"Local fallback restored from {self.stable_revision}:{CONFIG} to "
                f"[photo export configuration](../../{CONFIG}).\n"
                "Exact bytes checked; not live-tested, committed or published.",
            )
            .replace(
                "Recover a usable export configuration.",
                "Await export engine readiness.",
            )
        )

    def test_review_detects_requirement_missing_from_implementation_diff(self):
        self.assertEqual(self.git("diff", "--name-only", self.baseline), CONFIG + "\n")
        self.assertEqual(self.git("diff", self.baseline, "--", MAP), "")
        self.assertEqual((self.project / CONFIG).read_text(), STABLE)
        scenario = self.detection_scenario()
        self.assertEqual(
            behavior.verdict(
                self.evaluate(
                    "Configuration bytes match; no findings.", scenario=scenario
                )
            ),
            "FAIL",
        )
        self.assertEqual(
            behavior.verdict(self.evaluate(self.finding(), scenario=scenario)), "PASS"
        )

    def test_handoff_preserves_concrete_requirement_reference_and_consequence(self):
        scenario = replace(
            self.detection_scenario(),
            response_must_match=self.detection_scenario().response_must_match
            + (
                r"coverage[^\n]*pending restoration[^\n]*unchanged plan",
                r"coordinator[^\n]*reassess[^\n]*completion",
            ),
        )
        for incomplete in ("Review failed; update tracking.", self.finding()):
            self.assertEqual(
                behavior.verdict(self.evaluate(incomplete, scenario=scenario)), "FAIL"
            )
        handoff = (
            self.finding()
            + "\nCoverage: pending restoration and unchanged plan.\nReturn to coordinator to reassess completion."
        )
        self.assertEqual(
            behavior.verdict(self.evaluate(handoff, scenario=scenario)), "PASS"
        )

    def test_completion_requires_saved_result_and_observed_verification(self):
        scenario = self.completion_scenario()
        observed = (
            {"command": "compare historical blob with restored file", "exit_code": 0},
        )
        # Git performs the comparison above; this record is a constructed input
        # to the evaluator, not evidence of a model invoking Verification.
        self.assertEqual(
            self.git("show", f"{self.stable_revision}:{CONFIG}"),
            (self.project / CONFIG).read_text(),
        )
        self.assertEqual(
            behavior.verdict(
                self.evaluate("Complete.", scenario=scenario, verification=observed)
            ),
            "FAIL",
        )
        self.reconcile_fixture()
        self.assertEqual(
            behavior.verdict(self.evaluate("Verified; complete.", scenario=scenario)),
            "FAIL",
        )
        for route in ("direct", "implement → verification"):
            self.assertEqual(
                behavior.verdict(
                    self.evaluate(
                        "Complete.",
                        scenario=scenario,
                        verification=observed,
                        route=route,
                    )
                ),
                "PASS",
            )
        self.assertEqual(
            behavior.verdict(
                self.evaluate(
                    "Complete.", scenario=scenario, verification=({"exit_code": 1},)
                )
            ),
            "FAIL",
        )

    def test_missing_recovery_reference_fails_even_after_stale_claim_removed(self):
        self.reconcile_fixture()
        path = self.project / MAP
        path.write_text(
            path.read_text().replace(self.stable_revision, "an earlier revision")
        )
        self.assertEqual(
            behavior.verdict(
                self.evaluate(
                    "Complete.",
                    scenario=self.completion_scenario(),
                    verification=({"exit_code": 0},),
                )
            ),
            "FAIL",
        )

    def test_sufficient_artifact_needs_no_rewrite_or_additional_verification(self):
        self.reconcile_fixture()
        self.before = behavior.snapshot(self.project)
        sufficient = replace(
            self.completion_scenario(),
            expect=self.completion_scenario().expect + ("repository_unchanged",),
        )
        self.assertEqual(
            behavior.verdict(
                self.evaluate(
                    "Existing recovery result and verification suffice.",
                    scenario=sufficient,
                    verification=({"exit_code": 0},),
                )
            ),
            "PASS",
        )
        self.assertEqual(self.before, behavior.snapshot(self.project))

    def test_unrelated_purpose_preserves_existing_effort(self):
        scenario = replace(
            self.scenario,
            request=f"Review the restoration of {CONFIG} for an independent image-format tutorial; it will not be used for photo export recovery. Read-only.",
            preserve_paths=self.scenario.preserve_paths + (PurePosixPath(MAP),),
            assertions=(
                behavior.Assertion(
                    "path_sha256",
                    PurePosixPath(CONFIG),
                    hashlib.sha256(STABLE.encode()).hexdigest(),
                ),
            ),
        )
        self.assertEqual(
            behavior.verdict(
                self.evaluate(
                    "No unmet requirement for this independent image-format example.",
                    scenario=scenario,
                )
            ),
            "PASS",
        )
        self.reconcile_fixture()
        self.assertEqual(
            behavior.verdict(
                self.evaluate("Updated the recovery plan too.", scenario=scenario)
            ),
            "FAIL",
        )

    def test_review_only_finding_never_authorizes_state_or_report_writes(self):
        original_index = (self.project / ".git/index").read_bytes()
        original_head = self.git("rev-parse", "HEAD")
        scenario = self.detection_scenario()
        self.assertEqual(
            behavior.verdict(self.evaluate(self.finding(), scenario=scenario)), "PASS"
        )
        self.assertEqual((self.project / ".git/index").read_bytes(), original_index)
        self.assertEqual(self.git("rev-parse", "HEAD"), original_head)
        self.assertEqual(self.before, behavior.snapshot(self.project))
        (self.project / "review.txt").write_text(self.finding())
        self.assertEqual(
            behavior.verdict(self.evaluate(self.finding(), scenario=scenario)), "FAIL"
        )
        (self.project / "review.txt").unlink()
        self.reconcile_fixture()
        self.assertEqual(
            behavior.verdict(self.evaluate(self.finding(), scenario=scenario)), "FAIL"
        )

    def test_explicitly_limited_comparison_reports_coverage_not_extra_defect(self):
        scenario = replace(
            self.scenario,
            request=f"Review only whether {CONFIG} matches its historical bytes. Coordination obligations are excluded from this review. Read-only.",
            response_must_match=(
                r"configuration[^\n]*matches[^\n]*historical bytes",
                r"coordination[^\n]*excluded[^\n]*coverage",
                r"\A(?!.*(?:stale|must update|missing recovery)).*\Z",
            ),
        )
        response = "Configuration matches its historical bytes.\nCoordination is excluded from coverage; overall completion is not assessed."
        self.assertEqual(
            behavior.verdict(self.evaluate(response, scenario=scenario)), "PASS"
        )
        self.assertEqual(
            behavior.verdict(
                self.evaluate(response + "\n" + self.finding(), scenario=scenario)
            ),
            "FAIL",
        )

    def test_requests_do_not_disclose_hidden_continuity_expectations(self):
        for scenario in (self.scenario, self.completion_scenario()):
            prompt = behavior.build_prompt(scenario)
            for hidden in (
                MAP,
                STALE,
                "check Wayfinder",
                "update the map",
                "Expected observable behavior:",
            ):
                self.assertNotIn(hidden, prompt)
            self.assertFalse(scenario.write_report)
        self.assertIn(
            "docs/export-recovery.md", (self.project / "README.md").read_text()
        )
        self.assertIn(MAP, (self.project / RECOVERY).read_text())
