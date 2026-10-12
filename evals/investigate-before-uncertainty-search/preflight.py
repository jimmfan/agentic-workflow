#!/usr/bin/env python3
"""No-model preflight for the search campaign.

Usage: preflight.py --baseline-root <worktree>

Runs only scripted-provider and catalog requests, never a model. Writes raw
output under evals/artifacts and a compact summary to preflight.json here.
"""

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SUITE = Path(__file__).resolve().parent
sys.path.insert(0, str(SUITE))
import campaign  # noqa: E402
import run_campaign  # noqa: E402

ROOT = SUITE.parents[1]
ARTIFACTS = run_campaign.ARTIFACTS / "preflight"
CANDIDATE_SENTENCE = (
    "When unresolved uncertainty about a material fact could change a conclusion"
)
VOLATILE = {"id", "client_metadata", "prompt_cache_key"}


def install(arm_root, destination):
    destination.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=destination, check=True)
    subprocess.run(
        [
            sys.executable,
            str(arm_root / "agent_workflow/lifecycle.py"),
            "install",
            str(destination),
        ],
        check=True,
        capture_output=True,
    )
    shutil.rmtree(destination / ".git")


def payload_diff(baseline_root, scratch):
    install(baseline_root, scratch / "baseline")
    install(ROOT, scratch / "candidate")
    result = subprocess.run(
        ["diff", "-r", "-u", "baseline", "candidate"],
        cwd=scratch,
        text=True,
        capture_output=True,
    )
    added = [
        line[1:]
        for line in result.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    removed = [
        line[1:]
        for line in result.stdout.splitlines()
        if line.startswith("-") and not line.startswith("---")
    ]
    files = sorted(
        {
            line.split()[1]
            for line in result.stdout.splitlines()
            if line.startswith("+++ ")
        }
    )
    return {"files": files, "added_lines": added, "removed_lines": removed}


def shipped_catalog(scratch):
    home = scratch / "catalog-home"
    home.mkdir()
    source = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
    shutil.copyfile(source, home / "auth.json")
    try:
        text = subprocess.run(
            ["codex", "debug", "models"],
            env={
                "CODEX_HOME": str(home),
                "PATH": os.environ["PATH"],
                "LANG": "en_US.UTF-8",
            },
            text=True,
            capture_output=True,
            timeout=60,
            check=True,
        ).stdout
    finally:
        (home / "auth.json").unlink(missing_ok=True)
    return text


def normalized(value):
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items() if k not in VOLATILE}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value


def capture(scratch, workspace, catalog_path, label):
    """Capture one first-turn request with the MCP server attached."""
    home = scratch / "capture-codex-home"
    shutil.rmtree(home, ignore_errors=True)
    home.mkdir()
    settings = [
        f'model="{run_campaign.MODEL}"',
        'model_reasoning_effort="medium"',
        'approval_policy="never"',
        'web_search="disabled"',
        "features.apps=false",
        "features.plugins=false",
        "features.memories=false",
        f"model_catalog_json={json.dumps(str(catalog_path))}",
        *campaign.mcp_settings(sys.executable),
    ]
    config = [x for s in settings for x in ("-c", s)]
    env = {"CODEX_HOME": str(home), "PATH": os.environ["PATH"], "LANG": "en_US.UTF-8"}
    raw = scratch / "raw"
    raw.mkdir(exist_ok=True)
    result = campaign.run_mock(
        "codex", config, workspace, env, "Hello.", [{"message": "ok"}], raw, label
    )
    return result["requests"][0]["body"]


def request_diff(scratch, shipped_text):
    workspace = scratch / "diff-workspace"
    install(ROOT, workspace)
    shipped_path = scratch / "shipped-catalog.json"
    shipped_path.write_text(shipped_text)
    override_path = scratch / "override-catalog.json"
    override_path.write_text(campaign.override_catalog(shipped_text))
    shipped = capture(scratch, workspace, shipped_path, "shipped")
    override = capture(scratch, workspace, override_path, "override")
    changes = campaign.changed_paths(normalized(shipped), normalized(override))
    before = campaign.exec_description(shipped).splitlines()
    after = campaign.exec_description(override).splitlines()
    text_diff = list(difflib.unified_diff(before, after, lineterm="", n=0))
    return {
        "changed_request_paths": changes,
        "listed_tools_shipped": campaign.listed_tools(shipped),
        "listed_tools_override": campaign.listed_tools(override),
        "exec_description_added_lines": [
            line[1:]
            for line in text_diff
            if line.startswith("+") and not line.startswith("+++")
        ],
        "exec_description_removed_lines": [
            line[1:]
            for line in text_diff
            if line.startswith("-") and not line.startswith("---")
        ],
    }


