#!/usr/bin/env python3
"""Micro-test how instruction wording changes a model's plan, against a control."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Mapping, Sequence

from evals import routing_smoke as smoke


MICRO_ROOT = Path(__file__).resolve().parent / "wording-micro"
CASES_ROOT = MICRO_ROOT / "cases"
SKILLS_ROOT = smoke.REPOSITORY_ROOT / ".agents" / "skills"
MIN_REPS = 5
MAX_ROUNDS = 3
HARD_MAX_COST_USD = 5.0
PREDICATE_KINDS = {"resource_requested", "answer_equals", "answer_list_contains"}


def load_case(case_id: str, root: Path = CASES_ROOT) -> dict[str, Any]:
    path = root / f"{case_id}.json"
    if not path.is_file():
        raise smoke.SmokeError(f"unknown wording case: {case_id}")
    case = json.loads(path.read_text(encoding="utf-8"))
    validate_case(case)
    return case


def validate_case(case: Mapping[str, Any]) -> None:
    if case.get("schema_version") != 1:
        raise smoke.SmokeError("wording cases must use schema_version 1")
    for key in ("id", "request", "skills", "variants", "answer_schema", "predicates"):
        if key not in case:
            raise smoke.SmokeError(f"wording case lacks {key}")
    variants = case["variants"]
    controls = [name for name, spec in variants.items() if spec.get("control")]
    if len(controls) != 1:
        raise smoke.SmokeError("a wording case needs exactly one control variant")
    if len(variants) < 2:
        raise smoke.SmokeError(
            "a wording case needs a control and at least one variant"
        )
    baselines = [name for name, spec in variants.items() if spec.get("baseline")]
    if len(baselines) > 1:
        raise smoke.SmokeError("a wording case may name at most one baseline variant")
    for name, spec in variants.items():
        unknown = set(spec.get("descriptions", {})) - set(case["skills"])
        if unknown:
            raise smoke.SmokeError(
                f"variant {name} overrides unknown skills: {sorted(unknown)}"
            )
    for predicate in case["predicates"]:
        if predicate.get("kind") not in PREDICATE_KINDS:
            raise smoke.SmokeError(f"unknown predicate kind: {predicate.get('kind')}")
        if predicate["kind"] == "resource_requested" and predicate.get(
            "resource"
        ) not in set(case["skills"]):
            raise smoke.SmokeError(
                f"predicate {predicate['id']} names an unknown skill"
            )


def split_skill(text: str) -> tuple[str, str]:
    """Return a skill's frontmatter description and its body without frontmatter."""

    match = re.match(r"---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return "", text
    description = ""
    for line in match.group(1).splitlines():
        if line.startswith("description:"):
            description = line.split(":", 1)[1].strip()
    return description, text[match.end() :]


def skill_texts(
    names: Sequence[str], root: Path = SKILLS_ROOT
) -> dict[str, tuple[str, str]]:
    texts: dict[str, tuple[str, str]] = {}
    for name in names:
        path = root / name / "SKILL.md"
        if not path.is_file():
            raise smoke.SmokeError(f"skill is unavailable: {name}")
        texts[name] = split_skill(path.read_text(encoding="utf-8"))
    return texts


def response_schema(answer_schema: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["request_resources", "complete"]},
            "requested_skills": {"type": "array", "items": {"type": "string"}},
            "answer": answer_schema,
        },
        "required": ["status", "requested_skills", "answer"],
        "additionalProperties": False,
    }


def build_prompt(
    case: Mapping[str, Any],
    variant: str,
    *,
    policy: str,
    skills: Mapping[str, tuple[str, str]],
    loaded: Sequence[str],
    history: Sequence[Mapping[str, Any]],
) -> str:
    overrides = case["variants"][variant].get("descriptions", {})
    lines = []
    for name, (description, _body) in skills.items():
        shown = overrides.get(name, description)
        lines.append(f"- {name}: {shown}" if shown else f"- {name}")
    catalog = "\n".join(lines)
    loaded_text = (
        "\n\n".join(
            f'<skill name="{name}">\n{skills[name][1].strip()}\n</skill>'
            for name in loaded
        )
        or "(none)"
    )
    return f"""You are a coding agent in a repository that uses the root policy below.
Decide how you would handle the user request. This is a public plan, not hidden reasoning.
Do not use tools, access a filesystem, or invent skill contents.
The skills listed are exposed in this session. Before answering, you may request the full
instructions of any listed skill by name with status="request_resources"; they will be shown
next round. When you have what you need, return status="complete" with your answer.
Fill answer with your best current plan in every round.

<always_loaded_policy>
{policy}
</always_loaded_policy>

Exposed skills (name: description):
{catalog}

User request:
{case["request"]}

Skill instructions loaded so far:
{loaded_text}

Your prior responses:
{json.dumps(list(history), indent=2)}

Return only the JSON object required by the supplied output schema.
"""


