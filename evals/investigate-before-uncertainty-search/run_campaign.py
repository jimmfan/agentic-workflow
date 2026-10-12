#!/usr/bin/env python3
"""Run predeclared slots of the search campaign sequentially; no scoring.

Usage:
  run_campaign.py <plan.json> --label <name> --baseline-root <worktree>
                  [--b-form search|inline|embedded] [--capture-only]

A plan is a JSON list of [slot, arm, scenario] with arm in {baseline, candidate}
and scenario in {treatment-a, treatment-b, control}. Each slot gets a fresh
workspace holding only that arm's installed framework, then one adapter call
with exactly the frozen user message on stdin. Subject paths stay neutral and
outside the repository because they reach the model; each run's raw evidence is
moved under evals/artifacts afterwards. Stops at the first quota,
authentication, or rate-limit failure, or after two consecutive infrastructure
failures.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

SUITE = Path(__file__).resolve().parent
ROOT = SUITE.parents[1]
ADAPTER = ROOT / "evals/remaining-audit-behavior/codex_subject.py"
ARTIFACTS = ROOT / "evals/artifacts/investigate-before-uncertainty-search"
MODEL = "gpt-6.1-sol"
SHIPPED_CATALOG_SHA256 = (
    "85aa95e9ca74c6ea4c91ed2461d196622707625796ae1936ffcbffb82df54d9f"
)
STOP = re.compile(
    r"rate.?limit|quota|usage limit|\b429\b|\b401\b|\b403\b|unauthori[sz]ed"
    r"|authenticat|not logged in|login required",
    re.I,
)
SUCCESS = {"completed", "capture-completed"}


def prepare_workspace(arm_root, neutral):
    workspace = Path(tempfile.mkdtemp(dir=neutral / "w")) / "work"
    workspace.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=workspace, check=True)
    subprocess.run(
        [
            sys.executable,
            str(arm_root / "agent_workflow/lifecycle.py"),
            "install",
            str(workspace),
        ],
        check=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return workspace


def adapter_command(scenario, b_form, capture_only, neutral):
    command = [
        sys.executable,
        str(ADAPTER),
        "--output-root",
        str(neutral / "out"),
        "--model",
        MODEL,
        "--timeout-seconds",
        "600",
        "--mcp-server",
        "--catalog-sha256",
        SHIPPED_CATALOG_SHA256,
    ]
    if scenario == "treatment-b" and b_form != "embedded":
        command += ["--turn1", str(SUITE / "turn1.json"), "--turn1-form", b_form]
    if capture_only:
        command.append("--capture-only")
    return command


def prompt_for(scenario, b_form):
    prompts = json.loads((SUITE / "prompts.json").read_text())
    if scenario == "treatment-b" and b_form == "embedded":
        return prompts["treatment-b-embedded"]
    return prompts[scenario]


def run_slot(slot, arm, scenario, args, neutral, destination):
    arm_root = args.baseline_root if arm == "baseline" else ROOT
    workspace = prepare_workspace(arm_root, neutral)
    before = set((neutral / "out").iterdir())
    completed = subprocess.run(
        adapter_command(scenario, args.b_form, args.capture_only, neutral),
        cwd=workspace,
        input=prompt_for(scenario, args.b_form),
        text=True,
        capture_output=True,
        timeout=900,
    )
    created = sorted(set((neutral / "out").iterdir()) - before)
    target = destination / slot
    target.mkdir(parents=True)
    (target / "adapter-stdout.txt").write_text(completed.stdout)
    (target / "adapter-stderr.txt").write_text(completed.stderr)
    record = {}
    if len(created) == 1:
        shutil.move(str(created[0]), target / "run")
        record = json.loads((target / "run/invocation.json").read_text())
    shutil.move(str(workspace.parent), target / "workspace")
    texts = [completed.stderr, str(record.get("error") or "")]
    stderr = target / "run/raw/stderr.txt"
    if stderr.exists():
        texts.append(stderr.read_text(errors="replace")[-20000:])
    infrastructure = (
        record.get("execution") not in SUCCESS or record.get("returncode") != 0
    )
    return {
        "slot": slot,
        "arm": arm,
        "scenario": scenario,
        "b_form": args.b_form if scenario == "treatment-b" else None,
        "capture_only": args.capture_only,
        "execution": record.get("execution"),
        "returncode": record.get("returncode"),
        "error": record.get("error"),
        "infrastructure_failure": infrastructure,
        "stop_condition": infrastructure and bool(STOP.search("\n".join(texts))),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--baseline-root", required=True, type=Path)
    parser.add_argument(
        "--b-form", choices=("search", "inline", "embedded"), default="search"
    )
    parser.add_argument("--capture-only", action="store_true")
    parser.add_argument("--neutral-root", type=Path, default=Path("/private/tmp/kx"))
    args = parser.parse_args()
    args.baseline_root = args.baseline_root.resolve()
    neutral = args.neutral_root
    for name in ("w", "out"):
        (neutral / name).mkdir(parents=True, exist_ok=True)
    destination = ARTIFACTS / args.label
    destination.mkdir(parents=True, exist_ok=True)
    consecutive = 0
    for slot, arm, scenario in json.loads(args.plan.read_text()):
        status = run_slot(slot, arm, scenario, args, neutral, destination)
        print(json.dumps(status), flush=True)
        with (destination / "status.json-lines").open("a") as handle:
            handle.write(json.dumps(status) + "\n")
        consecutive = consecutive + 1 if status["infrastructure_failure"] else 0
        if status["stop_condition"]:
            print("STOP: quota, authentication, or rate-limit failure", flush=True)
            return 3
        if consecutive >= 2:
            print("STOP: two consecutive infrastructure failures", flush=True)
            return 4
    print("PLAN COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
