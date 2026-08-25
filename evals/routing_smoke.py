#!/usr/bin/env python3
"""Run a two-case, progressively loaded routing-interpretation smoke test."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable, Iterable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SMOKE_ROOT = Path(__file__).resolve().parent / "routing-smoke"
CASES_PATH = SMOKE_ROOT / "cases.json"
DEFAULT_MAX_ROUNDS = 4
DEFAULT_MAX_PROMPT_BYTES = 120_000
HARD_MAX_COST_USD = 2.0
CLAUDE_MAX_CALL_USD = 0.20

RESOURCE_PATHS = {
    ".agent-workflow/routing.md": REPOSITORY_ROOT / ".agent-workflow/routing.md",
    ".agent-workflow/providers.json": REPOSITORY_ROOT
    / ".agent-workflow/providers.json",
    ".agents/skills/wayfinder/SKILL.md": REPOSITORY_ROOT
    / ".agents/skills/wayfinder/SKILL.md",
    ".agent-workflow/contracts/wayfinder-state.md": REPOSITORY_ROOT
    / ".agent-workflow/contracts/wayfinder-state.md",
}

ROUTES = ["direct", "discovery", "debugging", "wayfinder", "other"]
PROVIDER_OUTCOMES = [
    "not_checked",
    "direct",
    "available",
    "unavailable",
    "host_native_fallback",
]

DECISION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["request_resources", "complete"]},
        "requested_resources": {
            "type": "array",
            "items": {"type": "string"},
        },
        "initial_route": {"type": "string", "enum": ROUTES},
        "current_route": {"type": "string", "enum": ROUTES},
        "wayfinder_assessment": {"type": "boolean"},
        "wayfinder_selected": {"type": "boolean"},
        "provider_outcome": {"type": "string", "enum": PROVIDER_OUTCOMES},
        "summary": {"type": "string"},
    },
    "required": [
        "status",
        "requested_resources",
        "initial_route",
        "current_route",
        "wayfinder_assessment",
        "wayfinder_selected",
        "provider_outcome",
        "summary",
    ],
    "additionalProperties": False,
}

Invoke = Callable[[str], tuple[Mapping[str, Any], Mapping[str, Any]]]


class SmokeError(RuntimeError):
    """Raised for an invalid smoke-test contract or adapter result."""


@dataclass
class CostBudget:
    max_usd: float
    input_per_million: float
    cached_input_per_million: float
    output_per_million: float
    spent_usd: float = 0.0

    def add(self, usage: Mapping[str, Any]) -> float:
        input_tokens = int(usage.get("input_tokens", 0) or 0)
        if "cached_input_tokens" in usage:
            cached_tokens = int(usage.get("cached_input_tokens", 0) or 0)
            uncached_tokens = max(input_tokens - cached_tokens, 0)
        else:
            cached_tokens = int(usage.get("cache_read_input_tokens", 0) or 0)
            uncached_tokens = input_tokens + int(
                usage.get("cache_creation_input_tokens", 0) or 0
            )
        output_tokens = int(usage.get("output_tokens", 0) or 0)
        cost = (
            uncached_tokens * self.input_per_million
            + cached_tokens * self.cached_input_per_million
            + output_tokens * self.output_per_million
        ) / 1_000_000
        self.spent_usd += cost
        if self.spent_usd >= self.max_usd:
            raise SmokeError(
                f"estimated model cost ${self.spent_usd:.4f} reached the ${self.max_usd:.2f} limit"
            )
        return cost


def load_cases(path: Path = CASES_PATH) -> dict[str, dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != 1 or not isinstance(raw.get("cases"), list):
        raise SmokeError("routing smoke cases must use schema_version 1")
    cases: dict[str, dict[str, Any]] = {}
    for item in raw["cases"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise SmokeError("every routing smoke case must have a string id")
        if item["id"] in cases:
            raise SmokeError(f"duplicate routing smoke case: {item['id']}")
        cases[item["id"]] = item
    return cases


def resource_path(case: Mapping[str, Any], name: str) -> Path:
    fixture = SMOKE_ROOT / "fixtures" / str(case["id"]) / name
    if fixture.is_file():
        return fixture
    try:
        return RESOURCE_PATHS[name]
    except KeyError as exc:
        raise SmokeError(f"no source is declared for resource {name!r}") from exc


def resource_catalog(case: Mapping[str, Any]) -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []
    for name in case["available_resources"]:
        path = resource_path(case, name)
        content = path.read_text(encoding="utf-8")
        catalog.append({"name": name, "bytes": len(content.encode("utf-8"))})
    return catalog


def build_prompt(
    case: Mapping[str, Any],
    *,
    host: str,
    loaded: Mapping[str, str],
    decisions: Sequence[Mapping[str, Any]],
) -> str:
    root_policy = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    available = json.dumps(resource_catalog(case), indent=2)
    loaded_text = (
        "\n\n".join(
            f"<resource name={json.dumps(name)}>\n{content}\n</resource>"
            for name, content in loaded.items()
        )
        or "(none)"
    )
    history = json.dumps(list(decisions), indent=2)
    return f"""Evaluate how an agent on host {host!r} interprets the repository routing policy.