def score(
    case: Mapping[str, Any], requested: Sequence[str], answer: Mapping[str, Any]
) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for predicate in case["predicates"]:
        kind = predicate["kind"]
        if kind == "resource_requested":
            passed = predicate["resource"] in requested
        elif kind == "answer_equals":
            passed = answer.get(predicate["field"]) == predicate["value"]
        else:
            value = answer.get(predicate["field"])
            passed = isinstance(value, list) and predicate["value"] in value
        results[predicate["id"]] = passed
    return results


def run_sample(
    case: Mapping[str, Any],
    variant: str,
    invoke: smoke.Invoke,
    budget: smoke.CostBudget,
    *,
    policy: str,
    skills: Mapping[str, tuple[str, str]],
) -> dict[str, Any]:
    loaded: list[str] = []
    requested: list[str] = []
    history: list[Mapping[str, Any]] = []
    first_prompt_bytes: int | None = None
    for round_number in range(1, MAX_ROUNDS + 1):
        budget.check()
        prompt = build_prompt(
            case, variant, policy=policy, skills=skills, loaded=loaded, history=history
        )
        if first_prompt_bytes is None:
            first_prompt_bytes = len(prompt.encode("utf-8"))
        response, usage = invoke(prompt)
        budget.add(usage)
        history.append(response)
        names = [
            name
            for name in response.get("requested_skills", [])
            if isinstance(name, str)
        ]
        if response.get("status") == "complete":
            answer = response.get("answer")
            if not isinstance(answer, dict):
                raise smoke.SmokeError("completed response lacks an answer object")
            return {
                "variant": variant,
                "rounds": round_number,
                "requested_skills": requested,
                "answer": answer,
                "predicates": score(case, requested, answer),
                "first_prompt_bytes": first_prompt_bytes,
            }
        new = [name for name in names if name in skills and name not in loaded]
        requested.extend(name for name in names if name not in requested)
        if not new:
            break
        loaded.extend(new)
    return {
        "variant": variant,
        "rounds": len(history),
        "requested_skills": requested,
        "answer": None,
        "predicates": None,
        "first_prompt_bytes": first_prompt_bytes,
        "error": "no complete answer within the round limit",
    }


