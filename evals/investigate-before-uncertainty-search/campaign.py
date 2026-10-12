"""Shared pieces for the search campaign; no scoring.

Covers the frozen `web` MCP attachment, the single-field model catalog override,
scripted mock turns through Codex's real tool and session machinery, and audits
of the captured model request.
"""

import json
from pathlib import Path
import re
import shutil
import subprocess

import mock_provider
import web_server

SUITE = Path(__file__).resolve().parent
SERVER = SUITE / "web_server.py"
CORPUS = SUITE / "corpus.json"
SERVER_NAME = "web"
MODEL_VISIBLE_TOOL = "mcp__web__search"
CATALOG_MODEL = "gpt-6.1-sol"
CATALOG_FIELD = "supports_search_tool"
# Terms that must not appear in the model-visible tool list or developer context.
FORBIDDEN = re.compile(
    r"quillmere|marathon|corral|runner-report|corpus|fixture|investigate-before"
    r"|evals/|evaluation|\brace\b|\bgate d\b",
    re.I,
)
# Path components that would reveal the evaluation, its location, or an arm.
PATH_LEAK = re.compile(
    r"evals|artifacts|investigat|baseline|candidate|agentic-workflow|subject"
    r"|scratchpad|claude-\d+|preflight|campaign|capture|fixture",
    re.I,
)
EXEC_ITEM_KEYS = {"type", "id", "status", "call_id", "name", "input"}
EXEC_INPUT = re.compile(r"^text\(await tools\.[a-z_]+\(\{.*\}\)\);\n$", re.S)


def mcp_settings(python):
    return [
        f"mcp_servers.{SERVER_NAME}.command={json.dumps(str(python))}",
        f"mcp_servers.{SERVER_NAME}.args=[{json.dumps(str(SERVER))}]",
        f'mcp_servers.{SERVER_NAME}.enabled_tools=["search"]',
        f"mcp_servers.{SERVER_NAME}.required=true",
        f'mcp_servers.{SERVER_NAME}.default_tools_approval_mode="approve"',
    ]


def override_catalog(shipped_text):
    """Return the shipped catalog with only the frozen field flipped to false."""
    catalog = json.loads(shipped_text)
    entries = [m for m in catalog["models"] if m.get("slug") == CATALOG_MODEL]
    if len(entries) != 1 or entries[0].get(CATALOG_FIELD) is not True:
        raise ValueError("Shipped catalog lacks the expected model or field value")
    entries[0][CATALOG_FIELD] = False
    return json.dumps(catalog, ensure_ascii=False)


def changed_paths(left, right, path=""):
    if isinstance(left, dict) and isinstance(right, dict):
        result = []
        for key in sorted(set(left) | set(right), key=str):
            if key not in left or key not in right:
                result.append(f"{path}/{key}")
            else:
                result.extend(changed_paths(left[key], right[key], f"{path}/{key}"))
        return result
    if isinstance(left, list) and isinstance(right, list) and len(left) == len(right):
        return [
            item
            for index, (a, b) in enumerate(zip(left, right))
            for item in changed_paths(a, b, f"{path}/{index}")
        ]
    return [] if left == right else [path or "/"]


def catalog_audit(shipped_text, override_text):
    """Require exactly one change: the frozen field of the frozen model."""
    shipped = json.loads(shipped_text)
    index = next(
        i for i, m in enumerate(shipped["models"]) if m.get("slug") == CATALOG_MODEL
    )
    changes = changed_paths(shipped, json.loads(override_text))
    expected = [f"/models/{index}/{CATALOG_FIELD}"]
    if changes != expected:
        raise ValueError(f"Catalog override changes {changes}, expected {expected}")
    return changes


def additional_tools(body):
    return [
        item for item in body.get("input", []) if item.get("type") == "additional_tools"
    ]


def exec_description(body):
    for item in additional_tools(body):
        for namespace in item.get("tools", []):
            for tool in namespace.get("tools", []) or []:
                if tool.get("name") == "exec":
                    return tool.get("description", "")
    return ""


def listed_tools(body):
    """Nested tool names declared in the exec description."""
    return re.findall(r"^### `([^`]+)`", exec_description(body), re.M)


def developer_texts(body):
    return [
        part.get("text", "")
        for item in body.get("input", [])
        if item.get("role") == "developer"
        for part in item.get("content", []) or []
    ]


def user_texts(body):
    return [
        part.get("text", "")
        for item in body.get("input", [])
        if item.get("role") == "user"
        for part in item.get("content", []) or []
    ]


