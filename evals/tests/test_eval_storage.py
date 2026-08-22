from __future__ import annotations

from pathlib import Path
import runpy
import subprocess
import unittest

from evals import (
    arc_wayfinder,
    arc_wayfinder_state_complexity,
    arc_wayfinder_v2,
    wayfinder_fresh_agent_continuation,
    wayfinder_fresh_agent_continuation_v2,
)


ROOT = Path(__file__).resolve().parents[2]


def tracked_eval_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "evals"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.splitlines()


def is_ignored(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "--", path],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def is_raw_artifact(path: str) -> bool:
    parts = Path(path).parts
    name = parts[-1]
    return (
        "__pycache__" in parts
        or "raw" in parts
        or "snapshots" in parts and "runs" in parts
        or "workspace" in parts and "runs" in parts
        or "attempts" in parts and "runs" in parts
        or name in {"reasoning-grader.jsonl", "reasoning-grader.stderr.txt"}
        or "audit-evidence" in parts
        or "isolation-audit" in parts and name.endswith((".jsonl", ".stderr.txt"))
    )


class EvaluationStorageTests(unittest.TestCase):
    def test_raw_artifact_paths_are_ignored_but_compact_results_are_not(self) -> None:
        ignored = [
            "evals/artifacts/example/run/raw/codex.jsonl",
            "evals/itbench-wayfinder/results/runs/example/raw/codex.jsonl",
            "evals/itbench-wayfinder/results/runs/example/workspace/AGENTS.md",
            "evals/itbench-wayfinder/results/grades/example/reasoning-grader.jsonl",
            "evals/results/example/runs/example/snapshots/phase-1.tar.gz",
            "evals/example/__pycache__/module.pyc",
        ]
        tracked_contract = [
            "evals/artifacts/README.md",
            "evals/itbench-wayfinder/results/runs/example/execution.json",
            "evals/itbench-wayfinder/reports/results-summary.json",
            "evals/tests/fixtures/token_forensics/codex-exec.jsonl",
        ]

        self.assertTrue(all(is_ignored(path) for path in ignored))
        self.assertTrue(all(not is_ignored(path) for path in tracked_contract))

    def test_no_raw_execution_exhaust_is_tracked_under_evals(self) -> None:
        raw = [path for path in tracked_eval_files() if is_raw_artifact(path)]
        self.assertEqual(raw, [])

    def test_active_harnesses_route_repository_local_raw_output_to_artifacts(self) -> None:
        expected = ROOT / "evals" / "artifacts"
        modules = [
            arc_wayfinder,
            arc_wayfinder_v2,
            arc_wayfinder_state_complexity,
            wayfinder_fresh_agent_continuation,
            wayfinder_fresh_agent_continuation_v2,
        ]
        roots = [module.ARTIFACTS_ROOT for module in modules]

        self.assertTrue(all(expected in root.parents for root in roots))
        self.assertTrue(
            all(module.artifact_root_for(module.RESULTS_ROOT) == module.ARTIFACTS_ROOT for module in modules)
        )
        custom_results = Path("/tmp/eval-results")
        self.assertTrue(
            all(
                module.artifact_root_for(custom_results) == custom_results / ".artifacts"
                for module in modules
            )
        )
        wrapper = (ROOT / "evals" / "wayfinder_local_state_smoke.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("ARTIFACTS_ROOT = EVAL_ROOT / \"artifacts\" / CAMPAIGN_ID", wrapper)
        self.assertIn("base.ARTIFACTS_ROOT = ARTIFACTS_ROOT", wrapper)

    def test_itbench_compact_summary_loads_without_raw_traces(self) -> None:
        namespace = runpy.run_path(str(ROOT / "evals" / "itbench-wayfinder" / "analyze.py"))
        rows = namespace["load_rows"]()

        self.assertEqual(len(rows), 54)
        self.assertTrue(all("input_tokens" in row for row in rows))


if __name__ == "__main__":
    unittest.main()