def summarize(
    case: Mapping[str, Any], samples: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    predicate_ids = [predicate["id"] for predicate in case["predicates"]]
    control = next(
        name for name, spec in case["variants"].items() if spec.get("control")
    )
    baseline = next(
        (name for name, spec in case["variants"].items() if spec.get("baseline")),
        control,
    )
    variants: dict[str, Any] = {}
    for name in case["variants"]:
        own = [sample for sample in samples if sample["variant"] == name]
        scored = [sample for sample in own if sample.get("predicates") is not None]
        patterns = Counter(
            tuple(sample["predicates"][pid] for pid in predicate_ids)
            for sample in scored
        )
        variants[name] = {
            "samples": len(own),
            "scored": len(scored),
            "passes": {
                pid: sum(1 for sample in scored if sample["predicates"][pid])
                for pid in predicate_ids
            },
            "distinct_outcome_patterns": len(patterns),
            "first_prompt_bytes": own[0]["first_prompt_bytes"] if own else None,
        }
    baseline_scored = [
        sample
        for sample in samples
        if sample["variant"] == baseline and sample.get("predicates") is not None
    ]
    failure_observed = (
        any(not all(sample["predicates"].values()) for sample in baseline_scored)
        if baseline_scored
        else None
    )
    return {
        "control": control,
        "baseline": baseline,
        "baseline_failure_observed": failure_observed,
        "interpretation": (
            f"The {baseline} variant showed no failure; this run supports no wording change."
            if failure_observed is False
            else "Compare pass counts and spread by hand; read every sample before deciding."
        ),
        "variants": variants,
    }


def run(
    case: Mapping[str, Any],
    invoke: smoke.Invoke,
    budget: smoke.CostBudget,
    *,
    reps: int,
    policy: str | None = None,
    skills: Mapping[str, tuple[str, str]] | None = None,
) -> dict[str, Any]:
    if reps < MIN_REPS:
        raise smoke.SmokeError(f"use at least {MIN_REPS} repetitions per variant")
    policy = smoke.consumer_policy() if policy is None else policy
    skills = skill_texts(case["skills"]) if skills is None else skills
    samples: list[dict[str, Any]] = []
    stopped: str | None = None
    for rep in range(1, reps + 1):
        for variant in case["variants"]:
            if budget.spent_usd >= budget.max_usd:
                stopped = (
                    f"estimated cost ${budget.spent_usd:.4f} reached the "
                    f"${budget.max_usd:.2f} limit"
                )
                break
            try:
                sample = run_sample(
                    case, variant, invoke, budget, policy=policy, skills=skills
                )
            except smoke.SmokeError as exc:
                sample = {"variant": variant, "predicates": None, "error": str(exc)}
            sample["rep"] = rep
            samples.append(sample)
        if stopped:
            break
    return {
        "schema_version": 1,
        "case": case["id"],
        "reps_requested": reps,
        "stopped": stopped,
        "estimated_cost_usd": round(budget.spent_usd, 6),
        "usage_unavailable": budget.usage_unavailable,
        "summary": summarize(case, samples),
        "samples": samples,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    payload = commands.add_parser("payload", help="print first-round prompts only")
    payload.add_argument("--case", required=True)

    live = commands.add_parser("run", help="contact a model and write a report")
    live.add_argument("--case", required=True)
    live.add_argument("--adapter", choices=["codex", "claude"], default="codex")
    live.add_argument("--model", required=True)
    live.add_argument("--executable")
    live.add_argument("--effort", choices=["low", "medium", "high"])
    live.add_argument("--reps", type=int, default=MIN_REPS)
    live.add_argument("--timeout-seconds", type=int, default=300)
    live.add_argument("--max-estimated-cost-usd", type=float, required=True)
    live.add_argument("--input-price-per-million", type=float, required=True)
    live.add_argument("--cached-input-price-per-million", type=float, required=True)
    live.add_argument("--output-price-per-million", type=float, required=True)
    live.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        case = load_case(args.case)
        if args.command == "payload":
            policy = smoke.consumer_policy()
            skills = skill_texts(case["skills"])
            for variant in case["variants"]:
                print(f"===== {variant} =====")
                print(
                    build_prompt(
                        case,
                        variant,
                        policy=policy,
                        skills=skills,
                        loaded=[],
                        history=[],
                    )
                )
            return 0
        prices = (
            args.input_price_per_million,
            args.cached_input_price_per_million,
            args.output_price_per_million,
        )
        if not all(value >= 0 for value in prices):
            raise smoke.SmokeError("token prices must be nonnegative")
        if not 0 < args.max_estimated_cost_usd <= HARD_MAX_COST_USD:
            raise smoke.SmokeError(
                f"the cost limit must be positive and at most ${HARD_MAX_COST_USD:.2f}"
            )
        if args.effort is not None and args.adapter != "codex":
            raise smoke.SmokeError("--effort applies only to the codex adapter")
        output = smoke.validated_output_path(args.output)
        schema = response_schema(case["answer_schema"])
        effort = None
        if args.adapter == "codex":
            effort = args.effort or "low"
            invoke = smoke.codex_invoke(
                model=args.model,
                executable=args.executable,
                timeout_seconds=args.timeout_seconds,
                schema=schema,
                effort=effort,
            )
        else:
            invoke = smoke.claude_invoke(
                model=args.model,
                executable=args.executable,
                timeout_seconds=args.timeout_seconds,
                schema=schema,
            )
        budget = smoke.CostBudget(args.max_estimated_cost_usd, *prices)
        report = run(case, invoke, budget, reps=args.reps)
        report["conditions"] = {
            "adapter": args.adapter,
            "model": args.model,
            "effort": effort,
            "revision": smoke.revision("rev-parse", "HEAD"),
            "case_sha256": smoke.fingerprint(case),
        }
        smoke.write_json(output, report)
        print(json.dumps(report["summary"], indent=2))
        return 0
    except smoke.SmokeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
