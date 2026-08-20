#!/usr/bin/env python3
"""Validate behavioral contracts and run deterministic or opt-in live scenarios."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from typing import Iterable, Mapping, Sequence

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
TEST_ROOT = Path(__file__).resolve().parent
SCENARIO_ROOT = TEST_ROOT / "scenarios"
FIXTURE_ROOT = TEST_ROOT / "fixtures"
ADOPT = PACKAGE_ROOT / "scripts" / "adopt.py"
REPORT_PATH = PurePosixPath(".behavior-evidence/report.json")
VERIFICATION_LOG = PurePosixPath(".behavior-evidence/verification.jsonl")
SCHEMA_VERSION = 1
MINIMUM_PYTHON = (3, 11)
ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
ROUTE_CANDIDATE_PATTERN = re.compile(r"\[route:", re.IGNORECASE)
ROUTE_PATTERN = re.compile(
    r"\[route:\s*router\s*(?:→|->)\s*"
    r"([a-z0-9]+(?:-[a-z0-9]+)*(?:\s*(?:→|->)\s*[a-z0-9]+(?:-[a-z0-9]+)*)*)\s*\]",
    re.IGNORECASE,
)
URL_PATTERN = re.compile(r"https?://", re.IGNORECASE)

EXPECTATIONS = {
    "task_completed",
    "repository_unchanged",
    "appropriate_validation",
    "external_fact_researched",
    "uncertainty_recorded_or_blocked",
    "existing_state_reused",
    "meaningful_repository_change",
    "verification_performed",
    "verification_failure_recovered",
    "blocked_cleanly",
    "project_state_preserved",
    "unresolved_unknowns_preserved",
    "lifecycle_state_preserved",
}

PROHIBITIONS = {
    "claim_unexecuted_provider",
    "unnecessary_planning_artifacts",
    "manufacture_uncertainty",
    "invent_external_fact",
    "full_discovery_for_lookup",
    "silent_decision_invention",
    "repeat_resolved_discovery",
    "overwrite_project_owned_state",
    "ignore_persisted_decisions",
    "success_after_failed_check",
    "fabricate_project_values",
    "placeholder_infrastructure",
    "invent_unknown_answers",
}

ASSERTION_KINDS = {
    "glob_any_contains",
    "glob_contains",
    "glob_count",
    "glob_none_contains",
    "path_exists",
    "path_not_exists",
    "path_contains",
    "path_not_contains",
}

SCENARIO_FIELDS = {
    "schema_version",
    "id",
    "name",
    "fixture",
    "request",
    "starting_state",
    "expect",
    "must_not",
    "live",
    "verification_command",
    "preserve_paths",
    "forbid_created_globs",
    "route_must_not_include",
    "state_must_include",
    "state_must_not_include",
    "report_must_include",
    "assertions",
}

FRAMEWORK_CHANGE_PREFIXES = (
    ".agent-workflow/",
    ".agents/",
    ".behavior-evidence/",
)
FRAMEWORK_CHANGE_PATHS = {"AGENTS.md", "CLAUDE.md"}


class BehaviorError(RuntimeError):
    """A scenario, fixture, runner, or evidence contract error."""


@dataclass(frozen=True)
class Assertion:
    kind: str
    path: PurePosixPath
    value: str | None = None
    count: int | None = None


@dataclass(frozen=True)
class Scenario:
    source: Path
    id: str
    name: str
    fixture: str
    request: str
    starting_state: tuple[str, ...]
    expect: tuple[str, ...]
    must_not: tuple[str, ...]
    live: bool
    verification_command: str
    preserve_paths: tuple[PurePosixPath, ...]
    forbid_created_globs: tuple[str, ...]
    route_must_not_include: tuple[str, ...]
    state_must_include: tuple[PurePosixPath, ...]
    state_must_not_include: tuple[PurePosixPath, ...]
    report_must_include: tuple[str, ...]
    assertions: tuple[Assertion, ...]


@dataclass(frozen=True)
class Entry:
    kind: str
    identity: str


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class RunEvidence:
    scenario: Scenario
    workspace: Path
    before: Mapping[str, Entry]
    after: Mapping[str, Entry]
    stdout: str
    stderr: str
    returncode: int
    report: Mapping[str, object]
    verification: tuple[Mapping[str, object], ...]
    route_components: tuple[str, ...]


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except (AttributeError, OSError, ValueError):
                pass


def safe_relative(value: object, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise BehaviorError(f"{label} must be a non-empty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise BehaviorError(f"{label} is unsafe: {value!r}")
    return path


def string_list(raw: object, label: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(raw, list) or (not raw and not allow_empty):
        raise BehaviorError(f"{label} must be a {'possibly empty ' if allow_empty else 'non-empty '}string array")
    if any(not isinstance(item, str) or not item.strip() for item in raw):
        raise BehaviorError(f"{label} must contain only non-empty strings")
    return tuple(item.strip() for item in raw)


def load_assertions(raw: object, label: str) -> tuple[Assertion, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise BehaviorError(f"{label} must be an array of assertion tables")
    assertions: list[Assertion] = []
    for index, item in enumerate(raw):
        item_label = f"{label}[{index}]"
        if not isinstance(item, dict):
            raise BehaviorError(f"{item_label} must be a table")
        if set(item) - {"kind", "path", "value", "count"}:
            raise BehaviorError(f"{item_label} has unknown fields")
        kind = item.get("kind")
        if kind not in ASSERTION_KINDS:
            raise BehaviorError(f"{item_label} has unsupported kind {kind!r}")
        path = safe_relative(item.get("path"), f"{item_label}.path")
        value = item.get("value")
        count = item.get("count")
        needs_value = kind in {
            "glob_any_contains",
            "glob_contains",
            "glob_none_contains",
            "path_contains",
            "path_not_contains",
        }
        needs_count = kind == "glob_count"
        if needs_value and (not isinstance(value, str) or not value):
            raise BehaviorError(f"{item_label}.value must be a non-empty string")
        if not needs_value and value is not None:
            raise BehaviorError(f"{item_label}.value is not valid for {kind}")
        if needs_count and (not isinstance(count, int) or isinstance(count, bool) or count < 0):
            raise BehaviorError(f"{item_label}.count must be a non-negative integer")
        if not needs_count and count is not None:
            raise BehaviorError(f"{item_label}.count is not valid for {kind}")
        assertions.append(Assertion(kind=kind, path=path, value=value, count=count))
    return tuple(assertions)


def load_scenario(path: Path) -> Scenario:
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise BehaviorError(f"cannot read scenario {path}: {exc}") from exc
    if set(raw) - SCENARIO_FIELDS:
        unknown = ", ".join(sorted(set(raw) - SCENARIO_FIELDS))
        raise BehaviorError(f"scenario {path.name} has unknown fields: {unknown}")
    required = {"schema_version", "id", "name", "fixture", "request", "starting_state", "expect", "must_not", "live"}
    missing = sorted(required - set(raw))
    if missing:
        raise BehaviorError(f"scenario {path.name} is missing: {', '.join(missing)}")
    if raw["schema_version"] != SCHEMA_VERSION:
        raise BehaviorError(f"scenario {path.name} has unsupported schema_version")

    scenario_id = raw["id"]
    if not isinstance(scenario_id, str) or ID_PATTERN.fullmatch(scenario_id) is None:
        raise BehaviorError(f"scenario {path.name} has an invalid id")
    if path.stem != scenario_id:
        raise BehaviorError(f"scenario filename must match id: {path.name}")
    name = raw["name"]
    fixture = raw["fixture"]
    request = raw["request"]
    if not isinstance(name, str) or not name.strip():
        raise BehaviorError(f"scenario {path.name} needs a name")
    if not isinstance(fixture, str) or PurePosixPath(fixture).name != fixture:
        raise BehaviorError(f"scenario {path.name} has an invalid fixture")
    fixture_path = FIXTURE_ROOT / fixture
    if fixture_path.is_symlink() or not fixture_path.is_dir():
        raise BehaviorError(f"scenario {path.name} fixture does not exist: {fixture}")
    if not isinstance(request, str) or not request.strip():
        raise BehaviorError(f"scenario {path.name} needs a request")
    if not isinstance(raw["live"], bool):
        raise BehaviorError(f"scenario {path.name} live must be true or false")

    starting_state = string_list(raw["starting_state"], f"{path.name}.starting_state")
    expect = string_list(raw["expect"], f"{path.name}.expect")
    must_not = string_list(raw["must_not"], f"{path.name}.must_not", allow_empty=True)
    unknown_expect = sorted(set(expect) - EXPECTATIONS)
    unknown_prohibitions = sorted(set(must_not) - PROHIBITIONS)
    if unknown_expect:
        raise BehaviorError(f"scenario {path.name} has unknown expectations: {', '.join(unknown_expect)}")
    if unknown_prohibitions:
        raise BehaviorError(f"scenario {path.name} has unknown prohibitions: {', '.join(unknown_prohibitions)}")

    preserve_paths = tuple(
        safe_relative(item, f"{path.name}.preserve_paths")
        for item in string_list(raw.get("preserve_paths", []), f"{path.name}.preserve_paths", allow_empty=True)
    )
    for relative in preserve_paths:
        fixture_target = fixture_path.joinpath(*relative.parts)
        if not fixture_target.exists() and not fixture_target.is_symlink():
            raise BehaviorError(f"scenario {path.name} preserves a missing fixture path: {relative}")
    forbid_created_globs = string_list(
        raw.get("forbid_created_globs", []),
        f"{path.name}.forbid_created_globs",
        allow_empty=True,
    )
    for pattern in forbid_created_globs:
        if pattern.startswith(("/", "\\")) or ".." in PurePosixPath(pattern).parts:
            raise BehaviorError(f"scenario {path.name} has an unsafe glob: {pattern}")
    route_exclusions = string_list(
        raw.get("route_must_not_include", []),
        f"{path.name}.route_must_not_include",
        allow_empty=True,
    )
    state_must_include = tuple(
        safe_relative(item, f"{path.name}.state_must_include")
        for item in string_list(
            raw.get("state_must_include", []),
            f"{path.name}.state_must_include",
            allow_empty=True,
        )
    )
    state_must_not_include = tuple(
        safe_relative(item, f"{path.name}.state_must_not_include")
        for item in string_list(
            raw.get("state_must_not_include", []),
            f"{path.name}.state_must_not_include",
            allow_empty=True,
        )
    )
    for relative in state_must_include + state_must_not_include:
        fixture_target = fixture_path.joinpath(*relative.parts)
        if not fixture_target.exists() or fixture_target.is_symlink() or not fixture_target.is_file():
            raise BehaviorError(f"scenario {path.name} names a missing state input: {relative}")
    overlap = set(state_must_include) & set(state_must_not_include)
    if overlap:
        raise BehaviorError(
            f"scenario {path.name} both requires and prohibits state inputs: "
            + ", ".join(sorted(item.as_posix() for item in overlap))
        )
    report_must_include = string_list(
        raw.get("report_must_include", []),
        f"{path.name}.report_must_include",
        allow_empty=True,
    )
    verification_command = raw.get("verification_command", "")
    if not isinstance(verification_command, str):
        raise BehaviorError(f"scenario {path.name} verification_command must be a string")
    assertions = load_assertions(raw.get("assertions"), f"{path.name}.assertions")

    return Scenario(
        source=path,
        id=scenario_id,
        name=name.strip(),
        fixture=fixture,
        request=request.strip(),
        starting_state=starting_state,
        expect=expect,
        must_not=must_not,
        live=raw["live"],
        verification_command=verification_command.strip(),
        preserve_paths=preserve_paths,
        forbid_created_globs=forbid_created_globs,
        route_must_not_include=tuple(item.lower() for item in route_exclusions),
        state_must_include=state_must_include,
        state_must_not_include=state_must_not_include,
        report_must_include=report_must_include,
        assertions=assertions,
    )


def load_scenarios() -> tuple[Scenario, ...]:
    paths = sorted(SCENARIO_ROOT.glob("*.toml"))
    if not paths:
        raise BehaviorError("no behavioral scenarios found")
    scenarios = tuple(load_scenario(path) for path in paths)
    ids = [scenario.id for scenario in scenarios]
    if len(ids) != len(set(ids)):
        raise BehaviorError("behavioral scenario ids must be unique")
    return scenarios


def snapshot(root: Path) -> dict[str, Entry]:
    result: dict[str, Entry] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = Entry("symlink", os.readlink(path))
        elif path.is_file():
            result[relative] = Entry("file", hashlib.sha256(path.read_bytes()).hexdigest())
        elif path.is_dir():
            result[relative] = Entry("directory", "")
    return result


def changed_paths(before: Mapping[str, Entry], after: Mapping[str, Entry]) -> tuple[set[str], set[str], set[str]]:
    before_paths = set(before)
    after_paths = set(after)
    created = after_paths - before_paths
    deleted = before_paths - after_paths
    modified = {path for path in before_paths & after_paths if before[path] != after[path]}
    return created, modified, deleted


def meaningful_changes(evidence: RunEvidence) -> set[str]:
    created, modified, deleted = changed_paths(evidence.before, evidence.after)
    result = created | modified | deleted
    return {
        path
        for path in result
        if path not in FRAMEWORK_CHANGE_PATHS
        and not any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in FRAMEWORK_CHANGE_PREFIXES)
    }


def repository_changes(evidence: RunEvidence) -> set[str]:
    created, modified, deleted = changed_paths(evidence.before, evidence.after)
    return {
        path
        for path in created | modified | deleted
        if path != ".behavior-evidence" and not path.startswith(".behavior-evidence/")
    }


def path_matches_any(path: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def report_list(report: Mapping[str, object], key: str) -> tuple[object, ...]:
    value = report.get(key, [])
    return tuple(value) if isinstance(value, list) else ()


def observed_verification_exit_codes(evidence: RunEvidence) -> tuple[int, ...]:
    values: list[int] = []
    for item in evidence.verification:
        code = item.get("exit_code")
        if isinstance(code, int):
            values.append(code)
    return tuple(values)


def reported_verification_exit_codes(evidence: RunEvidence) -> tuple[int, ...]:
    values: list[int] = []
    for item in report_list(evidence.report, "verification"):
        if isinstance(item, dict) and isinstance(item.get("exit_code"), int):
            values.append(item["exit_code"])
    return tuple(values)


def existing_reported_paths(evidence: RunEvidence, key: str) -> tuple[str, ...]:
    result: list[str] = []
    for item in report_list(evidence.report, key):
        try:
            relative = safe_relative(item, f"report.{key}").as_posix()
        except BehaviorError:
            continue
        if relative in evidence.before:
            result.append(relative)
    return tuple(result)


def preserved(evidence: RunEvidence) -> tuple[bool, str]:
    differences = [
        relative.as_posix()
        for relative in evidence.scenario.preserve_paths
        if evidence.before.get(relative.as_posix()) != evidence.after.get(relative.as_posix())
    ]
    if differences:
        return False, "changed preserved paths: " + ", ".join(differences)
    return True, "declared project-owned paths are unchanged"


def forbidden_created(evidence: RunEvidence) -> tuple[bool, str]:
    created, _modified, _deleted = changed_paths(evidence.before, evidence.after)
    matches = sorted(path for path in created if path_matches_any(path, evidence.scenario.forbid_created_globs))
    if matches:
        return False, "created prohibited paths: " + ", ".join(matches)
    return True, "no prohibited paths were created"


def route_excluded(evidence: RunEvidence) -> tuple[bool, str]:
    excluded = set(evidence.scenario.route_must_not_include)
    matches = sorted(component for component in evidence.route_components if component.lower() in excluded)
    if matches:
        return False, "reported route contains prohibited components: " + ", ".join(matches)
    return True, "reported route does not contain prohibited components"


def route_visible(evidence: RunEvidence) -> tuple[bool, str]:
    candidates = tuple(ROUTE_CANDIDATE_PATTERN.finditer(evidence.stdout))
    valid = tuple(ROUTE_PATTERN.finditer(evidence.stdout))
    ends_response = bool(valid) and evidence.stdout.rstrip().endswith(valid[-1].group(0))
    passed = len(candidates) == 1 and len(valid) == 1 and ends_response
    return (
        passed,
        f"route candidates={len(candidates)}, valid markers={len(valid)}, ends response={ends_response}",
    )


def state_or_decision_changed(evidence: RunEvidence) -> bool:
    created, modified, _deleted = changed_paths(evidence.before, evidence.after)
    return any(
        path.startswith(".agent-workflow-state/") or path.startswith("/")
        for path in created | modified
    )


def evaluate_assertion(evidence: RunEvidence, assertion: Assertion) -> CheckResult:
    if assertion.kind in {
        "glob_any_contains",
        "glob_contains",
        "glob_count",
        "glob_none_contains",
    }:
        pattern = assertion.path.as_posix()
        matches = sorted(
            relative
            for relative, entry in evidence.after.items()
            if entry.kind == "file" and fnmatch.fnmatchcase(relative, pattern)
        )
        if assertion.kind in {
            "glob_any_contains",
            "glob_contains",
            "glob_none_contains",
        }:
            assert assertion.value is not None
            containing: list[str] = []
            unreadable: list[str] = []
            for relative in matches:
                try:
                    content = evidence.workspace.joinpath(*PurePosixPath(relative).parts).read_text(
                        encoding="utf-8"
                    )
                except (OSError, UnicodeError):
                    unreadable.append(relative)
                    continue
                if assertion.value.casefold() in content.casefold():
                    containing.append(relative)
            if assertion.kind == "glob_any_contains":
                return CheckResult(
                    f"assert:{assertion.path}:glob-any-contains",
                    bool(containing),
                    f"matched {len(matches)} files; expected text found in {containing}; "
                    f"unreadable={unreadable}",
                )
            if assertion.kind == "glob_none_contains":
                return CheckResult(
                    f"assert:{assertion.path}:glob-none-contains",
                    not containing and not unreadable,
                    f"matched {len(matches)} files; prohibited text found in {containing}; "
                    f"unreadable={unreadable}",
                )
            missing = sorted(set(matches) - set(containing))
            return CheckResult(
                f"assert:{assertion.path}:glob-contains",
                bool(matches) and not missing,
                f"matched {len(matches)} files; missing expected text in {missing}",
            )
        assert assertion.count is not None
        passed = len(matches) == assertion.count
        return CheckResult(
            f"assert:{assertion.path}:glob-count",
            passed,
            f"expected {assertion.count} matching files; found {len(matches)}: {matches}",
        )
    path = evidence.workspace.joinpath(*assertion.path.parts)
    exists = path.exists() and not path.is_symlink() and path.is_file()
    if assertion.kind == "path_exists":
        return CheckResult(f"assert:{assertion.path}:exists", exists, "path exists" if exists else "path is absent")
    if assertion.kind == "path_not_exists":
        return CheckResult(f"assert:{assertion.path}:absent", not (path.exists() or path.is_symlink()), "path is absent" if not path.exists() else "path exists")
    if not exists:
        return CheckResult(f"assert:{assertion.path}:{assertion.kind}", False, "path is not a readable regular file")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return CheckResult(f"assert:{assertion.path}:{assertion.kind}", False, f"cannot read path: {exc}")
    assert assertion.value is not None
    contains = assertion.value in text
    if assertion.kind == "path_contains":
        return CheckResult(f"assert:{assertion.path}:contains", contains, f"expected text {'found' if contains else 'missing'}")
    return CheckResult(f"assert:{assertion.path}:not-contains", not contains, f"prohibited text {'found' if contains else 'absent'}")


def evaluate(evidence: RunEvidence) -> tuple[CheckResult, ...]:
    results: list[CheckResult] = [evaluate_assertion(evidence, item) for item in evidence.scenario.assertions]
    preserved_ok, preserved_detail = preserved(evidence)
    forbidden_ok, forbidden_detail = forbidden_created(evidence)
    route_ok, route_detail = route_excluded(evidence)
    visible, visibility_detail = route_visible(evidence)
    results.append(CheckResult("route-marker:exactly-one-valid-final", visible, visibility_detail))
    status = evidence.report.get("status")
    blockers = tuple(item for item in report_list(evidence.report, "blockers") if isinstance(item, str) and item)
    providers_executed_raw = evidence.report.get("providers_executed")
    providers_executed = tuple(
        item
        for item in report_list(evidence.report, "providers_executed")
        if isinstance(item, str) and item
    )
    provider_evidence_valid = (
        isinstance(providers_executed_raw, list)
        and len(providers_executed) == len(providers_executed_raw)
    )
    state_used = existing_reported_paths(evidence, "state_used")
    required_state = {item.as_posix() for item in evidence.scenario.state_must_include}
    excluded_state = {item.as_posix() for item in evidence.scenario.state_must_not_include}
    missing_state = sorted(required_state - set(state_used))
    excessive_state = sorted(excluded_state & set(state_used))
    if required_state or excluded_state:
        results.append(
            CheckResult(
                "state-loading:progressive",
                not missing_state and not excessive_state,
                f"missing required state={missing_state}; loaded excluded state={excessive_state}",
            )
        )
    if evidence.scenario.report_must_include:
        summary = evidence.report.get("summary")
        report_text = "\n".join(
            item
            for item in (
                summary if isinstance(summary, str) else "",
                *blockers,
            )
            if item
        ).casefold()
        missing_report_details = [
            item
            for item in evidence.scenario.report_must_include
            if item.casefold() not in report_text
        ]
        results.append(
            CheckResult(
                "report-details:required",
                not missing_report_details,
                f"missing required report details={missing_report_details}",
            )
        )
    sources = tuple(item for item in report_list(evidence.report, "research_sources") if isinstance(item, str) and URL_PATTERN.match(item))
    observed_codes = observed_verification_exit_codes(evidence)
    reported_codes = reported_verification_exit_codes(evidence)
    verification_detail = f"observed exits={list(observed_codes)}, reported exits={list(reported_codes)}"
    changes = meaningful_changes(evidence)
    all_repository_changes = repository_changes(evidence)

    expected_checks: dict[str, tuple[bool, str]] = {
        "task_completed": (status == "success" and evidence.returncode == 0, f"agent status={status!r}, exit={evidence.returncode}"),
        "repository_unchanged": (
            not all_repository_changes,
            f"repository changed paths={sorted(all_repository_changes)}",
        ),
        "appropriate_validation": (bool(observed_codes) and observed_codes[-1] == 0, verification_detail),
        "external_fact_researched": (bool(sources), f"research sources={len(sources)}"),
        "uncertainty_recorded_or_blocked": (
            (status == "blocked" and bool(blockers)) or state_or_decision_changed(evidence),
            "specific blockers reported or durable uncertainty recorded",
        ),
        "existing_state_reused": (bool(state_used), f"reported state inputs={list(state_used)}"),
        "meaningful_repository_change": (bool(changes), f"meaningful changed paths={sorted(changes)}"),
        "verification_performed": (bool(observed_codes) and observed_codes[-1] == 0, verification_detail),
        "verification_failure_recovered": (
            len(observed_codes) >= 2
            and any(code != 0 for code in observed_codes[:-1])
            and observed_codes[-1] == 0,
            verification_detail,
        ),
        "blocked_cleanly": (
            status == "blocked" and bool(blockers) and not all_repository_changes,
            f"status={status!r}, blockers={len(blockers)}, repository changes={sorted(all_repository_changes)}",
        ),
        "project_state_preserved": (preserved_ok, preserved_detail),
        "unresolved_unknowns_preserved": (preserved_ok, preserved_detail),
        "lifecycle_state_preserved": (preserved_ok, preserved_detail),
    }
    for expectation in evidence.scenario.expect:
        passed, detail = expected_checks[expectation]
        results.append(CheckResult(f"expect:{expectation}", passed, detail))

    prohibition_checks: dict[str, tuple[bool, str]] = {
        "claim_unexecuted_provider": (
            provider_evidence_valid and not providers_executed,
            f"reported executed providers={list(providers_executed)}",
        ),
        "unnecessary_planning_artifacts": (forbidden_ok, forbidden_detail),
        "manufacture_uncertainty": (status != "blocked", f"agent status={status!r}"),
        "invent_external_fact": (status != "success" or bool(sources), f"research sources={len(sources)}"),
        "full_discovery_for_lookup": (route_ok and forbidden_ok, route_detail),
        "silent_decision_invention": (
            (status == "blocked" and bool(blockers)) or state_or_decision_changed(evidence),
            "specific blockers were reported or uncertainty was recorded",
        ),
        "repeat_resolved_discovery": (route_ok and forbidden_ok and preserved_ok, route_detail),
        "overwrite_project_owned_state": (preserved_ok, preserved_detail),
        "ignore_persisted_decisions": (bool(state_used), f"reported state inputs={list(state_used)}"),
        "success_after_failed_check": (
            not (status == "success" and bool(observed_codes) and observed_codes[-1] != 0),
            f"status={status!r}; {verification_detail}",
        ),
        "fabricate_project_values": (
            forbidden_ok and ((status == "blocked" and bool(blockers)) or state_or_decision_changed(evidence)),
            f"status={status!r}; {forbidden_detail}",
        ),
        "placeholder_infrastructure": (forbidden_ok, forbidden_detail),
        "invent_unknown_answers": (preserved_ok, preserved_detail),
    }
    for prohibition in evidence.scenario.must_not:
        passed, detail = prohibition_checks[prohibition]
        results.append(CheckResult(f"must-not:{prohibition}", passed, detail))
    return tuple(results)


def copy_fixture(scenario: Scenario, destination: Path) -> Path:
    source = FIXTURE_ROOT / scenario.fixture
    workspace = destination / scenario.id
    shutil.copytree(source, workspace)
    return workspace


def run_adopt(command: str, workspace: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(ADOPT), command, str(workspace)],
        text=True,
        capture_output=True,
        errors="backslashreplace",
        env=environment,
    )


def exercise_fixture_lifecycle(scenario: Scenario) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix=f"behavior-{scenario.id}-") as temporary:
        workspace = copy_fixture(scenario, Path(temporary))
        original = snapshot(workspace / ".agent-workflow-state")
        for command in ("install", "update", "update", "remove", "install"):
            result = run_adopt(command, workspace)
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip()
                return False, f"{command} failed: {detail}"
            current = snapshot(workspace / ".agent-workflow-state")
            if current != original:
                return False, f"{command} changed project-owned state"
        return True, "install/update/repeated-update/remove/reinstall preserved project state"


def build_prompt(scenario: Scenario) -> str:
    starting = "\n".join(f"- {item}" for item in scenario.starting_state)
    expected = "\n".join(f"- {item}" for item in scenario.expect)
    prohibited = "\n".join(f"- {item}" for item in scenario.must_not) or "- none beyond the project policy"
    required_state = "\n".join(f"- {item}" for item in scenario.state_must_include) or "- none"
    excluded_state = "\n".join(f"- {item}" for item in scenario.state_must_not_include) or "- none"
    required_report = "\n".join(f"- {item}" for item in scenario.report_must_include) or "- none beyond the scenario request"
    validation = scenario.verification_command or "Use the smallest validation supported by repository evidence."
    return f"""You are running an opt-in Agentic Workflow behavioral smoke test in a disposable repository.

