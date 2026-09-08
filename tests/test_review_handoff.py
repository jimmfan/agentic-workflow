"""Git observations and synthetic evaluator controls, not a review implementation.

No agent runs here. Explicit candidate findings exercise the existing scenario
evaluator; Git commands establish which concrete fixture defects are observable.
"""

from dataclasses import replace
from pathlib import PurePosixPath
import unittest

from _behavior_test_support import behavior
from _test_support import (
    ProjectTestCase,
    commit_all,
    initialize_repository,
    run_git,
    workspace_snapshot,
)


TOTAL = "def total(items):\n    return sum(items)\n"
BAD_TOTAL = "def total(items):\n    return sum(items) - 1\n"
NORMALIZE = "def normalize(text):\n    return text.lower()\n"
BAD_NORMALIZE = "def normalize(text):\n    return text.upper()\n"
BAD_SLUG = 'def slug(text):\n    return text.replace(" ", "_")\n'
FINDINGS = {
    "total": "staged.py: total([2, 3]) returns 4; the request requires 5.",
    "normalize": "unstaged.py: normalize('Hi') returns HI; the request requires hi.",
    "slug": "new.py: slug('a b') returns a_b; the request requires a-b.",
}
# Match concrete fixture outcomes, not ordinary instruction prose or an exact
# review-report template. A status=success claim alone cannot satisfy these.
OUTCOMES = {
    "total": r"staged\.py[^\n]*total[^\n]*4[^\n]*5",
    "normalize": r"unstaged\.py[^\n]*normalize[^\n]*HI[^\n]*hi",
    "slug": r"new\.py[^\n]*slug[^\n]*a_b[^\n]*a-b",
}