def audit_request(body, agents_text):
    """Return failures for one captured model request; empty means it passed."""
    failures = []
    tools_text = json.dumps(additional_tools(body))
    names = listed_tools(body)
    mcp_names = sorted({n for n in names if n.startswith("mcp__")})
    if mcp_names != [MODEL_VISIBLE_TOOL]:
        failures.append(f"listed MCP tools are {mcp_names}")
    description = exec_description(body)
    section = description.split(f"### `{MODEL_VISIBLE_TOOL}`", 1)[-1]
    if not section.lstrip().startswith(web_server.DESCRIPTION):
        failures.append("search is not listed with the frozen description")
    if FORBIDDEN.search(tools_text):
        failures.append(f"tool list contains {FORBIDDEN.search(tools_text).group(0)!r}")
    for text in developer_texts(body):
        if MODEL_VISIBLE_TOOL in text:
            failures.append("a developer message mentions the search tool")
        if FORBIDDEN.search(text):
            failures.append(
                f"developer context contains {FORBIDDEN.search(text).group(0)!r}"
            )
    if str(SUITE) in json.dumps(body) or str(CORPUS) in json.dumps(body):
        failures.append("request contains the campaign directory or corpus path")
    leaked = sorted(
        {
            path
            for path in re.findall(r"(?:/[\w.@+-]+){2,}", json.dumps(body))
            if PATH_LEAK.search(path)
        }
    )
    if leaked:
        failures.append(f"request paths reveal the evaluation: {leaked[:5]}")
    if agents_text.strip() and not any(
        agents_text.strip() in t for t in user_texts(body)
    ):
        failures.append("request lacks the workspace AGENTS.md text")
    return failures


def run_mock(
    binary,
    config,
    cwd,
    env,
    prompt,
    steps,
    raw,
    label,
    *,
    resume=None,
    seed=None,
    provider="mock",
):
    """Run one Codex turn against the scripted provider and return its record."""
    log = raw / f"{label}-requests.json-lines"
    log.unlink(missing_ok=True)
    with mock_provider.MockProvider(steps, log, seed=seed or label) as mock:
        settings = mock_provider.provider_settings(mock.base_url, provider)
        mock_config = [*config, *(x for s in settings for x in ("-c", s))]
        command = [str(binary), "exec"]
        if resume:
            command += ["resume"]
        command += [
            "--ignore-user-config",
            "--ignore-rules",
            *mock_config,
            "--skip-git-repo-check",
            "--json",
        ]
        command += [resume, "-"] if resume else ["-C", str(cwd), "-"]
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=120,
        )
    (raw / f"{label}-events.json-lines").write_text(completed.stdout)
    (raw / f"{label}-stderr.txt").write_text(completed.stderr)
    events = [
        json.loads(line) for line in completed.stdout.splitlines() if line.strip()
    ]
    requests = (
        [json.loads(line) for line in log.read_text().splitlines()]
        if log.exists()
        else []
    )
    thread = next(
        (e["thread_id"] for e in events if e.get("type") == "thread.started"), None
    )
    return {
        "returncode": completed.returncode,
        "thread_id": thread,
        "events": events,
        "requests": [r for r in requests if r.get("method") == "POST" and "index" in r],
        "failed": any(e.get("type") in {"turn.failed", "error"} for e in events),
    }


def rollout_items(home, thread_id):
    paths = sorted(Path(home, "sessions").rglob(f"*{thread_id}*.jsonl"))
    if len(paths) != 1:
        raise ValueError(f"Expected one rollout for {thread_id}, found {len(paths)}")
    return [
        json.loads(line) for line in paths[0].read_text().splitlines() if line.strip()
    ]


def exec_item_failures(item):
    """Compare a recorded exec call with the shape of model-made exec calls."""
    failures = []
    keys = set(item) - {"internal_chat_message_metadata_passthrough"}
    if keys != EXEC_ITEM_KEYS:
        failures.append(f"keys {sorted(keys)}")
    if item.get("name") != "exec" or item.get("status") != "completed":
        failures.append("not a completed exec call")
    if not re.fullmatch(r"ctc_[0-9a-f]{50}", item.get("id", "")):
        failures.append("id format")
    if not re.fullmatch(
        r"call_(?:[0-9a-f]{32}|[A-Za-z0-9]{24})", item.get("call_id", "")
    ):
        failures.append("call_id format")
    if not EXEC_INPUT.fullmatch(item.get("input", "")):
        failures.append("input format")
    return failures


def copy_home(source, destination):
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("auth.json"))
    return destination
