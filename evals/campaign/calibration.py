"""Blind synthetic grader controls and assess cited, separately supplied reviews.

These helpers validate calibration evidence and agreement, not reviewer
independence or the semantic correctness of the authored answer key.
They never invoke a model or alter a subject campaign's counts.
"""

from __future__ import annotations

import json
from pathlib import Path

from evals.campaign.core import _validate_review, fingerprint
from evals.campaign.schema import VERDICTS, identifier, read_json, relative, text


def _load(source: Path) -> dict:
    corpus = read_json(source)
    if corpus.get("schema") != 1:
        raise ValueError("Unsupported calibration schema")
    rubric = corpus.get("rubric")
    if not isinstance(rubric, list) or not rubric:
        raise ValueError("Calibration needs a nonempty rubric")
    criteria = set()
    for item in rubric:
        if not isinstance(item, dict):
            raise ValueError("Calibration rubric entries must be objects")
        key = identifier(item.get("id"), "calibration criterion id")
        if key in criteria:
            raise ValueError("Duplicate calibration criterion")
        criteria.add(key)
        text(item.get("requirement"), "calibration requirement")
        if item.get("evidence_scope", "any") not in {"saved", "response", "any"}:
            raise ValueError("Invalid calibration evidence_scope")
    cases = corpus.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Calibration needs a nonempty case list")
    ids = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Calibration cases must be objects")
        key = identifier(case.get("id"), "calibration case id")
        if key in ids:
            raise ValueError("Duplicate calibration case")
        ids.add(key)
        evidence = case.get("evidence")
        if not isinstance(evidence, dict):
            raise ValueError("Calibration case evidence must be an object")
        text(evidence.get("request"), "calibration request")
        if not isinstance(evidence.get("response"), str):
            raise ValueError("Calibration response must be a string")
        if not isinstance(evidence.get("observations"), dict):
            raise ValueError("Calibration observations must be an object")
        files = evidence.get("files")
        if not isinstance(files, dict):
            raise ValueError("Calibration saved files must be an object")
        for path, content in files.items():
            relative(path, "calibration saved path")
            if path.startswith("@") or not isinstance(content, str):
                raise ValueError("Saved files need ordinary paths and text content")
        expected = case.get("expected")
        if not isinstance(expected, list):
            raise ValueError("Calibration needs explicit expected judgments")
        seen = set()
        for judgment in expected:
            if not isinstance(judgment, dict):
                raise ValueError("Expected judgments must be objects")
            key = judgment.get("id")
            if key not in criteria or key in seen:
                raise ValueError("Unknown or duplicate expected criterion")
            seen.add(key)
            if judgment.get("verdict") not in VERDICTS:
                raise ValueError("Invalid expected calibration verdict")
            text(judgment.get("rationale"), "expected calibration rationale")
        if seen != criteria:
            raise ValueError("Every calibration case needs every expected criterion")
    return corpus


def _packet(corpus: dict) -> tuple[dict, dict]:
    digest = fingerprint(corpus)
    items = []
    cases = {}
    for index, case in enumerate(corpus["cases"]):
        # Hide descriptive labels and original ordering. Bind even the hidden
        # answer key to the packet so it cannot change after a review is supplied.
        key = "case-" + fingerprint({"corpus": digest, "index": index})[:24]
        evidence = case["evidence"]
        checks = [
            {
                "id": criterion["id"],
                "kind": "semantic",
                "requirement": criterion["requirement"],
                "evidence_scope": criterion.get("evidence_scope", "any"),
            }
            for criterion in corpus["rubric"]
        ]
        items.append(
            {
                "id": key,
                "request": evidence["request"],
                "checks": checks,
                "evidence": {
                    **evidence["files"],
                    "@request": evidence["request"],
                    "@response": evidence["response"],
                    "@inventory": "\n".join(sorted(evidence["files"])),
                    "@observations": json.dumps(
                        evidence["observations"], sort_keys=True
                    ),
                },
            }
        )
        cases[key] = case
    return {
        "schema": 1,
        "kind": "semantic-grader-calibration",
        "corpus_sha256": digest,
        "purpose": "Judge every declared criterion from exact cited evidence; these are synthetic controls, not subject runs.",
        "items": sorted(items, key=lambda item: item["id"]),
    }, cases


