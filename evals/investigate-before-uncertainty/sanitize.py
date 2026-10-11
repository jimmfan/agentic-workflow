#!/usr/bin/env python3
"""Build blind adjudication cases from raw Codex traces; no scoring.

Usage: sanitize.py <manifest.json> <payload-root> <out-dir> <seed>

The manifest lists {"invocation", "arm", "scenario", "subject"} entries, where
subject is an adapter run directory. The payload root holds one installed
consumer per arm (<payload-root>/<arm>), used only to recognize policy text.
Cases omit reasoning items, the route marker, arm labels, absolute paths, and
policy-file text or output, including line numbers and sizes that differ
between arms. The case-to-invocation key is written beside the cases.
"""

import json
from pathlib import Path
import random
import re
import string
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/race-weekend-planning"
ROLES = {
    "arrival-margin-question": "Treatment A",
    "arrival-margin-followup": "Treatment B",
    "arrival-official-time": "Control",
}
POLICY_TOKEN = re.compile(r"AGENTS\.md|\.agent-workflow|\.agents/|\.claude/|skills/")
FIXTURE_TOKEN = re.compile(r"race-info/[\w.-]+|README\.md")
ROUTE = re.compile(r"\n?\[route:[^\]\n]*\]\s*$")
ABSOLUTE = re.compile(r"/(?:private|var|Users|tmp|opt|Library)(?:/[^\s'\"`:)]*)?")
LINE_PREFIX = re.compile(r"^(?:\./)?(?:[\w.-]+/)*[\w.-]+:\d+[:-]|^\s*\d+[\t:-]\s?")
REDACTED = "[policy text redacted]"


def lines_of(paths):
    result = set()
    for path in paths:
        if path.is_file():
            for line in path.read_text(errors="replace").splitlines():
                if line.strip():
                    result.add(line.strip())
    return result


def fixture_lines():
    return lines_of(FIXTURE.rglob("*")) | {
        str(path.relative_to(FIXTURE)) for path in FIXTURE.rglob("*")
    }


def policy_lines(payload_root, fixture):
    paths = []
    for arm in payload_root.iterdir():
        for path in arm.rglob("*"):
            relative = path.relative_to(arm).as_posix()
            if not FIXTURE.joinpath(relative).exists():
                paths.append(path)
    return {line for line in lines_of(paths) - fixture if len(line) >= 12}


def strip_paths(text, workspace):
    text = text.replace(str(workspace) + "/", "").replace(str(workspace), ".")
    return ABSOLUTE.sub("<path>", text)


def filter_output(output, policy_command, fixture, policy):
    kept = []
    for line in output.splitlines():
        content = LINE_PREFIX.sub("", line).strip()
        if policy_command:
            keep = not content or content in fixture
        else:
            keep = (
                not (POLICY_TOKEN.search(line) and line.strip() not in {"AGENTS.md"})
                and content not in policy
            )
        if keep:
            kept.append(line)
        elif not kept or kept[-1] != REDACTED:
            kept.append(REDACTED)
    return "\n".join(kept)


def events_for(subject, fixture, policy):
    record = json.loads((subject / "invocation.json").read_text())
    workspace = Path(record["workspace"])
    events, key = [], []
    for raw in (subject / "raw/codex.jsonl").read_text().splitlines():
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
        if kind == "command_execution":
            command = strip_paths(item.get("command", ""), workspace)
            policy_command = bool(POLICY_TOKEN.search(command))
            if policy_command:
                also = sorted(set(FIXTURE_TOKEN.findall(command)))
                command = "[policy-file command redacted]" + (
                    f"; also references {', '.join(also)}" if also else ""
                )
            output = strip_paths(item.get("aggregated_output") or "", workspace)
            entry.update(
                type="command",
                command=command,
                exit_code=item.get("exit_code"),
                output=filter_output(output, policy_command, fixture, policy),
            )
        elif kind == "agent_message":
            entry.update(type="message", text=strip_paths(item["text"], workspace))
        else:
            detail = {k: v for k, v in item.items() if k not in {"id", "type"}}
            entry.update(type=kind, detail=strip_paths(json.dumps(detail), workspace))
        events.append(entry)
        key.append({"event": entry["id"], "raw_item": item.get("id")})
    final = None
    if events and events[-1]["type"] == "message":
        final = events.pop()
        key.pop()
        final = ROUTE.sub("", final["text"]).rstrip()
    route = re.findall(
        r"\[route:[^\]\n]*\]", (subject / "raw/response.txt").read_text()
    )
    return events, final, route, key


def main():
    manifest, payload_root, out, seed = sys.argv[1:5]
    entries = json.loads(Path(manifest).read_text())
    rng = random.Random(seed)
    rng.shuffle(entries)
    fixture = fixture_lines()
    policy = policy_lines(Path(payload_root), fixture)
    out = Path(out)
    (out / "cases").mkdir(parents=True, exist_ok=True)
    key = []
    for index, entry in enumerate(entries, start=1):
        case_id = f"C{index:02d}-" + "".join(rng.choices(string.ascii_lowercase, k=4))
        scenario = tomllib.loads(
            (ROOT / "tests/scenarios" / f"{entry['scenario']}.toml").read_text()
        )
        events, final, route, event_key = events_for(
            Path(entry["subject"]), fixture, policy
        )
        case = {
            "case": case_id,
            "scenario_role": ROLES[entry["scenario"]],
            "user_request": scenario["request"].strip(),
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
