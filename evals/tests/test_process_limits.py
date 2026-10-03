"""Real subprocess controls for bounded prompt delivery; no model calls."""

from contextlib import contextmanager
import os
from pathlib import Path
import signal
import sys
import tempfile
import unittest

from evals.persistence import bounded_process


@contextmanager
def watchdog(seconds=3):
    """Fail safely if the runner itself stops supervising a pipe operation."""

    def expired(signum, frame):
        raise TimeoutError("bounded_process exceeded its outer test watchdog")

    previous_handler = signal.signal(signal.SIGALRM, expired)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        signal.setitimer(signal.ITIMER_REAL, *previous_timer)


class ProcessLimitTests(unittest.TestCase):
    def run_child(
        self, code, *, prompt, seconds=2, output_bytes=1_000_000, monitor=None
    ):
        with tempfile.TemporaryDirectory() as temporary, watchdog():
            root = Path(temporary)
            result = bounded_process(
                [sys.executable, "-c", code],
                cwd=root,
                env=os.environ.copy(),
                prompt=prompt,
                raw=root,
                limits={"seconds": seconds, "output_bytes": output_bytes},
                monitor=(lambda: monitor(root)) if monitor else None,
            )
            return (
                result,
                (root / "codex.jsonl").read_bytes(),
                (root / "stderr.txt").read_bytes(),
            )

    def test_timeout_applies_while_child_does_not_read_large_prompt(self):
        with tempfile.TemporaryDirectory() as temporary, watchdog():
            root = Path(temporary)
            status, code, elapsed = bounded_process(
                [sys.executable, "-c", "import time; time.sleep(10)"],
                cwd=root,
                env=os.environ.copy(),
                prompt="x" * 2_000_000,
                raw=root,
                limits={"seconds": 0.2, "output_bytes": 1000},
            )
            self.assertEqual(status, "timeout")
            self.assertNotEqual(code, 0)
            self.assertLess(elapsed, 2)

    def test_full_unicode_prompt_arrives_before_stdin_eof(self):
        prompt = "Aé🌲\n" * 40_000
        (status, code, _), output, error = self.run_child(
            "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())",
            prompt=prompt,
        )
        self.assertEqual((status, code), ("completed", 0))
        self.assertEqual(output, prompt.encode())
        self.assertEqual(error, b"")

    def test_output_is_drained_while_large_prompt_is_still_pending(self):
        (status, code, _), output, error = self.run_child(
            "import sys; "
            "sys.stdout.buffer.write(b'o' * 131072); sys.stdout.flush(); "
            "sys.stderr.buffer.write(b'e' * 131072); sys.stderr.flush(); "
            "print('\\n' + str(len(sys.stdin.buffer.read())))",
            prompt="x" * 2_000_000,
        )
        self.assertEqual((status, code), ("completed", 0))
        self.assertEqual(output, b"o" * 131072 + b"\n2000000\n")
        self.assertEqual(error, b"e" * 131072)

    def test_child_can_close_stdin_early_without_losing_its_output(self):
        (status, code, _), output, error = self.run_child(
            "import os; os.close(0); print('input declined')",
            prompt="x" * 2_000_000,
        )
        self.assertEqual((status, code), ("completed", 0))
        self.assertEqual(output, b"input declined\n")
        self.assertEqual(error, b"")

    def test_output_limit_applies_while_large_prompt_is_still_pending(self):
        (status, code, elapsed), output, error = self.run_child(
            "import sys, time; "
            "sys.stdout.write('o' * 200000); sys.stdout.flush(); time.sleep(10)",
            prompt="x" * 2_000_000,
            output_bytes=1000,
        )
        self.assertEqual(status, "output-limit")
        self.assertNotEqual(code, 0)
        self.assertLess(elapsed, 2)
        self.assertEqual(output, b"o" * 1000)
        self.assertEqual(error, b"")

    def test_monitor_applies_while_large_prompt_is_still_pending(self):
        (status, code, elapsed), _, _ = self.run_child(
            "from pathlib import Path; import time; "
            "Path('stop').touch(); time.sleep(10)",
            prompt="x" * 2_000_000,
            monitor=lambda root: (
                "infrastructure-blocked" if (root / "stop").exists() else None
            ),
        )
        self.assertEqual(status, "infrastructure-blocked")
        self.assertNotEqual(code, 0)
        self.assertLess(elapsed, 2)


if __name__ == "__main__":
    unittest.main()
