from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


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
        or "snapshots" in parts
        and "runs" in parts
        or "workspace" in parts
        and "runs" in parts
        or "attempts" in parts
        and "runs" in parts
        or name in {"reasoning-grader.jsonl", "reasoning-grader.stderr.txt"}
        or "audit-evidence" in parts
        or "isolation-audit" in parts
        and name.endswith((".jsonl", ".stderr.txt"))
    )


class EvaluationStorageTests(unittest.TestCase):
    def test_raw_artifact_paths_are_ignored_but_compact_results_are_not(self) -> None:
        ignored = [
            "evals/artifacts/example/run/raw/codex.jsonl",
            "evals/results/example/runs/example/snapshots/phase-1.tar.gz",
            "evals/example/__pycache__/module.pyc",
        ]
        tracked_contract = [
            "evals/artifacts/README.md",
            "evals/tests/fixtures/token_forensics/codex-exec.jsonl",
        ]

        self.assertTrue(all(is_ignored(path) for path in ignored))
        self.assertTrue(all(not is_ignored(path) for path in tracked_contract))

    def test_no_raw_execution_exhaust_is_tracked_under_evals(self) -> None:
        raw = [path for path in tracked_eval_files() if is_raw_artifact(path)]
        self.assertEqual(raw, [])


if __name__ == "__main__":
    unittest.main()