def reference_exec_items():
    """Check the format checker against real model-made exec calls from campaign 1."""
    rollouts = sorted(
        (ROOT / "evals/artifacts/investigate-before-uncertainty").glob(
            "*/subjects/*/codex-home/sessions/*/*/*/*.jsonl"
        )
    )
    items = []
    for path in rollouts:
        for line in path.read_text().splitlines():
            payload = json.loads(line).get("payload", {})
            if (
                payload.get("type") == "custom_tool_call"
                and payload.get("name") == "exec"
            ):
                items.append(payload)
    return {
        "model_made_exec_items": len(items),
        "items_with_format_failures": sum(
            bool(campaign.exec_item_failures(i)) for i in items
        ),
    }


def capture_matrix(baseline_root):
    plans = {
        "capture-search": [
            [f"{arm}-{scenario}", arm, scenario]
            for arm in ("baseline", "candidate")
            for scenario in ("treatment-a", "treatment-b", "control")
        ],
        "capture-inline": [
            [f"{arm}-treatment-b", arm, "treatment-b"]
            for arm in ("baseline", "candidate")
        ],
    }
    summary = {}
    for label, plan in plans.items():
        destination = run_campaign.ARTIFACTS / "preflight" / label
        shutil.rmtree(destination, ignore_errors=True)
        plan_path = ARTIFACTS / f"{label}-plan.json"
        plan_path.write_text(json.dumps(plan))
        form = "inline" if label == "capture-inline" else "search"
        subprocess.run(
            [
                sys.executable,
                str(SUITE / "run_campaign.py"),
                str(plan_path),
                "--label",
                f"preflight/{label}",
                "--baseline-root",
                str(baseline_root),
                "--b-form",
                form,
                "--capture-only",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        rows = []
        for slot, arm, scenario in plan:
            run = destination / slot / "run"
            record = json.loads((run / "invocation.json").read_text())
            requests_path = run / "raw/capture-requests.json-lines"
            body = (
                json.loads(requests_path.read_text().splitlines()[0])["body"]
                if requests_path.exists()
                else {}
            )
            agents = "\n".join(campaign.user_texts(body))
            info = record.get("search_campaign", {})
            rows.append(
                {
                    "slot": slot,
                    "execution": record.get("execution"),
                    "error": record.get("error"),
                    "prompt_sha256": record.get("prompt_sha256"),
                    "catalog_changes": record.get("catalog", {}).get("changes"),
                    "isolation_returncode": record.get("isolation", {}).get(
                        "returncode"
                    ),
                    "credential_copy_removed": record.get("credential_copy_removed"),
                    "candidate_sentence_present": CANDIDATE_SENTENCE in agents,
                    "listed_tools": info.get("capture", {}).get("listed_tools"),
                    "turn1": {
                        k: info["turn1"][k]
                        for k in ("form", "exec_item_format_failures")
                    }
                    if "turn1" in info
                    else None,
                    "turn1_search_result_sha256": hashlib.sha256(
                        json.dumps(info["turn1"]["search_results"]).encode()
                    ).hexdigest()
                    if info.get("turn1", {}).get("search_results")
                    else None,
                }
            )
        summary[label] = rows
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", required=True, type=Path)
    args = parser.parse_args()
    baseline_root = args.baseline_root.resolve()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="preflight-", dir=ARTIFACTS))
    shipped_text = shipped_catalog(scratch)
    override_text = campaign.override_catalog(shipped_text)
    summary = {
        "codex_cli": subprocess.check_output(["codex", "--version"], text=True).strip(),
        "payload_diff": payload_diff(baseline_root, scratch),
        "catalog": {
            "shipped_sha256": hashlib.sha256(shipped_text.encode()).hexdigest(),
            "frozen_sha256": run_campaign.SHIPPED_CATALOG_SHA256,
            "override_changes": campaign.catalog_audit(shipped_text, override_text),
        },
        "request_diff": request_diff(scratch, shipped_text),
        "reference_exec_items": reference_exec_items(),
        "capture_matrix": capture_matrix(baseline_root),
    }
    (SUITE / "preflight.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2)[:6000])


if __name__ == "__main__":
    main()