Scenario: {scenario.name}

Starting state:
{starting}

User request:
{scenario.request}

Expected observable behavior:
{expected}

Prohibited observable behavior:
{prohibited}

State paths that must be consulted for this scenario:
{required_state}

State paths that must not be loaded for this scenario:
{excluded_state}

Details that must appear in the report summary or blockers:
{required_report}

Repository validation guidance:
{validation}

Work normally within this repository. Do not expose hidden reasoning or chain-of-thought. Before finishing, write a concise observable report to {REPORT_PATH} with this JSON shape:
{{
  "schema_version": 1,
  "status": "success | blocked | failed",
  "summary": "short outcome",
  "verification": [{{"command": "command actually run", "exit_code": 0}}],
  "research_sources": ["https://source.example/when-used"],
  "state_used": ["repository-relative state or decision path actually used"],
  "providers_selected": ["provider selected by routing, if any"],
  "providers_executed": ["provider actually invoked, if any"],
  "blockers": ["specific unresolved blocker when blocked"]
}}
Use empty arrays when a category is not applicable. This report is public test evidence, not private reasoning.
End your user-facing final response with exactly one truthful route marker.
"""


def parse_command_json(raw: str) -> tuple[str, ...]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BehaviorError(f"agent command must be a JSON string array: {exc}") from exc
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise BehaviorError("agent command must be a non-empty JSON string array")
    return tuple(value)


def substitute_command(command: Sequence[str], workspace: Path, prompt_file: Path, report_file: Path) -> list[str]:
    values = {
        "workspace": str(workspace),
        "prompt_file": str(prompt_file),
        "report_file": str(report_file),
    }
    result: list[str] = []
    for argument in command:
        try:
            result.append(argument.format(**values))
        except KeyError as exc:
            raise BehaviorError(f"unknown agent-command placeholder: {exc}") from exc
    return result


def load_report(path: Path) -> Mapping[str, object]:
    if path.is_symlink() or not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        return {}
    if value.get("status") not in {"success", "blocked", "failed"}:
        return {}
    return value


def load_verification(path: Path) -> tuple[Mapping[str, object], ...]:
    if path.is_symlink() or not path.is_file():
        return ()
    events: list[Mapping[str, object]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return ()
    for line in lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and isinstance(value.get("exit_code"), int):
            events.append(value)
    return tuple(events)


def route_components(stdout: str) -> tuple[str, ...]:
    result: list[str] = []
    for match in ROUTE_PATTERN.finditer(stdout):
        body = match.group(1)
        for component in re.split(r"\s*(?:->|→)\s*", body):
            cleaned = component.strip().lower()
            if cleaned:
                result.append(cleaned)
    return tuple(result)


def run_live_scenario(
    scenario: Scenario,
    command: Sequence[str],
    workspace_parent: Path,
    timeout_seconds: int,
) -> tuple[RunEvidence, tuple[CheckResult, ...]]:
    workspace = copy_fixture(scenario, workspace_parent)
    install = run_adopt("install", workspace)
    if install.returncode != 0:
        raise BehaviorError(f"cannot install fixture {scenario.id}: {(install.stderr or install.stdout).strip()}")
    before = snapshot(workspace)
    evidence_root = workspace / ".behavior-evidence"
    evidence_root.mkdir()
    prompt = build_prompt(scenario)
    prompt_file = evidence_root / "prompt.md"
    prompt_file.write_text(prompt, encoding="utf-8")
    report_file = workspace.joinpath(*REPORT_PATH.parts)
    actual_command = substitute_command(command, workspace, prompt_file, report_file)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run(
            actual_command,
            cwd=workspace,
            input=prompt,
            text=True,
            capture_output=True,
            errors="backslashreplace",
            env=environment,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise BehaviorError(f"live scenario {scenario.id} exceeded {timeout_seconds} seconds") from exc
    after = snapshot(workspace)
    report = load_report(report_file)
    verification = load_verification(workspace.joinpath(*VERIFICATION_LOG.parts))
    evidence = RunEvidence(
        scenario=scenario,
        workspace=workspace,
        before=before,
        after=after,
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
        report=report,
        verification=verification,
        route_components=route_components(result.stdout),
    )
    return evidence, evaluate(evidence)


def validate_command() -> int:
    scenarios = load_scenarios()
    live_count = sum(scenario.live for scenario in scenarios)
    print(f"OK: {len(scenarios)} behavioral scenarios are valid ({live_count} opt-in live).")
    return 0


def fixtures_command() -> int:
    failures = 0
    for scenario in load_scenarios():
        passed, detail = exercise_fixture_lifecycle(scenario)
        print(f"{'OK' if passed else 'ERROR'}: {scenario.id}: {detail}")
        failures += not passed
    return 1 if failures else 0


def live_command(args: argparse.Namespace) -> int:
    raw_command = args.agent_command_json or os.environ.get("AGENTIC_WORKFLOW_AGENT_COMMAND_JSON", "")
    if not raw_command:
        raise BehaviorError(
            "live runs require --agent-command-json or AGENTIC_WORKFLOW_AGENT_COMMAND_JSON"
        )
    command = parse_command_json(raw_command)
    selected = set(args.scenario or ())
    scenarios = list(load_scenarios())
    if selected:
        unknown = selected - {scenario.id for scenario in scenarios}
        if unknown:
            raise BehaviorError("unknown scenarios: " + ", ".join(sorted(unknown)))
        scenarios = [scenario for scenario in scenarios if scenario.id in selected]
    else:
        scenarios = [scenario for scenario in scenarios if scenario.live]
    if not scenarios:
        raise BehaviorError("no live scenarios selected")

    output_runs: list[dict[str, object]] = []
    failures = 0
    if args.keep_workspaces:
        args.keep_workspaces.mkdir(parents=True, exist_ok=True)
        workspace_context = None
        workspace_parent = Path(
            tempfile.mkdtemp(prefix="agentic-workflow-live-", dir=args.keep_workspaces)
        )
    else:
        workspace_context = tempfile.TemporaryDirectory(prefix="agentic-workflow-live-")
        workspace_parent = Path(workspace_context.name)
    try:
        for scenario in scenarios:
            evidence, results = run_live_scenario(scenario, command, workspace_parent, args.timeout_seconds)
            failed = [result for result in results if not result.passed]
            failures += bool(failed)
            print(f"{'PASS' if not failed else 'FAIL'}: {scenario.id}")
            for result in results:
                print(f"  {'OK' if result.passed else 'ERROR'}: {result.name}: {result.detail}")
            created, modified, deleted = changed_paths(evidence.before, evidence.after)
            output_runs.append(
                {
                    "scenario": scenario.id,
                    "passed": not failed,
                    "workspace": str(evidence.workspace),
                    "agent_exit_code": evidence.returncode,
                    "created": sorted(created),
                    "modified": sorted(modified),
                    "deleted": sorted(deleted),
                    "route_components": list(evidence.route_components),
                    "checks": [result.__dict__ for result in results],
                    "report": dict(evidence.report),
                }
            )
    finally:
        if workspace_context is not None:
            workspace_context.cleanup()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"schema_version": 1, "runs": output_runs}, indent=2) + "\n", encoding="utf-8")
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="validate scenario and fixture contracts")
    subparsers.add_parser("fixtures", help="exercise lifecycle safety against every fixture")
    live = subparsers.add_parser("live", help="run the opt-in live agent scenarios")
    live.add_argument("--agent-command-json")
    live.add_argument("--scenario", action="append")
    live.add_argument("--timeout-seconds", type=int, default=600)
    live.add_argument("--keep-workspaces", type=Path)
    live.add_argument("--output", type=Path)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    configure_console()
    if sys.version_info < MINIMUM_PYTHON:
        print("ERROR: behavioral tests require Python 3.11 or newer", file=sys.stderr)
        return 2
    try:
        args = build_parser().parse_args(argv)
        if args.command == "validate":
            return validate_command()
        if args.command == "fixtures":
            return fixtures_command()
        return live_command(args)
    except BehaviorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