class ReviewHandoffTests(ProjectTestCase):
    def setUp(self):
        super().setUp()
        initialize_repository(self.project)
        (self.project / "staged.py").write_text(TOTAL)
        (self.project / "unstaged.py").write_text(NORMALIZE)
        (self.project / "earlier.py").write_text("VALUE = 1\n")
        (self.project / "shared.py").write_text(
            TOTAL + "\n" * 20 + 'def tagline():\n    return "original"\n'
        )
        commit_all(self.project, "review baseline")
        self.baseline = self.git("rev-parse", "HEAD").strip()
        self.scenario = replace(
            next(
                s
                for s in behavior.load_scenarios()
                if s.id == "objective-clear-request"
            ),
            id="review-handoff-control",
            request=(
                "Review only this implementation scope against the current request: "
                "total([2, 3]) must return 5, normalize('Hi') must return 'hi', and "
                "slug('a b') must return 'a-b'. Include earlier.py's implementation "
                "commit and the relevant staged.py, unstaged.py, and new.py changes "
                f"since {self.baseline}. Review read-only; keep unrelated user work."
            ),
            expect=(
                "task_completed",
                "repository_unchanged",
                "project_state_preserved",
            ),
            must_not=("overwrite_project_owned_state",),
            preserve_paths=(PurePosixPath("README.md"),),
            route_must_include=("code-review",),
            assertions=(),
            verification_command="Inspect the supplied scope without changing it.",
        )

    def git(self, *args):
        return run_git(self.project, *args).stdout

    def pending(self, kind):
        if kind == "total":
            (self.project / "staged.py").write_text(BAD_TOTAL)
            self.git("add", "staged.py")
        elif kind == "normalize":
            (self.project / "unstaged.py").write_text(BAD_NORMALIZE)
        elif kind == "slug":
            (self.project / "new.py").write_text(BAD_SLUG)
        else:
            self.fail(f"unknown fixture kind: {kind}")

    def earlier_commit(self):
        (self.project / "earlier.py").write_text("VALUE = 2\n")
        commit_all(self.project, "earlier implementation")

    def observe_preservation(self):
        # The existing project snapshot intentionally excludes Git internals.
        # Observe the index bytes and HEAD separately, without refreshing status.
        return (
            workspace_snapshot(self.project),
            (self.project / ".git/index").read_bytes(),
            self.git("rev-parse", "HEAD"),
        )

    def evaluate(self, response, *, required=(), scenario=None, before=None):
        scenario = replace(
            scenario or self.scenario,
            response_must_match=tuple(OUTCOMES[kind] for kind in required)
            + (scenario.response_must_match if scenario else ()),
        )
        evidence = behavior.RunEvidence(
            scenario=scenario,
            workspace=self.project,
            before=before if before is not None else behavior.snapshot(self.project),
            after=behavior.snapshot(self.project),
            stdout=response + "\n[route: router → code-review]",
            stderr="",
            returncode=0,
            report={"status": "success", "summary": "Both reviews passed; complete."},
            verification=(),
            route_components=("code-review",),
        )
        return behavior.evaluate(evidence)

    def assert_rejected(self, results):
        self.assertEqual(behavior.verdict(results), "FAIL", results)
        self.assertTrue(
            any(r.name.startswith("response:") and r.passed is False for r in results)
        )

    def test_staged_only_defect_is_absent_from_committed_range(self):
        self.pending("total")
        self.assertEqual(self.git("diff", f"{self.baseline}...HEAD"), "")
        self.assertEqual(self.git("diff"), "")
        cached = self.git("diff", "--cached")
        self.assertIn("+    return sum(items) - 1", cached)
        self.assert_rejected(self.evaluate("No findings.", required=("total",)))
        self.assertEqual(
            behavior.verdict(self.evaluate(FINDINGS["total"], required=("total",))),
            "PASS",
        )

    def test_unstaged_only_defect_is_absent_from_committed_range(self):
        self.pending("normalize")
        self.assertEqual(self.git("diff", f"{self.baseline}...HEAD"), "")
        self.assertEqual(self.git("diff", "--cached"), "")
        self.assertIn("+    return text.upper()", self.git("diff"))
        self.assert_rejected(self.evaluate("No findings.", required=("normalize",)))
        self.assertEqual(
            behavior.verdict(
                self.evaluate(FINDINGS["normalize"], required=("normalize",))
            ),
            "PASS",
        )

    def test_untracked_defect_requires_resulting_new_file_content(self):
        self.pending("slug")
        for arguments in ((f"{self.baseline}...HEAD",), ("--cached",), ()):
            self.assertEqual(self.git("diff", *arguments), "")
        self.assertEqual(
            self.git("ls-files", "--others", "--exclude-standard"), "new.py\n"
        )
        self.assertEqual((self.project / "new.py").read_text(), BAD_SLUG)
        self.assert_rejected(self.evaluate("No findings.", required=("slug",)))
        self.assertEqual(
            behavior.verdict(self.evaluate(FINDINGS["slug"], required=("slug",))),
            "PASS",
        )

    def test_earlier_commit_does_not_cover_newer_defective_pending_work(self):
        self.earlier_commit()
        for kind in FINDINGS:
            self.pending(kind)
        before = self.observe_preservation()
        self.assertEqual(
            set(self.git("--no-optional-locks", "status", "--short").splitlines()),
            {"M  staged.py", " M unstaged.py", "?? new.py"},
        )
        self.assertEqual(
            self.git("diff", "--name-only", f"{self.baseline}...HEAD"), "earlier.py\n"
        )
        self.assertIn("- 1", self.git("diff", "--cached", "--", "staged.py"))
        self.assertIn("upper", self.git("diff", "--", "unstaged.py"))
        self.assertEqual(
            self.git("ls-files", "--others", "--exclude-standard"), "new.py\n"
        )
        # Execute the tiny fixture functions to establish defects independently
        # of their labels and the candidate review reports.
        for filename, function, argument, actual in (
            ("staged.py", "total", [2, 3], 4),
            ("unstaged.py", "normalize", "Hi", "HI"),
            ("new.py", "slug", "a b", "a_b"),
        ):
            namespace = {}
            exec(
                compile((self.project / filename).read_text(), filename, "exec"),
                namespace,
            )
            self.assertEqual(namespace[function](argument), actual)
        required = tuple(FINDINGS)
        self.assert_rejected(
            self.evaluate(
                "earlier.py: VALUE changes from 1 to 2. No defects.", required=required
            )
        )
        self.assert_rejected(
            self.evaluate(
                "\n".join(FINDINGS[k] for k in ("total", "normalize")),
                required=required,
            )
        )
        self.assertEqual(
            behavior.verdict(
                self.evaluate("\n".join(FINDINGS.values()), required=required)
            ),
            "PASS",
        )
        self.assertEqual(before, self.observe_preservation())

    def test_current_request_is_sufficient_without_spec_file(self):
        self.pending("total")
        self.assertFalse((self.project / "spec.md").exists())
        self.assertFalse((self.project / "docs").exists())
        self.assertIn(self.scenario.request, behavior.build_prompt(self.scenario))
        self.assertEqual(
            behavior.verdict(self.evaluate(FINDINGS["total"], required=("total",))),
            "PASS",
        )
        self.assert_rejected(
            self.evaluate(
                "Cannot review without a tracker or separate spec file.",
                required=("total",),
            )
        )

    def test_committed_only_scope_excludes_pending_defects(self):
        self.earlier_commit()
        for kind in FINDINGS:
            self.pending(kind)
        scenario = replace(
            self.scenario,
            request=f"Review committed changes only in {self.baseline}...HEAD. Exclude pending work. VALUE must be 2.",
            response_must_match=(
                r"earlier\.py[^\n]*VALUE[^\n]*2",
                r"\A(?!.*(?:staged\.py[^\n]*total[^\n]*4|unstaged\.py[^\n]*normalize[^\n]*HI|new\.py[^\n]*slug[^\n]*a_b)).*\Z",
            ),
        )
        before = self.observe_preservation()
        self.assertEqual(
            self.git("diff", "--name-only", f"{self.baseline}...HEAD"), "earlier.py\n"
        )
        response = (
            "earlier.py: VALUE is 2, meeting the committed-only request.\n"
            "Pending staged.py, unstaged.py, and new.py were excluded from this review."
        )
        self.assertEqual(
            behavior.verdict(self.evaluate(response, scenario=scenario)), "PASS"
        )
        self.assert_rejected(
            self.evaluate(response + "\n" + FINDINGS["total"], scenario=scenario)
        )
        self.assertEqual(before, self.observe_preservation())

    def test_same_file_hunks_and_unrelated_work_need_pre_edit_attribution(self):
        shared = self.project / "shared.py"
        shared.write_text(shared.read_text().replace('"original"', '"user wording"'))
        (self.project / "notes.txt").write_text("Unrelated user draft.\n")
        pre_edit = workspace_snapshot(self.project)
        self.git("add", "shared.py")
        shared.write_text(
            shared.read_text().replace("return sum(items)", "return sum(items) - 1")
        )
        before = self.observe_preservation()
        self.assertIn("user wording", self.git("diff", "--cached", "--", "shared.py"))
        self.assertNotIn(
            "sum(items) - 1", self.git("diff", "--cached", "--", "shared.py")
        )
        self.assertIn("sum(items) - 1", self.git("diff", "--", "shared.py"))
        combined = self.git("diff", "HEAD", "--", "shared.py")
        self.assertEqual(
            sum(line.startswith("@@") for line in combined.splitlines()), 2
        )
        self.assertIn(b"user wording", pre_edit["shared.py"][1])
        scenario = replace(
            self.scenario,
            request="Review total's pending change in shared.py: total([2, 3]) must be 5. The tagline hunk and notes.txt predate this task and are unrelated.",
            response_must_match=(
                r"shared\.py[^\n]*total[^\n]*4[^\n]*5",
                r"\A(?!.*(?:tagline|notes\.txt)[^\n]*(?:defect|must change)).*\Z",
            ),
        )
        good = (
            "shared.py: total([2, 3]) returns 4; acceptance requires 5.\n"
            "The tagline hunk and notes.txt are unrelated user work, excluded and unchanged."
        )
        self.assertEqual(
            behavior.verdict(self.evaluate(good, scenario=scenario)), "PASS"
        )
        self.assert_rejected(
            self.evaluate(
                good + "\nshared.py: tagline must change back to original.",
                scenario=scenario,
            )
        )
        self.assert_rejected(
            self.evaluate("No findings in shared.py.", scenario=scenario)
        )
        self.assertEqual(before, self.observe_preservation())

    def test_git_observes_deletion_rename_and_distinct_index_result(self):
        self.git("mv", "staged.py", "renamed.py")
        (self.project / "unstaged.py").unlink()
        (self.project / "renamed.py").write_text(BAD_TOTAL)
        before = self.observe_preservation()
        self.assertEqual(self.git("diff", f"{self.baseline}...HEAD"), "")
        self.assertEqual(
            self.git("diff", "--cached", "--name-status", "--find-renames"),
            "R100\tstaged.py\trenamed.py\n",
        )
        self.assertEqual(
            set(self.git("diff", "--name-status").splitlines()),
            {"M\trenamed.py", "D\tunstaged.py"},
        )
        self.assertIn("-def normalize(text):", self.git("diff", "--", "unstaged.py"))
        self.assertEqual(self.git("show", ":renamed.py"), TOTAL)
        self.assertEqual((self.project / "renamed.py").read_text(), BAD_TOTAL)
        self.assertEqual(before, self.observe_preservation())

    def test_preservation_observations_detect_file_index_and_head_mutations(self):
        self.pending("total")
        self.pending("normalize")
        self.pending("slug")
        before = self.observe_preservation()
        before_evaluation = behavior.snapshot(self.project)
        (self.project / "README.md").write_text("Overwritten unrelated work.\n")
        self.assertNotEqual(before[0], self.observe_preservation()[0])
        results = self.evaluate(
            "\n".join(FINDINGS.values()),
            required=tuple(FINDINGS),
            before=before_evaluation,
        )
        failures = {r.name for r in results if r.passed is False}
        self.assertIn("expect:repository_unchanged", failures)
        self.assertIn("expect:project_state_preserved", failures)
        self.git("add", "unstaged.py")
        self.assertNotEqual(before[1], self.observe_preservation()[1])
        # Deliberately mutate the disposable fixture as a negative control.
        self.git("commit", "-qm", "unauthorized review commit control")
        self.assertNotEqual(before[2], self.observe_preservation()[2])


if __name__ == "__main__":
    unittest.main()
