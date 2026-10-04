"""Validate the small, versioned campaign input format before any execution."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path, PurePosixPath
import re


IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
CHECK_KINDS = {
    "semantic",
    "unchanged",
    "path_exists",
    "path_absent",
    "file_equals",
    "command_observed",
    "compaction_observed",
    "context_observed",
}
EXECUTION_STATUSES = {"completed", "infrastructure-blocked", "timeout", "error"}
VERDICTS = {"PASS", "FAIL", "INCONCLUSIVE"}


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def identifier(value, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError(f"Invalid {label}: {value!r}")
    return value


def text(value, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"A nonempty {label} is required")
    return value


def relative(value, label: str, *, glob=False) -> str:
    text(value, label)
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or "\\" in value
        or value in {".", ""}
        or ":" in value
        or (not glob and any(char in value for char in "*?[]"))
    ):
        raise ValueError(f"Unsafe {label}: {value!r}")
    return value


def integer(value, label: str, low=1, high=10000) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{label} must be an integer in [{low}, {high}]")
    return value


def validate_scenario(data: dict) -> dict:
    if data.get("schema") != 1:
        raise ValueError("Unsupported scenario schema")
    identifier(data.get("id"), "scenario id")
    text(data.get("title"), "scenario title")
    text(data.get("question"), "scenario question")
    text(data.get("fixture"), "fixture")
    if data.get("applicability") not in {"common-outcome", "current-contract"}:
        raise ValueError(
            "Scenario applicability must distinguish outcome from conformance"
        )
    turns = data.get("turns")
    if not isinstance(turns, list) or not turns:
        raise ValueError("A scenario needs at least one turn")
    ids = set()
    for turn in turns:
        key = identifier(turn.get("id"), "turn id")
        if key in ids:
            raise ValueError(f"Duplicate turn id: {key}")
        ids.add(key)
        identifier(turn.get("session"), "session label")
        text(turn.get("request"), "public request")
        allowed = turn.get("allowed_writes")
        if not isinstance(allowed, list):
            raise ValueError(
                "Every turn must declare allowed_writes; [] means no writes"
            )
        for pattern in allowed:
            relative(pattern, "allowed write pattern", glob=True)
        preserves = turn.get("preserve_paths", [])
        if not isinstance(preserves, list):
            raise ValueError("preserve_paths must be a list")
        for pattern in preserves:
            relative(pattern, "preserved path", glob=True)
        transition = turn.get("before_turn", {})
        if not isinstance(transition, dict) or set(transition) - {"create", "delete"}:
            raise ValueError("before_turn accepts only create and delete")
        creates, deletes = transition.get("create", {}), transition.get("delete", [])
        if not isinstance(creates, dict) or not isinstance(deletes, list):
            raise ValueError("before_turn requires a create object and delete list")
        if set(creates) & set(deletes) or len(set(deletes)) != len(deletes):
            raise ValueError("Conflicting or duplicate transition paths")
        for path in [*creates, *deletes]:
            relative(path, "transition path")
            if not path.startswith("docs/"):
                raise ValueError("Transitions may change only supplied docs")
        for value in creates.values():
            text(value, "transition content")
        checks = turn.get("checks")
        if not isinstance(checks, list) or not checks:
            raise ValueError("Every turn needs an observable check")
        check_ids = set()
        for check in checks:
            name = identifier(check.get("id"), "check id")
            if name in check_ids or name.startswith("boundary-"):
                raise ValueError(f"Duplicate or reserved check id: {name}")
            check_ids.add(name)
            kind = check.get("kind")
            if kind not in CHECK_KINDS:
                raise ValueError(f"Unsupported check kind: {kind}")
            if kind == "semantic":
                text(check.get("requirement"), "semantic requirement")
                if check.get("evidence_scope", "any") not in {
                    "saved",
                    "response",
                    "any",
                }:
                    raise ValueError(
                        "Semantic evidence_scope must be saved, response, or any"
                    )
            if kind in {"path_exists", "path_absent", "file_equals"}:
                relative(check.get("path"), "check path")
            if kind == "file_equals" and not isinstance(check.get("value"), str):
                raise ValueError("file_equals requires a string value")
            if kind == "command_observed":
                text(check.get("argv_contains"), "command observation")
            if kind == "context_observed":
                integer(
                    check.get("minimum_tokens"),
                    "minimum active context tokens",
                    high=2_000_000,
                )
    return data


def load_spec(path: Path) -> tuple[dict, list[tuple[dict, Path]]]:
    path = path.resolve()
    spec = read_json(path)
    if spec.get("schema") != 1:
        raise ValueError("Unsupported campaign schema")
    identifier(spec.get("name"), "campaign name")
    text(spec.get("question"), "campaign question")
    integer(spec.get("repetitions"), "repetitions", high=100)
    integer(spec.get("seed"), "seed", low=0, high=2**32 - 1)
    limits = spec.get("limits", {})
    integer(limits.get("max_turns"), "max_turns")
    integer(limits.get("turn_seconds"), "turn_seconds", high=3600)
    integer(limits.get("campaign_seconds"), "campaign_seconds", high=86400)
    deadline = limits.get("launch_before_utc")
    if deadline is not None:
        parsed = datetime.fromisoformat(text(deadline, "launch deadline"))
        if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
            raise ValueError("launch_before_utc must specify UTC")
    host = spec.get("host", {})
    if host.get("kind") not in {"manual", "command"}:
        raise ValueError("Host kind must be manual or command")
    text(
        host.get("model"), "requested model (use 'unavailable' when the host hides it)"
    )
    text(host.get("reasoning_effort"), "requested reasoning effort")
    if host["kind"] == "command":
        command = host.get("command")
        if not isinstance(command, list) or not command:
            raise ValueError("Command host requires a nonempty argv array")
        for part in command:
            text(part, "argv element")
    if not isinstance(host.get("settings", {}), dict):
        raise ValueError("Host settings must be an object")
    conditions = spec.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        raise ValueError("A campaign needs at least one condition")
    seen = set()
    for condition in conditions:
        key = identifier(condition.get("id"), "condition id")
        if key in seen:
            raise ValueError(f"Duplicate condition: {key}")
        seen.add(key)
        text(condition.get("ref"), "product ref")
        overlays = condition.get("overlays", [])
        if not isinstance(overlays, list):
            raise ValueError("overlays must be a list")
        for overlay in overlays:
            identifier(overlay.get("skill"), "overlay skill")
            text(overlay.get("ref"), "overlay donor ref")
    scenario_paths = spec.get("scenarios")
    if not isinstance(scenario_paths, list) or not scenario_paths:
        raise ValueError("A campaign needs scenario paths")
    scenarios = []
    seen = set()
    for source in scenario_paths:
        scenario_path = (path.parent / text(source, "scenario path")).resolve()
        scenario = validate_scenario(read_json(scenario_path))
        if scenario["id"] in seen:
            raise ValueError("Duplicate scenario id")
        seen.add(scenario["id"])
        fixture = (scenario_path.parent / scenario["fixture"]).resolve()
        if not fixture.is_dir():
            raise ValueError(f"Fixture directory not found: {fixture}")
        scenarios.append((scenario, fixture))
    expected = (
        len(conditions)
        * spec["repetitions"]
        * sum(len(s[0]["turns"]) for s in scenarios)
    )
    if expected > limits["max_turns"]:
        raise ValueError(f"Schedule needs {expected} turns, exceeding max_turns")
    return spec, scenarios


def validate_response(response: dict) -> dict:
    if response.get("schema") != 1:
        raise ValueError("Unsupported adapter response schema")
    if response.get("execution_status") not in EXECUTION_STATUSES:
        raise ValueError("Unsupported execution_status")
    if not isinstance(response.get("response"), str):
        raise ValueError("Adapter response text is required, even when empty")
    session = response.get("session_id")
    if session is not None and (not isinstance(session, str) or not session.strip()):
        raise ValueError("Invalid session_id")
    if response["execution_status"] == "completed" and not response["response"].strip():
        raise ValueError("A completed turn needs a final response")
    if not isinstance(response.get("observations", {}), dict):
        raise ValueError("observations must be an object")
    if not isinstance(response.get("traces", []), list):
        raise ValueError("traces must be a list")
    return response