This is a public behavioral decision, not a request for hidden reasoning. Do not use tools,
access a filesystem, or invent resource contents. Request only named resources that the policy
says are now relevant. Multiple resources may be requested together. Once enough evidence is
loaded, return status=\"complete\". Keep initial_route as the route justified before any requested
resource was revealed; current_route may change as evidence accumulates. current_route records
the router's conceptual selection before host/provider compatibility is applied. Record an
unavailable provider or host-native fallback separately in provider_outcome.
After selecting a provider-backed skill, MUST request provider metadata before completing
unless it is already loaded; use that metadata to report provider_outcome truthfully.

<always_loaded_policy>
{root_policy}
</always_loaded_policy>

User request:
{case["request"]}

Available resources (names and sizes only):
{available}

Resources loaded by prior requests:
{loaded_text}

Prior public decisions:
{history}

Return only the JSON object required by the supplied output schema. The summary must be a concise,
falsifiable explanation using policy signals, not chain-of-thought.
"""


def validate_decision(decision: Mapping[str, Any]) -> None:
    required = set(DECISION_SCHEMA["required"])
    if set(decision) != required:
        raise SmokeError(
            f"adapter decision fields differ from schema: {sorted(decision)}"
        )
    if decision["status"] not in {"request_resources", "complete"}:
        raise SmokeError("adapter returned an invalid status")
    requested = decision["requested_resources"]
    if not isinstance(requested, list) or any(
        not isinstance(item, str) for item in requested
    ):
        raise SmokeError("requested_resources must be a string array")
    if len(requested) != len(set(requested)):
        raise SmokeError("requested_resources must not contain duplicates")
    if decision["status"] == "request_resources" and not requested:
        raise SmokeError("request_resources status requires at least one resource")
    if decision["status"] == "complete" and requested:
        raise SmokeError("complete status cannot request resources")
    if (
        decision["initial_route"] not in ROUTES
        or decision["current_route"] not in ROUTES
    ):
        raise SmokeError("adapter returned an invalid route")
    if decision["provider_outcome"] not in PROVIDER_OUTCOMES:
        raise SmokeError("adapter returned an invalid provider outcome")
    if not isinstance(decision["wayfinder_assessment"], bool) or not isinstance(
        decision["wayfinder_selected"], bool
    ):
        raise SmokeError("Wayfinder fields must be booleans")
    if not isinstance(decision["summary"], str) or not decision["summary"].strip():
        raise SmokeError("summary must be a non-empty string")


def evaluate_case(
    case: Mapping[str, Any],
    loaded_names: Sequence[str],
    decisions: Sequence[Mapping[str, Any]],
    *,
    host: str,
) -> list[dict[str, Any]]:
    final = decisions[-1] if decisions else {}
    first = decisions[0] if decisions else {}
    first_requested = first.get("requested_resources", [])
    if case["id"] == "direct":
        expected_provider_outcomes = {"direct", "not_checked"}
    elif host == "claude":
        expected_provider_outcomes = {"unavailable", "host_native_fallback"}
    else:
        expected_provider_outcomes = {"available"}
    checks = [
        {
            "name": "completed",
            "passed": final.get("status") == "complete",
            "detail": f"final status={final.get('status')!r}",
        },
        {
            "name": "initial-route",
            "passed": final.get("initial_route") == case["expected_initial_route"],
            "detail": f"expected={case['expected_initial_route']!r}, actual={final.get('initial_route')!r}",
        },
        {
            "name": "final-route",
            "passed": final.get("current_route") == case["expected_final_route"],
            "detail": f"expected={case['expected_final_route']!r}, actual={final.get('current_route')!r}",
        },
        {
            "name": "wayfinder-selection",
            "passed": final.get("wayfinder_selected")
            is case["expected_wayfinder_selected"],
            "detail": f"expected={case['expected_wayfinder_selected']!r}, actual={final.get('wayfinder_selected')!r}",
        },
        {
            "name": "required-resources",
            "passed": all(name in loaded_names for name in case["required_resources"]),
            "detail": f"required={case['required_resources']!r}, loaded={list(loaded_names)!r}",
        },
        {
            "name": "forbidden-resources",
            "passed": not any(
                name in loaded_names for name in case["forbidden_resources"]
            ),
            "detail": f"forbidden={case['forbidden_resources']!r}, loaded={list(loaded_names)!r}",
        },
        {
            "name": "first-resources",
            "passed": first_requested == case["expected_first_resources"],
            "detail": f"expected={case['expected_first_resources']!r}, actual={first_requested!r}",
        },
        {
            "name": "provider-outcome",
            "passed": final.get("provider_outcome") in expected_provider_outcomes,
            "detail": f"expected one of={sorted(expected_provider_outcomes)!r}, actual={final.get('provider_outcome')!r}",
        },
    ]
    if case["id"] == "evolving":
        checks.append(
            {
                "name": "direct-to-wayfinder-transition",
                "passed": (
                    first.get("current_route") == "direct"
                    and first.get("wayfinder_selected") is False
                    and final.get("current_route") == "wayfinder"
                    and final.get("wayfinder_selected") is True
                ),
                "detail": (
                    f"first route={first.get('current_route')!r}, "
                    f"first Wayfinder={first.get('wayfinder_selected')!r}, "
                    f"final route={final.get('current_route')!r}, "
                    f"final Wayfinder={final.get('wayfinder_selected')!r}"
                ),
            }
        )
    return checks


def run_case(
    case: Mapping[str, Any],
    *,
    host: str,
    model: str,
    invoke: Invoke,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    max_prompt_bytes: int = DEFAULT_MAX_PROMPT_BYTES,
    cost_budget: CostBudget | None = None,
) -> dict[str, Any]:
    loaded: dict[str, str] = {}
    decisions: list[Mapping[str, Any]] = []
    rounds: list[dict[str, Any]] = []
    total_prompt_bytes = 0
    total_prompt_words = 0
    usage_totals: dict[str, int] = {}
    estimated_cost_usd = 0.0

    for number in range(1, max_rounds + 1):
        prompt = build_prompt(case, host=host, loaded=loaded, decisions=decisions)
        prompt_bytes = len(prompt.encode("utf-8"))
        if total_prompt_bytes + prompt_bytes > max_prompt_bytes:
            raise SmokeError(
                f"case {case['id']} would exceed the {max_prompt_bytes}-byte prompt budget"
            )
        decision, usage = invoke(prompt)
        validate_decision(decision)
        total_prompt_bytes += prompt_bytes
        total_prompt_words += len(prompt.split())
        for key, value in usage.items():
            if isinstance(value, int) and not isinstance(value, bool):
                usage_totals[key] = usage_totals.get(key, 0) + value
        if cost_budget is not None:
            estimated_cost_usd += cost_budget.add(usage)
        rounds.append(
            {
                "round": number,
                "prompt_bytes": prompt_bytes,
                "prompt_words": len(prompt.split()),
                "decision": dict(decision),
                "usage": dict(usage),
            }
        )
        decisions.append(dict(decision))
        if decision["status"] == "complete":
            break
        for name in decision["requested_resources"]:
            if name not in case["available_resources"]:
                raise SmokeError(f"adapter requested unavailable resource {name!r}")
            if name in loaded:
                raise SmokeError(f"adapter requested already loaded resource {name!r}")
            loaded[name] = resource_path(case, name).read_text(encoding="utf-8")

    checks = evaluate_case(case, list(loaded), decisions, host=host)
    return {
        "schema_version": 1,
        "case": case["id"],
        "host": host,
        "model": model,
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
        "resources_loaded": list(loaded),
        "rounds": rounds,
        "final_decision": dict(decisions[-1]) if decisions else None,
        "transmission": {
            "prompt_bytes": total_prompt_bytes,
            "prompt_words": total_prompt_words,
            "model_usage": usage_totals,
            "estimated_cost_usd": round(estimated_cost_usd, 6) if cost_budget else None,
        },
    }


def parse_json_object(raw: str, *, label: str) -> Mapping[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SmokeError(f"{label} did not return valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SmokeError(f"{label} must return one JSON object")
    return value


def codex_usage(jsonl: str) -> dict[str, int]:
    usage: dict[str, int] = {}
    for line in jsonl.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "turn.completed" or not isinstance(
            event.get("usage"), dict
        ):
            continue
        for key, value in event["usage"].items():
            if isinstance(value, int) and not isinstance(value, bool):
                usage[key] = value
    return usage


def executable_path(explicit: str | None, default: str) -> str:
    if explicit:
        candidate = Path(explicit).expanduser()
        if candidate.is_file():
            return str(candidate.resolve())
        resolved = shutil.which(explicit)
        if resolved:
            return resolved
        raise SmokeError(f"adapter executable is unavailable: {explicit}")
    resolved = shutil.which(default)
    if resolved:
        return resolved
    if default == "codex":
        bundled = Path("/Applications/ChatGPT.app/Contents/Resources/codex")
        if bundled.is_file():
            return str(bundled)
    raise SmokeError(f"adapter executable is unavailable: {default}")


def codex_invoke(*, model: str, executable: str | None, timeout_seconds: int) -> Invoke:
    binary = executable_path(executable, "codex")

    def invoke(prompt: str) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
        with tempfile.TemporaryDirectory(prefix="routing-smoke-codex-") as temporary:
            root = Path(temporary)
            source_home = Path(
                os.environ.get("CODEX_HOME", Path.home() / ".codex")
            ).expanduser()
            source_auth = source_home / "auth.json"
            if not source_auth.is_file() or source_auth.is_symlink():
                raise SmokeError(
                    "Codex adapter requires a regular CODEX_HOME/auth.json"
                )
            isolated_home = root / "codex-home"
            isolated_home.mkdir(mode=0o700)
            isolated_auth = isolated_home / "auth.json"
            shutil.copyfile(source_auth, isolated_auth)
            isolated_auth.chmod(0o600)
            schema = root / "decision-schema.json"
            output = root / "decision.json"
            schema.write_text(json.dumps(DECISION_SCHEMA), encoding="utf-8")
            command = [
                binary,
                "exec",
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "-m",
                model,
                "-c",
                'model_reasoning_effort="low"',
                "-c",
                'approval_policy="never"',
                "-c",
                'shell_environment_policy.inherit="none"',
                "-s",
                "read-only",
                "-C",
                str(root),
                "--skip-git-repo-check",
                "--output-schema",
                str(schema),
                "--output-last-message",
                str(output),
                "--json",
                "-",
            ]
            try:
                environment = {"CODEX_HOME": str(isolated_home)}
                for key in ("PATH", "TMPDIR", "LANG", "LC_ALL", "TERM"):
                    if os.environ.get(key):
                        environment[key] = os.environ[key]
                result = subprocess.run(
                    command,
                    input=prompt,
                    text=True,
                    capture_output=True,
                    errors="backslashreplace",
                    timeout=timeout_seconds,
                    env=environment,
                )
            except subprocess.TimeoutExpired as exc:
                raise SmokeError(
                    f"Codex adapter exceeded {timeout_seconds} seconds"
                ) from exc
            if result.returncode != 0:
                detail = "\n".join(
                    part
                    for part in (result.stdout.strip(), result.stderr.strip())
                    if part
                )
                raise SmokeError(
                    f"Codex adapter failed with exit {result.returncode}: {detail[-2000:]}"
                )
            if not output.is_file():
                raise SmokeError("Codex adapter did not create its structured output")
            decision = parse_json_object(
                output.read_text(encoding="utf-8"), label="Codex adapter"
            )
            return decision, codex_usage(result.stdout)

    return invoke


def claude_invoke(
    *, model: str, executable: str | None, timeout_seconds: int
) -> Invoke:
    binary = executable_path(executable, "claude")
    schema = json.dumps(DECISION_SCHEMA, separators=(",", ":"))

    def invoke(prompt: str) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
        with tempfile.TemporaryDirectory(prefix="routing-smoke-claude-") as temporary:
            command = [
                binary,
                "-p",
                "--safe-mode",
                "--no-session-persistence",
                "--no-chrome",
                "--max-turns",
                "1",
                "--max-budget-usd",
                str(CLAUDE_MAX_CALL_USD),
                "--output-format",
                "json",
                "--json-schema",
                schema,
                "--model",
                model,
                "--permission-mode",
                "plan",
            ]
            try:
                environment: dict[str, str] = {}
                for key in ("HOME", "PATH", "TMPDIR", "LANG", "LC_ALL", "TERM"):
                    if os.environ.get(key):
                        environment[key] = os.environ[key]
                result = subprocess.run(
                    command,
                    cwd=temporary,
                    input=prompt,
                    text=True,
                    capture_output=True,
                    errors="backslashreplace",
                    timeout=timeout_seconds,
                    env=environment,
                )
            except subprocess.TimeoutExpired as exc:
                raise SmokeError(
                    f"Claude adapter exceeded {timeout_seconds} seconds"
                ) from exc
            if result.returncode != 0:
                detail = result.stderr.strip() or result.stdout.strip()
                raise SmokeError(
                    f"Claude adapter failed with exit {result.returncode}: {detail[-2000:]}"
                )
            envelope = parse_json_object(result.stdout, label="Claude adapter")
            decision = envelope.get("structured_output")
            if not isinstance(decision, dict):
                raise SmokeError("Claude adapter response lacks structured_output")
            usage = (
                envelope.get("usage") if isinstance(envelope.get("usage"), dict) else {}
            )
            return decision, usage

    return invoke


def compare_reports(reports: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if len(reports) < 2:
        raise SmokeError("comparison requires at least two reports")
    by_case: dict[str, list[dict[str, Any]]] = {}
    expected_cases = set(load_cases())
    report_case_sets: list[set[str]] = []
    for report in reports:
        raw_cases = report.get("cases")
        if not isinstance(raw_cases, list):
            raise SmokeError("every comparison report must contain a cases array")
        report_case_sets.append(
            {str(case.get("case")) for case in raw_cases if isinstance(case, dict)}
        )
        for case in raw_cases:
            if not isinstance(case, dict):
                raise SmokeError("comparison case entries must be objects")
            decision = case.get("final_decision") or {}
            if not isinstance(decision, dict):
                raise SmokeError("comparison final_decision must be an object")
            by_case.setdefault(str(case.get("case")), []).append(
                {
                    "model": report.get("model"),
                    "host": report.get("host"),
                    "passed": case.get("passed"),
                    "initial_route": decision.get("initial_route"),
                    "current_route": decision.get("current_route"),
                    "provider_outcome": decision.get("provider_outcome"),
                }
            )
    complete_case_matrix = all(
        case_set == expected_cases for case_set in report_case_sets
    )
    interpretation_agreement = complete_case_matrix
    provider_outcome_agreement = complete_case_matrix
    for entries in by_case.values():
        interpretation_signatures = {
            (entry["passed"], entry["initial_route"], entry["current_route"])
            for entry in entries
        }
        provider_outcomes = {entry["provider_outcome"] for entry in entries}
        interpretation_agreement &= (
            len(entries) == len(reports)
            and all(entry["passed"] is True for entry in entries)
            and len(interpretation_signatures) == 1
        )
        provider_outcome_agreement &= (
            len(entries) == len(reports) and len(provider_outcomes) == 1
        )
    return {
        "schema_version": 1,
        "report_count": len(reports),
        "expected_cases": sorted(expected_cases),
        "complete_case_matrix": complete_case_matrix,
        "interpretation_agreement": interpretation_agreement,
        "provider_outcome_agreement": provider_outcome_agreement,
        "cases": by_case,
    }


def validated_output_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if resolved == REPOSITORY_ROOT or resolved.is_relative_to(REPOSITORY_ROOT):
        raise SmokeError("routing smoke reports must be written outside the repository")
    return resolved


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    resolved = validated_output_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run_command(args: argparse.Namespace) -> int:
    if args.output:
        validated_output_path(args.output)
    cases = load_cases()
    selected = args.case or list(cases)
    unknown = set(selected) - set(cases)
    if unknown:
        raise SmokeError("unknown cases: " + ", ".join(sorted(unknown)))
    if args.max_rounds < 1 or args.max_rounds > DEFAULT_MAX_ROUNDS:
        raise SmokeError(f"max rounds must be between 1 and {DEFAULT_MAX_ROUNDS}")
    if args.max_prompt_bytes < 1 or args.max_prompt_bytes > DEFAULT_MAX_PROMPT_BYTES:
        raise SmokeError(f"max prompt bytes cannot exceed {DEFAULT_MAX_PROMPT_BYTES}")
    if (
        args.max_estimated_cost_usd <= 0
        or args.max_estimated_cost_usd > HARD_MAX_COST_USD
    ):
        raise SmokeError(
            f"estimated cost limit must be greater than zero and at most ${HARD_MAX_COST_USD:.2f}"
        )
    if (
        min(
            args.input_price_per_million,
            args.cached_input_price_per_million,
            args.output_price_per_million,
        )
        < 0
    ):
        raise SmokeError("token prices must be non-negative")
    host = "claude" if args.adapter == "claude" else "codex"
    if args.adapter == "codex":
        invoke = codex_invoke(
            model=args.model,
            executable=args.executable,
            timeout_seconds=args.timeout_seconds,
        )
    elif args.adapter == "claude":
        invoke = claude_invoke(
            model=args.model,
            executable=args.executable,
            timeout_seconds=args.timeout_seconds,
        )
    cost_budget = CostBudget(
        max_usd=args.max_estimated_cost_usd,
        input_per_million=args.input_price_per_million,
        cached_input_per_million=args.cached_input_price_per_million,
        output_per_million=args.output_price_per_million,
    )
    results = [
        run_case(
            cases[case_id],
            host=host,
            model=args.model,
            invoke=invoke,
            max_rounds=args.max_rounds,
            max_prompt_bytes=args.max_prompt_bytes,
            cost_budget=cost_budget,
        )
        for case_id in selected
    ]
    report = {
        "schema_version": 1,
        "adapter": args.adapter,
        "host": host,
        "model": args.model,
        "passed": all(case["passed"] for case in results),
        "estimated_cost_usd": round(cost_budget.spent_usd, 6),
        "cases": results,
    }
    if args.output:
        write_json(args.output, report)
    else:
        print(json.dumps(report, indent=2))
    for case in results:
        print(
            f"{'PASS' if case['passed'] else 'FAIL'}: {case['case']} "
            f"({case['transmission']['prompt_bytes']} prompt bytes)",
            file=sys.stderr,
        )
    return 0 if report["passed"] else 1


def compare_command(args: argparse.Namespace) -> int:
    reports = [
        parse_json_object(path.read_text(encoding="utf-8"), label=str(path))
        for path in args.reports
    ]
    comparison = compare_reports(reports)
    if args.output:
        write_json(args.output, comparison)
    else:
        print(json.dumps(comparison, indent=2))
    return 0 if comparison["interpretation_agreement"] else 1


def payload_command(_args: argparse.Namespace) -> int:
    root = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    payload = {
        "always_loaded": {
            "name": "AGENTS.md",
            "bytes": len(root.encode("utf-8")),
            "words": len(root.split()),
        },
        "cases": {
            case_id: resource_catalog(case) for case_id, case in load_cases().items()
        },
        "limits": {
            "max_rounds": DEFAULT_MAX_ROUNDS,
            "max_prompt_bytes_per_case": DEFAULT_MAX_PROMPT_BYTES,
        },
    }
    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser(
        "run", help="run the two routing cases through one model adapter"
    )
    run.add_argument("--adapter", choices=("codex", "claude"), required=True)
    run.add_argument("--model", required=True)
    run.add_argument("--executable")
    run.add_argument("--case", action="append")
    run.add_argument("--max-rounds", type=int, default=DEFAULT_MAX_ROUNDS)
    run.add_argument("--max-prompt-bytes", type=int, default=DEFAULT_MAX_PROMPT_BYTES)
    run.add_argument("--timeout-seconds", type=int, default=180)
    run.add_argument("--max-estimated-cost-usd", type=float, required=True)
    run.add_argument("--input-price-per-million", type=float, required=True)
    run.add_argument("--cached-input-price-per-million", type=float, required=True)
    run.add_argument("--output-price-per-million", type=float, required=True)
    run.add_argument("--output", type=Path)
    compare = subparsers.add_parser(
        "compare", help="compare two or more completed model reports"
    )
    compare.add_argument("reports", nargs="+", type=Path)
    compare.add_argument("--output", type=Path)
    subparsers.add_parser(
        "payload", help="show the exact local payload sizes without contacting a model"
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        if args.command == "run":
            return run_command(args)
        if args.command == "compare":
            return compare_command(args)
        return payload_command(args)
    except (OSError, UnicodeError, json.JSONDecodeError, SmokeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
