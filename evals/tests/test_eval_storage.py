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
    if path == "evals/artifacts/README.md" or parts[:3] == (
        "evals",
        "tests",
        "fixtures",
    ):
        return False
    if parts[:2] == ("evals", "artifacts"):
        return True
    raw_directories = {
        "__pycache__",
        ".cache",
        "cache",
        "codex-home",
        "codex-homes",
        "jobs",
        "raw",
        "workspace",
        "workspaces",
    }
    raw_filenames = {
        "codex.jsonl",
        "stderr",
        "stderr.txt",
        "stdout",
        "stdout.txt",
    }
    return (
        bool(set(parts) & raw_directories)
        or Path(path).name in raw_filenames
        or Path(path).suffix in {".jsonl", ".log", ".pyc"}
        or Path(path).name.endswith((".stderr.txt", ".stdout.txt"))
    )


class EvaluationStorageTests(unittest.TestCase):
    def test_raw_artifact_paths_are_ignored_but_compact_results_are_not(self) -> None:
        ignored = [
            "evals/artifacts/example/run/raw/codex.jsonl",
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

    def test_raw_execution_exhaust_is_recognized_outside_artifacts(self) -> None:
        raw = (
            "evals/results/example/raw/codex.jsonl",
            "evals/results/example/workspace/source.py",
            "evals/results/example/stdout.txt",
            "evals/results/example/agent.log",
            "evals/results/example/grader-transcript.jsonl",
            "evals/results/example/reasoning-grader.stderr.txt",
        )
        retained = (
            "evals/routing-smoke/cases.json",
            "evals/tests/fixtures/token_forensics/codex-exec.jsonl",
        )

        self.assertTrue(all(is_raw_artifact(path) for path in raw))
        self.assertTrue(all(not is_raw_artifact(path) for path in retained))


if __name__ == "__main__":
    unittest.main()
