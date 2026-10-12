#!/usr/bin/env python3
"""Build blind adjudication cases for the search campaign; no scoring.

Usage: sanitize.py <manifest.json> <payload-root> <out-dir> <seed>

The manifest lists {"invocation", "arm", "scenario", "run"} entries, where run
is a moved adapter run directory. The payload root holds one installed
framework per arm (<payload-root>/<arm>), used only to recognize policy text.
Reuses campaign 1's redaction rules: no reasoning items, route marker, arm
labels, absolute paths, or policy-file text. `search` calls appear with their
query and full returned pages. Treatment B shows its fixed first turn as
context. The case-to-invocation key is written beside the cases.
"""

import importlib.util
import json
from pathlib import Path
import random
import re
import string
import sys

SUITE = Path(__file__).resolve().parent
ROOT = SUITE.parents[1]
spec = importlib.util.spec_from_file_location(
    "campaign1_sanitize", ROOT / "evals/investigate-before-uncertainty/sanitize.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

ROLES = {
    "treatment-a": "Treatment A",
    "treatment-b": "Treatment B",
    "control": "Control",
}


def corpus_lines():
    pages = json.loads((SUITE / "corpus.json").read_text())["pages"]
    lines = set()
    for page in pages:
        for text in (page["title"], page["url"], *page["text"].splitlines()):
            if text.strip():
                lines.add(text.strip())
    return lines


def policy_lines(payload_root, keep):
    paths = [path for arm in payload_root.iterdir() for path in arm.rglob("*")]
    return {line for line in base.lines_of(paths) - keep if len(line) >= 12}


def request_text(scenario, b_form, prompts, turn1, record):
    if scenario != "treatment-b":
        return prompts[scenario]
    if b_form == "embedded":
        return prompts["treatment-b-embedded"]
    inline = b_form == "inline"
    first_user = turn1["fallback_inline_user" if inline else "user"]
    reply = turn1["fallback_inline_steps" if inline else "steps"][-1]["message"]
    lines = [
        "Fixed first turn (identical in every Treatment B case):",
        "",
        f"User: {first_user}",
    ]
    results = (
        record.get("search_campaign", {}).get("turn1", {}).get("search_results") or []
    )
    if not inline:
        query = re.search(
            r'query:"([^"]+)"', turn1["steps"][0]["custom_tool_call"]["input"]
        )
        text = "".join(
            part.get("text", "") for part in (results[0] or {}).get("content", [])
        )
        lines += [
            "",
            f"Assistant called search with query {query.group(1)!r}; it returned:",
            text,
        ]
    lines += [
        "",
        f"Assistant: {reply}",
        "",
        f"Scored second turn, user: {prompts['treatment-b']}",
    ]
    return "\n".join(lines)


def events_for(run, keep, policy):
    record = json.loads((run / "invocation.json").read_text())
    workspace = Path(record["workspace"])
    events, key = [], []
    for raw in (run / "raw/codex.jsonl").read_text().splitlines():
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "item.completed":
            continue
        item = event.get("item", {})
        kind = item.get("type")
        if kind == "reasoning":
            continue
        entry = {"id": f"E{len(events) + 1}"}
        if kind == "mcp_tool_call":
            result = item.get("result") or {}
            text = "".join(
                part.get("text", "") for part in result.get("content", []) or []
            )
            entry.update(
                type="search",
                query=(item.get("arguments") or {}).get("query"),
                status=item.get("status"),
                result=base.strip_paths(text, workspace),
            )
        elif kind == "command_execution":
            command = base.strip_paths(item.get("command", ""), workspace)
            policy_command = bool(base.POLICY_TOKEN.search(command))
            if policy_command:
                command = "[policy-file command redacted]"
            output = base.strip_paths(item.get("aggregated_output") or "", workspace)
            entry.update(
                type="command",
                command=command,
                exit_code=item.get("exit_code"),
                output=base.filter_output(output, policy_command, keep, policy),
            )
        elif kind == "agent_message":
            entry.update(type="message", text=base.strip_paths(item["text"], workspace))
        else:
            detail = {k: v for k, v in item.items() if k not in {"id", "type"}}
            entry.update(
                type=kind, detail=base.strip_paths(json.dumps(detail), workspace)
            )
        events.append(entry)
        key.append({"event": entry["id"], "raw_item": item.get("id")})
    final = None
    if events and events[-1]["type"] == "message":
        final = base.ROUTE.sub("", events.pop()["text"]).rstrip()
        key.pop()
    response = run / "raw/response.txt"
    route = (
        re.findall(r"\[route:[^\]\n]*\]", response.read_text())
        if response.exists()
        else []
    )
    return record, events, final, route, key


def main():
    manifest, payload_root, out, seed = sys.argv[1:5]
    entries = json.loads(Path(manifest).read_text())
    rng = random.Random(seed)
    rng.shuffle(entries)
    prompts = json.loads((SUITE / "prompts.json").read_text())
    turn1 = json.loads((SUITE / "turn1.json").read_text())
    keep = corpus_lines() | {
        line.strip()
        for text in prompts.values()
        for line in text.splitlines()
        if line.strip()
    }
    policy = policy_lines(Path(payload_root), keep)
    out = Path(out)
    (out / "cases").mkdir(parents=True, exist_ok=True)
    key = []
    for index, entry in enumerate(entries, start=1):
        case_id = f"C{index:02d}-" + "".join(rng.choices(string.ascii_lowercase, k=4))
        record, events, final, route, event_key = events_for(
            Path(entry["run"]), keep, policy
        )
        case = {
            "case": case_id,
            "scenario_role": ROLES[entry["scenario"]],
            "user_request": request_text(
                entry["scenario"], entry.get("b_form"), prompts, turn1, record
            ),
            "events": events,
            "final_response": final,
        }
        (out / "cases" / f"{case_id}.json").write_text(
            json.dumps(case, indent=2, ensure_ascii=False) + "\n"
        )
        key.append({**entry, "case": case_id, "route": route, "events": event_key})
    (out / "key.json").write_text(
        json.dumps({"seed": seed, "cases": key}, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