def make_packet(source: Path) -> dict:
    """Return a blinded packet; reviews bind to ``fingerprint(packet)``.

    Expected answers, source case names, and revealing source-purpose text are
    omitted. The corpus digest makes later answer-key amendments detectable.
    """
    return _packet(_load(source))[0]


def _review(packet: dict, review: dict) -> None:
    if not isinstance(review, dict) or not isinstance(review.get("items"), list):
        raise ValueError("Calibration review needs an items list")
    for item in review["items"]:
        if not isinstance(item, dict) or not isinstance(item.get("checks", {}), dict):
            raise ValueError("Calibration review items need a checks object")
        for judgment in item.get("checks", {}).values():
            if not isinstance(judgment, dict):
                raise ValueError("Calibration judgments must be objects")
            text(judgment.get("rationale"), "calibration review rationale")
            cites = judgment.get("evidence")
            if not isinstance(cites, list) or not cites:
                raise ValueError("Calibration judgments need exact evidence citations")
            for cite in cites:
                if not isinstance(cite, dict):
                    raise ValueError("Calibration citations must be objects")
                text(cite.get("path"), "calibration citation path")
                text(cite.get("quote"), "calibration citation quote")
    # Reuse campaign packet binding, rubric alignment, exact citation matching
    # and saved-artifact support. Absence remains assessable below, not a pass.
    _validate_review(packet, review)


def assess(source: Path, review: dict) -> dict:
    """Compare a bound review to every authored expectation without model calls.

    Omitted judgments remain INCONCLUSIVE and make ``calibration_passed`` false.
    A concrete mismatch is FAIL. A review with only missing or inconclusive
    mismatches is INCONCLUSIVE. Explicit agreement with an expected
    INCONCLUSIVE may pass; an omitted judgment never does.
    """
    packet, cases = _packet(_load(source))
    _review(packet, review)
    supplied = {item["id"]: item.get("checks", {}) for item in review["items"]}
    rows = []
    total = {
        "cases": len(cases),
        "expected_checks": 0,
        "reviewed_checks": 0,
        "matching_checks": 0,
        "mismatched_checks": 0,
        "missing_checks": 0,
        "inconclusive_checks": 0,
    }
    for item in packet["items"]:
        case = cases[item["id"]]
        checks = []
        for expected in case["expected"]:
            judgment = supplied.get(item["id"], {}).get(expected["id"])
            actual = judgment["verdict"] if judgment is not None else "INCONCLUSIVE"
            agrees = judgment is not None and actual == expected["verdict"]
            outcome = (
                "PASS"
                if agrees
                else "INCONCLUSIVE"
                if actual == "INCONCLUSIVE"
                else "FAIL"
            )
            total["expected_checks"] += 1
            total["reviewed_checks"] += judgment is not None
            total["matching_checks"] += agrees
            total["mismatched_checks"] += judgment is not None and not agrees
            total["missing_checks"] += judgment is None
            total["inconclusive_checks"] += actual == "INCONCLUSIVE"
            checks.append(
                {
                    "id": expected["id"],
                    "expected": expected["verdict"],
                    "actual": actual,
                    "present": judgment is not None,
                    "agreement": agrees,
                    "verdict": outcome,
                    "expected_rationale": expected["rationale"],
                    "review": judgment,
                }
            )
        rows.append({"id": item["id"], "source_case_id": case["id"], "checks": checks})
    outcomes = [check["verdict"] for row in rows for check in row["checks"]]
    verdict = (
        "FAIL"
        if "FAIL" in outcomes
        else "INCONCLUSIVE"
        if "INCONCLUSIVE" in outcomes
        else "PASS"
    )
    return {
        "schema": 1,
        "kind": "semantic-grader-calibration",
        "packet_sha256": fingerprint(packet),
        "corpus_sha256": packet["corpus_sha256"],
        "reviewer": review["reviewer"],
        "verdict": verdict,
        "calibration_passed": verdict == "PASS",
        "totals": total,
        "cases": rows,
        "limits": [
            "Calibration agreement is separate from subject behavior and invocation counts.",
            "Exact citations bind supplied judgments to evidence; they do not prove semantic correctness or reviewer independence.",
            "Authored expectations require independent review; synthetic agreement does not establish live instruction compliance.",
        ],
    }
