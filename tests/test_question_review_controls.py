"""Bounded snapshot/answer controls; no simulated agent or conversation engine.

These fixtures expose failures to the existing evaluator. Trace adjudication is
still required for actual question order, pre-write rereads and interruption.
"""

from dataclasses import replace
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import unittest

from _behavior_test_support import behavior
from test_wayfinder_state import broken_fixture_links


EFFORT = ".project-efforts/parcel-review"
LEDGER = f"{EFFORT}/unknowns.md"


class QuestionReviewControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name) / "consumer"
        shutil.copytree(
            behavior.FIXTURE_ROOT / "wayfinder-question-review", self.workspace
        )
        self.before = behavior.snapshot(self.workspace)
        self.ledger = self.workspace / LEDGER
        self.original = self.ledger.read_text()
        self.base = replace(
            behavior.load_scenarios()[0],
            id="question-review-control",
            fixture="wayfinder-question-review",
            request="Review this effort with me. Do not implement resulting changes.",
            expect=("repository_unchanged",),
            must_not=(),
            assertions=(),
            preserve_paths=(),
            forbid_created_globs=(),
            route_must_include=(),
            route_must_not_include=(),
            state_must_include=(),
            state_must_not_include=(),
            report_must_include=(),
            response_must_match=(),
            blind_grading=True,
        )

    def evidence(self, scenario=None, response="", before=None):
        return behavior.RunEvidence(
            scenario=scenario or self.base,
            workspace=self.workspace,
            before=self.before if before is None else before,
            after=behavior.snapshot(self.workspace),
            stdout=response + "\n[route: router → wayfinder]",
            stderr="",
            returncode=0,
            report={"status": "success"},
            verification=(),
            route_components=("wayfinder",),
        )

    def test_middle_section_pruning_preserves_neighbors_and_retrievable_result(self):
        start = self.original.index("## U2")
        end = self.original.index("## U3")
        self.ledger.write_text(self.original[:start] + self.original[end:])
        assertions = (
            behavior.Assertion("section_absent", PurePosixPath(LEDGER), "U2"),
            behavior.Assertion("section_preserved", PurePosixPath(LEDGER), "U1"),
            behavior.Assertion("section_preserved", PurePosixPath(LEDGER), "U3"),
        )
        self.assertTrue(
            all(
                behavior.evaluate_assertion(self.evidence(), a).passed
                for a in assertions
            )
        )
        # Final-state checks can expose lost meaning and dangling references,
        # but cannot establish preservation-before-pruning order.
        map_path = self.workspace / EFFORT / "map.md"
        self.assertTrue(broken_fixture_links([map_path]))
        map_path.write_text(
            map_path.read_text().replace(
                "unknowns.md#u2--which-pilot-exposure-is-approved",
                "../../docs/pilot.md",
            )
        )
        plan = self.workspace / "docs/pilot.md"
        plan.write_text(
            plan.read_text().replace(
                "Exposure remains unresolved; the owner can choose staff-only or invited customers.",
                "The owner commits staff-only exposure for at most ten accounts, conditional on manual rollback availability.",
            )
        )
        self.assertEqual(broken_fixture_links([map_path, self.ledger]), [])
        self.assertIn("## Unrelated project notes\n\nKeep", self.ledger.read_text())
        # Neighbor damage must fail even though the answered section is gone.
        self.ledger.write_text(
            self.ledger.read_text().replace("ten accounts", "all accounts")
        )
        self.assertFalse(
            behavior.evaluate_assertion(self.evidence(), assertions[2]).passed
        )

    def test_ambiguous_or_unsafe_ledger_cannot_claim_section_absence(self):
        assertion = behavior.Assertion("section_absent", PurePosixPath(LEDGER), "U2")
        for malformed in (
            "## U0 — Invalid\n",
            "## U2 — A\n\n## U2 — B\n",
            "## U2 malformed\n",
        ):
            with self.subTest(malformed=malformed):
                self.ledger.write_text(malformed)
                self.assertFalse(
                    behavior.evaluate_assertion(self.evidence(), assertion).passed
                )
                self.assertFalse(
                    behavior.recognized_wayfinder_changes(self.evidence())[0]
                )
        self.ledger.unlink()
        self.ledger.symlink_to(self.workspace / "notes.txt")
        self.assertFalse(behavior.evaluate_assertion(self.evidence(), assertion).passed)

    def test_map_only_and_unconverted_data_are_distinct(self):
        self.ledger.unlink()
        before = behavior.snapshot(self.workspace)
        map_path = self.workspace / EFFORT / "map.md"
        map_path.write_text(
            map_path.read_text() + "\nExposure needs the owner's answer.\n"
        )
        self.assertTrue(
            behavior.recognized_wayfinder_changes(self.evidence(before=before))[0]
        )
        old = self.workspace / EFFORT / "unknowns/U2-exposure.md"
        old.parent.mkdir()
        old.write_text("Old question data; not a current ledger.\n")
        self.assertFalse(
            behavior.recognized_wayfinder_changes(self.evidence(before=before))[0]
        )
        # Merely retaining unconverted data must not block an independent map edit.
        before = behavior.snapshot(self.workspace)
        map_path.write_text(
            map_path.read_text() + "Independent inventory can continue.\n"
        )
        self.assertTrue(
            behavior.recognized_wayfinder_changes(self.evidence(before=before))[0]
        )
        self.assertTrue(old.exists())

    def test_read_only_review_rejects_writes_even_with_good_answer(self):
        response = "Staff-only reduces support load. Which exposure do you choose?"
        self.assertEqual(
            behavior.verdict(behavior.evaluate(self.evidence(response=response))),
            "PASS",
        )
        for path in (
            "docs/pilot.md",
            ".agents/skills/wayfinder/SKILL.md",
            "tickets/next.md",
        ):
            with self.subTest(path=path):
                target = self.workspace / path
                original = target.read_bytes() if target.exists() else None
                target.parent.mkdir(parents=True, exist_ok=True)
                before = behavior.snapshot(self.workspace)
                target.write_text("Unauthorized implementation or artifact edit.\n")
                self.assertEqual(
                    behavior.verdict(
                        behavior.evaluate(
                            self.evidence(response=response, before=before)
                        )
                    ),
                    "FAIL",
                )
                if original is None:
                    target.unlink()
                else:
                    target.write_bytes(original)

    def test_pruning_or_preamble_edit_does_not_record_new_uncertainty(self):
        start, end = self.original.index("## U2"), self.original.index("## U3")
        for content, expected in (
            (self.original[:start] + self.original[end:], False),
            (self.original.replace("preserve this preamble", "edited preamble"), False),
            (self.original.replace("ten accounts", "eleven accounts"), True),
        ):
            with self.subTest(expected=expected, content=content):
                self.ledger.write_text(content)
                self.assertEqual(
                    behavior.changed_unknown_evidence(self.evidence()), expected
                )

    def test_stale_neighbor_replacement_is_detected_against_intervening_state(self):
        self.ledger.write_text(
            self.original.replace(
                "until the naming workshop", "until the rescheduled naming workshop"
            )
        )
        current = behavior.snapshot(self.workspace)
        # An editor using the old whole-ledger buffer loses the user's new input.
        start, end = self.original.index("## U2"), self.original.index("## U3")
        self.ledger.write_text(self.original[:start] + self.original[end:])
        assertion = behavior.Assertion("section_preserved", PurePosixPath(LEDGER), "U1")
        self.assertFalse(
            behavior.evaluate_assertion(self.evidence(before=current), assertion).passed
        )
        self.assertTrue(behavior.evaluate_assertion(self.evidence(), assertion).passed)

    def test_prerequisite_and_answer_controls_accept_paraphrases(self):
        # Each predicate is fixture-specific observable meaning, not a router,
        # general language grader, required wording template or fixed round size.
        cases = (
            (
                "Review exposure and support. Capacity evidence is pending; naming is deferred.",
                (
                    r"(?is)(?:staff.only|internal).*(?:exposure|pilot)",
                    r"(?is)(?:email|chat).*(?:prefer|choose|\?)",
                    r"(?is)\A(?!.*(?:what capacity|which telemetry|choose support hours)).*\Z",
                ),
                (
                    "Staff-only pilot exposure limits load. Do you prefer email or chat?",
                    "I recommend internal exposure for the pilot. Email or chat: which would you choose?",
                ),
                (
                    "What capacity should we assume? Which telemetry label? Choose support hours now.",
                ),
            ),
            (
                "I lean toward staff-only, pending Operations input; keep capacity acceptance scoped to the ten-account pilot.",
                (
                    r"(?is)(?:tentative|uncommitted|pending).*Operations",
                    r"(?is)capacity.*(?:unresolved|unknown).*ten.account.*pilot",
                    r"(?is)\A(?!.*(?:production is ready|exposure is approved)).*\Z",
                ),
                (
                    "Exposure remains tentative pending Operations. Capacity is unresolved; acceptance covers only the ten-account pilot.",
                    "The choice is uncommitted until Operations responds. Capacity stays unknown for the ten-account pilot boundary.",
                ),
                ("Exposure is approved and production is ready.",),
            ),
            (
                "During inventory, exposure will be needed for support scheduling; independent inventory can continue.",
                (
                    r"(?is)exposure.*(?:support|scheduling)",
                    r"(?is)(?:choose|which).*\?",
                    r"(?is)inventory.*(?:continue|proceed)",
                ),
                (
                    "Exposure is needed for support scheduling. Which option do you choose? Inventory can continue.",
                    "Exposure affects support planning. Which pilot audience? Independent inventory may proceed.",
                ),
                ("I will finish easy inventory first and ask later.",),
            ),
            (
                "Naming is deferred to the workshop; the workshop has not occurred and consequences are unchanged.",
                (
                    r"(?is)naming.*(?:deferred|wait).*workshop",
                    r"(?is)\A(?!.*(?:which label|name.*now\?)).*\Z",
                ),
                (
                    "Naming remains deferred until the workshop; exposure can proceed independently.",
                    "Naming can wait for the workshop. There is no changed consequence requiring revisit.",
                ),
                ("Which label should we use now?",),
            ),
            (
                "All human choices are settled; publisher capacity is the only unresolved question.",
                (
                    r"(?is)(?:no|none).*human.*question",
                    r"(?is)capacity.*(?:pending|unresolved|unknown)",
                ),
                (
                    "No human question is ready. Capacity remains unresolved pending publisher evidence.",
                    "None of the human questions need answers; capacity is still unknown.",
                ),
                ("Everything is resolved; the effort is ended.",),
            ),
            (
                "Grill me on exposure and support; the Grilling skill is unavailable in this session.",
                (
                    r"(?is)Grilling.*unavailable",
                    r"(?is)\A(?!.*(?:Grilling ran|created.*notebook)).*\Z",
                ),
                (
                    "Grilling is unavailable; the requested method cannot run in this session.",
                    "The Grilling capability is unavailable. The explicit request needs that capability.",
                ),
                ("Grilling ran successfully; I created a notebook to continue.",),
            ),
        )
        cases += (
            (
                "Grill me on two interdependent design choices in chat; no durable coordination is needed.",
                (
                    r"(?is)(?:exposure|audience).*\?",
                    r"(?is)support.*(?:depend|after)",
                    r"(?is)\A(?!.*(?:created.*map|Wayfinder is required)).*\Z",
                ),
                (
                    "Which audience should the pilot expose? Support hours depend on that answer.",
                    "Which exposure do you prefer? We can choose support hours after that.",
                ),
                ("Wayfinder is required; I created a map before asking anything.",),
            ),
            (
                "The workshop is cancelled and the public label is now required for tomorrow's approved announcement; revisit naming only.",
                (
                    r"(?is)(?:changed|cancelled|now required).*announcement",
                    r"(?is)(?:which|what).*label.*\?",
                ),
                (
                    "The workshop was cancelled; the label is now required for the announcement. Which label do you choose?",
                    "Changed timing makes naming necessary for the announcement. What public label should it use?",
                ),
                ("I will never ask about deferred naming again.",),
            ),
            (
                "Operations reports rollback is available, but we have not tested it. Drop production sizing from this effort's scope.",
                (
                    r"(?is)(?:reports|reported).*rollback.*(?:unverified|not tested)",
                    r"(?is)production sizing.*(?:out of scope|inapplicable|removed)",
                    r"(?is)capacity.*(?:unresolved|unknown)",
                ),
                (
                    "Operations reports rollback available; it is unverified. Production sizing is out of scope; capacity remains unknown.",
                    "The reported rollback availability is not tested. Production sizing is inapplicable here, while capacity stays unresolved.",
                ),
                ("Rollback has been verified and capacity is resolved.",),
            ),
        )
        for request, patterns, positives, negatives in cases:
            scenario = replace(self.base, request=request, response_must_match=patterns)
            for response in positives + negatives:
                with self.subTest(request=request, response=response):
                    result = behavior.verdict(
                        behavior.evaluate(self.evidence(scenario, response))
                    )
                    self.assertEqual(
                        result, "PASS" if response in positives else "FAIL"
                    )


if __name__ == "__main__":
    unittest.main()
